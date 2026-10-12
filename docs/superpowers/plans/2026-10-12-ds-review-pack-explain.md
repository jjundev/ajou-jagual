# 복습팩 문제설명 자동 연결 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** ds-review-pack에 문제설명 자동 실행을 연결하고 기존 9팩 64문항의 해설 HTML·MD를 검증하여 발행한다.

**Architecture:** 신규 팩과 기존 문제 갱신의 마지막에 하나의 공통 안내 문서를 실행한다. 기존 ds-problem-explain CLI와 저작·검토·발행 계약을 재사용한다. 과거 교과서 갱신의 보존 기록은 유지하고, 새 해설의 검증된 교체를 별도 기록으로 확인한다.

**Tech Stack:** Python 3.10+, 표준 라이브러리 CLI, unittest/pytest, HTML/CSS/JavaScript, 로컬 KaTeX/Pretendard, 브라우저 검증.

**Spec:** `docs/superpowers/specs/2026-10-12-ds-review-pack-explain-design.md` — 실행자는 이 설계와 계획을 모두 읽는다.

## Global Constraints

- 신규 팩은 정리노트·복습문제·문제설명 각각 HTML과 MD를 제공한다.
- update-existing으로 문제를 갱신하면 전체 문항의 문제설명도 갱신한다.
- lite에서도 해설 작성·독립 검산·브라우저 검증을 수행한다.
- 해설이 실패하면 검증된 복습팩은 보존하고, “복습팩 생성됨 / 문제설명 보류”로 보고한다.
- bank 모드는 현재 절차를 유지한다.
- 최종 복습문제 HTML의 절대 경로를 지정한다. 날짜나 최신 팩 선택에 맡기지 않는다.
- Python 3.10 이상, 해설 실행기는 표준 라이브러리만 사용한다.
- 일곱 직계 구역 `understand → recall → start → solve → verify → pitfall → retry`를 유지한다.
- 브라우저는 1280×900·375×812와 light/dark에서 모든 문항을 확인한다.
- 콘솔·KaTeX 오류, 누락 자원, 외부 요청, 문서 가로 넘침은 0이어야 한다.
- ds-problem-explain 실행기·템플릿·이식 해시 기록과 과거 자료_복습팩 검증 기록은 변경하지 않는다.
- 기존 팩 해설 추가 시 원 복습문제 HTML/MD·정리노트·그림·은행은 변경하지 않는다.
- 커밋·푸시는 별도 사용자 요청이 있을 때만 수행한다. 작업별 커밋 지점은 제안으로 기록한다.

## Review Focus

1. 같은 날짜의 여러 slug와 NFC/NFD 경로: 자동 연결은 정확한 HTML을 선택한다 — Task 1의 기존 source 회귀 검사.
2. 0문항·모호한 소문항·원문 충돌: 빈 완성본이나 자동 fallback 없이 해당 팩 보류 — Task 1의 source/contract 검사, Task 3 실자료 검토.
3. 1012처럼 해설 생성 후 문제가 늘어난 경우: 현재 문항 ID와 원본 해시 전체가 일치 — Task 2의 낡은 manifest fixture와 Task 3 납품 검사.
4. 해설 검토 후 입력 변경·교체 실패: 승인 재사용을 거부하고 기존 파일 보존·복구 — Task 1의 publish/CLI 회귀 검사.
5. 과거 보존 해시를 핑계로 노트 손상을 허용하는 경우: 정확한 해설 소유 경로와 검증 기록에만 교체 예외 — Task 2의 보존 검사 fixture.

---

## 파일 구조와 경계

아래 경로는 저장소 루트 기준이다. 명령의 R은 실행 시 `git rev-parse --show-toplevel`로 얻은 절대 경로다. P는 pytest가 설치된 Python 3.10+ 실행 파일이다. 기존 테스트 환경을 우선 재사용하며 없는 경우 scratch venv를 준비한다. 시스템 Python과 실행기 의존성은 변경하지 않는다. 두 스킬의 테스트는 import 이름 충돌을 피하도록 별도 프로세스로 실행한다.

