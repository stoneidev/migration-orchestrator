import pytest
import os
from pathlib import Path

from src.git.manager import GitManager


@pytest.fixture
def git_repo(tmp_path):
    os.system(f"cd {tmp_path} && git init && git commit --allow-empty -m 'init'")
    return GitManager(repo_root=tmp_path)


def test_create_branch(git_repo):
    branch = git_repo.create_branch("bbs.alert_close")
    assert branch == "migration/bbs.alert_close"
    current = git_repo.get_current_branch()
    assert current == "migration/bbs.alert_close"


def test_commit_step(git_repo):
    # Create a file to commit
    (git_repo.repo_root / "test.txt").write_text("hello")
    result = git_repo.commit_step("bbs.alert_close", 1, "spec_load", model="haiku", cost=0.001)
    assert "feat(alert_close)" in result or result == ""

    # Verify commit exists
    import subprocess
    log = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        cwd=str(git_repo.repo_root),
        capture_output=True, text=True
    )
    assert "spec_load" in log.stdout


def test_commit_step_no_changes(git_repo):
    result = git_repo.commit_step("bbs.alert_close", 1, "spec_load")
    assert result == ""
