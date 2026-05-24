import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.deps import get_db, _SessionFactory
from src.db.models import Page
from src.pipeline.engine import PipelineEngine
from src.pipeline.steps.registry import create_pipeline_steps
from src.config import Settings

router = APIRouter()

_running_tasks: dict[str, dict] = {}


class PipelineRunRequest(BaseModel):
    page_ids: list[str]


async def _run_pipeline_bg(page_id: str, run_id: str):
    _running_tasks[run_id]["status"] = "running"
    try:
        settings = Settings()
        steps = create_pipeline_steps(settings)
        engine = PipelineEngine(steps=steps, session_factory=_SessionFactory)
        await engine.run(page_id)
        _running_tasks[run_id]["status"] = "completed"
    except Exception as e:
        _running_tasks[run_id]["status"] = "failed"
        _running_tasks[run_id]["error"] = str(e)


@router.post("/pipeline/run", status_code=202)
def run_pipeline(
    request: PipelineRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    run_id = str(uuid.uuid4())[:8]
    started_pages = []

    for page_id in request.page_ids:
        page = db.get(Page, page_id)
        if page:
            page.migration_status = "running"
            page.started_at = datetime.utcnow()
            started_pages.append(page_id)

    db.flush()

    for page_id in started_pages:
        task_id = f"{run_id}-{page_id}"
        _running_tasks[task_id] = {
            "page_id": page_id,
            "status": "queued",
            "started_at": datetime.utcnow().isoformat(),
        }
        background_tasks.add_task(_run_pipeline_bg, page_id, task_id)

    return {
        "success": True,
        "data": {
            "run_id": run_id,
            "page_ids": started_pages,
            "message": f"Pipeline started for {len(started_pages)} page(s)",
        },
    }


@router.get("/pipeline/status")
def get_pipeline_status():
    return {"success": True, "data": _running_tasks}