| 파일 | 역할 |
|---|---|
| `.agents/skills/ds-review-pack/SKILL.md` | 모드·산출물·단계·완료/보류 보고 연결 |
| `.agents/skills/ds-review-pack/references/problem-explain.md` (신규) | 정확한 최종 HTML을 받는 공통 해설 절차 |
| `.agents/skills/ds-review-pack/references/textbook-update.md` | 갱신된 리뷰 발행 이후 해설 재생성 |
| `.agents/skills/ds-review-pack/tests/explanation_delivery_checks.py` (신규) | 테스트용 납품 기록·현재 해시·교체 범위 검사 |
| `.agents/skills/ds-review-pack/tests/test_problem_explain_delivery.py` (신규) | 검사 helper의 fixture 테스트와 실제 해설 납품 검사 |
| `.agents/skills/ds-review-pack/tests/test_textbook_delivery.py` | 과거 보존 검사에 검증된 해설 교체만 허용 |
| `복습노트/<date>/문제설명_<date>_<slug>.html/.md` 및 소유 자료/그림 폴더 | 실제 해설; 1012는 백업 후 교체 |
| `docs/verify/2026-10-12-ds-review-pack-explain.json/.md` (신규) | 팩별 발행/보류·원본 보존·교체·검증·백업 기록 |

해설 실행기에는 새 API를 추가하지 않는다. 테스트 helper는 테스트 디렉터리 안에서만 사용한다.

### Task 1: 신규 생성과 기존 갱신의 공통 해설 단계 연결

**Files:** Modify `.agents/skills/ds-review-pack/SKILL.md:3-27,156-187`, `references/textbook-update.md:3-13`; Create `references/problem-explain.md`. Test: 기존 `test_skill_files.py`, ds-problem-explain의 source/contract/CLI/publish 테스트.

**Interfaces:**
- Consumes: 검증·MD 변환·발행이 끝난 복습문제 HTML의 절대 Path, 저장소 절대 Path, 팩별 고유 RUN.
- Produces: 최종 HTML을 `mpe_cli.py extract --repo R --target ABS_REVIEW --run EXPLAIN_RUN`에 넘기는 에이전트 실행 계약. 결과는 published 또는 withheld이며 이유·HTML/MD·RUN·백업 경로를 보고한다. Python 함수 호출로 스킬이 자동 실행된다고 가정하지 않는다.

- [x] **Step 1: 현재 검사 기준선 확인.** `P -m pytest .agents/skills/ds-review-pack/tests/test_skill_files.py -q`와 별도 프로세스의 `P -m pytest .agents/skills/ds-problem-explain/tests/test_source.py .agents/skills/ds-problem-explain/tests/test_contract.py .agents/skills/ds-problem-explain/tests/test_cli.py .agents/skills/ds-problem-explain/tests/test_publish.py -q`를 실행한다. 예상: 모두 PASS. 기존 실패는 이번 변경과 구분해 기록한다.
- [x] **Step 2: 공통 절차 작성.** 새 reference에 EXPLAIN_SKILL을 현재 스킬의 형제 `ds-problem-explain` 절대 경로로 정하고 파일 존재를 먼저 확인하도록 적는다. 해당 SKILL/authoring/verification을 읽고 extract→저작→독립 검산→build→check→실검토→publish 전부 수행한다. build 뒤 검토가 not_run으로 초기화되며 test helper의 approved()를 실제 승인에 쓰지 않도록 명시한다. 원본 변경은 재추출, 조각/stage 변경은 재build·재검토한다. 미해결 검사나 0문항 팩은 해설에 넘겨 발행하지 않는다.
- [x] **Step 3: 두 진입점 연결.** SKILL의 0~9 기존 번호를 유지하고 8단계에 MD 변환 후 해설 하위 단계를 추가한다. description/산출물/모드/lite/진행 표시/9단계 보고/오류 처리를 일치시킨다. textbook-update는 8단계 리뷰 발행 후 같은 reference를 실행하고 9단계에 해설 결과를 보고한다. 신규 reference는 SKILL에 명시하여 기존 every-reference 검사에 포함한다.
- [x] **Step 4: 모드별 검토.** 신규·update-existing·lite·bank·해설 스킬 누락·해설 실패의 여섯 시나리오를 읽어 추적한다. 예상: 앞의 세 모드는 전체 해설 단계, bank는 변화 없음, 누락은 생성 시작 전에 명확한 오류, 실패는 원 팩 보존과 보류 보고. 문구 존재만 확인하는 신규 테스트는 만들지 않는다.
- [x] **Step 5: 회귀 검증.** Step 1 명령을 다시 실행하고 `git diff --check`를 확인한다. 경로 선택은 test_nfd_target/test_multiple_slugs_require_path, 입력 문제는 test_empty_latest_does_not_fallback/test_ambiguous_subparts_block/test_disputed_reviews_rejected, 실패 보호는 test_stale_inputs_or_failed_reviews_are_refused/test_replace_failure_rolls_back_pair/test_one_stale_pack_does_not_block_other_pack가 PASS여야 한다.
- [x] **Step 6: 작업 경계 검토.** 위 세 문서만 변경되었는지 확인한다. 승인된 경우의 커밋 제안: `feat(ds-review-pack): generate problem explanations after reviews`.

