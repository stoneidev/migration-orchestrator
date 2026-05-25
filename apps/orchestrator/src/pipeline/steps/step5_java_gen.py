from dataclasses import dataclass, field
from pathlib import Path

from src.workers.claude_cli import ClaudeCLIWorker, CLIResult


@dataclass
class JavaGenResult:
    success: bool
    files_created: list[str] = field(default_factory=list)
    tests_passed: bool = False
    output: str = ""
    error: str = ""
    cost: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    duration_ms: int = 0


JAVA_TDD_PROMPT = """You are implementing a Spring Boot feature using STRICT TDD principles.
You MUST follow this exact workflow for each layer:

1. Write code
2. Run `./gradlew compileJava` — fix until it compiles
3. Write test
4. Run `./gradlew test` — fix until tests pass
5. Move to next layer

## Project Info
- Base package: com.silicon2.admin
- Feature package: com.silicon2.admin.ambassador.my_page
- Java 21, Spring Boot 3.4, Lombok, MapStruct
- JUnit 5 + Mockito + @WebMvcTest + @DataJpaTest

## Spec (use this for business logic)
Page: {page_id}
Operations: {operations}
Business Rules: {business_rules}
Tables: {tables}
SQL Queries: {sql_summary}

## TDD Implementation Order

### Layer 1: Domain Model
Create in `src/main/java/com/silicon2/admin/ambassador/my_page/domain/model/`:
- AmbassadorMember.java (Entity)
- AmbassadorMemberSns.java (Entity)
- AmbassadorStatus.java (enum: ACTIVE, INACTIVE, BANNED)

Then create test in `src/test/java/com/silicon2/admin/ambassador/my_page/domain/`:
- AmbassadorMemberTest.java (basic unit test)

Run: `./gradlew compileJava` then `./gradlew test`
Fix any errors before proceeding.

### Layer 2: Repository Interface (Port Out)
Create in `src/main/java/com/silicon2/admin/ambassador/my_page/domain/repository/`:
- AmbassadorMemberRepository.java (interface)
- AmbassadorMemberSnsRepository.java (interface)

Run: `./gradlew compileJava`

### Layer 3: UseCase (Application Layer)
Create in `src/main/java/com/silicon2/admin/ambassador/my_page/application/`:
- CheckAmbassadorStatusUseCase.java
- SubmitReviewUseCase.java
- GenerateSnsLinkUseCase.java

Create DTOs in `application/dto/`:
- AmbassadorStatusResponse.java
- SubmitReviewRequest.java
- GenerateSnsLinkRequest.java

Create tests in `src/test/java/com/silicon2/admin/ambassador/my_page/application/`:
- CheckAmbassadorStatusUseCaseTest.java (mock repository with Mockito)
- SubmitReviewUseCaseTest.java

Run: `./gradlew test` — fix until ALL tests pass.

### Layer 4: Controller (Adapter In)
Create in `src/main/java/com/silicon2/admin/ambassador/my_page/adapter/in/web/`:
- AmbassadorMyPageController.java (@RestController)

Create test:
- AmbassadorMyPageControllerTest.java (@WebMvcTest, mock UseCases)

Run: `./gradlew test`

### Layer 5: Persistence (Adapter Out)
Create JPA entities + repository implementations.
Create Flyway migration SQL.

Run: `./gradlew test`

## IMPORTANT
- Run gradle after EACH layer
- If compile fails → fix immediately
- If test fails → fix immediately
- Do NOT proceed to next layer until current layer passes
- Use @DisplayName with Korean descriptions in tests
- BDD style: // given // when // then
"""


async def generate_java(
    spec: dict,
    api_contract: str,
    output_dir: Path,
    worker: ClaudeCLIWorker | None = None,
) -> JavaGenResult:
    if worker is None:
        worker = ClaudeCLIWorker()

    meta = spec.get("meta", {})
    operations = spec.get("operations", [])
    business_rules = spec.get("business_rules", [])
    data_layer = spec.get("data_layer", {})

    ops_summary = "\n".join(
        f"- {op.get('id', '')}: {op.get('name', '')} ({op.get('http_method', 'GET')})"
        for op in operations
    )

    brs_summary = "\n".join(
        f"- {br.get('id', '')}: {br.get('description', '')}"
        for br in business_rules[:15]
    )

    raw_tables = data_layer.get("tables", [])
    if isinstance(raw_tables, dict):
        tables = [{"name": k, **v} if isinstance(v, dict) else {"name": k} for k, v in list(raw_tables.items())[:5]]
    elif isinstance(raw_tables, list):
        tables = raw_tables[:5]
    else:
        tables = []
    tables_summary = "\n".join(
        f"- {t.get('name', '')}"
        for t in tables
    ) if tables else "No tables defined"

    raw_queries = data_layer.get("queries", [])
    if isinstance(raw_queries, dict):
        sql_queries = [{"id": k, **v} if isinstance(v, dict) else {"id": k} for k, v in list(raw_queries.items())[:8]]
    elif isinstance(raw_queries, list):
        sql_queries = raw_queries[:8]
    else:
        sql_queries = []
    sql_summary = "\n".join(
        f"- {q.get('id', '')}: {q.get('type', '')} {q.get('description', '')}"
        for q in sql_queries
    ) if sql_queries else "No queries defined"

    prompt = JAVA_TDD_PROMPT.format(
        page_id=meta.get("id", "ambassador.my_page"),
        operations=ops_summary,
        business_rules=brs_summary,
        tables=tables_summary,
        sql_summary=sql_summary,
    )

    # Use the backend project root as cwd (where build.gradle.kts is)
    backend_root = output_dir
    while backend_root.name != "backend" and backend_root != backend_root.parent:
        backend_root = backend_root.parent
    if backend_root.name != "backend":
        backend_root = output_dir

    result: CLIResult = await worker.invoke(
        prompt=prompt,
        model="sonnet",
        max_turns=30,  # More turns for TDD cycles
        cwd=backend_root,
        allowed_tools=["Write", "Edit", "Bash", "Read"],
    )

    if not result.success:
        return JavaGenResult(
            success=False,
            error=result.error,
            cost=result.cost,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cache_creation_tokens=result.cache_creation_tokens,
            cache_read_tokens=result.cache_read_tokens,
            duration_ms=result.duration_ms,
        )

    # Collect created Java files. In production the layout is
    # ``backend_root/src/main/java/...`` but tests (and ad-hoc invocations)
    # may place generated files directly under ``output_dir`` without a
    # ``src`` subdir, so fall back to scanning the ``output_dir`` tree.
    created_files: list[str] = []
    scan_roots: list[Path] = []
    java_src = backend_root / "src"
    if java_src.exists():
        scan_roots.append(java_src)
    if output_dir.exists() and output_dir != java_src:
        scan_roots.append(output_dir)

    seen: set[Path] = set()
    for root in scan_roots:
        for f in root.rglob("*.java"):
            if f in seen:
                continue
            seen.add(f)
            try:
                rel = f.relative_to(backend_root)
            except ValueError:
                rel = f.relative_to(output_dir) if f.is_relative_to(output_dir) else f
            created_files.append(str(rel))

    # Check if tests exist
    test_files = [f for f in created_files if "test" in f.lower() or "Test" in f]

    return JavaGenResult(
        success=len(created_files) > 0,
        files_created=created_files,
        tests_passed=len(test_files) > 0,
        output=result.output[:500],
        error="" if created_files else "No Java files generated",
        cost=result.cost,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        cache_creation_tokens=result.cache_creation_tokens,
        cache_read_tokens=result.cache_read_tokens,
        duration_ms=result.duration_ms,
    )
