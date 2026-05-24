import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from src.workers.mcp import MCPWorker
from src.workers.analysis import AnalysisWorker
from src.api.ws.events import event_bus
from src.config import Settings
from src.db.deps import _SessionFactory
from src.db.models import SpecGenHistory

router = APIRouter()

_spec_gen_status: dict[str, dict] = {}


class SpecGenRequest(BaseModel):
    url: str
    php_path: str = ""
    page_id: str = ""


class SpecGenStepRequest(BaseModel):
    session_id: str


# ---- Session State ----

def _get_session(session_id: str) -> dict:
    if session_id not in _spec_gen_status:
        _spec_gen_status[session_id] = {
            "status": "idle",
            "url": "",
            "php_path": "",
            "page_id": "",
            "step": 0,
            "screenshot": None,
            "mcp_data": None,
            "spec": None,
            "error": None,
        }
    return _spec_gen_status[session_id]


# ---- API Endpoints ----

@router.post("/spec-gen/start")
async def start_spec_gen(request: SpecGenRequest):
    session_id = f"sg-{datetime.utcnow().strftime('%H%M%S')}"
    session = _get_session(session_id)
    session["url"] = request.url
    session["php_path"] = request.php_path
    session["page_id"] = request.page_id or request.url.split("/")[-1].split("?")[0]
    session["status"] = "ready"
    return {"success": True, "data": {"session_id": session_id, **session}}


@router.post("/spec-gen/step1-capture")
async def step1_capture(request: SpecGenStepRequest, background_tasks: BackgroundTasks):
    session = _get_session(request.session_id)
    session["step"] = 1
    session["status"] = "capturing"
    event_bus.emit("spec_gen:step_started", {"session_id": request.session_id, "step": 1, "name": "Playwright Capture"})
    background_tasks.add_task(_do_capture, request.session_id)
    return {"success": True, "data": {"message": "Capturing page...", "step": 1}}


@router.post("/spec-gen/step2-analyze")
async def step2_analyze(request: SpecGenStepRequest, background_tasks: BackgroundTasks):
    session = _get_session(request.session_id)
    session["step"] = 2
    session["status"] = "analyzing"
    event_bus.emit("spec_gen:step_started", {"session_id": request.session_id, "step": 2, "name": "MCP Analysis"})
    background_tasks.add_task(_do_mcp_analysis, request.session_id)
    return {"success": True, "data": {"message": "Analyzing PHP source...", "step": 2}}


@router.post("/spec-gen/step3-generate")
async def step3_generate(request: SpecGenStepRequest, background_tasks: BackgroundTasks):
    session = _get_session(request.session_id)
    session["step"] = 3
    session["status"] = "generating"
    event_bus.emit("spec_gen:step_started", {"session_id": request.session_id, "step": 3, "name": "Spec Generation"})
    background_tasks.add_task(_do_spec_generation, request.session_id)
    return {"success": True, "data": {"message": "Generating spec...", "step": 3}}


@router.get("/spec-gen/history")
async def get_history():
    if _SessionFactory is None:
        return {"success": True, "data": []}
    with _SessionFactory() as db:
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
    session = _get_session(session_id)
    return {"success": True, "data": session}


