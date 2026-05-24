from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class JavaTestResult:
    success: bool
    test_files: list[str] = field(default_factory=list)
    output: str = ""
    error: str = ""


async def generate_java_tests(
    spec: dict,
    java_files: list[str],
    output_dir: Path,
    worker: ClaudeCLIWorker | None = None,
) -> JavaTestResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    test_scenarios = spec.get("test_scenarios", [])
    business_rules = spec.get("business_rules", [])

    scenarios_desc = "\n".join(
        f"- {ts.get('id', '')}: {ts.get('title', '')} (given: {ts.get('given', '')}, when: {ts.get('when', '')}, then: {ts.get('then', '')})"
        for ts in test_scenarios[:15]
    )

    prompt = f"""Generate JUnit 5 + Mockito + BDD tests for the following Java implementation.

## Test Scenarios from Spec
{scenarios_desc}

## Java Files Already Generated
{java_files}

## Rules
- JUnit 5 with @Test annotation
- Mockito for mocking repositories
- BDD style: Given-When-Then comments
- Use @DisplayName with Korean descriptions
- Test each business rule

Output test files directly. Place them in the current directory."""

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=10,
        cwd=output_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return JavaTestResult(success=False, error=result.error)

    test_files = []
    if output_dir.exists():
        for f in output_dir.rglob("*Test.java"):
            test_files.append(str(f.relative_to(output_dir)))
        for f in output_dir.rglob("*Tests.java"):
            test_files.append(str(f.relative_to(output_dir)))

    return JavaTestResult(
        success=len(test_files) > 0,
        test_files=test_files,
        output=result.output[:500],
        error="" if test_files else "No test files generated",
    )
