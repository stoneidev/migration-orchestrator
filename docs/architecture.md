# Silicon2 마이그레이션 오케스트레이터 — 아키텍처 및 구현 명세

> **관련 문서**: [이론적 기반 (SDLC · AI-DLC · Harness Engineering)](./theoretical-foundation.md) · [구현 백로그](./backlog.md) · [문서 목록](./README.md)

---

## 1. 배경 및 동기

### 1.1 문제 정의

StyleKorean의 관리자 시스템은 Gnuboard5 기반 PHP로 구축된 레거시 시스템이다. `sk-main-php/adm` 디렉토리에 1,099개의 PHP 파일이 존재하며, 이를 현대적 기술 스택(React + Spring Boot)으로 마이그레이션해야 한다.

전통적인 수동 마이그레이션은 다음 문제를 갖는다:

- **규모**: 1,099 pages × 평균 2주/page = 약 42년의 인력 소요 (단순 산술)
- **일관성 부재**: 수십 명의 개발자가 참여하면 코딩 스타일, 아키텍처 해석이 발산
- **지식 손실**: 레거시 코드의 암묵적 비즈니스 규칙이 마이그레이션 과정에서 유실
- **검증 부재**: "동일 기능 보장"에 대한 체계적 검증 방법 없음

### 1.2 왜 AI 기반 자동화인가

2024년 이후 LLM의 코드 생성 능력이 production-grade 수준에 도달했다. 특히:

- **Anthropic "Building Effective Agents" (2024.12)**: LLM을 워크플로우로 구조화하면 단일 호출 대비 품질이 극적으로 향상됨을 입증
- **MetaGPT (arXiv:2308.00352)**: 구조화된 Artifact + 실행 기반 검증이 자연어 체이닝 대비 executability 2.25→3.75로 개선됨을 정량 증명
- **Andrew Ng의 Multi-Agent 패턴**: "한 번에 하나에 집중"시키면 LLM 성능이 향상된다는 원리 확인

그러나 단순히 LLM에게 "이 PHP를 Java로 변환해"라고 하면 실패한다:
- Cascading hallucination: 한 단계의 오류가 다음 단계로 증폭
- Context 부족: 1,099개 page의 상호 의존성을 하나의 프롬프트에 담을 수 없음
- 검증 불가: 생성된 코드가 원본과 기능적으로 동등한지 확인할 방법 없음

**해법**: Orchestrator-Worker 패턴을 적용한 구조화된 파이프라인 + 단계별 검증 게이트.

### 1.3 기존 자산 활용

이 프로젝트의 핵심 강점은 이미 확보된 자산이다:

| 자산 | 내용 | 활용 |
|------|------|------|
| **aispec.json** (707개) | PHP 코드 분석에서 추출된 상세 사양서 | Ground truth — LLM이 "무엇을 만들지" 판단하지 않아도 됨 |
| **review score** (평균 0.896) | 7개 품질 차원의 점수 | Pipeline-ready 판단 기준 |
| **php-analyzer MCP** (12 tools) | Call graph, SQL, entry points 등 | 정적 분석 데이터 정확히 제공 |
| **관리자 메뉴 구조** (16 섹션) | 전체 page 목록과 계층 | 마이그레이션 순서 결정 |

---

## 2. 이론적 기반: Orchestrator-Worker 패턴

### 2.1 패턴의 정의 (Anthropic)

> "A central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results. The key difference from parallelization: subtasks aren't pre-defined but determined by the orchestrator based on the specific input."
> — Anthropic, "Building Effective Agents", 2024.12

Orchestrator-Worker 패턴은 다음으로 구성된다:

```
[입력] → [Orchestrator: 작업 분해 및 판단] → [Worker A, B, C: 전문 실행] → [Orchestrator: 결과 통합] → [출력]
```

### 2.2 패턴의 핵심 원리

#### 원리 1: 관심사 분리 (Separation of Concerns)

Orchestrator는 "무엇을 해야 하는가"를 판단하고, Worker는 "어떻게 하는가"를 실행한다. 이 분리가 가져오는 이점:

- **Orchestrator**: 전체 파이프라인 상태를 파악하고 동적으로 결정. 더 강력한 모델(Opus) 사용.
- **Worker**: 좁은 범위의 전문 작업에 집중. 비용 효율적인 모델(Sonnet/Haiku) 사용.

Andrew Ng이 설명한 "인지적 집중 효과"와 정확히 일치한다: LLM에게 "코드도 생성하고 테스트도 만들고 문서도 써"라고 하면 산만해지지만, 각각 전문 Worker에게 하나씩 맡기면 품질이 올라간다.

#### 원리 2: 구조화된 통신 (Structured Communication)

MetaGPT가 증명한 핵심: Worker 간 통신을 **자연어가 아닌 구조화된 Artifact**로 수행하면 hallucination 전파가 차단된다.

| 기존 방식 (자연어 체이닝) | 본 시스템 (구조화 통신) |
|--------------------------|----------------------|
| "이 PHP를 보고 Java를 만들어" | Spec(JSON) + API Contract(OpenAPI) → Java 생성 |
| 문맥 손실, 해석 발산 | Schema-validated, 형식 고정 |
| MetaGPT 기준 executability 2.25 | MetaGPT 기준 executability 3.75 |

본 시스템에서 Step 간 전달되는 Artifact:
- Step 1→2: `aispec.json` (구조화된 사양서)
- Step 2→3: Verified spec + gap report
- Step 3→4,5: `openapi.yaml` (API Contract)
- Step 4,5→6,7: 생성된 코드 파일

모두 schema-validated JSON/YAML이며, 자연어 설명이 아니다.

#### 원리 3: 검증 게이트 (Verification Gates)

MetaGPT의 Executable Feedback Mechanism에서 영감:
- 코드를 생성한 후 **실제로 실행**하여 검증
- 실패 시 에러 피드백과 함께 재생성 (최대 3회)
- 이것만으로 +4.2~5.4%p 성능 향상

본 시스템의 검증 게이트:
| Step | 검증 방법 | 자동화 가능 여부 |
|------|----------|----------------|
| 2 (Spec Verify) | `php_detect_gaps()` — 정적 분석 비교 | 완전 자동 |
| 3 (API Contract) | OpenAPI schema validator | 완전 자동 |
| 4 (React) | TSX syntax parse + ESLint + Visual diff | 완전 자동 |
| 5 (Java) | `gradle compileJava` | 완전 자동 |
| 6 (Test) | `gradle test` 실행 결과 | 완전 자동 |

#### 원리 4: Adaptive Behavior (동적 적응)

고정된 Parallelization과 Orchestrator-Worker의 결정적 차이: **입력에 따라 전략이 달라진다.**

본 시스템에서의 적용:
- **단순 page** (1 operation, 6 BRs): Step 2 자동 통과, React/Java 생성도 한 번에 성공 가능
- **복잡 page** (12 operations, 36 BRs): Step 4에서 컴포넌트별 분할 생성, Opus로 업그레이드, 더 많은 context 제공
- **실패 시**: Progressive context loading (Layer 2 → Layer 3 확장), 모델 업그레이드 (Sonnet → Opus)