def _save_history(session_id: str, session: dict, spec: dict, spec_path: str):
    if _SessionFactory is None:
        return
    try:
        with _SessionFactory() as db:
            record = SpecGenHistory(
                session_id=session_id,
                page_id=session.get("page_id", ""),
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
            db.commit()
    except Exception:
        pass


# ---- Background Tasks ----

async def _do_capture(session_id: str):
    session = _get_session(session_id)
    settings = Settings()

    try:
        from playwright.async_api import async_playwright

        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Launching Playwright (headless)..."})

        screenshots_dir = Path(settings.screenshots_dir) / session["page_id"]
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 430, "height": 932})
            page = await context.new_page()

            # Login
            await page.goto(f"{settings.pw_base_url}/manage-account/gologin.php", timeout=60000)
            await page.wait_for_timeout(2000)
            email = page.locator('input[name="mb_id"]:visible').first
            if await email.count() > 0:
                await email.fill(settings.pw_admin_id)
            pw = page.locator('input[type="password"]:visible').first
            if await pw.count() > 0:
                await pw.fill(settings.pw_admin_pw)
            submit = page.locator('input[type="submit"]:visible').first
            if await submit.count() > 0:
                await submit.click()
            await page.wait_for_timeout(5000)

            # Navigate to target
            event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Navigating to {session['url']}..."})
            await page.goto(session["url"], timeout=60000)
            await page.wait_for_timeout(5000)

            # Capture
            screenshot_path = screenshots_dir / "original.png"
            await page.screenshot(path=str(screenshot_path), full_page=True)

            # Extract page structure
            headings = await page.locator("h1,h2,h3,h4").all_text_contents()
            buttons = await page.locator("button, a[class*='btn']").all_text_contents()

            session["screenshot"] = {
                "path": str(screenshot_path),
                "url": page.url,
                "title": await page.title(),
                "headings": [h.strip() for h in headings if h.strip()][:10],
                "buttons": [b.strip() for b in buttons if b.strip()][:10],
            }
            session["status"] = "captured"
            await browser.close()

        event_bus.emit("spec_gen:step_completed", {"session_id": session_id, "step": 1, "status": "success"})

    except Exception as e:
        session["status"] = "error"
        session["error"] = str(e)
        event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 1, "error": str(e)[:200]})


async def _do_mcp_analysis(session_id: str):
    session = _get_session(session_id)
    settings = Settings()

    try:
        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Connecting to php-analyzer MCP..."})
        worker = MCPWorker(mcp_server_path=settings.mcp_server_path)
        async with worker.connect():
            php_path = session["php_path"]

            event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Analyzing {php_path}..."})
            file_detail = await worker.call_tool("php_get_file_detail", {"file_path": php_path})
            trace = await worker.call_tool("php_trace_entry", {
                "entry_file": php_path,
                "max_depth": 5,
                "include_sql": True,
            })

            session["mcp_data"] = {
                "file_detail": file_detail if isinstance(file_detail, dict) else {"raw": str(file_detail)[:500]},
                "trace": {
                    "include_count": trace.get("include_count", 0) if isinstance(trace, dict) else 0,
                    "step_count": trace.get("step_count", 0) if isinstance(trace, dict) else 0,
                    "sql_count": trace.get("sql_count", 0) if isinstance(trace, dict) else 0,
                    "sql_queries": trace.get("sql_queries", [])[:10] if isinstance(trace, dict) else [],
                    "execution_flow": trace.get("execution_flow", [])[:10] if isinstance(trace, dict) else [],
                },
            }
            session["status"] = "analyzed"

        event_bus.emit("spec_gen:step_completed", {"session_id": session_id, "step": 2, "status": "success"})

    except Exception as e:
        session["status"] = "error"
        session["error"] = str(e)
        event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 2, "error": str(e)[:200]})


async def _do_spec_generation(session_id: str):
    session = _get_session(session_id)

    try:
        from src.workers.claude_cli import ClaudeCLIWorker

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
            session["spec"] = spec
            session["status"] = "complete"
            session["cost"] = result.cost

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
                session["spec"] = spec
                session["status"] = "complete"
                session["cost"] = result.cost
                event_bus.emit("spec_gen:step_completed", {"session_id": session_id, "step": 3, "status": "success"})
            else:
                session["status"] = "error"
                session["error"] = f"CLI succeeded but no JSON file generated. Output: {result.output[:300]}"
                event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 3, "error": session["error"][:200]})
        else:
            session["status"] = "error"
            session["error"] = result.error[:500]
            event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 3, "error": result.error[:200]})

    except Exception as e:
        session["status"] = "error"
        session["error"] = str(e)
        event_bus.emit("spec_gen:step_failed", {"session_id": session_id, "step": 3, "error": str(e)[:200]})
