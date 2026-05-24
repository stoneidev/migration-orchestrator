import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.deps import get_db
from src.db.models import Page, StepExecution, Artifact
from src.pipeline.engine import PipelineEngine
from src.pipeline.steps.registry import create_pipeline_steps
from src.config import Settings

router = APIRouter()

_running_tasks: dict[str, dict] = {}


class PipelineRunRequest(BaseModel):
    page_ids: list[str]


class StepRunRequest(BaseModel):
    page_id: str


def _get_engine():
    from src.db.deps import configure_db, _SessionFactory
    settings = Settings()
    if _SessionFactory is None:
        configure_db(settings.database_url)
    from src.db.deps import _SessionFactory as sf
    return sf, settings


async def _run_pipeline_bg(page_id: str, run_id: str):
    _running_tasks[run_id]["status"] = "running"
    try:
        sf, settings = _get_engine()
        steps = create_pipeline_steps(settings)
        engine = PipelineEngine(steps=steps, session_factory=sf)
        await engine.run(page_id)
        _running_tasks[run_id]["status"] = "completed"
    except Exception as e:
        _running_tasks[run_id]["status"] = "failed"
        _running_tasks[run_id]["error"] = str(e)


async def _run_single_step_bg(page_id: str, task_id: str):
    _running_tasks[task_id]["status"] = "running"
    try:
        sf, settings = _get_engine()
        steps = create_pipeline_steps(settings)
        engine = PipelineEngine(steps=steps, session_factory=sf)
        await engine.run_next_step(page_id)
        _running_tasks[task_id]["status"] = "completed"
    except Exception as e:
        _running_tasks[task_id]["status"] = "failed"
        _running_tasks[task_id]["error"] = str(e)


@router.post("/pipeline/run", status_code=202)
def run_pipeline(request: PipelineRunRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())[:8]
    for page_id in request.page_ids:
        task_id = f"{run_id}-{page_id}"
        _running_tasks[task_id] = {"page_id": page_id, "status": "queued", "started_at": datetime.utcnow().isoformat()}
        background_tasks.add_task(_run_pipeline_bg, page_id, task_id)
    return {"success": True, "data": {"run_id": run_id, "page_ids": request.page_ids}}


@router.post("/pipeline/run-step", status_code=202)
def run_single_step(request: StepRunRequest, background_tasks: BackgroundTasks):
    task_id = f"step-{request.page_id}-{datetime.utcnow().strftime('%H%M%S')}"
    _running_tasks[task_id] = {"page_id": request.page_id, "status": "queued", "started_at": datetime.utcnow().isoformat()}
    background_tasks.add_task(_run_single_step_bg, request.page_id, task_id)
    return {"success": True, "data": {"task_id": task_id, "page_id": request.page_id, "message": f"Running next step for {request.page_id}"}}


@router.get("/pipeline/status")
def get_pipeline_status():
    return {"success": True, "data": _running_tasks}


@router.get("/pipeline/{page_id}/steps")
def get_page_steps(page_id: str, db: Session = Depends(get_db)):
    page = db.get(Page, page_id)
    if not page:
        return {"success": False, "error": {"code": "PAGE-001", "message": "Page not found"}}

    executions = db.query(StepExecution).filter_by(page_id=page_id).order_by(StepExecution.step_number, StepExecution.attempt_number).all()
    artifacts = db.query(Artifact).filter_by(page_id=page_id).all()

    step_names = {1: "spec_load", 2: "spec_verify", 3: "api_contract", 4: "react_generation", 5: "java_generation", 6: "java_test", 7: "integration_test", 8: "equivalence_check", 9: "complete"}

    steps_data = []
    for step_num in range(1, 10):
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
            "step_name": step_names.get(step_num, f"step_{step_num}"),
            "status": status,
            "executions": [{"attempt": e.attempt_number, "status": e.status, "model": e.model_used, "cost": e.cost, "duration_ms": e.duration_ms, "error": e.error_message} for e in step_execs],
            "artifacts": [{"type": a.artifact_type, "path": a.file_path, "version": a.version} for a in step_artifacts],
        })

    return {"success": True, "data": {"page_id": page_id, "migration_status": page.migration_status, "current_step": page.current_step, "total_cost": page.total_cost, "steps": steps_data}}
