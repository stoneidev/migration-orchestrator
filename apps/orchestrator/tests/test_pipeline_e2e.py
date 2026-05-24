import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db.models import Base, Page, StepExecution, CostLog, Artifact
from src.pipeline.engine import PipelineEngine
from src.pipeline.steps.registry import Step1SpecLoad, Step2SpecVerify, Step3ApiContract
from src.workers.analysis import LLMResponse

SPECS_DIR = Path("/Users/stoni/Projects/silicon2/harness/specs")
MCP_PATH = Path("/Users/stoni/.mcp-servers/php-analyzer")


@pytest.fixture
def db_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        s.add(Page(id="bbs.alert_close", module="bbs", complexity="low", spec_status="complete"))
        s.commit()
    return factory


@pytest.mark.asyncio
async def test_steps_1_to_3_run_e2e(db_factory):
    """Step 1 (real spec) → Step 2 (real MCP) → Step 3 (mocked Bedrock) end-to-end."""

    mock_llm_response = LLMResponse(
        text="openapi: '3.1.0'\ninfo:\n  title: test\npaths: {}",
        input_tokens=500,
        output_tokens=200,
        model="sonnet",
        cost=0.004,
    )

    steps = [
        Step1SpecLoad(specs_dir=SPECS_DIR),
        Step2SpecVerify(mcp_server_path=MCP_PATH),
        Step3ApiContract(),
    ]

    with patch("src.pipeline.steps.step3_api_contract.analysis_worker") as mock_worker:
        async def fake_invoke(**kwargs):
            return mock_llm_response
        mock_worker.invoke = fake_invoke

        engine = PipelineEngine(steps=steps, session_factory=db_factory, max_retries=2)
        await engine.run("bbs.alert_close")

    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == "complete"
        assert page.current_step == 3

        executions = s.query(StepExecution).filter_by(page_id="bbs.alert_close").order_by(StepExecution.step_number).all()
        assert len(executions) == 3
        assert executions[0].step_name == "spec_load"
        assert executions[0].status == "passed"
        assert executions[1].step_name == "spec_verify"
        assert executions[1].status == "passed"
        assert executions[2].step_name == "api_contract"
        assert executions[2].status == "passed"

        # Verify artifacts saved
        artifacts = s.query(Artifact).filter_by(page_id="bbs.alert_close").all()
        assert len(artifacts) >= 1
        assert any(a.artifact_type == "api_contract" for a in artifacts)
