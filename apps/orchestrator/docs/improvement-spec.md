# Silicon2 Orchestrator 개선 스펙

> **컨텍스트**
> - 로컬 단일 사용자 마이그레이션 오케스트레이터 (운영 서비스 아님)
> - 인증·멀티워커·HA는 비핵심
> - 기존 `data/orchestrator.db`의 데이터(spec_gen_history, pages 등)는 **보존**
> - Critical → Cost → Durability → Quality → Cleanup 5단계로 **분리** 적용
> - 각 Phase는 독립 커밋, Phase 끝에 `pytest`로 회귀 확인

## 공통 규칙

- 새로운 파일은 기존 패키지 구조를 유지: `src/<sub>/<module>.py`
- 모든 신규/변경 함수에는 타입 힌트 포함
- 기존 테스트는 깨지지 않게 유지. 동작이 바뀐 부분은 테스트도 함께 갱신
- 신규 동작에는 단위 테스트 1개 이상 추가
- `datetime.utcnow()` 신규 사용 금지 (Phase 3에서 일괄 마이그레이션)
- 로그는 Phase 5 도입 전까지는 `event_bus.emit` 그대로 사용

---

# Phase 1 — Critical 버그 픽스 (correctness)

목표: 현재 silent failure / hang / 보안 위험을 모두 제거. DB 스키마 변경 없음.

## C1. `_SessionFactory` 모듈 임포트 버그

### 현재 동작
`src/api/routes/spec_gen.py:13`에서 `from src.db.deps import _SessionFactory`로 모듈 변수를 직접 임포트. 임포트 시점의 `None`이 영원히 캡처되어 `_save_history` / `get_history`가 항상 None 분기로 빠짐.

### 목표 동작
세션 팩토리를 동적으로 가져오는 헬퍼를 노출하고 모든 호출처가 이를 통해 접근. 모듈 변수 직접 import 금지.

### 변경 파일
- `src/db/deps.py`: `get_session_factory() -> sessionmaker | None` 추가. 내부에서 `_SessionFactory`가 None이면 `configure_db()` 호출 후 반환.
- `src/api/routes/spec_gen.py`: top-level `from src.db.deps import _SessionFactory` 제거 → `from src.db.deps import get_session_factory` 사용. `_SessionFactory` 참조를 `get_session_factory()` 호출로 교체.
- `src/api/routes/pipeline.py`: `_get_engine()` 내부의 어색한 재-import 제거, `get_session_factory()` 사용.

### 검증
- 신규 테스트: `tests/test_spec_gen_history.py` — `_save_history` 호출 후 DB에서 SpecGenHistory 행이 조회되는지.
- 기존 `tests/test_api.py`의 `deps._SessionFactory = None` 직접 조작은 `deps.reset_session_factory()` 헬퍼로 교체.

## C3. Claude CLI 타임아웃 미작동

### 현재 동작
`src/workers/claude_cli.py:111`의 `proc.wait(timeout=10)`은 stdout 스트림이 EOF에 도달한 뒤에만 호출되므로 실제 hang에는 무방비. 예외 메시지는 "300s"라고 적혀 있지만 실효 타임아웃 없음.

### 목표 동작
실제 전체 wall-clock 타임아웃을 강제. 기본 300초, 호출자가 override 가능. 타임아웃 시 자식 프로세스 그룹 전체 종료 (`os.killpg`).

### 변경 파일
- `src/workers/claude_cli.py`:
  - `ClaudeCLIWorker.__init__`에 `default_timeout: int = 600` 파라미터 추가.
  - `invoke()` / `_invoke_sync()`에 `timeout: int | None = None` 파라미터 추가.
  - `Popen` 호출 시 `start_new_session=True` (POSIX) 또는 `creationflags=subprocess.CREATE_NEW_PROCESS_GROUP` (Windows) 설정. 호환 위해 POSIX만 우선.
  - stdout 루프를 `threading.Thread`로 옮기고 메인은 deadline 기반 polling. 또는 `selectors`로 deadline-aware read. 가장 단순하게: `proc.communicate(timeout=...)` 활용 — 단, stream-json 라이브 emit 손실되므로 별도 thread + queue.
  - 타임아웃 발생 시 `os.killpg(os.getpgid(proc.pid), SIGTERM)` → 2초 대기 → `SIGKILL`.
