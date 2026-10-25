# Native report upload

Read this for a requested new report upload or an explicitly requested format repair. Routine wording edits continue to use `notion_report.py edit`; do not rebuild an existing page for them.

## Plan before writing

Resolve and record the verified parent page, intended title, local manuscript/source paths and hashes, ordered image-to-case mapping, separate downloaded-Markdown path, and evidence directory. Inspect the parent's existing pages and any prior upload manifest before creating a page. A title match alone does not establish identity: inspect the candidate and its recorded page ID. Reuse only the confirmed target; leave reference reports unchanged.

Save a native block plan with expected types, text, table rows, source segments, image captions/order, and heading/spacing rules. Apply the linked course format while building this plan. Derive counts from the current report, never from HW1 or HW2. Keep the approved prose, explicit line breaks, and assistance/authorship disclosures unchanged.

For an existing page's requested format repair, first save its exact recursive blocks, page metadata, and Markdown. Prepare a targeted plan with old IDs/types/text, replacements, and required empty paragraphs. Preserve content and order outside those targets; adding format does not authorize rewriting prose or replacing all blocks.

## Write native blocks

Use a sufficient connected tool when available. Otherwise use the official Notion API with the existing environment token and the common script's `NotionAPI` client. Inspect the client's configured API version and supported request behavior; consult current official documentation if an operation is uncertain. The CLI has no upload command.

- Create the new page under the verified parent with `POST /v1/pages`; immediately persist its ID and returned URL in the manifest. Append the planned native blocks in bounded batches with `PATCH /v1/blocks/{page_id}/children`. Respect current API text, child-count, nesting, and payload limits; split rich-text items without altering their concatenated text.
- Use a native `table_of_contents`, `heading_1`/`heading_2`, paragraphs, editable tables with `table_row` children, and code blocks where appropriate. Put source and corresponding analysis in the same two-column table row. For source cells follow **Code in table cells** in the skill: plain text, no `code` annotation, line-leading NBSP only. Keep native code blocks' source unchanged.
- For the course default, build title/spacing rules from the course-format reference: one gray TOC, explanation cells without repeated internal labels, and case-specific input/output/screen gaps. Count actual empty paragraph blocks at every prescribed boundary, including the last case. Preserve disclosures or other required content between the TOC and chapters. Repeated input/output/screen labels are bold paragraphs; genuine subordinate cases may use heading 3. Use the neighboring subsection title to identify a screenshot instead of repeating that title directly before its image.
- Persist each completed upload/batch, returned IDs, and response before proceeding. Do not infer successful insertion solely from the response's `results` length: insertion responses may also include existing following blocks. Read current children with pagination and verify the new IDs, types, text, and intended order against the pre-write state.

### Actual images versus empty slots

When uploading the report's execution evidence, attach the mapped local image files to native image blocks with captions, beside their corresponding input/output/analysis. Apply the course reference's consistent caption wording and state only observed facts; preserve the original images, capture environment, and hashes in local evidence.

The verified API pattern is to create `file_uploads` in `single_part` mode, send the file as multipart form data to `/v1/file_uploads/{id}/send`, require `status: uploaded`, and attach an image with `type: file_upload` and that ID. Use a compatible method for files beyond the current single-part limits. Check current limits instead of assuming every image fits. Readback can represent the attached image as `type: file` with a signed URL.

Download the attached image through its returned URL for comparison with the mapped local image: compare bytes when unchanged, or decoded pixels when the service re-encodes it. Record the comparison, caption, case order, and image block ID. Signed URLs and expiry times can refresh on read; their changes alone are not content edits. Keep local files rather than relying on expiring links for long-term evidence.

If the user says they will add images themselves, follow **Add image upload slots** in the skill instead: use the editor to create genuine empty image blocks, verify their positions, and leave them empty. A report-upload request does not override this explicit instruction.

## Page settings and existing-page repair

Apply the course reference's page settings using supported tools or the Notion UI. Verify **default font, small text off, full width on** in the live settings, reload, and confirm persistence. Save a screenshot or other direct UI evidence and its path. If UI access is unavailable, record settings as not verified; Markdown cannot prove them.

Adjust source/analysis column widths per table to the actual code and prose; check visible wrapping and readability in the UI. Do not reuse prior reports' width numbers as constants or alter source text to fit a width. Record serialized `<colgroup>` widths when available, but do not infer a zero width from an unspecified column or claim PDF layout from those values.

For a targeted insert after an existing block, the API form verified with version `2026-03-11` is:

```json
{"children": [], "position": {"type": "after_block", "after_block": {"id": "TARGET_BLOCK_ID"}}}
```

Replace `children` with the planned blocks. Verify current API compatibility before using this with another version. For a type replacement, create and read back the replacement at the intended position before recoverably archiving the old block. Record both IDs. Calculate spacing from existing empty blocks so rerunning a partial repair does not add duplicates; remove surplus blank blocks only within the reviewed repair scope.

## Uncertain writes and recovery

Keep a manifest containing parent/page IDs, source/report hashes, planned blocks and images, completed IDs, pending operation, and validation states. Record a pending mutation before sending it. On timeout, ambiguous response, or delayed readback, inspect the saved response and live page before another mutation. Retry bounded reads to resolve delayed visibility; do not blindly repeat page creation, image attachment, block insertion, or replacement. If the result remains uncertain, stop mutations, report completed IDs and observed state, and leave a recoverable record.

## Required completion record

Read the complete remote tree, including paginated table rows and nested children, and compare against the plan. Store the evidence path and `verified`, `failed`, or `not verified` for each applicable item:

| Item | Evidence required |
|---|---|
| Target | Verified parent, page ID, title and returned page URL; reference pages preserved |
| Native content | Exact approved prose, table dimensions/cell text, code/analysis correspondence and block order; course-default explanation cells start directly with specs/analysis rather than repeated internal labels |
| Source | Every planned source segment matches the actual source after reversing line-leading NBSP; no inline-code annotation in source cells; appendix matches when required |
| Images or slots | Planned count, case order, consistent factual captions without duplicate case-name paragraphs, actual image/pixel comparisons, or verified empty native slots as requested |
| Structure | Exactly one gray native TOC for the course default, intended heading levels and unnumbered titles, bold repeated execution labels, exact empty-block counts at every required chapter/case boundary including the last case |
| Page settings | Live UI evidence and reload confirmation for font, small text and full width; content-based per-table column widths checked for readability |
| Download | Fresh complete Markdown saved to a separate path using common `pull`, with previous-download diff before local-report diff and backups when changed |
| Deliverable states | Notion uploaded/formatted/verified, local PDF, Notion-exported PDF, cover merge, and submission recorded separately |

Mark upload and formatting complete only when all applicable checks are verified. If a check cannot be completed, report the page URL and the specific partial state. Do not call the local HTML-generated PDF a Notion export or claim PDF layout from this verification.

Finish by linking the page and summarizing content/format verification and any incomplete PDF or submission steps. Do not regenerate local report prose or PDFs merely because the Notion Markdown serialization changed.
