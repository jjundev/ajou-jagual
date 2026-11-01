"""1029 Tree 복습문제 p1~p10 독립 검산.

그림 문항(p1, p6, p7, p10)은 source.json 의 SVG 좌표에서 선분 양끝에 가장 가까운
원(노드)을 찾아 부모(위쪽)-자식(아래쪽) 간선을 다시 만든다. 카드의 풀이·답 문장은
읽지 않는다. 이진 트리 범위(p5, p8, p9)는 모양을 직접 열거하는 DP 로 확인한다.
"""
import json, math, re, sys, itertools
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "source.json"
probs = {p["id"]: p for p in json.loads(SRC.read_text())["problems"]}

def tree_from_svg(svg):
    nodes = []
    # 형식 1: <circle cx cy> 다음 <text>라벨
    for m in re.finditer(r'<circle[^>]*cx="([\d.]+)"[^>]*cy="([\d.]+)"[^>]*/>\s*<text[^>]*>([^<]+)</text>', svg):
        nodes.append((m.group(3).strip(), float(m.group(1)), float(m.group(2))))
    edges = []
    for m in re.finditer(r'<line[^>]*x1="([\d.]+)"[^>]*y1="([\d.]+)"[^>]*x2="([\d.]+)"[^>]*y2="([\d.]+)"', svg):
        x1, y1, x2, y2 = map(float, m.groups())
        def near(x, y):
            return min(nodes, key=lambda n: math.hypot(n[1]-x, n[2]-y))
        a, b = near(x1, y1), near(x2, y2)
        par, ch = (a, b) if a[2] < b[2] else (b, a)
        side = "L" if ch[1] < par[1] else ("R" if ch[1] > par[1] else "M")
        edges.append((par[0], ch[0], side, ch[1]))
    children = {n[0]: [] for n in nodes}
    for par, ch, side, x in sorted(edges, key=lambda e: e[3]):
        children[par].append((ch, side))
    return nodes, children

def svg_of(pid):
    return re.search(r"<svg.*?</svg>", probs[pid]["conditions_html"], re.S).group(0)

def levels(children):
    allc = {c for v in children.values() for c, _ in v}
    root = [n for n in children if n not in allc]
    assert len(root) == 1, root
    lv = {root[0]: 1}
    q = [root[0]]
    while q:
        u = q.pop(0)
        for c, _ in children[u]:
            lv[c] = lv[u] + 1; q.append(c)
    return root[0], lv

def descendants(children, u):
    out = []
    for c, _ in children[u]:
        out.append(c); out += descendants(children, c)
    return out

out = []
P = out.append

# p1
_, ch = tree_from_svg(svg_of("p1"))
root, lv = levels(ch)
P("[p1] 간선: " + "; ".join(f"{u}->{','.join(c for c,_ in v)}" for u, v in ch.items() if v))
P(f"[p1] 노드 수 {len(ch)}, 간선 수 {sum(len(v) for v in ch.values())}, 루트 {root}")
for L in range(1, max(lv.values())+1):
    P(f"[p1] 레벨 {L}: {[n for n in ch if lv[n]==L]}")
parent = {c: u for u, v in ch.items() for c, _ in v}
P(f"[p1] (a) 레벨 3: {sorted([n for n in ch if lv[n]==3], key=lambda s:int(s[1:]))}")
P(f"[p1] (b) v8 부모 {parent['v8']}, 형제: {[c for c,_ in ch[parent['v8']] if c!='v8']}")
P(f"[p1] (b') 같은 레벨이지만 부모 다른 노드: {[n for n in ch if lv[n]==lv['v8'] and parent.get(n)!=parent['v8']]}")
P(f"[p1] (c) v8 자손: {sorted(descendants(ch,'v8'), key=lambda s:int(s[1:]))}")
P(f"[p1] (d) 높이(최대 레벨): {max(lv.values())}, 최대 레벨 노드 {[n for n in ch if lv[n]==max(lv.values())]}")
P(f"[p1] (e) v8 차수: {len(ch['v8'])}")

# p6
_, ch = tree_from_svg(svg_of("p6"))
P("[p6] 간선: " + "; ".join(f"{u}->{','.join(c for c,_ in v)}" for u, v in ch.items() if v))
leaves = [n for n, v in ch.items() if not v]
P(f"[p6] 단말 노드: {leaves} -> {len(leaves)}개, 비단말 {len(ch)-len(leaves)}개, 전체 {len(ch)}개")
root, lv = levels(ch)
P(f"[p6] 최대 레벨 노드만: {[n for n in ch if lv[n]==max(lv.values())]}")

# p7
_, ch = tree_from_svg(svg_of("p7"))
P("[p7] 간선: " + "; ".join(f"{u}->{','.join(c for c,_ in v)}" for u, v in ch.items() if v))
deg = {n: len(v) for n, v in ch.items()}
P(f"[p7] 노드별 차수: {deg}")
P(f"[p7] 트리 차수(max): {max(deg.values())}, 노드 수 {len(ch)}, 단말 수 {sum(1 for d in deg.values() if d==0)}")

