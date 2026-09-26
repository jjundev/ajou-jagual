#!/usr/bin/env python3
"""Save a pixel-identical rectangular crop of a captured terminal PNG."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import uuid
from pathlib import Path

try:
    from PIL import Image, ImageChops
except ImportError as error:
    raise SystemExit("Pillow is required: install it in the active Python environment") from error


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def crop_and_verify(source: Path, output: Path, box: tuple[int, int, int, int]) -> dict:
    if source.resolve() == output.resolve():
        raise ValueError("source and output must be different files")
    if output.exists():
        raise FileExistsError(f"output already exists: {output}")
    with Image.open(source) as image:
        if image.format != "PNG":
            raise ValueError("source must be a PNG screenshot")
        width, height = image.size
        left, top, right, bottom = box
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise ValueError(f"crop box {box} is outside the {width}x{height} screenshot")
        expected = image.crop(box).convert("RGBA")
        cropped = image.crop(box)
        temporary = output.with_name(f".{output.name}.{uuid.uuid4().hex}.tmp.png")
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            cropped.save(temporary, format="PNG")
            with Image.open(temporary) as written:
                actual = written.convert("RGBA")
                if actual.size != expected.size or ImageChops.difference(actual, expected).getbbox():
                    raise RuntimeError("saved crop differs from source pixels")
            # The temporary file is a sibling, so this creates the final path
            # atomically without replacing a file created after the initial check.
            os.link(temporary, output)
        finally:
            temporary.unlink(missing_ok=True)
    return {
        "source": str(source),
        "source_sha256": sha256(source),
        "output": str(output),
        "output_sha256": sha256(output),
        "box": list(box),
        "size": [right - left, bottom - top],
        "pixel_identical": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="raw terminal-window PNG")
    parser.add_argument("output", type=Path, help="new cropped PNG; existing files are refused")
    parser.add_argument("--box", nargs=4, type=int, required=True,
                        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"),
                        help="crop rectangle in source pixels")
    args = parser.parse_args()
    try:
        result = crop_and_verify(args.source, args.output, tuple(args.box))
    except (OSError, ValueError, RuntimeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
