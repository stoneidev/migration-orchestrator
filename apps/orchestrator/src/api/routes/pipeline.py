import uuid

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session, sessionmaker

from src.api.validators import is_valid_page_id, validate_page_id
from src.db.deps import get_db, get_session_factory
from src.db.models import Artifact, Page, PipelineTask, StepExecution
from src.pipeline.engine import PipelineEngine
from src.pipeline.steps.registry import STEP_DEFINITIONS, create_pipeline_steps
from src.config import Settings
from src.util.clock import utcnow

router = APIRouter()

class PipelineRunRequest(BaseModel):
    page_ids: list[str]

    @field_validator("page_ids")
    @classmethod
    def _check_page_ids(cls, value: list[str]) -> list[str]:
        for pid in value:
            if not is_valid_page_id(pid):
                raise ValueError(f"Invalid page_id: {pid}")
        return value


class StepRunRequest(BaseModel):
    page_id: str

    @field_validator("page_id")
    @classmethod
    def _check_page_id(cls, value: str) -> str:
        if not is_valid_page_id(value):
            raise ValueError(f"Invalid page_id: {value}")
        return value


class StepRetryRequest(BaseModel):
    page_id: str
    step_number: int

    @field_validator("page_id")
    @classmethod
    def _check_page_id(cls, value: str) -> str:
        if not is_valid_page_id(value):
            raise ValueError(f"Invalid page_id: {value}")
        return value


def _get_engine() -> tuple[sessionmaker, Settings]:
    settings = Settings()
    factory = get_session_factory()
    return factory, settings