- 호출처 (`step3_api_contract`, `step4_react_gen`, `step5_java_gen`, `step7_integration`, `routes/project.py`)에 적절한 timeout 명시:
  - api_contract: 180s
  - react_gen: 900s
  - java_gen: 1800s (TDD 루프)
  - java_test: gradle 자체는 worker 미사용
  - integration: 1200s
  - project init (frontend/backend scaffold): 600s

### 검증
- 신규 단위 테스트: 가짜 sleep 스크립트를 `claude_path`로 주입해 timeout 발동 확인.
- 기존 `test_claude_cli.py` 유지.

## C4. 품질 게이트가 항상 통과

### 현재 동작
- `step6_java_test`: gradle test 실패 시에도 `success=True` 리턴.
- `step8_equivalence`: `java_files` 리스트가 비어있지만 않으면 모든 operation을 `covered`로 분류.

### 목표 동작
- Step6: gradle test exit code != 0이면 `success=False`. 단, 일시 인프라 문제(timeout, gradlew 없음)는 success=True로 두되 `warning` 필드로 표시.
- Step8: 실제로 생성된 Java 파일을 스캔해 클래스/메서드 시그니처를 추출하고, spec의 `operations[*].id` 또는 `http_method + route` 매칭으로 covered/missing 산출. 매핑 매칭은 단순 휴리스틱(파일명/메서드명 포함 여부)으로 시작.

### 변경 파일
- `src/pipeline/steps/step6_java_test.py`:
  - 테스트 실패 시 `JavaTestResult(success=False, ...)` 리턴.
  - `tests_failed` 카운트를 stdout/stderr에서 정규식으로 정확히 파싱 (`r"(\d+)\s+tests? failed"` 또는 gradle JSON 리포트 활용).
  - timeout/no-gradlew는 `success=True, warning="..."`로 유지하되 `error` 대신 `warning` 필드 신설.
- `src/pipeline/steps/step8_equivalence.py`:
  - 새 헬퍼 `_extract_java_endpoints(java_files: list[str], backend_root: Path) -> list[dict]` — 각 .java 파일을 열어 `@GetMapping`/`@PostMapping`/`@RequestMapping` 정규식으로 (method, path) 추출.
  - spec의 `operations`와 매칭. id 또는 (http_method, route) 정확 일치를 covered. 둘 다 안 맞으면 missing.
  - 결과: covered/missing/extra 3-way 분류. `success = len(missing) == 0`.

### 검증
- `tests/test_steps_codegen.py`에 Step6 실패/성공 분기 테스트 추가.
- 신규 `tests/test_step8_equivalence.py` — 가짜 .java 파일 fixture로 endpoint 추출 확인.

## C5. `page_id` Path Traversal 방지

### 현재 동작
API로 받은 `page_id`를 검증 없이 `page_id.replace(".", "/")` 형태로 파일 경로에 연결. `..`가 포함되면 출력 디렉토리 밖 쓰기 가능.

### 목표 동작
모든 API 입력 단에서 `page_id`를 정규식 검증. 패턴: `^[a-z0-9_]+(\.[a-z0-9_]+)*$`. 위반 시 400.

### 변경 파일
- `src/api/validators.py` (신규):
  - `PAGE_ID_PATTERN = re.compile(r"^[a-z0-9_]+(\.[a-z0-9_]+)*$")`
  - `validate_page_id(page_id: str) -> str` — 검증 후 반환, 실패 시 `HTTPException(400)`.
- 라우터 변경:
  - `routes/pages.py`: `get_page` path param 검증.
  - `routes/pipeline.py`: `PipelineRunRequest.page_ids` validator, `StepRunRequest.page_id` validator, `StepRetryRequest.page_id` validator. Pydantic `@field_validator` 활용.
  - `routes/spec_gen.py`: `_extract_from_url` 결과도 같은 정규식으로 한 번 더 통과.
- `src/pipeline/steps/registry.py`: 경로 결합 직전에 `safe_path_segment(page_id) -> str` 헬퍼 통과. 방어적 이중 검증.

### 검증
- 신규 테스트 `tests/test_validators.py`:
  - `validate_page_id("shop.products")` 성공
  - `validate_page_id("../etc/passwd")` 실패
  - `validate_page_id("shop/products")` 실패 (슬래시 거부)
  - `validate_page_id("Shop.Products")` 실패 (대문자 거부)

## C6. State Machine 일관성

