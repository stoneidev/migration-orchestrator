from pathlib import Path

import pytest

from src.config import Settings, discover_project_root


def test_discover_project_root_from_orchestrator_package():
    root = discover_project_root(start=Path(__file__).resolve().parent.parent)
    assert (root / "apps" / "orchestrator" / "pyproject.toml").is_file()
    assert (root / "apps" / "frontend").is_dir()


def test_discover_project_root_from_tmp_layout(tmp_path: Path):
    (tmp_path / "apps" / "orchestrator").mkdir(parents=True)
    (tmp_path / "apps" / "frontend").mkdir(parents=True)
    (tmp_path / "apps" / "orchestrator" / "pyproject.toml").write_text("[project]\nname='x'\n")

    root = discover_project_root(start=tmp_path / "apps" / "orchestrator")
    assert root == tmp_path


def test_settings_resolves_project_root():
    settings = Settings(
        specs_dir=Path("/tmp/specs"),
        php_project_root=Path("/tmp/php"),
        mcp_server_path=Path("/tmp/mcp"),
        _env_file=None,
    )
    assert settings.project_root is not None
    assert (settings.project_root / "apps" / "orchestrator").is_dir()


def test_settings_claude_and_mcp_defaults():
    settings = Settings(
        specs_dir=Path("/tmp/specs"),
        php_project_root=Path("/tmp/php"),
        mcp_server_path=Path("/tmp/mcp"),
        _env_file=None,
    )
    assert settings.claude_path == "claude"
    assert settings.mcp_python_path == "python3"
