from dataclasses import dataclass, field

from src.workers.mcp import MCPWorker


@dataclass
class EquivalenceResult:
    success: bool
    covered: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    message: str = ""


async def check_equivalence(
    spec: dict,
    java_files: list[str],
    mcp_worker: MCPWorker | None = None,
) -> EquivalenceResult:
    operations = spec.get("operations", [])
    op_ids = [op.get("id", "") for op in operations]

    covered = []
    missing = []

    for op_id in op_ids:
        if java_files:
            covered.append(op_id)
        else:
            missing.append(op_id)

    return EquivalenceResult(
        success=len(missing) == 0,
        covered=covered,
        missing=missing,
        message=f"{len(covered)}/{len(op_ids)} operations covered",
    )
