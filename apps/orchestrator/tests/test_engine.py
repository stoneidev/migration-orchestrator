import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db.models import Base, Page, StepExecution
from src.pipeline.engine import PipelineEngine, StepResult, StepContext, BaseStep


class MockPassStep(BaseStep):
    name = "mock_pass"
    step_number = 1

    async def execute(self, context: StepContext) -> StepResult:
        return StepResult(success=True, artifacts={})


class MockFailStep(BaseStep):
    name = "mock_fail"
    step_number = 1

    async def execute(self, context: StepContext) -> StepResult:
        return StepResult(success=False, error="Something went wrong")


@pytest.fixture
def db_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        s.add(Page(id="bbs.alert_close", module="bbs", complexity="low"))
        s.commit()
    return factory


@pytest.mark.asyncio
async def test_engine_runs_step_successfully(db_factory):
    engine = PipelineEngine(steps=[MockPassStep()], session_factory=db_factory)
    await engine.run("bbs.alert_close")

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.current_step == 1

        executions = s.query(StepExecution).filter_by(page_id="bbs.alert_close").all()
        assert len(executions) == 1
        assert executions[0].status == "passed"
        assert executions[0].step_name == "mock_pass"


@pytest.mark.asyncio
async def test_engine_records_failure(db_factory):
    engine = PipelineEngine(steps=[MockFailStep()], session_factory=db_factory, max_retries=1)
    await engine.run("bbs.alert_close")

    with db_factory() as s:
        executions = s.query(StepExecution).filter_by(page_id="bbs.alert_close").all()
        assert len(executions) == 1
        assert executions[0].status == "blocked"
        assert executions[0].error_message == "Something went wrong"


class MockFailThenPassStep(BaseStep):
    name = "flaky"
    step_number = 1

    def __init__(self):
        self.call_count = 0

    async def execute(self, context: StepContext) -> StepResult:
        self.call_count += 1
        if self.call_count < 3:
            return StepResult(success=False, error=f"Fail attempt {self.call_count}")
        return StepResult(success=True, artifacts={})


@pytest.mark.asyncio
async def test_engine_retries_then_passes(db_factory):
    step = MockFailThenPassStep()
    engine = PipelineEngine(steps=[step], session_factory=db_factory, max_retries=3)
    await engine.run("bbs.alert_close")

    assert step.call_count == 3

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.current_step == 1
        assert page.migration_status == "complete"

        executions = s.query(StepExecution).filter_by(page_id="bbs.alert_close").all()
        assert len(executions) == 3
        assert executions[0].status == "retrying"
        assert executions[1].status == "retrying"
        assert executions[2].status == "passed"


@pytest.mark.asyncio
async def test_engine_blocks_after_max_retries(db_factory):
    engine = PipelineEngine(steps=[MockFailStep()], session_factory=db_factory, max_retries=3)
    await engine.run("bbs.alert_close")

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == "blocked"

        executions = s.query(StepExecution).filter_by(page_id="bbs.alert_close").all()
        assert len(executions) == 3
        assert executions[-1].status == "blocked"


class SpecLoadStep(BaseStep):
    name = "spec_load"
    step_number = 1

    async def execute(self, context: StepContext) -> StepResult:
        return StepResult(
            success=True,
            artifacts={"spec": {"meta": {"id": "test"}, "operations": []}},
        )


class ApiContractStep(BaseStep):
    name = "api_contract"
    step_number = 2

    async def execute(self, context: StepContext) -> StepResult:
        # Verify previous step's spec is available in context
        assert context.spec is not None
        assert context.spec["meta"]["id"] == "test"
        return StepResult(
            success=True,
            artifacts={"api_contract": "openapi: '3.1.0'"},
        )


class CodeGenStep(BaseStep):
    name = "code_gen"
    step_number = 3

    async def execute(self, context: StepContext) -> StepResult:
        # Verify both spec and api_contract available
        assert context.spec is not None
        assert context.api_contract == "openapi: '3.1.0'"
        return StepResult(
            success=True,
            artifacts={"files": ["Component.tsx"]},
        )


@pytest.mark.asyncio
async def test_context_passes_between_steps(db_factory):
    steps = [SpecLoadStep(), ApiContractStep(), CodeGenStep()]
    engine = PipelineEngine(steps=steps, session_factory=db_factory)
    await engine.run("bbs.alert_close")

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.current_step == 3
        assert page.migration_status == "complete"


@pytest.mark.asyncio
async def test_cost_is_recorded(db_factory):
    class CostlyStep(BaseStep):
        name = "costly"
        step_number = 1

        async def execute(self, context: StepContext) -> StepResult:
            return StepResult(
                success=True,
                model_used="sonnet",
                input_tokens=5000,
                output_tokens=1500,
                cost=0.04,
            )

    engine = PipelineEngine(steps=[CostlyStep()], session_factory=db_factory)
    await engine.run("bbs.alert_close")

    with db_factory() as s:
        from src.db.models import CostLog
        logs = s.query(CostLog).filter_by(page_id="bbs.alert_close").all()
        assert len(logs) == 1
        assert logs[0].cost == 0.04
        assert logs[0].model == "sonnet"

        page = s.get(Page, "bbs.alert_close")
        assert page.total_cost == 0.04
        assert page.total_input_tokens == 5000
