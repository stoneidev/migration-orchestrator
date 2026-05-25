import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.pipeline.steps.step1_spec_load import load_spec
from src.pipeline.steps.step2_spec_verify import verify_spec
from src.pipeline.steps.step3_api_contract import generate_api_contract
from src.workers.claude_cli import CLIResult
from src.workers.mcp import MCPWorker


async def _mock_cli_invoke(**kwargs):
    cwd = kwargs.get("cwd")
    if cwd:
        out = Path(cwd)
        out.mkdir(parents=True, exist_ok=True)
        (out / "openapi.yaml").write_text(
            """openapi: "3.1.0"
info:
  title: bbs.alert_close API
  version: "1.0.0"
paths:
  /api/v1/admin/bbs/alert-close:
    get:
      summary: 관리자 경고 팝업 닫기
      responses:
        "200":
          description: Success
"""
        )
    return CLIResult(
        success=True,
        output="done",
        cost=0.004,
        input_tokens=500,
        output_tokens=200,
    )


@pytest.mark.asyncio
async def test_step2_verify_spec_passes_for_alert_close(specs_dir, mcp_server_path):
    spec = load_spec("bbs.alert_close", specs_dir=specs_dir)
    worker = MCPWorker(mcp_server_path=mcp_server_path)
    async with worker.connect():
        result = await verify_spec(spec, worker)
    assert result.success is True
    assert result.gaps == []


@pytest.mark.asyncio
async def test_step3_api_contract_generates_yaml(specs_dir):
    spec = load_spec("bbs.alert_close", specs_dir=specs_dir)

    with patch("src.pipeline.steps.step3_api_contract.ClaudeCLIWorker") as mock_worker_cls:
        mock_worker_cls.return_value.invoke = AsyncMock(side_effect=_mock_cli_invoke)
        result = await generate_api_contract(spec)

    assert result.success is True
    assert "openapi" in result.content
    assert "3.1.0" in result.content
