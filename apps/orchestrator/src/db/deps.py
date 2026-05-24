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


def get_db() -> Generator[Session, None, None]:
    global _SessionFactory
    if _SessionFactory is None:
        configure_db()
    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
