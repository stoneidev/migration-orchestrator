import pytest

from src.workers.claude_cli import ClaudeCLIWorker


@pytest.mark.asyncio
async def test_claude_cli_basic_invocation():
    worker = ClaudeCLIWorker()
    result = await worker.invoke(
        prompt="Respond with exactly: HELLO",
        model="sonnet",
        max_turns=1,
    )
    assert result.success is True
    assert "HELLO" in result.output.upper()
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_claude_cli_returns_structured_result():
    worker = ClaudeCLIWorker()
    result = await worker.invoke(
        prompt="What is 2+2? Reply with just the number.",
        model="haiku",
        max_turns=1,
    )
    assert result.success is True
    assert "4" in result.output
    assert result.duration_ms > 0