이것이 "하드코딩된 워크플로우"가 아니라 "Orchestrator가 판단하는 시스템"인 이유이다.

### 2.3 왜 순수 Agent가 아니라 Hybrid인가

Anthropic이 정의한 스펙트럼에서 본 시스템의 위치:

```
Prompt Chaining → Routing → Parallelization → [본 시스템] → Autonomous Agent
(고정 순서)      (분류)     (고정 병렬)       (적응형 파이프라인)  (완전 자율)
```

순수 Autonomous Agent를 사용하지 않는 이유:
1. **예측 가능성**: 마이그레이션은 "정해진 단계"가 있는 작업. 완전 자율은 불필요하며 위험.
2. **디버깅**: 어떤 step에서 문제가 발생했는지 정확히 추적 가능해야 함.
3. **비용 제어**: Agent 루프는 무한 반복 위험. Pipeline은 step 수가 유한.
4. **Human-in-the-Loop**: 사용자가 특정 지점에서 개입할 수 있어야 함.

따라서 **"고정된 단계 구조 + 각 단계 내 적응적 실행"**이라는 하이브리드를 채택한다.

### 2.4 Self-Correction: 3-Tier Escalation 이론

MetaGPT의 "max 3 retries" 메커니즘을 확장한 모델:

```
실패 발생
    │
    ▼
[Tier 1: Silent Auto-retry]
  └─ 기계적 실패 (syntax, compile, schema)
  └─ 같은 모델, error feedback 추가
  └─ 사용자 모름
  └─ 80%의 실패가 여기서 해결됨
    │ 3회 실패
    ▼
[Tier 2: Notify + Upgrade]
  └─ 논리적 실패 (test fail, gap)
  └─ 모델 업그레이드 (Sonnet→Opus)
  └─ Context 확장 (Layer 3 추가)
  └─ 사용자에게 "자동 수정 중" 알림
    │ 3회 실패
    ▼
[Tier 3: Human Escalation]
  └─ 판단이 필요한 실패 (비즈니스 로직 모호, 설계 결정)
  └─ Review Queue에 등록
  └─ 해당 page BLOCKED, 다른 page 계속 진행
```

이 구조의 핵심: **모든 실패를 사용자에게 올리지 않는다.** 사용자는 "진짜 판단이 필요한 것"만 처리하면 된다.

### 2.5 학습 축적: Pattern Library 이론

단순히 707개 page를 독립적으로 처리하면, page 1에서 배운 것이 page 707에 전혀 반영되지 않는다.

**Compounding Improvement Principle:**
```
Page  1-10:  avg cost $0.85/page, auto-fix rate 60%
Page 11-50:  avg cost $0.55/page, auto-fix rate 78%
Page 51+:    avg cost $0.42/page, auto-fix rate 88%
```

이것이 가능한 이유:
1. **Few-shot 축적**: 완료된 page의 input→output 쌍이 이후 page의 프롬프트에 포함됨
2. **패턴 발견**: `sql_fetch()` → `Repository.findBy()` 같은 매핑이 반복 확인되면 confidence 상승
3. **사용자 선호도 학습**: "테이블 헤더 고정"을 한 번 요청하면 이후 모든 list page에 자동 적용
4. **Prompt caching**: 같은 step의 system prompt + conventions가 캐시되어 비용 절감

### 2.6 Token 최적화 이론

LLM 호출 비용은 `(input_tokens × input_price) + (output_tokens × output_price)`이다.

핵심 통찰:
- **Output이 Input보다 5배 비쌈** (Sonnet: $3 vs $15 per 1M tokens)
- **Input의 90%는 반복됨** (같은 step의 다른 page에서 system prompt, conventions 동일)

따라서 최적화 전략:
1. **Prompt Caching**: 반복되는 prefix를 캐시 → input 비용 90% 절감
2. **Progressive Loading**: 첫 시도는 최소 context, 실패할 때만 확장
3. **Incremental Generation**: 한 번에 전체 파일 대신 컴포넌트별 분할 생성 → output 30% 절감
4. **Diff-based Refinement**: 사용자 수정 시 전체 재생성 대신 변경분만 → output 80% 절감
5. **Tiered Model**: 단순 작업은 Haiku ($0.25/$1.25), 복잡한 것만 Opus ($15/$75)

---

## 3. 시스템 개요

### 3.1 목적

PHP(Gnuboard5) 기반 e-commerce admin 시스템(`sk-main-php/adm`, 1,099 pages)을 React(Next.js) + Spring Boot(Java 21)으로 마이그레이션하는 **자동화된 Orchestrator-Worker 파이프라인**.

### 3.2 설계 원칙

| 원칙 | 의미 | 적용 |
|------|------|------|
| **Spec-driven** | LLM이 "무엇을 만들지" 추측하지 않음 | 707개 aispec.json이 ground truth |
| **Structured Communication** | Worker 간 자연어 X, 구조화 Artifact O | JSON Spec, OpenAPI YAML, typed schema |
| **Verification Gates** | 모든 생성물을 실행 기반으로 검증 | compile, test, visual diff |
| **Self-correcting** | 기계적 실패는 자동 복구 | 3-tier escalation |
| **Learning** | 경험이 축적됨 | Pattern Library, few-shot, preferences |
| **Observable** | 모든 것이 추적됨 | 비용, 토큰, 시간, cache hit |

### 3.3 기술 결정 요약

| 컴포넌트 | 기술 | 선정 근거 |
|----------|------|----------|
| Orchestrator | Python + FastAPI | AI 생태계 (Bedrock SDK, MCP), async 네이티브, WebSocket 지원 |
| Dashboard | Next.js + Pretendard | 모노리포 통합, SSR, 프로페셔널 한글 타이포그래피 |
| LLM | AWS Bedrock (Claude Opus/Sonnet/Haiku) | 기존 인프라, Bearer token 인증 유지 |
| PHP 분석 | php-analyzer MCP (subprocess stdio) | 기존 자산 (12 tools, NetworkX graph) |
| 스크린샷 | Playwright | dev.stylekorean.com 캡처, 자동 로그인 |
| DB | SQLite → Aurora | 로컬 간편 시작, AWS 이관 용이 |
| React 출력 | Next.js + FSD + shadcn/ui + TanStack Query + Zustand | 2026 modern stack |
| Java 출력 | Spring Boot 3.4 + Java 21 + DDD/Hexagonal + Gradle | 최신 LTS, 클린 아키텍처 |
| Java DB | MySQL (Docker) + Flyway | 형상 관리 포함 |
| 모노리포 | Turborepo + pnpm | 빌드 캐시, workspace 관리 |
| 통신 | WebSocket + REST | 실시간 상태 업데이트 + CRUD 조작 |

### 3.4 Worker 아키텍처: 4종 분리 + Hub-and-Spoke 토폴로지

#### 왜 Choreography(직접 통신)가 아닌 Orchestration(중앙 제어)인가

Worker 간 직접 데이터를 주고받는 Choreography/Saga 패턴을 검토했으나, 다음 이유로 **Hub-and-Spoke Orchestration**을 선택했다:

