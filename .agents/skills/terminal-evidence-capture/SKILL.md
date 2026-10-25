---
name: terminal-evidence-capture
description: Capture real execution screenshots in the Antigravity IDE integrated terminal when the user needs image evidence of a command or program run, including entered input and observed output. Not for mock terminal images, general app screenshots, or screen recordings.
---

# Terminal evidence capture

Produce screenshots of **actual completed runs**. A rendered transcript or a terminal-looking image is not a screenshot.

Use the **Antigravity IDE integrated terminal** for this workspace's macOS captures. Select the separate IDE app by bundle ID `com.google.antigravity-ide`. Read [the IDE capture procedure](references/antigravity-ide.md) before operating the UI; it covers app selection, interactive execution, process status, and screenshot formats.

1. Identify the exact command, current source or executable, cases, and output location from the request and local artifacts. Use the requested cases; do not import a previous assignment's case count. If building is necessary, compile current source into a temporary binary outside the assignment's top-level directory and record the source hash and build command. Do not change source or report prose just to make a screenshot.
2. Create a dedicated IDE terminal window or panel without replacing the user's running terminal session. Enter input one line at a time and observe the next prompt or result before continuing. Capture only after the result and the **target program's actual exit status** are visible. Record input, observed output, and exit status separately from the image; a wrapper's successful exit is not proof that its child succeeded.
3. Capture the **specific IDE terminal window** through the available authorized UI tool. Inspect the raw capture before retaining it. Discard a capture of another app or one exposing unrelated content and retry using the correct window. Do not substitute Antigravity 2.0, macOS Terminal, or a fabricated terminal image for the selected IDE surface.
4. Inspect the returned image's actual format before naming or processing it. Preserve the original bytes; for JPEG, create a pixel-equivalent PNG as described in the reference. Crop only irrelevant chrome or blank margins with [`scripts/crop_and_verify.py`](scripts/crop_and_verify.py), which continues to require PNG input. Choose bounds from the actual image and visually check the crop. Preserve the command, every relevant input, final output, and errors; do not remove unfavorable output or alter text.
5. Compare observed output with the requested expectation or report claim. Deliver one clearly named PNG per case plus a compact record of source/build, input, observed result, and image paths. Report mismatches and incomplete cases explicitly. Uploading images to Notion or editing a report requires a separate request; a screenshot alone does not establish general program correctness.

If the IDE is missing, its UI is blocked, or a complete readable capture cannot be obtained, stop and report the concrete limitation. Do not repeatedly request permission for an unchanged tool restriction or switch terminal apps without user direction. An actual text execution log may be delivered, labeled as a log rather than a screenshot.
