"""Alembic environment configuration.

Reads the database URL from :class:`src.config.Settings` at runtime so the
same migration scripts apply to dev SQLite and any future MySQL/Postgres
target. Importing :mod:`src.db.models` registers all tables on
``Base.metadata`` so autogenerate can pick up future schema changes.
"""

from __future__ import annotations

from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import engine_from_config, pool

from alembic import context

# Make the orchestrator package importable when alembic is invoked from any cwd.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.models import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _resolve_db_url() -> str:
    """Pick the database URL alembic should target.

    Priority:
      1. ``-x sqlalchemy.url=...`` override (tests, ad-hoc invocations).
      2. A URL already set on the alembic ``Config`` by the Python caller
         (``src.db.deps.configure_db`` does this).
      3. ``Settings().database_url``.
      4. Hard-coded local default.

    The ini-file default value is treated as the fallback only, never as
    the primary source of truth.
    """
    x_args = context.get_x_argument(as_dictionary=True)
    if "sqlalchemy.url" in x_args:
        return x_args["sqlalchemy.url"]

    configured = config.get_main_option("sqlalchemy.url") or ""
    if configured and not configured.startswith("driver://"):
        return configured

    try:
        from src.config import Settings

        return Settings().database_url
    except Exception:
        return "sqlite:///./data/orchestrator.db"


target_metadata = Base.metadata
db_url = _resolve_db_url()
config.set_main_option("sqlalchemy.url", db_url)


def run_migrations_offline() -> None:
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == "sqlite",
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
