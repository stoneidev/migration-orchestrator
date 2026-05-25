# Silicon2 Migration Orchestrator — System Design

## 1. Overview

PHP 레거시 (Gnuboard5 e-commerce admin, 1,099 pages)를 React (Next.js 15) + Spring Boot (Java 21)로 자동 마이그레이션하는 AI 파이프라인.

**Pattern**: Orchestrator-Worker (Anthropic Building Effective Agents, 2024.12)

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard (Next.js)                    │
│              http://localhost:3000                        │
└──────────────────────┬──────────────────────────────────┘
                       │ WebSocket + REST
┌──────────────────────▼──────────────────────────────────┐
│              Orchestrator (FastAPI + SQLite)              │
│              http://localhost:8000                        │
│  ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌─────────────┐ │
│  │ Engine  │ │State Mgr │ │Cost Trk │ │  Event Bus  │ │
│  └────┬────┘ └──────────┘ └─────────┘ └─────────────┘ │
└───────┼─────────────────────────────────────────────────┘
        │ Hub-and-Spoke (no worker-to-worker communication)
   ┌────┼────────────────────────────────┐
   │    ├─→ Claude CLI (Code Generation)  │
   │    ├─→ MCP Server (PHP AST Analysis) │
   │    ├─→ Playwright (Screen Capture)   │
   │    └─→ Bedrock (LLM Analysis/Haiku)  │
   └──────────────────────────────────────┘
```

---

## 2. Monorepo Structure

```
silicon2-migration/
├── apps/
│   ├── orchestrator/         # Python FastAPI — Pipeline Engine
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── pipeline/     # Engine + State Machine + Steps
│   │   │   ├── workers/      # Claude CLI, MCP, Playwright, Bedrock
│   │   │   ├── api/          # REST + WebSocket routes
│   │   │   ├── db/           # SQLAlchemy models + Alembic
│   │   │   └── git/          # Auto-commit manager
│   │   └── data/orchestrator.db
│   │
│   ├── frontend/             # Generated Next.js 15 React
│   │   └── src/app/admin/    # Page-per-directory
│   │
│   └── backend/              # Generated Spring Boot 3.4
│       └── src/main/java/com/silicon2/admin/
│
├── tools/dashboard/          # Management UI (Next.js)
├── screenshots/              # Mobile captures (430×932)
├── docs/                     # This documentation
└── .env                      # Configuration (gitignored)
```

---

## 3. 9-Step Pipeline

| # | Step | Worker | Model | Duration | Cost |
|---|------|--------|-------|----------|------|
| 1 | spec_load | File I/O | — | <1s | $0 |
| 2 | spec_verify | MCP | — | <1s | $0 |
| 3 | api_contract | Bedrock | Haiku | ~25s | $0.07 |
| 4 | react_generation | Claude CLI | Sonnet | ~120s | $0.20 |
| 5 | java_generation | Claude CLI | Sonnet | ~180s | $0.60 |
| 6 | java_test | CLI + Gradle | Sonnet | ~90s | $0~0.30 |
| 7 | integration | Claude CLI | Sonnet | ~100s | $0.35 |
| 8 | equivalence_check | Static | — | <1s | $0 |
| 9 | complete | DB update | — | <1s | $0 |

**Total per page**: $1.5 ~ $2.5, 8~13 minutes

### Step 1: Spec Load
- `{specs_dir}/{page_id}.aispec.json` 파일 로드
- Spec 구조: meta, source, operations, business_rules, data_layer, test_scenarios

### Step 2: Spec Verify
- MCP `php_detect_gaps()` 호출
- Source path 대비 spec 완전성 검증
- Draft status면 timeout 30초 후 skip

### Step 3: API Contract
- Bedrock Haiku (최소 비용)
- Spec operations → OpenAPI 3.1 YAML 변환
- Context에 api_contract 저장

### Step 4: React Generation
- 원본 모바일 스크린샷 기반 UI 복제
- Claude CLI (Sonnet, max_turns=15)
- Output: page.tsx, types.ts, mock-data.ts, components/
- Visual Gate (optional): SSIM >= 0.85

### Step 5: Java Generation
- Hexagonal Architecture (DDD)
- Claude CLI (Sonnet, max_turns=30)
- Layer: Domain → Repository → UseCase → Controller → Persistence
- `./gradlew compileJava` 검증

### Step 6: Java Test
- `./gradlew test` 실행
- 실패 시 Claude CLI로 자동 수정 (fix → test 루프, 최대 3회)
- Prompt hints: @DataJpaTest 충돌 해결, 파일명/클래스명 매칭

### Step 7: Integration
- Backend 기동 (H2, nomysql profile)
- **curl 응답의 실제 JSON 구조** 확인 후 Frontend 매핑
- API 호출 + mock fallback (AbortSignal.timeout 3000ms)
- 검색/필터/페이징 동작 구현 + 결과 렌더링 JSX 필수
- DataInitializer에 고유 bean name 사용

### Step 8: Equivalence Check
- Backend `*Controller.java` 파일에서 @*Mapping 파싱
- Spec operations과 대조
- Route fuzzy matching (/v1 prefix 무시, keyword matching)
- 모든 operation 구현 확인

### Step 9: Complete
- Page status → COMPLETE
- completed_at 타임스탬프 기록

---

## 4. Workers

### Claude CLI Worker
```
claude --print --verbose --output-format stream-json
       --model sonnet --max-turns 15
       --allowedTools Write,Edit,Bash,Read