### 현재 동작
`engine.py`에서 `page.migration_status = "running"`을 직접 대입. `transition_page()`는 검증만 하고 결과를 무시. 잘못된 전이가 통과되어도 알 수 없음.

### 목표 동작
모든 페이지 상태 변경은 `_set_page_state(page, target)` 헬퍼 경유. 헬퍼는 `transition_page(current, target)` 결과를 받아 `page.migration_status`에 대입. 잘못된 전이는 `InvalidTransitionError`로 즉시 실패. Step execution 상태 전이도 동일 헬퍼 사용.

### 변경 파일
- `src/pipeline/engine.py`:
  - `_set_page_state(page: Page, target: PageState, *, session: Session) -> None` 헬퍼.
  - `_set_step_state(execution: StepExecution, target: StepState) -> None` 헬퍼.
  - `run()` / `run_next_step()` / `_execute_step()`의 모든 직접 대입을 헬퍼 호출로 교체.
  - retry_step 경로 (`routes/pipeline.py:_retry_step_bg`)에서 BLOCKED → RUNNING 전이도 헬퍼 사용 (이미 page_transitions에 허용됨).
- `src/pipeline/state_machine.py`:
  - `VALID_PAGE_TRANSITIONS`에 `COMPLETE → RUNNING` 추가 (재실행 허용). 또는 명시적 `reset()` 메서드 추가. → **결정: COMPLETE → RUNNING은 막고, 명시적 retry-step 경로에서만 page를 새 사이클로 진입시키도록 한다.**

### 검증
- `tests/test_engine.py`에 잘못된 전이 시도 시 InvalidTransitionError 케이스 추가.
- 기존 `test_state_machine.py` 유지.

## Phase 1 종료 기준

- [ ] `pytest` 전체 통과
- [ ] spec-gen 1회 수동 실행 후 DB의 `spec_gen_history` 행 확인
- [ ] Claude CLI에 sleep 무한 루프 스크립트 주입 시 deadline 후 SIGTERM 확인
- [ ] `curl ... -d '{"page_ids":["../../etc/passwd"]}'` → 400

---

# Phase 2 — 비용 추적 정상화

목표: 실제 LLM 비용이 DB에 정확히 누적. CostLog, Page.total_cost가 신뢰 가능한 메트릭이 되어야 함.

## P2.1 모델 가격표 갱신 + 캐시 토큰 분리

### 현재 동작
`workers/analysis.py:15`의 `MODEL_PRICING`은 (input, output) 2축만 가지며 단가도 부정확. `_invoke_sync`에서 `cache_creation_input_tokens` + `cache_read_input_tokens`가 일반 input과 동일 단가로 합산됨.

### 목표 동작
- 가격표를 4축 (input, output, cache_write, cache_read)으로 확장.
- 실제 Anthropic 공시가 반영 (Haiku $0.80/$4, Sonnet $3/$15, Opus $15/$75 per 1M tokens; cache_write 1.25배 input, cache_read 0.1배 input).
- 모든 cost 계산을 새 가격표로.
- 호출 응답에서 cache 토큰 별도 추적해 `LLMResponse`에 `cache_creation_tokens`, `cache_read_tokens` 필드 추가.

### 변경 파일
- `src/workers/analysis.py`:
  - `MODEL_PRICING` 구조 변경.
  - `LLMResponse` 데이터클래스에 `cache_creation_tokens: int = 0`, `cache_read_tokens: int = 0` 추가.
  - `_invoke_sync`에서 4종 토큰을 분리 계산.
- `src/workers/claude_cli.py`:
  - `CLIResult`에 `cache_creation_tokens`, `cache_read_tokens` 추가.
  - stream-json `result` 이벤트의 `usage`에서 4종 토큰 분리 파싱.
  - 비용 계산은 CLI가 직접 주는 `total_cost_usd`를 우선 사용, 없으면 가격표로 재계산.

### 검증
- 단위 테스트: 더미 `LLMResponse` 토큰을 주어 expected cost와 일치.
- `tests/test_analysis_worker.py` 갱신.

## P2.2 Step4/5/6/7 비용 전파

### 현재 동작
`generate_react`, `generate_java`, `generate_java_tests`는 CLI 결과의 cost/토큰을 자기 결과 데이터클래스에 담지 않음. 그래서 registry의 `Step4ReactGen.execute` 등이 `cost=0, input_tokens=0`인 StepResult를 만들어 CostLog가 안 생기거나 0으로 누적.

