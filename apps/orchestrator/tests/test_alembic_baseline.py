"""Phase 3 regression: Alembic baseline must apply cleanly to a fresh DB
*and* to an existing dev DB that already has the baseline schema."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

from src.db.deps import configure_db, reset_session_factory
from src.db.models import Base, Page


REQUIRED_TABLES = {
    "pages",
    "step_executions",
    "artifacts",
    "reviews",
    "cost_log",
    "spec_gen_history",
    "pipeline_tasks",
    "spec_gen_sessions",
}


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    reset_session_factory()


def test_alembic_upgrade_creates_all_tables_on_empty_db(tmp_path: Path):
    db_path = tmp_path / "fresh.db"
    url = f"sqlite:///{db_path}"

    configure_db(url)

    engine = create_engine(url)
    try:
        tables = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()

    assert REQUIRED_TABLES.issubset(tables)
    assert "alembic_version" in tables


def test_alembic_stamps_existing_baseline_db_without_recreating(tmp_path: Path):
    """Existing DBs with the baseline schema but no alembic_version row
    should be auto-stamped instead of triggering a re-create error."""
    db_path = tmp_path / "existing.db"
    url = f"sqlite:///{db_path}"

    engine = create_engine(url)
    Base.metadata.create_all(engine)
    # Insert a row to prove preservation.
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "INSERT INTO pages (id, module, migration_status, current_step, total_cost, "
            "total_input_tokens, total_output_tokens, created_at, updated_at) "
            "VALUES ('keep.me', 'mod', 'queued', 0, 0, 0, 0, datetime('now'), datetime('now'))"
        )
    engine.dispose()

    configure_db(url)

    engine = create_engine(url)
    try:
        tables = set(inspect(engine).get_table_names())
        with engine.begin() as conn:
            kept = conn.exec_driver_sql("SELECT id FROM pages WHERE id='keep.me'").fetchone()
    finally:
        engine.dispose()

    assert "alembic_version" in tables
    assert kept is not None and kept[0] == "keep.me"


def test_configure_db_keeps_in_memory_tests_fast(tmp_path: Path):
    """In-memory tests bypass alembic and use create_all directly."""
    configure_db("sqlite:///:memory:", run_migrations=False)
    from src.db.deps import get_session_factory

    factory = get_session_factory()
    with factory() as session:
        session.add(Page(id="x.y", module="x"))
        session.commit()
        assert session.get(Page, "x.y") is not None
