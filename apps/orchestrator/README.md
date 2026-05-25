# Silicon2 Migration Orchestrator

StyleKorean PHP 레거시를 React (Next.js) + Spring Boot로 자동 마이그레이션하기 위한 **로컬 단일 사용자** 오케스트레이터입니다.

9단계 파이프라인(spec load → verify → API contract → React gen → Java gen → Java test → integration → equivalence → complete)을 실행하고, WebSocket으로 진행 상황을 UI에 전달합니다.

## 사전 요구사항

- Python 3.11+
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) (`claude` 명령이 PATH에 있어야 함)
- AWS 자격증명 (Bedrock 사용 step용, 기본 credential chain)
- MCP php-analyzer 서버 (`MCP_SERVER_PATH`)
- Node.js / Java (생성된 frontend·backend 앱 실행·테스트용)
- Playwright (스크린샷 캡처·비주얼 비교 step용)

## 설치

```bash
cd apps/orchestrator
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium
```

Playwright만 별도로 설치하려면:

```bash
pip install -e ".[playwright]"
playwright install chromium
```

## 환경 변수

모노레포 루트의 `.env` 또는 `apps/orchestrator/.env`에 설정합니다. Settings는 두 위치를 모두 읽습니다.

| 변수 | 필수 | 설명 |
|------|------|------|
| `SPECS_DIR` | ✅ | 페이지 spec YAML 디렉터리 |
| `PHP_PROJECT_ROOT` | ✅ | 원본 PHP 프로젝트 루트 |
| `MCP_SERVER_PATH` | ✅ | php-analyzer MCP 서버 경로 |
| `SCREENSHOTS_DIR` | | 스크린샷 저장 경로 (기본 `./screenshots`) |
| `PW_BASE_URL` | | Playwright 대상 URL (기본 `https://dev.stylekorean.com`) |
| `PW_ADMIN_ID` / `PW_ADMIN_PW` | | 관리자 로그인 (캡처 step) |
| `DATABASE_URL` | | SQLite URL (기본 `sqlite:///./data/orchestrator.db`) |
| `ORCH_LOG_LEVEL` | | 로그 레벨 (기본 `INFO`) |
| `MAX_PARALLEL_PAGES` | | 동시 페이지 파이프라인 수 (기본 `1`) |
| `PROJECT_ROOT` | | monorepo 루트 (미설정 시 자동 탐지) |
| `CLAUDE_PATH` | | Claude CLI 경로 (기본 `claude`) |
| `MCP_PYTHON_PATH` | | MCP 서버 Python (기본 `python3`) |
| `ENFORCE_PROJECT_BUDGET` | | `true` 시 budget 초과 페이지 run 차단 |
| `USE_WORKTREE` | | `true` 시 페이지별 git worktree 격리 (병렬 실행 안전) |

루트 `.env.example`을 참고해 값을 채우세요.

## 데이터베이스

```bash
cd apps/orchestrator
alembic upgrade head
```

앱 시작 시 lifespan에서도 마이그레이션이 적용됩니다.

## 실행

```bash
cd apps/orchestrator
uvicorn src.main:app --reload --port 8000
```

- Health: `GET http://localhost:8000/api/health`
- WebSocket: `ws://localhost:8000/ws`

## 테스트

```bash
cd apps/orchestrator
pytest
```

Playwright 브라우저가 없는 환경에서는 캡처 관련 테스트가 graceful하게 skip되거나 연결 실패로 종료됩니다.

## 문서

- [Phase 1~5 개선 스펙](docs/improvement-spec.md)
- [Phase 6 개선 스펙](docs/phase6-spec.md)
- 모노레포 아키텍처: `../../docs/architecture.md`
