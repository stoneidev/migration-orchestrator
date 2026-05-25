"""Bedrock-backed analysis worker.

Cost is computed from a 4-axis price table (input / output / cache_write /
cache_read) per 1k tokens, matching Anthropic's published pricing for the
Claude 4 family. The previous 2-axis table priced cached reads at the same
rate as fresh input (an order of magnitude too high) and used outdated
Haiku numbers; both are corrected here.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any

import boto3


MODEL_IDS = {
    "haiku": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
    "sonnet": "us.anthropic.claude-sonnet-4-6",
    "opus": "us.anthropic.claude-opus-4-6-v1",
}


# Prices are USD per 1k tokens. Source: Anthropic public pricing for the
# Claude 4 family. Cache writes are billed at 1.25x input; cache reads at
# 0.10x input.
MODEL_PRICING: dict[str, dict[str, float]] = {
    "haiku": {
        "input": 0.0008,
        "output": 0.004,
        "cache_write": 0.001,
        "cache_read": 0.00008,
    },
    "sonnet": {
        "input": 0.003,
        "output": 0.015,
        "cache_write": 0.00375,
        "cache_read": 0.0003,
    },
    "opus": {
        "input": 0.015,
        "output": 0.075,
        "cache_write": 0.01875,
        "cache_read": 0.0015,
    },
}


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    cost: float
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0


def compute_cost(
    model: str,
    *,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """USD cost for a single LLM call, given the four token classes."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING["sonnet"])
    cost = (
        input_tokens * pricing["input"]
        + output_tokens * pricing["output"]
        + cache_creation_tokens * pricing.get("cache_write", pricing["input"])
        + cache_read_tokens * pricing.get("cache_read", pricing["input"])
    )
    return round(cost / 1000, 6)


class AnalysisWorker:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._client = None

    def get_model_id(self, model_name: str) -> str:
        if model_name not in MODEL_IDS:
            raise ValueError(f"Unknown model: {model_name}. Use: {list(MODEL_IDS.keys())}")
        return MODEL_IDS[model_name]

    def _get_client(self):
        if self._client is None:
            from botocore.config import Config
            config = Config(read_timeout=300, connect_timeout=10, retries={"max_attempts": 2})
            self._client = boto3.client("bedrock-runtime", region_name=self.region, config=config)
        return self._client

    async def invoke(
        self,
        messages: list[dict],
        model: str = "sonnet",
        system: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
    ) -> LLMResponse:
        return await asyncio.to_thread(
            self._invoke_sync, messages, model, system, max_tokens, temperature
        )

    def _invoke_sync(
        self,
        messages: list[dict],
        model: str,
        system: str | None,
        max_tokens: int,
        temperature: float,
    ) -> LLMResponse:
        model_id = self.get_model_id(model)

        body: dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system:
            body["system"] = system

        response = self._call_bedrock(model_id, body)

        text = ""
        input_tokens = 0
        output_tokens = 0
        cache_creation = 0
        cache_read = 0

        # Format 1: InvokeModel response (content at top level).
        content_blocks = response.get("content", [])
        if content_blocks:
            for block in content_blocks:
                if isinstance(block, dict) and block.get("text"):
                    text += block["text"]
            usage = response.get("usage", {})
            input_tokens = usage.get("input_tokens", 0)
            output_tokens = usage.get("output_tokens", 0)
            cache_creation = usage.get("cache_creation_input_tokens", 0)
            cache_read = usage.get("cache_read_input_tokens", 0)
        else:
            # Format 2: Converse API (output.message.content).
            output = response.get("output", {})
            message = output.get("message", {})
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("text"):
                    text += block["text"]
            usage = response.get("usage", {})
            input_tokens = usage.get("inputTokens", usage.get("input_tokens", 0))
            output_tokens = usage.get("outputTokens", usage.get("output_tokens", 0))
            cache_creation = usage.get(
                "cacheCreationInputTokens", usage.get("cache_creation_input_tokens", 0)
            )
            cache_read = usage.get(
                "cacheReadInputTokens", usage.get("cache_read_input_tokens", 0)
            )

        cost = compute_cost(
            model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation,
            cache_read_tokens=cache_read,
        )

        return LLMResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_creation_tokens=cache_creation,
            cache_read_tokens=cache_read,
            model=model,
            cost=cost,
        )

    def _call_bedrock(self, model_id: str, body: dict) -> dict:
        client = self._get_client()
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        return json.loads(response["body"].read())
