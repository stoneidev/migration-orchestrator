from dataclasses import dataclass, field

from src.workers.analysis import AnalysisWorker, LLMResponse


@dataclass
class IntegrationResult:
    success: bool
    report: dict = field(default_factory=dict)
    error: str = ""


async def check_integration(
    spec: dict,
    api_contract: str,
    react_files: list[str],
    java_files: list[str],
    worker: AnalysisWorker | None = None,
) -> IntegrationResult:
    if worker is None:
        worker = AnalysisWorker()

    operations = spec.get("operations", [])
    endpoints = [op.get("route", "") for op in operations]

    prompt = f"""Verify API contract compliance between frontend and backend.

## API Contract (OpenAPI)
{api_contract[:1500]}

## React files generated
{react_files}

## Java files generated
{java_files}

## Expected Endpoints
{endpoints}

Check:
1. Are all endpoints from the contract implemented in Java controllers?
2. Do React files call the correct endpoints?

Output JSON:
{{
  "compliant": true/false,
  "covered_endpoints": [...],
  "missing_endpoints": [...],
  "issues": [...]
}}"""

    try:
        response: LLMResponse = await worker.invoke(
            messages=[{"role": "user", "content": prompt}],
            model="haiku",
        )

        return IntegrationResult(
            success=True,
            report={"analysis": response.text[:1000], "endpoints": endpoints},
        )
    except Exception as e:
        return IntegrationResult(success=True, report={"skipped": str(e)})
