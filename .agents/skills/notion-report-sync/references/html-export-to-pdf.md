# Notion HTML export to A4 landscape PDF

Read this for a requested report HTML download or complete export-and-print task. This procedure uses the actual Notion HTML export as the PDF source. An upload or text edit alone does not request an export; an HTML-only request ends after the verified download. For another course or an explicit paper/orientation choice, apply the user's requested format rather than imposing this course's A4 landscape default.

## Verify the target and scope

- Resolve the page ID, URL, title, latest approved edits, download location, output PDF path, and evidence directory from the current request and project material. Verify the live page identity and representative latest changes; filenames and titles alone do not prove that a ZIP contains the current revision.
- Read current blocks or a fresh Markdown pull as needed. Content edits remain targeted under the parent skill; exporting does not authorize rewriting the report. A complete export request authorizes the agent to operate the export dialog, save the download, extract it, print the HTML, and verify the output without repeatedly asking the user to do those steps.
- Prefer a connected tool if it supports the required export. Otherwise use available UI automation on the authenticated Notion app/browser. The common `notion_report.py` CLI has only `pull` and `edit`; do not invent an `export` or `print` command. Record concrete access/authentication blockers and completed stages if progress is impossible.

## Download the genuine default-mode HTML

1. Open the verified page's actions menu and locate **Export** (possibly under **More**). Inspect the current dialog; menu labels and options may change.
2. Choose **HTML** and include the report's images and files. In the export dialog's **데이터베이스 보기 (Database view)** dropdown, select **기본 보기 (Default view)** rather than **현재 보기 (Current view)** when that control is present. This is separate from page font, full-width settings, and the app's light/dark theme. Include subpages or comments only when they belong to the requested scope. Preserve the default sans font and native export appearance unless the user requested another mode. If the current UI lacks that dropdown, record the controls actually available and verify the exported appearance; do not claim to have selected a nonexistent control or change the whole app's theme as a substitute.
3. Trigger export and complete the download/save dialog directly. Wait for the actual file to finish and verify it can be opened as a ZIP or HTML bundle; an export progress dialog is not a completed download. Avoid silently overwriting an unrelated existing download.
4. Preserve the ZIP bytes and extract into a dedicated directory. Reject archive entries that escape the extraction directory through absolute paths, parent traversal, or unsafe links. Keep the extracted HTML and its relative image/file paths together. If multiple HTML files exist, identify the requested page by its page ID, title, and contents instead of selecting the first file.
5. Verify that the export contains the latest approved changes and the expected content, code, and image-to-case mapping derived from the current report. Compare downloaded asset bytes or hashes with the ZIP members; verify every required asset resolves. Re-export when the content is stale, and resolve missing assets before printing. Preserve the original export while diagnosing either problem.

Save page identity, verified revision/content markers, actual export options, ZIP/HTML paths and hashes, and the asset inventory in review material. Do not add this operational record to the report body or copy signed download URLs, cookies, or tokens into it. If only HTML was requested, deliver this verified bundle without generating a PDF.

## Print the downloaded HTML

- Use the PDF skill for the applicable artifact workflow, dependencies, PDF rendering, and visual checks. Prefer the environment's bundled dependencies. Render the downloaded HTML locally using a browser/PDF renderer; headless Chromium is suitable for this artifact step. This is separate from UI automation of Notion's live export dialog.
- Use the local `notion_pdf.py print` and `verify` commands described in [common tools](common-tools.md) for reusable printing and checks. Pass document-specific settings when needed; defaults are starting values to inspect, not prescribed dimensions for every report. The tool cannot certify that an arbitrary HTML file came from the latest Notion export.
- Keep the extracted original untouched. Use a separate print copy or injected print stylesheet with **A4 landscape**, suitable margins, and browser headers/footers disabled. Retain the default font family and appearance. Record the renderer and actual print parameters rather than assuming the browser retained previous settings.
- Adjust only print presentation: proportional column fitting, line wrapping, page breaks, image bounds, and a print-only TOC layout. Preserve all report text, code, line-leading indentation, block order, links, captions, and image files. Never replace the export with HTML generated from a local Markdown draft or another assignment's renderer.
- Compare DOM text and code before and after print adjustments; verify indentation separately. Keep asset bytes and resolved link targets unchanged. Wait for fonts and every required image to load. Check horizontal overflow and ensure tall code/analysis rows can fit on a page. Keep each paired row together; long tables may break between rows and repeat their header. Keep headings and repeated input/output/screen labels with the content they introduce. Fit screenshots without cropping or distorting them.
- Group short input/output blocks with their labels and screenshot figures with their preceding labels in the print copy. Let code blocks taller than a page flow, independently of programming language. Treat paragraphs containing only whitespace as print-empty; CSS `:empty` alone misses newline-containing paragraphs. Preserve all original DOM text while making these layout changes.
- If a row cannot fit at a readable size, leave the PDF unverified and report the specific layout issue. Do not silently delete text, shrink the whole document to illegibility, split paired code/analysis across pages, or change the live Notion report to make printing pass.
- Produce a distinct candidate PDF or back up an existing destination before replacement. Retain the previous PDF until the candidate passes content and visual checks. Record hashes for the exported source and resulting PDF so review records refer to the file actually delivered.

## Verify and deliver

Check the actual PDF, not only the HTML or print command:

| Check | Required evidence |
|---|---|
| Origin and freshness | Verified page ID and latest changes in the downloaded HTML; original ZIP and extracted bytes retained |
| Paper | Every page measures A4 landscape; no browser URL/date/page-number headers or footers |
| Text and code | Required headings, prose, input/output, source cells and appendix survive text extraction; source matches the current report; indentation checked separately from whitespace-normalized text comparisons |
| Tables and flow | Paired code/analysis on the same page; no clipped columns, isolated headings/labels, or unintended blank/orphan pages |
| Assets | Expected images derived from the current report load locally and appear in their intended order in the PDF; screenshots remain readable and complete |
| Visual review | Render every page, inspect all-page contact sheets and affected/dense pages at readable resolution, then correct any failures and recheck the changed output |
| Prior files | Previous PDF remains recoverable; print styles/copies and review images are associated with the new PDF rather than an older file |

Do not hard-code a prior assignment's page ID, image count, table-row count, page count, column widths, or font sizes. Automated text/bounds checks and a successful print do not replace visual review. If a source conflict is discovered, distinguish it from export/render loss and leave the affected claim unresolved instead of silently editing code or prose.

Record each requested stage as verified, failed, or not verified: Notion content, HTML download, PDF printing, PDF content checks, PDF visual review. Keep native Notion PDF export, cover creation/merge, and actual submission separate. Report the result as **Notion HTML export → A4 landscape PDF**; do not call it a native Notion PDF export or a submitted assignment. Deliver links to the original HTML bundle and verified PDF, or state the exact remaining blocker. A native PDF dialog without an orientation selector does not block this HTML route.
