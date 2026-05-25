from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from src.db.models import Base

_engine: Optional[Engine] = None
_SessionFactory: Optional[sessionmaker] = None


def configure_db(url: str = "sqlite:///./data/orchestrator.db") -> None:
    global _engine, _SessionFactory
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    _engine = create_engine(url, connect_args=connect_args)
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
