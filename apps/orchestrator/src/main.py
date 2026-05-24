from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.pages import router as pages_router
from src.api.routes.pipeline import router as pipeline_router
from src.api.routes.project import router as project_router
from src.api.ws.events import event_bus
from src.db.deps import get_db  # noqa: F401 — re-export for tests

app = FastAPI(title="Silicon2 Migration Orchestrator", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
app.include_router(project_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    event_bus.register(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        event_bus.unregister(ws)
