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
    visual_diff_threshold: int = 5

    project_budget: float = 20000.0

    database_url: str = "sqlite:///./data/orchestrator.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
