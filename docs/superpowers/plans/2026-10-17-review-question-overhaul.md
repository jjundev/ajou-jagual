# 복습문제 전면 개편 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 전체 복습문제의 중복을 제거하고 강의 예제 코드 문제를 직접 추가하며 생성 스킬과 검증기로 재발을 막는다.

**Architecture:** 기존 HTML 카드·manifest와 강의·기출·교과서 출처를 유지하면서 전체 팩을 비교하는 검증기를 추가한다. 강의 코드 출처 계약을 먼저 구현하고, 개편 전용 갱신 흐름에서 날짜별 문제를 재작성한 뒤 기존 문제설명·PDF 절차로 전체 산출물을 갱신한다. 자동 유사도는 검토 후보만 제시하고 실제 출제와 의미 판정은 작성자가 수행한다.

**Tech Stack:** Python 3.10+, 기존 HTMLParser/pytest, PyMuPDF, C11 컴파일러, 기존 Playwright/Google Chrome, 로컬 HTML·MD·JSON·PDF.

**Spec:** `docs/superpowers/specs/2026-10-17-review-question-overhaul.md` — 사용자 승인 설계와 #7 확정값.

## Global Constraints

- **핵심 범위 충족 우선**, 보통 8~12개를 목표로 하되 부족하면 적게, 필요하면 초과한다.
- 문제 수를 채우기 위한 숫자 변형은 만들지 않는다.
- 같은 원문과 숫자만 바꾼 변형의 재사용은 날짜 전체에서 차단한다.
- 같은 개념이어도 평가 능력이 다르면 허용한다.
- 검토 기준 `review-questions-2026-10-17`을 기록한다.
- 정리노트 본문·MD·기존 그림, STT, 강의록, 기출·교과서 원본은 보존한다.
- 날짜 폴더·slug·현재 파일명을 유지한다. 루트 HTML 3개·PDF 2개, 보조 파일은 `.pack/`에 둔다.
- 미검토를 pass로 기록하지 않는다. 커밋·푸시는 자동으로 하지 않는다.

## Review Focus

- 미완성 전체 개편: 먼저 수정한 팩만 비교해 중복을 놓치지 않는다. stage overlay와 아직 수정하지 않은 실파일을 함께 검사한다(Task 3).
- 한글/NFD 경로·backup 복사본: 같은 실제 팩을 두 번 세거나 숨김 제작자료의 복사본을 문제로 세지 않는다(Task 1).
- 상수·변수명 변경: 서로 다른 출처 ID의 사실상 같은 문제를 탐지하고 서로 다른 평가 능력은 이유를 기록해 구분한다(Task 3).
- 문제 번호 변경: 이전 pN의 풀이 완료 상태와 PDF 작성용 표가 새 문제에 붙지 않는다(Task 4).
- 낡은 검토 기록: 과거 retrofit의 카드 보존 기록·해설·PDF 승인이 변경된 내용의 승인으로 통과하지 않는다(Task 6).

---

## 파일 구조와 책임

| 파일 | 역할 |
|---|---|
| `.agents/skills/ds-review-pack/scripts/review_inventory.py` (신규) | 실제 날짜 폴더 HTML·manifest의 전체 카드 추출과 불일치 진단 |
| `.agents/skills/ds-review-pack/scripts/lecture_sources.py` (신규) | 강의 코드 출처·페이지·해시·학습 근거 검사 |
| `.agents/skills/ds-review-pack/scripts/review_audit.py` (신규) | 전체 날짜의 원문 계열·내용·유사 후보·검토 판정 검사 CLI |
| 기존 `manifest.py`, `bank.py`, `check_html.py` | lecture-code 계약과 팩·전체 검증 연결 |
| 기존 `update_review.py`, `assemble.py`, `assets/review-template.html` | 전체 개편 stage와 내용 버전별 풀이 상태 |
| 기존 `pdf_cards.py` | 강의 출처 표기와 source 기반 작성용 표 판별 |
| `references/review-overhaul.md` (신규), 기존 스킬·참조 문서 | revise-existing 및 신규·기존 모드의 필수 검사 |
| `.agents/skills/ds-review-pack/tests/test_review_{inventory,audit,overhaul,delivery}.py` (신규) | 추출·전체 검사·개편·실제 납품 회귀 검사 |
| `.agents/skills/ds-review-pack/tests/test_lecture_sources.py` (신규) | 강의 출처·실패 경계 검사 |
| `복습노트/<날짜>/` 및 `.pack/` | 실제 10개 팩의 수정 문제와 파생 산출물 |
| `docs/verify/2026-10-17-review-question-overhaul.{json,md}` (신규) | 전 문항 판정·범위·검증·백업·최종 상태 보고 |

