"""발행 전 규칙 검사. 문제마다 "[코드] <id>: <설명>" 한 줄, 없으면 []."""
from __future__ import annotations

import re
import sys
import unicodedata
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

import _paths
import tree as treemod
from build import BuildError, load_source

SLIDE_RE = re.compile(r"^S\d+ p\d+(–\d+)?$")
NEG_WORDS = ("않은", "아닌", "틀린", "옳지")
STRICT_KINDS = ("절차 결과", "규칙 적용")
SOURCE_PREFIXES = ("stt:", "note:", "bank:")
DUP_WINDOW = 20


def _text(html: str) -> str:
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]*>", " ", html or ""))).strip()


class _CardStems(HTMLParser):
    """article.card 안 .problem 요소의 텍스트를 모은다."""

    def __init__(self):
        super().__init__()
        self.stems: list[str] = []
        self._depth = 0
        self._buf: list[str] = []
        self._in_card = 0

    def handle_starttag(self, tag, attrs):
        cls = (dict(attrs).get("class") or "").split()
        if tag == "article" and "card" in cls:
            self._in_card += 1
        if self._depth:
            self._depth += 1
        elif self._in_card and "problem" in cls:
            self._depth = 1
            self._buf = []

    def handle_endtag(self, tag):
        if tag == "article" and self._in_card:
            self._in_card -= 1
        if self._depth:
            self._depth -= 1
            if not self._depth:
                self.stems.append(re.sub(r"\s+", " ", "".join(self._buf)).strip())

    def handle_data(self, data):
        if self._depth:
            self._buf.append(data)


def _card_texts(pack_root: Path) -> list[str]:
    out = []
    for f in sorted(Path(pack_root).iterdir()):
        name = unicodedata.normalize("NFC", f.name)
        if f.is_file() and name.startswith("복습문제_") and name.endswith(".html"):
            p = _CardStems()
            p.feed(f.read_text(encoding="utf-8"))
            out.extend(p.stems)
    return out


def _is_dup(stem: str, cards: list[str]) -> bool:
    if len(stem) < DUP_WINDOW:
        return any(stem in c for c in cards)
    return any(stem[i:i + DUP_WINDOW] in c
               for i in range(len(stem) - DUP_WINDOW + 1) for c in cards)


