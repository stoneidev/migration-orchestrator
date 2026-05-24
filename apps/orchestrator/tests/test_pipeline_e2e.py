import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db.models import Base, Page, StepExecution, CostLog, Artifact
from src.pipeline.engine import PipelineEngine, StepContext, StepResult, BaseStep
from src.pipeline.steps.registry import (
    Step1SpecLoad, Step2SpecVerify, Step3ApiContract,
    Step4ReactGen, Step5JavaGen, Step6JavaTest,
    Step7Integration, Step8Equivalence, Step9Complete,
    create_pipeline_steps,
)
from src.workers.analysis import LLMResponse
from src.workers.claude_cli import CLIResult

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


@pytest.mark.asyncio
async def test_full_9_step_pipeline(db_factory, tmp_path):
    """Complete 9-step pipeline for bbs.alert_close with mocked code generation."""

    mock_llm_response = LLMResponse(
        text="openapi: '3.1.0'\ninfo:\n  title: test\npaths:\n  /api/v1/admin/bbs/alert-close:\n    get:\n      summary: close alert",
        input_tokens=500, output_tokens=200, model="sonnet", cost=0.004,
    )

    # Prepare mock output dirs with fake generated files
    react_dir = tmp_path / "frontend" / "bbs" / "alert_close"
    react_dir.mkdir(parents=True)
    (react_dir / "page.tsx").write_text("export default function AlertClose() { return <div/> }")
    (react_dir / "useAlertClose.ts").write_text("export const useAlertClose = () => {}")

    java_dir = tmp_path / "backend" / "bbs" / "alert_close"
    java_dir.mkdir(parents=True)
    (java_dir / "AlertCloseController.java").write_text("@RestController class AlertCloseController {}")
    (java_dir / "AlertCloseService.java").write_text("@Service class AlertCloseService {}")

    test_dir = tmp_path / "test" / "bbs" / "alert_close"
    test_dir.mkdir(parents=True)
    (test_dir / "AlertCloseControllerTest.java").write_text("@Test class AlertCloseControllerTest {}")

    # Build steps with mocked CLI workers
    steps = [
        Step1SpecLoad(specs_dir=SPECS_DIR),
        Step2SpecVerify(mcp_server_path=MCP_PATH),
        Step3ApiContract(),
        Step4ReactGen(output_base=tmp_path / "frontend"),
        Step5JavaGen(output_base=tmp_path / "backend"),
        Step6JavaTest(output_base=tmp_path / "test"),
        Step7Integration(),
        Step8Equivalence(mcp_server_path=MCP_PATH),
        Step9Complete(),
    ]

    mock_cli = AsyncMock()
    mock_cli.invoke.return_value = CLIResult(success=True, output="done", cost=0.01, duration_ms=5000)

    with patch("src.pipeline.steps.step3_api_contract.analysis_worker") as mock_analysis, \
         patch("src.pipeline.steps.step4_react_gen.ClaudeCLIWorker", return_value=mock_cli), \
         patch("src.pipeline.steps.step5_java_gen.ClaudeCLIWorker", return_value=mock_cli), \
         patch("src.pipeline.steps.step6_java_test.ClaudeCLIWorker", return_value=mock_cli), \
         patch("src.pipeline.steps.step7_integration.AnalysisWorker") as mock_int_worker:

        async def fake_invoke(**kwargs):
            return mock_llm_response
        mock_analysis.invoke = fake_invoke

        mock_int_instance = AsyncMock()
        mock_int_instance.invoke.return_value = mock_llm_response
        mock_int_worker.return_value = mock_int_instance

        engine = PipelineEngine(steps=steps, session_factory=db_factory, max_retries=2)
        await engine.run("bbs.alert_close")

    # Verify complete execution
    with db_factory() as s:
        page = s.get(Page, "bbs.alert_close")
        assert page.migration_status == "complete"
        assert page.current_step == 9
        assert page.completed_at is not None

        executions = s.query(StepExecution).filter_by(page_id="bbs.alert_close").order_by(StepExecution.step_number).all()
        assert len(executions) == 9
        for ex in executions:
            assert ex.status == "passed", f"Step {ex.step_number} ({ex.step_name}) failed: {ex.error_message}"

        artifacts = s.query(Artifact).filter_by(page_id="bbs.alert_close").all()
        assert len(artifacts) >= 1
