"""1109 Heap 문제설명 p5~p8 독립 검산 (저자 작성, answers.py 를 import 하지 않는다).

p5: 1-기반 배열 최소 히프 upheap/downheap 을 새로 구현해 단계별 상태를 출력하고,
    결과가 최소 히프 조건·완전 이진 트리(배열 1..n)·원소 집합을 지키는지 검사한다.
p6: 레벨 순서 번호(1..n)가 완전 이진 트리에서 빈칸 없이 차는지, 경사(skewed) 트리에서는
    빈칸이 생기는지 센다. 정답 모델은 만들지 않는다(source.json choice=null).
p7: n=10 높이를 루트 깊이 1 / 0 두 기준으로 센다. ceil(log2(n+1)) 과 대조.
p8: 교과서 그림 SVG(교과서/assets/ch09-q12-tree.svg)의 선 끝점 좌표로 부모-자식 관계를
    직접 복원해 모든 쌍을 검사한다(레벨 순서 가정에 기대지 않음).
"""
import math, os, re, sys, unicodedata

REPO = "/Users/hyunjun_macbook_pro/Documents/Univ/자구알"

# ---------- p5 ----------
def up(A, i):
    while i > 1 and A[i] < A[i // 2]:
        A[i], A[i // 2] = A[i // 2], A[i]
        i //= 2

def down(A):
    n = len(A) - 1
    i = 1
    while 2 * i <= n:
        c = 2 * i
        if c + 1 <= n and A[c + 1] < A[c]:
            c += 1
        if A[i] <= A[c]:
            break
        A[i], A[c] = A[c], A[i]
        i = c

def is_min_heap(A):
    return all(A[i // 2] <= A[i] for i in range(2, len(A)))

print("== p5 최소 히프: 삽입 90,85,80,75,70,65 후 한 번 삭제")
A = [None]
for k in [90, 85, 80, 75, 70, 65]:
    A.append(k)
    up(A, len(A) - 1)
    print(f"insert {k:>2} -> {A[1:]}  heap={is_min_heap(A)}")
ins = A[1:]
root = A[1]
A[1] = A.pop()
print(f"delete: root {root} 꺼냄, 마지막 노드를 루트로 -> {A[1:]}")
down(A)
print(f"downheap -> {A[1:]}  heap={is_min_heap(A)}")
assert ins == [65, 75, 70, 90, 80, 85]
assert A[1:] == [70, 75, 85, 90, 80]
assert sorted(A[1:]) == sorted([90, 85, 80, 75, 70])
for i in range(1, len(A)):
    ch = [A[j] for j in (2 * i, 2 * i + 1) if j < len(A)]
    print(f"  A[{i}]={A[i]} 자식 {ch}")
print("p5 OK")

# ---------- p6 ----------
print("\n== p6 배열 표현: 레벨 순서 번호가 1..n 을 빈칸 없이 채우는가")
ok = True
for n in range(1, 32):
    # 완전 이진 트리: 위 레벨부터, 같은 레벨은 왼쪽부터 n개
    pos, lvl = [], 0
    while len(pos) < n:
        for j in range(2 ** lvl):
            if len(pos) < n:
                pos.append(2 ** lvl + j)
        lvl += 1
    if pos != list(range(1, n + 1)):
        ok = False
    # 부모 식 i//2 가 실제 부모 칸(이미 채워진 칸)인지
    if any(p // 2 not in pos for p in pos if p > 1):
        ok = False
print("완전 이진 트리 n=1..31: 번호가 정확히 1..n, 부모 i//2 존재 ->", ok)
assert ok
for n in (3, 4, 5):
    idx = [1]  # 오른쪽 경사: 1,3,7,15,...
    for _ in range(n - 1):
        idx.append(2 * idx[-1] + 1)
    print(f"오른쪽 경사 이진 트리 노드 {n}개: 사용 칸 {idx}, 배열 크기 {idx[-1]}, 빈칸 {idx[-1]-n}")
print("p6: 정답 모델 미생성(choice=null). 근거는 위 구조 사실뿐")

# ---------- p7 ----------
print("\n== p7 노드 10개 히프 높이")
def height_root1(n):
    h, cap = 0, 0
    while cap < n:
        h += 1
        cap += 2 ** (h - 1)
    return h
n = 10
h1 = height_root1(n)
print(f"루트 깊이 1 기준: 깊이별 최대 1,2,4,8 / 누적 1,3,7,15 -> 높이 {h1}")
print(f"ceil(log2(n+1)) = {math.ceil(math.log2(n + 1))}, floor(log2 n)+1 = {math.floor(math.log2(n)) + 1}")
print(f"루트 깊이 0 기준(간선 수): {h1 - 1}")
print("깊이 4 에 남는 노드 수:", n - (1 + 2 + 4))
print("높이 4 인 n 범위:", [m for m in range(1, 20) if height_root1(m) == 4])
assert h1 == 4 and math.ceil(math.log2(11)) == 4
print("p7 OK")

# ---------- p8 ----------
print("\n== p8 교과서 그림에서 트리 복원 후 최소 히프 판정")
d = os.path.join(REPO, "교과서", "assets")
svgname = [f for f in os.listdir(d) if unicodedata.normalize("NFC", f) == "ch09-q12-tree.svg"][0]
s = open(os.path.join(d, svgname), encoding="utf-8").read()
nodes = {}
for m in re.finditer(r'<g id="([^"]+)">\s*<circle cx="([\d.]+)" cy="([\d.]+)"[^>]*/>\s*<text[^>]*>([^<]+)</text>', s):
    gid, x, y, t = m.groups()
    nodes[(float(x), float(y))] = (gid.split("-")[-1], int(t))
edges = []
for m in re.finditer(r'<line x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', s):
    x1, y1, x2, y2 = map(float, m.groups())
    p, c = nodes[(x1, y1)], nodes[(x2, y2)]
    side = "L" if x2 < x1 else "R"
    edges.append((p, c, side))
print("노드 수", len(nodes), "간선 수", len(edges))
# 레벨 복원
ys = sorted({y for (_, y) in nodes})
for li, yv in enumerate(ys, 1):
    row = [nodes[k][1] for k in sorted([k for k in nodes if k[1] == yv])]
    print(f"레벨 {li}: {row}")
viol = []
print("부모-자식 쌍 점검 (min heap: 부모 <= 자식)")
for p, c, side in sorted(edges, key=lambda e: (e[0][0], e[2])):
    good = p[1] <= c[1]
    print(f"  {p[1]:>2}({p[0]}) -{side}-> {c[1]:>2}({c[0]})  {'OK' if good else '위반'}")
    if not good:
        viol.append((p[1], c[1], side))
# 완전 이진 트리: 레벨 순서로 1..n 번호를 매겨 자식이 2i,2i+1 인지
children = {}
for p, c, side in edges:
    children.setdefault(p[0], {})[side] = c[0]
order, q = [], ["a"]
while q:
    v = q.pop(0); order.append(v)
    for sd in ("L", "R"):
        if sd in children.get(v, {}):
            q.append(children[v][sd])
num = {v: i + 1 for i, v in enumerate(order)}
complete = all(num[c] == 2 * num[p] + (0 if sd == "L" else 1) for p, cs in children.items() for sd, c in cs.items())
print("완전 이진 트리(자식 번호가 2i, 2i+1 이고 1..n 연속):", complete)
print("위반 쌍:", viol)
assert complete and viol == [(6, 5, "L")]
print("p8 OK: 최소 히프 아님")
print("\nALL OK")
