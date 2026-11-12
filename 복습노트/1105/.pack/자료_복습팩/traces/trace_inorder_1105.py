"""1105 노트 19쪽 트리의 재귀 중위 순회를 실제로 실행해 trace JSON 을 만든다.

실행: python3 make_inorder_1105.py <출력 JSON 경로>
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

NODES = {
    "18": {"l": "7", "r": "26"},
    "7": {"l": "3", "r": "12"},
    "26": {"r": "31"},
    "31": {"l": "27"},
    "3": {},
    "12": {},
    "27": {},
}

# 1105 노트 s0-inorder 의 <li> 14개 (태그 제거한 평문)
TEXTS = [
    "18에서는 왼쪽을 먼저 처리해요. 18의 방문을 미루고 7로 내려가요.",
    "7에서도 방문을 미루고 왼쪽의 3으로 내려가요.",
    "3의 왼쪽 NULL에서 바닥 조건을 확인하고 돌아와요. 3을 출력해요.",
    "3의 오른쪽 NULL도 확인하고 돌아와요. 3의 처리가 끝나요.",
    "7의 왼쪽 처리가 끝났으므로 7을 출력해요.",
    "7의 오른쪽 12로 들어가요. 12의 왼쪽 NULL을 확인한 뒤 12를 출력해요.",
    "12의 오른쪽 NULL을 확인하고 돌아와요. 7을 뿌리로 하는 왼쪽 전체가 끝나요.",
    "18의 왼쪽 처리가 끝났으므로 18을 출력해요.",
    "18의 오른쪽 26으로 들어가요. 26의 왼쪽 NULL을 확인한 뒤 26을 출력해요.",
    "26의 오른쪽 31로 들어가요. 31의 방문을 미루고 왼쪽 27로 내려가요.",
    "27의 왼쪽 NULL을 확인한 뒤 27을 출력해요.",
    "27의 오른쪽 NULL을 확인하고 돌아와요. 31의 왼쪽 처리가 끝나요.",
    "31을 출력해요. 31의 오른쪽 NULL을 확인하고 돌아와요.",
    "26과 18의 남은 호출도 끝나요. 최종 출력은 3, 7, 12, 18, 26, 27, 31이에요."
]

# 노트 <li> 하나가 묶는 원시 사건 수 (합 19)
GROUPS = [1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 2, 1, 2, 1]
KEY_STEPS = {1, 5, 8, 14}


def run() -> list[dict]:
    """재귀 중위 순회. 사건: defer(자식으로 내려감), null(빈 자식 확인), out(출력)."""
    events: list[dict] = []
    stack: list[str] = []
    out: list[str] = []

    def snap(cur, null_at=None):
        events.append({"cur": cur, "null_at": null_at, "st": list(stack),
                       "out": list(out), "new": None})

    def walk(n: str | None, side: str | None = None, parent: str | None = None):
        if n is None:
            snap(parent, {"node": parent, "side": side})
            return
        node = NODES[n]
        if node.get("l"):
            stack.append(n)  # 왼쪽 일을 마친 뒤 방문하려고 미룬다
            snap(node["l"])
            walk(node["l"])
            stack.pop()
        else:
            walk(None, "l", n)
        out.append(n)
        snap(n)
        events[-1]["new"] = n
        if node.get("r"):
            walk(node["r"])
        else:
            walk(None, "r", n)

    walk("18")
    snap(None)  # 모든 호출이 끝남
    return events


def build() -> dict:
    events = run()
    assert len(events) == sum(GROUPS), (len(events), sum(GROUPS))
    steps = []
    i = 0
    for n, size in enumerate(GROUPS, 1):
        grp = events[i:i + size]
        i += size
        last = grp[-1]
        null_at = next((e["null_at"] for e in grp if e["null_at"]), None)
        changed = [e["new"] for e in grp if e["new"]]
        out = last["out"]
        steps.append({
            "text": TEXTS[n - 1],
            "state": {
                "t": {"cur": last["cur"], "done": list(out), "null_at": null_at,
                      "changed": changed},
                "st": list(last["st"]),
                "out": {"values": list(out), "hi": list(range(len(out) - len(changed), len(out))),
                        "ptr": {}},
            },
            **({"key": True} if n in KEY_STEPS else {}),
        })
    # 14단계: 모든 호출이 끝난 상태
    final = steps[-1]["state"]
    final["t"].update(cur=None, null_at=None, changed=[])
    final["st"] = []
    final["out"]["hi"] = []
    steps[-1]["state"] = final

    result = steps[-1]["state"]["out"]["values"]
    assert result == ["3", "7", "12", "18", "26", "27", "31"], result
    for a, b in zip(steps, steps[1:]):
        va, vb = a["state"]["out"]["values"], b["state"]["out"]["values"]
        assert vb[:len(va)] == va, (va, vb)
    assert steps[0]["state"]["t"]["cur"] == "7" and steps[0]["state"]["st"] == ["18"]
    assert steps[0]["state"]["out"]["values"] == []
    assert len(steps[-1]["state"]["t"]["done"]) == 7

    return {
        "version": 1,
        "id": "inorder-1105",
        "title": "중위 순회로 19쪽 트리 따라가기",
        "structures": [
            {"id": "t", "kind": "bintree", "root": "18", "nodes": NODES},
            {"id": "st", "kind": "stack", "label": "미뤄 둔 노드"},
            {"id": "out", "kind": "array", "label": "출력", "size": 7},
        ],
        "steps": steps,
    }


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(
        json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
