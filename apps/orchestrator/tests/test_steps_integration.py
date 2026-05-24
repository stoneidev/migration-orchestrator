import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.pipeline.steps.step1_spec_load import load_spec
from src.pipeline.steps.step2_spec_verify import verify_spec
from src.pipeline.steps.step3_api_contract import generate_api_contract
from src.workers.mcp import MCPWorker

SPECS_DIR = Path("/Users/stoni/Projects/silicon2/harness/specs")
MCP_PATH = Path("/Users/stoni/.mcp-servers/php-analyzer")


@pytest.mark.asyncio
async def test_step2_verify_spec_passes_for_alert_close():
    spec = load_spec("bbs.alert_close", specs_dir=SPECS_DIR)
    worker = MCPWorker(mcp_server_path=MCP_PATH)
    async with worker.connect():
        result = await verify_spec(spec, worker)
    assert result.success is True
    assert result.gaps == []


@pytest.mark.asyncio
async def test_step3_api_contract_generates_yaml():
    spec = load_spec("bbs.alert_close", specs_dir=SPECS_DIR)

    mock_response = MagicMock()
    mock_response.text = """openapi: "3.1.0"
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
    mock_response.input_tokens = 500
    mock_response.output_tokens = 200
    mock_response.model = "sonnet"
    mock_response.cost = 0.004

    async def fake_invoke(**kwargs):
        return mock_response

    with patch("src.pipeline.steps.step3_api_contract.analysis_worker") as mock_worker:
        mock_worker.invoke = fake_invoke
        result = await generate_api_contract(spec)

    assert result.success is True
    assert "openapi" in result.content
    assert "3.1.0" in result.content
