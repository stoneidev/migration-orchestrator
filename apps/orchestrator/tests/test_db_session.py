from sqlalchemy import text

from src.db.session import get_engine, get_session


def test_engine_connects():
    engine = get_engine("sqlite:///:memory:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_get_session_yields_usable_session():
    engine = get_engine("sqlite:///:memory:")
    session_gen = get_session(engine)
    session = next(session_gen)
    result = session.execute(text("SELECT 42"))
    assert result.scalar() == 42
    try:
        next(session_gen)
    except StopIteration:
        pass