| 관점 | Choreography (직접 통신) | Orchestration (중앙 제어) |
|------|--------------------------|--------------------------|
| 상태 관리 | 분산 (각 Worker가 보유) | 중앙 집중 (Orchestrator) |
| 실패 처리 | Worker가 스스로 판단 | Orchestrator가 tier 결정 |
| 예측 가능성 | 낮음 | 높음 |
| 디버깅 | 분산 로그 추적 어려움 | 단일 trace |
| 결합도 | Worker가 서로를 알아야 함 | Worker는 Orchestrator만 앎 |
| 비용 추적 | 분산, 합산 어려움 | 중앙에서 모든 호출 추적 |

Andrew Ng의 경고: "에이전트 간 자유 상호작용을 허용하면 출력 품질이 예측 불가능해진다."
→ 우리 시스템에서는 Worker가 서로를 모르고, Orchestrator가 모든 데이터 흐름을 중재한다.

실제로 Worker 간 직접 통신이 필요한 시나리오도 없다:
- React가 Java의 타입을 알아야 함? → API Contract(Step 3)가 이미 정의
- Java가 React의 호출 패턴을 참조? → API Contract가 이미 정의
- Integration 실패 시 책임 판단? → Orchestrator의 판단 영역

#### 4종 Worker 구조

```
┌───────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATOR                                   │
│                       (Pipeline Engine)                                 │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    Artifact Store                                  │ │
│  │                                                                   │ │
│  │  aispec.json → openapi.yaml → react/*.tsx → java/*.java → tests  │ │
│  │                                                                   │ │
│  │  모든 Worker의 산출물이 여기 저장됨.                               │ │
│  │  Worker는 서로를 모름. Orchestrator가 "이 artifact를 참조해"      │ │
│  │  라고 지시할 뿐.                                                  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
└────────┬──────────────┬──────────────┬──────────────┬────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Analysis    │ │    React     │ │    Java      │ │     MCP      │
│  Worker      │ │   Worker     │ │   Worker     │ │    Worker    │
│              │ │              │ │              │ │              │
│ 구현: Raw    │ │ 구현: Claude │ │ 구현: Claude │ │ 구현:        │
│ Bedrock API  │ │ Code CLI     │ │ Code CLI     │ │ subprocess   │
│              │ │ (headless)   │ │ (headless)   │ │ stdio        │
│              │ │              │ │              │ │              │
│ 실행 환경:   │ │ 실행 환경:   │ │ 실행 환경:   │ │ 실행 환경:   │
│ In-process   │ │ 격리된       │ │ 격리된       │ │ In-process   │
│ (async)      │ │ Git Worktree │ │ Git Worktree │ │              │
│              │ │              │ │              │ │              │
│ 담당 Step:   │ │ 담당 Step:   │ │ 담당 Step:   │ │ 담당 Step:   │
│ 2.Spec검증   │ │ 4.React생성  │ │ 5.Java개발   │ │ 모든 Step의  │
│ 3.API계약    │ │              │ │ 6.Java테스트 │ │ 보조 데이터  │
│ 7.통합테스트 │ │ 내장 기능:   │ │              │ │              │
│ 8.기능동등성 │ │ ✓ 파일 생성  │ │ 내장 기능:   │ │ 제공 데이터: │
│ 9.패턴추출   │ │ ✓ ESLint     │ │ ✓ 파일 생성  │ │ - Call graph │
│              │ │ ✓ Prettier   │ │ ✓ Compile    │ │ - SQL 추출   │
│ 모델:        │ │ ✓ Jest 실행  │ │ ✓ Test 실행  │ │ - Gap 감지   │
│ Haiku/Sonnet │ │ ✓ Self-fix   │ │ ✓ Self-fix   │ │ - Entry pts  │
│              │ │              │ │ ✓ BDD 작성   │ │ - JS API     │
│              │ │ 모델: Sonnet │ │              │ │              │
│              │ │ (→Opus)      │ │ 모델: Sonnet │ │              │
│              │ │              │ │ (→Opus)      │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

#### Worktree 격리 전략

React Worker와 Java Worker는 **격리된 Git Worktree**에서 작업한 후 merge한다:

```
silicon2-migration/                        ← main worktree (Orchestrator 실행)
├── .worktrees/
│   ├── react-{page_id}/                   ← React Worker 전용
│   │   └── apps/frontend/src/...         ← Claude CLI가 여기서 작업
│   └── java-{page_id}/                    ← Java Worker 전용
│       └── apps/backend/src/...          ← Claude CLI가 여기서 작업
```

실행 흐름:
1. Orchestrator: `git worktree add .worktrees/react-{page_id} -b wt/react/{page_id}`
2. React Worker (Claude CLI): worktree 내에서 파일 생성 + lint + test → self-correction
3. Orchestrator: 결과 확인 (compile pass, lint pass) → `migration/{page_id}` branch에 merge
4. Orchestrator: `git worktree remove .worktrees/react-{page_id}`

Java Worker도 동일. **React와 Java는 같은 page에서 병렬 실행 가능** (서로 다른 worktree).

#### Claude CLI Worker 설정

```python
REACT_WORKER_CONFIG = {
    "command": ["claude", "--headless", "--model", "sonnet",
                "--allowedTools", "Edit,Write,Bash,Read"],
    "cwd": ".worktrees/react-{page_id}/apps/frontend",
    "bash_allowed": ["npx", "eslint", "prettier", "jest", "next"],
    "max_turns": 15,
    "system_prompt": "prompts/react_specialist.md",
}

