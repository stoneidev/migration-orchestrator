# Silicon2 Orchestrator — Phase 6 개선 스펙

> **컨텍스트**
> - 로컬 단일 사용자 마이그레이션 오케스트레이터 (운영 서비스 아님)
> - Phase 1~5 (`docs/improvement-spec.md`) 완료 후 남은 **정합성·안정성·이식성·운영성** 개선
> - **범위 제외 (의도적)**: API/WebSocket 인증, 보안 강화 (자격증명 제거, SSRF 방어, shell injection 등)
> - 기존 `data/orchestrator.db` 데이터는 **보존**
> - 각 서브페이즈는 **독립 커밋**, 종료 시 `pytest` 회귀 확인

## 공통 규칙

- 새 파일은 기존 패키지 구조 유지: `src/<sub>/<module>.py`
- 모든 신규/변경 함수에 타입 힌트 포함
- 기존 테스트 유지; 동작 변경 시 테스트 함께 갱신
- 신규 동작에는 단위 테스트 1개 이상
- DB 스키마 변경 시 Alembic revision 필수 (baseline stamp 유지)

---

# 실행 계획 (Plan)

아래 순서는 **의존성·리스크·diff 크기** 기준. 한 서브페이즈 = 한 PR/커밋.

| 순서 | ID | 제목 | 리스크 | 예상 diff |
|------|-----|------|--------|-----------|
| 1 | 6A | Playwright 의존성 + README | 낮음 | S |
| 2 | 6B | 백그라운드 예외 → Page FAILED | 낮음 | S |
| 3 | 6C | 병렬 실행 직렬화 (`max_parallel_pages`) | 낮음 | S |
| 4 | 6D | `project_root` + 경로 이식성 | 중간 | M |
| 5 | 6E | CI (pytest) + 테스트 경로 이식성 | 낮음 | M |
| 6 | 6F | `.env.example` 동기화 | 낮음 | S |
| 7 | 6G | silent failure 제거 + CostLog cache_creation | 중간 | M |
| 8 | 6H | DB session DRY + 코드 정리 | 중간 | M |
| 9 | 6I | Worktree + GitManager 파이프라인 통합 | 높음 | L |

**현재 baseline**: 133 tests passing (`pytest`)

---

# Phase 6A — Playwright 의존성 + README

목표: 런타임 ImportError 방지, 신규 개발자 온보딩.

## 6A.1 Playwright optional extra

### 현재 동작
`src/workers/playwright.py`, `step4_react_gen.py`가 runtime에 `playwright` import. `pyproject.toml` dependencies에 없어 fresh install 시 Step 4/spec-gen 캡처 실패.

### 목표 동작
- `[project.optional-dependencies]`에 `playwright = ["playwright>=1.49.0"]` 추가
- dev extra에 playwright 포함: `dev = [..., "playwright>=1.49.0"]`
- ImportError 메시지는 유지하되 README에 설치 절차 명시

### 변경 파일
- `pyproject.toml`

### 검증
- `pip install -e ".[dev]"` 후 `python -c "import playwright"` 성공
- 기존 `tests/test_playwright_worker.py` 통과 (playwright 미설치 환경에서는 skip marker 유지)

## 6A.2 Orchestrator README

### 목표 동작
`apps/orchestrator/README.md` 신규 작성:
- 사전 요구사항 (Python 3.11+, Claude CLI, Node/Java for generated apps)
- 설치: venv, `pip install -e ".[dev]"`, `playwright install chromium`
- 필수 env vars (`SPECS_DIR`, `PHP_PROJECT_ROOT`, `MCP_SERVER_PATH`)
- 실행: `uvicorn src.main:app --reload --port 8000`
- Alembic: `alembic upgrade head`
- 테스트: `pytest`

### 변경 파일
- `apps/orchestrator/README.md` (신규)

### 검증
- README의 명령어가 현재 코드와 일치 (수동 spot-check)

## Phase 6A 종료 기준

- [x] README 존재, pyproject에 playwright extra 존재
- [~] `pytest` — 6A diff와 무관한 기존 4 failures 잔존 (129 passed). 6B~6E에서 정리 예정

---

# Phase 6B — 백그라운드 예외 시 Page FAILED

목표: 파이프라인/스텝 백그라운드 태스크 예외 시 `Page.migration_status` stuck `running` 방지.

## 6B.1 `_mark_page_failed` 헬퍼

### 현재 동작
`src/api/routes/pipeline.py`의 `_run_pipeline_bg`, `_run_single_step_bg`, `_retry_step_bg`는 예외 시 `PipelineTask`만 `failed`. `PageState.FAILED`는 state machine에 정의돼 있으나 engine/routes에서 미사용.