`update-existing`는 기존 교과서 추가 동작을 유지한다. `.claude/skills/ds-review-pack`과 `ds-problem-explain`은 `.agents`를 가리키는 심볼릭 링크이므로 복제본을 만들지 않는다.

### Task 1: 실제 전체 문항 목록과 개편 기준선

**Files:** Create `scripts/review_inventory.py`, `tests/test_review_inventory.py`(위 ds-review-pack 기준); 실제 기준선은 고유 RUN의 `baseline.json`에 저장.

**Interfaces:** `collect_reviews(repo: Path, *, overlays: dict[str, Path] | None = None) -> list[dict]`. 반환 행은 `range`, `review_path`, `manifest_path`, `source_sha256`, `cards`를 가지며 카드는 `id`, `source`, `source_kind`, `statement_html`, `original_html`, `content_sha256`을 갖는다. 손상·모호함·HTML/manifest 불일치는 `ValueError`다. overlay는 range별 stage HTML이며 manifest는 같은 stage의 명시적 제작자료 경로를 사용한다.

- [x] **Step 1: 실패 테스트 작성.** `test_root_reviews_only_nfd_and_overlay`는 날짜 폴더의 NFC/NFD 이름을 읽되 `.pack/`·backup의 HTML은 제외하고 overlay는 해당 팩만 대체함을 단언한다. `test_manifest_card_mismatch_fails`는 누락·추가·source 불일치를 각각 거부한다.

  ```python
  rows = collect_reviews(repo, overlays={"0917": staged_review})
  assert [r["range"] for r in rows] == ["0914", "0917"]
  assert rows[1]["review_path"] == str(staged_review.resolve())
  with pytest.raises(ValueError, match="manifest"):
      collect_reviews(repo_with_source_mismatch)
  ```
- [x] **Step 2: 실패 확인.** `python -m pytest .agents/skills/ds-review-pack/tests/test_review_inventory.py -q` → 미구현 import 실패.
- [x] **Step 3: 인터페이스 구현.** 기존 `html2md.Builder`로 DOM을 읽고 질문·코드·보기·그림을 포함한 해시를 계산한다. 강의/원문/힌트/풀이 영역은 질문 해시에서 분리한다. `pack_layout.pack_folders`의 날짜 폴더 선택 규칙을 따른다.
- [x] **Step 4: 통과·기준선 확인.** 같은 테스트 PASS. 실제 입력에서 10팩·72문항을 확인하고 전체 입력 파일 해시·기존 산출물 경로를 baseline에 저장한다. 기준선이 달라졌으면 최신 실제 목록으로 기록하고 이유를 보고한다.

### Task 2: 강의 코드 출처 계약을 끝까지 전달

**Files:** Create `scripts/lecture_sources.py`, `tests/test_lecture_sources.py`; Modify `scripts/{manifest,bank,check_html,pdf_cards}.py`; Extend `tests/{test_manifest,test_bank,test_check_html,test_pdf_cards}.py`; add lecture fixture to explanation `tests/test_source.py`.

**Interfaces:** `validate_lecture_source(repo: Path, problem: dict, sessions: list[dict]) -> list[str]`; `bank.check_manifest(bank: dict, manifest: dict, *, textbook=None, repo: Path | None = None) -> list[str]`(기존 인자 유지). `lecture_ref={path,pdf_page,sha256,example,taught_on}`와 `objectives: list[str]`, `task_family: str`를 lecture-code에 필수화한다. `source`는 `lecture-sNN-pN-<example>` 형식이다.