### 목표 동작
모든 LLM 호출 step이 cost/토큰을 빠짐없이 StepResult에 담음.

### 변경 파일
- `src/pipeline/steps/step4_react_gen.py`:
  - `ReactGenResult`에 `cost`, `input_tokens`, `output_tokens`, `cache_creation_tokens`, `cache_read_tokens` 필드 추가.
  - `generate_react`가 `CLIResult`에서 4종 토큰 + cost를 복사.
- `src/pipeline/steps/step5_java_gen.py`: 동일.
- `src/pipeline/steps/step6_java_test.py`: gradle만 돌므로 cost=0 그대로. 단 duration_ms는 정확히 측정.
- `src/pipeline/steps/step7_integration.py`: `IntegrationResult`에 cost/tokens 필드 노출 (현재 report dict로 우회 중) → 명시 필드로 정리.
- `src/pipeline/steps/registry.py`:
  - 각 Step의 `execute`가 위 필드를 그대로 `StepResult`로 전달.
- `src/pipeline/engine.py`:
  - `_execute_step`이 `result.cost > 0` 분기뿐 아니라 `result.input_tokens > 0 or result.cost > 0` 조건으로 CostLog 생성 (cost가 0이지만 토큰이 있는 경우도 기록).
  - CostLog 모델에 캐시 토큰 컬럼은 Phase 3 마이그레이션에서 추가하고, Phase 2에서는 기존 `cache_read_tokens` 컬럼만 사용 (이미 모델에 있음).

### 검증
- 신규 테스트: Mock step이 cost/토큰을 리턴할 때 CostLog 행 + Page.total_cost 누적 확인 (기존 test_engine.py:test_cost_is_recorded 확장).
- Step4/5의 CLIResult mock 주입 후 전파 단위 테스트.

## Phase 2 종료 기준

- [ ] `pytest` 전체 통과
- [ ] Mock 통합 테스트로 1회 파이프라인 실행 시 CostLog 행 수가 LLM 호출 step 수와 일치
- [ ] Page.total_cost == sum(CostLog.cost for that page)

---

# Phase 3 — 영속화 + Resumability + Deprecated API 정리

목표: 서버 재시작 후에도 작업 상태 보존. Python 3.12+ 호환. EventBus가 안전하게 동시성 처리.

## P3.1 Alembic 도입 + 베이스라인

### 현재 동작
`configure_db()`가 `Base.metadata.create_all`로만 스키마 생성. 컬럼 추가/제거 시 운영 DB와 불일치.

### 목표 동작
- `alembic` 패키지 추가, `alembic/` 디렉토리 생성.
- 베이스라인 마이그레이션 1개: 현재 모델 스키마 = 베이스라인.
- `configure_db()`는 `Base.metadata.create_all`를 유지 (테스트 in-memory용)하되 운영 시작 시 `alembic upgrade head` 호출 분기 추가.
- 기존 `data/orchestrator.db`는 첫 실행 시 자동으로 `alembic stamp <baseline_rev>`로 마킹 (이미 같은 스키마이므로 안전).

### 변경 파일
- `pyproject.toml`: `alembic>=1.13.0` 추가.
- `alembic/` (신규):
  - `alembic.ini`
  - `env.py` — `Settings().database_url` 동적 사용
  - `versions/0001_baseline.py` — autogenerate로 현재 스키마 캡처
- `src/db/deps.py`:
  - `configure_db()` signature 유지하되 `auto_migrate: bool = True` 파라미터 추가.
  - 운영 (sqlite 파일 경로일 때):
    - DB 파일이 없으면 → `Base.metadata.create_all` → `alembic stamp head`
    - DB 파일이 있고 alembic_version 테이블 없음 → `alembic stamp head` (베이스라인으로 간주)
    - DB 파일이 있고 alembic_version 있음 → `alembic upgrade head`
  - 테스트 (in-memory) → `Base.metadata.create_all`만.
- `src/main.py`의 lifespan에서 `configure_db()` 호출.

### 검증
- 기존 `data/orchestrator.db`를 백업 후 새 코드로 한 번 띄워 alembic_version 테이블 생성 + 데이터 보존 확인.
- 신규 `tests/test_alembic.py`: 임시 sqlite 파일에 대해 `alembic upgrade head` 후 스키마 일치 확인.