JAVA_WORKER_CONFIG = {
    "command": ["claude", "--headless", "--model", "sonnet",
                "--allowedTools", "Edit,Write,Bash,Read"],
    "cwd": ".worktrees/java-{page_id}/apps/backend",
    "bash_allowed": ["./gradlew", "gradle", "java"],
    "max_turns": 20,  # Java는 compile + test 루프가 더 길음
    "system_prompt": "prompts/java_specialist.md",
}
```

Claude CLI Worker의 장점: **Output Harness(파싱, 검증, 자동수정)를 직접 구현할 필요 없음.** Claude Code가 내부적으로 파일 생성 → 컴파일 → 에러 확인 → 수정 루프를 수행한다.

#### MetaGPT Shared Message Pool과의 대응

MetaGPT 논문의 핵심 혁신인 "Shared Message Pool + Pub/Sub"가 본 시스템에서 어떻게 구현되는지:

| MetaGPT 개념 | 본 시스템 구현 |
|-------------|--------------|
| Shared Message Pool | Artifact Store (SQLite + filesystem) |
| 구조화된 문서 게시 | Step 완료 시 artifact 저장 (JSON, YAML, code) |
| 구독 기반 소비 | Orchestrator가 다음 Worker에게 필요한 artifact 주입 |
| 의존성 기반 활성화 | Pipeline Engine의 step 순서 + Entity lock |

핵심: Worker는 서로를 모른다. Orchestrator가 "이전 Step의 이 artifact를 참고하라"고 context에 포함시킬 뿐이다.

#### Orchestrator의 동적 판단

고정 순서이지만, 각 Step 내에서 Orchestrator는 적응적으로 판단한다:

예시 — Step 4 (React 생성) 실행 시:
1. Orchestrator가 page complexity를 보고 Sonnet vs Opus 결정
2. Pattern Library에서 유사 page가 있는지 확인 → few-shot 포함 여부 결정
3. React Worker(Claude CLI) 호출 — worktree에서 실행
4. Worker 완료 후 Orchestrator가 결과 확인 (파일 존재, lint pass)
5. 실패 시: context 확장 + 모델 업그레이드 후 재호출
6. 3회 실패 시: Human escalation
5. 실패 시 Orchestrator가 context 확장 + 모델 업그레이드 판단
6. 3회 실패 시 Orchestrator가 Human escalation 결정

이것이 "고정 워크플로우"와 "Orchestrator-Worker"의 차이점이다.

---

## 4. 모노리포 구조

```
silicon2-migration/
├── apps/
│   ├── orchestrator/              ← FastAPI + Pipeline Engine (Python)
│   │   ├── src/
│   │   │   ├── main.py           ← FastAPI 진입점, static 서빙
│   │   │   ├── api/              ← REST + WebSocket
│   │   │   │   ├── routes/       ← pipeline, pages, review, patterns, cost, settings
│   │   │   │   └── ws/           ← WebSocket event broadcasting
│   │   │   ├── pipeline/         ← 파이프라인 엔진
│   │   │   │   ├── engine.py     ← Orchestrator 메인 루프
│   │   │   │   ├── scheduler.py  ← 동시성 제어, entity lock
│   │   │   │   ├── steps/        ← 9개 step 구현
│   │   │   │   └── retry.py      ← Self-correction 3-tier
│   │   │   ├── context/          ← Context 조립
│   │   │   │   ├── assembler.py  ← 3-Layer context 구성
│   │   │   │   ├── cache.py      ← Prompt caching 전략
│   │   │   │   └── compressor.py ← Artifact 압축/요약
│   │   │   ├── workers/          ← Worker 실행 (4종 분리)
│   │   │   │   ├── analysis.py   ← Analysis Worker (Raw Bedrock API)
│   │   │   │   ├── react.py      ← React Worker (Claude CLI headless + worktree)
│   │   │   │   ├── java.py       ← Java Worker (Claude CLI headless + worktree)
│   │   │   │   ├── mcp.py        ← MCP Worker (php-analyzer subprocess stdio)
│   │   │   │   ├── playwright.py ← Playwright (screenshot capture)
│   │   │   │   └── worktree.py   ← Git worktree lifecycle 관리
│   │   │   ├── output/           ← Output Harness
│   │   │   │   ├── parser.py     ← LLM 출력에서 코드 추출
│   │   │   │   ├── validator.py  ← 문법/스키마/컴파일 검증
│   │   │   │   └── fixer.py      ← 자동 수정 (imports, formatting)
│   │   │   ├── learning/         ← 학습 시스템
│   │   │   │   ├── pattern_store.py ← Pattern CRUD
│   │   │   │   ├── extractor.py  ← 완료 page에서 패턴 추출
│   │   │   │   └── preference.py ← 사용자 선호도 학습
│   │   │   ├── git/              ← Git 자동화
│   │   │   │   └── manager.py    ← branch 생성, step별 커밋
│   │   │   ├── db/               ← 데이터베이스
│   │   │   │   ├── models.py     ← SQLAlchemy 모델
│   │   │   │   ├── migrations/   ← Alembic
│   │   │   │   └── session.py
│   │   │   └── config.py         ← Pydantic Settings
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── frontend/                  ← 생성될 React (Next.js + FSD)
│   │   ├── src/
│   │   │   ├── app/admin/         ← App Router (자동 매핑)
│   │   │   ├── features/          ← FSD features
│   │   │   ├── entities/          ← FSD entities
│   │   │   ├── shared/
│   │   │   │   ├── ui/            ← shadcn/ui
│   │   │   │   ├── api/           ← TanStack Query hooks
│   │   │   │   └── lib/           ← Zustand stores, utilities
│   │   │   └── widgets/           ← FSD widgets
│   │   ├── package.json
│   │   ├── next.config.ts
│   │   ├── tailwind.config.ts
│   │   ├── tsconfig.json (strict)
│   │   ├── jest.config.ts
│   │   ├── .eslintrc.json
│   │   └── .prettierrc
│   │
│   └── backend/                   ← 생성될 Java (Spring Boot + DDD/Hexagonal)
│       ├── src/main/java/com/silicon2/admin/
│       │   ├── domain/            ← Layer별 (전체 공유)
│       │   │   ├── model/         ← Entity, VO
│       │   │   ├── service/       ← Domain Service
│       │   │   └── repository/    ← Repository interface (Port out)
│       │   ├── {feature}/         ← Feature별
│       │   │   ├── application/   ← UseCase, Port in
│       │   │   └── adapter/
│       │   │       ├── in/web/    ← Controller (REST)
│       │   │       └── out/persistence/ ← JPA Repository Impl
│       │   ├── common/            ← 공통 모듈
│       │   │   ├── response/      ← ApiResponse 래퍼
│       │   │   ├── exception/     ← 에러 코드 체계
│       │   │   └── config/        ← Security, CORS, etc.
│       │   └── SiliconAdminApplication.java
│       ├── src/main/resources/
│       │   ├── application.yml
│       │   └── db/migration/      ← Flyway scripts
│       ├── src/test/              ← JUnit5 + Mockito + BDD
│       ├── build.gradle.kts
│       └── Dockerfile
│
├── tools/
│   └── dashboard/                 ← Next.js Dashboard UI
│       ├── src/
│       │   ├── app/               ← App Router
│       │   ├── components/        ← UI 컴포넌트
│       │   ├── hooks/             ← WebSocket, API hooks
│       │   ├── lib/               ← API client
│       │   └── types/             ← TypeScript 타입
│       ├── package.json
│       └── next.config.ts
│
├── docs/                          ← 문서
│   ├── architecture.md            ← 이 파일
│   └── architecture.html          ← HTML 버전
│
├── screenshots/                   ← Playwright 캡처 결과
│   └── {page_id}/
│       ├── original.png
│       └── react_v{N}.png
│
├── docker-compose.yml             ← MySQL + (향후) Orchestrator
├── .env.example
├── .gitignore
├── turbo.json                     ← Turborepo 설정
├── package.json                   ← Root workspace
└── pnpm-workspace.yaml
```

---

## 5. 파이프라인 엔진

### 5.1 9단계 파이프라인 (Page당)

#### 단계 1: Spec 로딩

- **입력**: spec_id (예: `shop_admin.af_member_analysis`)
- **동작**: `{specs_dir}/{spec_id}.aispec.json` 파일 로딩 + JSON schema 검증
- **출력**: 파싱된 Spec 객체 (operations, business_rules, data_models, test_scenarios 등)
- **검증 게이트**: Spec schema 정합성 (필수 필드 존재 여부)
- **모델**: 없음 (파일 I/O만)
- **실패 조건**: 파일 미존재, JSON 파싱 에러, 필수 필드 누락

#### 단계 2: Spec 검증

- **입력**: 파싱된 Spec + MCP 분석 결과
- **동작**: 
  1. `php_detect_gaps()` 호출 → unresolved_calls, broken_includes 확인
  2. Spec의 operations vs MCP trace_entry_tree 비교 → 누락된 flow 확인
  3. 누락 발견 시 Haiku로 Spec 보완 시도
- **출력**: 검증 리포트 (gaps 목록, 보완 내용)
- **검증 게이트**: critical gaps == 0
- **모델**: Haiku (gap 분석 및 보완) / Retry: Sonnet
- **Self-correction**: gaps 발견 → 자동 보완 시도 (max 3회) → 실패 시 Human

#### 단계 3: API Contract 생성

- **입력**: 검증된 Spec + MCP `php_extract_js_api_calls()` 결과
- **동작**: 
  1. Spec의 operations에서 HTTP method, route, input/output 추출
  2. MCP의 js_api_calls에서 프론트엔드 호출 패턴 확인
  3. 둘을 매칭하여 OpenAPI 3.1 schema 생성
- **출력**: `openapi.yaml` (해당 page의 API endpoints)
- **검증 게이트**: `openapi-spec-validator`로 스키마 정합성 확인
- **모델**: Sonnet
- **포함 내용**: 공통 응답 래퍼, 에러 코드, 페이지네이션(offset + cursor)

#### 단계 4: React 생성

- **입력**: Spec + API Contract + Playwright screenshot + Pattern Library (few-shot)
- **동작**:
  1. Playwright로 PHP 원본 화면 캡처
  2. Spec의 UI 관련 정보 + screenshot을 Context에 포함
  3. FSD 구조에 맞는 컴포넌트 생성 (컴포넌트별 분할 생성)
  4. shadcn/ui 사용, TanStack Query로 API 연결, Zustand로 상태 관리
- **출력**: `.tsx`, `.ts` 파일들 (app router page + features + shared)
- **검증 게이트**: 
  1. TSX syntax valid (`eslint --fix` 통과)
  2. Playwright로 생성된 React 렌더 → 원본과 visual diff
  3. diff ≤ 5% → 자동 통과
- **모델**: Sonnet / Retry: Opus
- **Human Review**: 이 단계 완료 후 사용자 확인 필요

#### 단계 5: Java 개발

- **입력**: Spec + API Contract + Entity Registry + Pattern Library (few-shot)
- **동작**:
  1. DDD/Hexagonal 구조에 맞는 클래스 생성 (레이어별 분할)
  2. Domain model → Repository interface → UseCase → Controller → Repository Impl
  3. Lombok, MapStruct 활용
  4. Flyway migration script 생성
- **출력**: `.java` 파일들 + `build.gradle.kts` 의존성 + Flyway SQL
- **검증 게이트**: `gradle compileJava` 성공
- **모델**: Sonnet / Retry: Opus
- **Human Review**: 이 단계 완료 후 사용자 확인 필요

#### 단계 6: Java 테스트

- **입력**: Java 코드 + Spec의 test_scenarios + business_rules
- **동작**:
  1. Spec의 test scenarios를 JUnit5 + Mockito + BDD(Given-When-Then) 형식으로 변환
  2. Repository mock, Service 단위 테스트, Controller 슬라이스 테스트 생성
  3. `gradle test` 실행
- **출력**: 테스트 파일 + 실행 결과
- **검증 게이트**: 모든 테스트 통과
- **모델**: Sonnet (생성) / Haiku (수정)
- **Self-correction**: 테스트 실패 시 에러 메시지 + 실패 케이스를 피드백으로 재생성

#### 단계 7: 통합 테스트

- **입력**: React + Java + API Contract
- **동작**:
  1. API Contract의 각 endpoint에 대해 request/response 쌍 생성
  2. React의 API 호출 코드가 Contract에 맞는지 타입 검증
  3. Java Controller의 응답이 Contract에 맞는지 검증
- **출력**: 통합 테스트 결과 리포트
- **검증 게이트**: 모든 endpoint의 Contract 준수
- **모델**: Haiku / Retry: Sonnet

#### 단계 8: 기능 동등성 확인

- **입력**: PHP MCP trace (call graph, SQL) + Java 코드
- **동작**:
  1. `php_trace_entry_tree()`로 PHP의 전체 실행 흐름 추출
  2. `php_find_sql_by_table()`로 PHP의 데이터 조작 추출
  3. Java 코드의 Repository method들과 비교
  4. 누락된 operation 감지
- **출력**: 동등성 리포트 (covered / missing operations)
- **검증 게이트**: critical missing == 0
- **모델**: Haiku / Retry: Sonnet

#### 단계 9: 완료

- **입력**: 모든 artifact
- **동작**:
  1. Pattern Library 업데이트 (Haiku로 패턴 추출)
  2. 사용자 refinement에서 preference 학습
  3. Git commit (최종)
  4. 상태를 `complete`로 업데이트
  5. Entity Registry 업데이트 (새로 정의된 Entity 등록)
- **출력**: 완료 기록
- **검증 게이트**: 없음
- **모델**: Haiku (패턴 추출)

### 5.2 상태 머신

```
QUEUED → RUNNING → PASSED → (다음 step)
              │         
              ├── RETRYING → (max 3회) → BLOCKED
              │
              └── REVIEW_NEEDED → APPROVED → RUNNING (다음 step)
                                → REFINED → RUNNING (현재 step 재실행)
                                → SKIPPED → (다음 step, 수동 마킹)
