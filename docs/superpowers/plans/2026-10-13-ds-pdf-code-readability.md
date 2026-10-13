# DS PDF Code Readability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 PDF 18개의 코드 블록을 선명한 번들 글꼴과 실제 12pt 크기로 출력하고 전체 결과를 검증한다.

**Architecture:** DS 전용 스타일·로컬 글꼴 리소스를 기존 frozen EC2 렌더러에 연결한다. 공통 PageSlice 분할은 그대로 사용하고 새 글꼴·고정 크기로 실제 적합 여부를 측정한다. 최종 PDF 검증과 기존 해시 기반 시각 검토·백업 교체를 통과한 결과만 게시한다.

**Tech Stack:** Python, Playwright/Chrome, PyMuPDF, pytest, JetBrains Mono, Pretendard.

**Spec:** `docs/superpowers/specs/2026-10-13-ds-pdf-code-readability-design.md`

## Global Constraints
- 최종 1440×810pt PDF 블록 코드 12pt, 오차 ±0.05pt; 페이지 증가 허용.
- JetBrains Mono Regular 400 + 기존 Pretendard Regular; 합자 비활성화; line-height 1.45; tab-size 4; 긴 줄 2ch 내어쓰기.
- 원문 문자·공백·줄 순서 보존; inline code와 출처/HTML/MD/문제설명/그림 유지.
- EC2 원본 4개 파일 바이트 보존; 기존 빈 조건/표 배치/Hint 계약 유지.
- 모든 렌더링은 offline; 폰트 실패나 크기·잘림·내용 검증 실패 시 기존 PDF 유지.
- Native 방식: 본 에이전트가 구현하고 executing-plans의 최종 독립 리뷰를 수행한다.
- 기존 managed worktree `/Users/hyunjun_macbook_pro/.codex/worktrees/ds-review-pdf/자구알`, branch `codex/ds-review-pdf`를 재사용한다. main 병합/푸시는 이 계획의 작업 범위가 아니다.

## Review Focus
1. 영어와 한글이 섞인 주석: 두 실제 글꼴이 사용되고 읽히는지 — Task 1/3.
2. 긴 한 줄·탭·빈 줄: 화면 줄바꿈 후 원문·들여쓰기와 오른쪽 경계가 보존되는지 — Task 2.
3. 패널과 해설이 서로 다른 축소율을 받는 페이지: 두 영역 모두 실제 12pt인지 — Task 1/3.
4. 글꼴 파일 누락·교체와 이름만 일치하는 fallback: 빌드와 게시가 모두 거부되는지 — Task 1/3.
5. 코드 없는 페이지와 inline code: 전체 구조·표·Hint와 기존 문장 크기가 유지되는지 — Task 2/4.

## File Structure
이 문서의 `S`는 `.agents/skills/ds-review-pack`이다. 아래 테스트/명령의 경로는 저장소 루트 기준이다.
- Create `S/scripts/pdf_code.py`: 코드 시각 계약, 글꼴 manifest 검증, 최종 PDF 코드 검증.
- Create `S/assets/pdf/vendor/jetbrains-mono/{JetBrainsMono-Regular.ttf,OFL.txt,manifest.json}`: 공식 고정 배포 자산과 출처/버전/라이선스/SHA.
- Modify `S/scripts/pdf_ds_layout.py`: 블록 코드 스타일·긴 줄 표시 확장.
- Modify `S/scripts/pdf_render.py`: 로컬 글꼴 route, loaded-face 검사, 코드 geometry 정보.
- Modify `S/scripts/pdf_layout.py`: 필요 시 새 코드 계약에 따른 fits 검증; 기존 PageSlice 타입/공통 분할 유지.
- Modify `S/scripts/review_pdf.py`, `S/scripts/pdf_publish.py`: 보고서와 글꼴/코드 gate.
- Create `S/tests/test_pdf_code.py`; extend existing PDF layout/publish/delivery tests.
- Modify `S/references/pdf-build.md`; Create `docs/verify/2026-10-13-ds-pdf-code-readability.json`; replace 18 PDFs + 9 `자료_PDF/pdf-validation.json` only after review.

