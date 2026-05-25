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
    if path.endswith(".php"):
        php_path = path
    else:
        # URL without .php extension → assume PHP file at same path
        # /mypage/wallet → mypage/wallet.php
        php_path = f"{path}.php" if path else ""

    # Generate page_id from path
    # /shop/mp_question.php → shop.mp_question
    # /mypage/wallet → mypage.wallet
    page_id = path.replace("/", ".").replace(".php", "").strip(".")

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
        # Ensure spec has meta.id and source.path
        if "meta" not in spec:
            spec["meta"] = {}
        spec["meta"]["id"] = page_id
        spec["meta"]["status"] = "draft"
        if "source" not in spec:
            spec["source"] = {}
        php_path = session.get("php_path", "")
        if php_path and not spec["source"].get("path"):
            spec["source"]["path"] = php_path
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


async def _llm_resolve_php_path(
    url: str,
    php_path: str,
    page_id: str,
    entry_files: list[str],
) -> str:
    """Use LLM to match a URL to the actual PHP source file from entry_points list."""
    try:
        from src.workers.analysis import AnalysisWorker

        # Extract keywords from URL/path for pre-filtering
        from urllib.parse import urlparse
        url_path = urlparse(url).path.strip("/").replace(".php", "")
        keywords = [w for w in re.split(r"[/_\-.]", url_path) if len(w) > 2 and w not in ("shop", "mobile", "www", "php", "device")]

        # Pre-filter: files containing any keyword from URL
        keyword_matches = [f for f in entry_files if any(kw.lower() in f.lower() for kw in keywords)]

        # If keyword filtering gives results, use those; otherwise use mobile entries
        if keyword_matches and len(keyword_matches) <= 50:
            candidates = keyword_matches
        else:
            mobile_entries = [f for f in entry_files if "mobile" in f and ("member" in f or "shop" in f)]
            candidates = mobile_entries[:150] if len(mobile_entries) > 150 else mobile_entries
            if not candidates:
                candidates = entry_files[:150]

        prompt = f"""Find the PHP source file that implements a specific web page.

The URL is: {url}
The URL path suggests the page is related to: {php_path.replace('.php','').replace('/',' ').replace('_',' ')}
Page ID: {page_id}

The file is likely in the "mobile/shop/member/" directory since this is a mobile user page.
The filename may differ from the URL (e.g., "mp_settings" in URL might be "account_settings" in filesystem).

Available PHP files:
{chr(10).join(candidates)}

Which ONE file from the list above implements the "{php_path.replace('.php','').split('/')[-1].replace('mp_','').replace('_',' ')}" page?
Reply with ONLY the exact file path. Nothing else."""

        worker = AnalysisWorker()
        messages = [{"role": "user", "content": prompt}]
        result = await worker.invoke(messages, model="haiku", max_tokens=100)

        if result.text:
            resolved = result.text.strip().strip('"').strip("'").strip("`")
            if resolved in entry_files:
                return resolved
            for f in entry_files:
                if resolved in f or f.endswith(resolved):
                    return f
        return ""
    except Exception as e:
        log.warning("LLM resolve failed: %s — %s", type(e).__name__, e)
        event_bus.emit("spec_gen:log", {"message": f"LLM resolve exception: {type(e).__name__}: {e}"})
        return ""


