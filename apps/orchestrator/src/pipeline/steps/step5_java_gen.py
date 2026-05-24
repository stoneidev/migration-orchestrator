from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class JavaGenResult:
    success: bool
    files_created: list[str] = field(default_factory=list)
    output: str = ""
    error: str = ""


JAVA_SYSTEM_PROMPT = """You are a Java/Spring Boot specialist generating DDD/Hexagonal architecture code.

Rules:
- Java 21, Spring Boot 3.4
- DDD/Hexagonal: domain/model, domain/service, domain/repository (layer별)
- Feature별: application/ (UseCase), adapter/in/web/ (Controller), adapter/out/persistence/ (JPA)
- Use Lombok (@Data, @Builder, @RequiredArgsConstructor)
- Use MapStruct for DTO mapping
- Base package: com.silicon2.admin
- RESTful endpoints with common ApiResponse wrapper
- Include Flyway migration SQL if DB tables needed

Output files directly. Do NOT wrap in markdown code blocks."""


async def generate_java(
    spec: dict,
    api_contract: str,
    output_dir: Path,
    worker: ClaudeCLIWorker | None = None,
) -> JavaGenResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    meta = spec.get("meta", {})
    operations = spec.get("operations", [])
    business_rules = spec.get("business_rules", [])
    data_layer = spec.get("data_layer", {})

    ops_desc = "\n".join(
        f"- {op.get('id', '')}: {op.get('name', '')} ({op.get('http_method', 'GET')} {op.get('route', '')})"
        for op in operations
    )

    rules_desc = "\n".join(
        f"- {rule.get('id', '')}: {rule.get('description', '')}"
        for rule in business_rules[:10]
    )

    tables = data_layer.get("tables", [])
    tables_desc = "\n".join(
        f"- {t.get('name', '')}: {[c.get('name', '') for c in t.get('columns', [])[:5]]}"
        for t in tables[:5]
    )

    prompt = f"""{JAVA_SYSTEM_PROMPT}

## Page Specification
- ID: {meta.get('id', '')}
- Title: {meta.get('title', '')}
- Module: {meta.get('module', meta.get('id', '').split('.')[0])}

## Operations
{ops_desc}

## Business Rules
{rules_desc}

## Database Tables
{tables_desc}

## API Contract (OpenAPI)
{api_contract[:2000]}

## Task
Generate Spring Boot implementation for this admin page.
Create proper package structure under the current directory.
Include Controller, Service (UseCase), Repository interface, and Entity."""

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=15,
        cwd=output_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return JavaGenResult(success=False, error=result.error)

    created_files = []
    if output_dir.exists():
        for f in output_dir.rglob("*.java"):
            created_files.append(str(f.relative_to(output_dir)))

    return JavaGenResult(
        success=len(created_files) > 0,
        files_created=created_files,
        output=result.output[:1000],
        error="" if created_files else "No .java files generated",
    )
