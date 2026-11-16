#!/usr/bin/env python3
"""
manifest + 조각 파일 → 정리노트/복습문제 HTML 두 개 (표준 라이브러리만 사용).

실행 폴더 구조:
  RUN/manifest.json
  RUN/sections/<section-id>.html   (섹션 안쪽: <article class="topic"> 들, <script> 가능)
  RUN/cards/<problem-id>.html      (<article class="card"> 하나)
조각 안의 {{NOTE_HREF}} / {{REVIEW_HREF}} 는 실제 파일명으로 바뀐다.
<script> 블록은 조각에서 빼서 </body> 앞({{SCRIPTS}})으로 모은다.
CLI: assemble.py --run RUN --out 복습노트/<range>
"""

from __future__ import annotations

import argparse
import shutil
import html
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import manifest as manifest_mod  # noqa: E402
from pack_layout import RANGE_RE, nfc

ASSETS = Path(__file__).resolve().parent.parent / "assets"
NOTES = ASSETS.parents[3] / "복습노트"
SHARED_ASSETS = NOTES / "_assets/problem-explain/v1"
SLOT_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.S | re.I)


class AssembleError(RuntimeError):
    pass


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def fill(template: str, values: dict[str, str]) -> str:
    missing = sorted(set(SLOT_RE.findall(template)) - values.keys())
    if missing:
        raise AssembleError(f"템플릿 슬롯 값 없음: {missing}")
    return SLOT_RE.sub(lambda mo: values[mo.group(1)], template)


def asset_root(out_dir: Path, *, assets_dir: Path | None = None) -> str:
    """Relative URL to the pinned assets, from the HTML's actual output directory."""
    assets = SHARED_ASSETS if assets_dir is None else assets_dir
    for name in ("pretendard/pretendard.css", "katex/katex.min.css", "katex/katex.min.js",
                 "katex/contrib/auto-render.min.js"):
        if not (assets / name).is_file():
            raise AssembleError(f"공용 자원 없음: {assets / name}")
    try:
        relative = Path(os.path.relpath(assets.resolve(), out_dir.resolve()))
    except ValueError as e:
        raise AssembleError("공용 자원과 HTML 출력은 같은 드라이브에 있어야 해요") from e
    return quote(relative.as_posix(), safe="/")


def split_scripts(fragment: str) -> tuple[str, list[str]]:
    scripts = SCRIPT_RE.findall(fragment)
    return SCRIPT_RE.sub("", fragment), scripts


def read_fragment(path: Path, m: dict) -> str:
    if not path.exists():
        raise AssembleError(f"조각 파일 없음: {path}")
    text = path.read_text(encoding="utf-8")
    return text.replace("{{NOTE_HREF}}", manifest_mod.note_name(m)).replace("{{REVIEW_HREF}}", manifest_mod.review_name(m))


def build_note(m: dict, run_dir: Path, out_dir: Path | None = None) -> str:
    sections, scripts = [], []
    for sec in m["sections"]:
        body, found = split_scripts(read_fragment(run_dir / "sections" / f"{sec['id']}.html", m))
        scripts += found
        sections.append(f'    <section id="{sec["id"]}"><h2>{esc(sec["title"])}</h2>\n{body.strip()}\n    </section>')
    return fill((ASSETS / "note-template.html").read_text(encoding="utf-8"), {
        "ASSET_ROOT": asset_root(out_dir if out_dir is not None else NOTES / m["range"]),
        "PAGE_TITLE": esc(f"{m['course']} 정리노트 {m['range']}"),
        "DESCRIPTION": esc(m["note_subtitle"]),
        "TOC": "".join(f'<a href="#{s["id"]}">{esc(s["short"])}</a>' for s in m["sections"]),
        "TITLE": esc(m["note_title"]),
        "SUBTITLE": esc(m["note_subtitle"]),
        "SECTIONS": "\n".join(sections),
        "FOOTER": m["footer_note"],
        "SCRIPTS": "\n".join(f"  {s}" for s in scripts),
        "RANGE": m["range"],
    })