- [x] **Step 1: 실패 테스트 작성.** `test_lecture_reference_valid`는 실제 임시 2쪽 PDF의 2쪽·현재 SHA·수업 날짜를 받아 빈 오류 목록을 요구한다. `test_reference_rejects_missing_stale_outside_or_future`는 누락 파일·해시 불일치·저장소 밖 경로·페이지 0/3·미학습 날짜를 거부한다. 기존 past-exam 생략 필드·textbook 검증은 그대로 통과해야 한다.

  ```python
  assert validate_lecture_source(repo, valid_question, sessions) == []
  for page in (0, 3):
      invalid = copy.deepcopy(valid_question)
      invalid["lecture_ref"]["pdf_page"] = page
      assert validate_lecture_source(repo, invalid, sessions)
  assert bank.check_manifest(old_bank, legacy_manifest) == []
  ```
- [x] **Step 2: 실패 확인.** 관련 다섯 테스트 모듈 실행 → 신규 출처 또는 인터페이스 미지원 실패.
- [x] **Step 3: 최소 구현.** manifest 형식 검사와 실제 근거 검사를 분리한다. `bank.py check-manifest --repo REPO`를 지원하고 lecture-code에는 repo 없이 성공하지 않는다. HTML의 source-kind와 원문 표지를 대조하고 PDF kind는 `강의 코드`로 전달한다. 자체 소문항은 원 강의 예제에 없는 소문항 표지와 충돌하지 않게 원문 영역과 분리한다.
- [x] **Step 4: 통과 확인.** 위 테스트와 `.agents/skills/ds-problem-explain/tests/test_source.py` PASS. 신규 fixture의 질문·소문항·코드가 해설 추출에서 그대로 유지되는지 단언한다. 이때 해설 실행기가 이미 지원하면 변경하지 않는다.

### Task 3: 전체 날짜 중복 검사와 현재 입력에 묶인 검토 기록

**Files:** Create `scripts/review_audit.py`, `tests/test_review_audit.py`; Modify `scripts/bank.py`의 팩 내 동일 source 재사용 검사와 CLI.

**Interfaces:** `audit_reviews(repo: Path, *, overlays: dict[str, Path] | None = None, decisions: list[dict] | None = None) -> dict`. 보고서 필드는 `policy_version`, `inputs`, `blocking`, `candidates`, `decisions`, `status`. 판정은 두 카드의 range/id/content hash, `decision=duplicate|distinct`, `reason`, `evidence`를 갖는다. CLI `review_audit.py --repo REPO [--overlay overlay.json] [--decisions decisions.json] --out report.json`; pass=0, 차단/미판정/손상=1이다.

- [x] **Step 1: 실패 테스트 작성.** `test_global_sources_and_variants_blocked`는 서로 다른 날짜의 동일 원문·duplicate_of·variant true 중복을 거부한다. `test_cross_source_numeric_and_identifier_candidate`는 다른 source의 상수·변수명만 다른 코드가 후보가 됨을 단언한다. `test_distinct_objectives_need_current_decision`는 근거 있는 distinct만 후보를 해소하고 내용 변경 후 옛 판정을 거부한다. `test_overlay_keeps_unmodified_packs_in_scope`는 stage 한 팩과 실파일 다른 팩의 중복도 잡는다.

  ```python
  assert audit_reviews(repo_with_numeric_variant)["status"] == "fail"
  assert audit_reviews(repo_with_cross_source_clone)["candidates"]
  current = audit_reviews(repo_with_distinct_tasks, decisions=current_decisions)
  assert current["status"] == "pass"
  assert audit_reviews(changed_task_repo, decisions=current_decisions)["status"] == "fail"
  ```
