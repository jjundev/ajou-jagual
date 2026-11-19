import re, itertools, math
from collections import deque
HTML = open(__file__.replace('solver.py','problems_only.html'), encoding='utf-8').read()
sections = re.split(r'<h2>(p\d+) ', HTML)
sec = {sections[i]: sections[i+1] for i in range(1, len(sections), 2)}

def parse_graph(pid):
    s = sec[pid]
    svg = s[s.index('<svg'):s.index('</svg>')]
    lines = [tuple(float(x) for x in m) for m in re.findall(
        r'<line[^>]*x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', svg)]
    circles = [(float(a), float(b)) for a, b in re.findall(r'<circle[^>]*cx="([\d.]+)" cy="([\d.]+)"', svg)]
    texts = re.findall(r'<text[^>]*x="([\d.]+)" y="([\d.]+)"[^>]*>(\d+)</text>', svg)
    labels = []
    for (cx, cy) in circles:
        if texts:
            t = min(texts, key=lambda t: (float(t[0])-cx)**2 + (float(t[1])-cy)**2)
            labels.append(int(t[2]))
        else:
            labels.append(None)
    if labels[0] is None:
        labels = list(range(len(circles)))  # unlabeled: index by drawing order
    def near(x, y):
        d = [(math.hypot(x-cx, y-cy), i) for i, (cx, cy) in enumerate(circles)]
        d.sort()
        return d[0]
    edges = []
    for (x1, y1, x2, y2) in lines:
        d1, a = near(x1, y1); d2, b = near(x2, y2)
        assert d1 < 30 and d2 < 30, (pid, x1, y1, x2, y2)
        # check segment does not pass through another circle
        for k, (cx, cy) in enumerate(circles):
            if k in (a, b): continue
            dx, dy = x2-x1, y2-y1
            t = max(0, min(1, ((cx-x1)*dx + (cy-y1)*dy)/(dx*dx+dy*dy)))
            if math.hypot(x1+t*dx-cx, y1+t*dy-cy) < 22:
                print(f"  WARNING {pid}: segment {labels[a]}-{labels[b]} passes through circle {labels[k]}")
        u, v = sorted((labels[a], labels[b]))
        edges.append((u, v))
    return len(circles), sorted(edges)

def matrix(n, edges):
    m = [[0]*n for _ in range(n)]
    for u, v in edges: m[u][v] = m[v][u] = 1
    return m

def dfs(m, s):
    n = len(m); vis = [0]*n; order = []; tree = []
    def go(v):
        vis[v] = 1; order.append(v)
        for w in range(n):
            if m[v][w] and not vis[w]:
                tree.append(tuple(sorted((v, w)))); go(w)
    go(s); return order, tree

def bfs(adj, s, n):
    vis = [0]*n; vis[s] = 1; q = deque([s]); order = []; tree = []
    while q:
        v = q.popleft(); order.append(v)
        for w in adj[v]:
            if not vis[w]:
                vis[w] = 1; q.append(w); tree.append(tuple(sorted((v, w))))
    return order, tree

def mat_adj(m):
    return [[w for w in range(len(m)) if m[v][w]] for v in range(len(m))]

def connected(n, edges):
    m = matrix(n, edges); o, _ = dfs(m, 0); return len(o) == n

for pid in ['p1', 'p2']:
    n, E = parse_graph(pid)
    print(f"== {pid}: n={n}, edges={E}")
    m = matrix(n, E)
    o, t = dfs(m, 0); print(f"  DFS(0) order={o} tree={sorted(t)} (discovery order {t})")
    o, t = bfs(mat_adj(m), 0, n); print(f"  BFS(0) order={o} tree={sorted(t)} (discovery order {t})")

print("== p3: adjacency list as given")
p3 = {0: [1, 5], 1: [0, 5, 2], 2: [1, 3], 3: [2, 4, 5], 4: [3, 5], 5: [0, 1, 3, 4]}
# symmetry check
for v, ws in p3.items():
    for w in ws: assert v in p3[w], (v, w)
print("  symmetric: yes")
o, t = bfs(p3, 0, 6); print(f"  BFS(0) order={o} tree={t}")
o, t = bfs({v: sorted(ws) for v, ws in p3.items()}, 0, 6); print(f"  (ascending-order BFS for comparison) order={o}")

n, E = parse_graph('p7'); print(f"== p7: n={n}, edges={E}")
m = matrix(n, E)
for s in (3, 6):
    print(f"  DFS({s}) order={dfs(m, s)[0]}")
for s in (3, 6):
    print(f"  BFS({s}) order={bfs(mat_adj(m), s, n)[0]}")

n, E8 = parse_graph('p8'); print(f"== p8: n={n}, edges={E8}")
print(f"  same graph as p7: {E8 == E}")
br = [e for e in E8 if not connected(n, [f for f in E8 if f != e])]
print(f"  bridges (brute force): {br}")

n, E9 = parse_graph('p9'); print(f"== p9: n={n}, edges (vertices indexed by drawing order TL=0,TR=1,BR=2,BL=3)={E9}")
sts = []
for sub in itertools.combinations(E9, n-1):
    if connected(n, list(sub)): sts.append(sub)
print(f"  spanning trees: {len(sts)}")
for s in sts:
    missing = [e for e in E9 if e not in s]
    print(f"   {list(s)}  (removed {missing})")

print("== p10: simulate given C code")
E10 = [(0, 2), (0, 5), (1, 3), (2, 5), (3, 6), (4, 6)]
m = matrix(8, E10); visited = [0]*8; count = 0; out = []
def dfs_mat(v):
    visited[v] = count; out.append(v)
    for w in range(8):
        if m[v][w] and not visited[w]: dfs_mat(w)
for i in range(8):
    if not visited[i]:
        count += 1; dfs_mat(i)
print(f"  printed: {' '.join(map(str, out))}")
print(f"  visited[0..7] = {visited}")
print(f"  count = {count}")