```
- Subprocess with stdin/stdout streaming
- Watchdog thread: SIGTERM after deadline
- Stream-json 파싱 → WebSocket live events (cli:text, cli:tool_use)
- Cost/token 추출 from result event

### MCP Worker (php-analyzer)
- 12 tools: php_find_entry_points, php_get_file_detail, php_trace_entry, etc.
- Fresh connection per-use (background task 호환성)
- Python MCP SDK (stdio_client)
- PHP 프로젝트 AST 분석 (regex-based, NetworkX 콜그래프)

### Playwright Worker
- All captures: Mobile UA (iPhone 17) + 430×932 viewport
- Login → Navigate → Screenshot + DOM extraction
- capture_for_spec(): headings, buttons, title 추출
- capture_react(): Generated React 페이지 캡처

### Bedrock Analysis Worker
- AWS Bedrock API (us-east-1)
- Models: Haiku ($0.001/1K in) / Sonnet ($0.003) / Opus ($0.015)
- Used for: API contract gen, LLM file resolution, spec verify
- 4-class cost tracking: input, output, cache_write, cache_read

---

## 5. Harness Engineering

### Spec Generation (New Page Workflow)

```
1. URL 입력 (Dashboard /new-page)
2. Playwright: 모바일 로그인 + 페이지 캡처 + DOM 추출
3. MCP: PHP 소스 파일 탐색 → 분석 (SQL, 함수, 실행흐름)
4. Claude CLI: 분석 데이터 + 스크린샷 → aispec.json 생성
5. Pipeline 자동 시작
```

### PHP File Resolution (LLM-based)
URL에서 실제 PHP 소스 파일 매핑:
1. MCP `php_get_file_detail(guessed_path)` 시도
2. 실패 → MCP `php_find_entry_points()` 전체 목록 가져옴
3. URL 키워드 pre-filter (예: "settings" → 1건 매칭)
4. 1건이면 자동 선택, 여러 건이면 LLM(Haiku) 선택
5. **Rule-based가 아닌 LLM으로 유연하게** (mp_settings → account_settings 등)

### Spec Prompt Design
- "소스에 없는 operation을 만들지 마라" 강제
- 실제 SQL 테이블명/쿼리 포함 (MCP trace 결과)
- Read-only 페이지는 GET operation만
- source.path에 resolved PHP 경로 기록

### Integration Prompt Design
- Backend curl 응답의 **실제 JSON 필드**로 매핑 강제
- DataInitializer: 고유 @Component bean name
- 검색 결과 렌더링 JSX 포함 필수 (로딩, 빈결과, 카드)
- Mock fallback 패턴 (try/catch + AbortSignal.timeout)

---

## 6. State Machine

### Page States
```
QUEUED ──→ RUNNING ──→ COMPLETE
              │              │
              ├──→ BLOCKED   │ (retry allowed)
              ├──→ FAILED    │ (retry allowed)
              └──→ REVIEW    │
                             ↓
              COMPLETE ──→ RUNNING (re-run allowed)
```

### Step States
```
RUNNING ──→ PASSED
        ├──→ RETRYING (auto-retry)
        └──→ BLOCKED (max retries)
