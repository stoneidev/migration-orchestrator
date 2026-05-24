import pytest
from unittest.mock import MagicMock, patch

from src.workers.analysis import AnalysisWorker, LLMResponse


@pytest.mark.asyncio
async def test_analysis_worker_invoke_returns_response():
    mock_response = {
        "output": {"message": {"content": [{"text": "Hello from Claude"}]}},
        "usage": {"inputTokens": 100, "outputTokens": 20},
    }

    with patch("src.workers.analysis.AnalysisWorker._call_bedrock") as mock_call:
        mock_call.return_value = mock_response
        worker = AnalysisWorker(region="us-east-1")
        result = await worker.invoke(
            messages=[{"role": "user", "content": "test"}],
            model="haiku",
        )

    assert isinstance(result, LLMResponse)
    assert result.text == "Hello from Claude"
    assert result.input_tokens == 100
    assert result.output_tokens == 20


@pytest.mark.asyncio
async def test_analysis_worker_model_mapping():
    worker = AnalysisWorker(region="us-east-1")
    assert "haiku" in worker.get_model_id("haiku")
    assert "sonnet" in worker.get_model_id("sonnet")
    assert "opus" in worker.get_model_id("opus")
