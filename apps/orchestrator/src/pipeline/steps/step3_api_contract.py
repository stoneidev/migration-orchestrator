from dataclasses import dataclass
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class ContractResult:
    success: bool
    content: str = ""
    error: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0


API_CONTRACT_PROMPT = """Read the spec file at {spec_path} and generate an OpenAPI 3.1 YAML file.

## Rules:
- RESTful endpoints: /api/v1/{{module}}/{{resource}}
- Common response wrapper: {{ success: boolean, data: object, error: object }}
- Support both offset and cursor pagination where applicable
- Include error codes and responses
- Base path: /api

## Output:
Write a file called `openapi.yaml` in the current directory.
The file must be valid OpenAPI 3.1.0 YAML.
Do NOT include markdown wrapping — just the raw YAML content in the file.
"""


async def generate_api_contract(
    spec: dict,
    output_dir: Path | None = None,
    worker: ClaudeCLIWorker | None = None,
) -> ContractResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    meta = spec.get("meta", {})
    page_id = meta.get("id", "unknown")

    # Find spec file path
    from src.config import Settings
    settings = Settings()
    spec_path = settings.specs_dir / f"{page_id}.aispec.json"

    if not spec_path.exists():
        return ContractResult(success=False, error=f"Spec file not found: {spec_path}")

    # Output directory
    if output_dir is None:
        output_dir = Path(settings.screenshots_dir) / page_id.replace(".", "_")
    output_dir.mkdir(parents=True, exist_ok=True)

    prompt = API_CONTRACT_PROMPT.format(spec_path=str(spec_path))

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="haiku",
        max_turns=5,
        cwd=output_dir,
        allowed_tools=["Write", "Read"],
    )

    if not result.success:
        return ContractResult(success=False, error=result.error)

    # Check if openapi.yaml was created
    yaml_file = output_dir / "openapi.yaml"
    if yaml_file.exists():
        content = yaml_file.read_text()
        return ContractResult(
            success=True,
            content=content,
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )

    # Maybe it wrote it with a different name
    for f in output_dir.glob("*.yaml"):
        content = f.read_text()
        return ContractResult(success=True, content=content, cost=result.cost)
    for f in output_dir.glob("*.yml"):
        content = f.read_text()
        return ContractResult(success=True, content=content, cost=result.cost)

    return ContractResult(success=False, error=f"CLI succeeded but no YAML file generated. Output: {result.output[:200]}")
