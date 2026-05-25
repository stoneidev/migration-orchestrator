import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db.models import Base, Page, PipelineTask
from src.pipeline.engine import mark_page_failed
from src.pipeline.state_machine import PageState


@pytest.fixture
def db_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        s.add(
            Page(
                id="bbs.alert_close",
                module="bbs",
                complexity="low",
                migration_status=PageState.RUNNING.value,
            )
        )
        s.commit()
    return factory


def test_mark_page_failed_transitions_running_page(db_factory):
    mark_page_failed("bbs.alert_close", db_factory, error="boom")

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == PageState.FAILED.value


def test_mark_page_failed_noop_for_non_running(db_factory):
    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        page.migration_status = PageState.BLOCKED.value
        s.commit()

    mark_page_failed("bbs.alert_close", db_factory, error="boom")

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == PageState.BLOCKED.value


def test_mark_page_failed_noop_for_missing_page(db_factory):
    mark_page_failed("missing.page", db_factory, error="boom")


@pytest.mark.asyncio
async def test_run_pipeline_bg_marks_page_failed_on_exception(db_factory):
    from src.api.routes import pipeline as pipeline_routes

    task_id = "run-test-001"
    with db_factory() as s:
        s.add(
            PipelineTask(
                id=task_id,
                task_type="pipeline_run",
                page_id="bbs.alert_close",
                status="queued",
            )
        )
        s.commit()

    mock_settings = MagicMock()
    with patch.object(pipeline_routes, "_get_engine", return_value=(db_factory, mock_settings)):
        with patch.object(pipeline_routes, "create_pipeline_steps", return_value=[]):
            with patch.object(pipeline_routes, "PipelineEngine") as mock_engine_cls:
                mock_engine_cls.return_value.run = AsyncMock(
                    side_effect=RuntimeError("pipeline exploded")
                )
                await pipeline_routes._run_pipeline_bg("bbs.alert_close", task_id)

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == PageState.FAILED.value
        task = s.get(PipelineTask, task_id)
        assert task.status == "failed"
        assert "pipeline exploded" in task.error_message


@pytest.mark.asyncio
async def test_run_single_step_bg_marks_page_failed_on_exception(db_factory):
    from src.api.routes import pipeline as pipeline_routes

    task_id = "step-test-001"
    with db_factory() as s:
        s.add(
            PipelineTask(
                id=task_id,
                task_type="run_step",
                page_id="bbs.alert_close",
                status="queued",
            )
        )
        s.commit()

    mock_settings = MagicMock()
    with patch.object(pipeline_routes, "_get_engine", return_value=(db_factory, mock_settings)):
        with patch.object(pipeline_routes, "create_pipeline_steps", return_value=[]):
            with patch.object(pipeline_routes, "PipelineEngine") as mock_engine_cls:
                mock_engine_cls.return_value.run_next_step = AsyncMock(
                    side_effect=RuntimeError("step exploded")
                )
                await pipeline_routes._run_single_step_bg("bbs.alert_close", task_id)

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == PageState.FAILED.value
        task = s.get(PipelineTask, task_id)
        assert task.status == "failed"


@pytest.mark.asyncio
async def test_retry_step_bg_marks_page_failed_on_exception(db_factory):
    from src.api.routes import pipeline as pipeline_routes

    task_id = "retry-test-001"
    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        page.current_step = 2
        s.add(
            PipelineTask(
                id=task_id,
                task_type="retry_step",
                page_id="bbs.alert_close",
                step_number=3,
                status="queued",
            )
        )
        s.commit()

    mock_settings = MagicMock()
    with patch.object(pipeline_routes, "_get_engine", return_value=(db_factory, mock_settings)):
        with patch.object(pipeline_routes, "create_pipeline_steps", return_value=[]):
            with patch.object(pipeline_routes, "PipelineEngine") as mock_engine_cls:
                mock_engine_cls.return_value.run_next_step = AsyncMock(
                    side_effect=RuntimeError("retry exploded")
                )
                await pipeline_routes._retry_step_bg("bbs.alert_close", 3, task_id)

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == PageState.FAILED.value
        task = s.get(PipelineTask, task_id)
        assert task.status == "failed"
