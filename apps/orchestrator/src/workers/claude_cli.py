import asyncio
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CLIResult:
    success: bool
    output: str = ""
    error: str = ""
    cost: float = 0.0
    duration_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class ClaudeCLIWorker:
    def __init__(self, claude_path: str = "/opt/homebrew/bin/claude", mcp_config: str | None = None):
        self.claude_path = claude_path
        self.mcp_config = mcp_config

    async def invoke(
        self,
        prompt: str,
        model: str = "sonnet",
        max_turns: int = 10,
        cwd: str | Path | None = None,
        allowed_tools: list[str] | None = None,
        mcp_config: str | None = None,
    ) -> CLIResult:
        return await asyncio.to_thread(
            self._invoke_sync, prompt, model, max_turns, cwd, allowed_tools, mcp_config or self.mcp_config
        )

    def _invoke_sync(
        self,
        prompt: str,
        model: str,
        max_turns: int,
        cwd: str | Path | None,
        allowed_tools: list[str] | None,
        mcp_config: str | None = None,
    ) -> CLIResult:
        cmd = [
            self.claude_path,
            "--print",
            "--output-format", "json",
            "--model", model,
            "--max-turns", str(max_turns),
        ]

        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])

        if mcp_config:
            cmd.extend(["--mcp-config", mcp_config])

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(cwd) if cwd else None,
            )
            duration_ms = int((time.time() - start) * 1000)

            if result.returncode != 0:
                return CLIResult(
                    success=False,
                    error=result.stderr or f"Exit code: {result.returncode}",
                    duration_ms=duration_ms,
                )

            output_text, cost, input_tokens, output_tokens = self._parse_json_output(result.stdout)

            return CLIResult(
                success=True,
                output=output_text,
                cost=cost,
                duration_ms=duration_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

        except subprocess.TimeoutExpired:
            return CLIResult(success=False, error="Claude CLI timed out after 300s", duration_ms=300000)
        except FileNotFoundError:
            return CLIResult(success=False, error=f"Claude CLI not found at {self.claude_path}")

    def _parse_json_output(self, stdout: str) -> tuple[str, float, int, int]:
        text = ""
        cost = 0.0
        input_tokens = 0
        output_tokens = 0

        try:
            data = json.loads(stdout)
            if isinstance(data, dict):
                text = data.get("result", data.get("text", stdout))
                cost = data.get("total_cost_usd", data.get("cost_usd", 0.0))
                usage = data.get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                # Include cache tokens in input count
                cache_creation = usage.get("cache_creation_input_tokens", 0)
                cache_read = usage.get("cache_read_input_tokens", 0)
                if cache_creation or cache_read:
                    input_tokens += cache_creation + cache_read
            elif isinstance(data, list):
                text_parts = []
                for item in data:
                    if isinstance(item, dict):
                        if item.get("type") == "result":
                            text_parts.append(item.get("result", ""))
                            cost += item.get("total_cost_usd", 0.0)
                            u = item.get("usage", {})
                            input_tokens += u.get("input_tokens", 0)
                            output_tokens += u.get("output_tokens", 0)
                text = "\n".join(text_parts) if text_parts else stdout
        except json.JSONDecodeError:
            text = stdout

        return text, cost, input_tokens, output_tokens
