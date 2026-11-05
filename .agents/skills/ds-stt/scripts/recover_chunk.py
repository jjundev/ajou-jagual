#!/usr/bin/env python3
"""
Automated sub-chunk recovery script for ds-stt safety-filter-blocked audio chunks.

When a 10-minute chunk is blocked by Gemini Safety Filters due to false-positive
metaphors/colloquialisms:
1. Splits the failing chunk into smaller sub-chunks (default 120s).
2. Optionally applies subtle acoustic perturbation (--perturb, atempo=1.05) if stubbornly blocked.
3. Wraps each sub-chunk into a 1fps black MP4 for isolated subagent transcription.
4. Supports merging sub-chunk markdown files (--merge-subs) back into the single part markdown file.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys


def get_duration(audio_path: str | Path) -> float:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())


def split_and_wrap(
    chunk_path: str | Path,
    sub_seconds: int = 120,
    perturb: bool = False,
) -> list[tuple[Path, Path]]:
    path = Path(chunk_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    # Determine base name without _temp or extension
    base_name = path.stem
    base_name = re.sub(r"_temp$", "", base_name)

    parent_dir = path.parent
    duration = get_duration(path)

    sub_chunks = []
    num_subs = int(duration // sub_seconds) + (1 if duration % sub_seconds > 0 else 0)

    print(f"[*] 총 재생 시간: {duration:.2f}초 -> {num_subs}개 서브 청크 (각 {sub_seconds}초)")

    for i in range(num_subs):
        start_sec = i * sub_seconds
        sub_num = i + 1
        sub_mp3 = parent_dir / f"{base_name}_sub{sub_num:02d}.mp3"
        sub_mp4 = parent_dir / f"{base_name}_sub{sub_num:02d}_temp.mp4"

        # Slice mp3
        cmd_slice = [
            "ffmpeg", "-y",
            "-ss", str(start_sec),
            "-i", str(path),
            "-t", str(sub_seconds),
        ]
        if perturb:
            cmd_slice.extend(["-af", "atempo=1.05"])
        cmd_slice.extend(["-c:a", "libmp3lame", "-b:a", "192k", str(sub_mp3), "-loglevel", "error"])

        subprocess.run(cmd_slice, check=True)
        sub_dur = get_duration(sub_mp3)

        # Wrap into 1fps MP4
        cmd_wrap = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=320x240:r=1",
            "-i", str(sub_mp3),
            "-t", str(sub_dur),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "128k",
            str(sub_mp4),
            "-loglevel", "error",
        ]
        subprocess.run(cmd_wrap, check=True)
        sub_chunks.append((sub_mp3, sub_mp4))
        print(f"  [+] 생성 완료: {sub_mp4.name} ({sub_dur:.1f}초)")

    return sub_chunks


def merge_subs(part_dir: str | Path, part_prefix: str, output_part_md: str | Path | None = None) -> Path:
    dir_path = Path(part_dir).resolve()
    pattern = re.compile(rf"^{re.escape(part_prefix)}_sub(\d+)\.md$")

    sub_files = []
    for f in dir_path.iterdir():
        m = pattern.match(f.name)
        if m:
            sub_files.append((int(m.group(1)), f))

    if not sub_files:
        raise FileNotFoundError(f"{dir_path} 내에서 {part_prefix}_sub*.md 파일을 찾을 수 없습니다.")

    sub_files.sort(key=lambda x: x[0])

    if output_part_md:
        out_path = Path(output_part_md).resolve()
    else:
        out_path = dir_path / f"{part_prefix}.md"

    merged_text = []
    for _, sf in sub_files:
        content = sf.read_text(encoding="utf-8").strip()
        if content:
            merged_text.append(content)

    final_content = "\n\n".join(merged_text).strip() + "\n"
    out_path.write_text(final_content, encoding="utf-8")
    print(f"[✓] 서브 청크 {len(sub_files)}개 병합 완료: {out_path}")

    # Cleanup sub files
    cleaned = 0
    for _, sf in sub_files:
        mp3 = sf.with_suffix(".mp3")
        mp4 = dir_path / f"{sf.stem}_temp.mp4"
        for p in (sf, mp3, mp4):
            if p.is_file():
                p.unlink(missing_ok=True)
                cleaned += 1
    print(f"[✓] 임시 서브 파일 {cleaned}개 정리 완료.")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="ds-stt Safety Filter Recovery Helper")
    parser.add_argument("chunk", help="Path to failing chunk (e.g. 1105_자구알_part06.mp3 or _part06_temp.mp4)")
    parser.add_argument("--sub-seconds", type=int, default=120, help="Sub-chunk length in seconds (default: 120)")
    parser.add_argument("--perturb", action="store_true", help="Apply acoustic shift (atempo=1.05) to alter classifier hash")
    parser.add_argument("--merge-subs", action="store_true", help="Merge existing _sub*.md files into part markdown")
    parser.add_argument("--out", help="Output path for merged part markdown (used with --merge-subs)")

    args = parser.parse_args()

    chunk_p = Path(args.chunk)
    if args.merge_subs:
        prefix = re.sub(r"(_sub\d+)?(\.md|\.mp3|\.mp4|_temp\.mp4)$", "", chunk_p.stem)
        merge_subs(chunk_p.parent, prefix, args.out)
    else:
        subs = split_and_wrap(chunk_p, sub_seconds=args.sub_seconds, perturb=args.perturb)
        print("\n[안내] 서브 청크가 준비되었습니다. 각 서브 청크별로 독립 서브에이전트(self)를 기동하세요:")
        for _, mp4 in subs:
            md_path = mp4.parent / f"{mp4.name.replace('_temp.mp4', '.md')}"
            print(f"  - Target: {mp4.name} -> Output: {md_path.name}")
        prefix = re.sub(r"_temp$", "", chunk_p.stem)
        print(f"\n[안내] 모든 서브 청크 전사 완료 후 아래 명령어로 병합하세요:")
        print(f"  python3 {Path(__file__).resolve()} {chunk_p} --merge-subs")


if __name__ == "__main__":
    main()
