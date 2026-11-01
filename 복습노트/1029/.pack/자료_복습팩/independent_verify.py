import re, sys, math
from collections import defaultdict
SRC = sys.argv[1] if len(sys.argv) > 1 else 'problems-only.html'
s = open(SRC, encoding='utf-8').read()
svgs = re.findall(r'<svg.*?</svg>', s, flags=re.S)

def parse(svg):
    nodes = {}
    for m in re.finditer(r'<circle[^>]*cx="([\d.]+)"[^>]*cy="([\d.]+)"[^>]*r="([\d.]+)"[^>]*/>\s*<text[^>]*>([^<]+)</text>', svg):
        nodes[m.group(4).strip()] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    def near(x, y):
        best = min(nodes, key=lambda n: math.hypot(nodes[n][0]-x, nodes[n][1]-y))
        d = math.hypot(nodes[best][0]-x, nodes[best][1]-y)
        return best, d
    children = defaultdict(list); parent = {}
    for m in re.finditer(r'<line[^>]*x1="([\d.]+)"[^>]*y1="([\d.]+)"[^>]*x2="([\d.]+)"[^>]*y2="([\d.]+)"', svg):
        x1,y1,x2,y2 = map(float, m.groups())
        a,da = near(x1,y1); b,db = near(x2,y2)
        r = nodes[a][2]
        assert da <= r+3 and db <= r+3, (a,da,b,db)
        if nodes[a][1] > nodes[b][1]: a,b = b,a
        assert b not in parent, b
        parent[b] = a; children[a].append(b)
    for p in children: children[p].sort(key=lambda n: nodes[n][0])
    roots = [n for n in nodes if n not in parent]
    assert len(roots) == 1, roots
    root = roots[0]
    level = {root: 1}; order=[root]
    for n in order:
        for c in children[n]: level[c] = level[n]+1; order.append(c)
    assert len(order) == len(nodes) and len(parent) == len(nodes)-1
    return nodes, children, parent, root, level

def desc(ch, n):
    out=[]; st=list(ch[n])
    while st:
        c=st.pop(0); out.append(c); st.extend(ch[c])
    return out
def side(nodes, p, c):
    return 'L' if nodes[c][0] < nodes[p][0] else ('R' if nodes[c][0] > nodes[p][0] else '?')

out=[]
def P(*a): out.append(' '.join(str(x) for x in a))

# p1
nodes, ch, par, root, lv = parse(svgs[0])
key = lambda n: int(n[1:])
P('p1 tree:', {k: ch[k] for k in sorted(ch, key=key)})
P('p1:a', sorted([n for n in nodes if lv[n]==3], key=key))
P('p1:b', sorted([n for n in ch[par['v8']] if n!='v8'], key=key))
P('p1:c', sorted(desc(ch,'v8'), key=key))
P('p1:d', max(lv.values()))
P('p1:e', len(ch['v8']))
# p2-p5 definitional
P('p2:main 트리 (계층 구조)')
P('p3:main 완전 이진 트리')
P('p4:main 높이')
# p5: binary tree of height K with 2^K-1 nodes -> full; check full is complete
for K in range(1,7):
    n = 2**K-1
    # max nodes at height K is sum 2^(i-1) = 2^K-1, so all levels full
    assert sum(2**(i-1) for i in range(1,K+1)) == n
P('p5:main X (2^K-1 노드면 포화 -> 포화는 완전의 특수 경우)')
# p6
nodes, ch, par, root, lv = parse(svgs[1])
leaves = sorted(n for n in nodes if not ch[n])
P('p6 tree:', dict(ch)); P('p6:main leaves', leaves, len(leaves))
# p7
nodes, ch, par, root, lv = parse(svgs[2])
deg = {n: len(ch[n]) for n in nodes}
P('p7 tree:', dict(ch)); P('p7:main degrees', deg, 'tree degree', max(deg.values()))
# p8
P('p8:main', sum(2**(i-1) for i in range(1,6)))
# p9 brute force over shapes: count of binary trees by (nodes,height) feasibility
from functools import lru_cache
@lru_cache(None)
def heights(n):
    # set of possible heights of binary trees with n nodes
    if n == 0: return frozenset([0])
    res=set()
    for l in range(n):
        for hl in heights(l):
            for hr in heights(n-1-l):
                res.add(1+max(hl,hr))
    return frozenset(res)
h12 = heights(12)
P('p9:a edges', 12-1)
P('p9:b height max', max(h12), 'min', min(h12))
ns = [n for n in range(1,40) if 4 in heights(n)]
P('p9:c nodes min', min(ns), 'max', max(ns))
# p10
nodes, ch, par, root, lv = parse(svgs[3])
P('p10 tree:', {k:[(c,side(nodes,k,c)) for c in v] for k,v in ch.items()})
def heap_slots(nodes, ch, root):
    # assign BFS-numbered position (1-based) using sides
    pos={root:1}; q=[root]
    for n in q:
        for c in ch[n]:
            pos[c]=2*pos[n]+(0 if side(nodes,n,c)=='L' else 1); q.append(c)
    return pos
def classify(nodes, ch, root, lv):
    pos=heap_slots(nodes,ch,root); N=len(nodes); h=max(lv.values())
    binary = all(len(v)<=2 for v in ch.values())
    complete = sorted(pos.values()) == list(range(1,N+1))
    full = complete and N == 2**h-1
    return binary, complete, full, pos
b,c,f,pos = classify(nodes,ch,root,lv)
P('p10:a binary',b,'complete',c,'full',f,'N',len(nodes),'h',max(lv.values()), 'lastlevel', sorted([n for n in nodes if lv[n]==max(lv.values())]))
nxt = len(nodes)+1; p = nxt//2
pn = [n for n,v in pos.items() if v==p][0]
P('p10:b next slot', nxt, '-> parent', pn, 'L' if nxt%2==0 else 'R')
# (c) move J to E right: place J to right of E
nodes2 = dict(nodes); ex,ey,er = nodes['E']; jx,jy,jr = nodes['J']
nodes2['J'] = (ex + (ex-jx), jy, jr)
b,c,f,pos2 = classify(nodes2,ch,root,lv)
P('p10:c binary',b,'complete',c,'full',f,'positions',sorted(pos2.values()))
print('\n'.join(out))
