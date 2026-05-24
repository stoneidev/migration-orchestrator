import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.pipeline.steps.step4_react_gen import generate_react, ReactGenResult
from src.pipeline.steps.step5_java_gen import generate_java, JavaGenResult
from src.pipeline.steps.step1_spec_load import load_spec
from src.workers.claude_cli import CLIResult

SPECS_DIR = Path("/Users/stoni/Projects/silicon2/harness/specs")


@pytest.fixture
def spec():
    return load_spec("bbs.alert_close", specs_dir=SPECS_DIR)


@pytest.mark.asyncio
async def test_react_gen_with_mock_cli(spec, tmp_path):
    # Simulate Claude CLI creating a file
    (tmp_path / "page.tsx").write_text("export default function AlertClose() { return <div>Close</div> }")

    mock_worker = AsyncMock()
    mock_worker.invoke.return_value = CLIResult(success=True, output="Created page.tsx")

    result = await generate_react(
        spec=spec,
        api_contract="openapi: '3.1.0'\ninfo:\n  title: test",
        output_dir=tmp_path,
        worker=mock_worker,
    )

    assert result.success is True
    assert "page.tsx" in result.files_created
    mock_worker.invoke.assert_called_once()


@pytest.mark.asyncio
async def test_react_gen_fails_when_no_files(spec, tmp_path):
    mock_worker = AsyncMock()
    mock_worker.invoke.return_value = CLIResult(success=True, output="done")

    result = await generate_react(
        spec=spec,
        api_contract="",
        output_dir=tmp_path,
        worker=mock_worker,
    )

    assert result.success is False
    assert "No .tsx/.ts files" in result.error


@pytest.mark.asyncio
async def test_java_gen_with_mock_cli(spec, tmp_path):
    # Simulate Claude CLI creating Java files
    pkg_dir = tmp_path / "com" / "silicon2" / "admin" / "bbs"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "AlertCloseController.java").write_text("public class AlertCloseController {}")
    (pkg_dir / "AlertCloseService.java").write_text("public class AlertCloseService {}")

    mock_worker = AsyncMock()
    mock_worker.invoke.return_value = CLIResult(success=True, output="Created Java files")

    result = await generate_java(
        spec=spec,
        api_contract="openapi: '3.1.0'",
        output_dir=tmp_path,
        worker=mock_worker,
    )

    assert result.success is True
    assert len(result.files_created) == 2
    assert any("Controller" in f for f in result.files_created)


@pytest.mark.asyncio
async def test_java_gen_cli_failure(spec, tmp_path):
    mock_worker = AsyncMock()
    mock_worker.invoke.return_value = CLIResult(success=False, error="timeout")

    result = await generate_java(
        spec=spec,
        api_contract="",
        output_dir=tmp_path,
        worker=mock_worker,
    )

    assert result.success is False
    assert "timeout" in result.error
