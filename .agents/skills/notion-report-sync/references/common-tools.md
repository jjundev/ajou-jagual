# Common image, print and freshness tools

Use these tools for an authorized image replacement or export-derived PDF task. They do not extend the requested scope to new pages, report rewriting, cover merging or submission. `notion_report.py` still provides only `pull` and `edit`.

## Dependencies and evidence

Use Python 3.10+ with Pillow for image processing; local printing additionally needs Playwright with Chromium, and verification needs PyMuPDF and pypdf. Prefer an existing environment containing them. If needed, install `Pillow playwright PyMuPDF pypdf` and run `python3 -m playwright install chromium` in the chosen environment. Invoke scripts through that interpreter. No live Notion token is needed for PDF operations; image operations use the existing `NOTION_TOKEN` environment variable and the common client's API version.

Choose new evidence directories per preparation/print. Keep page IDs, input mappings and state files assignment-specific. Do not copy a historical assignment script with its fixed IDs, filenames, counts or layout constants. Raw before/after page snapshots may contain expiring attachment URLs; keep those local as recovery material, omit them from summary manifests/logs, and never publish tokens or signed URLs.

## Replace existing image attachments

Resolve and inspect the verified page and local image files first. Prepare a JSON array mapping exact existing image block IDs to files:

```json
[
  {"block_id": "IMAGE_BLOCK_ID", "source_path": "../screenshots/current.png"}
]
```

Relative source paths resolve against the mapping file's directory. Entries may cover a subset of the page's images; execution order follows the live page. A duplicate, foreign or non-image block fails the entire preparation. Static PNG/JPEG/WebP up to 20,000,000 bytes are supported; other formats/sizes require another reviewed workflow.

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_images.py prepare \
  --page-id PAGE_ID --mapping /path/to/images.json \
  --report /path/to/report.md --state /path/to/workflow-state.json \
  --evidence /path/to/new-image-evidence
```

`prepare` reads but does not mutate Notion. It saves exact recursive page blocks, Markdown, old attached files, the original mapping JSON, source snapshots, hashes, writable captions and image order. The CLI tracks changes to the original mapping file as well as the resolved plan. `--report` is optional for image-only work; when provided it becomes another freshness input. `--state` is optional; the default is `state.json` inside the evidence directory. This image tool records an `images` check, not the `notion` stage's full report/content/settings validation.

Inspect `manifest.json` against the requested files and block positions before applying:

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_images.py apply \
  --evidence /path/to/new-image-evidence
```

The tool preflights the whole batch, uploads each file, and replaces the attachment in the same image block, preserving caption rich text and block order. It downloads readback attachments and compares bytes or dimensions plus RGBA pixels. Final comparison preserves non-target attachments and all other page content. Known Notion-hosted URL signatures/expiry may refresh; ordinary URL changes are not ignored. New-image creation and existing-image PATCH shapes differ; see [Native report upload](native-report-upload.md).

After interruption or an uncertain response, inspect the pending state and live blocks, then use:

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_images.py resume \
  --evidence /path/to/new-image-evidence
```

`resume` rechecks source snapshots, current source files, page membership and captions before writes. A verified/possibly applied attachment must match the intended pixels. A saved upload ID can be reused after confirming `uploaded`. Creation without a returned ID, an unresolved send, expired uploads, an unchanged uncertain PATCH or a divergent attachment stops mutations; inspect and establish its actual outcome before preparing a new reviewed plan. Do not edit the manifest to skip uncertainty. A final fresh Markdown read is saved as `after.md`; use the existing `pull` command separately for its previous-download and local-report comparisons.

## Print and check genuine exported HTML

First complete [the native default-view export procedure](html-export-to-pdf.md), preserve the ZIP/extracted original, verify the page and latest assets, and record that evidence. These local tools cannot prove origin or remotely current content. Do not give them locally regenerated manuscript HTML and call it a Notion export.

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_pdf.py print \
  --html /path/to/untouched-export/report.html \
  --output /path/to/new-candidate.pdf --evidence /path/to/new-print-evidence \
  --state /path/to/workflow-state.json
python3 .agents/skills/notion-report-sync/scripts/notion_pdf.py verify \
  --evidence /path/to/new-print-evidence
```

Printing refuses existing output/evidence paths. Use a candidate outside the preserved export bundle; replace the deliverable only after automated checks and actual visual review, retaining a recoverable prior PDF. There is no automatic promotion or overwrite command.