### Task 2: 납품과 과거 보존 기록을 함께 검사

**Files:** Create `.agents/skills/ds-review-pack/tests/explanation_delivery_checks.py`, `test_problem_explain_delivery.py`; Modify `tests/test_textbook_delivery.py:32-35`. 과거 validation.json은 수정하지 않는다.

**Interfaces:**
- Consumes: R의 현재 리뷰/설명 manifest·validation, 기존 교과서 보존 digest, 아래의 새 발행 JSON.
- Produces: 테스트 helper `check_pack(root: Path, item: dict) -> list[str]`, `check_preserved(root: Path, relative: str, digest: str, report: dict | None) -> list[str]`. 빈 list가 통과다. report가 없어도 원 파일 해시가 같으면 과거 보존 검사는 통과한다.
- JSON: `version: 1`, `packs: list[dict]`. 각 item은 `date`, `slug`, `source`(repo 상대 경로), `source_sha256`, `problem_ids`, `status`(published|withheld), `reason`, `html`, `md`, `manifest`, `validation`, `run`, `backup`(절대 경로 또는 null), `protected_files`(repo 상대 경로→sha256), `replacements`(repo 상대 경로→`{before_sha256, after_sha256, backup_sha256}`; after는 삭제 시 null). withheld의 미발행 경로는 null 허용. 기록은 직접 읽거나 실행하여 확인한 값만 넣는다.

- [x] **Step 1: 실패 fixture 테스트 작성.** `test_current_source_and_all_problem_ids_required`: source가 12문항이면 이전 8문항 manifest와 이전 source_sha256 각각 check_pack 오류; 전체 ID와 현재 해시는 통과. `test_unreviewed_delivery_rejected`: validation의 네 검토 중 not_run/fail/disputed가 있으면 오류. `test_exact_explanation_ownership_only`: note 또는 자료_복습팩 경로를 replacements에 넣어도 check_preserved는 digest mismatch 오류. `test_unrecorded_or_unbacked_change_rejected`: 해설 파일 변경에 before digest 불일치 또는 backup_sha256 누락이면 오류. `test_historical_record_survives_valid_replacement`: 정확한 해설 소유 경로·before==backup digest·통과한 현재 납품이면 허용; 과거 validation bytes는 동일. fixture는 tmp_path를 쓰고 실제 수업 파일에 쓰지 않는다.
- [x] **Step 2: 실패 확인.** `P -m pytest .agents/skills/ds-review-pack/tests/test_problem_explain_delivery.py -k 'not real_delivery' -q`. 예상: helper 미구현으로 FAIL.
- [x] **Step 3: helper 구현.** check_pack은 표준 라이브러리로 현재 source/manifest 해시·문항 ID·validation의 source_visual/content/independent/browser와 모든 item pass·manifest files의 실파일 해시·validation artifact_hashes를 확인한다. review의 test-only approved()는 사용하지 않는다. source ID는 review-pack의 기존 extract_cards로 얻는다. check_preserved는 원 digest를 우선 확인하고, 다를 때 정확한 stem HTML/MD 또는 그 stem의 figures/자료 하위 경로에 한해서 해당 published 팩이 check_pack을 통과하고 replacements.before_sha256==digest==backup_sha256인 경우만 허용한다. 현재 교체된 파일은 after_sha256까지 확인하고 삭제는 실제 부재를 확인한다.
- [x] **Step 4: 과거 보존 검사 연결.** test_preserved_note_figures_and_explanations의 경로별 단순 hash 비교를 check_preserved로 교체한다. 보고서가 없으면 현재와 같은 검사다. 해설 교체를 제외한 모든 파일은 동일 digest를 요구한다. 신규 `test_real_delivery`는 JSON 존재, 9개 날짜 중복 없음, 모든 status==published, 각 check_pack 오류 없음, 총 64문항을 요구한다. 이 검사는 Task 3 전에는 누락 보고서로 실패하는 것이 정상이다.
- [x] **Step 5: fixture 통과 확인.** Step 2 명령은 PASS, 기존 교과서 납품 테스트도 PASS여야 한다. 실제 납품 검사는 아직 FAIL임을 별도 기록한다. 두 스킬 테스트의 전체 프로세스를 합치지 않는다.
- [x] **Step 6: 작업 경계 검토.** 테스트 3개 파일만 변경되었는지 확인한다. 승인된 경우의 커밋 제안: `test(ds-review-pack): verify explanation delivery and historical preservation`.

