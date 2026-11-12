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
