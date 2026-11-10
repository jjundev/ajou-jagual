---
name: terminal-evidence-capture
description: Use when the user needs real execution screenshots from the Antigravity IDE integrated terminal, or needs existing terminal captures recropped or replaced for a report. Not for mock terminal images, general app screenshots, or screen recordings.
---

# Terminal evidence capture

Produce screenshots of **actual completed runs**. A rendered transcript or a terminal-looking image is not a screenshot.

Use the **Antigravity IDE integrated terminal** for this workspace's macOS captures. Select the separate IDE app by bundle ID `com.google.antigravity-ide`. Read [the IDE capture procedure](references/antigravity-ide.md) before capturing or recropping; it covers execution, formats, crop selection, and final-file checks.

## What belongs in each image

For this workspace's report images, use the following default. If the requested evidence is the shell command itself, retain that command in the final image too.

| Content | Raw capture and execution record | Final report image |
|---|---|---|
| Run command, shell username/host/path, setup commands, returned shell prompt | Preserve | Exclude |
| Program prompts, every relevant input, complete output and errors, target exit status | Preserve | Preserve, with readable padding |

Program prompts are part of the evidence. A program that reads numbers without printing a prompt needs only its actual echoed inputs; do not add an invented instruction or change source to produce one.

## Workflow

1. Identify the requested cases, evidence source, and output paths. For a new run, identify the current source/executable; build into a temporary directory if needed and record its identity and build command. For a recrop, inspect the original captures first and skip steps 2–3 when they contain the complete evidence. Reuse their execution provenance without claiming a fresh run. Do not change source or report prose just to make a screenshot.
2. Create a dedicated IDE terminal without replacing the user's session. Enter input one line at a time and observe each result. Capture only after the result and the **target program's actual exit status** are visible. Record input, output, and status separately; a wrapper's zero exit code is not proof of its child's success.
3. Capture the **specific IDE terminal window** through the authorized UI tool. Inspect the raw capture; retry if it is the wrong app or exposes unrelated content. Do not substitute Antigravity 2.0, macOS Terminal, or a fabricated image.
4. Preserve original bytes and detect their format. For JPEG, create a pixel-equivalent PNG as described in the reference. Use `python3 scripts/crop_and_verify.py` with that PNG and a new temporary output path. Choose bounds from the actual image using the table above; never reconstruct missing input from a log. Follow the reference's replacement procedure for existing PNGs.
5. Inspect **every final image**, including the files at their destination paths after replacement. Confirm all inputs, program prompts, complete results/errors/status, readable character edges, and shell-detail treatment from the content table. Compare with the original and execution record; check output against requested expectations or report claims. Pixel equality and matching logs do not establish content completeness. Update crop bounds, hashes, paths, and per-case visual-check results only after these checks. Report mismatches and incomplete cases explicitly.

Deliver the named PNGs and a compact execution/crop record. Uploading images to Notion or editing a report requires a separate request; a screenshot alone does not establish general program correctness.

If the IDE is missing, its UI is blocked, or a complete readable capture cannot be obtained, stop and report the concrete limitation. Do not repeatedly request permission for an unchanged tool restriction or switch terminal apps without user direction. An actual text execution log may be delivered, labeled as a log rather than a screenshot.
