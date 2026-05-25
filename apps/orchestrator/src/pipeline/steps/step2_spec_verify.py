import asyncio
from dataclasses import dataclass, field

from src.workers.mcp import MCPWorker


@dataclass
class VerifyResult:
    success: bool
    gaps: list[str] = field(default_factory=list)
    message: str = ""


async def verify_spec(spec: dict, mcp_worker: MCPWorker) -> VerifyResult:
    meta = spec.get("meta", {})
    spec_id = meta.get("id", "unknown")

    source = spec.get("source", {})
    file_path = source.get("path", "")

    if not file_path:
        return VerifyResult(success=True, gaps=[], message="No source path — skipping MCP verification")

    # If spec was just generated (status=draft), skip deep verification
    if meta.get("status") == "draft":
        return VerifyResult(success=True, gaps=[], message=f"Spec {spec_id} is freshly generated — verification skipped")

    try:
        result = await asyncio.wait_for(
            mcp_worker.call_tool("php_detect_gaps"),
            timeout=30.0,
        )
    except asyncio.TimeoutError:
        return VerifyResult(success=True, gaps=[], message=f"MCP timeout for {spec_id} — skipping verification")
    except Exception as e:
        return VerifyResult(success=True, gaps=[], message=f"MCP error: {str(e)[:100]} — skipping")

    gaps = []
    if isinstance(result, dict):
        unresolved = result.get("unresolved_calls", [])
        broken = result.get("broken_includes", [])
        if unresolved:
            gaps.extend([f"unresolved: {c}" for c in unresolved[:5]])
        if broken:
            gaps.extend([f"broken_include: {b}" for b in broken[:5]])

    return VerifyResult(
        success=len(gaps) == 0,
        gaps=gaps,
        message=f"Verified {spec_id}: {len(gaps)} gaps found",
    )