def _task_to_dict(task: PipelineTask) -> dict:
    return {
        "task_id": task.id,
        "task_type": task.task_type,
        "page_id": task.page_id,
        "step": task.step_number,
        "status": task.status,
        "error": task.error_message,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def _create_task(
    *,
    task_id: str,
    task_type: str,
    page_id: str,
    step_number: int | None = None,
) -> None:
    sf, _ = _get_engine()
    with sf() as session:
        session.add(
            PipelineTask(
                id=task_id,
                task_type=task_type,
                page_id=page_id,
                step_number=step_number,
                status="queued",
            )
        )
        session.commit()


def _update_task(task_id: str, *, status: str, error: str | None = None) -> None:
    sf, _ = _get_engine()
    with sf() as session:
        task = session.get(PipelineTask, task_id)
        if task is None:
            return
        task.status = status
        task.error_message = error
        task.updated_at = utcnow().replace(tzinfo=None)
        session.commit()


async def _run_pipeline_bg(page_id: str, task_id: str):
    _update_task(task_id, status="running")
    try:
        sf, settings = _get_engine()
        steps = create_pipeline_steps(settings)
        engine = PipelineEngine(steps=steps, session_factory=sf)
        await engine.run(page_id)
        _update_task(task_id, status="completed")
    except Exception as e:
        _update_task(task_id, status="failed", error=str(e))


async def _run_single_step_bg(page_id: str, task_id: str):
    _update_task(task_id, status="running")
    try:
        sf, settings = _get_engine()
        steps = create_pipeline_steps(settings)
        engine = PipelineEngine(steps=steps, session_factory=sf)
        await engine.run_next_step(page_id)
        _update_task(task_id, status="completed")
    except Exception as e:
        _update_task(task_id, status="failed", error=str(e))


@router.post("/pipeline/run", status_code=202)
def run_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    run_id = uuid.uuid4().hex[:12]
    for page_id in request.page_ids:
        task_id = f"run-{run_id}-{uuid.uuid4().hex[:8]}"
        _create_task(task_id=task_id, task_type="pipeline_run", page_id=page_id)
        background_tasks.add_task(_run_pipeline_bg, page_id, task_id)
    return {"success": True, "data": {"run_id": run_id, "page_ids": request.page_ids}}


@router.post("/pipeline/run-step", status_code=202)
def run_single_step(request: StepRunRequest, background_tasks: BackgroundTasks):
    task_id = f"step-{uuid.uuid4().hex[:16]}"
    _create_task(task_id=task_id, task_type="run_step", page_id=request.page_id)
    background_tasks.add_task(_run_single_step_bg, request.page_id, task_id)
    return {"success": True, "data": {"task_id": task_id, "page_id": request.page_id, "message": f"Running next step for {request.page_id}"}}


@router.post("/pipeline/retry-step", status_code=202)
def retry_step(request: StepRetryRequest, background_tasks: BackgroundTasks):
    """Reset a specific step and re-run from that point."""
    task_id = f"retry-{uuid.uuid4().hex[:16]}"
    _create_task(
        task_id=task_id,
        task_type="retry_step",
        page_id=request.page_id,
        step_number=request.step_number,
    )
    background_tasks.add_task(_retry_step_bg, request.page_id, request.step_number, task_id)
    return {"success": True, "data": {"task_id": task_id, "page_id": request.page_id, "step": request.step_number, "message": f"Retrying step {request.step_number} for {request.page_id}"}}


async def _retry_step_bg(page_id: str, step_number: int, task_id: str):
    from src.pipeline.engine import _set_page_state
    from src.pipeline.state_machine import PageState

    _update_task(task_id, status="running")
    try:
        sf, settings = _get_engine()
        # Reset page to before this step
        with sf() as s:
            page = s.get(Page, page_id)
            if page:
                page.current_step = step_number - 1
                _set_page_state(page, PageState.RUNNING)
                # Delete old executions for this step
                s.query(StepExecution).filter_by(page_id=page_id, step_number=step_number).delete()
                s.query(Artifact).filter_by(page_id=page_id, step_number=step_number).delete()
                s.commit()

        # Run the step
        steps = create_pipeline_steps(settings)
        engine = PipelineEngine(steps=steps, session_factory=sf)
        await engine.run_next_step(page_id)
        _update_task(task_id, status="completed")
    except Exception as e:
        _update_task(task_id, status="failed", error=str(e))


@router.get("/pipeline/status")
def get_pipeline_status(db: Session = Depends(get_db)):
    rows = db.query(PipelineTask).order_by(PipelineTask.started_at.desc()).limit(500).all()
    return {"success": True, "data": {row.id: _task_to_dict(row) for row in rows}}


@router.get("/pipeline/{page_id}/steps")
def get_page_steps(page_id: str, db: Session = Depends(get_db)):
    page_id = validate_page_id(page_id)
    page = db.get(Page, page_id)
    if not page:
        return {"success": False, "error": {"code": "PAGE-001", "message": "Page not found"}}

    executions = db.query(StepExecution).filter_by(page_id=page_id).order_by(StepExecution.step_number, StepExecution.attempt_number).all()
    artifacts = db.query(Artifact).filter_by(page_id=page_id).all()

    step_definitions = list(STEP_DEFINITIONS)
    known_numbers = {n for n, _ in step_definitions}
    for n in sorted({e.step_number for e in executions if e.step_number not in known_numbers}):
        step_definitions.append((n, f"step_{n}"))
    step_definitions.sort(key=lambda x: x[0])

    steps_data = []
    for step_num, step_name in step_definitions:
        step_execs = [e for e in executions if e.step_number == step_num]
        step_artifacts = [a for a in artifacts if a.step_number == step_num]
        if step_num <= page.current_step:
            status = "passed"
        elif step_num == page.current_step + 1 and page.migration_status == "running":
            status = "running"
        else:
            status = "pending"
        if step_execs and step_execs[-1].status == "blocked":
            status = "blocked"
        steps_data.append({
            "step_number": step_num,
            "step_name": step_name,
            "status": status,
            "executions": [{"attempt": e.attempt_number, "status": e.status, "model": e.model_used, "cost": e.cost, "duration_ms": e.duration_ms, "error": e.error_message} for e in step_execs],
            "artifacts": [{"type": a.artifact_type, "path": a.file_path, "version": a.version} for a in step_artifacts],
        })

    return {"success": True, "data": {"page_id": page_id, "migration_status": page.migration_status, "current_step": page.current_step, "total_cost": page.total_cost, "steps": steps_data}}