```

### 5.3 동시성 모델

```python
# 설정
MAX_PARALLEL_PAGES = 5          # Phase A+B: 동시 page 수
MAX_PARALLEL_GENERATION = 2     # Phase C: React/Java 생성 동시 수
ENTITY_LOCK_TIMEOUT = 300       # Entity lock 5분 타임아웃

# 실행 단계별 병렬성
Phase A (Step 1-2): 최대 5개 page 동시   ← 독립적 (Spec 로딩/검증)
Phase B (Step 3):   최대 5개 page 동시   ← 독립적 (API Contract)
Phase C (Step 4-5): 최대 2개 page 동시   ← Entity 충돌 가능
Phase D (Step 6-8): page당 순차          ← DB/서버 상태 의존
Phase E (Step 9):   병렬 (독립적)         ← 패턴 축적만
```

---

## 6. Context 조립 전략

### 6.1 3-Layer Context 아키텍처

이 설계의 이론적 근거: LLM의 attention mechanism은 context가 길어질수록 중간 부분에 대한 주의가 감소한다 ("Lost in the Middle" 현상). 따라서:

- **핵심 정보(Layer 1)는 prefix에 고정** → 항상 주의 받음 + 캐시 적용
- **Page별 정보(Layer 2)는 중간에** → 필요한 최소 정보만
- **추가 정보(Layer 3)는 실패 시에만** → 불필요한 noise 방지

```
┌─────────────────────────────────────────────────────────┐
│ Layer 1: CACHED (모든 page의 같은 step에서 동일)         │
│                                                          │
│ - System prompt (역할 정의, 출력 규칙)       ~800 tok   │
│ - 프로젝트 코딩 컨벤션                       ~500 tok   │
│ - Shared Entity 정의                        ~1,500 tok  │
│ - Migration Context (축적된 패턴)           ~1,000 tok  │
│                                                          │
│ Subtotal: ~3,800 tokens                                  │
│ Bedrock Prompt Caching 적용 → 비용 90% 절감             │
├─────────────────────────────────────────────────────────┤
│ Layer 2: PAGE-SPECIFIC (page마다 다름)                    │
│                                                          │
│ - Spec (full 또는 relevant section)         ~1,200 tok  │
│ - API Contract (해당 endpoint만)              ~600 tok  │
│ - PHP 원본 (MCP로 핵심 함수만 추출)         ~2,000 tok  │
│ - Few-shot (가장 유사한 완료 page 1개)      ~2,000 tok  │
│                                                          │
│ Subtotal: ~5,800 tokens                                  │
├─────────────────────────────────────────────────────────┤
│ Layer 3: ON-DEMAND (retry 시에만 추가)                    │
│                                                          │
│ - PHP 전체 소스                              ~5,000 tok  │
│ - React 코드 (Java step에서 참조)           ~3,000 tok  │
│ - 이전 시도 결과 + 에러 메시지               ~1,500 tok  │
│                                                          │
│ Subtotal: ~9,500 tokens (필요 시에만)                    │
└─────────────────────────────────────────────────────────┘
```

### 6.2 Progressive Loading

```
시도 1: Layer 1 + Layer 2              → ~6,200 effective tokens
시도 2: Layer 1 + Layer 2 + error      → ~9,000 tokens
시도 3: Layer 1 + Layer 2 + Layer 3    → ~15,700 tokens (전체)
```

비용 효과: 80%가 시도 1에서 성공 → 가중 평균 ~6,800 tokens (항상 전체: 15,700 대비 57% 절감)

### 6.3 모델 선택

| 단계 | 기본 모델 | Retry 모델 | 근거 |
|------|----------|-----------|------|
| Spec 검증 | Haiku | Sonnet | Gap 분석은 구조적 비교 |
| API Contract | Sonnet | Sonnet | Spec에서 기계적 도출 |
| React 생성 | Sonnet | Opus | 복잡한 UI는 더 강력한 추론 필요 |
| Java 개발 | Sonnet | Opus | 아키텍처 결정이 포함됨 |
| Java 테스트 | Sonnet | Sonnet | 패턴 기반 생성 |
| 통합 테스트 | Haiku | Sonnet | Contract 비교 |
| 기능 동등성 | Haiku | Sonnet | Graph 비교 |
| 완료 | Haiku | — | 패턴 추출 |

---

## 7. Output Harness (출력 처리 계층)

### 7.1 필요성

LLM의 출력은 "코드"가 아니라 "텍스트"이다. 다음 문제가 발생한다:

- Markdown 코드블록으로 감싸져 있음 → 추출 필요
- 설명 텍스트가 섞여 있음 → 분리 필요
- import가 누락됨 → 보완 필요
- 들여쓰기가 맞지 않음 → 포맷팅 필요
- 타입 에러가 있음 → 감지 필요

이런 "기계적 실패"가 전부 사용자에게 올라가면 안 된다.

### 7.2 처리 파이프라인

```
LLM Raw Output
    │
    ▼ [1. Extraction]
    │  코드블록 추출 (```tsx, ```java, ```yaml)
    │  JSON 파싱, YAML 파싱
    │  파일 경로 + 내용 분리
    │
    ▼ [2. Validation]
    │  TSX: eslint --fix (subprocess)
    │  Java: gradle compileJava (subprocess)
    │  YAML: openapi-spec-validator
    │  JSON: jsonschema validation
    │
    ▼ [3. Auto-fix]
    │  import 문 자동 추가
    │  Prettier/Spotless 포맷팅
    │  사소한 syntax 수정
    │
    ▼ [4. Persist]
       파일 시스템 저장
       Git staging
       Artifact DB 기록
```

### 7.3 자동 수정 주석

모든 생성 파일에 다음 주석을 추가:

```typescript
// Auto-generated by Silicon2 Migration Orchestrator
// Source: shop_admin.af_member_analysis.aispec.json
// Step: 4 (React Generation)
// Model: claude-sonnet-4-6
// Generated: 2026-05-23T14:30:00Z
```

```java
/**
 * Auto-generated by Silicon2 Migration Orchestrator
 * Source: shop_admin.af_member_analysis.aispec.json
 * Step: 5 (Java Development)
 * Model: claude-sonnet-4-6
 * Generated: 2026-05-23T14:32:00Z
 */
```

---

## 8. Self-Correction 엔진

### 8.1 이론적 근거

MetaGPT 실험 결과: 실행 피드백(Executable Feedback) 제거 시 성능이 -4.2~5.4%p 하락. 즉, "생성 후 검증 → 피드백 → 재생성" 루프가 품질의 핵심 요소이다.

그러나 모든 실패를 동일하게 처리하면 비효율적이다:
- **기계적 실패** (syntax error, import 누락): LLM에게 에러 메시지만 주면 99% 해결
- **논리적 실패** (test fail, wrong logic): 더 많은 context + 더 강한 모델 필요
- **판단 필요 실패** (비즈니스 규칙 모호): 사람만 결정 가능

### 8.2 3-Tier 구조

| Tier | 트리거 | 전략 | 최대 시도 | 사용자 영향 |
|------|--------|------|----------|------------|
| **1. Silent** | compile error, syntax, schema, format | 에러 피드백 → 같은 모델 | 3회 | 없음 (완료 후 "자동 수정됨" 배지) |
| **2. Notify** | test fail, visual diff 초과, minor gap | context 확장 + 모델 업그레이드 | 3회 | "자동 수정 중" 알림 |
| **3. Human** | 3회 소진, 비즈니스 모호, 설계 결정 | Review Queue 등록 | — | BLOCKED 상태 |

### 8.3 Retry Prompt 구성

```python
def build_retry_prompt(error, previous_output, attempt):
    return f"""
## 이전 시도가 실패했습니다 (시도 {attempt}/3)

### 에러:
{error.message}

### 이전 출력 (발췌):
{previous_output[:2000]}

### 지시:
위 에러만 수정하세요.
다른 부분은 절대 변경하지 마세요.
수정된 전체 코드를 출력하세요.
"""
```

---

## 9. 학습 시스템 (Pattern Library)

### 9.1 이론적 근거

707개 page를 처리하는 동안 **동일한 패턴**이 수십~수백 번 반복된다:
- `sql_fetch()` → `Repository.findBy()` (거의 모든 page에서)
- `$_SESSION['ss_mb_id']` → `SecurityContextHolder` (인증 관련 page)
- `get_paging()` → `PageRequest.of()` (모든 list page)

이것을 매번 "처음부터 추론"하게 하면:
1. 비용 낭비 (같은 결론에 도달하기 위해 토큰 소비)
2. 일관성 저하 (미묘하게 다른 변환 결과)
3. 실패 반복 (한 번 실패한 패턴을 다시 시도)

### 9.2 축적 시점

1. **Page 완료 시 (Step 9)**: Haiku가 PHP→Java, PHP→React 매핑 패턴 추출
2. **사용자 Refinement 시**: prompt 분석하여 project-wide preference 자동 추출

### 9.3 활용 시점

다음 page의 Worker 호출 시 Context Layer 1에 포함:
```
## 학습된 프로젝트 패턴 (48개 완료 page에서 추출)

### PHP→Java 매핑 (confidence ≥ 0.9)
- sql_fetch("SELECT...") → {Table}Repository.findBy{Condition}()
- auth_check($member, 'admin') → @PreAuthorize("hasRole('ADMIN')")
- get_paging(...) → PageRequest.of(page, size)

### 사용자 선호도 (항상 적용)
- 테이블 컴포넌트: 항상 sticky header
- 날짜 필터: date-range picker 사용
- Form: React Hook Form + Zod validation
```

### 9.4 Few-shot 선택 알고리즘

```python
def select_few_shot(current_page, completed_pages):
    """가장 유사한 완료 page를 선택하여 input/output 쌍 제공"""
    
    scores = []
    for page in completed_pages:
        score = 0
        # 같은 테이블 사용 → 높은 유사도
        score += len(intersect(current_page.tables, page.tables)) * 3
        # 비슷한 operation 수
        score += similarity(current_page.ops_count, page.ops_count)
        # 비슷한 business rule 수
        score += similarity(current_page.br_count, page.br_count)
        # 같은 UI 패턴 (list/detail/form)
        if current_page.ui_pattern == page.ui_pattern:
            score += 5
        scores.append((page, score))
    
    # 최고 점수 page의 해당 step artifact를 few-shot으로 반환
    best = sorted(scores, key=lambda x: -x[1])[0]
    return best
```

---

## 10. 데이터베이스 스키마

### 10.1 핵심 테이블

```sql
-- 페이지 상태 (707 rows)
CREATE TABLE pages (
    id TEXT PRIMARY KEY,                    -- "shop_admin.af_member_analysis"
    module TEXT NOT NULL,                   -- "shop_admin"
    title TEXT,                            -- "제휴회원 상세 분석"
    spec_status TEXT,                       -- draft/complete/ready/final
    spec_score REAL,                        -- 0.906
    complexity TEXT,                        -- low/medium/high
    migration_status TEXT DEFAULT 'queued', -- queued/running/review/blocked/complete/failed
    current_step INTEGER DEFAULT 0,        -- 0-9
    branch_name TEXT,                       -- "migration/shop_admin.af_member_analysis"
    total_cost REAL DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 단계 실행 기록
CREATE TABLE step_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id TEXT REFERENCES pages(id),
    step_number INTEGER NOT NULL,          -- 1-9
    step_name TEXT NOT NULL,               -- "react_generation"
    status TEXT NOT NULL,                  -- running/passed/failed/retrying/review/blocked
    attempt_number INTEGER DEFAULT 1,     -- 현재 시도 회차
    model_used TEXT,                       -- "claude-sonnet-4-6"
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost REAL,
    duration_ms INTEGER,
    cache_hit_rate REAL,                   -- 0.0-1.0
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- 생성된 Artifact
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id TEXT REFERENCES pages(id),
    step_number INTEGER NOT NULL,
    artifact_type TEXT NOT NULL,           -- react_component/java_class/api_contract/test/screenshot
    file_path TEXT NOT NULL,               -- 모노리포 루트 기준 상대 경로
    version INTEGER DEFAULT 1,
    content_hash TEXT,                     -- SHA-256
    token_count INTEGER,                   -- 이 artifact의 토큰 수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 사용자 리뷰
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id TEXT REFERENCES pages(id),
    step_number INTEGER NOT NULL,
    status TEXT NOT NULL,                  -- pending/approved/refined/skipped
    review_type TEXT,                      -- blocking/info
    summary TEXT,                          -- 리뷰 요청 요약
    user_prompt TEXT,                      -- 사용자 수정 요청 (refinement 시)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- 패턴 라이브러리
CREATE TABLE patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,            -- php_to_java/php_to_react/user_preference
    php_pattern TEXT,                      -- 원본 패턴
    target_pattern TEXT,                   -- 변환 결과 패턴
    description TEXT,                      -- 설명
    confidence REAL DEFAULT 0.5,          -- 신뢰도 (0-1)
    usage_count INTEGER DEFAULT 0,        -- 사용된 횟수
    source_pages TEXT,                     -- JSON array: 발견된 page_ids
    applies_to TEXT,                       -- all/list_pages/form_pages/detail_pages
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 비용 추적
CREATE TABLE cost_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id TEXT REFERENCES pages(id),
    step_number INTEGER,
    model TEXT NOT NULL,                   -- "claude-opus-4-6"
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cache_read_tokens INTEGER DEFAULT 0,
    cost REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 공유 Entity 레지스트리
CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name TEXT UNIQUE NOT NULL,      -- "AffiliateMember"
    table_name TEXT NOT NULL,              -- "g5_shop_affiliate_member"
    package_path TEXT,                     -- "com.silicon2.admin.domain.model"
    definition TEXT NOT NULL,              -- JSON: fields, types, constraints, relationships
    defined_by_page TEXT,                  -- 처음 정의한 page
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 11. API 명세

### 11.1 REST Endpoints

```
파이프라인 제어
  POST   /api/pipeline/run              ← 파이프라인 시작 (단일/다중/모듈 선택)
  POST   /api/pipeline/pause            ← 전체 일시정지
  POST   /api/pipeline/resume           ← 재개
  DELETE /api/pipeline/{page_id}        ← 특정 page 취소

페이지 관리
  GET    /api/pages                     ← 목록 (필터, 정렬, 페이지네이션)
  GET    /api/pages/{page_id}           ← 상세 (step 상태 포함)
  GET    /api/pages/{page_id}/artifacts ← Artifact 목록
  GET    /api/pages/{page_id}/logs      ← 실행 로그
  POST   /api/pages/{page_id}/retry     ← 현재 step 재시도
  POST   /api/pages/{page_id}/skip      ← 현재 step 건너뛰기
  POST   /api/pages/{page_id}/rollback  ← 이전 step으로 되돌리기

리뷰 관리
  GET    /api/reviews                   ← 대기 중 리뷰 목록
  GET    /api/reviews/{id}              ← 리뷰 상세
  POST   /api/reviews/{id}/approve      ← 승인하고 다음 진행
  POST   /api/reviews/{id}/refine       ← 수정 요청 (prompt body)
  POST   /api/reviews/{id}/skip         ← 건너뛰기 (수동 처리 마킹)

패턴 관리 (CRUD)
  GET    /api/patterns                  ← 전체 패턴 목록
  GET    /api/patterns/{id}             ← 패턴 상세
  POST   /api/patterns                  ← 패턴 수동 생성
  PUT    /api/patterns/{id}             ← 패턴 수정
  DELETE /api/patterns/{id}             ← 패턴 삭제

비용 분석
  GET    /api/cost/summary              ← 전체 요약
  GET    /api/cost/by-model             ← 모델별 분석
  GET    /api/cost/by-step              ← 단계별 분석
  GET    /api/cost/by-page              ← 페이지별 분석

설정
  GET    /api/settings                  ← 현재 설정 조회
  PUT    /api/settings                  ← 설정 변경
```

### 11.2 WebSocket 이벤트

```
서버 → 클라이언트 (실시간 업데이트)
  pipeline:step_started       { page_id, step, timestamp }
  pipeline:step_completed     { page_id, step, status, duration_ms, cost }
  pipeline:step_failed        { page_id, step, error, attempt_number }
  pipeline:review_needed      { page_id, step, review_type, summary }
  pipeline:page_completed     { page_id, total_cost, total_duration }
  pipeline:auto_fixed         { page_id, step, description }
  cost:updated                { total_spend, page_id, delta }
  pattern:learned             { pattern_id, pattern_type, description }

클라이언트 → 서버 (제어)
  pipeline:run                { page_ids: string[], mode: "single"|"batch"|"module" }
  pipeline:pause              {}
  pipeline:resume             {}
  review:approve              { review_id: number }
  review:refine               { review_id: number, prompt: string }
```

### 11.3 공통 응답 형식

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2026-05-23T14:30:00Z",
    "request_id": "req_abc123"
  }
}
```

에러 시:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "PIPELINE-001",
    "message": "Page not found",
    "detail": "Page 'shop_admin.nonexistent' does not exist in specs directory"
  },
  "meta": { ... }
}
```

---

## 12. Git 관리

### 12.1 Branch 전략

```
main (보호됨)
├── migration/shop_admin.af_member_analysis
├── migration/bbs.delete_all
├── migration/core.auth_list
└── ...
```

각 page가 pipeline을 시작하면 `migration/{page_id}` branch가 자동 생성된다.
pipeline 완료 후 사용자가 main에 merge (수동 or 자동 PR 생성).

### 12.2 자동 커밋 형식

```
feat({feature}): step {N} - {한글 설명}

