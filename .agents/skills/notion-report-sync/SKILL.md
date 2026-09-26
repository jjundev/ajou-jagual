---
name: notion-report-sync
description: Use when comparing a course report edited in Notion with its local Markdown or applying a specifically requested edit to that report's Notion blocks. Works across assignments with an explicit page ID and file paths; not for databases or PDF export.
---

# Notion report sync

Use [`scripts/notion_report.py`](scripts/notion_report.py) for report pages across assignments. Resolve the page ID and the assignment's local report, downloaded Markdown, and evidence directory from current project material or the user's request. Do not infer a page ID from another assignment. Keep `NOTION_TOKEN` in the environment.

## Pull and compare

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_report.py pull \
  --page-id PAGE_ID --report PATH_TO_LOCAL_REPORT \
  --output PATH_TO_NOTION_MARKDOWN
```

The script refuses incomplete Notion Markdown, backs up a changed previous download, and prints a text diff against the local report. It rejects an output path that points to the local report. Review wording, table cells, code, headings, blank lines, spaces, and `<br>` separately; distinguish Markdown serialization from actual content edits. For layout that Markdown cannot establish, inspect the live blocks or the user's exported PDF. Do not claim PDF verification from Markdown alone.

## Edit specified blocks

Only when the user asks to change particular Notion content: read the current page and identify exact block IDs, types, and old text. Prepare a temporary JSON file with `page_id` and an `edits` array; each edit has `block_id`, `type`, `old_text`, and `new_text`, plus zero-based `cell_index` for a table row. Review the file against the request, then run:

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_report.py edit \
  --page-id PAGE_ID --plan PATH_TO_EDIT_JSON --evidence PATH_TO_EVIDENCE_DIRECTORY
```

The tool checks every target belongs to that page and matches the old text before any PATCH. It saves the exact pre-edit blocks and Markdown, preserves supported rich-text annotations and links, updates one block at a time, and reads back each result. If a write or readback is uncertain, report the target, completed IDs, and observed state; do not blindly retry. Unsupported rich-text structures require a separately reviewed edit. Never use a page-wide upload or layout migration for routine changes.

`과제/과제1/검토자료/notion_sync.py` contains historical HW1-only upload and table-migration commands. Use the common script above for new assignments and routine HW1 pull or targeted edits. The user handles final Notion PDF export and any separate cover merge.
