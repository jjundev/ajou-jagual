---
name: assignment-report-audit
description: Use when reviewing an assignment report in this project against its instructions, grading rubric, source material, and execution evidence. Not for proofreading alone or implementing assignment code.
---

# Assignment report audit

Review the **current deliverable** against the current assignment, not against a past assignment's format or a prior review. Keep factual correctness, the author's demonstrated understanding, document format, and submission status separate. A fluent paragraph or a low detector score proves none of them.

## Establish the contract

1. Identify the requested report version and its source: local draft, Notion page, exported PDF, or submitted file. Do not silently treat a local draft as the live Notion page. For Notion comparisons or targeted edits, use `notion-report-sync` with that page's verified ID.
2. Read the assignment prompt, grading rubric, supplied material, and any official updates available in the workspace. Record each relevant requirement with its source and page, weight or hard-fail condition when stated, and the evidence needed to check it. Inspect rendered PDF pages when layout or figures matter; text extraction alone cannot establish appearance.
3. For **[2026-2] 자료구조 및 알고리즘 이해** programming assignments, read [the common course rubric](../programming-assignment-report/references/course-rubric.md) before assessing the current assignment and official changes. The user confirmed its course-wide scope. Reuse its confirmed grading and submission rules, keep its deferred items unresolved, and distinguish mandatory rules from author layout preferences. Do not apply it automatically to other courses or semesters.
4. Separate requirements for report content, code or other underlying work, layout, file format, and submission. Do not carry HW1-specific earned scores, examples, or deadlines into another assignment; shared rubric weights are reusable within the scope above. Author preferences cannot waive official requirements. Record contradictions unless an explicit official change resolves them.

## Test the report's claims

- Map each factual claim, calculation, figure, source attribution, and described action to the underlying material. Flag missing support, contradictions, and statements that present a possible failure as an observed result.
- For programming reports, use `programming-assignment-report` for the code and execution analysis. Compare supplied code with the student's version so the report does not claim a provided choice as a new design. Reconstruct code included in the report and compare it with the current source; check inputs, outputs, state changes, numerical results, and test counts against actual runs.
- For other reports, check methods, measurements, tables, citations, and images against the available records. If evidence is absent, mark the claim `확인 불가` rather than passing or inventing a test.
- Where the assignment requires the student's own writing, evaluate whether the explanation connects specific evidence to a causal account the author can explain. Do not infer authorship from style. Give factual notes or focused questions for the author to resolve; assistant-written prose is provisional and does not establish direct authorship.

Use a compact review record: `requirement | source and page | report location | evidence | status | correction`. Use `충족`, `보완 필요`, `확인 불가`, and `자료 충돌` as appropriate. State scoring as a provisional rubric assessment, not an awarded grade.

## Final text hygiene

After factual review, load both `remove-ai-marks` and `clean-user-facing-text` when the user asks to remove AI-like artifacts or wants a final text pass. Use the former to inspect invisible Unicode and file metadata, and the latter to audit clarity and formulaic prose. Protect code, formulas, identifiers, citations, quotations, links, and required disclosures. Line-leading U+00A0 in Notion code cells is indentation required by `notion-report-sync`; exclude it from `space` cleanup. Never run a whole-file cleaning pass over mixed report Markdown without locating protected spans first.

Only clean or rewrite content the user owns and the assignment permits editing. On a permitted copy, use `remove-ai-marks` for a measured deterministic Unicode cleanup and, only if requested and allowed, metadata cleanup; retain the original and record what changed. Use `clean-user-facing-text` to revise prose only under its own density and voice rules. If direct authorship is required, present concrete issues and let the author compose the final explanation; a paraphrase, metadata strip, or stylometry score cannot turn AI-assisted text into independently written work. Do not remove provenance or optimize detector scores to conceal prohibited assistance. When a permitted text edit is requested, preserve every claim and number, compare before and after against the evidence, and report what was mechanically changed versus what remains a judgment call. Neither skill can certify that text is human-written or undetectable.

## Edit and verify only within scope

- A request to **review** does not authorize editing. When editing is requested, change only identified passages and preserve unrelated work. For a Notion page, follow `notion-report-sync`'s current-block preflight, backup, targeted edit, and readback procedure. Re-pull and compare separately with the local draft. Never use a page-wide replacement for a small correction.
- Recheck the corrected claims against their sources. If code or data changed, rerun the focused checks that support those claims. Do not repeat unrelated tests merely because prose changed.
- If a PDF is required, inspect the actual exported PDF for section presence, legible layout, and selectable code text where required. A Markdown file or Notion table does not prove PDF compliance. Do not claim submission from an export or local file.

Finish with the highest-risk findings first, exact locations and repair directions, what was verified, what remains unverified, and the next concrete step. Preserve the distinction between a review finding, an authorized edit, and a student's own final writing.