def _nospace(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def check(src: Path) -> list[str]:
    s = load_source(Path(src))
    objectives, items, manifest = s["objectives"], s["items"], s["manifest"]
    problems: list[str] = []

    def add(code, id_, msg):
        problems.append(f"[{code}] {id_}: {msg}")

    topics = {t["id"] for sec in manifest.get("sections", []) for t in sec.get("topics", [])}
    preview = manifest.get("preview_topic")
    forbidden = [w.lower() for w in manifest.get("forbidden_outside_preview", [])]
    obj_by_id = {o["id"]: o for o in objectives}

    # 목표 단위
    if not items:
        add("count", "-", "문항이 하나도 없어요.")
    elif len(items) > 16:
        add("count", "-", f"문항이 {len(items)}개예요. 16개 이하로 줄여 주세요.")
    per_obj: dict[str, int] = {o["id"]: 0 for o in objectives}
    for it in items:
        per_obj[it["objective"]] = per_obj.get(it["objective"], 0) + 1
    for o in objectives:
        n = per_obj[o["id"]]
        if n == 0:
            add("count", o["id"], "이 목표에 문항이 없어요.")
        elif n >= 3:
            add("count", o["id"], f"이 목표에 문항이 {n}개예요. 1~2개만 두세요.")
        if o.get("topic_id") not in topics:
            add("topic", o["id"], f"topic_id {o.get('topic_id')!r} 가 manifest 토픽에 없어요.")
        elif o.get("topic_id") == preview:
            add("topic", o["id"], "미리보기 토픽은 확인 목표로 쓸 수 없어요.")
        slide = (o.get("source") or {}).get("slide", "")
        if not SLIDE_RE.match(slide or ""):
            add("source", o["id"], f"source.slide {slide!r} 형식이 'S7 p8' 또는 'S7 p8–9' 가 아니에요.")

    cards = _card_texts(s["pack_root"])
    mcq_answers: list[str] = []
    negatives = 0

    for it in items:
        iid = it["id"]
        obj = obj_by_id.get(it["objective"], {})
        stem = _text(it.get("stem_html", ""))
        title = it.get("title", "")
        fmt = it.get("format")
        opts = it.get("options") or []

        if obj.get("kind") in STRICT_KINDS and fmt != "short":
            add("format", iid, f"'{obj['kind']}' 목표의 문항은 단답(short)이어야 해요.")

        correct = None
        if fmt == "mcq":
            ids = [o.get("id") for o in opts]
            if len(opts) != 4 or ids != ["A", "B", "C", "D"]:
                add("mcq-shape", iid, f"보기는 id가 A B C D 인 4개여야 해요(현재 {ids}).")
            if it.get("answer") not in ids:
                add("mcq-shape", iid, f"answer {it.get('answer')!r} 가 보기에 없어요.")
            else:
                correct = next(o for o in opts if o.get("id") == it["answer"])
            mcq_answers.append(it.get("answer"))
            for o in opts:
                oid = o.get("id")
                if not (o.get("why") or "").strip():
                    add("explain", iid, f"보기 {oid} 에 why 가 비어 있어요.")
                if oid != it.get("answer"):
                    if not (o.get("misconception") or "").strip():
                        add("explain", iid, f"오답 보기 {oid} 에 misconception 이 비어 있어요.")
                    if not str(o.get("source") or "").startswith(SOURCE_PREFIXES):
                        add("explain", iid, f"오답 보기 {oid} 의 source 는 stt: note: bank: 로 시작해야 해요.")
            if correct is not None:
                ans = _nospace(correct.get("text", ""))
                if len(ans) >= 2 and ans in _nospace(title):
                    add("title-leak", iid, "제목에 정답 보기 문구가 그대로 들어 있어요.")

        if any(w in title or w in stem for w in NEG_WORDS):
            negatives += 1

        if forbidden:
            bag = [title, stem]
            for o in opts:
                bag += [_text(o.get("text", "")), _text(o.get("why", "")), _text(o.get("misconception", ""))]
            bag += [_text(x) for x in it.get("solution", [])]
            low = "\n".join(bag).lower()
            for w in forbidden:
                if w in low:
                    add("forbidden", iid, f"미리보기 전용 낱말 '{w}' 이 들어 있어요.")

        if fmt == "short":
            spec = it.get("compute")
            if not spec:
                add("compute", iid, "단답 문항에 compute 가 없어요.")
            else:
                try:
                    got = treemod.compute(spec, it.get("tree"))
                except Exception as e:  # noqa: BLE001
                    add("compute", iid, f"compute 를 계산하지 못했어요: {e}")
                else:
                    want = (it.get("answer") or {}).get("canonical")
                    if got != want:
                        add("compute", iid, f"compute 결과 {got!r} 가 answer.canonical {want!r} 와 달라요.")
        elif fmt == "mcq" and it.get("compute") and correct is not None:
            spec = it["compute"]
            try:
                got = treemod.compute(spec, it.get("tree"))
            except Exception as e:  # noqa: BLE001
                add("compute", iid, f"compute 를 계산하지 못했어요: {e}")
            else:
                if got != str(correct.get("value")):
                    add("compute", iid, f"compute 결과 {got!r} 가 정답 보기 value {correct.get('value')!r} 와 달라요.")

        if stem and _is_dup(stem, cards):
            add("duplicate", iid, "발문이 기존 복습문제 카드와 20자 이상 겹쳐요.")

        if re.search(r"\bstyle\s*=", it.get("stem_html", ""), re.I):
            add("style", iid, "stem_html 에 style 속성을 쓸 수 없어요.")

    if len(mcq_answers) >= 4:
        counts = [mcq_answers.count(c) for c in "ABCD"]
        if max(counts) - min(counts) > 1:
            add("balance", "-", f"객관식 정답 위치가 한쪽에 몰렸어요(A~D {counts}).")
    if negatives * 4 > len(items):
        add("negative", "-", f"부정형 발문이 {negatives}개예요. 전체 {len(items)}개의 4분의 1 이하여야 해요.")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("사용법: python3 check.py <.pack/자료_확인문제_범위_슬러그>", file=sys.stderr)
        return 2
    try:
        problems = check(Path(argv[1]))
    except BuildError as e:
        print(str(e), file=sys.stderr)
        return 1
    print("\n".join(problems) if problems else "OK")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