def build_review(m: dict, run_dir: Path, out_dir: Path | None = None) -> str:
    parts, scripts = [], []
    populated={q['part'] for q in m['problems']}
    visible_parts=[part for part in m['parts'] if part['id'] in populated]
    for part in visible_parts:
        cards = []
        for q in (q for q in m["problems"] if q["part"] == part["id"]):
            body, found = split_scripts(read_fragment(run_dir / "cards" / f"{q['id']}.html", m))
            scripts += found
            cards.append(body.strip())
        parts.append(f'    <section id="{part["id"]}"><h2>{esc(part["title"])}</h2>\n' + "\n".join(cards) + "\n    </section>")
    result = fill((ASSETS / "review-template.html").read_text(encoding="utf-8"), {
        "ASSET_ROOT": asset_root(out_dir if out_dir is not None else NOTES / m["range"]),
        "PAGE_TITLE": esc(f"{m['course']} 복습문제 {m['range']}"),
        "DESCRIPTION": esc(m["review_title"]),
        "TOC": "".join(f'<a href="#{p["id"]}">{esc(p["short"])}</a>' for p in visible_parts),
        "NOTE_HREF": manifest_mod.note_name(m),
        "TITLE": esc(m["review_title"]),
        "INTRO": m["review_intro"],
        "PARTS": "\n".join(parts),
        "FOOTER": m["footer_review"],
        "SCRIPTS": "\n".join(f"  {s}" for s in scripts),
        "RANGE": m["range"],
    })
    from update_review import stamp_revision
    cards={q["id"]:read_fragment(run_dir / "cards" / f"{q['id']}.html",m).strip() for q in m["problems"]}
    return stamp_revision(result, m, cards)



def _sync_traces_and_sources(run_dir: Path, out_dir: Path) -> None:
    # trace 재생기 조각을 검사하는 check_html 이 <노트 폴더>/.pack/자료_복습팩/traces/ 에서 JSON 을 찾는다.
    traces = sorted((run_dir / "traces").glob("*.json"))
    if traces:
        dest = out_dir / ".pack" / "자료_복습팩" / "traces"
        dest.mkdir(parents=True, exist_ok=True)
        for t in traces:
            shutil.copyfile(t, dest / t.name)
    copy_pack_sources(run_dir, out_dir)


def assemble_note(run_dir: Path | str, out_dir: Path | str) -> Path:
    """정리노트 HTML과 manifest·trace 근거만 조립하고 기존 복습문제는 건드리지 않는다."""
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    m = manifest_mod.load(run_dir / "manifest.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    note_path = out_dir / manifest_mod.note_name(m)
    note_html = build_note(m, run_dir, out_dir)
    note_path.write_text(note_html, encoding="utf-8")
    _sync_traces_and_sources(run_dir, out_dir)
    return note_path


def assemble(run_dir: Path | str, out_dir: Path | str) -> tuple[Path, Path]:
    run_dir, out_dir = Path(run_dir), Path(out_dir)
    m = manifest_mod.load(run_dir / "manifest.json")
    out_dir.mkdir(parents=True, exist_ok=True)
    note_path = out_dir / manifest_mod.note_name(m)
    review_path = out_dir / manifest_mod.review_name(m)
    # 둘 다 만든 뒤에 쓴다: 조각이 하나라도 없으면 어느 파일도 바뀌지 않는다.
    note_html = build_note(m, run_dir, out_dir)
    review_html = build_review(m, run_dir, out_dir)
    note_path.write_text(note_html, encoding="utf-8")
    review_path.write_text(review_html, encoding="utf-8")
    _sync_traces_and_sources(run_dir, out_dir)
    return note_path, review_path


def copy_pack_sources(run_dir: Path, out_dir: Path) -> None:
    """확인문제(ds-concept-check)가 근거로 읽는 manifest.json·stt-summary.md 를 .pack/자료_복습팩/ 에 쓴다.

    요약은 summaries/stt-*.md 를 이름(날짜)순으로 이어 붙인다. 요약이 없으면 기존 stt-summary.md 를 그대로 둔다.
    """
    dest = Path(out_dir) / ".pack" / "자료_복습팩"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(run_dir) / "manifest.json", dest / "manifest.json")
    parts = sorted(Path(run_dir).glob("summaries/stt-*.md"))
    if parts:
        text = "\n\n---\n\n".join(p.read_text(encoding="utf-8").rstrip("\n") for p in parts) + "\n"
        (dest / "stt-summary.md").write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--note-only", action="store_true", help="정리노트 HTML만 조립하고 기존 복습문제는 보존")
    args = ap.parse_args(argv)
    try:
        target = Path(args.out).resolve()
        if not args.note_only and nfc(target.parent.name) == "복습노트" and RANGE_RE.fullmatch(nfc(target.name)):
            raise AssembleError("작업 폴더를 준비하려면 release_review.py prepare를 사용하세요.")
        paths = (assemble_note(args.run, args.out),) if args.note_only else assemble(args.run, args.out)
        for path in paths:
            print(path)
    except (AssembleError, manifest_mod.ManifestError) as e:
        print(f"assemble 실패: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