- [x] **Step 2: 실패 확인.** `python -m pytest .agents/skills/ds-review-pack/tests/test_review_audit.py -q` → 미구현 실패.
- [x] **Step 3: 검사 구현.** canonical source와 실제 질문 동일성은 blocking이다. C 토큰에서 식별자·숫자를 순서에 따라 정규화한 구조 및 숫자를 정리한 질문으로 후보를 제시한다. 문자열 literal·연산자·괄호 순서를 보존한다. 동일 code만으로 중복 확정하지 않는다. 숫자 변형은 검토로 우회할 수 없고 같은 원문은 한 번만 쓴다.
- [x] **Step 4: 통과와 현행 탐지 확인.** 테스트 PASS. 실제 baseline 검사에서 6개 source 계열·13회 추가 사용이 진단되며 PASS가 아니어야 한다. 신규 후보는 사람이 전 문항 판정에서 검토한다. 보고서에 대상 전체 입력 해시를 포함한다.

### Task 4: 개편 stage·풀이 상태·PDF 표의 문항 식별 보강

**Files:** Modify `scripts/{update_review,assemble,pdf_cards}.py`, `assets/review-template.html`; Create `tests/test_review_overhaul.py`; Extend `tests/{test_update_review,test_assemble,test_pdf_cards,test_pdf_ds_layout}.py`.

**Interfaces:** `build_revision(existing_html: str, *, manifest: dict, cards: dict[str, str]) -> str`와 `revision_hash(manifest: dict, cards: dict[str, str]) -> str`를 `update_review.py`에 추가한다. 원문 shell의 허용 변경은 title/meta/hero/main sections/TOC/footer/body 내용 버전/복습문제 저장 키다. 기존 `build_update`의 보존 계약은 유지한다.

- [x] **Step 1: 실패 테스트 작성.** `test_revision_replaces_removes_and_reorders_cards`는 p1..pN·part·source·목차가 새 manifest와 같고 노트 링크·스타일·패널 동작은 보존됨을 단언한다. `test_revision_idempotent_and_changes_state_namespace`는 동일 입력의 결과 동일성, 내용 변경의 버전 변경, 테마·note-read 키 불변을 확인한다. `test_pdf_worksheet_uses_source_not_pn`는 기존 두 postfix 원문의 번호가 바뀌어도 표가 작성 공간에 있고 새 p2가 참고 표면 이동하지 않음을 단언한다.

  ```python
  revised = build_revision(old_html, manifest=m, cards=cards)
  assert build_revision(revised, manifest=m, cards=cards) == revised
  assert revision_hash(m, cards) != revision_hash(m, changed_cards)
  assert [c["source"] for c in extract_cards(revised)] == [q["source"] for q in m["problems"]]
  ```
- [x] **Step 2: 실패 확인.** 새 테스트 및 연결 테스트 실행 → 신규 API/출처 기반 표 판별 실패.
- [x] **Step 3: 구현.** 기존 Spans를 사용해 허용 구역만 교체한다. 풀이 저장 키는 `od-review-solved:<range>:<revision>`이며 구버전은 읽지 않는다. 신규 생성은 `assemble.build_review`도 같은 revision을 만든다. PDF 표는 `2018-mid-c024-q9`, `2017-mid-c050-q6` source로 판별한다. 정리노트의 setupReview는 실행 경로가 아니므로 정리노트 파일을 바꾸지 않는다.
- [x] **Step 4: 통과 확인.** 관련 단위 검사 PASS. 브라우저 fixture에 구 key의 `[p1]`을 넣은 뒤 교체된 새 p1은 미완료이고 새 완료 표시는 재로드 뒤 유지되는지 확인한다.

### Task 5: 생성 스킬에 전면 검토 모드와 필수 게이트 반영

**Files:** Create `references/review-overhaul.md`; Modify `SKILL.md`, `references/{problem-selection,manifest-guide,card-rules,review-prompt,textbook-update,problem-explain,pdf-build}.md`; Extend `tests/test_skill_files.py`.

