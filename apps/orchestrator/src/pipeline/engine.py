from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from sqlalchemy.orm import sessionmaker, Session

from src.db.models import Page, StepExecution, Artifact, CostLog
from src.pipeline.state_machine import StepState, PageState, transition_page


@dataclass
class StepContext:
    page_id: str
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
    ):
        self.steps = sorted(steps, key=lambda s: s.step_number)
        self.session_factory = session_factory
        self.max_retries = max_retries

    async def run(self, page_id: str) -> None:
        with self.session_factory() as session:
            page = session.get(Page, page_id)
            if page is None:
                return

            current_state = PageState(page.migration_status)
            transition_page(current_state, PageState.RUNNING)
            page.migration_status = PageState.RUNNING.value
            page.started_at = datetime.utcnow()
            session.flush()

            context = StepContext(page_id=page.id)

            for step in self.steps:
                result = await self._execute_step(step, page, context, session)
                if not result.success:
                    transition_page(PageState.RUNNING, PageState.BLOCKED)
                    page.migration_status = PageState.BLOCKED.value
                    session.commit()
                    return

                context.previous_results[step.step_number] = result
                self._update_context_from_result(context, step, result)

            transition_page(PageState.RUNNING, PageState.COMPLETE)
            page.migration_status = PageState.COMPLETE.value
            page.completed_at = datetime.utcnow()
            session.commit()

    async def _execute_step(
        self, step: BaseStep, page: Page, context: StepContext, session: Session
    ) -> StepResult:
        for attempt in range(1, self.max_retries + 1):
            started = datetime.utcnow()
            result = await step.execute(context)
            ended = datetime.utcnow()
            duration_ms = int((ended - started).total_seconds() * 1000)
            result.duration_ms = duration_ms

            if result.success:
                status = StepState.PASSED
            elif attempt < self.max_retries:
                status = StepState.RETRYING
            else:
                status = StepState.BLOCKED

            execution = StepExecution(
                page_id=page.id,
                step_number=step.step_number,
                step_name=step.name,
                status=status.value,
                attempt_number=attempt,
                model_used=result.model_used,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cost=result.cost,
                duration_ms=duration_ms,
                error_message=result.error,
                started_at=started,
                completed_at=ended,
            )
            session.add(execution)

            if result.cost > 0:
                cost_entry = CostLog(
                    page_id=page.id,
                    step_number=step.step_number,
                    model=result.model_used or "unknown",
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens,
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
                return result

            if attempt == self.max_retries:
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
