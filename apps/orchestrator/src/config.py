from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_ORCHESTRATOR_DIR = Path(__file__).resolve().parent.parent


def discover_project_root(start: Path | None = None) -> Path:
    """Find monorepo root by walking up for orchestrator + frontend markers."""
    origins: list[Path] = []
    if start is not None:
        origins.append(start.resolve())
    origins.extend([Path.cwd().resolve(), _ORCHESTRATOR_DIR.resolve()])

    seen: set[Path] = set()
    for origin in origins:
        current = origin
        while current not in seen:
            seen.add(current)
            if (
                (current / "apps" / "orchestrator" / "pyproject.toml").is_file()
                and (current / "apps" / "frontend").is_dir()
            ):
                return current
            if current.parent == current:
                break
            current = current.parent

    # Fallback: apps/orchestrator → apps → monorepo root
    return _ORCHESTRATOR_DIR.parent.parent


class Settings(BaseSettings):
    specs_dir: Path
    php_project_root: Path
    mcp_server_path: Path
    screenshots_dir: Path = Path("./screenshots")

    project_root: Path | None = None
    claude_path: str = "claude"
    mcp_python_path: str = "python3"

    pw_base_url: str = "https://dev.stylekorean.com"
    pw_admin_id: str = ""
    pw_admin_pw: str = ""

    aws_region: str = "us-east-1"

    max_parallel_pages: int = 1  # shared monorepo writes; raise via MAX_PARALLEL_PAGES after worktree (6I)
    max_parallel_generation: int = 2
    max_retry_attempts: int = 3

    visual_ssim_threshold: float = 0.85
    visual_diff_threshold_pct: float = 15.0
    strict_visual_gate: bool = True

    frontend_dev_port: int = 3100
    frontend_dev_startup_timeout_s: int = 30
    strict_java_test: bool = True

    project_budget: float = 20000.0
    enforce_project_budget: bool = False

    use_worktree: bool = False

    database_url: str = "sqlite:///./data/orchestrator.db"

    model_config = SettingsConfigDict(
        env_file=[".env", "../../.env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _resolve_project_root(self) -> Self:
        if self.project_root is None:
            self.project_root = discover_project_root()
        return self