**Interfaces:** `/ds-review-pack revise-existing [MMDD|all] [lite]`. 기존 신규·update-existing·bank 인자는 유지한다. bank는 전면 개편을 실행하지 않는다. 신규·update-existing·revise-existing은 manifest→출처→팩 HTML→전체 audit→실화면→MD→해설/PDF 순서로 검사한다.

- [x] **Step 1: 회귀 검증 작성.** `test_revision_workflow_requires_full_audit_and_lecture_evidence`는 세 모드가 같은 실제 CLI 게이트와 정확한 최종 HTML 경로를 쓰는지 확인한다. `test_coverage_policy_does_not_require_variants_or_fixed_count`는 전면 검토가 출제 수를 강제하거나 기출 변형으로 부족을 채우지 않음을 확인한다. 강의 PDF 부재·후보 부족·미학습 예제라는 세 시나리오에서 실제 audit/출처 검증 실패와 문서의 처리 지침을 대조한다.

  ```python
  skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
  overhaul = (SKILL / "references/review-overhaul.md").read_text(encoding="utf-8")
  assert "revise-existing" in skill
  assert "review_audit.py" in overhaul
  assert "핵심 범위 충족 우선" in overhaul
  assert validate_lecture_source(repo, future_question, sessions)
  ```
- [x] **Step 2: 실패 확인.** `python -m pytest .agents/skills/ds-review-pack/tests/test_skill_files.py -q` → 새 모드/지침 없음 실패.
- [x] **Step 3: 문서 수정.** 자작 문제 금지를 강의 예제 근거 출제 허용으로 바꾸고 출처·저작 브리프·검산·coverage·판정·백업·복구 절차를 적는다. update-existing의 카드 보존과 revise-existing의 교체를 명확히 구분한다. lite에도 중복·출처·해설·PDF 검증은 생략하지 않는다.
- [x] **Step 4: 통과·상충 지침 확인.** 테스트 PASS. 전체 스킬에서 `자작 문제 금지`, `8개로 맞춘다`, `변형 규칙` 등 남은 상충 문구와 두 출처만 허용하는 지침을 검색해 적용 모드에 맞게 수정한다. writing-skills의 실패 시나리오 검증도 수행하고 기록한다.

### Task 6: 10개 팩의 문항 판정·출제·검산·리뷰 발행

**Files:** 각 `복습노트/<날짜>/복습문제_<날짜>_<slug>.html`, `.pack/복습문제_<날짜>_<slug>.md`, `.pack/자료_복습팩/{manifest,selection,validation}.json`, `answers.py`; Create `tests/test_review_delivery.py`; Update mode별 분기를 위해 `tests/test_textbook_delivery.py`.

**Interfaces:** selection의 `mode=revision`, `policy_version`, `selected`(최종 전 문항), `excluded`, `coverage`, `replacements`, `duplicate_decisions`. validation은 `before_hashes`, `after_hashes`, `checks`, `unresolved`, `preserved`를 갖는다. 개편 전 자료는 고유 RUN backup과 `baseline.json`으로 보존한다. 과거 문서·검토 보고서는 고치지 않는다.

- [x] **Step 1: 실제 납품 검사 작성.** `test_all_packs_current_revision_and_complete_coverage`는 10팩의 HTML/manifest/selected ID 일치와 모든 핵심 목표의 문항 또는 제외 근거를 확인한다. `test_every_changed_card_has_mapping_and_verification`는 이전 72문항 전부에 판정·대응이 있고 최종 모든 답에 pass 근거가 있음을 확인한다. `test_legacy_retrofit_still_validated`는 예전 fixture의 4~8개 추가·카드 보존 검사도 유지한다. 실제 revision 분기는 새 규칙으로 검사하며 단순 skip을 추가하지 않는다.

  ```python
  assert selection["mode"] == "revision"
  assert selection["policy_version"] == "review-questions-2026-10-17"
  assert [q["id"] for q in selection["selected"]] == [q["id"] for q in manifest["problems"]]
  assert all(q["verification"]["result"] == "pass" for q in selection["selected"])
  assert audit_reviews(REPO, decisions=current_decisions)["status"] == "pass"
  ```