### 목표 동작
- `src/pipeline/engine.py`에 `mark_page_failed(page_id: str, session_factory: sessionmaker, error: str | None = None) -> None` 추가
  - Page가 `RUNNING`이면 `_set_page_state(page, PageState.FAILED)` 적용
  - `event_bus.emit("page_state", {...})` 로 UI 알림
- 세 background handler의 `except` 블록에서 task failed + `mark_page_failed` 호출
- Page가 DB에 없으면 no-op (task failed만 기록)

### 변경 파일
- `src/pipeline/engine.py`: `mark_page_failed` 추가
- `src/api/routes/pipeline.py`: 3개 bg handler 수정

### 검증
- `tests/test_pipeline_bg_failure.py` (신규):
  - mock engine이 예외 raise → Page.migration_status == `"failed"`, PipelineTask.status == `"failed"`

## 6B.2 `_rebuild_context` spec 로드 실패 경고

### 현재 동작
`engine._rebuild_context`가 spec 로드 실패를 `except Exception: pass`로 삼킴.

### 목표 동작
- 실패 시 `logger.warning` + `event_bus.emit("log", ...)` (silent pass 제거)
- spec 없이 step 실행은 기존과 동일 (step 자체가 실패 처리) — 동작 변경 최소화

### 변경 파일
- `src/pipeline/engine.py`

### 검증
- `tests/test_engine.py`에 broken specs_dir → warning emit 확인 (mock logger)

## Phase 6B 종료 기준

- [x] `pytest` — 6B 신규 7 tests 통과
- [x] bg exception 시 Page가 `failed`로 전환됨 (unit test)
- [x] `_rebuild_context` spec 로드 실패 시 warning emit

---

# Phase 6C — 병렬 실행 직렬화

목표: worktree 통합 전까지 shared monorepo 파일 corruption 방지.

## 6C.1 페이지 단위 asyncio Semaphore

### 현재 동작
`Settings.max_parallel_pages = 5`이 config에만 존재. `POST /pipeline/run`이 여러 page를 동시에 background task로 실행 가능. 모든 step이 `apps/frontend`, `apps/backend`에 직접 쓰기.

### 목표 동작
- `src/api/routes/pipeline.py`에 모듈 레벨 `_page_semaphore: asyncio.Semaphore | None = None`
- lifespan 또는 첫 요청 시 `Settings().max_parallel_pages`로 초기화
- `_run_pipeline_bg`, `_run_single_step_bg`, `_retry_step_bg` 진입 시 `async with semaphore:` 로 감싸기
- **기본값은 1로 변경** (`config.py`: `max_parallel_pages: int = 1`) — 로컬 안전 우선; `.env`로 override 가능

### 변경 파일
- `src/config.py`: default `max_parallel_pages` 5 → 1
- `src/api/routes/pipeline.py`: semaphore 적용
- `src/main.py`: lifespan에서 semaphore init (선택 — routes lazy init도 허용)

### 검증
- `tests/test_parallel_limit.py` (신규): semaphore=1일 때 두 bg task가 순차 실행됨 (mock sleep engine)

## Phase 6C 종료 기준

- [x] `pytest` — 6C 신규 3 tests + boot test 통과
- [x] default `max_parallel_pages=1` (code default; `.env` override 가능)
- [x] 동시 2 page run 시 semaphore=1이면 직렬화 (unit test)

---

# Phase 6D — project_root + 경로 이식성

목표: `Path(__file__).parent × 6` 및 Homebrew 하드코딩 제거.

## 6D.1 Settings.project_root 자동 탐지

### 현재 동작
- `registry.py`: `Path(__file__).parent.parent.parent.parent.parent.parent`
- `claude_cli.py`: `claude_path="/opt/homebrew/bin/claude"`
- `mcp.py`: Homebrew python 하드코딩

### 목표 동작
`Settings`에 추가:
```python
project_root: Path | None = None  # env PROJECT_ROOT
claude_path: str = "claude"
mcp_python_path: str = "python3"
```

`model_validator(mode="after")`:
1. `PROJECT_ROOT` env 있으면 사용
2. 없으면 CWD에서 상위로 올라가며 `apps/orchestrator/pyproject.toml` + `apps/frontend` 존재하는 디렉터리 탐색
3. 실패 시 orchestrator 패키지 기준 6단계 parent (기존 동작 fallback)

### 변경 파일
- `src/config.py`
- `src/pipeline/steps/registry.py`: `settings.project_root` 사용
- `src/workers/claude_cli.py`: default `"claude"`
- `src/workers/mcp.py`: Settings 경유
- `src/api/routes/project.py`, `services.py`: 동일