### Task 3: 기존 9팩의 전체 해설 작성·검증·발행

**Files:** Create/Replace 설계 표의 날짜별 `문제설명_<date>_<slug>.html/.md`, `figures_문제설명_<date>_<slug>/`, `자료_문제설명_<date>_<slug>/`; Create `docs/verify/2026-10-12-ds-review-pack-explain.json/.md`.

**Interfaces:**
- Consumes: Task 1 공통 실행 계약, Task 2 JSON/검사 helper 계약.
- Produces: 현재 원본 전체 문항의 검증된 해설과 발행 기록. source.json·조각·검산·review.json은 고유 RUN에 두고 기존 CLI가 소유 자료 폴더에 보관한다.

- [x] **Step 1: 대상과 보존 기준선 기록.** NFC/NFD 실제 경로로 9개 리뷰를 찾아 read-only load_source로 문항 수를 재확인한다. 표의 4/12/12/8/4/4/4/4/12와 다르면 그 팩의 작업을 중단해 변경 이유를 확인한다. 전체 원 리뷰/노트/기존 figures/자료_복습팩·양쪽 은행을 protected_files에 기록한다. 1012의 기존 설명 소유 파일도 별도 bytes/hash 목록과 고유 RUN 백업으로 기록한다. RUN 백업은 종료 시 삭제하지 않는다.
- [x] **Step 2: 팩별 extract.** 각 날짜 오름차순으로 고유 EXPLAIN_RUN에 Task 1의 정확한 절대 HTML target 명령을 실행한다. 예상: extract 종료 코드 0, source.json 문항 ID 목록이 현재 리뷰와 동일. extract 실패 시 withheld 이유를 기록하고 다음 팩을 진행한다. update-existing all은 실행하지 않는다.
- [x] **Step 3: 팩별 원자료 확인과 해설 저작.** 모든 pN에 대해 현재 source.json과 원 기출/교과서/강의록/정리노트의 실제 관련 페이지를 읽는다. understand/recall/start/solve/verify/pitfall/retry 및 우측 요약을 작성한다. 재귀는 호출·반환, 리스트/스택/큐는 연산별 상태, C는 변수·주소·객체·입력 가정과 정의된 동작을 구분한다. 기존 풀이를 길게 복제해 독립 설명으로 대신하지 않는다.
- [x] **Step 4: 팩별 독립 검산.** 각 소문항의 실행·별도 시뮬레이션·논증을 evidence에 보관한다. 원자료 충돌/UB/비종료/모호함은 disputed로 보고하고 팩 발행을 보류한다. 증명 문제는 숫자 예제만으로 승인하지 않는다.
- [x] **Step 5: 팩별 build/check.** `python3 ABS_EXPLAIN_CLI build --run EXPLAIN_RUN`, `python3 ABS_EXPLAIN_CLI check --run EXPLAIN_RUN`. 예상: 종료 코드 0, machine PASS. 수정 후 build하면 이전 검토가 초기화되므로 새 stage를 다시 검토한다.
- [x] **Step 6: 팩별 실제 검토.** source_visual/content/independent를 현재 자료·해시·소문항별로 기록한다. 로컬 서버에서 1280×900·375×812, light/dark의 모든 문항·목차·이전/다음·요약·수식·코드·그림·링크를 확인한다. stage 링크의 최종 발행 경로와 anchor도 대조한다. 콘솔/KaTeX/누락 자원/외부 요청/문서 overflow가 0일 때만 browser pass. 합성 browser_acceptance 결과를 실자료 승인으로 재사용하지 않는다. 서버를 종료한다.
- [x] **Step 7: 팩별 publish와 기록.** 실제 네 검토가 pass이면 `python3 ABS_EXPLAIN_CLI publish --run EXPLAIN_RUN`을 실행한다. 예상: 종료 코드 0과 publish/backup 경로. 최종 경로에서 자원·링크·문항 수·manifest/source_sha256·protected_files를 다시 확인한다. 1012의 교체된 파일은 실제 백업 bytes를 대조하여 replacements와 backup_sha256을 기록한다. 자료_복습팩의 과거 기록은 보존한다. 보류 팩은 기존 해설을 유지하고 이유를 기록한다. 이 Step 2~7 주기를 팩마다 마친 뒤 다음 날짜로 진행한다.
- [x] **Step 8: 납품 검사.** JSON을 Task 2 계약으로 저장하고 `P -m pytest .agents/skills/ds-review-pack/tests/test_problem_explain_delivery.py .agents/skills/ds-review-pack/tests/test_textbook_delivery.py -q`를 실행한다. 예상: 9팩 전체 발행이면 PASS; 보류가 있으면 납품 실패를 완료로 표현하지 않고 이유를 해결한다. Python 환경에 교과서 검사 의존성이 필요한 경우 기존 DS_TEXTBOOK_PYTHON 설정을 재사용한다.
- [x] **Step 9: 최종 회귀와 자체 검토.** 각 별도 프로세스에서 `P -m pytest .agents/skills/ds-review-pack/tests -q`, `P -m pytest .agents/skills/ds-problem-explain/tests -q`를 실행한다. 요구 검사가 skip된 경우 해당 사유를 기록하고 필요한 환경에서 수행한다. `git diff --check`와 실제 원본 해시 보존을 확인한다. JSON 사실만 근거로 MD에 날짜별 문항 수·검토 결과·원문 충돌·보류·RUN/백업 경로를 적는다.
- [x] **Step 10: 결과 제시.** 9팩 64문항 전체의 성공 여부와 HTML 링크를 보고한다. 승인된 경우의 커밋 제안: `docs(notes): add verified explanations for existing ds review packs`. 원문과 과거 제작자료가 변경되지 않았는지 staging 전에 다시 확인한다.

