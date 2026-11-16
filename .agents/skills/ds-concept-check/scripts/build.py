"""확인문제 소스 폴더(.pack/자료_확인문제_<범위>_<슬러그>) → 팩 루트의 확인문제 HTML."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import _paths
import interaction  # DS_REVIEW_PACK/scripts 를 sys.path 에 넣는다
import render

import assemble  # noqa: E402


class BuildError(RuntimeError):
    pass


BRAND_ANCHOR = '<strong class="brand">복습문제</strong>'
BRAND = '<strong class="brand">확인문제</strong>'


def swap_brand(page: str) -> str:
    """복습문제 템플릿 상단 바 brand 를 확인문제로. 앵커가 정확히 한 번이 아니면 멈춘다."""
    n = page.count(BRAND_ANCHOR)
    if n != 1:
        raise BuildError(f"템플릿 상단 바 brand 앵커가 {n}번 있어요(정확히 1번이어야 해요): {BRAND_ANCHOR}")
    return page.replace(BRAND_ANCHOR, BRAND)


def output_name(range_: str, slug: str) -> str:
    return f"확인문제_{range_}_{slug}.html"


def _read_json(path: Path) -> dict:
    if not path.is_file():
        raise BuildError(f"파일이 없습니다: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_source(src: Path) -> dict:
    src = Path(src)
    pack_root = src.parent.parent
    objectives_doc = _read_json(src / "objectives.json")
    items_doc = _read_json(src / "items.json")
    pack = _paths.find_nfc(src.parent, "자료_복습팩")
    if pack is None:
        raise BuildError(f"팩이 없어 근거가 없습니다: {src.parent / '자료_복습팩'}")
    for name in ("manifest.json", "stt-summary.md"):
        if _paths.find_nfc(pack, name) is None:
            raise BuildError(f"팩이 없어 근거가 없습니다: {pack / name} ({name} 없음)")
    manifest = json.loads(_paths.find_nfc(pack, "manifest.json").read_text(encoding="utf-8"))
    for key in ("range", "slug"):
        if objectives_doc.get(key) != manifest.get(key):
            raise BuildError(f"objectives.json 의 {key} {objectives_doc.get(key)!r} 가 "
                             f"manifest 의 {key} {manifest.get(key)!r} 와 달라요")
    objectives = objectives_doc["objectives"]
    known = {o["id"] for o in objectives}
    for item in items_doc["items"]:
        if item["objective"] not in known:
            raise BuildError(f"문항 {item['id']} 의 목표 {item['objective']} 가 objectives.json 에 없습니다")
    return dict(range=objectives_doc["range"], slug=objectives_doc["slug"], objectives=objectives,
                items=items_doc["items"], manifest=manifest, pack_root=pack_root)


def note_name(range_: str, slug: str) -> str:
    return f"정리노트_{range_}_{slug}.html"


def check_note_anchors(pack_root: Path, name: str, topic_ids: list[str]) -> Path:
    """풀이의 정리노트 링크가 깨지지 않게, 노트 HTML 과 토픽 앵커가 실제로 있는지 본다."""
    note = _paths.find_nfc(pack_root, name)
    if note is None:
        raise BuildError(f"정리노트 HTML이 없어 링크를 걸 수 없어요: {Path(pack_root) / name}")
    text = note.read_text(encoding="utf-8")
    missing = [t for t in dict.fromkeys(topic_ids) if f'id="{t}"' not in text]
    if missing:
        raise BuildError(f"정리노트 {name} 에 앵커가 없어요: " + ", ".join(f"#{t}" for t in missing))
    return note


def render_page(src: Path, *, assets_dir: Path | None = None) -> str:
    s = load_source(src)
    range_, slug = s["range"], s["slug"]
    by_id = {o["id"]: o for o in s["objectives"]}
    note = check_note_anchors(s["pack_root"], note_name(range_, slug),
                              [by_id[it["objective"]]["topic_id"] for it in s["items"]]).name
    cards = "".join(render.card_html(it, by_id[it["objective"]], n, note) for n, it in enumerate(s["items"], 1))
    title = f"{range_} 확인문제 — 이번 수업 개념 확인"
    template = (_paths.DS_REVIEW_PACK / "assets" / "review-template.html").read_text(encoding="utf-8")
    page = assemble.fill(template, dict(
        ASSET_ROOT=assemble.asset_root(s["pack_root"], assets_dir=assets_dir),
        PAGE_TITLE=assemble.esc(f"{s['manifest']['course']} 확인문제 {range_}"),
        DESCRIPTION=assemble.esc(title), TITLE=assemble.esc(title),
        TOC='<a href="#check">확인</a>',
        NOTE_HREF=assemble.esc(note),
        INTRO=f"이번 수업에서 처음 배운 개념을 {len(s['items'])}문항으로 확인해요. 고르면 바로 채점돼요.",
        PARTS=f'<section id="check"><h2>확인문제</h2>{cards}</section>',
        FOOTER="<p>AI가 강의록과 수업 녹음 요약을 바탕으로 만든 문항이에요.</p>",
        SCRIPTS="", RANGE=assemble.esc(f"{range_}-확인")))
    return interaction.install(swap_brand(page), output_name(range_, slug).removesuffix(".html"))


def build(src: Path, *, assets_dir: Path | None = None) -> Path:
    s = load_source(src)
    try:
        page = render_page(src, assets_dir=assets_dir)
    except (ValueError, assemble.AssembleError) as e:
        raise BuildError(str(e)) from e
    out = Path(s["pack_root"]) / output_name(s["range"], s["slug"])
    out.write_text(page, encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path)
    parser.add_argument("--assets-dir", type=Path)
    args = parser.parse_args(argv[1:])
    try:
        print(build(args.src, assets_dir=args.assets_dir))
    except BuildError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
