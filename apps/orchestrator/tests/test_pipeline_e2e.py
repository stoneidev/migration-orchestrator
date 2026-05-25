import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db.models import Base, Page, StepExecution, Artifact
from src.pipeline.engine import PipelineEngine
from src.pipeline.steps.registry import (
    Step1SpecLoad, Step2SpecVerify, Step3ApiContract,
    Step4ReactGen, Step5JavaGen, Step6JavaTest,
    Step7Integration, Step8Equivalence, Step9Complete,
)
from src.workers.claude_cli import CLIResult


@pytest.fixture
def db_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        s.add(Page(id="bbs.alert_close", module="bbs", complexity="low", spec_status="complete"))
        s.commit()
    return factory


async def _mock_cli_invoke(**kwargs):
    cwd = kwargs.get("cwd")
    if cwd:
        out = Path(cwd)
        out.mkdir(parents=True, exist_ok=True)
        (out / "openapi.yaml").write_text(
            "openapi: '3.1.0'\ninfo:\n  title: test\npaths:\n"
            "  /api/v1/admin/bbs/alert-close:\n    get:\n      summary: close alert\n"
        )
    return CLIResult(
        success=True,
        output="done",
        cost=0.004,
        input_tokens=500,
        output_tokens=200,
    )


@pytest.mark.asyncio
async def test_steps_1_to_3_run_e2e(db_factory, specs_dir, mcp_server_path):
    """Step 1 (real spec) → Step 2 (real MCP) → Step 3 (mocked CLI) end-to-end."""

    steps = [
        Step1SpecLoad(specs_dir=specs_dir),
        Step2SpecVerify(mcp_server_path=mcp_server_path),
        Step3ApiContract(),
    ]

    with patch("src.pipeline.steps.step3_api_contract.ClaudeCLIWorker") as mock_worker_cls:
        mock_worker_cls.return_value.invoke = AsyncMock(side_effect=_mock_cli_invoke)
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

        artifacts = s.query(Artifact).filter_by(page_id="bbs.alert_close").all()
        assert len(artifacts) >= 1
        assert any(a.artifact_type == "api_contract" for a in artifacts)


@pytest.mark.asyncio
async def test_full_9_step_pipeline(db_factory, tmp_path, specs_dir, mcp_server_path):
    """Complete 9-step pipeline with mocked code generation."""

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

    steps = [
        Step1SpecLoad(specs_dir=specs_dir),
        Step2SpecVerify(mcp_server_path=mcp_server_path),
        Step3ApiContract(),
        Step4ReactGen(output_base=tmp_path / "frontend"),
        Step5JavaGen(output_base=tmp_path / "backend"),
        Step6JavaTest(output_base=tmp_path / "test"),
        Step7Integration(
            frontend_base=tmp_path / "frontend",
            backend_dir=tmp_path / "backend",
        ),
        Step8Equivalence(mcp_server_path=mcp_server_path),
        Step9Complete(),
    ]

    mock_cli = AsyncMock()
    mock_cli.invoke.return_value = CLIResult(success=True, output="done", cost=0.01, duration_ms=5000)

    with patch("src.pipeline.steps.step3_api_contract.ClaudeCLIWorker") as mock_step3_cli, \
         patch("src.pipeline.steps.step4_react_gen.ClaudeCLIWorker", return_value=mock_cli), \
         patch("src.pipeline.steps.step5_java_gen.ClaudeCLIWorker", return_value=mock_cli), \
         patch("src.pipeline.steps.step6_java_test.ClaudeCLIWorker", return_value=mock_cli), \
         patch("src.pipeline.steps.step7_integration.ClaudeCLIWorker", return_value=mock_cli):

        mock_step3_cli.return_value.invoke = AsyncMock(side_effect=_mock_cli_invoke)
        engine = PipelineEngine(steps=steps, session_factory=db_factory, max_retries=2)
        await engine.run("bbs.alert_close")

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