### 검증
- `tests/test_config.py` (신규): tmp monorepo layout에서 root 탐지

## Phase 6D 종료 기준

- [x] `/opt/homebrew` src/ 제거
- [x] `Settings.project_root` + registry/routes/workers 이식성
- [x] `tests/test_config.py`

## Phase 6E 종료 기준

- [x] `.github/workflows/orchestrator.yml`
- [x] e2e/integration tests — fixture + skip (CI friendly)

## Phase 6F 종료 기준

- [x] 루트 `.env.example` + `apps/orchestrator/.env.example` 갱신

## Phase 6G 종료 기준

- [x] `cache_creation_tokens` Alembic + CostLog + engine
- [x] `enforce_project_budget` soft gate

## Phase 6H 종료 기준

- [x] `deps.create_sqlalchemy_engine` WAL pragma 통합
- [x] `session.py` re-export

---

# Phase 6I — Worktree + GitManager 통합

목표: 페이지별 격리 workspace, step마다 auto-commit. **가장 큰 변경 — Phase 6C 이후 진행**.

## 6I.1 StepContext.workspace_root

### 목표 동작
- `PipelineEngine.run()` 시작 시 `WorktreeManager.create(page_id)` → `context.workspace_root`
- registry steps가 `output_base` 대신 `workspace_root / "apps/frontend/..."` 사용
- step 성공마다 `GitManager.commit_step(page_id, step_number, message)`
- 실패 시 worktree 보존 (cleanup은 manual 또는 COMPLETE 시)

### 변경 파일
- `src/pipeline/engine.py`
- `src/pipeline/steps/registry.py` + 각 step
- `src/workers/worktree.py`, `src/git/manager.py` (필요 시 소폭 수정)

### 검증
- `tests/test_worktree_pipeline.py` (신규): temp git repo, 1-page mock run → branch + ≥1 commit

## 6I.2 max_parallel_pages > 1 재활성화

worktree 격리 확인 후 default 또는 문서에서 parallel > 1 안전 사용 가능 명시.

## Phase 6I 종료 기준

- [x] `pytest` — worktree pipeline tests 통과
- [x] worktree 통합 + step마다 auto-commit
- [x] `USE_WORKTREE=false` fallback (기본 off)

---

# 작업 진행 규약

각 서브페이즈 시작 전:
1. `git status` 클린 확인
2. `cd apps/orchestrator && pytest` baseline 통과

각 서브페이즈 종료 시:
1. 본 문서 종료 기준 체크
2. `pytest` 통과
3. `git commit -m "phase 6X: <요약>"` (사용자 요청 시)
4. 아래 진행 로그 한 줄 추가

---

# 진행 로그

- **Phase 6 스펙 작성** (2026-05-25) — 인증·보안 제외, 9 서브페이즈(6A~6I) 계획 수립. baseline 133 tests.
- **Phase 6A 완료** (2026-05-25) — `pyproject.toml`에 `playwright` optional extra 및 dev extra 포함. `README.md` 추가. pytest 129 passed / 4 pre-existing failures.
- **Phase 6B 완료** (2026-05-25) — `mark_page_failed()` 추가, pipeline bg handler 3곳 연동. `_rebuild_context` silent pass → warning+log emit. `tests/test_pipeline_bg_failure.py` 신규 (6 tests) + engine warning test.
- **Phase 6C 완료** (2026-05-25) — `asyncio.Semaphore`로 페이지 파이프라인 동시 실행 제한. lifespan에서 `init_page_semaphore`. default `max_parallel_pages=1`. `tests/test_parallel_limit.py` 신규.
- **Phase 6D 완료** (2026-05-25) — `Settings.project_root` 자동 탐지, `claude_path`/`mcp_python_path` 기본값. registry/project/services 경로 이식성. `tests/test_config.py`.
- **Phase 6E 완료** (2026-05-25) — GitHub Actions workflow, conftest fixtures, e2e/integration test patch·skip. `test_api` flaky fix.
- **Phase 6F 완료** (2026-05-25) — 루트·orchestrator `.env.example` 동기화.
- **Phase 6G 완료** (2026-05-25) — `cache_creation_tokens` migration, `enforce_project_budget` gate, state machine `queued→blocked`.
- **Phase 6H 완료** (2026-05-25) — `create_sqlalchemy_engine` WAL 통합, `session.py` re-export.
- **Phase 6I 완료** (2026-05-25) — `StepContext.workspace_root`, engine worktree ensure + `GitManager.commit_step`. registry step 4~8 workspace 경로. `USE_WORKTREE` (default false). `tests/test_worktree_pipeline.py`.
