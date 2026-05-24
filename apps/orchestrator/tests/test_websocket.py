from fastapi.testclient import TestClient

from src.main import app
from src.api.ws.events import event_bus


def test_websocket_connects():
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        assert len(event_bus._connections) >= 1


def test_websocket_disconnect_cleanup():
    client = TestClient(app)
    before = len(event_bus._connections)
    with client.websocket_connect("/ws"):
        assert len(event_bus._connections) == before + 1
    assert len(event_bus._connections) == before
