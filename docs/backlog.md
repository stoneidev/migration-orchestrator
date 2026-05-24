# Dashboard & Implementation Backlog

> Orchestrator·Dashboard·Harness 구현 우선순위 백로그.  
> 이론적 배경: [theoretical-foundation.md](./theoretical-foundation.md) · 설계: [architecture.md](./architecture.md)

**우선순위**: P0 (PoC 차단) · P1 (Alpha) · P2 (Beta/Production)

**상태**: `[ ]` 미착수 · `[~]` 진행 중 · `[x]` 완료

---

## 1. Dashboard (tools/dashboard) — UI 백로그

Dashboard는 AI-DLC의 **Human Oversight 실행면**이자, Harness의 **관측(Observability) 콘솔**이다.

### 1.1 P0 — PoC 필수 화면

| ID | Task | AI-DLC / Harness 연계 | 상태 |
|----|------|----------------------|------|
| D-001 | Next.js 프로젝트 스캐폴딩 (`tools/dashboard`, Pretendard, App Router) | Operations phase UI | `[ ]` |
| D-002 | **Pipeline Overview** — 전체 page migration_status, current_step 집계 | Traceability dashboard | `[ ]` |
| D-003 | **Page List** — 필터(module, complexity, status), 정렬, 페이지네이션 | Unit of Work 목록 | `[ ]` |
| D-004 | **Page Detail** — 9-step 타임라인, step_executions 이력 | Bolt progress view | `[ ]` |
| D-005 | **Run Pipeline** — single/batch page 선택 → `POST /api/pipeline/run` | AI execution trigger | `[ ]` |
| D-006 | **Live Status** — WebSocket `pipeline:step_*` 이벤트 수신 | Real-time Mob Construction | `[ ]` |
| D-007 | **Health / Connection** — Orchestrator `/api/health` 상태 표시 | Ops monitoring | `[ ]` |

### 1.2 P1 — Alpha (Human-in-the-Loop)

| ID | Task | AI-DLC / Harness 연계 | 상태 |
|----|------|----------------------|------|
| D-010 | **Review Queue** — `REVIEW_NEEDED` page 목록, approve/refine/skip | Human checkpoint UI | `[ ]` |
| D-011 | **Refinement Prompt** — 사용자 수정 요청 입력 → step 재실행 | Mob Elaboration feedback | `[ ]` |
| D-012 | **Artifact Viewer** — spec, openapi.yaml, 생성 파일 목록/미리보기 | Artifact traceability | `[ ]` |
| D-013 | **Step Log Panel** — error_message, attempt_number, duration | Feedback loop visibility | `[ ]` |
| D-014 | **Screenshot Compare** — original vs react_v{N} side-by-side | Visual diff harness UI | `[ ]` |
| D-015 | **Blocked Pages** — Tier 3 escalation 목록, retry/rollback 액션 | Human escalation queue | `[ ]` |

### 1.3 P1 — Alpha (Observability / Cost)

| ID | Task | AI-DLC / Harness 연계 | 상태 |
|----|------|----------------------|------|
| D-020 | **Cost Summary** — total spend, by-model, by-step 차트 | AI-DLC velocity vs cost | `[ ]` |
| D-021 | **Token Metrics** — input/output, cache hit rate per page | Harness efficiency KPI | `[ ]` |
| D-022 | **Budget Gauge** — PROJECT_BUDGET 대비 사용률, 경고 | Budget governor UI | `[ ]` |
| D-023 | **Auto-fix Badge** — Tier 1 silent correction occurred 표시 | Harness self-correction UX | `[ ]` |

### 1.4 P2 — Beta (Pattern & Settings)

| ID | Task | AI-DLC / Harness 연계 | 상태 |
|----|------|----------------------|------|
| D-030 | **Pattern Library CRUD** — php→java/react 매핑 목록, confidence | Learning system UI | `[ ]` |
| D-031 | **Settings Panel** — MAX_PARALLEL, model tier, visual diff threshold | Workflow scaffold config | `[ ]` |
| D-032 | **Module Batch Run** — module 단위 일괄 실행 (e.g. `shop_admin.*`) | Adaptive batch depth | `[ ]` |
| D-033 | **Git Branch Link** — `migration/{page_id}` branch, commit 이력 | Operations traceability | `[ ]` |
| D-034 | **Entity Registry** — 공유 Entity 정의, 충돌 경고 | Construction coordination | `[ ]` |

### 1.5 Dashboard 기술 Task

