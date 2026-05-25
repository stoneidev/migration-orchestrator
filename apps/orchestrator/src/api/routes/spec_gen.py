import json
import re
import uuid
from pathlib import Path

from src.util.clock import utcnow

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

import logging

from src.workers.mcp import MCPWorker
from src.workers.playwright import PlaywrightWorker
from src.api.ws.events import event_bus
from src.api.validators import validate_page_id
from src.config import Settings
from src.db.deps import get_session_factory
from src.db.models import Page, SpecGenHistory, SpecGenSession

log = logging.getLogger(__name__)

router = APIRouter()

class SpecGenRequest(BaseModel):
    url: str
    php_path: str = ""
    page_id: str = ""


class SpecGenStepRequest(BaseModel):
    session_id: str


def _decode_json(data: str | None):
    if not data:
        return None
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def _session_row_to_dict(row: SpecGenSession) -> dict:
    return {
        "session_id": row.id,
        "status": row.status,
        "url": row.url,
        "php_path": row.php_path,
        "page_id": row.page_id,
        "step": row.step,
        "screenshot": _decode_json(row.screenshot_json),
        "mcp_data": _decode_json(row.mcp_data_json),
        "spec": _decode_json(row.spec_json),
        "error": row.error,
        "cost": row.cost,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


def _load_session_or_404(session_id: str) -> SpecGenSession:
    factory = get_session_factory()
    with factory() as db:
        row = db.get(SpecGenSession, session_id)
        if row is None:
            raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "SESSION-001", "message": "SpecGen session not found"}})
        db.expunge(row)
        return row


# ---- API Endpoints ----

