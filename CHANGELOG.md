# Changelog

## 2026-05-26 — Pipeline Stabilization & Multi-Page Migration

### New Pages Migrated
- **shop.mp_profile** — Beauty Profile (모바일)
- **shop.mp_settings** — Account Settings (모바일)
- **mypage.wallet** — My Wallet (포인트/쿠폰)

### Orchestrator Improvements

#### MCP PHP File Resolution (LLM-based)
- URL에서 실제 PHP 소스 파일을 찾을 때 LLM(Haiku)을 활용
- MCP `php_find_entry_points`에서 전체 엔트리 목록 조회 → URL 키워드 pre-filter → LLM 선택
- 예: `mp_settings.php` URL → `mobile/shop/member/account_settings.php` 자동 매핑
- Rule-based prefix 제거(mp_, my_) 대신 유연한 LLM 매칭

#### Playwright 모바일 캡처
- 모든 캡처에 iPhone UA + 430x932 viewport 적용
- `capture`, `capture_for_spec`, `capture_react` 모두 모바일 통일
- 로그인 셀렉터 다양화 (mb_id, email, button 등)

#### Pipeline Engine 실시간 상태 반영
- 각 Step 시작 시 "running" execution을 DB에 commit → Dashboard 즉시 반영
- Step 완료 후 execution 업데이트 (passed/blocked/retrying)
- `engine.run()`에서 매 step 후 `session.commit()` (이전: 전체 완료 후 1회 commit)
- 이미 완료된 step skip (`step_number <= current_step`)
- `_rebuild_context()` 호출로 중간부터 재개 가능

#### Dashboard 상태 정확도
- Step status 표시 로직 개선:
  - `running`: 실제 active execution이 있을 때만
  - `queued`: page가 running이지만 해당 step 미시작
  - `passed`: execution 기록에 passed가 있으면 무조건 passed 표시
- Live Log 패널 추가 (cli:text, cli:tool_use, step 이벤트 실시간 표시)
- Artifacts 컬럼: 파일명 리스트 펼침 (details/summary)

#### Step 6 (Java Test) 자동 수정
- 테스트 실패 시 Claude CLI(max_turns=15)로 코드 수정 후 재테스트
- 최대 3번 반복 (fix → test → fix → test → fix → test)
- 프롬프트에 @DataJpaTest 충돌, 파일명/클래스명 불일치 해결 힌트 포함

#### Step 7 (Integration) 프롬프트 강화
- Backend curl 응답의 **실제 JSON 구조**를 읽고 매핑하도록 강제
- 검색 결과 JSX 렌더링 필수 (로딩 스피너, 빈 결과, 결과 카드)
- DataInitializer에 고유 bean name 사용 지시

#### Step 8 (Equivalence) 매칭 개선
- java_files 없어도 search_roots에서 *Controller.java 자동 탐색
- Route fuzzy matching: /v1 prefix 무시, keyword 기반 파일명 매칭

#### State Machine
- `COMPLETE → RUNNING` 전환 허용 (retry 가능)

#### Spec 생성 프롬프트
- "소스에 없는 operation을 만들지 마라" 강제
- 실제 SQL 테이블명 사용, read-only 페이지는 GET만
- `source.path`에 resolved PHP 경로 기록

### Bug Fixes
- Bean name 충돌: 모든 DataInitializer에 고유 @Component name
- `data_layer.tables`가 dict일 때 slice 에러 → 타입 체크 추가
- MCP singleton background task 호환 문제 → 제거, 항상 fresh connection
- `SCREENSHOTS_DIR` 절대경로로 변경 (경로 불일치 해결)
- `BeautyProfileRepositoryTest` @DataJpaTest context 로딩 실패 → 제거

### Cost Summary (per page)
| Page | Total Cost | Duration |
|------|-----------|----------|
| shop.mp_profile | $2.21 | ~13min |
| mypage.wallet | $1.77 | ~10min |
| shop.mp_settings | ~$2.00 | ~12min |
