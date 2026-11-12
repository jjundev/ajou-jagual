"""알고리즘 trace JSON 의 스키마 검사와 도장.

trace JSON 한 개가 단계별 그림(SVG)과 재생기의 단일 원천이다.
이 모듈은 읽기·lint·sha 만 맡는다. 그리는 코드는 뒤 작업에서 이 파일에 붙는다.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

VERSION = 1
MAX_STEPS = 40
MAX_NODES = 31
MAX_CELLS = 20
KEY_RANGE = (2, 4)
KINDS = ("bintree", "array", "stack", "list")
ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


class TraceError(ValueError):
    """lint 오류가 있는 trace. code 는 첫 오류 코드."""

    def __init__(self, code: str, message: str = ""):
        super().__init__(f"{code}: {message}" if message else code)
        self.code = code


def trace_sha(trace: dict) -> str:
    """정규 JSON(키 정렬, 공백 없음) sha256 의 앞 12자."""
    canon = json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canon.encode()).hexdigest()[:12]


def load(path: Path) -> dict:
    """JSON 을 읽고 lint 한다. 오류가 있으면 첫 코드로 TraceError."""
    trace = json.loads(Path(path).read_text(encoding="utf-8"))
    codes = lint(trace)
    if codes:
        raise TraceError(codes[0], f"{path}: {', '.join(codes)}")
    return trace


def _tree_nodes(struct: dict) -> dict:
    nodes = struct.get("nodes")
    return nodes if isinstance(nodes, dict) else {}


def _lint_structure(struct, codes: list[str]) -> None:
    kind = struct.get("kind") if isinstance(struct, dict) else None
    if kind not in KINDS:
        codes.append("unknown-kind")
        return
    if kind == "bintree":
        nodes = _tree_nodes(struct)
        if len(nodes) > MAX_NODES:
            codes.append("too-many-nodes")
        refs = [struct.get("root")]
        for children in nodes.values():
            if isinstance(children, dict):
                refs += [children.get("l"), children.get("r")]
        if any(ref is not None and ref not in nodes for ref in refs):
            codes.append("missing-node")
    elif kind == "array":
        size = struct.get("size")
        if isinstance(size, int) and size > MAX_CELLS:
            codes.append("too-many-cells")


def _lint_state(struct: dict, state, codes: list[str]) -> None:
    kind = struct.get("kind")
    if kind == "bintree" and isinstance(state, dict):
        nodes = _tree_nodes(struct)
        null_at = state.get("null_at")
        refs = [state.get("cur")] + list(state.get("done") or []) + list(state.get("changed") or [])
        if isinstance(null_at, dict):
            refs.append(null_at.get("node"))
        if any(ref is not None and ref not in nodes for ref in refs):
            codes.append("missing-node")
    elif kind == "array" and isinstance(state, dict):
        values = state.get("values")
        if isinstance(values, list) and len(values) > MAX_CELLS:
            codes.append("too-many-cells")


def lint(trace: dict) -> list[str]:
    """오류 코드 목록(처음 발견한 순서, 중복 없음). 빈 목록이면 통과. 던지지 않는다."""
    codes: list[str] = []
    if trace.get("version") != VERSION:
        codes.append("version")
    tid = trace.get("id")
    if not (isinstance(tid, str) and ID_RE.fullmatch(tid)):
        codes.append("id")

    structs = trace.get("structures")
    by_id = {}
    for struct in structs if isinstance(structs, list) else []:
        _lint_structure(struct, codes)
        if isinstance(struct, dict):
            by_id[struct.get("id")] = struct

    steps = trace.get("steps")
    steps = steps if isinstance(steps, list) else []
    if not steps:
        codes.append("no-steps")
    if len(steps) > MAX_STEPS:
        codes.append("too-many-steps")
    if not KEY_RANGE[0] <= sum(1 for s in steps if isinstance(s, dict) and s.get("key")) <= KEY_RANGE[1]:
        codes.append("key-count")
    for step in steps:
        if not isinstance(step, dict):
            continue
        if "$" in str(step.get("text", "")):
            codes.append("dollar")
        state = step.get("state")
        for sid, value in (state if isinstance(state, dict) else {}).items():
            if sid not in by_id:
                codes.append("unknown-structure")
            else:
                _lint_state(by_id[sid], value, codes)
    return list(dict.fromkeys(codes))


# ---------------------------------------------------------------- 그리기
# 모든 수치는 스펙 고정값. 출력은 입력만으로 정해져야 한다(재렌더 바이트 비교).

NODE_R = 16
CUR_R = 21
LAYER_H = 56
MARGIN = 20
ARR_W, ARR_H = 40, 32
STK_W, STK_H = 52, 28
STK_GAP = 24
NULL_LEN = 24
LABEL_H = 18
FONT = 13
MAX_W = 720
INNER_W = 680


def _arr_w(cells: int) -> float:
    return min(ARR_W, INNER_W / max(1, cells))


def _list_pitch(cells: int) -> float:
    return min(ARR_W + STK_GAP, INNER_W / max(1, cells))


def _n(x: float) -> str:
    """좌표를 소수 1자리로 반올림하고 끝의 .0 을 지운다."""
    s = f"{round(x, 1):.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


def _esc(text) -> str:
    return (str(text).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _tree_info(struct: dict) -> tuple[dict, dict]:
    """(중위 순위, 깊이). 루트에서 닿는 노드만. 재귀 없이 명시 스택."""
    nodes = _tree_nodes(struct)
    rank: dict = {}
    depth: dict = {}
    stack: list = []
    cur = struct.get("root")
    d = 0
    path_depth: list = []
    while cur is not None or stack:
        while cur is not None and cur in nodes:
            stack.append(cur)
            path_depth.append(d)
            depth[cur] = d
            cur = (nodes[cur] or {}).get("l")
            d += 1
        if not stack:
            break
        cur = stack.pop()
        d = path_depth.pop()
        rank[cur] = len(rank)
        cur = (nodes[cur] or {}).get("r")
        d += 1
    return rank, depth


def _cell_w(struct: dict) -> float:
    return min(44, 680 / max(1, len(_tree_nodes(struct))))


def tree_layout(structure: dict) -> dict:
    """노드 -> (x, y). x 는 중위 순서, y 는 깊이."""
    rank, depth = _tree_info(structure)
    cw = _cell_w(structure)
    return {k: (MARGIN + (rank[k] + 0.5) * cw, MARGIN + NODE_R + depth[k] * LAYER_H) for k in rank}


def _tree_size(struct: dict) -> tuple[float, float]:
    rank, depth = _tree_info(struct)
    width = len(rank) * _cell_w(struct)
    height = NODE_R + (max(depth.values()) if depth else 0) * LAYER_H + NODE_R + NULL_LEN + 18
    return width, height


def _state_of(step: dict, sid: str):
    state = step.get("state")
    return state.get(sid) if isinstance(state, dict) else None


def _edge(a, b, r=NODE_R) -> str:
    dx, dy = b[0] - a[0], b[1] - a[1]
    dist = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = dx / dist, dy / dist
    return f"M{_n(a[0] + ux * r)} {_n(a[1] + uy * r)}L{_n(b[0] - ux * r)} {_n(b[1] - uy * r)}"


def _arrow(x1, y, x2, cls) -> str:
    """수평 화살표. 머리도 <path>."""
    sign = 1 if x2 >= x1 else -1
    return (f'<path class="{cls}" d="M{_n(x1)} {_n(y)}H{_n(x2)} '
            f'M{_n(x2 - sign * 8)} {_n(y - 4)}L{_n(x2)} {_n(y)}L{_n(x2 - sign * 8)} {_n(y + 4)}"/>')


def _text(cls, x, y, s, anchor="middle") -> str:
    return f'<text class="{cls}" x="{_n(x)}" y="{_n(y)}" font-size="{FONT}" text-anchor="{anchor}">{_esc(s)}</text>'


def _max_len(trace: dict, sid: str, key=None) -> int:
    best = 0
    for step in trace.get("steps", []):
        v = _state_of(step, sid)
        if key is not None and isinstance(v, dict):
            v = v.get(key)
        if isinstance(v, list):
            best = max(best, len(v))
    return best


def _blocks(trace: dict) -> tuple[list, float, float]:
    """구조별 배치 [(struct, x, y, extra)]와 viewBox 크기. 모든 단계에서 같다."""
    blocks: list = []
    y = float(MARGIN)
    right = 0.0
    tree_block = None
    for struct in trace.get("structures", []):
        kind = struct.get("kind")
        if kind == "bintree":
            w, h = _tree_size(struct)
            tree_block = {"struct": struct, "x": MARGIN, "y": y, "h": h, "right": MARGIN + w}
            blocks.append(tree_block)
            right = max(right, MARGIN + w)
            y += h
        elif kind == "stack":
            cap = max(_max_len(trace, struct["id"]), 1)
            need = LABEL_H + cap * STK_H
            label_w = len(struct.get("label", "")) * FONT
            side_right = (tree_block["right"] + STK_GAP + max(STK_W, label_w)) if tree_block else 0
            if tree_block is not None and not tree_block.get("stack") and side_right + MARGIN <= MAX_W:
                x = tree_block["right"] + STK_GAP
                bottom = max(tree_block["y"] + tree_block["h"], tree_block["y"] + need)
                tree_block["stack"] = True
                blocks.append({"struct": struct, "x": x, "y": tree_block["y"], "bottom": bottom})
                y = max(y, bottom)
            else:
                x = MARGIN
                blocks.append({"struct": struct, "x": x, "y": y, "bottom": y + need})
                y += need
            right = max(right, x + max(STK_W, label_w))
        elif kind == "array":
            cells = max(struct.get("size") or 0, _max_len(trace, struct["id"], "values"))
            blocks.append({"struct": struct, "x": MARGIN, "y": y, "cells": cells})
            right = max(right, MARGIN + cells * _arr_w(cells))
            y += LABEL_H + ARR_H + 22
        elif kind == "list":
            cells = max(_max_len(trace, struct["id"], "order"), 1)
            blocks.append({"struct": struct, "x": MARGIN, "y": y, "cells": cells})
            pitch = _list_pitch(cells)
            right = max(right, MARGIN + (cells - 1) * pitch + pitch * ARR_W / (ARR_W + STK_GAP))
            y += LABEL_H + ARR_H + 22 + 12
    return blocks, right + MARGIN, y + MARGIN


def _draw_tree(blk, state, parts) -> None:
    struct = blk["struct"]
    pos = tree_layout(struct)
    oy = blk["y"] - MARGIN
    pos = {k: (x, y + oy) for k, (x, y) in pos.items()}
    nodes = _tree_nodes(struct)
    state = state if isinstance(state, dict) else {}
    edges = []
    for k in pos:
        for side in ("l", "r"):
            c = (nodes.get(k) or {}).get(side)
            if c in pos:
                edges.append(_edge(pos[k], pos[c]))
    if edges:
        parts.append(f'<path class="fig-ink" d="{"".join(edges)}"/>')
    changed = set(state.get("changed") or [])
    done = set(state.get("done") or [])
    for k, (x, y) in pos.items():
        cls = "fig-accent" if k in changed else "fig-ink"
        parts.append(f'<circle class="{cls}" cx="{_n(x)}" cy="{_n(y)}" r="{NODE_R}"/>')
        parts.append(_text("fig-text", x, y + 4.5, k))
        if k in done:
            parts.append(f'<circle class="fig-dot" cx="{_n(x)}" cy="{_n(y + NODE_R + 6)}" r="4"/>')
    cur = state.get("cur")
    if cur in pos:
        parts.append(f'<circle class="fig-accent" cx="{_n(pos[cur][0])}" cy="{_n(pos[cur][1])}" r="{CUR_R}"/>')
    na = state.get("null_at")
    if isinstance(na, dict) and na.get("node") in pos:
        x, y = pos[na["node"]]
        x += -11 if na.get("side") == "l" else 11
        y0 = y + 12
        parts.append(f'<path class="fig-ink" stroke-dasharray="4 3" d="M{_n(x)} {_n(y0)}V{_n(y0 + NULL_LEN)}"/>')
        parts.append(_text("fig-muted", x, y0 + NULL_LEN + 14, "NULL"))


def _draw_stack(blk, state, parts) -> None:
    struct = blk["struct"]
    x, top, bottom = blk["x"], blk["y"], blk["bottom"]
    if struct.get("label"):
        parts.append(_text("fig-muted", x, top + 12, struct["label"], "start"))
    for i, v in enumerate(state if isinstance(state, list) else []):
        y = bottom - (i + 1) * STK_H
        parts.append(f'<rect class="fig-ink" x="{_n(x)}" y="{_n(y)}" width="{STK_W}" height="{STK_H}"/>')
        parts.append(_text("fig-text", x + STK_W / 2, y + STK_H / 2 + 4.5, v))


def _draw_array(blk, state, parts) -> None:
    struct = blk["struct"]
    x0, y0 = blk["x"], blk["y"]
    state = state if isinstance(state, dict) else {}
    values = state.get("values") or []
    hi = set(state.get("hi") or [])
    if struct.get("label"):
        parts.append(_text("fig-muted", x0, y0 + 12, struct["label"], "start"))
    cy = y0 + LABEL_H
    aw = _arr_w(blk["cells"])
    for i in range(blk["cells"]):
        x = x0 + i * aw
        cls = "fig-accent" if i in hi else "fig-ink"
        parts.append(f'<rect class="{cls}" x="{_n(x)}" y="{_n(cy)}" width="{_n(aw)}" height="{ARR_H}"/>')
        if i < len(values):
            parts.append(_text("fig-text", x + aw / 2, cy + ARR_H / 2 + 4.5, values[i]))
    for name, idx in (state.get("ptr") or {}).items():
        parts.append(_text("fig-muted", x0 + idx * aw + aw / 2, cy + ARR_H + 15, name))


def _draw_list(blk, state, parts) -> None:
    struct = blk["struct"]
    x0, y0 = blk["x"], blk["y"]
    state = state if isinstance(state, dict) else {}
    order = state.get("order") or []
    changed = {tuple(e) for e in state.get("edge_changed") or []}
    step = _list_pitch(blk["cells"])
    nw = step * ARR_W / (ARR_W + STK_GAP)
    if struct.get("label"):
        parts.append(_text("fig-muted", x0, y0 + 12, struct["label"], "start"))
    cy = y0 + LABEL_H + 12
    idx = {v: i for i, v in enumerate(order)}
    for i, v in enumerate(order):
        x = x0 + i * step
        parts.append(f'<rect class="fig-ink" x="{_n(x)}" y="{_n(cy)}" width="{_n(nw)}" height="{ARR_H}"/>')
        parts.append(_text("fig-text", x + nw / 2, cy + ARR_H / 2 + 4.5, v))
    edges = [(a, b) for a, b in zip(order, order[1:])]
    edges += [e for e in sorted(changed) if e not in edges and e[0] in idx and e[1] in idx]
    for a, b in edges:
        cls = "fig-accent" if (a, b) in changed else "fig-ink"
        ia, ib = idx[a], idx[b]
        ym = cy + ARR_H / 2
        if abs(ia - ib) == 1:
            xa = x0 + ia * step + (nw if ib > ia else 0)
            xb = x0 + ib * step + (0 if ib > ia else nw)
            parts.append(_arrow(xa, ym, xb, cls))
        else:
            xa, xb = x0 + ia * step + nw / 2, x0 + ib * step + nw / 2
            peak = cy - 10
            parts.append(f'<path class="{cls}" d="M{_n(xa)} {_n(cy)}Q{_n((xa + xb) / 2)} {_n(peak - 8)} {_n(xb)} {_n(cy)} '
                         f'M{_n(xb - 4)} {_n(cy - 8)}L{_n(xb)} {_n(cy)}L{_n(xb + 4)} {_n(cy - 8)}"/>')
    for name, node in (state.get("ptr") or {}).items():
        if node in idx:
            parts.append(_text("fig-muted", x0 + idx[node] * step + nw / 2, cy + ARR_H + 15, name))


_DRAW = {"bintree": _draw_tree, "stack": _draw_stack, "array": _draw_array, "list": _draw_list}


def _svg(svg_id: str, w: float, h: float, label: str, body: list, hidden: bool = False) -> str:
    hid = " hidden" if hidden else ""
    return (f'<svg id="{_esc(svg_id)}" viewBox="0 0 {_n(w)} {_n(h)}" role="img" '
            f'aria-label="{_esc(label)}"{hid}>{"".join(body)}</svg>')


def step_svg(trace: dict, index: int, svg_id: str, *, hidden: bool = False) -> str:
    """index 번째 단계(0부터)의 SVG. viewBox 는 모든 단계에서 같다."""
    step = trace["steps"][index]
    blocks, w, h = _blocks(trace)
    parts: list = []
    for blk in blocks:
        struct = blk["struct"]
        _DRAW[struct["kind"]](blk, _state_of(step, struct["id"]), parts)
    return _svg(svg_id, w, h, step.get("text", ""), parts, hidden)


def shadow_svg(trace: dict, structure_id: str, svg_id: str) -> str:
    """트리 노드를 아래 수직선으로 내려 중위 순서를 보이는 그림."""
    struct = next((s for s in trace["structures"] if s.get("id") == structure_id), None)
    if struct is None or struct.get("kind") != "bintree":
        raise ValueError(f"shadow_svg: bintree structure {structure_id!r} not found")
    rank, depth = _tree_info(struct)
    pos = tree_layout(struct)
    nodes = _tree_nodes(struct)
    base = MARGIN + NODE_R + (max(depth.values()) if depth else 0) * LAYER_H + NODE_R + 24  # 가장 깊은 노드 아래
    parts: list = []
    edges = []
    for k in pos:
        for side in ("l", "r"):
            c = (nodes.get(k) or {}).get(side)
            if c in pos:
                edges.append(_edge(pos[k], pos[c]))
    if edges:
        parts.append(f'<path class="fig-ink" d="{"".join(edges)}"/>')
    order = sorted(pos, key=lambda k: rank[k])
    for k in order:
        x, y = pos[k]
        parts.append(f'<circle class="fig-ink" cx="{_n(x)}" cy="{_n(y)}" r="{NODE_R}"/>')
        parts.append(_text("fig-text", x, y + 4.5, k))
        parts.append(f'<path class="fig-ink" stroke-dasharray="4 3" d="M{_n(x)} {_n(y + NODE_R)}V{_n(base)}"/>')
        parts.append(_text("fig-text", x, base + 15, k))
    left = pos[order[0]][0] - 10 if order else MARGIN
    right = pos[order[-1]][0] + 10 if order else MARGIN
    parts.append(_arrow(left, base + 28, right, "fig-accent"))
    w = MARGIN + len(order) * _cell_w(struct) + MARGIN
    h = base + 28 + MARGIN
    label = f"나무의 숫자를 아래로 내리면 왼쪽부터 {', '.join(order)}이 차례로 놓여요"
    return _svg(svg_id, w, h, label, parts)


# ---------------------------------------------------------------------------
# HTML 조각 (노트 재생기 / 문제설명 대표 그림)
# ---------------------------------------------------------------------------

_BTN_GHOST = ('style="justify-self:auto;min-width:0;padding:0 16px;border:1px solid var(--line)"')
_BTN_PRIMARY = 'style="justify-self:auto;min-width:0;padding:0 16px"'

_PLAYER_JS = """(function () {
  var id = %s;
  var svgs = [];
  var k = 1;
  var el;
  while ((el = document.getElementById('trace-' + id + '-s' + k))) { svgs.push(el); k += 1; }
  var items = document.getElementById('trace-' + id + '-steps').getElementsByTagName('li');
  var num = document.getElementById('trace-' + id + '-n');
  var text = document.getElementById('trace-' + id + '-text');
  var reset = document.getElementById('trace-' + id + '-reset');
  var prev = document.getElementById('trace-' + id + '-prev');
  var next = document.getElementById('trace-' + id + '-next');
  var i = 0;
  function show(n) {
    i = Math.max(0, Math.min(svgs.length - 1, n));
    for (var j = 0; j < svgs.length; j += 1) {
      if (j === i) { svgs[j].removeAttribute('hidden'); } else { svgs[j].setAttribute('hidden', ''); }
    }
    num.textContent = (i + 1) + '/' + svgs.length;
    text.textContent = items[i].textContent;
    prev.disabled = i === 0;
    reset.disabled = i === 0;
    next.disabled = i === svgs.length - 1;
  }
  reset.addEventListener('click', function () { show(0); });
  prev.addEventListener('click', function () { show(i - 1); });
  next.addEventListener('click', function () { show(i + 1); });
  show(0);
})();"""


def _key_indexes(trace: dict) -> list[int]:
    return [i for i, s in enumerate(trace["steps"]) if s.get("key")]


def _wrapper_open(trace: dict, target: str) -> str:
    return (f'<div class="trace-block" data-trace="{_esc(trace["id"])}" '
            f'data-trace-sha="{trace_sha(trace)}" data-trace-target="{target}">')


def _render_note(trace: dict) -> str:
    tid = trace["id"]
    steps = trace["steps"]
    total = len(steps)
    keys = _key_indexes(trace)
    out = [_wrapper_open(trace, "note")]
    out.append(f'<div class="widget" id="widget-trace-{tid}"><h4>직접 해 보기: {_esc(trace.get("title", ""))}</h4>')
    out.append('<p class="widget-help">이전·다음을 누르면 한 단계씩 그림과 설명이 바뀌어요.</p>')
    out.append('<div class="controls" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center">'
               f'<button class="btn btn-ghost" id="trace-{tid}-reset" type="button" {_BTN_GHOST}>처음부터</button>'
               f'<button class="btn btn-ghost" id="trace-{tid}-prev" type="button" {_BTN_GHOST}>이전</button>'
               f'<button class="btn btn-primary" id="trace-{tid}-next" type="button" {_BTN_PRIMARY}>다음</button>'
               '</div>')
    for i in range(total):
        out.append(step_svg(trace, i, f"trace-{tid}-s{i + 1}", hidden=i > 0))
    out.append(f'<p class="readout"><b id="trace-{tid}-n">1/{total}</b> '
               f'<span id="trace-{tid}-text" aria-live="polite">{_esc(steps[0]["text"])}</span></p>')
    out.append('<div class="widget-static" hidden>')
    for n, i in enumerate(keys, 1):
        out.append(f'<figure class="figure">{step_svg(trace, i, f"widget-trace-{tid}-static-{n}")}'
                   f'<figcaption>단계 {i + 1}. {_esc(steps[i]["text"])}</figcaption></figure>')
    rows = "".join(f'<tr><td>{i + 1}</td><td>{_esc(steps[i]["text"])}</td></tr>' for i in keys)
    out.append(f'<div class="table-wrap"><table><tr><th>단계</th><th>설명</th></tr>{rows}</table></div>')
    out.append('</div></div>')
    out.append(f'<ol class="steps" id="trace-{tid}-steps" data-trace="{_esc(tid)}">'
               + "".join(f'<li>{_esc(s["text"])}</li>' for s in steps) + '</ol>')
    out.append('</div>')
    out.append(f'<!-- /trace {tid} -->')
    out.append(f'<script id="widget-trace-{tid}-ui">{_PLAYER_JS % json.dumps(tid)}</script>')
    return "\n".join(out) + "\n"


def _render_explain(trace: dict) -> str:
    tid = trace["id"]
    steps = trace["steps"]
    out = [_wrapper_open(trace, "explain")]
    for n, i in enumerate(_key_indexes(trace), 1):
        out.append(f'<figure class="figure">{step_svg(trace, i, f"trace-{tid}-k{n}")}'
                   f'<figcaption>단계 {i + 1}. {_esc(steps[i]["text"])}</figcaption></figure>')
    out.append('</div>')
    out.append(f'<!-- /trace {tid} -->')
    return "\n".join(out) + "\n"


def render(trace: dict, target: str) -> str:
    """target 'note' 은 단계 재생기, 'explain' 은 key 단계 정적 그림."""
    if target == "note":
        return _render_note(trace)
    if target == "explain":
        return _render_explain(trace)
    raise ValueError(f"render: unknown target {target!r}")


_BLOCK_RE = re.compile(
    r'<div class="trace-block" data-trace="([^"]*)"[^>]*? data-trace-target="(note|explain)">')
_SCRIPT_RE = r'<script id="widget-trace-%s-ui">.*?</script>'


def _split_fragment(rendered: str, tid: str) -> tuple[str, str]:
    """render 결과를 (표지까지의 블록, 스크립트 또는 빈 문자열)로 가른다."""
    marker = f"<!-- /trace {tid} -->"
    cut = rendered.index(marker) + len(marker)
    m = re.search(_SCRIPT_RE % re.escape(tid), rendered[cut:], re.S)
    return rendered[:cut], (m.group(0) if m else "")


def verify(html: str, traces_dir: Path) -> list[tuple[str, str]]:
    """문서 속 trace 조각이 JSON 과 일치하는지 본다. (code, id) 목록.

    JSON 이 없으면 trace-missing, 있어도 읽기·lint 에 실패하거나 조각이 다르면 trace-stale.
    스크립트는 조립 때 </body> 앞으로 옮겨지므로 블록(표지까지)과 따로 비교한다.
    """
    out: list[tuple[str, str]] = []
    for m in _BLOCK_RE.finditer(html):
        tid, target = m.group(1), m.group(2)
        json_path = Path(traces_dir) / f"{tid}.json"
        if not json_path.is_file():
            out.append(("trace-missing", tid))
            continue
        try:
            want_block, want_script = _split_fragment(render(load(json_path), target), tid)
        except (TraceError, ValueError, OSError):
            out.append(("trace-stale", tid))
            continue
        marker = f"<!-- /trace {tid} -->"
        end = html.find(marker, m.start())
        if end < 0 or html[m.start():end + len(marker)] != want_block:
            out.append(("trace-stale", tid))
            continue
        if want_script:
            found = re.search(_SCRIPT_RE % re.escape(tid), html, re.S)
            if not found or found.group(0) != want_script:
                out.append(("trace-stale", tid))
    return out


def main(argv: list[str] | None = None) -> int:
    import argparse
    import sys

    ap = argparse.ArgumentParser(prog="trace_figs.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("lint")
    p.add_argument("path")
    p = sub.add_parser("render")
    p.add_argument("path")
    p.add_argument("--target", choices=("note", "explain"), required=True)
    p = sub.add_parser("shadow")
    p.add_argument("path")
    p.add_argument("--structure", required=True)
    p.add_argument("--id", required=True)
    p = sub.add_parser("verify")
    p.add_argument("path")
    p.add_argument("--traces", required=True)
    args = ap.parse_args(argv)
    try:
        if args.cmd == "verify":
            bad = verify(Path(args.path).read_text(encoding="utf-8"), Path(args.traces))
            for code, tid in bad:
                print(code, tid)
            return 1 if bad else 0
        if args.cmd == "lint":
            errors = lint(json.loads(Path(args.path).read_text(encoding="utf-8")))
            for e in errors:
                print(e)
            return 1 if errors else 0
        trace = load(Path(args.path))
        if args.cmd == "render":
            sys.stdout.write(render(trace, args.target))
        else:
            sys.stdout.write(shadow_svg(trace, args.structure, args.id))
    except (TraceError, ValueError) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
