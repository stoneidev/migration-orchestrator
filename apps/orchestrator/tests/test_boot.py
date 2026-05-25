from pathlib import Path

from src.config import Settings


def test_settings_has_required_fields():
    settings = Settings(
        specs_dir=Path("/tmp/specs"),
        php_project_root=Path("/tmp/php"),
        mcp_server_path=Path("/tmp/mcp"),
        database_url="sqlite:///./data/test.db",
    )
    assert settings.specs_dir == Path("/tmp/specs")
    assert settings.php_project_root == Path("/tmp/php")
    assert settings.mcp_server_path == Path("/tmp/mcp")
    assert settings.database_url == "sqlite:///./data/test.db"
    assert settings.max_retry_attempts == 3
    assert settings.project_budget == 20000.0


def test_settings_defaults():
    settings = Settings(
        specs_dir=Path("/tmp/specs"),
        php_project_root=Path("/tmp/php"),
        mcp_server_path=Path("/tmp/mcp"),
    )
    assert settings.max_parallel_pages == 5
    assert settings.max_parallel_generation == 2
    assert settings.visual_ssim_threshold == 0.85
    assert settings.visual_diff_threshold_pct == 15.0
    assert settings.frontend_dev_port == 3100
    assert settings.screenshots_dir == Path("./screenshots")
