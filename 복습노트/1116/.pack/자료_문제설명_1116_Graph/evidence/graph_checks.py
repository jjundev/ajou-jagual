"""1116 Graph 복습문제 독립 검산 (p1, p2, p4~p8, p10, p11).
참고 답을 읽지 않고 문제 조건만으로 계산한다."""
import itertools, random

def mat(n, edges, directed=False):
    M = [[0]*n for _ in range(n)]
    for a, b in edges:
        M[a][b] = 1
        if not directed:
            M[b][a] = 1
    return M

def lists(M):
    return [[j for j, x in enumerate(r) if x] for r in M]

print("== p1: 사이클 정의 확인 (S10 p7 G1) ==")
G1 = [(0,1),(0,2),(0,3),(1,2),(2,3)]
A1 = mat(4, G1)
def is_simple_cycle(M, path):
    if len(path) < 4 or path[0] != path[-1]: return False
    if any(M[a][b] != 1 for a, b in zip(path, path[1:])): return False
    return len(set(path[:-1])) == len(path) - 1
for p in ([0,1,2,3], [0,1,2,0], [0,1,2,0,3,2,0]):
    print(p, "closed" if p[0]==p[-1] else "open", "simple-cycle" if is_simple_cycle(A1,p) else "-")

print("== p2/p10: 완전 그래프 간선 수 (모든 쌍 직접 연결) ==")
for n in (1,2,3,4,5,10):
    pairs = list(itertools.combinations(range(n), 2))
    degsum = sum(n-1 for _ in range(n))
    print(f"n={n}: pairs={len(pairs)} degree_sum/2={degsum//2} formula={n*(n-1)//2}")
    assert len(pairs) == n*(n-1)//2 == degsum//2

print("== p4: 인접 행렬 -> 인접 리스트 ==")
M4 = [[0,1,0,0],[1,0,1,1],[0,1,0,0],[0,1,0,0]]
assert all(M4[i][j]==M4[j][i] for i in range(4) for j in range(4))
L4 = lists(M4)
for v, nb in enumerate(L4):
    print(f"{v} -> " + " -> ".join(map(str, nb)) + " -> NULL")
E4 = sum(map(sum, M4))//2
print("nodes", sum(map(len, L4)), "edges", E4)

print("== p5: 인접 행렬에서 한 정점 차수: 확인하는 칸 수 ==")
random.seed(1116)
for n in (4, 8, 16):
    for e_target in (0, n, n*(n-1)//2):
        allp = list(itertools.combinations(range(n), 2))
        E = random.sample(allp, e_target)
        M = mat(n, E)
        cells = 0; deg = 0
        for j in range(n):
            cells += 1; deg += M[0][j]
        print(f"n={n} e={e_target}: cells_examined={cells} deg(0)={deg}")
        assert cells == n

print("== p6: 인접 리스트 총 노드 수 ==")
print("G1 nodes", sum(map(len, lists(A1))), "edges", len(G1))
for trial in range(200):
    n = random.randint(1, 9)
    allp = list(itertools.combinations(range(n), 2))
    E = random.sample(allp, random.randint(0, len(allp)))
    assert sum(map(len, lists(mat(n, E)))) == 2*len(E)
    D = [(a,b) for a in range(n) for b in range(n) if a!=b and random.random()<0.4]
    assert sum(map(len, lists(mat(n, D, directed=True)))) == len(D)
print("random 200 graphs: undirected nodes == 2e, directed nodes == e : OK")

print("== p7: 그림 그래프 (e0..e5) ==")
E7 = [(0,1),(1,2),(1,3),(3,4),(2,4),(0,4)]
M7 = mat(5, E7)
for r in M7: print(" ".join(map(str, r)))
for v, nb in enumerate(lists(M7)):
    print(f"v{v} -> " + " -> ".join(f"v{u}" for u in nb) + " -> NULL")
print("ones", sum(map(sum, M7)), "nodes", sum(map(len, lists(M7))), "edges", len(E7))

print("== p8: 방향 그래프 ==")
E8 = [(1,2),(1,3),(1,4),(2,1),(2,3),(2,5),(3,1),(3,2),(3,4),(3,5),(4,2),(5,1),(5,3)]
assert len(set(E8)) == 13
for v in range(1,6):
    print(v, "->", [b for a,b in E8 if a==v], " in:", [a for a,b in E8 if b==v])
both = sorted({tuple(sorted(e)) for e in E8 if (e[1],e[0]) in E8})
one = [e for e in E8 if (e[1],e[0]) not in E8]
print("both directions:", both); print("one direction:", one)
print("4-5 edge?", (4,5) in E8 or (5,4) in E8)
print("unordered pairs with an edge:", len({tuple(sorted(e)) for e in E8}), "of", len(list(itertools.combinations(range(1,6),2))))
print("in-degree sum", sum(len([a for a,b in E8 if b==v]) for v in range(1,6)))

print("== p11: 쾨니히스베르크 다리 ==")
B = {'a':('A','B'),'b':('A','B'),'c':('A','C'),'d':('A','C'),'e':('A','D'),'f':('B','D'),'g':('C','D')}
V = ['A','B','C','D']
print("vertices", len(V), "edges", len(B))
deg = {v: sum((x==v)+(y==v) for x,y in B.values()) for v in V}
nbr = {v: sorted({y if x==v else x for x,y in B.values() if v in (x,y)}) for v in V}
print("degree (incident bridges)", deg, "sum", sum(deg.values()))
print("distinct neighbour lands", {v: len(nbr[v]) for v in V})
closed = opened = 0
for order in itertools.permutations(B):
    for s in V:
        cur = s; ok = True
        for br in order:
            x, y = B[br]
            if cur == x: cur = y
            elif cur == y: cur = x
            else: ok = False; break
        if ok:
            if cur == s: closed += 1
            else: opened += 1
print("orders x starts tried", 5040*4, "closed walks using every bridge once:", closed, "open:", opened)