The renderer preserves DOM text, source indentation, links, fonts and original asset files; only its print copy is changed. It groups short code/output and image labels, handles whitespace-only paragraphs, fits proportional table columns, and allows tall code blocks to flow without a language-based exception. Small tables stay with their heading/short label; large tables start their section on a fresh page, carrying the chapter introduction when it can fit with the first row. A row that cannot fit with its repeated table header or required section heading fails rather than splitting its code/analysis pair. Required images must resolve locally from the genuine export bundle. Native Notion exports can reference CDN stylesheets, fonts and syntax-highlighting scripts; the renderer loads those export resources and saves their exact bytes/hashes under the print evidence's `assets/` directory. Remote images/other resource types fail rather than silently changing the export's image provenance. Use only the genuine, inspected export. The source bundle remains untouched.

Optional `--config /path/to/print-settings.json` accepts:

```json
{
  "margin_mm": 14,
  "body_pt": 10,
  "table_pt": 9,
  "code_pt": 9,
  "section_breaks": [],
  "paired_table_selector": null
}
```

These are adjustable starting values, not assignment requirements. `section_breaks` takes heading tags such as `["h1", "h2"]`, leaving the first matching heading without a forced break. By default source/analysis tables are recognized by their first header cell (`소스코드` or `Source code`); supply a selector for other labels. Paired source cells and native `pre` blocks receive separate PDF indentation checks. Ambiguous/unsupported extraction should remain failed pending investigation, not be bypassed by removing the source from verification.

`print.json`, `content.json`, the CSS and print HTML bind the candidate to its source, assets and settings. `verify` checks the current candidate, ordered text occurrences (including repeats and fragmented navigation paint order), code indentation, source/analysis pairing, A4 landscape geometry, blank pages, text/image bounds, screenshot labels and decoded image occurrence order. The text inventory includes blockquotes, summaries and direct callout/div text as well as paragraphs, headings and table cells. It renders all pages and contact sheets under a new `pages` directory (numbered on repeat verification). Image counts come from the HTML, and repeated identical images are treated as separate occurrences. Automated checks do not establish legibility, all heading placement, or every visual defect.

Inspect every page/contact sheet and affected/dense pages at readable resolution. Only then record the pages actually reviewed and the findings:

```bash
python3 .agents/skills/notion-report-sync/scripts/notion_pdf.py review \
  --evidence /path/to/new-print-evidence --pages 1 2 3 \
  --notes 'All listed pages and their contact sheets inspected; no unresolved layout defects.'
```

The page numbers above are illustrative; pass the complete actual set. `review` records an already performed review; it does not inspect images itself. It requires current automated checks for this exact candidate/print record, all page numbers, nonempty notes and unchanged render hashes. Another candidate becoming current in a shared ledger prevents an older PDF's checks/review from being attached to it. It writes `visual-review.json`. An automated success alone always leaves visual review **not verified**.

## Track freshness across the workflow

Use one shared `--state` path when connecting image and PDF operations. Each stage records its current file hashes, settings, evidence and earlier-stage record versions. Changing an input makes its checks and downstream checks **stale**, while prior evidence remains recoverable. Stage order is `images → notion → html → print → content → visual`; an absent stage is not verified. Not every task requests every stage: an image-only request ends with its `images` check, and local print/content success does not establish missing Notion/HTML checks. Re-recording a parent invalidates old child records even when their files remain present.

For externally observed Notion/HTML checks, create an inputs JSON object mapping names to paths (relative to that JSON file): include manuscript/source, every mapped screenshot, mappings, and the original ZIP/HTML/assets applicable to that stage. Include the export options and live readback observations in a separate evidence file. Then record the check actually performed:

```bash
python3 .agents/skills/notion-report-sync/scripts/report_state.py record \
  --state /path/to/workflow-state.json --page-id PAGE_ID --stage html \
  --inputs /path/to/html-inputs.json --evidence /path/to/export-check.json
python3 .agents/skills/notion-report-sync/scripts/report_state.py status \
  --state /path/to/workflow-state.json
```

`record` stores an observation; it does not inspect Notion, operate its UI or validate claims in the evidence file. Stage `notion` is available for a separately performed full content/settings check. Retain scope details in evidence so a targeted attachment check is never reported as complete report-format validation. `status` rehashes recorded paths and refreshes the local JSON ledger; it cannot watch or infer remote edits. Updates use a locked reload/write transaction on macOS/Linux so concurrent tool instances preserve each other's stages. Re-read Notion before exporting and compare the actual downloaded bundle. If a stage is stale, regenerate/recheck it and affected downstream stages before claiming completion. Never restore an earlier verified flag by editing JSON.

Run reusable tool tests without network writes:

```bash
python3 -m unittest discover -s .agents/skills/notion-report-sync/scripts -p 'test_*.py'
```