- [x] **Step 2: 실패 확인·입력 보호.** 납품 검사에서 현행 old mode 실패 확인. git 상태와 보호 대상 해시를 baseline에 기록하고 10개 팩의 기존 리뷰·해설·PDF·제작자료를 고유 RUN에 백업한다. 쓰기 전 각 절대 경로가 해당 날짜 폴더 또는 RUN 안인지 확인한다.
- [x] **Step 3: 전 문항 판정과 범위 확인.** 날짜 오름차순으로 기존 질문·전체 소문항·실제 슬라이드·STT·정리노트를 읽고 유지/이동/통합/교체와 이유를 정한다. 코드 예제별 coverage와 아직 배우지 않은 개념을 기록한다. 0907은 코드 부재를 허용하며 0914에 뒤 날짜 재귀 예제를 소급하지 않는다.
- [x] **Step 4: 직접 출제와 답 작성.** 앞 spec의 예제 후보를 바탕으로 핵심 코드 동작을 묻고 같은 원문·풀이 절차는 반복하지 않는다. 기출·교과서의 유효 원문은 보존하고 강의 예제의 자체 질문·원문·harness 변경을 구분한다. 풀이와 힌트는 각 카드만으로 이해할 수 있게 작성한다.
- [x] **Step 5: 독립 검산.** 팩별 answers.py와 C11 검증 코드를 RUN에 작성·실행하고 결과를 보관한다. 컴파일 경고·오류·입력 가정·UB를 점검한다. 다중 정답 구현은 한 코드 문자열 일치로 채점하지 않는다. 틀린 문제·답을 고친 뒤 재실행한다.
- [x] **Step 6: stage 전체 검증.** 10팩 overlay로 manifest·출처·check_html·audit를 실행한다. `blocking=[]`, 미판정 후보 0, current input hash 일치가 필요하다. 최종 전체 문항을 의미상으로도 검토한다. 1280×900/375×812 light/dark의 원문·힌트·풀이·목차·pager·링크·긴 코드 스크롤을 실제 확인한다.
- [x] **Step 7: 리뷰·MD 발행.** `html2md.py REVIEW --check` 단일 리뷰 변환만 사용한다. source 변경 검사와 rollback이 있는 publish_update로 팩별 발행하며, 실패 팩은 보고하고 독립 팩은 계속한다. 관련 단위·실제 납품 검사 PASS, 정리노트·그림·원자료 해시 불변을 확인한다.

### Task 7: 전체 문제설명·PDF 갱신과 최종 납품 검사

**Files:** 10개 팩의 `문제설명_*.html`, `.pack/문제설명_*.md`, `.pack/자료_문제설명_*`, `복습문제_*-문제.pdf`, `복습문제_*-답안.pdf`, `.pack/자료_PDF/pdf-validation.json`; Create `docs/verify/2026-10-17-review-question-overhaul.{json,md}`; Extend `tests/test_review_delivery.py`와 기존 해설 delivery helpers의 현재 보고서 선택.

**Interfaces:** 기존 `mpe_cli.py extract/build/check/publish`, `review_pdf.py build/check/publish`를 그대로 사용한다. 입력은 매 팩의 최종 REVIEW 절대 경로다. 최종 보고서에 range/source hash/problem IDs·문항 수·중복 판정·coverage·검산·브라우저·해설/PDF status·backup/run을 기록한다.

- [x] **Step 1: stale 검증 작성.** `test_delivery_rejects_old_explanation_or_pdf_approval`는 원 리뷰 해시가 다르거나 문항 ID가 빠진 해설·PDF, stage 변경 후 옛 승인을 거부한다. `test_delivery_reports_all_ten_packs`는 1015 포함 10팩 모두에 published 또는 구체적 보류 원인이 있어야 하며 완료 판정은 전 팩 published일 때만 참이다.

  ```python
  assert explanation_manifest["source_sha256"] == digest(review)
  assert pdf_validation["source_sha256"] == digest(review)
  assert explanation_ids == review_ids
  assert {p["range"] for p in report["packs"]} == {"0907", "0914", "0917", "0921", "0928", "1001", "1005", "1008", "1012", "1015"}
  ```
