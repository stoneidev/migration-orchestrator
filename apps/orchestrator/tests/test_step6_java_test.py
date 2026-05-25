import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.pipeline.steps.step6_java_test import (
    _parse_test_counts,
    generate_java_tests,
)


def test_parse_test_counts_extracts_passed_and_failed():
    output = "BUILD FAILED in 12s\nfoo > bar FAILED\n10 tests completed, 1 failed"
    passed, failed = _parse_test_counts(output)
    assert failed == 1
    assert passed == 9


def test_parse_test_counts_returns_zero_when_no_summary():
    assert _parse_test_counts("nothing here") == (0, 0)


@pytest.mark.asyncio
async def test_generate_java_tests_returns_success_with_warning_when_no_gradlew(tmp_path):
    output_dir = tmp_path / "deep" / "nested"
    output_dir.mkdir(parents=True)

    result = await generate_java_tests(spec={}, java_files=[], output_dir=output_dir)

    assert result.success is True
    assert "No gradlew" in result.warning


@pytest.mark.asyncio
async def test_generate_java_tests_returns_failure_on_gradle_failure(tmp_path):
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    (backend_root / "gradlew").write_text("#!/bin/sh\nexit 1\n")
    (backend_root / "gradlew").chmod(0o755)
    (backend_root / "src" / "test").mkdir(parents=True)

    fake_proc = subprocess.CompletedProcess(
        args=["./gradlew", "test"],
        returncode=1,
        stdout="10 tests completed, 3 failed\n",
        stderr="",
    )

    with patch("subprocess.run", return_value=fake_proc):
        result = await generate_java_tests(
            spec={}, java_files=[], output_dir=backend_root / "src",
        )

    assert result.success is False
    assert result.tests_failed >= 1
    assert "gradle test failed" in result.error


@pytest.mark.asyncio
async def test_generate_java_tests_returns_success_on_zero_exit(tmp_path):
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    (backend_root / "gradlew").write_text("#!/bin/sh\nexit 0\n")
    (backend_root / "gradlew").chmod(0o755)

    fake_proc = subprocess.CompletedProcess(
        args=["./gradlew", "test"],
        returncode=0,
        stdout="BUILD SUCCESSFUL in 5s\n5 tests completed",
        stderr="",
    )

    with patch("subprocess.run", return_value=fake_proc):
        result = await generate_java_tests(
            spec={}, java_files=[], output_dir=backend_root / "src",
        )

    assert result.success is True
    assert result.tests_passed == 5


@pytest.mark.asyncio
async def test_generate_java_tests_warns_on_timeout(tmp_path):
    backend_root = tmp_path / "backend"
    backend_root.mkdir()
    (backend_root / "gradlew").write_text("#!/bin/sh\nsleep 60\n")
    (backend_root / "gradlew").chmod(0o755)

    with patch(
        "subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd=["./gradlew"], timeout=1),
    ):
        result = await generate_java_tests(
            spec={},
            java_files=[],
            output_dir=backend_root / "src",
            timeout=1,
        )

    assert result.success is True
    assert "timed out" in result.warning