```

### Retry Escalation (3-Tier)
| Tier | Trigger | Action |
|------|---------|--------|
| 1 | Step failure | Same model, error context, silent retry (max 3) |
| 2 | Repeated failure | Model upgrade, context expansion |
| 3 | All retries exhausted | BLOCKED → Human review queue |

---

## 7. Real-Time Dashboard

### WebSocket Events
| Event | Data | Trigger |
|-------|------|---------|
| pipeline:step_started | page_id, step, step_name | Step 시작 |
| pipeline:step_completed | page_id, step, cost, duration_ms | Step 완료 |
| pipeline:step_failed | page_id, step, error | Step 실패 |
| cli:tool_use | tool, input | Claude CLI 도구 사용 |
| cli:text | text | Claude CLI 텍스트 출력 |
| page_state | page_id, status | 상태 변경 |
| spec_gen:* | session_id, step | Spec 생성 이벤트 |

### Dashboard Status Accuracy
- Step 시작 시 "running" execution을 DB에 즉시 commit
- API 조회 시 active execution 기반으로 정확한 상태 표시
- `queued` = page running이지만 해당 step 미시작
- 매 step 완료 후 `session.commit()` (이전: 전체 완료 후 1회)

---

## 8. Cost Model & Optimization

### Token Pricing (per 1K tokens)
| Model | Input | Output | Cache Write | Cache Read |
|-------|-------|--------|-------------|------------|
| Haiku | $0.001 | $0.005 | $0.00125 | $0.0001 |
| Sonnet | $0.003 | $0.015 | $0.00375 | $0.0003 |
| Opus | $0.015 | $0.075 | $0.01875 | $0.0015 |

### Optimization Strategies
1. **Model Tiering**: Haiku for deterministic (Step 3), Sonnet for creative (Steps 4-7)
2. **Prompt Caching**: System prompt + conventions cached → 90% input reduction
3. **Progressive Context**: 최소 context로 시작, 실패 시에만 확장
4. **Budget Enforcement**: per-page + project-level limit

### Actual Costs (measured)
| Page | Steps | Total | Time |
|------|-------|-------|------|
| shop.mp_profile | 9/9 passed | $2.21 | 13min |
| mypage.wallet | 9/9 passed | $1.77 | 10min |
| shop.mp_settings | 9/9 passed | ~$2.00 | 12min |

---

## 9. Generated Code Patterns

### Frontend (React/Next.js)
```typescript
// page.tsx pattern
'use client';
import { useState, useEffect } from 'react';
import { fetchData } from './api';
import { mockData } from './mock-data';

export default function Page() {
  const [data, setData] = useState(mockData);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData().then(setData).finally(() => setLoading(false));
  }, []);

  // Mobile layout: max-w-[430px] mx-auto
}
```

```typescript
// api.ts pattern
export async function fetchData() {
  try {
    const res = await fetch('http://localhost:8080/api/...', {
      signal: AbortSignal.timeout(3000),
    });
    const json = await res.json();
    return mapResponseToFrontend(json.data || json);
  } catch {
    return mockData; // Fallback
  }
}
```

### Backend (Spring Boot)
```java
// Hexagonal Architecture
@RestController
@RequestMapping("/v1/{module}/{page}")
@RequiredArgsConstructor
@CrossOrigin(origins = {"http://localhost:3001"})
public class PageController {
    private final GetDataUseCase useCase;

    @GetMapping
    public ResponseEntity<ApiResponse> getData(@RequestParam ...) {
        return ResponseEntity.ok(ApiResponse.success(useCase.execute(...)));
    }
}
```

---

## 10. Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| SPECS_DIR | Yes | — | aispec.json 디렉토리 |
| PHP_PROJECT_ROOT | Yes | — | PHP 소스 루트 |
| MCP_SERVER_PATH | Yes | — | php-analyzer 경로 |
| MCP_PYTHON_PATH | No | python3 | MCP Python 경로 |
| SCREENSHOTS_DIR | No | ./screenshots | 캡처 저장 |
| PW_BASE_URL | No | stylekorean.com | 대상 사이트 |
| PW_ADMIN_ID | No | — | 로그인 ID |
| PW_ADMIN_PW | No | — | 로그인 PW |
| AWS_REGION | No | us-east-1 | Bedrock 리전 |
| MAX_PARALLEL_PAGES | No | 1 | 동시 실행 수 |
| MAX_RETRY_ATTEMPTS | No | 3 | 재시도 횟수 |
| STRICT_VISUAL_GATE | No | true | 시각 검증 strict |
| STRICT_JAVA_TEST | No | true | 테스트 검증 strict |
| PROJECT_BUDGET | No | 20000 | 예산 (USD) |
| USE_WORKTREE | No | false | Git worktree |
| DATABASE_URL | No | sqlite:///./data/orchestrator.db | DB |

---

## 11. Running the System

```bash
# 1. Orchestrator
cd apps/orchestrator
.venv/bin/uvicorn src.main:app --port 8000

# 2. Dashboard
cd tools/dashboard
npm run dev  # port 3000

# 3. Frontend (generated)
cd apps/frontend
npx next dev --port 3001

# 4. Backend (generated, H2 mode)
cd apps/backend
./gradlew bootRun --args='--spring.profiles.active=nomysql'  # port 8080
```

### New Page Migration
1. Dashboard `http://localhost:3000/new-page` → URL 입력
2. Step 1-2-3 (Capture → MCP → Spec Gen) 자동 진행
3. Pipeline 자동 시작 또는 수동 "Run All"
4. 완료 후 `http://localhost:3001/admin/{module}/{page}` 에서 확인
