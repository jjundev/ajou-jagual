"""확인문제 소스 폴더(.pack/자료_확인문제_<범위>_<슬러그>) → 팩 루트의 확인문제 HTML."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import _paths
import interaction  # DS_REVIEW_PACK/scripts 를 sys.path 에 넣는다
import render

import assemble  # noqa: E402


class BuildError(RuntimeError):
    pass


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
            raise BuildError(f"팩이 없어 근거가 없습니다: {pack / name}")
    manifest = json.loads(_paths.find_nfc(pack, "manifest.json").read_text(encoding="utf-8"))
    objectives = objectives_doc["objectives"]
    known = {o["id"] for o in objectives}
    for item in items_doc["items"]:
        if item["objective"] not in known:
            raise BuildError(f"문항 {item['id']} 의 목표 {item['objective']} 가 objectives.json 에 없습니다")
    return dict(range=objectives_doc["range"], slug=objectives_doc["slug"], objectives=objectives,
                items=items_doc["items"], manifest=manifest, pack_root=pack_root)


def render_page(src: Path) -> str:
    s = load_source(src)
    range_, slug = s["range"], s["slug"]
    by_id = {o["id"]: o for o in s["objectives"]}
    cards = "".join(render.card_html(it, by_id[it["objective"]], n) for n, it in enumerate(s["items"], 1))
    title = f"{range_} 확인문제 — 이번 수업 개념 확인"
    template = (_paths.DS_REVIEW_PACK / "assets" / "review-template.html").read_text(encoding="utf-8")
    page = assemble.fill(template, dict(
        PAGE_TITLE=f"{s['manifest']['course']} 확인문제 {range_}",
        DESCRIPTION=title, TITLE=title,
        TOC='<a href="#check">확인</a>',
        NOTE_HREF=f"정리노트_{range_}_{slug}.html",
        INTRO=f"<p>이번 수업에서 처음 배운 개념을 {len(s['items'])}문항으로 확인해요. 고르면 바로 채점돼요.</p>",
        PARTS=f'<section id="check"><h2>확인문제</h2>{cards}</section>',
        FOOTER="<p>Claude가 강의 근거로 만든 문항이에요. 근거: 강의록·수업 녹음 요약.</p>",
        SCRIPTS="", RANGE=f"{range_}-확인"))
    return interaction.install(page, output_name(range_, slug).removesuffix(".html"))


def build(src: Path) -> Path:
    s = load_source(src)
    try:
        page = render_page(src)
    except ValueError as e:
        raise BuildError(str(e)) from e
    out = Path(s["pack_root"]) / output_name(s["range"], s["slug"])
    out.write_text(page, encoding="utf-8")
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("사용법: python3 build.py <.pack/자료_확인문제_범위_슬러그>", file=sys.stderr)
        return 2
    try:
        print(build(Path(argv[1])))
    except BuildError as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
