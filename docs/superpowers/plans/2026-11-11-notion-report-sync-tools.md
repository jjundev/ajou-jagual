# Notion report sync tools implementation plan

**Goal:** Preserve the existing pull/edit CLI while adding reusable, resumable image replacement and export-derived PDF checks tied to current inputs.

**Spec:** The approved chat design, “Notion 보고서 동기화 스킬 업데이트 설계”.

**Architecture:** Separate image and local PDF CLIs share a small file-based verification ledger. Native export remains an observed UI operation. No live report, submission PDF, or unrelated working changes are modified by implementation tests.

**Stack:** Python 3, unittest; Pillow for image identity; Playwright Chromium and PyMuPDF for local artifact checks.

## Constraints and review focus

- Keep `notion_report.py pull/edit` compatible; reuse its API client.
- Preserve captions, rich text, non-target attachments, source order, code indentation, and previous deliverables.
- Persist pending writes before requests; resolve uncertain writes through readback rather than repeating them.
- Test changed inputs, signed-URL refresh, partial writes, repeated identical images/text, tall rows, and changed PDF/settings.
- Work in the current checkout: the skill directory is the user's requested target and currently clean; preserve unrelated dirty files. No commit/push is requested.

## Tasks

- [x] 1. Add tests and `report_state.py`: atomic JSON records, dependency fingerprints, stale downstream status, explicit visual review evidence. RED → GREEN.
- [x] 2. Add tests and `notion_images.py`: prepare/apply/resume, explicit mapping, exact backups, conservative readback/recovery, target-only tree comparison. RED → GREEN.
- [x] 3. Add fixture-driven tests and `notion_pdf.py`: immutable source, configurable print groups, PDF text/order/indentation/image checks, page rendering and review records. RED → GREEN.
- [x] 4. Update skill references and CLI documentation. Run the before/after consumer scenario, existing and new tests, skill validator, and independent review. Fix demonstrated issues and report exact validation limits.

## Execution record

- Baseline: existing common script suite passes, 27 tests. No common image/PDF commands exist. Prior task artifacts establish the failed image PATCH shape and print-layout failures.
- Read-only baseline/forward consumer evaluations confirmed that the replacement request and export selector gaps are now discoverable. Forward evaluation also found ambiguous full-page certification and missing original-mapping fingerprints; targeted checks now use a separate `images` stage, and the original mapping is preserved and checked.
- Independent code review reproduced final-readback source changes, cross-candidate PDF review, omitted quotation/callout text, and lost ledger updates. Regression cases were observed failing and now pass. Records require checked fingerprints and parent versions; ledger updates lock and reload; PDF text inventory includes uncovered body text. The print-copy evidence is fingerprinted as well.
- Native export smoke testing exposed CDN dependencies, fragmented PDF paint order, and heading/table orphans. Export styles/scripts/fonts are cached without changing source files. Ordered checks use glyph geometry as well as paint order; pypdf checks leading indentation separately. Table-heading grouping and row/header/heading height checks have regression coverage.
- Final skill test command: `python3 -m unittest discover -s .agents/skills/notion-report-sync/scripts -p 'test_*.py'` — 71 tests pass, including all 27 pre-existing tests.
- Repository tests: `/tmp/notion-sync-qa-env/bin/python -m pytest -q --ignore=tmp` — 69 pass. The initial unqualified root collection included generated copies under `tmp/textbook-exercises/20261012/package/` and failed with duplicate test modules plus a missing `jsonschema` dependency. An importlib-mode attempt additionally could not import historical `notion_sync` and `test_validation`; default-mode canonical tests pass. pytest/jsonschema were installed only in the temporary QA environment.
- Skill validator, compilation, CLI help and `git diff --check` pass. Upstream PyMuPDF emits deprecation warnings in this Python environment; no test failures remain in the checked scope.
- Latest native HTML smoke test: `tmp/notion-sync-smoke-20261111/print6/` — 34 landscape pages, all 27 paired rows and all 5 screenshot occurrences verified. All contact sheets and dense/affected pages 2/17/25/33 visually reviewed; review recorded. This is a local tool check using the preserved earlier export, not a new live export or replacement deliverable. Notion/HTML origin stages remain separate and unverified in that local test ledger.
- No live Notion writes, stable report-PDF replacement, cover merge, commit or push were performed by this implementation task.
