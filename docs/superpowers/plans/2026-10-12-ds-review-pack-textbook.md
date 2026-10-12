# 기출·교과서 통합 복습문제 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ds-review-pack이 기출과 교과서 문제를 함께 선별하고, 기존 9개 팩에 기존 문제를 보존하면서 교과서 원문 4~8개씩 추가한다.

**Architecture:** 기출 bank.py는 유지하고 교과서 검증/장 대응을 담당하는 좁은 어댑터를 추가한다. source_kind와 namespaced ID로 manifest와 검사를 확장한다. 기존 팩은 raw 카드 보존 갱신기로 업데이트하고 날짜별 선별·정답·검증 자료를 보관한다.

**Tech Stack:** Python 3.10+, unittest, HTML/CSS/JavaScript, 기존 교과서 검증기의 jsonschema/PyMuPDF, C11 compiler, 로컬 브라우저 검증.

**Spec:** `docs/superpowers/specs/2026-10-12-ds-review-pack-textbook-design.md`

## Global Constraints

- 기존 문제는 유지하고 교과서 원문 4~8개씩 추가한다. 기본 4개, 개념 커버리지가 필요한 경우 최대 8개. 기존 팩에는 총 12개 상한을 적용하지 않는다.
- 새 팩은 총 8~12개, 적합한 후보가 있으면 교과서 원문 최소 2개. 원문 선별을 먼저 하고 기존 기출 숫자 변형 규칙을 적용한다.
- 날짜는 0907, 0914, 0917, 0921, 0928, 1001, 1005, 1008, 1012이고 순서대로 갱신한다.
- STT/강의록의 실제 학습 범위를 지킨다. 예고·보충·장 번호만으로 문제를 허용하지 않는다.
- 기출/교과서 원본과 기존 정리노트 HTML/MD, 기존 문항 id/source/raw HTML, 기존 문제설명 파일을 보존한다.
- source_kind 생략은 past-exam, 교과서 ID는 textbook-chNN-qNN, 새 part는 partD이다.
- 교과서 verified는 원문 검수이며 정답 검증이 아니다. 선택한 문항마다 정답·풀이를 별도로 검증한다.
- 적합한 원문이 4개 미만이면 가능한 만큼만 추가하고 미해결을 보고한다. 원문 중복 사용이나 범위 확장으로 수를 채우지 않는다.
- 1280×900/375×812와 light/dark에서 9개 팩을 검증한다. 콘솔·KaTeX 오류, 누락 자원, 문서 가로 넘침은 0.
- 새로운 런타임 의존성은 추가하지 않는다. 교과서 검증기의 기존 의존성이 필요한 경우 실행 인터프리터를 명시한다.
- 구현은 실행 인계 후 시작한다. 커밋·푸시는 별도 사용자 요청 없이는 실행하지 않으며 각 task의 commit은 제안으로만 기록한다.

## Review Focus

1. 장 번호가 다른 스택/큐·배열 리스트: 매핑이 미학습 연결 리스트·응용 문항을 허용하지 않아야 한다 — Tasks 1, 5.
2. verified이지만 null 정답/외부 문맥/선행 문제 의존: 구조 통과를 정답·독립 풀이 가능성으로 오인하지 않아야 한다 — Tasks 1, 5.
3. 두 bank.py 모듈과 NFD 경로/오래된 해시: 모듈 혼선·경로 누락·검토 승인 재사용을 거부해야 한다 — Task 1.
4. 여러 카드의 SVG ID/정답 노출: 모든 내부 참조와 흰 배경을 유지하고 새 그림에 답을 넣지 않아야 한다 — Tasks 2, 6.
5. 0문항 팩/기존 문제설명/재실행·발행 실패: 기존 문항·링크·읽음 키를 보존하고 partD 중복 없이 복구해야 한다 — Tasks 3, 6.

---

## 파일 구조와 책임

기준 폴더 S는 `.agents/skills/ds-review-pack`이다. 실제 한글 경로는 NFC로 검색하고 발견한 Path를 사용한다.

