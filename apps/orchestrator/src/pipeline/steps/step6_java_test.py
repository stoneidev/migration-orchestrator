import asyncio
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class JavaTestResult:
    success: bool
    test_files: list[str] = field(default_factory=list)
    tests_passed: int = 0
    tests_failed: int = 0
    output: str = ""
    error: str = ""


async def generate_java_tests(
    spec: dict,
    java_files: list[str],
    output_dir: Path,
    worker: ClaudeCLIWorker | None = None,
) -> JavaTestResult:
    """
    Step 6: Java 테스트 실행.
    Step 5에서 TDD로 이미 테스트를 생성했으므로,
    여기서는 기존 테스트를 실행하고 결과를 확인합니다.
    테스트가 없으면 새로 생성합니다.
    """

    # Find backend root (where build.gradle.kts is)
    backend_root = output_dir
    while backend_root.name != "backend" and backend_root != backend_root.parent:
        backend_root = backend_root.parent
    if not (backend_root / "build.gradle.kts").exists():
        # Try going up from output_dir
        for p in output_dir.parents:
            if (p / "build.gradle.kts").exists():
                backend_root = p
                break

    # Check existing test files
    test_files = []
    test_src = backend_root / "src" / "test"
    if test_src.exists():
        for f in test_src.rglob("*Test.java"):
            test_files.append(str(f.relative_to(backend_root)))
        for f in test_src.rglob("*Tests.java"):
            test_files.append(str(f.relative_to(backend_root)))

    if not test_files:
        # No existing tests — generate with Claude CLI
        if worker is None:
            worker = ClaudeCLIWorker()

        test_scenarios = spec.get("test_scenarios", [])
        prompt = f"""Run `./gradlew test` in this project.
If there are no test files, create JUnit 5 tests based on:
{[ts.get('title','') for ts in test_scenarios[:10]]}

Then run `./gradlew test` and make sure all tests pass."""

        result = await worker.invoke(
            prompt=prompt,
            model="sonnet",
            max_turns=15,
            cwd=backend_root,
            allowed_tools=["Write", "Edit", "Bash", "Read"],
        )

        # Re-check test files
        if test_src.exists():
            for f in test_src.rglob("*Test.java"):
                test_files.append(str(f.relative_to(backend_root)))

        if not test_files:
            return JavaTestResult(success=False, error="No test files generated", output=result.output[:300])

    # Run existing tests
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            ["./gradlew", "test"],
            cwd=str(backend_root),
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout + result.stderr
        passed = result.returncode == 0

        # Parse test counts from output
        tests_passed = output.count("PASSED") + output.count("BUILD SUCCESSFUL")
        tests_failed = output.count("FAILED")

        return JavaTestResult(
            success=passed,
            test_files=test_files,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            output=output[-500:],
            error="" if passed else f"Tests failed (exit code {result.returncode}): {output[-200:]}",
        )

    except subprocess.TimeoutExpired:
        return JavaTestResult(success=False, test_files=test_files, error="Test execution timed out (120s)")
    except Exception as e:
        return JavaTestResult(success=False, test_files=test_files, error=str(e))