## P3.2 In-memory 작업 상태 영속화

### 현재 동작
`_running_tasks` (pipeline.py), `_spec_gen_status` (spec_gen.py), `_init_status` (project.py)가 dict에 저장.

### 목표 동작
- 파이프라인 작업 상태는 **별도 테이블 불필요**. `Page.migration_status` + `StepExecution` 마지막 행으로 도출 가능. 따라서 `_running_tasks` 제거하고 `GET /pipeline/status`는 DB 조회로 응답.
- spec-gen 세션 상태는 **세션 단위로 휘발성**이지만 페이지 재시작 시 진행 중인 세션이 끊기는 게 정상 동작이라 dict 유지. 단 lifespan-bounded weakref 또는 TTL 만료 추가.
- project init 상태(`_init_status`)도 동일하게 dict 유지하되 startup에서 frontend/backend 디렉토리 존재 여부로 idle/complete 도출.

### 변경 파일
- `src/api/routes/pipeline.py`:
  - `_running_tasks` 제거.
  - `GET /pipeline/status` → `Page` 테이블에서 `migration_status IN ('running', 'blocked')` 행을 조회해 응답.
  - run/run-step/retry-step 핸들러는 task_id를 응답으로 반환하지만 내부 상태는 DB에서 도출.
- `src/api/routes/spec_gen.py`:
  - `_spec_gen_status` dict 유지하되 entry에 `created_at: float` 추가.
  - 백그라운드 cleanup task (lifespan)에서 1시간 초과 entry 제거.
- `src/api/routes/project.py`:
  - startup 시 `package.json`/`build.gradle.kts` 존재 여부 보고 `_init_status` 초기값 결정.

### 검증
- 신규 `tests/test_pipeline_status.py`: 페이지 상태 시드 후 `GET /pipeline/status` 결과 확인.

## P3.3 Lifespan + datetime.now(timezone.utc) + asyncio loop

### 현재 동작
- `@app.on_event("startup")` 사용 (deprecated).
- `asyncio.get_event_loop()` (events.py:34) deprecated.
- `datetime.utcnow()` 다수.

### 목표 동작
- `lifespan` async context manager로 마이그레이션. startup/shutdown 모두 명시.
- `event_bus.set_loop()`은 lifespan 안에서 `asyncio.get_running_loop()` 호출.
- 신규 헬퍼 `src/util/clock.py`:
  ```python
  from datetime import datetime, timezone
  def utcnow() -> datetime: return datetime.now(timezone.utc)
  ```
- 모든 `datetime.utcnow()` 호출을 `utcnow()`로 치환.
- DB 모델의 `default=datetime.utcnow` → `default=utcnow`.

### 변경 파일
- `src/main.py`: lifespan 구현.
- `src/util/__init__.py`, `src/util/clock.py` (신규).
- `src/db/models.py`: utcnow 임포트 교체. **단 컬럼은 TIMESTAMP 그대로 (timezone-naive 저장 유지)** — Alembic 마이그레이션 없이 호환되도록 함수만 변경.
- `src/pipeline/engine.py`, `src/api/routes/pipeline.py`, `src/api/routes/spec_gen.py`: 호출처 교체.

### 검증
- `pytest -W error::DeprecationWarning`으로 deprecation 0건 확인 (Phase 3 종료 시).

## P3.4 EventBus 동시성 안전

### 현재 동작
list 기반 connection 저장, lock 없음, 닫힌 소켓 send 실패 시 일부 예외만 swallow.

### 목표 동작
- `asyncio.Lock`으로 register/unregister/emit 보호.
- emit은 closed connection을 자동 제거.
- 동기 호출자도 안전하도록 `emit(event, data)`은 내부적으로 `asyncio.run_coroutine_threadsafe` 사용.

### 변경 파일
- `src/api/ws/events.py`:
  - `_connections: set[WebSocket]` (set으로 변경, 순서 무의미).
  - `_lock: asyncio.Lock`.
  - `async def _broadcast(message)` 내부 메서드.
  - `emit()`은 sync API 유지하되 `run_coroutine_threadsafe(self._broadcast(message), self._loop)`로 위임.
  - send 실패 시 해당 ws를 자동 unregister.
- `threading` 임포트 제거 (dead).

### 검증
- 신규 `tests/test_event_bus.py`: 동시에 register/emit/unregister 호출 후 일관성 확인.

