from dataclasses import dataclass


@dataclass
class CompletionResult:
    success: bool
    message: str = ""


async def complete_migration(
    page_id: str,
    total_cost: float = 0.0,
    total_steps: int = 9,
) -> CompletionResult:
    return CompletionResult(
        success=True,
        message=f"Migration complete for {page_id}. {total_steps} steps executed. Total cost: ${total_cost:.3f}",
    )
