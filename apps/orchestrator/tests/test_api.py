import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.db import deps
from src.db.models import Base, Page


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    # Seed
    with factory() as s:
        s.add(Page(id="bbs.alert_close", module="bbs", title="팝업 닫기", complexity="low", migration_status="queued"))
        s.add(Page(id="shop_admin.cs_list", module="shop_admin", title="CS 목록", complexity="medium", migration_status="running", current_step=4))
        s.commit()

    deps.set_session_factory(factory)
    yield TestClient(app)
    deps.reset_session_factory()


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_pages(client):
    response = client.get("/api/pages")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 2


def test_get_page_detail(client):
    response = client.get("/api/pages/bbs.alert_close")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["id"] == "bbs.alert_close"
    assert data["data"]["module"] == "bbs"
    assert data["data"]["complexity"] == "low"


def test_get_page_not_found(client):
    response = client.get("/api/pages/nonexistent")
    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["success"] is False
    assert detail["error"]["code"] == "PAGE-001"


def test_pipeline_run(client):
    response = client.post("/api/pipeline/run", json={"page_ids": ["bbs.alert_close"]})
    assert response.status_code == 202
    data = response.json()
    assert data["success"] is True


def test_pipeline_run_updates_status(client):
    response = client.post("/api/pipeline/run", json={"page_ids": ["bbs.alert_close"]})
    assert response.status_code == 202

    status = client.get("/api/pipeline/status").json()
    assert status["success"] is True
    tasks = status["data"].values()
    assert any(t["page_id"] == "bbs.alert_close" for t in tasks)
