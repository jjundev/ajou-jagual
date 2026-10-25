---
name: notion-report-sync
description: Use when uploading a course report to Notion, applying its report format, comparing it with local Markdown, editing specified report blocks, or adding image upload slots. Not for databases or PDF export.
---

# Notion report sync

Resolve the assignment's local report, source, execution images, downloaded Markdown, and evidence directory from current project material or the user's request. For a new page, verify its parent and title; for an existing page, verify its page ID. Do not infer a page ID from another assignment. Keep `NOTION_TOKEN` in the environment.

## Upload and apply report format

A request to upload the report includes applying the course's default report format and verifying it, unless the user specifies another format. For this workspace's **[2026-2] 자료구조 및 알고리즘 이해** reports, read and apply [the course report format](../programming-assignment-report/references/data-structures-course-format.md). Treat it as author preferences within the current assignment's official requirements; do not apply it automatically to other courses.

Before uploading, read [Native report upload](references/native-report-upload.md). Upload editable native Notion blocks, including source/analysis tables and requested execution images. Markdown is the local manuscript and comparison artifact; this workflow does not import a Markdown file. Preserve the approved wording and authorship disclosures. Create the required heading hierarchy and blank-block spacing in the initial plan, rather than leaving formatting for a later request.

The common [`scripts/notion_report.py`](scripts/notion_report.py) CLI provides **only `pull` and `edit`**, not upload/create/layout commands. Use its API client for an assignment-specific native upload following the reference; do not invent an upload CLI or run a historical assignment script unchanged. Prefer connected tools when they support the required operations; use the UI for settings or empty image slots unsupported by the API.

Upload completion requires the reference's verification record: native content, code, images or slots, headings/spacing, live page settings and table widths, and a fresh Markdown download. For the course default, explicitly check the single gray TOC, direct explanation-cell text, every execution case's gaps, and consistent captions without duplicate case titles. Record each as verified, failed, or not verified with evidence. An incomplete setting or readback is partial completion, even when the page exists. Keep Notion upload, local PDF generation, Notion PDF export, cover merge, and actual submission as separate states.

## Pull and compare

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_report.py pull \
  --page-id PAGE_ID --report PATH_TO_LOCAL_REPORT \
  --output PATH_TO_NOTION_MARKDOWN
```

The script refuses incomplete Notion Markdown and rejects an output path that points to the local report. If the output path already contains a download from the same page, the script compares that exact file with the new download before replacing it. A changed previous download is backed up under `<output directory>/검토자료/노션_백업/`; use `--backup-dir` to choose another location. An unchanged one creates no backup. A first download has no previous version to compare. This is a comparison with the previous local download, not Notion's page version history. Use a separate output path for each page.

Report the previous-download comparison first, then the separately labeled diff against the local report. Summarize the actual wording, table-cell, code, heading, blank-line, space, and `<br>` changes instead of pasting a large diff alone. Distinguish Markdown serialization from an actual content edit. For layout that Markdown cannot establish, inspect the live blocks or the user's exported PDF. Do not claim PDF verification from Markdown alone.

## Edit specified blocks

Only when the user asks to change particular Notion content: read the current page and identify exact block IDs, types, and old text. Prepare a temporary JSON file with `page_id` and an `edits` array; each edit has `block_id`, `type`, `old_text`, and `new_text`, plus zero-based `cell_index` for a table row. Review the file against the request, then run:

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_report.py edit \
  --page-id PAGE_ID --plan PATH_TO_EDIT_JSON --evidence PATH_TO_EVIDENCE_DIRECTORY
```

The tool checks every target belongs to that page and matches the old text before any PATCH. It saves the exact pre-edit blocks and Markdown, preserves supported rich-text annotations and links, updates one block at a time, and reads back each result. If a write or readback is uncertain, report the target, completed IDs, and observed state; do not blindly retry. Unsupported rich-text structures require a separately reviewed edit. Never use a page-wide upload or layout migration for routine changes.

## Code in table cells

Write source code in a Notion table cell as plain `text` rich text without the `code` annotation, and put each line's leading spaces as the same number of U+00A0 (no-break space). Leave spaces inside a line as ASCII spaces. Reason, from a 2026-09-27 export test: Notion's PDF export drops leading ASCII spaces, and an inline-code cell prints in red (#EB5757) even with an explicit `color`. Text extracted from that PDF contained no U+00A0, so copied code carries no stray characters.

After writing, read the cell back: it must have no `code` annotation, and replacing U+00A0 with a space must reproduce the source exactly. When a target text item already has line-leading U+00A0, `edit` also matches an `old_text` written with ASCII indentation and converts `new_text`'s line-leading spaces to U+00A0. Indentation typed with the space bar in the Notion editor is ASCII and disappears again in the PDF, so check the exported PDF after manual code edits.

## Add image upload slots

When the user asks for an image placeholder in the Notion report, create an **empty Notion image block**, not a paragraph saying where an image belongs. Place it beside the relevant result or analysis, leaving existing input, output, and explanation intact unless the user asks to change them. Record the intended image-to-slot order before adding multiple slots.

Use the Notion editor for this operation: insert an image block with `/image` at each intended position and leave its upload dialog empty. If replacing a prior text placeholder, select only that paragraph's text, clear it, choose `/image`, then dismiss the upload dialog. Do not upload the screenshot when the user intends to add it personally. Back up the current page blocks and Markdown before changing existing slots.

Read the page again after editing. Confirm the expected number and order of `image` blocks at the intended positions, with empty `external.url`, and confirm the old text placeholders are gone. Notion's Markdown export represents these empty image blocks as `![]()`; that syntax alone does not prove their position or type, so verify the live blocks. Pull again to update the local Markdown. Later, the user can click **이미지 추가** on each block and choose **파일 업로드**.

`과제/과제1/검토자료/notion_sync.py` contains historical HW1-only upload and table-migration commands. Use the common script for pull or targeted text edits across assignments, and the native-upload reference for new uploads. PDF export and separate cover merging are outside this skill; perform them only under the user's requested scope and the relevant workflow.