## Phase 3 종료 기준

- [ ] `pytest` 전체 통과
- [ ] 서버 재시작 후 `GET /api/pipeline/status` 결과가 DB와 일치
- [ ] `DeprecationWarning` 0건
- [ ] 기존 sqlite 파일에서 데이터 보존 확인

---

# Phase 4 — 품질 게이트 진짜 동작 + 설정 외부화

목표: Visual diff, Java tests, equivalence가 실제로 의미 있는 신호를 만들어내고, 환경/포트 하드코딩 제거.

## P4.1 SSIM 기반 비주얼 비교

### 현재 동작
`_compare_screenshots`가 RGB 픽셀 차이의 절대값 평균. 안티앨리어싱·폰트 렌더링 차이만으로 임계 초과.

### 목표 동작
- `scikit-image`의 SSIM(Structural Similarity Index)으로 비교.
- 기준값을 `Settings.visual_diff_threshold` 의미 변경: "최대 허용 diff %" → "최소 허용 SSIM (0~1)". 기본 0.85.
- 두 이미지 크기 다르면 작은 쪽에 맞춰 crop or resize.

### 변경 파일
- `pyproject.toml`: `scikit-image>=0.24.0` 추가 (numpy는 기존).
- `src/pipeline/steps/step4_react_gen.py`:
  - `_compare_screenshots` 재구현 → `(ssim_score: float, diff_pct_fallback: float)` 튜플 반환.
  - `verify_visual_similarity`의 success 판정: `ssim >= settings.visual_similarity_threshold`.
- `src/config.py`: `visual_similarity_threshold: float = 0.85` (기존 `visual_diff_threshold` 유지하되 deprecated 표기 후 사용처 교체).

### 검증
- 신규 `tests/test_visual_compare.py`: PIL로 동일/유사/다른 PNG 3쌍 생성 후 SSIM 점수 확인.

## P4.2 포트/경로 Settings 화

### 현재 동작
- `verify_visual_similarity`의 `port=3001` 하드코딩, `services.py`의 frontend 포트 3001과 충돌.
- `Path(__file__).parent.parent.parent.parent.parent.parent` 패턴 (4곳).
- claude_path, mcp python_path 하드코딩.

### 목표 동작
- `Settings`에 다음 필드 추가:
  - `project_root: Path` — 자동 탐지 (env 또는 marker file `.silicon2-root` 탐색)
  - `frontend_port: int = 3001`
  - `backend_port: int = 8080`
  - `visual_check_port: int = 3099` (independent)
  - `claude_path: str = "claude"` (PATH 기반 기본)
  - `mcp_python_path: str = "python3"`
- 모든 호출처가 Settings 경유.

### 변경 파일
- `src/config.py`: 위 필드 추가. `project_root` validator로 marker file 탐색.
- `src/workers/claude_cli.py`: 기본값을 `"claude"`로, Settings 우선.
- `src/workers/mcp.py`: 동일.
- `src/pipeline/steps/step4_react_gen.py`: `verify_visual_similarity(port=...)` 호출처가 settings.visual_check_port 사용.
- `src/api/routes/services.py`, `routes/project.py`, `pipeline/steps/registry.py`: `Path(__file__).parent.parent...` → `Settings().project_root`.

### 검증
- 신규 `tests/test_config.py`: marker file이 있는 임시 디렉토리에서 Settings가 올바른 root 탐지.

## P4.3 파이프라인 step 수 하드코딩 제거

### 현재 동작
`engine.py:112`의 `next_step_num == 9` 비교.

### 목표 동작
- `PipelineEngine`이 `self.steps[-1].step_number`를 `_final_step_number`로 저장.
- 모든 비교는 `_final_step_number` 사용.

### 변경 파일
- `src/pipeline/engine.py`.

### 검증
- 기존 `test_engine.py` 통과.

## Phase 4 종료 기준

- [ ] `pytest` 전체 통과
- [ ] 수동: 동일 페이지 캡처 2장 SSIM ≥ 0.95 확인
- [ ] Settings 변경 없이 다른 머신에서 import 가능 (마커 파일 탐색)
- [ ] 9 → 10 step 추가 시 (가상의 step10 mock) 완료 판정 정상

---

# Phase 5 — 정리: Worktree 통합, DRY, Dead Code, Logging

