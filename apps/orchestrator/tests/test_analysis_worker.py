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


@pytest.mark.asyncio
async def test_analysis_worker_extracts_cache_tokens_converse():
    mock_response = {
        "output": {"message": {"content": [{"text": "hi"}]}},
        "usage": {
            "inputTokens": 100,
            "outputTokens": 20,
            "cacheCreationInputTokens": 50,
            "cacheReadInputTokens": 1000,
        },
    }
    with patch("src.workers.analysis.AnalysisWorker._call_bedrock", return_value=mock_response):
        worker = AnalysisWorker(region="us-east-1")
        result = await worker.invoke(messages=[{"role": "user", "content": "x"}], model="sonnet")

    assert result.cache_creation_tokens == 50
    assert result.cache_read_tokens == 1000
    # Cost must include cache reads, but at the lower cache_read rate.
    assert result.cost > 0


@pytest.mark.asyncio
async def test_analysis_worker_extracts_cache_tokens_invoke_model_format():
    mock_response = {
        "content": [{"text": "hi"}],
        "usage": {
            "input_tokens": 100,
            "output_tokens": 20,
            "cache_creation_input_tokens": 50,
            "cache_read_input_tokens": 1000,
        },
    }
    with patch("src.workers.analysis.AnalysisWorker._call_bedrock", return_value=mock_response):
        worker = AnalysisWorker(region="us-east-1")
        result = await worker.invoke(messages=[{"role": "user", "content": "x"}], model="sonnet")

    assert result.cache_creation_tokens == 50
    assert result.cache_read_tokens == 1000
