from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class IntegrationResult:
    success: bool
    report: dict = field(default_factory=dict)
    files_modified: list[str] = field(default_factory=list)
    error: str = ""
    cost: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    duration_ms: int = 0


INTEGRATION_PROMPT = """You are performing end-to-end integration between a React frontend and Spring Boot backend.

## Your Goal
Make the Frontend (React/Next.js) successfully call the Backend (Spring Boot) API and display real data.
ALL interactive elements (buttons, filters, search, pagination) MUST actually work end-to-end.

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
  - Insert at least 10 realistic test records with varied categories, dates, statuses
- Run `./gradlew compileJava` — fix any errors

### 2. Start Backend and verify API
- Run: `./gradlew bootRun --args='--spring.profiles.active=nomysql'` in background
- Wait 10 seconds for startup
- Test the API endpoint with curl (check controller's @RequestMapping for actual path)
- If it fails, read the error and fix

### 3. Fix Frontend API calls
- Read the Backend Controller's `@RequestMapping` to get the actual URL paths
- Update Frontend's `api.ts` to call the correct Backend URLs
- The Backend has `context-path: /api` so full URL is `http://localhost:8080/api/` + controller path
- Add fallback to mock data if Backend is unreachable (try/catch with timeout)
- Add `AbortSignal.timeout(3000)` to fetch calls

### 4. Make ALL Interactive Elements Functional (CRITICAL)
This is the most important step. Every button, filter, dropdown, and input MUST work:

- **Search button**: Must send query parameters to Backend API and display filtered results
- **Category/Type dropdowns**: Must filter results by selected category via API query param
- **Date range pickers**: Must send date_from/date_to params to Backend API
- **Pagination**: Must work with page/size query params
- **Status filters**: Must filter by status via API
- **Any other buttons**: Must trigger appropriate API calls

Implementation requirements:
- Use React state (useState) to track all filter values
- On Search click: call API with all current filter params as query string
- On filter change: either auto-search or wait for Search click (match original PHP behavior)
- Show loading spinner/state during API calls
- Show "검색 결과가 없습니다" (No results) when API returns empty array
- Display result count (e.g., "총 N건")
- After API returns, update the displayed list/table with real results

**YOU MUST ALSO RENDER THE RESULTS IN JSX.** Do NOT just update state — the page.tsx must contain
JSX that maps over the results array and renders each item as a card/row. Include:
- A loading spinner while `loading` is true
- A "검색 결과가 없습니다" message when results array is empty after search
- A "총 N건" count above the results list
- Each result rendered as a card/row showing its key fields (title, category, date, status, etc.)

Example pattern:
```typescript
const [filters, setFilters] = useState({{ keyword: '', category: '', dateFrom: '', dateTo: '' }});
const [results, setResults] = useState([]);
const [loading, setLoading] = useState(false);
const [searched, setSearched] = useState(false);

const handleSearch = async () => {{
  setLoading(true);
  setSearched(true);
  const params = new URLSearchParams();
  if (filters.keyword) params.set('keyword', filters.keyword);
  if (filters.category) params.set('category', filters.category);
  // ... other filters
  const data = await fetchFromApi(`/endpoint?${{params.toString()}}`);
  setResults(data.content || data);
  setLoading(false);
}};

// In JSX — MUST be included:
{{loading && <div className="flex justify-center py-8"><div className="w-6 h-6 border-2 border-black border-t-transparent rounded-full animate-spin" /></div>}}
{{!loading && searched && results.length === 0 && <p className="text-center py-8 text-gray-500">검색 결과가 없습니다</p>}}
{{!loading && results.length > 0 && (
  <>
    <p className="text-sm text-gray-600 mb-3">총 {{results.length}}건</p>
    <div className="space-y-3">
      {{results.map((item) => (
        <div key={{item.id}} className="border rounded-xl p-4">
          /* render item fields here */
        </div>
      ))}}
    </div>
  </>
)}}
```

### 5. Backend must support query parameters
- Ensure the Controller accepts query params: keyword, category, dateFrom, dateTo, page, size
- Implement filtering logic in Repository (use @Query or Specification)
- Return paginated results with total count

### 6. Verify end-to-end
- Start Frontend: `npx next dev --port 3001`
- Test with curl that the API responds correctly to filter params:
  - `curl "http://localhost:8080/api/.../list?keyword=test"`
  - `curl "http://localhost:8080/api/.../list?category=some_cat"`
- Verify frontend compiles without errors: `npx next build` or check dev server logs

### 7. Cleanup
- Kill backend process when done testing
- Ensure Frontend works both WITH and WITHOUT backend (mock fallback)

## IMPORTANT
- Run gradle/npm commands to verify your changes compile
- If backend compile fails, fix it before moving on
- If frontend has import errors, fix them
- The final state must be: Frontend renders correctly, ALL buttons/filters work with Backend API
- Do NOT leave any button as no-op. Every interactive element must produce a visible result.
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
        return IntegrationResult(
            success=False,
            error=result.error,
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )

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
        report={"output": result.output[:500]},
        cost=result.cost,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cache_creation_tokens=result.cache_creation_tokens,
        cache_read_tokens=result.cache_read_tokens,
        duration_ms=result.duration_ms,
    )
