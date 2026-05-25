"""Backward-compatible DB helpers. Prefer ``src.db.deps`` for new code."""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from src.db.deps import create_sqlalchemy_engine as get_engine


def get_session(engine) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
