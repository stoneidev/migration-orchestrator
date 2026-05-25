from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class IntegrationResult:
    success: bool
    report: dict = field(default_factory=dict)
    files_modified: list[str] = field(default_factory=list)
    error: str = ""


INTEGRATION_PROMPT = """You are performing end-to-end integration between a React frontend and Spring Boot backend.

## Your Goal
Make the Frontend (React/Next.js) successfully call the Backend (Spring Boot) API and display real data.

## Current State
- Frontend is at: {frontend_dir}
- Backend is at: {backend_dir}
- Frontend has mock data that renders correctly
- Backend has controllers but may need fixes to work end-to-end

## API Contract
{api_contract}

## Steps You MUST Do (in order):

### 1. Fix Backend to be runnable
- Check `application-nomysql.yml` exists (H2 in-memory DB for local dev)
  - If not, create it with: H2 MODE=MySQL, ddl-auto: create-drop, flyway disabled
- Check CORS config allows localhost:3001
- Add `@Setter` and `@NoArgsConstructor` to JPA entities if missing
- Create a DataInitializer class (@Profile("nomysql")) that inserts test data on startup
- Run `./gradlew compileJava` — fix any errors

### 2. Start Backend and verify API
- Run: `./gradlew bootRun --args='--spring.profiles.active=nomysql'` in background
- Wait 10 seconds for startup
- Test the API endpoint with curl: `curl http://localhost:8080/api/ambassador/my-page/status?memberId=1`
- If it fails, read the error and fix

### 3. Fix Frontend API calls
- Read the Backend Controller's `@RequestMapping` to get the actual URL paths
- Update Frontend's `api.ts` to call the correct Backend URLs
- The Backend has `context-path: /api` so full URL is `http://localhost:8080/api/` + controller path
- Add fallback to mock data if Backend is unreachable (try/catch with timeout)
- Add `AbortSignal.timeout(3000)` to fetch calls

### 4. Verify end-to-end
- Start Frontend: `npx next dev --port 3001`
- Open `http://localhost:3001/admin/ambassador/my_page`
- Check browser console for errors
- If there are errors, fix them

### 5. Cleanup
- Kill backend process when done testing
- Ensure Frontend works both WITH and WITHOUT backend (mock fallback)

## IMPORTANT
- Run gradle/npm commands to verify your changes compile
- If backend compile fails, fix it before moving on
- If frontend has import errors, fix them
- The final state must be: Frontend renders correctly and calls Backend API when available
"""


async def integrate_frontend_backend(
    spec: dict | None,
    api_contract: str | None,
    frontend_dir: Path,
    backend_dir: Path | None = None,
    worker: ClaudeCLIWorker | None = None,
) -> IntegrationResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    api_summary = api_contract[:2000] if api_contract else "No API contract available"

    # Find backend dir
    if backend_dir is None:
        backend_dir = frontend_dir.parent.parent.parent.parent.parent / "backend"

    prompt = INTEGRATION_PROMPT.format(
        api_contract=api_summary,
        frontend_dir=str(frontend_dir),
        backend_dir=str(backend_dir),
    )

    # Run from project root so CLI can access both frontend and backend
    project_root = frontend_dir
    while project_root.name != "silicon2-migration" and project_root != project_root.parent:
        project_root = project_root.parent

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=15,
        cwd=project_root,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return IntegrationResult(success=False, error=result.error)

    # Check what files were modified
    modified = []
    for d in [frontend_dir, backend_dir]:
        if d and d.exists():
            for f in d.rglob("*.java"):
                modified.append(str(f.relative_to(project_root)))
            for f in d.rglob("*.ts"):
                modified.append(str(f.relative_to(project_root)))
            for f in d.rglob("*.tsx"):
                modified.append(str(f.relative_to(project_root)))
            for f in d.rglob("*.yml"):
                modified.append(str(f.relative_to(project_root)))

    return IntegrationResult(
        success=True,
        files_modified=modified[:30],
        report={"output": result.output[:500], "cost": result.cost, "duration_ms": result.duration_ms},
    )
