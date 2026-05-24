import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPWorker:
    def __init__(self, mcp_server_path: Path, python_path: str = "/opt/homebrew/opt/python@3.11/libexec/bin/python3"):
        self.server_path = mcp_server_path
        self.python_path = python_path
        self._session: ClientSession | None = None

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

    async def call_tool(self, tool_name: str, arguments: dict | None = None) -> Any:
        if self._session is None:
            raise RuntimeError("Not connected. Use 'async with worker.connect()' first.")

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

    async def close(self) -> None:
        pass