목표: 미연결 컴포넌트 통합, 중복 제거, 표준 logging 도입.

## P5.1 Worktree + GitManager 통합

### 현재 동작
`WorktreeManager`, `GitManager` 정의만 되어 있고 파이프라인이 단일 디렉토리에서 작업.

### 목표 동작
- `PipelineEngine`에 `worktree_manager: WorktreeManager | None` 주입.
- 페이지 시작 시 `migration/<page_id>` 브랜치 + worktree 생성, 모든 step의 cwd가 worktree path 기준.
- 페이지 완료 시 `commit_step`으로 자동 커밋, 실패 시 worktree 보존(디버깅용).
- registry의 `output_base` 등 경로가 worktree 기준이 되도록 전달 체계 정리.

### 변경 파일
- `src/pipeline/engine.py`:
  - `run()` 시작 시 worktree 생성, `StepContext`에 `workspace_root: Path` 추가.
  - step 사이마다 `GitManager.commit_step` 호출.
- `src/pipeline/steps/registry.py`: 각 Step이 `output_base` 대신 `context.workspace_root` 기반으로 동작하도록 refactor.

### 검증
- 신규 통합 테스트: 임시 git repo에서 1-page 실행 후 worktree 생성 + 커밋 1개 확인.

## P5.2 중복 제거

- `_init_frontend` / `_init_backend` → 공통 `_init_target(target, prompt, marker_file)` 함수로 통합.
- Playwright 로그인 + 캡처를 `workers/playwright.py`로 일원화. `spec_gen.py:_do_capture`는 이를 호출.
- `services.py`의 start/stop을 `_start_service(name)`, `_stop_service(name)` 헬퍼로 통합.

## P5.3 Dead Code / 정리

- `workers/claude_cli.py:_parse_json_output` 제거.
- `api/ws/events.py:import threading` 제거.
- `db/session.py`와 `db/deps.py` 통합 (deps.py만 남기고 session.py 제거 또는 deps.py가 session.py를 호출하도록).

## P5.4 Logging 도입

- `src/util/logging.py`: `get_logger(name)` 헬퍼.
- 표준 `logging` 모듈, JSON 포맷터 (운영용) + 콘솔 핸들러.
- 주요 경로에 `logger.info/warning/error` 추가하되 event_bus.emit과 병행 (event_bus는 UI용, logger는 디스크용).
- `print` 호출 0건 (기존에는 없음, 회귀 방지).

## Phase 5 종료 기준

- [ ] `pytest` 전체 통과
- [ ] 1-페이지 통합 테스트 (mock CLI) — worktree 생성 + 커밋 + 정리 확인
- [ ] `ruff` / `mypy --strict` (선택) 통과

---

# 작업 진행 규약

각 Phase 시작 전:
1. `git status`로 워킹 트리 클린 확인
2. `pytest`로 baseline 통과 확인

각 Phase 종료 시:
1. 본 문서의 종료 기준 체크리스트 확인
2. `pytest` 통과
3. `git commit -m "phase N: <요약>"`로 단일 커밋
4. CHANGELOG 또는 본 문서 하단의 진행 로그에 한 줄 추가

---

# 진행 로그

- **Phase 1 완료** (2026-05-25) — C1 (`_SessionFactory` 헬퍼화), C3 (Claude CLI 실제 wall-clock 타임아웃 + process-group 종료), C4 (Step6 gradle 실패 전파, Step8 실제 endpoint 매칭), C5 (`validate_page_id` API/Pydantic/방어 검증 3-layer), C6 (`_set_page_state` 헬퍼로 상태 전이 강제 + step 9 하드코딩 제거). 부수적으로 Step5의 `"ambassador"` 하드코딩 필터 제거. 88 tests passing.
- **Phase 2 완료** (2026-05-25) — 모델 가격표 4축(input/output/cache_write/cache_read) 재작성 + Anthropic 공시가 반영. `compute_cost` 헬퍼 추출, `AnalysisWorker`가 cache_creation/cache_read 토큰을 별도 추적. 모든 LLM step (`step3_api_contract`, `step4_react_gen`, `step5_java_gen`, `step7_integration`)이 cost·input·output·cache 토큰·duration을 자기 결과 데이터클래스 및 `StepResult`로 전파. `engine._execute_step`이 cost==0이어도 토큰만 있으면 `CostLog` 기록. 95 tests passing.
