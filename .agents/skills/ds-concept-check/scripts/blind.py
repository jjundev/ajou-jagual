"""블라인드 사본(make)·대조 장부(record)·상태(status). 풀이자는 정답이 없는 사본만 본다."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from html import unescape
from pathlib import Path

import render
import tree
from build import BuildError, load_source

ID_RE = re.compile(r"^q\d+$")


def item_hash(item: dict, objective: dict) -> str:
    """문항 + 화면에 함께 보이는 목표 근거 줄(concept·source.slide). 어느 쪽이 바뀌어도 장부가 무효가 된다."""
    shown = dict(concept=objective.get("concept"), slide=(objective.get("source") or {}).get("slide"))
    blob = json.dumps(dict(item=item, objective=shown), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def source_line(objective: dict) -> str:
    """render._problem 이 카드에 찍는 근거 줄과 같은 글."""
    return f"{(objective.get('source') or {}).get('slide', '')} · 확인: {objective['concept']}"


def _plain(html: str) -> str:
    """태그 제거 텍스트. 그림(svg)은 [그림: aria-label] 로 바꾼다."""
    def fig(m):
        label = re.search(r'aria-label="([^"]*)"', m.group(0))
        return f" [그림: {unescape(label.group(1)) if label else ''}] "
    html = re.sub(r"<svg\b.*?</svg>", fig, html or "", flags=re.S)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]*>", " ", html))).strip()


def _tree_line(t: list) -> str:
    """그림이 보여 주는 만큼만: 루트와 부모→자식 간선(왼쪽/오른쪽). 칸 번호·빈 자리는 쓰지 않는다."""
    parts = [f"루트 {t[0]}"] if tree._has(t, 0) else []
    for i in range(len(t)):
        if not tree._reachable(t, i):
            continue
        for side, j in (("왼쪽", 2 * i + 1), ("오른쪽", 2 * i + 2)):
            if tree._has(t, j):
                parts.append(f"{t[i]}의 {side} 자식 {t[j]}")
    return "[그림: 트리 — " + "; ".join(parts) + "]"


def _card(item: dict, objective: dict) -> str:
    lines = [f"## {item['id']}. {item['title']}", "", _plain(item.get("stem_html", ""))]
    if item.get("tree"):
        lines += ["", _tree_line(item["tree"])]
    lines += ["", source_line(objective), ""]
    if item["format"] == "mcq":
        lines += [f"{o['id']}. {_plain(o['text'])}" for o in item["options"]]
    else:
        lines.append("(값을 쓰시오)")
    return "\n".join(lines) + "\n"


def make(src: Path, out: Path, only: set[str] | None = None) -> None:
    s = load_source(src)
    objs = {o["id"]: o for o in s["objectives"]}
    items = [it for it in s["items"] if only is None or it["id"] in only]
    head = "# 확인문제 블라인드 사본\n\n문항마다 답을 하나 고르세요. 결과는 표로 적습니다.\n"
    Path(out).write_text(head + "\n" + "\n".join(_card(it, objs[it["objective"]]) for it in items),
                         encoding="utf-8")


def parse_answers(text: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2 or not ID_RE.match(cells[0]):
            continue
        if cells[0] in out:
            raise ValueError(f"문항 {cells[0]} 이(가) 표에 두 번 있어요")
        cells += [""] * (4 - len(cells))
        out[cells[0]] = dict(answer=cells[1], rationale=cells[2], objection=cells[3])
    return out


def _load(ledger: Path) -> dict:
    ledger = Path(ledger)
    return json.loads(ledger.read_text(encoding="utf-8")) if ledger.is_file() else {}


def record(src: Path, answers_md: Path, ledger: Path, round_no: int) -> dict:
    s = load_source(src)
    objs = {o["id"]: o for o in s["objectives"]}
    items = {it["id"]: it for it in s["items"]}
    answers = parse_answers(Path(answers_md).read_text(encoding="utf-8"))
    data = _load(ledger)
    for id_, a in answers.items():
        if id_ not in items:
            raise ValueError(f"소스에 없는 문항: {id_}")
        data[id_] = dict(answer=a["answer"], objection=a["objection"], hash=item_hash(items[id_], objs[items[id_]["objective"]]), round=round_no)
    Path(ledger).write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return data


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(s))).strip().lower()


def _accepted(item: dict) -> set[str]:
    if item["format"] == "mcq":
        return {_norm(item["answer"])}
    ans = item["answer"]
    canon = ans["canonical"]
    return {_norm(v) for v in [canon, *ans.get("accepted", []), *render.accepted_variants(canon)]}


def status(src: Path, ledger: Path) -> list[str]:
    data = _load(ledger)
    s = load_source(src)
    objs = {o["id"]: o for o in s["objectives"]}
    out: list[str] = []
    for item in s["items"]:
        id_ = item["id"]
        row = data.get(id_)
        if row is None:
            out.append(f"{id_}: 장부에 없음")
            continue
        if row.get("hash") != item_hash(item, objs[item["objective"]]):
            out.append(f"{id_}: 수정됨")
            continue
        if _norm(row["answer"]) not in _accepted(item):
            correct = item["answer"] if item["format"] == "mcq" else item["answer"]["canonical"]
            out.append(f"{id_}: 답 불일치 ({row['answer']} ≠ {correct})")
        if row.get("objection", "").strip():
            out.append(f"{id_}: 이의 — {row['objection'].strip()}")
    return out


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="blind.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make"); m.add_argument("src"); m.add_argument("out"); m.add_argument("--only")
    r = sub.add_parser("record"); r.add_argument("src"); r.add_argument("answers"); r.add_argument("ledger")
    r.add_argument("--round", type=int, required=True)
    s = sub.add_parser("status"); s.add_argument("src"); s.add_argument("ledger")
    a = p.parse_args(argv[1:])
    try:
        if a.cmd == "make":
            make(Path(a.src), Path(a.out), set(a.only.split(",")) if a.only else None)
        elif a.cmd == "record":
            record(Path(a.src), Path(a.answers), Path(a.ledger), a.round)
        else:
            lines = status(Path(a.src), Path(a.ledger))
            print("\n".join(lines) if lines else "OK")
            return 1 if lines else 0
    except (BuildError, ValueError) as e:
        print(str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
