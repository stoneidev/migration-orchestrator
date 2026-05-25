from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any

from sqlalchemy.orm import sessionmaker, Session

from src.db.models import Page, StepExecution, Artifact, CostLog
from src.pipeline.state_machine import (
    InvalidTransitionError,
    PageState,
    StepState,
    transition_page,
)
from src.api.ws.events import event_bus
from src.util.clock import utcnow_naive

log = logging.getLogger(__name__)


def _set_page_state(page: Page, target: PageState) -> None:
    """Validate and apply a page-level state transition.

    All page status writes inside the engine MUST go through this helper so
    that ``state_machine`` is the single source of truth for what's allowed.
    Bypassing it (``page.migration_status = "running"``) was how a number of
    invalid states could be silently entered.
    """
    try:
        current = PageState(page.migration_status)
    except ValueError as exc:
        raise InvalidTransitionError(
            f"Unknown current page state: {page.migration_status!r}"
        ) from exc
    if current == target:
        return
    page.migration_status = transition_page(current, target).value


def mark_page_failed(
    page_id: str,
    session_factory: sessionmaker,
    error: str | None = None,
) -> None:
    """Mark a page as failed after an unhandled background pipeline error.

    Only transitions pages that are currently ``RUNNING``; other states are
    left unchanged (e.g. rollback left the page ``queued``, or step failure
    already set ``blocked``).
    """
    with session_factory() as session:
        page = session.get(Page, page_id)
        if page is None:
            return
        try:
            current = PageState(page.migration_status)
        except ValueError:
            log.warning("Cannot mark page %s failed: unknown status %r", page_id, page.migration_status)
            return
        if current != PageState.RUNNING:
            return
        _set_page_state(page, PageState.FAILED)
        session.commit()

    payload: dict[str, str] = {"page_id": page_id, "status": PageState.FAILED.value}
    if error:
        payload["error"] = error
    event_bus.emit("page_state", payload)
    log.error("page %s marked failed: %s", page_id, error)


@dataclass
class StepContext:
    page_id: str
    workspace_root: Path | None = None
    spec: dict | None = None
    api_contract: str | None = None
    generated_files: dict[str, list[str]] = field(default_factory=dict)
    previous_results: dict[int, "StepResult"] = field(default_factory=dict)


@dataclass
class StepResult:
    success: bool
    artifacts: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    model_used: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    cost: float = 0.0
    duration_ms: int = 0


class BaseStep(ABC):
    name: str
    step_number: int

    @abstractmethod
    async def execute(self, context: StepContext) -> StepResult:
        pass