## Runtime
기존 설치를 사용한다. 먼저 경로 존재와 import를 확인하고, 경로가 만료됐으면 실제 설치를 찾아 선택한다. 의존성을 재설치하지 않는다.
```bash
export PYTHONPATH=/Users/hyunjun_macbook_pro/.cache/uv/archive-v0/iwYsA3I8sBPc0zFW/lib/python3.14/site-packages
export DS_TEXTBOOK_PYTHON=/Users/hyunjun_macbook_pro/.cache/uv/archive-v0/lXGetgsy0jEjmBFQ/bin/python
```

### Task 1: 실제 번들 글꼴과 고정 크기 렌더링
**Files:** Create `S/scripts/pdf_code.py`, font assets and `S/tests/test_pdf_code.py`; modify `S/scripts/pdf_ds_layout.py`, `S/scripts/pdf_render.py`.

**Interfaces:**
- Consume existing `pdf_ds_layout.extend(template, mode)` and `pdf_render.load_template(mode, layout='a4')`.
- Produce `pdf_code.code_css(layout: str) -> str`, `pdf_code.font_manifest() -> dict`, `pdf_code.check_font_assets(expected: dict | None = None) -> None` (raise PdfError on failure).
- Pass layout to `extend(template: str, mode: str, layout: str = 'a4') -> str`; existing two-argument calls remain compatible.
- Manifest contains `family`, `version`, `source`, `license`, `files` (relative filename→SHA256). Font family is `DS JetBrains Mono`; real English glyphs must use embedded JetBrainsMono font.
- Add `geometry[physical_id]['code']` list entries: `region` (`panel`/`work`), `rect`, `font_family`, `font_size_css_px`, `effective_pdf_pt`, `line_height_css_px`, `text`. Keep Probe fields unchanged.

