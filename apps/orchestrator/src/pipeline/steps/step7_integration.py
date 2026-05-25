from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class IntegrationResult:
    success: bool
    report: dict = field(default_factory=dict)
    files_modified: list[str] = field(default_factory=list)
    error: str = ""


INTEGRATION_PROMPT = """You are integrating the React frontend with the Spring Boot backend.

## Task
The React frontend currently uses mock data (mock-data.ts).
You need to replace mock data with actual API calls to the backend.

## Backend API Info
- Backend runs at: http://localhost:8080/api
- API Contract (OpenAPI):
{api_contract}

## Current Frontend Files Location
{frontend_dir}

## What to do:
1. Read the existing mock-data.ts to understand the data structure
2. Read the existing page.tsx and components to see how data is used
3. Create/update an API client file that calls the actual backend endpoints
4. Replace mock data imports with API calls using fetch or TanStack Query
5. Keep the mock data as fallback (if API fails, show mock data)
6. Ensure the page still renders correctly with both mock and real data

## Rules:
- Use TanStack Query (useQuery) for data fetching
- API base URL should be configurable: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'
- Handle loading and error states
- Keep 'use client' directive
- Do NOT change the visual appearance — only the data source

## After modification:
- The page should work with mock data when backend is off
- The page should fetch real data when backend is running
"""


async def integrate_frontend_backend(
    spec: dict | None,
    api_contract: str | None,
    frontend_dir: Path,
    worker: ClaudeCLIWorker | None = None,
) -> IntegrationResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    api_summary = api_contract[:2000] if api_contract else "No API contract available"

    prompt = INTEGRATION_PROMPT.format(
        api_contract=api_summary,
        frontend_dir=str(frontend_dir),
    )

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=15,
        cwd=frontend_dir,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return IntegrationResult(success=False, error=result.error)

    # Check what files were modified/created
    modified = []
    if frontend_dir.exists():
        for f in frontend_dir.rglob("*.ts"):
            if "api" in f.name.lower() or "query" in f.name.lower() or "client" in f.name.lower():
                modified.append(str(f.relative_to(frontend_dir)))
        for f in frontend_dir.rglob("*.tsx"):
            modified.append(str(f.relative_to(frontend_dir)))

    return IntegrationResult(
        success=True,
        files_modified=modified,
        report={"output": result.output[:300], "cost": result.cost},
    )