## 자체 검토 결과

- 설계 대응: 자동 연결/모드/실패 처리는 Task 1, 과거 보존과 최신성 검사는 Task 2, 기존 전 팩과 실자료 검증은 Task 3에 대응한다.
- 인터페이스: 실제 설명 CLI는 재사용하고, 두 helper와 발행 JSON은 Task 2에서 정의해 Task 3가 사용한다.
- 테스트 범위: 다섯 Review Focus 모두 기존 회귀 검사·신규 fixture·실자료 검사에 배정했다. 안내 문구만 따라 하는 테스트는 추가하지 않는다.
- 작업 분리: 문서 연결은 즉시 검토 가능하고, 납품 검사는 fixture로 검토 가능하며, 실자료 작업은 날짜별 결과로 검토 가능하다.
- 실행 전에는 이 문서의 체크박스를 완료로 표시하지 않는다. 계획 작성 중 코드 변경·해설 저작·발행·커밋은 수행하지 않는다.

## 실행 방식 추천

Native를 추천한다. 실행기 변경 없이 안내 문서를 연결하고 기존 9팩에 동일한 절차를 반복하므로, 한 실행자가 자료·검증 상태를 이어서 관리하기 쉽다. 작업 종료 후 독립 리뷰어가 전체 변경과 납품 기록을 확인한다. Subagent-driven을 선택하면 작업별 구현자·리뷰어를 사용하되 실제 검토 없이 pass 기록을 만들어서는 안 된다. 두 방식 모두 기존 스킬이 요구하는 문항 작성/독립 검토 역할은 지킨다.

실행 중 예외는 설계의 “실행 중 확인한 최소 예외”와 Native ledger에 기록했다. 과거 이식 bytes/hash 항목을 바꾸지 않고 삽입만 역복원 가능한 local_overrides로 기록했다. 검증된 교체 예외는 보고서 digest 문자열뿐 아니라 실제 백업 bytes까지 확인한다.