- [ ] **Step 1: Write failing tests.** In `test_pdf_code.py`, add `test_offline_font_loaded_and_used`, `test_code_fixed_size_ignores_parent_scale`, `test_missing_or_changed_font_rejected`. For both modes and parent scale 0.8/1.0 assert loaded DS JetBrains Mono face, extracted English PDF spans use JetBrainsMono, `abs(size-12)<=0.05`, mixed `// 스택 초기화` renders with Pretendard, ligatures disabled. Missing font and changed byte must raise PdfError; inline code keeps previous computed size.
- [ ] **Step 2: Run** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_pdf_code.py -q`; confirm failures name missing APIs/style or font.
- [ ] **Step 3: Implement interfaces and assets.** Obtain Regular static TTF and license from official JetBrains Mono release **2.304**, inspect identity/license before bundling, record verified download source and SHA in manifest. Register an offline route for the DS font URL, demand an actually loaded FontFace, and verify assets before each render. Add styles after frozen template conversion so 16:9 code is 12pt independent of `--fs/--sfs`; calibrate A4 size with frozen VIDEO_TEXT_SCALE so the final probe measures equivalent fitting. Apply identical rules to problem/solution `pre` and child `code`, using Pretendard as Korean fallback. Report effective size after print transforms; do not mistake screen overview zoom for PDF print size.
- [ ] **Step 4: Run** the Task 1 tests and `test_pdf_template.py`; all pass and frozen reference SHA checks unchanged.
- [ ] **Step 5: Commit** only Task 1 files, both spec/plan documents, and tests: `feat: render ds pdf code with bundled font`.

### Task 2: 원문 보존과 읽기 편한 이어지는 페이지
**Files:** Modify `S/scripts/pdf_ds_layout.py`, `S/scripts/pdf_render.py`, `S/scripts/pdf_layout.py` only where necessary; extend `S/tests/test_pdf_code.py` and `S/tests/test_pdf_layout.py`.

**Interfaces:** Consume Task 1 code geometry and `code_css(layout)`. Preserve `plan_pages(pack, run: Path) -> tuple[PageSlice, ...]`, `units`, `regroup`, `check_coverage`; no new source-content field. Presentation wrappers must preserve `pre.textContent` exactly.

- [ ] **Step 1: Write failing tests.** Add `test_long_line_wrap_preserves_text_and_indent` using tabs, consecutive spaces, blank lines, Korean comments and a line wider than the panel: assert exact pre textContent before/after decoration, 2ch continuation indentation and every displayed line within its container. Add `test_long_code_paginates_at_fixed_size`: all code metrics are 12±0.05pt, both modes have equal logical slices, `check_coverage(pack,pages)==[]`, original line order and terminal newline preserved. Include independent long solution code to exercise central work. Add `test_code_free_pages_keep_existing_layout`: inline font unchanged, no empty code section, existing worksheet placement and condition visibility pass.
- [ ] **Step 2: Run** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_pdf_code.py .agents/skills/ds-review-pack/tests/test_pdf_layout.py -q`; confirm new cases fail before implementation.
- [ ] **Step 3: Implement.** Apply pre-wrap visual wrapping, tab-size 4 and 2ch hanging indentation per original logical line using presentation-only wrappers when required. Preserve original textContent, including tabs/blank lines. Populate measured line rectangles in code geometry; overflow tests must check displayed lines, not the original unwrapped width. Keep existing common greedy PageSlice splitter, including 128-page failure cap; treat size violations as non-fitting candidates, and split rather than allowing code shrink. Avoid repeated blank code blocks/labels within a page. Unbreakable failures remain withheld/stale.
- [ ] **Step 4: Run** Task 2 tests plus `test_pdf_ds_layout.py`; expect all pass with source coverage and existing table behavior intact.
- [ ] **Step 5: Commit** Task 2 diff: `fix: preserve readable code across pdf continuations`.

### Task 3: Final PDF and publication gates
**Files:** Modify `S/scripts/pdf_code.py`, `S/scripts/review_pdf.py`, `S/scripts/pdf_publish.py`, `S/references/pdf-build.md`; extend `S/tests/test_pdf_code.py`, `S/tests/test_pdf_publish.py`.

**Interfaces:**
- Produce `pdf_code.check_pdf_code(pdf: Path, geometry: dict) -> list[str]` with errors for wrong actual font/size/missing Korean code text. Match code glyphs to measured code-region rectangles rather than treating all Courier/inline text as block code.
- New build report adds `code_style_version: 1` and `code_font: font_manifest()`; retain existing vendor/extension/template/artifact hashes.
- `check_stage(run)` invokes asset and final PDF code validation for reports with code_style_version. `publish_stage(run,repo)` revalidates code-font assets against report inside its existing lock before any backup/replacement. Old reports without code_style_version retain previous contract.

- [ ] **Step 1: Write failing tests.** Add `test_final_pdf_gate_detects_shrunken_or_fallback_code` (synthetic 8.3pt/Courier code region fails, real 12pt output passes), `test_publish_rejects_font_changed_after_review` (mutate temporary font copy, valid review unchanged, no destination byte changes), and `test_legacy_report_compatibility` (absent new fields still follows previous validation). Mixed Korean case must have no missing-glyph squares and extracted code text must include its comment.
- [ ] **Step 2: Run** code/publish tests; confirm new gates fail before implementation.
- [ ] **Step 3: Implement** declared APIs and gates; document code contracts/font provenance/failure recovery in pdf-build.md. Keep runtime layout hashes and font hashes consistent between build, check and publish; do not approve a fallback based on CSS font-family alone.
- [ ] **Step 4: Run** `python3 -m pytest .agents/skills/ds-review-pack/tests -q`; require no failed tests and investigate skips (do not report skipped verification as passing).
- [ ] **Step 5: Commit** Task 3 files: `test: enforce ds pdf code font and size gates`.

