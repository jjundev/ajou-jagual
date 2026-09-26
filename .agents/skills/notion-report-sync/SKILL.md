---
name: notion-report-sync
description: Compare the project's HW1 Notion report with local Markdown and, when explicitly requested, update specified blocks while preserving formatting. Not for other Notion pages, databases, or PDF export.
---

# HW1 Notion report sync

The fixed page and paths live in `과제/과제1/검토자료/notion_sync.py`. Use its current `PAGE_ID`; do not substitute a page inferred from prose. Read `과제/과제1/검토자료/노션_API_동기화.md` before a live operation.

## Review a Notion edit

1. Run `python3 과제/과제1/검토자료/notion_sync.py pull` with `NOTION_TOKEN` in the environment. If the API says truncated or unknown blocks, stop; do not treat a partial download as a complete report.
2. Compare `과제/과제1/보고서_노션.md` with its preceding backup and with `과제/과제1/보고서.md`. Report actual wording, table-cell, code, heading, blank-line, and `<br>` differences separately. Do not normalize intentional spaces or blank blocks away. Distinguish Notion Markdown serialization from an actual content change.
3. For layout that Markdown cannot establish, inspect the live block tree or the PDF exported by the user. Do not claim to have verified the PDF from Markdown alone. Never overwrite `보고서.md` automatically.

## Edit specified blocks

Only after a user request to change specific Notion content: identify the exact block IDs and old text from a current API read. Prepare a temporary JSON edit plan with `page_id` and `edits`, each containing `block_id`, `type`, `old_text`, `new_text`, and `cell_index` for a table row. Review the plan against the requested change. Run `python3 과제/과제1/검토자료/notion_targeted_edit.py <edit-plan.json>`. The helper checks every target, saves a snapshot, patches one block at a time, and reads each back. Report the snapshot path and completed IDs. If preflight, PATCH, or readback fails, report the exact stage and any partial completion; do not blindly rerun an uncertain PATCH. Never use `push` or `layout-table` for ordinary edits.

`NOTION_TOKEN` stays in the environment. The user's final Notion PDF export and separate cover merge are outside this skill.
