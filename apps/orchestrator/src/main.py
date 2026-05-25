from contextlib import asynccontextmanager

import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.pages import router as pages_router
from src.api.routes.pipeline import router as pipeline_router
from src.api.routes.project import router as project_router
from src.api.routes.spec_gen import router as spec_gen_router
from src.api.routes.services import router as services_router
from src.api.ws.events import event_bus
from src.db.deps import configure_db, get_db  # noqa: F401 — get_db re-exported for tests
from src.logging_setup import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    log = logging.getLogger(__name__)
    log.info("orchestrator starting up")
    event_bus.set_loop(asyncio.get_running_loop())
    from src.config import Settings
    settings = Settings()
    # Consistency-first mode: fail fast on invalid settings or DB migration
    # errors rather than silently writing to an unexpected fallback DB.
    configure_db(settings.database_url)
    try:
        yield
    finally:
        await event_bus.shutdown()


app = FastAPI(title="Silicon2 Migration Orchestrator", version="0.1.0", lifespan=lifespan)

# Local single-user tool: explicit dev-only loopback origins. Allowing "*"
# together with credentials is invalid per the CORS spec and was rejected by
# browsers, so we whitelist the actual dev ports we run.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pages_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
app.include_router(project_router, prefix="/api")
app.include_router(spec_gen_router, prefix="/api")
app.include_router(services_router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    await event_bus.register(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await event_bus.unregister(ws)
