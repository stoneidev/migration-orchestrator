"""Resolve codegen paths against an optional per-page git worktree."""

from pathlib import Path

from src.pipeline.engine import StepContext


def effective_root(context: StepContext, default_project_root: Path) -> Path:
    return context.workspace_root if context.workspace_root is not None else default_project_root


def frontend_admin_dir(context: StepContext, default_project_root: Path) -> Path:
    return effective_root(context, default_project_root) / "apps" / "frontend" / "src" / "app" / "admin"


def frontend_app_dir(context: StepContext, default_project_root: Path) -> Path:
    return effective_root(context, default_project_root) / "apps" / "frontend"


def backend_dir(context: StepContext, default_project_root: Path) -> Path:
    return effective_root(context, default_project_root) / "apps" / "backend"


def java_sources_dir(context: StepContext, default_project_root: Path) -> Path:
    return backend_dir(context, default_project_root) / "src" / "main" / "java"