- Create `S/scripts/textbook.py`: 현재 교과서 검증기를 별도 프로세스로 호출해 import 이름 충돌을 피하고, catalog·장/문항 대응·후보를 제공한다.
- Modify `S/scripts/bank.py`: 선택/출처 검사에 optional 교과서 catalog를 연결한다. 기존 기출 API를 보존한다.
- Modify `S/scripts/manifest.py`, `check_html.py`: 출처 종류와 ID, partD, 정답 검증 자료 계약을 검사한다.
- Create `S/scripts/textbook_blocks.py`: 순서 있는 content/options와 검토된 SVG의 HTML 표현 및 ID 재지정만 담당한다. 정답을 작성하지 않는다.
- Create `S/scripts/update_review.py`: 기존 카드 raw HTML 추출, 교과서 구역 교체, 기존 카드 보존·재실행·발행 복구를 담당한다.
- Modify `S/scripts/html2md.py`: 단일 review 변환 및 기존 SVG 경로 충돌 처리를 검증한다. 기존 NOTE REVIEW CLI도 유지한다.
- Modify `S/SKILL.md`, `references/{problem-selection,manifest-guide,card-rules,review-prompt}.md`, `assets/review-template.html`: 확정한 두 출처 계약, 기존 팩 갱신 모드, 중립 문구를 동기화한다.
- Create `S/tests/test_textbook.py`, `test_textbook_blocks.py`, `test_update_review.py`, `test_textbook_delivery.py`; Modify `test_bank.py`, `test_manifest.py`, `test_check_html.py`, `test_html2md.py`, `test_skill_files.py`.
- Modify 9개 `복습노트/<range>/복습문제_<range>_<slug>.html/.md`; 필요하면 새 SVG 파일만 추가한다.
- Create 날짜별 `복습노트/<range>/자료_복습팩/{manifest.json,selection.json,answers.py,validation.json}`와 전체 `docs/verify/2026-10-12-ds-review-pack-textbook.md`.

## 공통 데이터 계약

`TextbookCatalog` dataclass는 `package: Path`, `questions: dict[str,dict]`, `chapters: dict[str,dict]`, `sources: dict[str,dict]`, `assets: dict[str,dict]`를 가진다. questions 키는 원본 chNN-qNN이다.

교과서 후보는 원본 question 필드를 보존하고 `id: textbook-chNN-qNN`, `question_id: chNN-qNN`, `source_kind: textbook`, `chapters: list[int]`(강의록 번호), `type: str`(원본 kind), `answer: None`을 가진다. choice/mixed를 기존 기출 유형으로 강제 변환하지 않는다. 새 카드 level은 객관식/단순 확인=1, 추적/코드 읽기/단답=2, 구현/논술=3이며 mixed는 실제 요구 중 최고 난이도를 사용한다.

selection.json은 `range`, `mode: retrofit|new`, `taught_evidence`, `concept_overrides`, `selected`, `excluded`를 가진다. selected의 각 항목은 `id`, `source`, `source_kind`, `original_id`, `prerequisites`, `evidence`(path/locator/sha256), `answer`, `verification`(method/reference/result)을 가진다. excluded는 source/reason이다. concept_overrides는 question ID→강의록 번호 목록이며 반드시 같은 문항의 강의 근거를 가진다. 검산 methods는 python, c-run, lecture-reference이고 result는 pass|blocked이다.

validation.json은 checks(검사별 결과), counts(existing/added/total), preserved(기존 문항/노트/문제설명 해시 결과), unresolved를 가진다. 실패/미실행을 pass로 저장하지 않는다. 이를 manifest의 선택 문항과 대조한다.

### Task 1: 교과서 catalog와 기출 호환 선별

**Files:** Create `S/scripts/textbook.py`, `S/tests/test_textbook.py`; Modify `S/scripts/bank.py`, `S/tests/test_bank.py`.

**Interfaces:**
- Consumes: `교과서/제작자료/scripts/validate.py PACKAGE --complete`, 현재 장별 JSON과 기출 `load/select/check_manifest`.
- Produces: `load_textbook(package: Path, *, python: str) -> TextbookCatalog`; `course_chapters(chapter: int) -> set[int]`; `textbook_candidates(catalog: TextbookCatalog, range_ch: set[int], taught: set[int], used: set[str], *, concept_overrides: dict[str,list[int]] | None = None) -> list[dict]`.
- Produces: `bank.select(bank: dict, range_ch: set[int], taught: set[int], used=frozenset(), *, textbook: TextbookCatalog | None = None, concept_overrides=None) -> list[dict]`; `bank.check_manifest(bank: dict, manifest: dict, *, textbook: TextbookCatalog | None = None) -> list[str]`.

