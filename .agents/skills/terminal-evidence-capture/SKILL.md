---
name: terminal-evidence-capture
description: Capture real terminal screenshots when the user needs image evidence of a command or program run, including entered input and observed output. Not for mock terminal images, general app screenshots, or screen recordings.
---

# Terminal evidence capture

Produce screenshots of **actual completed runs**. A rendered transcript or a terminal-looking image is not a screenshot.

1. Identify the exact command, current source or executable, cases, and output location from the request and local artifacts. Use the requested cases; do not import a previous assignment's case count. If building is necessary, compile current source into a temporary binary outside the assignment's top-level directory and record the source hash and build command. Do not change source or report prose just to make a screenshot.
2. Run each case in an accessible terminal UI. When input must be visible, enter it interactively and wait for the prompt to update before the next input; a fast multiline paste can make input appear beside the wrong prompt. Capture only after the result and process exit are visible. Record the case input, observed result, and exit status separately from the image.
3. Target the **specific terminal window**, not whichever app happens to be foreground. On macOS, a permitted `screencapture -l <window-id>` can capture a selected window; if Terminal itself is unavailable, an accessible IDE terminal may work. Inspect the raw capture before retaining it. Discard a capture of another app or one exposing unrelated content and retry using the correct window. Do not substitute a fabricated terminal image when window capture is unavailable.
4. Crop only irrelevant chrome or blank margins. Choose bounds from the actual image, then use [`scripts/crop_and_verify.py`](scripts/crop_and_verify.py) to make a pixel-identical crop. Keep the raw capture until the cropped image has been visually checked. Verify that the command, every relevant input, final output, and any error remain readable; do not remove unfavorable output or alter text.
5. Compare observed output with the requested expectation or report claim. Deliver one clearly named PNG per case plus a compact record of source/build, input, observed result, and image paths. Report mismatches and incomplete cases explicitly. Uploading images to Notion or editing a report requires a separate request; a screenshot alone does not establish general program correctness.

If a real screenshot cannot be captured after trying the available authorized terminal and capture surfaces, stop the screenshot attempt and report the concrete limitation. An actual text execution log may be delivered, labeled as a log rather than a screenshot.