Auto-generated by Silicon2 Migration Orchestrator
Page: {page_id}
Model: {model_used}
Cost: ${cost}
Duration: {duration}s
Attempt: {attempt}/{max_attempts}
```

예시:
```
feat(af-member): step 4 - React 컴포넌트 생성

Auto-generated by Silicon2 Migration Orchestrator
Page: shop_admin.af_member_analysis
Model: claude-sonnet-4-6
Cost: $0.12
Duration: 18s
Attempt: 1/3
```

### 12.3 커밋 시점

- Step 3 완료: API Contract (`openapi.yaml`)
- Step 4 완료: React 파일들
- Step 5 완료: Java 파일들 + Flyway migration
- Step 6 완료: Java 테스트 파일들
- Step 9 완료: 최종 정리 (lint fix 등)

---

## 13. 설정

### 13.1 환경 변수 (.env)

```bash
# 경로
SPECS_DIR=/Users/stoni/Projects/silicon2/harness/specs
PHP_PROJECT_ROOT=/Users/stoni/Projects/silicon2/sk-main-php
MCP_SERVER_PATH=/Users/stoni/.mcp-servers/php-analyzer
SCREENSHOTS_DIR=./screenshots

# Playwright
PW_BASE_URL=https://dev.stylekorean.com
PW_ADMIN_ID=xxxxx
PW_ADMIN_PW=xxxxx

