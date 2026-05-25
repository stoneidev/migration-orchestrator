import subprocess
from pathlib import Path

import pytest
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

from src.db.models import Base, Page
from src.pipeline.engine import BaseStep, PipelineEngine, StepContext, StepResult
from src.workers.worktree import WorktreeManager


def _init_monorepo_git(root: Path) -> Path:
    (root / "apps" / "frontend" / "src" / "app" / "admin").mkdir(parents=True)
    (root / "apps" / "backend" / "src" / "main" / "java").mkdir(parents=True)
    (root / "README.md").write_text("test monorepo")
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=root, check=True)
    return root


@pytest.fixture
def db_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as s:
        s.add(Page(id="bbs.test_page", module="bbs", complexity="low"))
        s.commit()
    return factory


class WriteMarkerStep(BaseStep):
    name = "write_marker"
    step_number = 1

    async def execute(self, context: StepContext) -> StepResult:
        if context.workspace_root is None:
            return StepResult(success=False, error="no workspace")
        marker = (
            context.workspace_root
            / "apps"
            / "backend"
            / "src"
            / "main"
            / "java"
            / "marker.txt"
        )
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("generated")
        return StepResult(success=True, artifacts={"files": [str(marker)]})


@pytest.mark.asyncio
async def test_pipeline_run_commits_in_worktree(tmp_path, db_factory):
    repo = _init_monorepo_git(tmp_path)
    wt_mgr = WorktreeManager(repo)

    mock_settings = MagicMock()
    mock_settings.use_worktree = True
    mock_settings.project_root = repo
    mock_settings.enforce_project_budget = False

    engine = PipelineEngine(
        steps=[WriteMarkerStep()],
        session_factory=db_factory,
        worktree_manager=wt_mgr,
    )

    with patch("src.config.Settings", return_value=mock_settings):
        await engine.run("bbs.test_page")

    wt_path = wt_mgr.get_path("bbs.test_page", "migration")
    assert wt_path.exists()

    log = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=wt_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "write_marker" in log.stdout

    with db_factory() as s:
        page = s.get(Page, "bbs.test_page")
        assert page.migration_status == "complete"
        assert page.current_step == 1


@pytest.mark.asyncio
async def test_pipeline_skips_worktree_when_disabled(tmp_path, db_factory):
    repo = _init_monorepo_git(tmp_path)

    mock_settings = MagicMock()
    mock_settings.use_worktree = False
    mock_settings.project_root = repo
    mock_settings.enforce_project_budget = False

    engine = PipelineEngine(steps=[WriteMarkerStep()], session_factory=db_factory)

    with patch("src.config.Settings", return_value=mock_settings):
        await engine.run("bbs.test_page")

    assert not (repo / ".worktrees" / "migration-bbs_test_page").exists()

    with db_factory() as s:
        page = s.get(Page, "bbs.test_page")
        assert page.migration_status == "blocked"
