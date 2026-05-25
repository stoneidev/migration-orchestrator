"""Phase 2 regression: cost / token figures must propagate end-to-end.

Each step that talks to an LLM has its own result dataclass (ReactGenResult,
JavaGenResult, etc.). Phase 2 wires those through to ``StepResult`` and on
to ``CostLog`` / ``Page.total_cost`` so the orchestrator's billing figures
match what was actually spent.
"""

from __future__ import annotations

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker

from src.db.models import Base, CostLog, Page
from src.pipeline.engine import BaseStep, PipelineEngine, StepContext, StepResult
from src.workers.analysis import MODEL_PRICING, compute_cost


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
        s.add(Page(id="shop.products", module="shop"))
        s.commit()
    return factory


def test_compute_cost_uses_separate_cache_rate():
    """cache_read should be 10x cheaper than fresh input."""
    pricing = MODEL_PRICING["sonnet"]
    assert pricing["cache_read"] < pricing["input"]
    assert pricing["cache_write"] > pricing["input"]

    fresh_only = compute_cost(
        "sonnet", input_tokens=10_000, output_tokens=0
    )
    cache_only = compute_cost(
        "sonnet", input_tokens=0, output_tokens=0, cache_read_tokens=10_000
    )
    # Cache reads bill at one tenth of fresh input, so the cost ratio should
    # be ~10x.
    assert fresh_only > cache_only * 5


def test_compute_cost_haiku_matches_published_price():
    """Haiku: $0.80 / 1M input == $0.0008 / 1k tokens."""
    cost = compute_cost("haiku", input_tokens=1_000_000, output_tokens=0)
    assert round(cost, 2) == 0.80


@pytest.mark.asyncio
async def test_engine_records_cost_log_for_token_only_steps(db_factory):
    """Even if the cost from the upstream API is 0, recording the tokens
    enables retrospective recomputation. The engine now writes a CostLog
    whenever tokens are non-zero, not only when cost is non-zero."""

    class TokenOnlyStep(BaseStep):
        name = "tokens_only"
        step_number = 1

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(
                success=True,
                model_used="sonnet",
                input_tokens=500,
                output_tokens=200,
                cost=0.0,
            )

    engine = PipelineEngine(steps=[TokenOnlyStep()], session_factory=db_factory)
    await engine.run("shop.products")

    with db_factory() as s:
        logs = s.query(CostLog).filter_by(page_id="shop.products").all()
        assert len(logs) == 1
        assert logs[0].input_tokens == 500
        assert logs[0].output_tokens == 200
        page = s.get(Page, "shop.products")
        assert page.total_input_tokens == 500
        assert page.total_output_tokens == 200


@pytest.mark.asyncio
async def test_engine_persists_cache_read_tokens(db_factory):
    """CostLog has a cache_read_tokens column that should reflect what the
    step actually reported."""

    class CachedStep(BaseStep):
        name = "cached"
        step_number = 1

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(
                success=True,
                model_used="sonnet",
                input_tokens=100,
                output_tokens=50,
                cache_read_tokens=5_000,
                cost=0.01,
            )

    engine = PipelineEngine(steps=[CachedStep()], session_factory=db_factory)
    await engine.run("shop.products")

    with db_factory() as s:
        logs = s.query(CostLog).filter_by(page_id="shop.products").all()
        assert len(logs) == 1
        assert logs[0].cache_read_tokens == 5_000


@pytest.mark.asyncio
async def test_engine_persists_cache_creation_tokens(db_factory):
    class CacheWriteStep(BaseStep):
        name = "cache_write"
        step_number = 1

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(
                success=True,
                model_used="sonnet",
                input_tokens=100,
                output_tokens=50,
                cache_creation_tokens=2_000,
                cost=0.01,
            )

    engine = PipelineEngine(steps=[CacheWriteStep()], session_factory=db_factory)
    await engine.run("shop.products")

    with db_factory() as s:
        logs = s.query(CostLog).filter_by(page_id="shop.products").all()
        assert len(logs) == 1
        assert logs[0].cache_creation_tokens == 2_000


@pytest.mark.asyncio
async def test_engine_blocks_when_budget_exceeded(db_factory, monkeypatch):
    monkeypatch.setenv("ENFORCE_PROJECT_BUDGET", "true")

    class NoOpStep(BaseStep):
        name = "noop"
        step_number = 1

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(success=True)

    with db_factory() as s:
        page = s.get(Page, "shop.products")
        page.total_cost = 25_000.0
        s.commit()

    engine = PipelineEngine(steps=[NoOpStep()], session_factory=db_factory)
    await engine.run("shop.products")

    with db_factory() as s:
        page = s.get(Page, "shop.products")
        assert page.migration_status == "blocked"
        assert page.current_step == 0


@pytest.mark.asyncio
async def test_page_total_cost_equals_sum_of_cost_logs(db_factory):
    class A(BaseStep):
        name = "a"
        step_number = 1

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(success=True, model_used="haiku", cost=0.02, input_tokens=100)

    class B(BaseStep):
        name = "b"
        step_number = 2

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(success=True, model_used="sonnet", cost=0.13, input_tokens=200)

    engine = PipelineEngine(steps=[A(), B()], session_factory=db_factory)
    await engine.run("shop.products")

    with db_factory() as s:
        logs = s.query(CostLog).filter_by(page_id="shop.products").all()
        total_from_logs = sum(log.cost for log in logs)
        page = s.get(Page, "shop.products")
        assert pytest.approx(page.total_cost) == total_from_logs
