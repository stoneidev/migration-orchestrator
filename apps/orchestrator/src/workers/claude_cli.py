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
    def __init__(self, claude_path: str = "/opt/homebrew/bin/claude"):
        self.claude_path = claude_path

    async def invoke(
        self,
        prompt: str,
        model: str = "sonnet",
        max_turns: int = 10,
        cwd: str | Path | None = None,
        allowed_tools: list[str] | None = None,
    ) -> CLIResult:
        return await asyncio.to_thread(
            self._invoke_sync, prompt, model, max_turns, cwd, allowed_tools
        )

    def _invoke_sync(
        self,
        prompt: str,
        model: str,
        max_turns: int,
        cwd: str | Path | None,
        allowed_tools: list[str] | None,
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
                usage = data.get("usage", {})
                input_tokens = usage.get("input_tokens", 0)
                output_tokens = usage.get("output_tokens", 0)
                cost = data.get("cost_usd", 0.0)
            elif isinstance(data, list):
                text_parts = []
                for item in data:
                    if isinstance(item, dict):
                        if item.get("type") == "result":
                            text_parts.append(item.get("result", ""))
                        elif item.get("type") == "usage":
                            input_tokens = item.get("input_tokens", 0)
                            output_tokens = item.get("output_tokens", 0)
                            cost = item.get("cost_usd", 0.0)
                text = "\n".join(text_parts) if text_parts else stdout
        except json.JSONDecodeError:
            text = stdout

        return text, cost, input_tokens, output_tokens
