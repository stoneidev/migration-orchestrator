from dataclasses import dataclass

from src.workers.analysis import AnalysisWorker

analysis_worker = AnalysisWorker()


@dataclass
class ContractResult:
    success: bool
    content: str = ""
    error: str = ""
    input_tokens: int = 0
    output_tokens: int = 0


async def generate_api_contract(spec: dict) -> ContractResult:
    meta = spec.get("meta", {})
    operations = spec.get("operations", [])

    ops_summary = []
    for op in operations:
        ops_summary.append({
            "id": op.get("id", ""),
            "name": op.get("name", ""),
            "http_method": op.get("http_method", "GET"),
            "route": op.get("route", ""),
        })

    prompt = f"""Generate an OpenAPI 3.1.0 specification for the following page:

Page: {meta.get('id', 'unknown')}
Title: {meta.get('title', '')}

Operations:
{ops_summary}

Rules:
- RESTful URL pattern: /api/v1/admin/{{module}}/{{resource}}
- Common response wrapper: {{ success, data, error, meta }}
- Support both offset and cursor pagination
- Include error codes

Output ONLY valid YAML. No markdown wrapping. No explanations."""

    response = await analysis_worker.invoke(
        messages=[{"role": "user", "content": prompt}],
        model="sonnet",
        system="You are an API architect. Generate OpenAPI 3.1.0 specs.",
    )

    if not response.text.strip():
        return ContractResult(success=False, error="Empty response from LLM")

    content = response.text.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])

    return ContractResult(
        success=True,
        content=content,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
    )
