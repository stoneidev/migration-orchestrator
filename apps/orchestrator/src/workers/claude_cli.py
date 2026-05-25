"""Wrapper around the local ``claude`` CLI binary.

The wrapper enforces a real wall-clock timeout: a watchdog thread runs the
process inside its own POSIX session and SIGTERM/SIGKILLs the entire group
when the deadline is exceeded. Live stream-json events are forwarded to the
WebSocket event bus as they arrive.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_TIMEOUT_SECONDS = 600


@dataclass
class CLIResult:
    success: bool
    output: str = ""
    error: str = ""
    cost: float = 0.0
    duration_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    timed_out: bool = False
    raw_events: list[dict] = field(default_factory=list)


class ClaudeCLIWorker:
    def __init__(
        self,
        claude_path: str = "/opt/homebrew/bin/claude",
        mcp_config: str | None = None,
        default_timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.claude_path = claude_path
        self.mcp_config = mcp_config
        self.default_timeout = default_timeout

    async def invoke(
        self,
        prompt: str,
        model: str = "sonnet",
        max_turns: int = 10,
        cwd: str | Path | None = None,
        allowed_tools: list[str] | None = None,
        mcp_config: str | None = None,
        timeout: int | None = None,
    ) -> CLIResult:
        return await asyncio.to_thread(
            self._invoke_sync,
            prompt,
            model,
            max_turns,
            cwd,
            allowed_tools,
            mcp_config or self.mcp_config,
            timeout if timeout is not None else self.default_timeout,
        )

    def _invoke_sync(
        self,
        prompt: str,
        model: str,
        max_turns: int,
        cwd: str | Path | None,
        allowed_tools: list[str] | None,
        mcp_config: str | None,
        timeout: int,
    ) -> CLIResult:
        cmd = [
            self.claude_path,
            "--print",
            "--verbose",
            "--output-format", "stream-json",
            "--model", model,
            "--max-turns", str(max_turns),
        ]

        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])

        if mcp_config:
            cmd.extend(["--mcp-config", mcp_config])

        start = time.time()
        try:
            proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(cwd) if cwd else None,
                start_new_session=True,
            )
        except FileNotFoundError:
            return CLIResult(success=False, error=f"Claude CLI not found at {self.claude_path}")

        # Watchdog: kill the entire process group when the wall-clock deadline
        # passes. SIGTERM first, then SIGKILL 2s later if still alive.
        deadline = start + timeout
        timed_out_flag = {"value": False}

        def _watchdog() -> None:
            while time.time() < deadline:
                if proc.poll() is not None:
                    return
                time.sleep(0.5)
            if proc.poll() is None:
                timed_out_flag["value"] = True
                _terminate_group(proc, grace_seconds=2.0)

        watchdog = threading.Thread(target=_watchdog, name="claude-cli-watchdog", daemon=True)
        watchdog.start()

        try:
            assert proc.stdin is not None
            proc.stdin.write(prompt)
            proc.stdin.close()
        except (BrokenPipeError, OSError):
            pass

        output_lines: list[str] = []
        result_data: dict | None = None
        raw_events: list[dict] = []

        assert proc.stdout is not None
        try:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                output_lines.append(line)

                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                raw_events.append(event)
                event_type = event.get("type", "")

                from src.api.ws.events import event_bus
                if event_type == "assistant":
                    msg = event.get("message", {})
                    for block in msg.get("content", []):
                        if block.get("type") == "tool_use":
                            event_bus.emit("cli:tool_use", {
                                "tool": block.get("name", ""),
                                "input": str(block.get("input", {}))[:100],
                            })
                        elif block.get("type") == "text":
                            text = block.get("text", "")[:100]
                            if text:
                                event_bus.emit("cli:text", {"text": text})
                elif event_type == "result":
                    result_data = event
        except Exception:
            pass

        # Wait for process to actually exit so watchdog can finish.
        try:
            proc.wait(timeout=max(1.0, deadline - time.time() + 5))
        except subprocess.TimeoutExpired:
            _terminate_group(proc, grace_seconds=2.0)

        duration_ms = int((time.time() - start) * 1000)

        if timed_out_flag["value"]:
            return CLIResult(
                success=False,
                error=f"Claude CLI timed out after {timeout}s",
                duration_ms=duration_ms,
                timed_out=True,
                raw_events=raw_events,
            )

        if proc.returncode != 0 and result_data is None:
            stderr = proc.stderr.read() if proc.stderr else ""
            return CLIResult(
                success=False,
                error=stderr or f"Exit code: {proc.returncode}",
                duration_ms=duration_ms,
                raw_events=raw_events,
            )

        if result_data:
            output_text = result_data.get("result", "")
            cost = result_data.get("total_cost_usd", 0.0)
            usage = result_data.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            cache_creation = usage.get("cache_creation_input_tokens", 0)
            cache_read = usage.get("cache_read_input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
        else:
            output_text = "\n".join(output_lines[-5:]) if output_lines else ""
            cost = 0.0
            input_tokens = 0
            cache_creation = 0
            cache_read = 0
            output_tokens = 0

        return CLIResult(
            success=True,
            output=output_text[:2000],
            cost=cost,
            duration_ms=duration_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation,
            cache_read_tokens=cache_read,
            raw_events=raw_events,
        )


def _terminate_group(proc: subprocess.Popen, grace_seconds: float = 2.0) -> None:
    """SIGTERM the process group, then SIGKILL after ``grace_seconds`` if still alive."""
    try:
        pgid = os.getpgid(proc.pid)
    except (ProcessLookupError, OSError):
        return

    try:
        os.killpg(pgid, signal.SIGTERM)
    except (ProcessLookupError, OSError):
        return

    deadline = time.time() + grace_seconds
    while time.time() < deadline:
        if proc.poll() is not None:
            return
        time.sleep(0.1)

    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, OSError):
        return
