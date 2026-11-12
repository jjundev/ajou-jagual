"""레벨 순서 배열 이진 트리 연산, compute, SVG.

Tree: 0번이 루트, 자식은 2k+1·2k+2, 빈 자리는 None.
강의 번호는 1부터(루트 1, 자식 2i·2i+1)이며 lecture_number 등이 변환한다.
"""
from html import escape

Tree = list  # list[str | None]

OPS = ("preorder", "inorder", "postorder", "levelorder", "height", "node_count",
       "evaluate", "lecture_number", "parent_index", "left_index", "right_index")

_OPERATORS = ("+", "-", "*", "/")


def _has(t, i):
    return 0 <= i < len(t) and t[i] is not None


def preorder(t):
    out = []

    def go(i):
        if _has(t, i):
            out.append(t[i])
            go(2 * i + 1)
            go(2 * i + 2)
    go(0)
    return out


def inorder(t):
    out = []

    def go(i):
        if _has(t, i):
            go(2 * i + 1)
            out.append(t[i])
            go(2 * i + 2)
    go(0)
    return out


def postorder(t):
    out = []

    def go(i):
        if _has(t, i):
            go(2 * i + 1)
            go(2 * i + 2)
            out.append(t[i])
    go(0)
    return out


def levelorder(t):
    return [x for i, x in enumerate(t) if _reachable(t, i)]


def _reachable(t, i):
    while True:
        if not _has(t, i):
            return False
        if i == 0:
            return True
        i = (i - 1) // 2


def _depth(i):
    return (i + 1).bit_length() - 1


def height(t):
    return max((_depth(i) + 1 for i in range(len(t)) if _reachable(t, i)), default=0)


def node_count(t):
    return sum(1 for i in range(len(t)) if _reachable(t, i))


def evaluate(t):
    def go(i):
        v = t[i]
        if v in _OPERATORS:
            a, b = go(2 * i + 1), go(2 * i + 2)
            if v == "+":
                return a + b
            if v == "-":
                return a - b
            if v == "*":
                return a * b
            if b == 0:
                raise ZeroDivisionError("트리 계산에서 0으로 나눴어요")
            q = abs(a) // abs(b)          # C 처럼 0 쪽으로 버림
            return q if (a >= 0) == (b >= 0) else -q
        return int(v)
    if not _has(t, 0):
        raise ValueError("빈 트리는 계산할 수 없어요")
    return go(0)


def lecture_number(t, label):
    for i, x in enumerate(t):
        if x == label and _reachable(t, i):
            return i + 1
    raise ValueError(f"트리에 {label!r} 노드가 없어요")


def parent_index(i):
    return i // 2


def left_index(i):
    return 2 * i


def right_index(i):
    return 2 * i + 1


def compute(spec, tree):
    op = spec["op"]
    if op in ("preorder", "inorder", "postorder", "levelorder"):
        return ", ".join(globals()[op](tree))
    if op in ("height", "node_count", "evaluate"):
        return str(globals()[op](tree))
    if op == "lecture_number":
        return str(lecture_number(tree, spec["arg"]))
    if op in ("parent_index", "left_index", "right_index"):
        return str(globals()[op](int(spec["arg"])))
    raise ValueError(f"알 수 없는 op: {op!r}")


R = 17
X_STEP = 44
Y0 = 30
Y_STEP = 45


def tree_svg(t, svg_id, aria_label):
    h = max(height(t), 1)
    width = max(2 ** (h - 1) * X_STEP, 2 * X_STEP)
    heightpx = Y0 + (h - 1) * Y_STEP + R + 10
    pos = {}
    for i in range(len(t)):
        if _reachable(t, i):
            d = _depth(i)
            j = i + 1 - 2 ** d
            pos[i] = (round(width * (j + 0.5) / 2 ** d), Y0 + d * Y_STEP)
    lines, nodes = [], []
    for i, (x, y) in pos.items():
        if i and (i - 1) // 2 in pos:
            px, py = pos[(i - 1) // 2]
            lines.append(f'<line class="fig-ink" x1="{px}" y1="{py + R}" x2="{x}" y2="{y - R}"/>')
    for i, (x, y) in pos.items():
        nodes.append(f'<circle class="fig-ink" cx="{x}" cy="{y}" r="{R}"/>')
        nodes.append(f'<text class="fig-text" x="{x}" y="{y + 5}" text-anchor="middle" '
                     f'font-size="14">{escape(str(t[i]))}</text>')
    return (f'<svg id="{escape(svg_id)}" viewBox="0 0 {width} {heightpx}" role="img" '
            f'aria-label="{escape(aria_label, quote=True)}">'
            + "".join(lines) + "".join(nodes) + "</svg>")
