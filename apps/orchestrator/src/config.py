from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    specs_dir: Path
    php_project_root: Path
    mcp_server_path: Path
    screenshots_dir: Path = Path("./screenshots")

    pw_base_url: str = "https://dev.stylekorean.com"
    pw_admin_id: str = ""
    pw_admin_pw: str = ""

    aws_region: str = "us-east-1"

    max_parallel_pages: int = 5
    max_parallel_generation: int = 2
    max_retry_attempts: int = 3

    # Visual diff settings (Phase 4):
    #
    # The pipeline compares each generated React page against the original
    # PHP screenshot using SSIM (1 = identical) and a 0-100% pixel diff.
    # A page passes when ``ssim >= visual_ssim_threshold`` **or** the diff
    # percentage is below ``visual_diff_threshold_pct``. SSIM is preferred
    # because it tolerates anti-aliasing / font shifts that a raw pixel
    # diff would over-count.
    visual_ssim_threshold: float = 0.85
    visual_diff_threshold_pct: float = 15.0
    # If True, visual verification errors/missing baselines fail the step.
    strict_visual_gate: bool = True

    # Ports used during integration testing (Phase 4: stop hardcoding).
    frontend_dev_port: int = 3100   # next dev server for visual comparison
    frontend_dev_startup_timeout_s: int = 30
    # If True, Java test infrastructure warnings (missing gradle/timeout)
    # are treated as hard failures rather than pass-with-warning.
    strict_java_test: bool = True

    project_budget: float = 20000.0

    database_url: str = "sqlite:///./data/orchestrator.db"

    model_config = SettingsConfigDict(
        env_file=[".env", "../../.env"],
        env_file_encoding="utf-8",
        # Ignore unknown env vars so renaming/removing a field doesn't break
        # existing .env files until they're cleaned up.
        extra="ignore",
    )