# AWS Bedrock
AWS_REGION=us-east-1

# 파이프라인
MAX_PARALLEL_PAGES=5
MAX_PARALLEL_GENERATION=2
MAX_RETRY_ATTEMPTS=3
VISUAL_DIFF_THRESHOLD=5

# 예산
PROJECT_BUDGET=20000

# 데이터베이스
DATABASE_URL=sqlite:///./data/orchestrator.db
```

---

## 14. 배포 경로

### 14.1 로컬 개발

```bash
# 모노리포 클론
git clone <repo> silicon2-migration && cd silicon2-migration
pnpm install

# Python 환경
cd apps/orchestrator
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# MySQL (Docker)
docker-compose up -d mysql

# 실행
uvicorn src.main:app --reload --port 8000   # Orchestrator
cd tools/dashboard && pnpm dev               # Dashboard
```

### 14.2 이관 경로

| 컴포넌트 | 로컬 | Docker | AWS |
|----------|------|--------|-----|
| DB | SQLite | PostgreSQL | Aurora |
| 컴퓨팅 | 로컬 프로세스 | Docker container | ECS Fargate |
| 파일 저장 | 로컬 filesystem | Volume mount | S3 |
| WebSocket | FastAPI native | 동일 | API Gateway WebSocket |
| 백그라운드 작업 | asyncio | 동일 | SQS + Lambda |

---

## 15. PoC 범위

### 15.1 대상

- **Page**: `bbs.alert_close`
- **사양**: 1 operation, 6 business rules, 10 test scenarios
- **Review score**: 0.950 (최고 수준)
- **Complexity**: LOW
- **선정 근거**: 최소 리스크로 전체 파이프라인 end-to-end 검증

### 15.2 성공 기준

1. 9단계 파이프라인이 시작부터 끝까지 실행됨
2. React component (.tsx) 생성 + TypeScript 문법 정상
3. Java code 생성 + `gradle compileJava` 성공
4. JUnit test 생성 + `gradle test` 통과
5. Git branch 생성 + step별 자동 커밋 완료
6. Dashboard에서 실시간 진행 상태 확인 가능
7. WebSocket으로 step 진행 이벤트 수신 확인
8. Cost/token 추적 정상 동작
9. Playwright screenshot 캡처 성공

### 15.3 PoC에서 제외 (이후 구현)

- 통합 테스트 (E2E) 실제 실행
- 기능 동등성 검증 실제 실행
- Pattern Library 자동 축적
- 병렬 실행 (5개 동시)
- Visual diff 자동 비교
- Budget governor

---

## 16. 참고 자료

1. **본 프로젝트**: [theoretical-foundation.md](./theoretical-foundation.md) — SDLC · AWS AI-DLC · Harness Engineering 통합 포지셔닝
2. AWS. [AI-Driven Development Life Cycle](https://aws.amazon.com/blogs/devops/ai-driven-development-life-cycle/). 2025.
3. AWS Labs. [awslabs/aidlc-workflows](https://github.com/awslabs/aidlc-workflows). GitHub.
4. Anthropic. "Building Effective Agents." 2024.12 — Orchestrator-Worker 패턴 정의 및 적용 가이드
5. Hong, S. et al. "MetaGPT: Meta Programming for Multi-Agent Collaborative Framework." arXiv:2308.00352 — 구조화 통신 + 실행 검증의 정량적 효과 입증
6. Andrew Ng. "Agentic Design Patterns Part 5: Multi-Agent Collaboration." DeepLearning.AI — 다중 에이전트의 이론적 근거
7. LangChain. "LangGraph Multi-Agent Workflows." — Supervisor-as-Tool-User 패턴 구현 레퍼런스
