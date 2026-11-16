# Antigravity IDE terminal capture

## Select the separate IDE app

Use the authorized computer-use tool. With `cua_repl`, select the app directly:

```javascript
var ide = await cua.getApp("com.google.antigravity-ide");
```

Keep the tool's first-use call separate and read the returned documentation before continuing. `com.google.antigravity-ide` is **Antigravity IDE**; `com.google.antigravity` is the separate Antigravity 2.0 app. Selecting the display name `Antigravity` can open the latter. Verify the selected app and window before entering commands.

If app selection or capture is denied, report the exact restriction. User authorization does not by itself change a tool's app restrictions. Follow the active computer-use API and permission rules rather than substituting another UI automation mechanism.

## Create and target a dedicated terminal

Open the IDE's Terminal menu and use **New Terminal Window** when available. Otherwise create a new integrated terminal panel and expose enough of it to show the complete run. Use fresh UI observations to locate controls; menu indexes, window IDs, coordinates, font size, and pixel bounds are not stable across sessions.

Target the newly created terminal window or panel explicitly. Leave existing editor content and running terminal sessions intact. Choose the working directory and cases from the current task, and keep temporary executables outside the assignment's top-level directory. Do not carry over a particular assignment's compiler, paths, test count, or dimensions.

## Execute and retain evidence

1. Run the current authorized command. If compilation is needed, retain the source hash, build command, diagnostics, and executable identity.
2. Enter each input line separately. After submission, observe the prompt or result before sending the next line. A single multiline paste can place input beside the wrong prompt.
3. Capture after the program terminates and its final output is visible. Do not type `echo $?` or any other status command into the IDE terminal, before or after the capture. Make sure the command, all relevant inputs and outputs, and errors fit the captured surface. If they do not, adjust the dedicated terminal or capture complete, clearly identified portions before claiming the case is captured; do not omit the beginning or failed output.
4. Obtain the target program's actual exit status outside the IDE terminal: run the same executable with the same stdin through the shell tool, compare its stdout with the captured screen, and record the status as `exit_status_separate_run`. If a PTY logger is used for a transcript, have it write the child's status to its log file, not to the terminal. A logger's or shell's own zero exit code cannot replace the program's status. Keep the IDE run interactive so prompts and echoed input remain visible.
5. Where a terminal transcript is available, compare it with the requested input sequence and expected results. Inspect the screenshot itself as well: a matching text log does not prove the correct window was captured or the text is readable.

The final record should identify the IDE app/window, source or executable, build and run commands, case input, observed output, target exit status and how it was obtained (separate run), transcript path when available, original capture format/path, final PNG path, and crop verification. Include per-case visual-check results for complete input/prompts, complete output/errors, no exit-status or `echo` line, excluded shell details (or the requested command-evidence exception), and the reviewed destination file. Record mismatches rather than changing source or evidence to hide them.

## Preserve the capture format and pixels

A screenshot API may return **JPEG bytes even if the caller chose a `.png` filename**. Detect the actual format from the image, save original bytes with the matching extension, and keep that original. Renaming a JPEG to `.png` does not convert it and will fail the PNG-only crop helper.

For a JPEG capture, decode it once and save a PNG copy without resizing, retouching, or changing text. Verify equality between the decoded original pixels and the PNG pixels. This preserves the pixels returned by the screenshot tool; it does not undo JPEG compression or prove equality with an uncompressed display framebuffer.

For example, with distinct, discovered `raw_path` and `png_path` values:

```python
from pathlib import Path
from PIL import Image, ImageChops

raw_path = Path(raw_path)
png_path = Path(png_path)
with Image.open(raw_path) as original:
    if original.format == "PNG":
        crop_source = raw_path
    elif original.format == "JPEG":
        if png_path.exists() or png_path.resolve() == raw_path.resolve():
            raise FileExistsError("Use a new PNG path; preserve the original capture")
        pixels = original.convert("RGB")
        pixels.save(png_path, format="PNG")
        with Image.open(png_path) as written:
            if ImageChops.difference(pixels, written.convert("RGB")).getbbox():
                raise RuntimeError("PNG pixels differ from the decoded capture")
        crop_source = png_path
    else:
        raise ValueError(f"Unsupported capture format: {original.format}")
```