# 이진 트리 모양 열거 DP: H[n] = n개 노드 이진 트리가 가질 수 있는 높이 집합
N = 35
H = {0: {0}}
for n in range(1, N+1):
    s = set()
    for nl in range(n):
        for hl in H[nl]:
            for hr in H[n-1-nl]:
                s.add(1+max(hl, hr))
    H[n] = s
P(f"[p9] (a) 트리 간선 = 노드-1 (p1 그림 19개 노드 18간선으로도 확인) -> 12개 노드: {12-1}")
P(f"[p9] (b) 12개 노드 이진 트리의 가능한 높이: {sorted(H[12])} -> 최소 {min(H[12])}, 최대 {max(H[12])}")
P(f"[p9] (b) ceil(log2(13)) = {math.ceil(math.log2(13))}")
by_h = {}
for n in range(1, N+1):
    for h in H[n]:
        by_h.setdefault(h, []).append(n)
P(f"[p9] (c) 높이 4 가 가능한 노드 수: {by_h[4]} -> 최소 {min(by_h[4])}, 최대 {max(by_h[4])}")
P(f"[p8] 높이 5 가 가능한 노드 수: {min(by_h[5])}~{max(by_h[5])}, 보기별 높이 5 가능 여부: " + ", ".join(f"{v}:{v in by_h[5]}" for v in (26, 8, 32, 31)) + f" -> 최대 {max(by_h[5])}")
P(f"[p8] 레벨별 최대: {[2**(i-1) for i in range(1,6)]}, 합 {sum(2**(i-1) for i in range(1,6))}")

# p5: 높이 K, 노드 2^K-1 인 이진 트리 모양을 전부 열거해 완전 이진 트리인지 확인 (K=1..4)
def shapes(h):
    """높이 정확히 h 인 이진 트리 모양을 (레벨, 왼쪽부터 칸 번호) 집합으로 열거."""
    if h == 0:
        yield frozenset(); return
    def build(maxd):
        if maxd == 0:
            yield None; return
        yield None
        for l in build(maxd-1):
            for r in build(maxd-1):
                yield (l, r)
    def pos(t, lvl, idx, acc):
        if t is None: return
        acc.add((lvl, idx)); pos(t[0], lvl+1, 2*idx, acc); pos(t[1], lvl+1, 2*idx+1, acc)
    for t in build(h):
        if t is None: continue
        acc = set(); pos(t, 1, 0, acc)
        if max(l for l, _ in acc) == h:
            yield frozenset(acc)

def is_complete(S):
    h = max(l for l, _ in S)
    for L in range(1, h):
        if sum(1 for l, _ in S if l == L) != 2**(L-1): return False
    last = sorted(i for l, i in S if l == h)
    return last == list(range(len(last)))

def is_full(S):
    h = max(l for l, _ in S)
    return all(sum(1 for l, _ in S if l == L) == 2**(L-1) for L in range(1, h+1))

for K in range(1, 5):
    target = [S for S in shapes(K) if len(S) == 2**K-1]
    P(f"[p5] K={K}: 노드 {2**K-1}개 모양 {len(target)}개, 모두 포화 {all(map(is_full,target))}, 모두 완전 {all(map(is_complete,target))}")

# p10
_, ch = tree_from_svg(svg_of("p10"))
P("[p10] 간선: " + "; ".join(f"{u}->{','.join(c+'('+s+')' for c,s in v)}" for u, v in ch.items() if v))
def slots(ch):
    root, _ = levels(ch)
    acc = {}
    def go(u, lvl, idx):
        acc[u] = (lvl, idx)
        for c, s in ch[u]:
            go(c, lvl+1, 2*idx + (0 if s == "L" else 1))
    go(root, 1, 0)
    return acc
S = slots(ch)
SS = frozenset(S.values())
P(f"[p10] (a) 노드 {len(S)}개, 높이 {max(l for l,_ in SS)}, 포화 {is_full(SS)}, 완전 {is_complete(SS)}")
h = max(l for l, _ in SS)
free = [i for i in range(2**(h-1)) if (h, i) not in SS]
par_of = {v: k for k, v in S.items()}
i = free[0]
P(f"[p10] (b) 레벨 {h} 첫 빈칸 = 왼쪽부터 {i}번째 칸(0부터) -> 부모 {par_of[(h-1, i//2)]} 의 {'왼' if i%2==0 else '오른'}쪽 자식")
SS_b = SS | {(h, i)}
P(f"[p10] (b) K 추가 후 완전 {is_complete(SS_b)}")
# (c) J 를 E 오른쪽으로
ch_c = {u: [(c, ("R" if c == "J" else s)) for c, s in v] for u, v in ch.items()}
Sc = frozenset(slots(ch_c).values())
P(f"[p10] (c) 모든 노드 자식 ≤2: {all(len(v)<=2 for v in ch_c.values())}, 완전 {is_complete(Sc)}, 레벨4 칸 {sorted(i for l,i in Sc if l==4)}")

text = "\n".join(out)
print(text)
(Path(__file__).with_suffix(".txt")).write_text(text + "\n")