class PipelineEngine:
    def __init__(
        self,
        steps: list[BaseStep],
        session_factory: sessionmaker,
        max_retries: int = 3,
        worktree_manager: Any | None = None,
    ):
        self.steps = sorted(steps, key=lambda s: s.step_number)
        self.session_factory = session_factory
        self.max_retries = max_retries
        self._worktree_manager = worktree_manager

    def _get_worktree_manager(self, project_root: Path):
        if self._worktree_manager is None:
            from src.workers.worktree import WorktreeManager

            self._worktree_manager = WorktreeManager(project_root)
        return self._worktree_manager

    def _prepare_workspace(self, page_id: str, context: StepContext, settings) -> None:
        if not settings.use_worktree:
            return
        mgr = self._get_worktree_manager(settings.project_root)
        wt_path = mgr.ensure(page_id, "migration")
        context.workspace_root = wt_path
        event_bus.emit(
            "worktree:ready",
            {"page_id": page_id, "path": str(wt_path)},
        )
        log.info("worktree ready for %s at %s", page_id, wt_path)

    def _commit_step(self, context: StepContext, step: BaseStep, result: StepResult) -> None:
        if context.workspace_root is None:
            return
        from src.git.manager import GitManager

        git = GitManager(repo_root=context.workspace_root)
        message = git.commit_step(
            context.page_id,
            step.step_number,
            step.name,
            model=result.model_used or "",
            cost=result.cost,
        )
        if message:
            event_bus.emit(
                "git:commit",
                {
                    "page_id": context.page_id,
                    "step": step.step_number,
                    "message": message[:120],
                },
            )

    async def run(self, page_id: str) -> None:
        from src.config import Settings

        settings = Settings()
        with self.session_factory() as session:
            page = session.get(Page, page_id)
            if page is None:
                return

            if settings.enforce_project_budget and page.total_cost >= settings.project_budget:
                _set_page_state(page, PageState.BLOCKED)
                session.commit()
                event_bus.emit(
                    "log",
                    {
                        "level": "warning",
                        "message": (
                            f"Project budget exceeded "
                            f"(${page.total_cost:.2f} >= ${settings.project_budget:.2f})"
                        ),
                        "page_id": page_id,
                    },
                )
                return

            _set_page_state(page, PageState.RUNNING)
            page.started_at = utcnow_naive()
            session.commit()

            context = await self._rebuild_context(page, session)
            self._prepare_workspace(page_id, context, settings)
            event_bus.emit("pipeline:started", {"page_id": page_id})

            for step in self.steps:
                if step.step_number <= page.current_step:
                    continue
                event_bus.emit("pipeline:step_started", {"page_id": page_id, "step": step.step_number, "step_name": step.name})
                result = await self._execute_step(step, page, context, session)
                session.commit()
                if not result.success:
                    _set_page_state(page, PageState.BLOCKED)
                    session.commit()
                    return

                context.previous_results[step.step_number] = result
                self._update_context_from_result(context, step, result)
                self._commit_step(context, step, result)

            _set_page_state(page, PageState.COMPLETE)
            page.completed_at = utcnow_naive()
            session.commit()

    async def run_next_step(self, page_id: str) -> None:
        from src.config import Settings

        settings = Settings()
        with self.session_factory() as session:
            page = session.get(Page, page_id)
            if page is None:
                return

            if PageState(page.migration_status) != PageState.RUNNING:
                _set_page_state(page, PageState.RUNNING)
                page.started_at = page.started_at or utcnow_naive()
                session.flush()

            next_step_num = page.current_step + 1
            step = next((s for s in self.steps if s.step_number == next_step_num), None)
            if step is None:
                _set_page_state(page, PageState.COMPLETE)
                page.completed_at = utcnow_naive()
                session.commit()
                return

            context = await self._rebuild_context(page, session)
            self._prepare_workspace(page_id, context, settings)

            event_bus.emit("pipeline:step_started", {"page_id": page_id, "step": step.step_number, "step_name": step.name})
            result = await self._execute_step(step, page, context, session)

            if result.success:
                self._update_context_from_result(context, step, result)
                self._commit_step(context, step, result)
                final_step_number = self.steps[-1].step_number if self.steps else next_step_num
                if next_step_num == final_step_number:
                    _set_page_state(page, PageState.COMPLETE)
                    page.completed_at = utcnow_naive()
                session.commit()
                event_bus.emit("pipeline:step_completed", {
                    "page_id": page_id, "step": step.step_number,
                    "status": "passed", "next_step": next_step_num + 1,
                })
            else:
                _set_page_state(page, PageState.BLOCKED)
                session.commit()

    async def _rebuild_context(self, page: Page, session: Session) -> StepContext:
        context = StepContext(page_id=page.id)
        from src.pipeline.steps.step1_spec_load import load_spec
        from src.config import Settings

        try:
            settings = Settings()
            spec = load_spec(page.id, specs_dir=settings.specs_dir)
            context.spec = spec
        except Exception as exc:
            log.warning(
                "Failed to load spec for %s during context rebuild: %s",
                page.id,
                exc,
            )
            event_bus.emit(
                "log",
                {
                    "level": "warning",
                    "message": f"Failed to load spec for {page.id}: {exc}",
                    "page_id": page.id,
                },
            )

        # Minimal API contract from spec (no file I/O to avoid stuck)
        if context.spec:
            ops = context.spec.get("operations", [])
            routes = "\n".join(f"  /api/v1/{op.get('id','')}:\n    get:\n      summary: {op.get('name','')}" for op in ops)
            context.api_contract = f"openapi: '3.1.0'\ninfo:\n  title: {page.id}\npaths:\n{routes}"

        return context

    async def _execute_step(
        self, step: BaseStep, page: Page, context: StepContext, session: Session
    ) -> StepResult:
        for attempt in range(1, self.max_retries + 1):
            started = utcnow_naive()
            # Mark as running immediately so Dashboard shows real-time status
            running_exec = StepExecution(
                page_id=page.id,
                step_number=step.step_number,
                step_name=step.name,
                status="running",
                attempt_number=attempt,
                started_at=started,
            )
            session.add(running_exec)
            session.commit()

            result = await step.execute(context)
            ended = utcnow_naive()
            duration_ms = int((ended - started).total_seconds() * 1000)
            result.duration_ms = duration_ms

            if result.success:
                status = StepState.PASSED
            elif attempt < self.max_retries:
                status = StepState.RETRYING
            else:
                status = StepState.BLOCKED

            # Update the running execution with final status
            running_exec.status = status.value
            running_exec.model_used = result.model_used
            running_exec.input_tokens = result.input_tokens
            running_exec.output_tokens = result.output_tokens
            running_exec.cost = result.cost
            running_exec.duration_ms = duration_ms
            running_exec.error_message = result.error
            running_exec.completed_at = ended

            if result.cost > 0 or result.input_tokens > 0 or result.output_tokens > 0:
                cost_entry = CostLog(
                    page_id=page.id,
                    step_number=step.step_number,
                    model=result.model_used or "unknown",
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens,
                    cache_read_tokens=result.cache_read_tokens,
                    cache_creation_tokens=result.cache_creation_tokens,
                    cost=result.cost,
                )
                session.add(cost_entry)
                page.total_cost += result.cost
                page.total_input_tokens += result.input_tokens
                page.total_output_tokens += result.output_tokens

            session.flush()

            if result.success:
                page.current_step = step.step_number
                self._save_artifacts(page.id, step, result, session)
                event_bus.emit("pipeline:step_completed", {
                    "page_id": page.id, "step": step.step_number,
                    "step_name": step.name, "status": "passed",
                    "duration_ms": result.duration_ms, "cost": result.cost,
                })
                return result

            if attempt == self.max_retries:
                event_bus.emit("pipeline:step_failed", {
                    "page_id": page.id, "step": step.step_number,
                    "step_name": step.name, "error": result.error,
                })
                return result

        return StepResult(success=False, error="Max retries exceeded")

    def _save_artifacts(
        self, page_id: str, step: BaseStep, result: StepResult, session: Session
    ) -> None:
        artifacts = result.artifacts
        files = artifacts.get("files", [])
        for file_path in files:
            artifact = Artifact(
                page_id=page_id,
                step_number=step.step_number,
                artifact_type=self._infer_artifact_type(step.name, file_path),
                file_path=file_path,
            )
            session.add(artifact)

        if "api_contract" in artifacts:
            session.add(Artifact(
                page_id=page_id,
                step_number=step.step_number,
                artifact_type="api_contract",
                file_path=f"artifacts/{page_id}/openapi.yaml",
            ))

        session.flush()

    def _infer_artifact_type(self, step_name: str, file_path: str) -> str:
        if file_path.endswith(".tsx") or file_path.endswith(".ts"):
            return "react_component"
        if file_path.endswith(".java"):
            return "java_class"
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            return "api_contract"
        return "other"

    def _update_context_from_result(
        self, context: StepContext, step: BaseStep, result: StepResult
    ) -> None:
        artifacts = result.artifacts
        if "spec" in artifacts:
            context.spec = artifacts["spec"]
        if "api_contract" in artifacts:
            context.api_contract = artifacts["api_contract"]
        if "files" in artifacts:
            context.generated_files[step.name] = artifacts["files"]