## Select and verify the final crop

Keep command and provenance evidence in the raw capture and execution record. For final report images, apply the content table in [SKILL.md](../SKILL.md#what-belongs-in-each-image): start before the first program prompt or echoed input and end after the program's last output line. Exclude the launch line, shell username/host/path, setup commands, and returned shell prompt. If the task requests command evidence, include that command. Preserve program output that happens to contain a path or command; it is not shell decoration.

Choose bounds from each observed image, with enough padding for entire characters on every edge. Check the first and last input lines, all output/error rows, the final summary, any exit-status or `echo` line that must not be there, and any fragments of an excluded shell line at the edges. Do not reuse a previous case's coordinates, dimensions, or input count without inspecting this case. Crop unused margins so the evidence remains readable; if a new capture needs larger text, adjust the dedicated terminal before capturing rather than redrawing or enlarging screenshot text.

For an existing screenshot correction, open the raw original before deciding anything is missing. If the original has all the evidence, recrop it without rerunning the program. If it is incomplete or illegible, a crop cannot repair it: capture again when a new run is authorized, otherwise report the limitation. A transcript can help locate missing evidence but cannot supply pixels for an input line that was not captured. If excluding shell text would also cut required evidence on the same row, retain the evidence and explain the limitation, or arrange a new capture with a separable launch line. Do not erase, paint over, splice, or retype image text.

Use `python3 scripts/crop_and_verify.py SOURCE_PNG NEW_OUTPUT_PNG --box LEFT TOP RIGHT BOTTOM` from the skill directory, substituting discovered paths and bounds. Preserve the raw capture and conversion PNG. The helper verifies that the selected rectangle is pixel-identical; it does **not** decide whether the rectangle contains all required inputs or whether shell details remain.

When replacing an existing final PNG:

1. Write the candidate to a new temporary path; the helper intentionally refuses to overwrite files. Preserve recoverability of the previous final file through version control or a backup.
2. Open every candidate and compare it with its raw capture and input/output record. Verify complete prompts and inputs, output/errors, no exit-status line, readable edges, and the requested shell-detail treatment. Keep actual program prompts; when the program has none, the numeric input lines alone are correct.
3. Replace only the requested final PNGs. Open the files at the actual destination paths and check them again, including the first input and the last output line. A reviewed temporary file is not proof that the intended destination was updated.
4. Recompute destination hashes and verify destination pixels against the original crop. Update existing manifests and per-case crop records together: source/output paths, bounds, dimensions, hashes, pixel check, and visual-check results must describe the delivered files. Leave unrelated report content and remote uploads unchanged.

Only mark a case complete after both pixel and visual checks. A matching hash or execution log does not compensate for cropped-away input, clipped characters, missing errors, or an unwanted shell line. If one image fails, correct that image and repeat its checks before reporting completion.

## Focused verification cases

When changing this procedure, check the affected scenarios:

- Capture: both Antigravity apps installed; prompts requiring sequential input; a target program that exits nonzero (screen shows only its output, record holds the separate run's status); JPEG returned by the screenshot tool; IDE access denied.
- Crop/replacement: an original with complete numeric input but no program prompts; an original with program prompts; a candidate missing its first input despite a matching transcript/hash; unwanted launch/returned shell lines; and a destination file or crop record that still describes the previous image. Include a task that explicitly requests command evidence to check that exception.

For crop-only changes, exercise the helper on existing raw captures in a temporary directory and inspect every result without modifying deliverables. Distinguish document review, simulated decision exercises, and live UI runs. A previous successful capture is evidence for that run, not proof that a revised skill was executed successfully.