### Task 4: Regenerate and verify all 18 deliveries
**Files:** Replace PDFs for 0907 Intro_DS_Algorithms, 0914/0917 Recursion, 0921/0928 ArrayStructureList, 1001/1005 List, 1008 Stack, 1012 Queue and their nine `자료_PDF/pdf-validation.json` reports. Create `docs/verify/2026-10-13-ds-pdf-code-readability.json`. Update task status in this plan.

**Interfaces:** Use existing `review_pdf.py build/check/backfill/publish` CLI, `build_pack(review,run)` and Task 3 gates. Store stage/backups outside repo at a fresh `/private/tmp/ds-pdf-code-readability-<timestamp>` directory. Aggregate fields: packs/pdf_count/page_count, actual font manifest, test result, code-size range, protected source hashes, 18 artifact hashes, visual page count/evidence, nine backup locations and final reviewer findings.

- [ ] **Step 1: Snapshot** SHA256 of source HTML/MD/problem-explanation/figures and frozen EC2 files; require no unrelated tracked edits in worktree. Inspect PDF skill and run its authoring marker exactly once before first PDF edit operation.
- [ ] **Step 2: Build pilot** via `python3 .agents/skills/ds-review-pack/scripts/review_pdf.py build --review 복습노트/1012/복습문제_1012_Queue.html --run <fresh-pilot-run>`; expect staged/pass. Inspect P6 and continuations from final PDF at whole-page scale and enlarged scale; verify 12pt, readable comments, wrapping and preserved blank answer positions. Pilot is staged only; do not publish before complete review.
- [ ] **Step 3: Build all** via `python3 .agents/skills/ds-review-pack/scripts/review_pdf.py backfill --repo "$PWD" --target all --run <fresh-all-run>`; require nine successful packs and 18 PDFs. Run `check --run <pack-run>` for each; require PASS.
- [ ] **Step 4: Visually inspect** every final PDF page at whole-page scale and every code region enlarged. Check thin glyphs, Korean fallback, right-edge wrapping, continuation labels, left code sections, center solution code, condition/table regressions, Hint/footer and source labels. On a defect fix generator, rebuild affected stages, and rerun relevant checks before re-review. Record actual reviewed pages and image hashes; bind review.json to actual stage/report hashes.
- [ ] **Step 5: Obtain fresh final review** per Native executing-plans on the entire implementation branch. Resolve all material findings and rerun affected verification. Never use reviewer approval as a substitute for visual review.
- [ ] **Step 6: Publish** each nine approved packs with `review_pdf.py publish --repo "$PWD" --run <pack-run>`. Verify destination hashes against reviewed stage and backup availability; require protected source hashes equal snapshot. Record actual new page count, not historical 139. Preserve all external backups.
- [ ] **Step 7: Run** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_pdf_delivery.py .agents/skills/ds-review-pack/tests/test_pdf_code.py -q` and `git diff --check`; expect PASS/no whitespace errors. Write aggregate result from actual evidence; mark checklist from actual completion only.
- [ ] **Step 8: Commit** explicitly scoped PDFs/reports/docs: `fix: regenerate ds pdfs with readable code`. Inspect staged diff/stat and `git diff --cached --check` before commit. Report branch commit, test counts, actual pages, verification report and all 18 output files; preserve main until separately authorized.

## Plan Self-Review
- Spec coverage: all visual/source/offline/size/wrapping/pagination/publication requirements map to Tasks 1–4.
- Interfaces: new font/code APIs are owned by pdf_code.py; Probe/PageSlice fields remain compatible; old report compatibility is explicit.
- Five review-focus classes have named tests in their owning tasks and final visual checks.
- Spec version/licensing source is obtained and verified in Task 1; no unverified hashes or success claims are fabricated in planning.
- Execution has not begun. User review of this plan is required by writing-plans before Native execution.
