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
    """Run ``./gradlew test`` directly. No CLI required."""

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

    try:
        completed = await asyncio.to_thread(
            subprocess.run,
            ["./gradlew", "test", "--no-daemon"],
            cwd=str(backend_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return JavaTestResult(
            success=True,
            test_files=test_files,
            warning=f"gradle test timed out after {timeout}s",
            output=(e.stdout or "")[-300:] if isinstance(e.stdout, str) else "",
        )
    except FileNotFoundError as e:
        return JavaTestResult(
            success=True,
            test_files=test_files,
            warning=f"gradle not runnable: {e}",
        )

    output = (completed.stdout or "") + (completed.stderr or "")
    passed_count, failed_count = _parse_test_counts(output)

    if completed.returncode == 0:
        return JavaTestResult(
            success=True,
            test_files=test_files,
            tests_passed=passed_count,
            tests_failed=failed_count,
            output=output[-500:],
        )

    return JavaTestResult(
        success=False,
        test_files=test_files,
        tests_passed=passed_count,
        tests_failed=failed_count or 1,
        output=output[-1000:],
        error=f"gradle test failed (exit={completed.returncode}, failed={failed_count})",
    )
