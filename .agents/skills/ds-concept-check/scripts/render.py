"""문항(item) → 카드 HTML. 생명과학 review_interaction.build_model 이 읽는 마크업을 따른다."""
from __future__ import annotations

import html
import json

import tree

SEP = ", "
JOINERS = (",", " ", "", "→")


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def accepted_variants(canonical: str) -> list[str]:
    """", " 로 나뉘는 순서열이면 다른 구분자로 이은 변형들(정답 자신 제외). 아니면 []."""
    parts = canonical.split(SEP)
    if len(parts) < 2 or not all(p.strip() for p in parts):
        return []
    out: list[str] = []
    for joiner in JOINERS:
        v = joiner.join(parts)
        if v != canonical and v not in out:
            out.append(v)
    return out


def _problem(item: dict, objective: dict, choices: str) -> str:
    body = item["stem_html"]
    if item.get("tree"):
        svg = tree.tree_svg(item["tree"], f"fig-{item['id']}", f"{item['title']} 트리")
        body += f'<figure class="figure">{svg}</figure>'
    slide = objective.get("source", {}).get("slide", "")
    body += f'<p class="source">{esc(slide)} · 확인: {esc(objective["concept"])}</p>'
    # 보기 목록은 .problem 안에 둔다(review-prompt.js problemText 가 .problem 안의 .choices 를 지운다).
    return f'<div class="problem">{body}{choices}</div>'


def _mcq(item: dict) -> tuple[str, str, str, str]:
    choices = "".join(f'<li data-choice="{esc(o["id"])}">{esc(o["text"])}</li>' for o in item["options"])
    steps = []
    for o in item["options"]:
        if o["id"] == item["answer"]:
            text = esc(o["why"])
        else:
            text = f'"{esc(o["misconception"])}" — {esc(o["why"])}'
        steps.append(f'<li data-explains="{esc(o["id"])}">{text}</li>')
    return ("", f'<ol class="choices">{choices}</ol>', "",
            f'<ol class="steps">{"".join(steps)}</ol><p class="answer">정답: {esc(item["answer"])}</p>')


def _short(item: dict) -> tuple[str, str, str, str]:
    canonical = item["answer"]["canonical"]
    accepted: list[str] = []
    for a in list(item["answer"].get("accepted", [])) + accepted_variants(canonical):
        if a != canonical and a not in accepted:
            accepted.append(a)
    data = json.dumps(dict(canonical=canonical, accepted=accepted, case_sensitive=False), ensure_ascii=False)
    cid = esc(item["id"])
    attrs = f' data-format="short" data-short-answer="{esc(data)}"'
    inputs = (f'<div class="short-input"><label for="answer-{cid}">답</label>'
              f'<input type="text" id="answer-{cid}" autocomplete="off">'
              '<button class="btn check-answer" type="button">답 확인</button></div>')
    steps = "".join(f"<li>{esc(s)}</li>" for s in item["solution"])
    return attrs, "", inputs, f'<ol class="steps">{steps}</ol><p class="answer">정답: {esc(canonical)}</p>'


def card_html(item: dict, objective: dict, number: int) -> str:
    attrs, choices, after, solution = _short(item) if item["format"] == "short" else _mcq(item)
    return (f'<article class="card" id="{esc(item["id"])}" data-objective="{esc(objective["id"])}"{attrs}>'
            f'<h3>Q{number}. {esc(item["title"])}</h3>'
            + _problem(item, objective, choices) + after
            + f'<details class="solution"><summary>풀이 보기</summary>{solution}</details></article>')