def _extract_from_url(url: str) -> tuple[str, str]:
    """Extract php_path and page_id from URL automatically."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    # Extract PHP filename: /shop/mp_question.php → shop/mp_question.php
    php_path = path if path.endswith(".php") else ""

    # Generate page_id from path
    # /shop/mp_question.php → shop.mp_question
    # /myambassador → ambassador.my_page
    if php_path:
        page_id = php_path.replace("/", ".").replace(".php", "")
    else:
        page_id = path.replace("/", ".").strip(".")

    # Clean up common prefixes
    for prefix in ["mobile.", "adm.", "www."]:
        if page_id.startswith(prefix):
            page_id = page_id[len(prefix):]

    # Normalise: lowercase + strip any path-unsafe characters so the result
    # always passes downstream ``page_id`` validation.
    page_id = re.sub(r"[^a-z0-9_.]", "_", page_id.lower()).strip("._")

    return php_path, page_id


@router.post("/spec-gen/start")
async def start_spec_gen(request: SpecGenRequest):
    session_id = f"sg-{uuid.uuid4().hex[:12]}"

    # Auto-extract php_path and page_id from URL
    auto_php_path, auto_page_id = _extract_from_url(request.url)
    php_path = request.php_path or auto_php_path
    page_id = request.page_id or auto_page_id
    safe_page_id = validate_page_id(page_id)

    factory = get_session_factory()
    with factory() as db:
        row = SpecGenSession(
            id=session_id,
            url=request.url,
            php_path=php_path,
            page_id=safe_page_id,
            status="ready",
            step=0,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {"success": True, "data": _session_row_to_dict(row)}


@router.post("/spec-gen/step1-capture")
async def step1_capture(request: SpecGenStepRequest, background_tasks: BackgroundTasks):
    factory = get_session_factory()
    with factory() as db:
        row = db.get(SpecGenSession, request.session_id)
        if row is None:
            raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "SESSION-001", "message": "SpecGen session not found"}})
        row.step = 1
        row.status = "capturing"
        row.error = None
        db.commit()
    event_bus.emit("spec_gen:step_started", {"session_id": request.session_id, "step": 1, "name": "Playwright Capture"})
    background_tasks.add_task(_do_capture, request.session_id)
    return {"success": True, "data": {"message": "Capturing page...", "step": 1}}


@router.post("/spec-gen/step2-analyze")
async def step2_analyze(request: SpecGenStepRequest, background_tasks: BackgroundTasks):
    factory = get_session_factory()
    with factory() as db:
        row = db.get(SpecGenSession, request.session_id)
        if row is None:
            raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "SESSION-001", "message": "SpecGen session not found"}})
        row.step = 2
        row.status = "analyzing"
        row.error = None
        db.commit()
    event_bus.emit("spec_gen:step_started", {"session_id": request.session_id, "step": 2, "name": "MCP Analysis"})
    background_tasks.add_task(_do_mcp_analysis, request.session_id)
    return {"success": True, "data": {"message": "Analyzing PHP source...", "step": 2}}


@router.post("/spec-gen/step3-generate")
async def step3_generate(request: SpecGenStepRequest, background_tasks: BackgroundTasks):
    factory = get_session_factory()
    with factory() as db:
        row = db.get(SpecGenSession, request.session_id)
        if row is None:
            raise HTTPException(status_code=404, detail={"success": False, "error": {"code": "SESSION-001", "message": "SpecGen session not found"}})
        row.step = 3
        row.status = "generating"
        row.error = None
        db.commit()
    event_bus.emit("spec_gen:step_started", {"session_id": request.session_id, "step": 3, "name": "Spec Generation"})
    background_tasks.add_task(_do_spec_generation, request.session_id)
    return {"success": True, "data": {"message": "Generating spec...", "step": 3}}


@router.get("/spec-gen/history")
async def get_history():
    factory = get_session_factory()
    with factory() as db:
        records = db.query(SpecGenHistory).order_by(SpecGenHistory.created_at.desc()).limit(50).all()
        return {
            "success": True,
            "data": [
                {
                    "session_id": r.session_id,
                    "page_id": r.page_id,
                    "url": r.url,
                    "php_path": r.php_path,
                    "status": r.status,
                    "operations": r.operations_count,
                    "business_rules": r.business_rules_count,
                    "test_scenarios": r.test_scenarios_count,
                    "cost": r.cost,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ],
        }


@router.get("/spec-gen/{session_id}")
async def get_session_status(session_id: str):
    row = _load_session_or_404(session_id)
    return {"success": True, "data": _session_row_to_dict(row)}


def _save_history(session_id: str, session: dict, spec: dict, spec_path: str):
    try:
        factory = get_session_factory()
        settings = Settings()
        page_id = session.get("page_id", "")

        with factory() as db:
            # 1. Save to history
            record = SpecGenHistory(
                session_id=session_id,
                page_id=page_id,
                url=session.get("url", ""),
                php_path=session.get("php_path", ""),
                status="complete",
                operations_count=len(spec.get("operations", [])),
                business_rules_count=len(spec.get("business_rules", [])),
                test_scenarios_count=len(spec.get("test_scenarios", [])),
                cost=session.get("cost", 0.0),
                spec_path=spec_path,
            )
            db.add(record)

            # 2. Register in pages table (for pipeline)
            existing = db.get(Page, page_id)
            if not existing:
                db.add(Page(
                    id=page_id,
                    module=page_id.split(".")[0] if "." in page_id else "unknown",
                    title=spec.get("meta", {}).get("title", page_id),
                    spec_status="draft",
                    spec_score=0.0,
                    complexity="medium",
                    migration_status="queued",
                ))

            db.commit()

        # 3. Copy spec to specs directory (for pipeline Step 1)
        specs_dir = settings.specs_dir
        target = specs_dir / f"{page_id}.aispec.json"
        # Ensure spec has meta.id
        if "meta" not in spec:
            spec["meta"] = {}
        spec["meta"]["id"] = page_id
        spec["meta"]["status"] = "draft"
        target.write_text(json.dumps(spec, indent=2, ensure_ascii=False))

        event_bus.emit("spec_gen:registered", {"page_id": page_id, "spec_path": str(target)})

    except Exception as e:
        import traceback
        event_bus.emit("spec_gen:log", {"message": f"Save error: {e} — {traceback.format_exc()[:200]}"})


# ---- Background Tasks ----

async def _do_capture(session_id: str):
    settings = Settings()
    factory = get_session_factory()

    with factory() as db:
        row = db.get(SpecGenSession, session_id)
        if row is None:
            return
        target_url = row.url
        page_id = row.page_id

    event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Launching Playwright (headless)..."})

    worker = PlaywrightWorker(
        base_url=settings.pw_base_url,
        admin_id=settings.pw_admin_id,
        admin_pw=settings.pw_admin_pw,
        screenshots_dir=Path(settings.screenshots_dir),
    )

    event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Navigating to {target_url}..."})
    capture = await worker.capture_for_spec(
        target_url=target_url,
        page_id=page_id,
    )

    if not capture.success:
        with factory() as db:
            row = db.get(SpecGenSession, session_id)
            if row:
                row.status = "error"
                row.error = capture.error
                db.commit()
        log.warning("spec-gen capture failed for %s: %s", session_id, capture.error)
        event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 1, "error": capture.error[:200]})
        return

    screenshot_data = {
        "path": capture.screenshot_path,
        "url": capture.url,
        "title": capture.title,
        "headings": capture.headings,
        "buttons": capture.buttons,
    }
    with factory() as db:
        row = db.get(SpecGenSession, session_id)
        if row:
            row.screenshot_json = json.dumps(screenshot_data, ensure_ascii=False)
            row.status = "captured"
            row.error = None
            db.commit()
    event_bus.emit("spec_gen:step_completed", {"session_id": session_id, "step": 1, "status": "success"})


async def _do_mcp_analysis(session_id: str):
    settings = Settings()
    factory = get_session_factory()

    with factory() as db:
        row = db.get(SpecGenSession, session_id)
        if row is None:
            return
        php_path = row.php_path

    try:
        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Connecting to php-analyzer MCP..."})
        worker = MCPWorker(mcp_server_path=settings.mcp_server_path)
        async with worker.connect():
            event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Analyzing {php_path}..."})
            file_detail = await worker.call_tool("php_get_file_detail", {"file_path": php_path})
            trace = await worker.call_tool("php_trace_entry", {
                "entry_file": php_path,
                "max_depth": 5,
                "include_sql": True,
            })

            mcp_data = {
                "file_detail": file_detail if isinstance(file_detail, dict) else {"raw": str(file_detail)[:500]},
                "trace": {
                    "include_count": trace.get("include_count", 0) if isinstance(trace, dict) else 0,
                    "step_count": trace.get("step_count", 0) if isinstance(trace, dict) else 0,
                    "sql_count": trace.get("sql_count", 0) if isinstance(trace, dict) else 0,
                    "sql_queries": trace.get("sql_queries", [])[:10] if isinstance(trace, dict) else [],
                    "execution_flow": trace.get("execution_flow", [])[:10] if isinstance(trace, dict) else [],
                },
            }
            with factory() as db:
                row = db.get(SpecGenSession, session_id)
                if row:
                    row.mcp_data_json = json.dumps(mcp_data, ensure_ascii=False)
                    row.status = "analyzed"
                    row.error = None
                    db.commit()

        event_bus.emit("spec_gen:step_completed", {"session_id": session_id, "step": 2, "status": "success"})

    except Exception as e:
        with factory() as db:
            row = db.get(SpecGenSession, session_id)
            if row:
                row.status = "error"
                row.error = str(e)
                db.commit()
        event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 2, "error": str(e)[:200]})


async def _do_spec_generation(session_id: str):
    try:
        from src.workers.claude_cli import ClaudeCLIWorker
        factory = get_session_factory()
        with factory() as db:
            row = db.get(SpecGenSession, session_id)
            if row is None:
                return
            session = _session_row_to_dict(row)

        mcp = session.get("mcp_data", {})
        screenshot = session.get("screenshot", {})
        trace = mcp.get("trace", {})
        detail = mcp.get("file_detail", {})

        calls = [c.get("name", "") for c in detail.get("calls", [])[:10]]
        tables = list(set(q.get("table", "") for q in trace.get("sql_queries", []) if q.get("table")))
        sql_samples = trace.get("sql_queries", [])[:8]
        exec_flow = trace.get("execution_flow", [])[:10]

        settings = Settings()
        out_dir = Path(settings.screenshots_dir) / session["page_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        output_file = out_dir / "generated_spec.json"

        prompt = f"""You are a PHP migration specialist. Analyze the following data and generate a complete aispec.json file.

