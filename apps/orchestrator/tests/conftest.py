import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.models import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    yield session
    session.close()


def _path_from_env(name: str) -> Path | None:
    raw = os.environ.get(name)
    if raw:
        path = Path(raw).expanduser()
        if path.exists():
            return path
    return None


@pytest.fixture
def specs_dir() -> Path:
    path = _path_from_env("SPECS_DIR")
    if path is None:
        try:
            from src.config import Settings

            s = Settings(_env_file=None)
            if s.specs_dir.is_dir():
                path = s.specs_dir
        except Exception:
            pass
    if path is None or not path.is_dir():
        pytest.skip("SPECS_DIR not configured or missing")
    return path


@pytest.fixture
def mcp_server_path() -> Path:
    path = _path_from_env("MCP_SERVER_PATH")
    if path is None:
        try:
            from src.config import Settings

            s = Settings(_env_file=None)
            if s.mcp_server_path.is_dir():
                path = s.mcp_server_path
        except Exception:
            pass
    if path is None or not path.is_dir():
        pytest.skip("MCP_SERVER_PATH not configured or missing")
    return path
