import asyncio

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.api.routes import pipeline as pipeline_routes
from src.db.models import Base, Page, PipelineTask
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
        s.add(
            Page(
                id="shop_admin.cs_list",
                module="shop_admin",
                complexity="medium",
                migration_status=PageState.RUNNING.value,
            )
        )
        s.commit()
    return factory


@pytest.fixture(autouse=True)
def semaphore_reset():
    pipeline_routes.reset_page_semaphore()
    yield
    pipeline_routes.reset_page_semaphore()


def test_init_page_semaphore_clamps_to_at_least_one():
    pipeline_routes.init_page_semaphore(0)
    assert pipeline_routes._page_semaphore._value == 1


@pytest.mark.asyncio
async def test_run_pipeline_bg_serializes_when_limit_is_one(db_factory):
    pipeline_routes.init_page_semaphore(1)
    order: list[str] = []

    async def track_run(page_id: str, *_args, **_kwargs):
        order.append(f"start-{page_id}")
        await asyncio.sleep(0.05)
        order.append(f"end-{page_id}")

    mock_settings = MagicMock()
    for page_id, task_id in [
        ("bbs.alert_close", "run-a"),
        ("shop_admin.cs_list", "run-b"),
    ]:
        with db_factory() as s:
            s.add(
                PipelineTask(
                    id=task_id,
                    task_type="pipeline_run",
                    page_id=page_id,
                    status="queued",
                )
            )
            s.commit()

    with patch.object(pipeline_routes, "_get_engine", return_value=(db_factory, mock_settings)):
        with patch.object(pipeline_routes, "create_pipeline_steps", return_value=[]):
            with patch.object(pipeline_routes, "PipelineEngine") as mock_engine_cls:
                mock_engine_cls.return_value.run = AsyncMock(side_effect=track_run)
                await asyncio.gather(
                    pipeline_routes._run_pipeline_bg("bbs.alert_close", "run-a"),
                    pipeline_routes._run_pipeline_bg("shop_admin.cs_list", "run-b"),
                )

    assert len(order) == 4
    first_end = order.index("end-bbs.alert_close")
    second_start = order.index("start-shop_admin.cs_list")
    alt_first_end = order.index("end-shop_admin.cs_list")
    alt_second_start = order.index("start-bbs.alert_close")
    assert first_end < second_start or alt_first_end < alt_second_start


@pytest.mark.asyncio
async def test_run_pipeline_bg_allows_parallel_when_limit_is_two(db_factory):
    pipeline_routes.init_page_semaphore(2)
    active = 0
    peak = 0
    lock = asyncio.Lock()

    async def track_run(page_id: str, *_args, **_kwargs):
        nonlocal active, peak
        async with lock:
            active += 1
            peak = max(peak, active)
        await asyncio.sleep(0.05)
        async with lock:
            active -= 1

    mock_settings = MagicMock()
    for page_id, task_id in [
        ("bbs.alert_close", "run-a"),
        ("shop_admin.cs_list", "run-b"),
    ]:
        with db_factory() as s:
            s.add(
                PipelineTask(
                    id=task_id,
                    task_type="pipeline_run",
                    page_id=page_id,
                    status="queued",
                )
            )
            s.commit()

    with patch.object(pipeline_routes, "_get_engine", return_value=(db_factory, mock_settings)):
        with patch.object(pipeline_routes, "create_pipeline_steps", return_value=[]):
            with patch.object(pipeline_routes, "PipelineEngine") as mock_engine_cls:
                mock_engine_cls.return_value.run = AsyncMock(side_effect=track_run)
                await asyncio.gather(
                    pipeline_routes._run_pipeline_bg("bbs.alert_close", "run-a"),
                    pipeline_routes._run_pipeline_bg("shop_admin.cs_list", "run-b"),
                )

    assert peak == 2