## Page Information
- URL: {session['url']}
- PHP File: {session['php_path']} ({detail.get('line_count', '?')} lines)
- Page ID: {session['page_id']}

## Visual (from Playwright capture)
- Headings: {screenshot.get('headings', [])}
- Buttons: {screenshot.get('buttons', [])}
- Title: {screenshot.get('title', '')}

## PHP Static Analysis (from MCP php-analyzer)
- Functions called: {calls}
- Database tables: {tables}
- SQL query count: {trace.get('sql_count', 0)}
- Execution flow steps: {trace.get('step_count', 0)}
- Includes: {[i.get('file','') for i in detail.get('includes', [])]}

## SQL Samples
{json.dumps(sql_samples, indent=2)[:1000]}

## Execution Flow (first 10 steps)
{json.dumps(exec_flow, indent=2)[:1000]}

## Task
Write a file called `{output_file}` with a complete aispec.json containing:

1. **meta**: id="{session['page_id']}", title, status="draft", version=1
2. **source**: path="{session['php_path']}", lines={detail.get('line_count', 567)}
3. **operations** (at least 3): Each with id, name, http_method, route, description, steps array, error_cases
4. **business_rules** (at least 10): Each with id, description, when, then
5. **preconditions** (at least 3): Each with id, description, check, on_failure
6. **data_models**: Input/Output models with typed fields
7. **data_layer**: tables (name, columns) and queries (id, type, template)
8. **test_scenarios** (at least 15): Each with id, title, given, when, then, rule_ref