- [ ] Step 1: Add unittest cases `test_stack_maps_4_to_5`, `test_queue_maps_5_to_6`, `test_full_mapping`, `test_nfd_package`, `test_validator_failure_has_no_fallback`, `test_stale_source_or_asset_fails`, `test_validator_module_isolation`, `test_null_answer_stays_null`, `test_pending_blocking_external_context_excluded`, `test_used_and_this_range`, `test_existing_cli_unchanged`, `test_source_kind_mismatch`. Assertions: mappings equal spec table; dependencies/failed validator are errors; null stays null; choice/mixed content stays intact; rejected statuses/issues/used IDs do not appear; omitted textbook argument yields existing EXACT EXPECTED test results.

  ```python
  self.assertEqual(course_chapters(4), {5})
  self.assertEqual(course_chapters(5), {6})
  self.assertEqual(course_chapters(6), {4})
  self.assertEqual(course_chapters(7), {4})
  self.assertEqual([q['id'] for q in bank.select(mini_bank(), {2}, {1, 2})], EXPECTED)
  ```
- [ ] Step 2: Run `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p 'test_textbook.py' -v`. Expected: new API missing failures before implementation.
- [ ] Step 3: Implement catalog loading by subprocess validation with the passed interpreter, then read the validated JSON. Resolve the real NFC/NFD path. Wrap errors as BankError with actionable dependency/path details; do not modify sys.path to load the other bank.py.
- [ ] Step 4: Implement candidates and dispatch by source_kind. Preserve original structured fields. Reject blocking/unreadable/incomplete/external-context candidates; retain nonblocking source-error metadata for mandatory manual exclusion or justified acceptance. Union mapped chapters and explicitly reviewed overrides, then use taught/intersection/used checks. Rank textbook by type priority then chapter/number; keep existing past-exam order unchanged. Selection of a balanced final set belongs to the main workflow, not this loader.
- [ ] Step 5: Add `--textbook-dir PATH` and `--textbook-python EXECUTABLE` to select/check-manifest. Default textbook-python is sys.executable. Without textbook-dir preserve old CLI; with it missing/invalid package is failure. validate BANK remains the past-exam validator.
- [ ] Step 6: Run new test_textbook and existing test_bank suites. Expected: all pass, including subprocess CLI compatibility. Suggested commit only: `feat(ds-review): add textbook source adapter`.

### Task 2: Manifest and structured original cards

**Files:** Create `S/scripts/textbook_blocks.py`, `S/tests/test_textbook_blocks.py`; Modify `S/scripts/manifest.py`, `check_html.py`, `S/tests/test_manifest.py`, `test_check_html.py`.

**Interfaces:**
- Consumes: Task 1 TextbookCatalog and candidate contract.
- Produces: `render_question(catalog: TextbookCatalog, question_id: str, *, prefix: str) -> str`; `render_blocks(blocks: list[dict], catalog: TextbookCatalog, *, prefix: str) -> str`.
- Produces: old manifest support plus optional source_kind; HTML validation of matching `data-source` and `data-source-kind` when present. Textbook cards require `data-source-kind="textbook"`.

- [ ] Step 1: Add `test_legacy_manifest_defaults_to_past_exam`, `test_textbook_source_dispatch`, `test_wrong_kind_prefix_fails`, `test_choice_and_recursive_subquestions_preserved`, `test_c_literals_escaped_once`, `test_svg_ids_and_references_unique`, `test_white_background_and_alt_preserved`, `test_observations_not_rendered`. Assert source lookup succeeds only in the right catalog; options/labels/block order remain; literal C `<`, `&`, backslash-n round-trip; both duplicated SVG copies have distinct IDs and valid local references; no handwriting or computed answer is inserted into original content.

  ```python
  self.assertEqual(bank.check_manifest(past_bank, legacy_manifest), [])
  self.assertEqual(bank.check_manifest(past_bank, textbook_manifest, textbook=catalog), [])
  self.assertTrue(bank.check_manifest(past_bank, wrong_kind_manifest, textbook=catalog))
  self.assertNotIn('handwriting', render_question(catalog, 'ch04-q03', prefix='p1-original'))
  ```
