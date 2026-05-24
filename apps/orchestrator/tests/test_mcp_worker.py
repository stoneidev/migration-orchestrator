import pytest
from pathlib import Path

from src.workers.mcp import MCPWorker

MCP_PATH = Path("/Users/stoni/.mcp-servers/php-analyzer")


@pytest.mark.asyncio
async def test_mcp_graph_stats():
    worker = MCPWorker(mcp_server_path=MCP_PATH)
    async with worker.connect():
        result = await worker.call_tool("php_graph_stats")
    assert isinstance(result, (dict, str))
    assert len(str(result)) > 10


@pytest.mark.asyncio
async def test_mcp_find_entry_points():
    worker = MCPWorker(mcp_server_path=MCP_PATH)
    async with worker.connect():
        result = await worker.call_tool("php_find_entry_points")
    assert isinstance(result, (dict, list, str))
    assert len(str(result)) > 10
