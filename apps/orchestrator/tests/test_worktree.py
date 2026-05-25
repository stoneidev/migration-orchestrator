import pytest
import os
from pathlib import Path

from src.workers.worktree import WorktreeManager


@pytest.fixture
def worktree_mgr(tmp_path):
    # Create a bare git repo for testing
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()
    os.system(f"cd {repo_dir} && git init && git commit --allow-empty -m 'init'")
    return WorktreeManager(repo_root=repo_dir)


def test_create_worktree(worktree_mgr):
    path = worktree_mgr.create("bbs.alert_close", "react")
    assert path.exists()
    assert path.is_dir()
    assert (path / ".git").exists()


def test_remove_worktree(worktree_mgr):
    path = worktree_mgr.create("bbs.alert_close", "react")
    assert path.exists()

    worktree_mgr.remove("bbs.alert_close", "react")
    assert not path.exists()


def test_create_worktree_creates_branch(worktree_mgr):
    path = worktree_mgr.create("bbs.alert_close", "java")
    branch_name = worktree_mgr.get_branch_name("bbs.alert_close", "java")
    assert "bbs.alert_close" in branch_name
    assert "java" in branch_name


def test_ensure_reuses_existing_worktree(worktree_mgr):
    first = worktree_mgr.create("bbs.alert_close", "migration")
    second = worktree_mgr.ensure("bbs.alert_close", "migration")
    assert first == second
