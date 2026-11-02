from collections import deque
from itertools import product

class N:
    def __init__(s, v, l=None, r=None): s.v, s.l, s.r = v, l, r

def build(edges, root):
    nodes = {}
    def g(k): return nodes.setdefault(k, N(k.split('#')[0]))
    for p, c, side in edges:
        if side == 'L': g(p).l = g(c)
        else: g(p).r = g(c)
    return g(root)

def pre(t): return [] if t is None else [t.v] + pre(t.l) + pre(t.r)
def ino(t): return [] if t is None else ino(t.l) + [t.v] + ino(t.r)
def post(t): return [] if t is None else post(t.l) + post(t.r) + [t.v]
def level(t, trace=False):
    out, q, rows = [], deque([t]), []
    while q:
        x = q.popleft(); out.append(x.v)
        if x.l: q.append(x.l)
        if x.r: q.append(x.r)
        rows.append((x.v, [y.v for y in q]))
    return (out, rows) if trace else out
def arr(t):
    a = {}
    def f(x, i):
        if x: a[i] = x.v; f(x.l, 2*i); f(x.r, 2*i+1)
    f(t, 1); return dict(sorted(a.items()))
def levels_children(t):
    res, q = [], deque([(t, 0)]); cur = -1
    lines = []
    while q:
        x, d = q.popleft()
        if d != cur: lines.append([]); cur = d
        lines[-1].append(x.v)
        res.append(f"{x.v}: L={x.l.v if x.l else '-'} R={x.r.v if x.r else '-'}")
        if x.l: q.append((x.l, d+1))
        if x.r: q.append((x.r, d+1))
    return lines, res

def trees(P=None, I=None, Q=None):
    """주어진 순회(None 이면 미지정)와 모순 없는 모든 트리를 전수 생성."""
    seqs = [s for s in (P, I, Q) if s is not None]
    n = len(seqs[0])
    if any(len(s) != n for s in seqs): return
    if n == 0: yield None; return
    if any(sorted(s) != sorted(seqs[0]) for s in seqs): return
    roots = set()
    if P is not None: roots.add(P[0])
    if Q is not None: roots.add(Q[-1])
    if len(roots) > 1: return
    cand_roots = roots if roots else set(I)
    for r in cand_roots:
        if I is not None:
            if I.count(r) != 1: continue
            ks = [I.index(r)]
        else: ks = range(n)
        for k in ks:
            lP = P[1:1+k] if P else None; rP = P[1+k:] if P else None
            lI = I[:k] if I else None; rI = I[k+1:] if I else None
            lQ = Q[:k] if Q else None; rQ = Q[k:-1] if Q else None
            for L in trees(lP, lI, lQ):
                for R in trees(rP, rI, rQ):
                    yield N(r, L, R)

def all_trees(**kw): return list(trees(**kw))
def S(x): return ' '.join(x)

print("=== p1 ===")
t1 = build([('A','B','L'),('A','F','R'),('B','C','L'),('B','D','R'),('D','E','R'),('F','G','L'),('G','H','L')], 'A')
print("배열:", arr(t1))
print("전위:", S(pre(t1))); print("후위:", S(post(t1))); print("중위:", S(ino(t1)))

def recon_report(name, P=None, I=None, Q=None):
    ts = all_trees(P=P, I=I, Q=Q)
    print(f"[{name}] 일관 트리 수 = {len(ts)}")
    for t in ts[:3]:
        ok = (P is None or pre(t) == P) and (I is None or ino(t) == I) and (Q is None or post(t) == Q)
        print("  재순회 일치:", ok)
    return ts

print("\n=== p2 ===")
I2 = "D F G E H R T N S M P K".split(", ") if False else "D,F,G,E,H,R,T,N,S,M,P,K".split(",")
Q2 = "F,D,E,G,R,T,S,N,P,M,K,H".split(",")
ts = recon_report("p2 중위+후위", I=I2, Q=Q2)
if ts:
    lines, ch = levels_children(ts[0])
    print("레벨:", " / ".join(S(l) for l in lines)); print("\n".join(ch))
    print("전위:", S(pre(ts[0])))

