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
3. Obtain the target program's actual exit status immediately after it terminates. If a shell wrapper or PTY logger is used, collect the child's status inside it, print that value visibly, and retain the wrapper command. A logger's or shell's own zero exit code cannot replace the program's status. Keep terminal behavior interactive so prompts and echoed input remain visible.
4. Capture after the final output and status are visible. Make sure the command, all relevant inputs and outputs, and errors fit the captured surface. If they do not, adjust the dedicated terminal or capture complete, clearly identified portions before claiming the case is captured; do not omit the beginning or failed output.
5. Where a terminal transcript is available, compare it with the requested input sequence and expected results. Inspect the screenshot itself as well: a matching text log does not prove the correct window was captured or the text is readable.

The final record should identify the IDE app/window, source or executable, build and run commands, case input, observed output, target exit status, transcript path when available, original capture format/path, final PNG path, and crop verification. Record mismatches rather than changing source or evidence to hide them.

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

Choose crop bounds from the observed image and pass `crop_source` to [crop_and_verify.py](../scripts/crop_and_verify.py). Preserve original capture bytes, the PNG copy when conversion was needed, and the cropped PNG. Inspect the crop and retain its recorded bounds, hashes, and pixel-identical result. Crop only window decoration and irrelevant blank margins.

## Focused verification cases

When changing this procedure, check separate scenarios: both Antigravity apps installed; prompts requiring sequential input; a target process returning nonzero through a wrapper; JPEG returned by the screenshot tool; and IDE access denied. Distinguish a document review or simulated scenario from a live UI run. A previous successful capture is evidence for that run, not proof that a revised skill was executed successfully.