- [ ] Step 2: Run the Task 2 test suites to see failures for missing renderer/contracts.
- [ ] Step 3: Implement the renderer using html.escape for text/code, ordered option/subquestion markup, safe inline verified SVG, and prefix-renamed XML IDs/href/url(#...) references. Reject unsafe paths and broken SVG references. Do not create hint/answer content in this renderer.
- [ ] Step 4: Extend manifest/check_html validation by adding source_kind checks without changing required fields for existing manifests. Keep generic parts support and existing card markup classes.
- [ ] Step 5: Run Task 2 suites and existing test_assemble. Expected: pass for legacy and textbook cases. Suggested commit only: `feat(ds-review): support textbook card provenance`.

### Task 3: Preserve existing cards during updates

**Files:** Create `S/scripts/update_review.py`, `S/tests/test_update_review.py`; Modify `S/scripts/html2md.py`, `S/tests/test_html2md.py`.

**Interfaces:**
- Consumes: existing HTML, prepared raw textbook card strings, Task 2 markup.
- Produces: `extract_cards(source: str) -> list[dict[str,str]]` with id/source/raw keys; `build_update(existing_html: str, cards: list[str], *, title: str, intro: str, footer: str) -> str`; `check_preserved(before: str, after: str) -> list[str]`; `publish_update(files: dict[Path,bytes], *, backup: Path) -> None`.
- Produces: `html2md.py REVIEW.html --check` support, preserving existing `NOTE.html REVIEW.html --check` behavior. Existing figure path/content collisions must fail rather than overwrite.

- [ ] Step 1: Add `test_existing_cards_are_byte_identical`, `test_empty_pack_receives_p1`, `test_existing_eight_cards_append_from_p9`, `test_part_d_rerun_identical`, `test_duplicate_or_reassigned_source_rejected`, `test_existing_hash_links_and_storage_keys_unchanged`, `test_second_replace_failure_rolls_back`, `test_review_only_keeps_note_md_and_figures`. Use 0-card and 8-card fixture HTML; assert all old card raw strings and sources unchanged, partD appears once, rerun is identical, duplicate IDs fail, file replacement failure restores original bytes.

  ```python
  self.assertEqual(check_preserved(before, after), [])
  self.assertEqual(extract_cards(before), extract_cards(after)[:8])
  self.assertEqual(extract_cards(after)[8]['id'], 'p9')
  self.assertEqual(build_update(after, new_cards, title=title, intro=intro, footer=footer), after)
  ```
- [ ] Step 2: Run new test_update_review and relevant test_html2md cases to confirm failures.
- [ ] Step 3: Implement HTMLParser-based source span extraction preserving raw strings. Patch only title/meta description/intro/footer/TOC/common panel text and the checked partD insertion/replacement location. Retain existing part sections, shell JS, links, read-state keys and IDs. Use existing metadata for source→pN mapping on rerun; number initial additions consecutively after the existing maximum.
- [ ] Step 4: Implement staged file publication after preservation checks, with backup and rollback for all files in this date's output set. Guard against target bytes changing after backup. Extend the single-review converter and check existing figure content before writing; conversion takes place in RUN/stage until validated. The existing convert_pack at html2md.py:641–644 removes every SVG first: the single-review path must bypass that cleanup, preserve all pre-existing SVG bytes, and choose a review-specific new filename when required. Existing two-file CLI behavior remains tested separately.
- [ ] Step 5: Run update/html2md/backup suites. Expected: pass, including simulated second-file failure and no note writes. Suggested commit only: `feat(ds-review): preserve cards in textbook updates`.

### Task 4: Update skill instructions and author contracts

**Files:** Modify `S/SKILL.md`, `S/references/problem-selection.md`, `manifest-guide.md`, `card-rules.md`, `review-prompt.md`, `S/assets/review-template.html`, `S/tests/test_skill_files.py`; Create `S/references/textbook-update.md`.

**Interfaces:**
- Consumes: Tasks 1–3 CLI/render/update interfaces and spec.
- Produces: documented `/ds-review-pack [MMDD|MMDD-MMDD] [lite]` mixed-source workflow and `/ds-review-pack update-existing [MMDD|all]` workflow. bank mode still builds only the past-exam bank.

- [ ] Step 1: Add `test_textbook_is_supported_not_ml_leak`, `test_new_and_retrofit_counts_are_distinct`, `test_update_mode_preserves_ids`, `test_all_references_and_cli_flags_exist`. Remove only 교과서 from the ML_WORDS denylist; retain all unrelated ML leakage checks. Assert new reference is linked, partD text and both count policies are documented, textbook CLI uses both catalog/path contracts, and no legacy source rule still says past-exam-only.

  ```python
  self.assertNotIn('교과서', ML_WORDS)
  self.assertIn('references/textbook-update.md', skill_text)
  self.assertIn('D. 교과서 연습문제', selection_rules)
  self.assertIn('--textbook-dir', skill_text)
  ```
- [ ] Step 2: Run test_skill_files. Expected: new behavior assertions fail against current docs.
- [ ] Step 3: Revise the workflow's preparation, selection, manifest checks, card brief, review and report. Add textbook source prerequisites, mapping, concept review, structured render/answer verification, exact source ID/kind/partD copy, selection.json and persistent metadata. Make setup failure explicit. Spell out 4–8 retrofit policy separately from 8–12 new-pack policy.
- [ ] Step 4: Document chronological update, backups, preservation checks, single-review MD conversion, idempotency and shortage reports in textbook-update.md. Change common template phrase 기출 원문 to 문제 원문. Keep existing source-specific original summaries unchanged.
- [ ] Step 5: Run `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -v`. Expected: entire skill suite passes. Suggested commit only: `docs(ds-review): document mixed-source pack workflow`.

### Task 5: Select and solve textbook questions for all nine dates

**Files:** Create 9×`복습노트/<range>/자료_복습팩/{manifest.json,selection.json,answers.py}` in RUN first; Create `S/tests/test_textbook_delivery.py`.

**Interfaces:**
- Consumes: Tasks 1–4; each existing note/review, matching STT, lecture slides, original textbook pages.
- Produces: per-date reviewed selection, validated manifest and raw cards; answers.py reproducibly verifies each selected new answer. No final HTML is written in this task.

- [ ] Step 1: Record fresh inventory and SHA256 for original banks, all original reviews/cards, notes, MD, figures and problem-explain artifacts into RUN/baseline.json. Confirm the 9 paths and observed 28-card baseline; if current state differs, use actual state and document it rather than assume.
- [ ] Step 2: Build each date's taught-evidence and forbidden/preview boundaries from actual STT/slides and preserved notes. If prior RUN manifest is unavailable, reconstruct the manifest from HTML and evidence without regenerating notes or existing cards. Read each selected question's original page and all referenced options/assets.
- [ ] Step 3: Query combined candidates in chronological order and select 4–8 textbook originals/date. Resolve dependencies between questions and review source-error issues. For 1001 inspect array insertion/deletion questions across textbook chapters using evidenced concept_overrides; never mark entire linked-list chapter taught. Record every rejection and any less-than-4 shortage. Existing questions are never part of the re-selection.
- [ ] Step 4: Solve and verify chosen questions using Python, C11 runs or lecture-reference reasoning. Store executable calculations/temporary C harness in RUN, reference exact book IDs and evidence, and generate answers.py plus per-question verification results. For implementation questions exercise the requested behavior, not only compile. Undefined behavior/ambiguous assumptions cannot produce a verified answer.
- [ ] Step 5: Write unittest delivery assertions `test_selected_ids_have_current_provenance`, `test_textbook_answers_verified_separately`, `test_every_selected_question_has_taught_evidence`, `test_dependency_is_present`, `test_chronological_originals_not_reused`, `test_retrofit_counts_or_explicit_shortage`, `test_existing_problem_ids_unchanged`. Require selected count 4≤N≤8 or explicit shortage reason, answer present, verification result pass, dependency selected/supplied by actual original, no prior source reuse, actual evidence refs and hashes resolve, and selected/manifest/card IDs agree.

  ```python
  self.assertEqual(selection['mode'], 'retrofit')
  self.assertTrue(4 <= added <= 8 or bool(validation['unresolved']))
  self.assertTrue(all(q['verification']['result'] == 'pass' for q in selection['selected']))
  self.assertTrue(all(q['answer'] and q['evidence'] for q in selection['selected']))
  self.assertEqual(validation['counts']['total'], existing + added)
  ```

- [ ] Step 6: Delivery tests read `DS_REVIEW_DELIVERY_ROOT` as the root containing staged 복습노트 and baseline.json; if unset they read the repository's final 복습노트 and persisted preserved metadata. Run `DS_REVIEW_DELIVERY_ROOT=<absolute RUN/stage> python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p 'test_textbook_delivery.py' -v` against staged metadata, run each answers.py and both manifest/catalog checks. Expected: pass; underfilled dates remain explicitly unresolved. Produce textbook cards using Task 2 original render plus independently written hints/steps/answer/scope connection, then check source equality, all required answer terms and prohibited concepts. Suggested commit only after Task 6 publication: `docs(ds-review): add verified textbook exercises`.

### Task 6: Stage, inspect and publish the nine updated packs

**Files:** Modify the 9 existing review HTML/MD files; Create persistent per-date metadata and `docs/verify/2026-10-12-ds-review-pack-textbook.md`; add only needed new figures.

**Interfaces:**
- Consumes: staged manifests/cards/answers from Task 5 and Task 3 preservation/publication.
- Produces: published mixed-source review HTML/MD and exact validation report, with all preservation boundaries confirmed.

- [ ] Step 1: Back up every date using backup.py and additionally copy/hash existing metadata and problem-explain references. Build updated HTML through build_update in a stage mirroring final relative paths. Stage unchanged note files as inspection inputs only. Store an exact original-to-final card ID/source comparison.
- [ ] Step 2: Run manifest.py, bank.py check-manifest BANK MANIFEST --textbook-dir PACKAGE --textbook-python PYTHON, check_html.py with staged note/review and html2md.py REVIEW --check for each date. Expected: OK and no preservation errors. Run delivery tests over all 9 staged outputs. If inherited problems fail checks, report them separately and do not silently rewrite old cards.
- [ ] Step 3: Serve staged paths and inspect all new cards and existing links at 1280×900/375×812 in light/dark. Verify TOC, pager, original/hint/solution panels, choices/subquestions, source page attribution, code/symbol round-trip, SVG references/white background, no answer added to problem figures, and preserved progress keys. Capture exact browser results per date/card. Expected: no console/KaTeX/resource/viewport errors; scroll inside code/table is allowed.
- [ ] Step 4: Check 1012's existing p1–p8 links against the unchanged problem-explain artifact. Record that the old explanations cover old cards only. Verify original banks, note HTML/MD and all existing raw cards match baseline. Verify publishing the same prepared update twice is identical using temporary files; no duplicate partD/cards or changed pN mapping.
- [ ] Step 5: Publish passing dates through publish_update and rerun final-path link/preservation/metadata checks. Save validation.json and aggregate verification report with actual old/added/total counts, shortage/unresolved items, exclusions, answer methods, browser checks and backup paths. Do not claim 9/9 completion when a date has blocked publication.
- [ ] Step 6: Run the full unittest suite and `git diff --check`; inspect exact changed paths. Confirm original banks/notes/explain files have no diff, confirm final HTML→MD correspondence, and report actual updated packs. Proposed commit only, without executing: `feat(ds-review): include textbook exercises in review packs`.

## Self-review

- Spec coverage: source catalog/compatibility Task 1; rendering/provenance Task 2; preservation/rollback Task 3; skill contracts Task 4; scope/answers/counts Task 5; all artifacts/browser/report Task 6.
- Interface consistency: textbook catalog type, textbook namespaced ID and original question_id are shared by selection, rendering, manifest and delivery; no second bank import occurs in-process.
- Review Focus: all five failure classes have named tests or per-card browser inspection in their owning tasks.
- Scope: no original source edits, full textbook answer bank, note rebuild, explanation rebuild or unsolicited Git publication.
- Execution handoff: recommend Native because all six tasks depend on one source/manifest/preservation contract and the nine dates must be processed in order. After user review/approach selection, use executing-plans for Native or subagent-driven-development for delegated task gates.
