from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class ReactGenResult:
    success: bool
    files_created: list[str] = field(default_factory=list)
    output: str = ""
    error: str = ""


REACT_SYSTEM_PROMPT = """You are a React/TypeScript specialist generating Next.js components.

Rules:
- Use TypeScript strict mode
- Use shadcn/ui components where appropriate
- Use TanStack Query for API calls
- Follow FSD (Feature-Sliced Design) structure
- Generate ONLY code files, no explanations
- Each component in its own file
- Include proper imports

Output files directly. Do NOT wrap in markdown code blocks."""


async def generate_react(
    spec: dict,
    api_contract: str,
    output_dir: Path,
    worker: ClaudeCLIWorker | None = None,
) -> ReactGenResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    meta = spec.get("meta", {})
    operations = spec.get("operations", [])
    business_rules = spec.get("business_rules", [])

    ops_desc = "\n".join(
        f"- {op.get('id', '')}: {op.get('name', '')} ({op.get('http_method', 'GET')} {op.get('route', '')})"
        for op in operations
    )

    rules_desc = "\n".join(
        f"- {rule.get('id', '')}: {rule.get('description', '')}"
        for rule in business_rules[:10]
    )

    prompt = f"""{REACT_SYSTEM_PROMPT}

## Page Specification
- ID: {meta.get('id', '')}
- Title: {meta.get('title', '')}

## Operations
{ops_desc}

## Business Rules
{rules_desc}

## API Contract (OpenAPI)
{api_contract[:2000]}

## Task
Generate a Next.js page component and any sub-components for this admin page.
Place files in the current directory.
Use 'use client' directive where needed.
Include a page.tsx as the main entry point."""

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=10,
        cwd=output_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return ReactGenResult(success=False, error=result.error)

    created_files = []
    if output_dir.exists():
        for f in output_dir.rglob("*.tsx"):
            created_files.append(str(f.relative_to(output_dir)))
        for f in output_dir.rglob("*.ts"):
            if not f.name.endswith(".d.ts"):
                created_files.append(str(f.relative_to(output_dir)))

    return ReactGenResult(
        success=len(created_files) > 0,
        files_created=created_files,
        output=result.output[:1000],
        error="" if created_files else "No .tsx/.ts files generated",
    )
