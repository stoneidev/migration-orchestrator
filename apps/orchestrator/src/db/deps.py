"""Database session and schema management.

The orchestrator preserves history across releases (spec_gen_history, pages,
cost_log), so schema evolution goes through Alembic rather than
``Base.metadata.create_all``. Tests still use in-memory SQLite with
``create_all`` for speed; production / on-disk sqlite uses Alembic.

The first time a real on-disk DB is opened we automatically baseline it
with ``alembic stamp head`` if it has the expected schema but no
``alembic_version`` row, so existing dev databases don't need a manual
migration step.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, inspect, Engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.models import Base

_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None


_ALEMBIC_INI = Path(__file__).resolve().parent.parent.parent / "alembic.ini"
_BASELINE_REVISION = "cb0a1fb6f34a"
_BASELINE_TABLES = {"pages", "step_executions", "artifacts", "reviews", "cost_log", "spec_gen_history"}
_RUNTIME_STATE_TABLES = {"pipeline_tasks", "spec_gen_sessions"}


def _is_on_disk_sqlite(url: str) -> bool:
    return url.startswith("sqlite") and ":memory:" not in url and not url.startswith("sqlite+pysqlite:///:memory:")


def _run_alembic_for(url: str) -> None:
    """Bring the target DB up to head using Alembic migrations.

    If the DB already has the baseline tables but no ``alembic_version``
    row, stamp the current head before upgrading so we don't try to create
    tables that already exist.
    """
    from alembic import command
    from alembic.config import Config

    if not _ALEMBIC_INI.exists():
        # Repository checkout without alembic — fall back to create_all so
        # the orchestrator can still boot in unusual setups.
        return

    cfg = Config(str(_ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", url)

    probe_engine = create_engine(url)
    try:
        inspector = inspect(probe_engine)
        existing = set(inspector.get_table_names())
    finally:
        probe_engine.dispose()

    has_alembic_version = "alembic_version" in existing

    if not has_alembic_version and _BASELINE_TABLES.issubset(existing):
        # Existing dev DB from pre-alembic days: mark it at the known baseline
        # revision first, then run normal upgrades so new revisions still apply.
        if _RUNTIME_STATE_TABLES.issubset(existing):
            command.stamp(cfg, "head")
            return
        command.stamp(cfg, _BASELINE_REVISION)
    command.upgrade(cfg, "head")


def configure_db(
    url: str = "sqlite:///./data/orchestrator.db",
    *,
    run_migrations: bool = True,
) -> None:
    """Create the engine + session factory and bring the schema up to date.

    For on-disk SQLite (the production / dev case) this runs Alembic; for
    in-memory SQLite (tests) it falls back to ``Base.metadata.create_all``
    so the test suite doesn't pay the migration overhead.
    """
    global _engine, _SessionFactory
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

    on_disk = _is_on_disk_sqlite(url) or not url.startswith("sqlite")

    if on_disk and url.startswith("sqlite"):
        db_path = url.replace("sqlite:///", "", 1)
        # Ensure parent directory exists (data/orchestrator.db lives under data/).
        Path(db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)

    if on_disk and run_migrations:
        _run_alembic_for(url)

    _engine = create_engine(url, connect_args=connect_args)

    if not on_disk:
        # In-memory tests: just create tables directly.
        Base.metadata.create_all(_engine)

    _SessionFactory = sessionmaker(bind=_engine)


def set_session_factory(factory: sessionmaker) -> None:
    global _SessionFactory
    _SessionFactory = factory


def reset_session_factory() -> None:
    """Clear the module-level factory. Used by tests to isolate fixtures."""
    global _SessionFactory, _engine
    _SessionFactory = None
    _engine = None


def get_session_factory() -> sessionmaker:
    """Return the live session factory, configuring the default DB if needed.

    Callers MUST use this instead of importing ``_SessionFactory`` directly:
    ``from src.db.deps import _SessionFactory`` captures whatever the module
    variable held at import time (typically ``None``), so the imported name
    never sees later updates from :func:`configure_db`.
    """
    global _SessionFactory
    if _SessionFactory is None:
        configure_db()
    assert _SessionFactory is not None
    return _SessionFactory


def get_db() -> Generator[Session, None, None]:
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
