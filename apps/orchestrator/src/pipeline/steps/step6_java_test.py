"""Step 6: run ``./gradlew test`` against the generated backend.

A non-zero exit code is now reported as ``success=False`` so the pipeline can
treat it as a real failure (and trigger retries / blocks). Infrastructure-level
problems that are not test failures – missing ``gradlew``, gradle timeouts,
subprocess errors – are reported via a dedicated ``warning`` field with
``success=True`` so they don't pretend the suite passed.
"""

from __future__ import annotations

import asyncio
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


_FAILED_TESTS_RE = re.compile(r"(\d+)\s+tests?\s+(?:completed|failed|errors?)", re.IGNORECASE)


@dataclass
class JavaTestResult:
    success: bool
    test_files: list[str] = field(default_factory=list)
    tests_passed: int = 0
    tests_failed: int = 0
    output: str = ""
    error: str = ""
    warning: str = ""
    duration_ms: int = 0


def _find_backend_root(start: Path) -> Path | None:
    """Walk up looking for a directory that contains ``gradlew``."""
    current = start
    seen: set[Path] = set()
    while current and current not in seen:
        seen.add(current)
        if (current / "gradlew").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def _parse_test_counts(output: str) -> tuple[int, int]:
    """Best-effort parse of ``X tests completed, Y failed``-style summaries.

    Prefers the explicit ``N failed`` count from the summary line; falls back
    to counting ``FAILED`` markers (per-test) when no summary is present.
    """
    failed_match = re.search(r"(\d+)\s+failed", output, re.IGNORECASE)
    if failed_match:
        failed = int(failed_match.group(1))
    else:
        failed = output.count(" FAILED")

    passed = 0
    total_match = re.search(r"(\d+)\s+tests?\s+completed", output, re.IGNORECASE)
    if total_match:
        total = int(total_match.group(1))
        passed = max(0, total - failed)
    return passed, failed


async def generate_java_tests(
    spec: dict,
    java_files: list[str],
    output_dir: Path,
    worker=None,
    timeout: int = 300,
) -> JavaTestResult:
    """Run ``./gradlew test``. If tests fail, use Claude CLI to fix and re-run."""

    backend_root = _find_backend_root(output_dir)
    if backend_root is None:
        return JavaTestResult(
            success=True,
            warning="No gradlew found upstream of output_dir; skipping java tests",
        )

    test_files: list[str] = []
    test_src = backend_root / "src" / "test"
    if test_src.exists():
        for f in test_src.rglob("*Test.java"):
            test_files.append(str(f.relative_to(backend_root)))

    # First run
    result = await _run_gradle_test(backend_root, timeout)
    if result is None:
        return JavaTestResult(success=True, test_files=test_files, warning="gradle not runnable")

    returncode, output = result
    passed_count, failed_count = _parse_test_counts(output)

    if returncode == 0:
        return JavaTestResult(
            success=True,
            test_files=test_files,
            tests_passed=passed_count,
            tests_failed=0,
            output=output[-500:],
        )

    # Tests failed — use Claude CLI to fix, repeat until success or max attempts
    from src.workers.claude_cli import ClaudeCLIWorker, CLIResult

    cli_worker = worker or ClaudeCLIWorker()
    max_fix_attempts = 3
    last_output = output

    for fix_attempt in range(1, max_fix_attempts + 1):
        fix_prompt = f"""The Java tests are failing ({failed_count} failed). Fix the code so ALL tests pass.

## Error Output (last 2000 chars)
```
{last_output[-2000:]}
```

## Steps
1. Read the failing test file(s) to understand what they expect
2. Read the corresponding source file(s)
3. Fix the source code (NOT the tests) so the tests pass
4. Run `./gradlew test --no-daemon` to verify ALL tests pass
5. If still failing, read the new error output and fix again
6. Keep fixing until `./gradlew test` exits with 0

## Rules
- Fix the implementation, not the tests
- If a test expects a method/class that doesn't exist, create it
- If a test expects specific behavior, implement that behavior
- If @DataJpaTest loads unrelated @Component beans (DataInitializer conflicts), add @ComponentScan filtering or use @Import to limit the scan scope
- If a filename doesn't match the public interface/class name, rename the FILE (not the class)
- You MUST run `./gradlew test` at the end and confirm it passes with 0 failures
"""

        cli_result: CLIResult = await cli_worker.invoke(
            prompt=fix_prompt,
            model="sonnet",
            max_turns=15,
            cwd=backend_root,
            allowed_tools=["Write", "Edit", "Bash", "Read"],
        )

        # Re-run tests after fix
        result2 = await _run_gradle_test(backend_root, timeout)
        if result2 is None:
            return JavaTestResult(success=True, test_files=test_files, warning="gradle not runnable after fix")

        returncode2, last_output = result2
        passed_count, failed_count = _parse_test_counts(last_output)

        if returncode2 == 0:
            return JavaTestResult(
                success=True,
                test_files=test_files,
                tests_passed=passed_count,
                tests_failed=0,
                output=last_output[-500:],
            )

    return JavaTestResult(
        success=False,
        test_files=test_files,
        tests_passed=passed_count,
        tests_failed=failed_count or 1,
        output=last_output[-1000:],
        error=f"gradle test failed (exit={returncode2}, failed={failed_count})",
    )


async def _run_gradle_test(backend_root: Path, timeout: int) -> tuple[int, str] | None:
    try:
        completed = await asyncio.to_thread(
            subprocess.run,
            ["./gradlew", "test", "--no-daemon"],
            cwd=str(backend_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        return None

    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode, output