print("\n=== p3 ===")
I3 = "G,F,H,E,K,C,B,D,O,M,R,P,T".split(",")
Q3 = "G,H,P,K,E,C,O,R,T,P,M,D,B".split(",")
print("원문 그대로(P 두 번):", len(all_trees(I=I3, Q=Q3)), "트리")
for idx in [i for i, v in enumerate(Q3) if v == 'P']:
    q = Q3[:]; q[idx] = 'F'
    ts = all_trees(I=I3, Q=q)
    print(f"후위 {idx+1}번째 자리 P->F: {S(q)} => 일관 트리 {len(ts)}개")
    if ts:
        for t in ts: print("  재순회 일치:", ino(t) == I3 and post(t) == q)
        a = arr(ts[0]); print("  배열:", a, " 최대 칸:", max(a))
        lines, ch = levels_children(ts[0]); print("  레벨:", " / ".join(S(l) for l in lines)); print("  " + "\n  ".join(ch))

print("\n=== p4 ===")
A4 = "D,B,A,E,G,C,F,H".split(","); B4 = "D,B,G,E,H,F,C,A".split(",")
names = {'pre': 'P', 'in': 'I', 'post': 'Q'}
for k1, k2 in product(names, names):
    if k1 == k2: continue
    kw = {names[k1]: A4, names[k2]: B4}
    ts = all_trees(**kw)
    print(f"첫 줄={k1}, 둘째 줄={k2}: 일관 트리 {len(ts)}개")
    if ts and len(ts) <= 3:
        for t in ts:
            lines, ch = levels_children(t)
            print("   레벨:", " / ".join(S(l) for l in lines), "|", "; ".join(ch))
ts = all_trees(I=A4, Q=B4)
t4 = ts[0]
print("채택(중위+후위): 전위 =", S(pre(t4)), " 재순회 일치:", ino(t4) == A4 and post(t4) == B4)

print("\n=== p5 ===")
print("후위 순회: 폴더 용량 = 하위 폴더(자식) 용량을 모두 구한 뒤 자기 크기를 더하므로 자식 먼저, 루트 나중(LRV).")
print("\n=== p6 ===")
print("전위 순회(preorder): VLR — 루트를 자손보다 먼저 방문.")

def which(t, opts):
    m = {'전위': pre(t), '중위': ino(t), '후위': post(t), '레벨': level(t)}
    for i, o in enumerate(opts, 1):
        hit = [k for k, v in m.items() if v == o.split()]
        print(f"  보기{i} {o}: {hit or '어느 순회와도 불일치'}")

print("\n=== p7 ===")
t7 = build([('A','B','L'),('A','C','R'),('B','D','L'),('C','E','L'),('C','F','R')], 'A')
print("중위:", S(ino(t7)))
which(t7, ["A B D C E F", "A B C D E F", "D B E C F A", "D B A E C F"])

print("\n=== p8 ===")
t8 = build([('A','B','L'),('A','C','R'),('B','D','L'),('C','E','L'),('C','F','R'),('E','G','L'),('E','H','R')], 'A')
p = pre(t8); print("전위:", S(p), " 5번째:", p[4])
print("  보기: 1 C, 2 E, 3 G, 4 H -> 각 노드의 전위 위치:", {x: p.index(x)+1 for x in "CEGH"})

print("\n=== p9 ===")
t9 = build([('+','*#1','L'),('+','E','R'),('*#1','*#2','L'),('*#1','D','R'),('*#2','/','L'),('*#2','C','R'),('/','A','L'),('/','B','R')], '+')
print("후위:", S(post(t9)))
which(t9, ["+ * * / A B C D E", "A / B * C * D + E", "+ * A B / * C D E", "A B / C * D * E +"])

print("\n=== p10 (파이썬 교차 확인) ===")
def mystery(t):
    if t is None: return 0
    if t.l is None and t.r is None: return int(t.v)
    return max(mystery(t.l), mystery(t.r))
t10 = build([('3','5','L'),('3','1','R'),('5','4','L'),('5','2','R'),('1','8','L'),('1','6','R')], '3')
print("mystery(root) =", mystery(t10))

print("\n=== p11 ===")
t11 = build([('+','*','L'),('+','/','R'),('*','a','L'),('*','b','R'),('/','c','L'),('/','d','R')], '+')
out, rows = level(t11, trace=True)
print("(a) 레벨:", S(out))
print("단계 | 꺼낸 노드 | 자식 넣은 뒤 큐(앞->뒤)")
for i, (v, q) in enumerate(rows, 1): print(f"  {i} | {v} | {S(q) or '(빈 큐)'}")
print("(b)", S([q for v, q in rows if v == '*'][0]))
print("(c) 전위:", S(pre(t11)), "| 중위:", S(ino(t11)), "| 후위:", S(post(t11)))
