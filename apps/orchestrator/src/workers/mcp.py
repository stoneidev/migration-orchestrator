import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

log = logging.getLogger(__name__)


class MCPWorker:
    def __init__(self, mcp_server_path: Path, python_path: str = "python3"):
        self.server_path = mcp_server_path
        self.python_path = python_path
        self._session: ClientSession | None = None
        self._context_stack: Any = None

    @asynccontextmanager
    async def connect(self):
        server_params = StdioServerParameters(
            command=self.python_path,
            args=["server.py"],
            cwd=str(self.server_path),
        )
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                self._session = session
                yield self
                self._session = None

    async def start(self) -> None:
        """Start MCP server and keep connection alive (for app-lifetime use)."""
        server_params = StdioServerParameters(
            command=self.python_path,
            args=["server.py"],
            cwd=str(self.server_path),
        )
        self._stdio_ctx = stdio_client(server_params)
        read_stream, write_stream = await self._stdio_ctx.__aenter__()
        self._client_ctx = ClientSession(read_stream, write_stream)
        self._session = await self._client_ctx.__aenter__()
        await self._session.initialize()
        log.info("MCP server started and connected: %s", self.server_path)

    async def stop(self) -> None:
        """Gracefully shut down the persistent MCP connection."""
        if self._session is not None:
            try:
                await self._client_ctx.__aexit__(None, None, None)
            except Exception:
                pass
            self._session = None
        if hasattr(self, "_stdio_ctx") and self._stdio_ctx is not None:
            try:
                await self._stdio_ctx.__aexit__(None, None, None)
            except Exception:
                pass
        log.info("MCP server stopped")

    @property
    def connected(self) -> bool:
        return self._session is not None

    async def call_tool(self, tool_name: str, arguments: dict | None = None) -> Any:
        if self._session is None:
            raise RuntimeError("MCP not connected. Call start() or use 'async with worker.connect()' first.")

        result = await self._session.call_tool(tool_name, arguments=arguments or {})

        text_parts = []
        for content in result.content:
            if hasattr(content, "text"):
                text_parts.append(content.text)

        combined = "\n".join(text_parts)
        try:
            return json.loads(combined)
        except json.JSONDecodeError:
            return combined


# App-level singleton
_mcp_worker: MCPWorker | None = None


def get_mcp_worker() -> MCPWorker | None:
    return _mcp_worker


async def start_mcp_worker(mcp_server_path: Path, python_path: str = "python3") -> MCPWorker:
    global _mcp_worker
    if _mcp_worker is not None and _mcp_worker.connected:
        return _mcp_worker
    _mcp_worker = MCPWorker(mcp_server_path=mcp_server_path, python_path=python_path)
    await _mcp_worker.start()
    return _mcp_worker


async def stop_mcp_worker() -> None:
    global _mcp_worker
    if _mcp_worker is not None:
        await _mcp_worker.stop()
        _mcp_worker = None