async def _do_mcp_analysis(session_id: str):
    settings = Settings()
    factory = get_session_factory()

    with factory() as db:
        row = db.get(SpecGenSession, session_id)
        if row is None:
            return
        php_path = row.php_path
        page_id = row.page_id
        target_url = row.url

    try:
        from src.workers.mcp import get_mcp_worker

        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Connecting to php-analyzer MCP..."})
        worker = MCPWorker(mcp_server_path=settings.mcp_server_path, python_path=settings.mcp_python_path)
        ctx = worker.connect()
        await ctx.__aenter__()
        use_ctx = True
        try:
            # Step A: Resolve actual PHP file path using MCP + LLM
            resolved_path = php_path
            filename = php_path.split("/")[-1] if php_path else f"{page_id.split('.')[-1]}.php"

            event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Searching for PHP source: {php_path or filename}..."})

            # Try exact path first
            file_detail = await worker.call_tool("php_get_file_detail", {"file_path": php_path}) if php_path else {"error": "no path"}

            if isinstance(file_detail, dict) and file_detail.get("error"):
                # Exact path failed — use MCP entry_points + keyword filter + LLM
                event_bus.emit("spec_gen:log", {"session_id": session_id, "message": "Exact path not found. Querying MCP entry points..."})

                all_entries = await worker.call_tool("php_find_entry_points", {})
                entries = all_entries.get("entries", []) if isinstance(all_entries, dict) else []
                entry_files = [e["file"] for e in entries]
                event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"MCP returned {len(entry_files)} entries."})

                # Keyword pre-filter from URL path
                from urllib.parse import urlparse as _urlparse
                url_path = _urlparse(target_url).path.strip("/").replace(".php", "")
                keywords = [w for w in re.split(r"[/_\-.]", url_path) if len(w) > 2 and w not in ("shop", "mobile", "www", "php", "device")]

                keyword_matches = [f for f in entry_files if any(kw.lower() in f.lower() for kw in keywords)]
                event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Keywords {keywords} → {len(keyword_matches)} matches"})

                if len(keyword_matches) == 1:
                    resolved_path = keyword_matches[0]
                elif keyword_matches:
                    resolved_path = await _llm_resolve_php_path(
                        url=target_url, php_path=php_path, page_id=page_id, entry_files=keyword_matches,
                    )
                else:
                    # No keyword match — give LLM mobile entries
                    mobile_entries = [f for f in entry_files if "mobile" in f]
                    resolved_path = await _llm_resolve_php_path(
                        url=target_url, php_path=php_path, page_id=page_id, entry_files=mobile_entries[:150],
                    )

                event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Resolved: '{resolved_path}'"})

                if resolved_path:
                    file_detail = await worker.call_tool("php_get_file_detail", {"file_path": resolved_path})
                    if isinstance(file_detail, dict) and file_detail.get("error"):
                        event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Invalid: {file_detail.get('error')}"})
                        file_detail = {"error": f"No PHP source found for '{php_path}'"}
                else:
                    file_detail = {"error": f"No PHP source found matching '{filename}'"}
            else:
                event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Found source at: {php_path}"})

            # Step B: Trace execution flow
            trace = {}
            if resolved_path and not (isinstance(file_detail, dict) and file_detail.get("error")):
                event_bus.emit("spec_gen:log", {"session_id": session_id, "message": f"Tracing execution: {resolved_path}..."})
                trace = await worker.call_tool("php_trace_entry", {
                    "entry_file": resolved_path,
                    "max_depth": 5,
                    "include_sql": True,
                })

            # Update php_path in session if resolved differently
            if resolved_path and resolved_path != php_path:
                with factory() as db:
                    row = db.get(SpecGenSession, session_id)
                    if row:
                        row.php_path = resolved_path
                        db.commit()

            mcp_data = {
                "resolved_path": resolved_path,
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
        finally:
            if use_ctx:
                await ctx.__aexit__(None, None, None)

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

        resolved_path = mcp.get("resolved_path", session['php_path'])

        prompt = f"""You are a PHP migration specialist. Analyze the following data and generate a complete aispec.json file.

## CRITICAL RULES
- ONLY include operations that ACTUALLY EXIST in the PHP source code.
- Do NOT invent POST/PUT/DELETE endpoints that are not in the source.
- If the page is read-only (only SELECT queries), then only define GET operations.
- All business_rules MUST be derivable from the actual SQL queries and PHP logic shown below.
- Use the EXACT table names from the SQL samples — do not rename or guess tables.

## Page Information
- URL: {session['url']}
- PHP File: {resolved_path} ({detail.get('line_count', '?')} lines)
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

## SQL Samples (ACTUAL queries from the source)
{json.dumps(sql_samples, indent=2)[:1500]}

## Execution Flow (first 10 steps)
{json.dumps(exec_flow, indent=2)[:1000]}

## Task
Write a file called `{output_file}` with a complete aispec.json containing:

1. **meta**: id="{session['page_id']}", title, status="draft", version=1
2. **source**: path="{resolved_path}", lines={detail.get('line_count', 0)}
3. **operations**: ONLY operations that exist in the source. Each with id, name, http_method, route, description, steps array, error_cases
4. **business_rules**: Each with id, description, when, then — ALL must come from actual PHP logic
5. **preconditions**: Each with id, description, check, on_failure
6. **data_models**: Input/Output models with typed fields matching actual DB columns
7. **data_layer**: tables (use EXACT names from SQL) and queries (actual SQL templates from source)
8. **test_scenarios**: Each with id, title, given, when, then, rule_ref

Do NOT make up features. Only document what the PHP source actually does.
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