| ID | Task | 상태 |
|----|------|------|
| D-T01 | API client (`lib/api.ts`) — 공통 `{ success, data, error, meta }` 래퍼 | `[ ]` |
| D-T02 | WebSocket hook (`hooks/usePipelineEvents.ts`) | `[ ]` |
| D-T03 | 공통 타입 (`types/page.ts`, `types/pipeline.ts`) | `[ ]` |
| D-T04 | Step 상태 색상/아이콘 매핑 (queued/running/passed/blocked/review) | `[ ]` |
| D-T05 | 다크 모드 + 한글 타이포그래피 (Pretendard) | `[ ]` |
| D-T06 | E2E: Playwright dashboard smoke test | `[ ]` |

---

## 2. Orchestrator — Backend 백로그

### 2.1 P0 — PoC E2E (현재 ~35%)

| ID | Task | SDLC Step | 상태 |
|----|------|-----------|------|
| O-001 | Step 1–5 `BaseStep` registry + Engine 연결 | 1–5 | `[x]` |
| O-002 | `POST /pipeline/run` BackgroundTask → `engine.run()` | — | `[x]` |
| O-003 | `GET /pipeline/status` — 실행 중 task 목록 | — | `[x]` |
| O-004 | Step 2: MCP에 `source.path` 인자 전달 | Analysis | `[ ]` |
| O-005 | Step 3: OpenAPI schema validator 통합 | Design | `[ ]` |
| O-006 | Step 4: WorktreeManager + ESLint gate | Implementation FE | `[ ]` |
| O-007 | Step 5: WorktreeManager + `gradle compileJava` gate | Implementation BE | `[ ]` |
| O-008 | Artifact DB 저장 (step 완료 시 `artifacts` 테이블) | Traceability | `[ ]` |
| O-009 | Page seed/import — 707 spec 메타 → `pages` 테이블 | Inception | `[ ]` |

### 2.2 P1 — Step 6–9 (Construction 완성)

| ID | Task | SDLC Step | 상태 |
|----|------|-----------|------|
| O-010 | Step 6: Java test generation + `gradle test` | Testing | `[ ]` |
| O-011 | Step 7: Contract compliance (FE type + BE response) | Integration | `[ ]` |
| O-012 | Step 8: Functional equivalence (MCP trace vs Java) | Verification | `[ ]` |
| O-013 | Step 9: Pattern extraction + Git final commit | Learning/Ops | `[ ]` |
| O-014 | `state_machine.py` ↔ Engine 통합 (REVIEW_NEEDED flow) | AI-DLC checkpoint | `[ ]` |

### 2.3 P1 — API 완성 (architecture §11)

| ID | Task | 상태 |
|----|------|------|
| O-020 | `POST /pipeline/pause`, `/resume` | `[ ]` |
| O-021 | `DELETE /pipeline/{page_id}` — cancel | `[ ]` |
| O-022 | `GET /pages/{id}/artifacts`, `/logs` | `[ ]` |
| O-023 | `POST /pages/{id}/retry`, `/skip`, `/rollback` | `[ ]` |
| O-024 | Review API — `/api/reviews/*` (approve/refine/skip) | `[ ]` |
| O-025 | Cost API — `/api/cost/summary`, `/by-model`, `/by-step` | `[ ]` |
| O-026 | Patterns API — CRUD `/api/patterns` | `[ ]` |
| O-027 | Settings API — GET/PUT `/api/settings` | `[ ]` |
| O-028 | WebSocket `/ws` — event broadcasting | `[ ]` |

### 2.4 P2 — Concurrency & Resilience

| ID | Task | 상태 |
|----|------|------|
| O-030 | `scheduler.py` — MAX_PARALLEL_PAGES, entity lock | `[ ]` |
| O-031 | `retry.py` — 3-Tier escalation (Silent/Notify/Human) | `[ ]` |
| O-032 | Budget governor — PROJECT_BUDGET 초과 시 pause | `[ ]` |
| O-033 | Phase C: React/Java parallel (별도 worktree) | `[ ]` |
| O-034 | Alembic migrations (SQLite → Aurora path) | `[ ]` |

---

## 3. Harness Engineering — 검증 계층 백로그

| ID | Task | Harness Layer | 상태 |
|----|------|---------------|------|
| H-001 | `output/validator.py` — TSX eslint, Java compile, YAML openapi | Verification Gates | `[ ]` |
| H-002 | `output/parser.py` — markdown code block extraction | Output Harness | `[ ]` |
| H-003 | `output/fixer.py` — import auto-add, prettier/spotless | Auto-fix | `[ ]` |
| H-004 | Playwright screenshot capture (`workers/playwright.py`) | Visual harness | `[ ]` |
| H-005 | Visual diff ≤ 5% gate | Visual harness | `[ ]` |
| H-006 | OpenAPI ↔ React TanStack Query type check | Contract harness | `[ ]` |
| H-007 | OpenAPI ↔ Java Controller response check | Contract harness | `[ ]` |
| H-008 | Generated file header comment (source, step, model, timestamp) | Traceability | `[ ]` |
| H-009 | Pre-commit hook template (lint + compile before merge) | Mechanical constraint | `[ ]` |