Be thorough and specific based on the PHP analysis data. All business rules should be derivable from the functions and SQL queries listed above.
"""

        worker = ClaudeCLIWorker()
        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Claude Code CLI generating spec..."})

        result = await worker.invoke(
            prompt=prompt,
            model="sonnet",
            max_turns=15,
            cwd=str(out_dir),
            allowed_tools=["Write", "Edit", "Read"],
        )

        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"CLI done: success={result.success}, duration={result.duration_ms}ms"})

        if result.success and output_file.exists():
            spec = json.loads(output_file.read_text())
            with factory() as db:
                row = db.get(SpecGenSession, session_id)
                if row:
                    row.spec_json = json.dumps(spec, ensure_ascii=False)
                    row.status = "complete"
                    row.cost = result.cost
                    row.error = None
                    db.commit()

            # Save to DB
            _save_history(session_id, session, spec, str(output_file))

            event_bus.emit("spec_gen:step_completed", {
                "session_id": session_id, "step": 3, "status": "success",
                "operations": len(spec.get("operations", [])),
                "business_rules": len(spec.get("business_rules", [])),
                "test_scenarios": len(spec.get("test_scenarios", [])),
                "cost": result.cost,
                "duration_ms": result.duration_ms,
            })
        elif result.success:
            # CLI succeeded but file not found — check if it wrote somewhere else
            json_files = list(out_dir.glob("*.json"))
            if json_files:
                spec = json.loads(json_files[0].read_text())
                with factory() as db:
                    row = db.get(SpecGenSession, session_id)
                    if row:
                        row.spec_json = json.dumps(spec, ensure_ascii=False)
                        row.status = "complete"
                        row.cost = result.cost
                        row.error = None
                        db.commit()
                _save_history(session_id, session, spec, str(json_files[0]))
                event_bus.emit("spec_gen:step_completed", {"session_id": session_id, "step": 3, "status": "success"})
            else:
                error_msg = f"CLI succeeded but no JSON file generated. Output: {result.output[:300]}"
                with factory() as db:
                    row = db.get(SpecGenSession, session_id)
                    if row:
                        row.status = "error"
                        row.error = error_msg
                        db.commit()
                event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 3, "error": error_msg[:200]})
        else:
            with factory() as db:
                row = db.get(SpecGenSession, session_id)
                if row:
                    row.status = "error"
                    row.error = result.error[:500]
                    db.commit()
            event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 3, "error": result.error[:200]})

    except Exception as e:
        factory = get_session_factory()
        with factory() as db:
            row = db.get(SpecGenSession, session_id)
            if row:
                row.status = "error"
                row.error = str(e)
                db.commit()
        event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 3, "error": str(e)[:200]})
