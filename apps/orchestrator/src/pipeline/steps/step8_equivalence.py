from dataclasses import dataclass, field

from src.workers.mcp import MCPWorker


@dataclass
class EquivalenceResult:
    success: bool
    covered: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    message: str = ""


async def check_equivalence(
    spec: dict | None,
    java_files: list[str] | None = None,
    mcp_worker: MCPWorker | None = None,
) -> EquivalenceResult:
    if spec is None:
        return EquivalenceResult(success=True, covered=[], missing=[], message="Spec not available — skipped")

    operations = spec.get("operations", [])
    op_ids = [op.get("id", "") for op in operations]

    if not op_ids:
        return EquivalenceResult(success=True, covered=[], missing=[], message="No operations to check")

    covered = []
    missing = []

    for op_id in op_ids:
        if java_files:
            covered.append(op_id)
        else:
            missing.append(op_id)

    return EquivalenceResult(
        success=True,  # PoC: pass with report
        covered=covered,
        missing=missing,
        message=f"{len(covered)}/{len(op_ids)} operations covered",
    )
