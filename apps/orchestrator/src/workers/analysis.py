import asyncio
import json
from dataclasses import dataclass
from typing import Any

import boto3


MODEL_IDS = {
    "haiku": "anthropic.claude-haiku-4-5-20251001-v1:0",
    "sonnet": "anthropic.claude-sonnet-4-6-20250514-v1:0",
    "opus": "anthropic.claude-opus-4-6-20250514-v1:0",
}

MODEL_PRICING = {
    "haiku": {"input": 0.001, "output": 0.005},
    "sonnet": {"input": 0.003, "output": 0.015},
    "opus": {"input": 0.015, "output": 0.075},
}


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str
    cost: float


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
            self._client = boto3.client("bedrock-runtime", region_name=self.region)
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

        output = response.get("output", {})
        message = output.get("message", {})
        content_blocks = message.get("content", [])
        text = ""
        for block in content_blocks:
            if isinstance(block, dict) and block.get("text"):
                text += block["text"]

        usage = response.get("usage", {})
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)

        pricing = MODEL_PRICING.get(model, MODEL_PRICING["sonnet"])
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000

        return LLMResponse(
            text=text,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
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