---

## 4. Context & Learning — AI-DLC Scaffold 백로그

| ID | Task | AI-DLC Phase | 상태 |
|----|------|--------------|------|
| C-001 | `context/assembler.py` — 3-Layer context 조립 | Construction | `[ ]` |
| C-002 | `context/cache.py` — Bedrock prompt caching | Cost optimization | `[ ]` |
| C-003 | `context/compressor.py` — artifact 요약 (Layer 3) | Adaptive depth | `[ ]` |
| C-004 | `learning/pattern_store.py` — Pattern CRUD | Operations learning | `[ ]` |
| C-005 | `learning/extractor.py` — Step 9 Haiku pattern extraction | Operations learning | `[ ]` |
| C-006 | `learning/preference.py` — user refinement → project preference | Human feedback | `[ ]` |
| C-007 | Few-shot selector — 유사 completed page algorithm | Adaptive depth | `[ ]` |
| C-008 | Specialist prompts — `prompts/react_specialist.md`, `java_specialist.md` | Workflow scaffolds | `[ ]` |

---

## 5. Monorepo & Infrastructure

| ID | Task | 상태 |
|----|------|------|
| I-001 | `apps/frontend` Next.js scaffold (FSD, shadcn, TanStack Query) | `[ ]` |
| I-002 | `apps/backend` Spring Boot 3.4 scaffold (DDD/Hexagonal, Flyway) | `[ ]` |
| I-003 | `docker-compose.yml` — MySQL + Orchestrator | `[ ]` |
| I-004 | `git/manager.py` — branch 생성, step별 commit | `[ ]` |
| I-005 | CI: orchestrator pytest on push | `[ ]` |
| I-006 | CI: path-agnostic test fixtures (Settings env) | `[ ]` |
| I-007 | `entities`, `patterns` DB models + migrations | `[ ]` |
| I-008 | AWS ECS Fargate deployment path (PoC 이후) | `[ ]` |

---

## 6. AI-DLC 방법론 정렬 Task

AWS [aidlc-workflows](https://github.com/awslabs/aidlc-workflows)와의 명시적 정렬:

| ID | Task | AI-DLC Stage | 상태 |
|----|------|--------------|------|
| A-001 | `aidlc-docs/` — page bolt별 artifact trace 디렉토리 (선택) | Persistent context | `[ ]` |
| A-002 | Orchestrator steering rules → `CLAUDE.md` / Cursor rules 연동 | Workflow scaffolds | `[ ]` |
| A-003 | Complexity-aware depth — low page는 Step 6–8 skip 옵션 | Adaptive depth | `[ ]` |
| A-004 | Review checkpoint definition per step (blocking vs info) | Human oversight | `[ ]` |
| A-005 | Unit of Work = 1 page 문서화 + Dashboard 표기 | Terminology alignment | `[ ]` |

---

## 7. PoC 완료 체크리스트 (`bbs.alert_close`)

architecture.md §15.2 기준:

| # | 성공 기준 | 관련 Task | 상태 |
|---|----------|-----------|------|
| 1 | 9단계 파이프라인 E2E 실행 | O-010~O-013 | `[ ]` |
| 2 | React .tsx 생성 + TS 문법 정상 | O-006, H-001 | `[ ]` |
| 3 | Java 생성 + compileJava | O-007, H-001 | `[ ]` |
| 4 | JUnit 생성 + gradle test | O-010 | `[ ]` |
| 5 | Git branch + step별 commit | I-004 | `[ ]` |
| 6 | Dashboard 실시간 진행 상태 | D-001~D-006 | `[ ]` |
| 7 | WebSocket step 이벤트 | O-028, D-T02 | `[ ]` |
| 8 | Cost/token 추적 | D-020~D-021, O-025 | `[ ]` |
| 9 | Playwright screenshot | H-004 | `[ ]` |

---

## 8. 권장 구현 순서 (Sprint 제안)

### Sprint 1 — PoC Pipeline (1–2주)
O-004 → O-005 → O-006 → O-007 → O-008 → H-001

### Sprint 2 — Dashboard MVP (1–2주)
D-001 → D-T01~T03 → D-002~D-007 → O-028 (basic)

### Sprint 3 — Harness & Review (2주)
O-010~O-014 → D-010~D-015 → H-004~H-005

### Sprint 4 — Scale (2–3주)
O-030~O-033 → C-001~C-007 → D-020~D-034 → I-001~I-004

---

*Last updated: 2026-05-24*