- [x] **Step 2: 실패 확인.** 새 납품 검사를 실행해 변경 후 기존 해설/PDF가 통과하지 않음을 확인한다. 과거 보고서를 새 source에 맞게 덮어써서 통과시키지 않는다.
- [x] **Step 3: 전체 문제설명 재저작·검산.** ds-problem-explain의 저작·검증 지침을 읽고 모든 최종 질문의 이해→회상→첫 줄→풀이→검산→함정→재도전과 각 소문항을 작성한다. 입력이 같은 유지 문항만 기존 설명을 근거 대조 후 재사용한다. 현재 입력 해시로 네 검토를 실제 수행한 뒤 팩별 publish한다.
- [x] **Step 4: PDF build/check·모든 페이지 검토.** 기존 pdf-build 절차와 실제 로컬 런타임으로 문제·답안 PDF를 만든다. 코드·표·그림·풀이 누락과 문제지 정답 노출을 확인하고 현재 report/artifact hash에 연결된 review를 작성한 후 publish한다. 실패하면 이전 파일을 보존하고 stale 이유를 기록한다.
- [x] **Step 5: 최종 검증.** 두 스킬의 pytest 전체를 각각 별도 프로세스로 실행해 import 충돌을 피한다. 실제 source hash·전체 ID 일치·PDF 전체 페이지 확인·전체 중복 0·미판정 후보 0·보호 파일 해시 불변을 확인한다. `python .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo .` → OK. 변경한 모든 팩에서 재실행 동일성을 확인한다.
- [x] **Step 6: 보고.** 날짜별 전/후 문항 수·제거/통합/이동·강의 코드 신규 수·대표 예제와 범위·검증 결과·백업·미해결을 JSON/MD에 기록한다. git diff --check와 status로 의도한 변경만 있는지 확인한다. 실제 실행하지 않은 검사를 완료로 적지 않는다. 커밋은 제안만 한다.

## 검증 명령

저장소 루트에서 실행한다. Windows에서는 `python`과 발견한 C11 컴파일러 절대 경로를 사용한다. 도구가 없으면 실제 오류를 보고하고 검증되지 않은 결과를 발행하지 않는다.

```powershell
python -m pytest .agents/skills/ds-review-pack/tests -q
python -m pytest .agents/skills/ds-problem-explain/tests -q
python .agents/skills/ds-review-pack/scripts/review_audit.py --repo . --decisions "<최종 판정 JSON 절대경로>" --out "<최종 audit JSON 절대경로>"
python .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo .
git diff --check
```

## 자체 검토와 실행 인계

- 설계의 중복 제거·코드 출제·범위·가변 문항 수·상태·해설/PDF·보호·백업·재발 방지 요구를 Tasks 1–7에 대응했다.
- Review Focus의 다섯 실패 조건은 각각 Task 1/3/4/6/7의 검증 항목으로 연결했다.
- 설명과 PDF는 기존 실행기를 재사용하며 새 시스템을 만들지 않는다. 해설 source 처리의 변경은 신규 fixture가 실패하는 경우에만 한다.
- 자동 커밋은 로컬 ds-review-pack의 지침에 따라 생략하고 최종 제안만 한다.
- 권장 실행 방식은 Native다. 공유 manifest·실제 수업 범위·문항 판정·현재 산출물 해시가 작업 전체에 이어지므로 한 구현자가 순서대로 처리하는 편이 인계가 적다. 독립 리뷰가 필요하면 확정된 사용자 실행 방식과 현재 사용 가능한 도구 범위에서 수행한다.
- writing-plans의 Execution Handoff에 따라 계획 검토와 실행 방식 선택 후 구현을 시작한다. 이 문서의 체크박스는 실제 수행한 작업만 체크한다.
