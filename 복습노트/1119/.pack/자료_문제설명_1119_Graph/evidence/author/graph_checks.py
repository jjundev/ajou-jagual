from collections import deque
from itertools import combinations
def adj(n,E):
    a={v:[] for v in range(n)}
    for u,v in E: a[u].append(v); a[v].append(u)
    return {v:sorted(a[v]) for v in a}
def dfs(a,s):
    seen=[];tree=[]
    def go(v):
        seen.append(v)
        for w in a[v]:
            if w not in seen: tree.append((v,w)); go(w)
    go(s); return seen,tree
def bfs(a,s):
    seen=[s];tree=[];q=deque([s])
    while q:
        v=q.popleft()
        for w in a[v]:
            if w not in seen: seen.append(w);tree.append((v,w));q.append(w)
    return seen,tree
def connected(n,E):
    a=adj(n,E); return len(dfs(a,0)[0])==n
G1=[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6),(3,7),(4,7),(5,7),(6,7)]
G2=[(0,2),(0,5),(0,7),(1,7),(2,6),(3,4),(3,5),(4,5),(4,6),(4,7)]
for name,G in (('p1',G1),('p2',G2)):
    a=adj(8,G); print(name,'DFS',dfs(a,0),'BFS',bfs(a,0))
L={0:[1,5],1:[0,5,2],2:[1,3],3:[2,4,5],4:[3,5],5:[0,1,3,4]}
print('p3 BFS list-order',bfs(L,0)[0])
G7=[(0,1),(1,2),(1,3),(2,4),(3,4),(3,5),(5,6),(5,7),(6,7),(7,8),(7,9)]
a=adj(10,G7)
for s in (3,6): print('p7 DFS',s,dfs(a,s)[0],'BFS',s,bfs(a,s)[0])
print('p8 bridges',[e for e in G7 if not connected(10,[f for f in G7 if f!=e])])
SQ=[('A','B'),('B','C'),('C','D'),('D','A')]
idx={'A':0,'B':1,'C':2,'D':3}
st=[c for c in combinations(SQ,3) if connected(4,[(idx[u],idx[v]) for u,v in c])]
print('p9 spanning trees',len(st),st)
# p10: simulate given code with count stored
G10=[(0,2),(0,5),(1,3),(2,5),(3,6),(4,6)]
A=[[0]*8 for _ in range(8)]
for u,v in G10: A[u][v]=A[v][u]=1
visited=[0]*8;out=[];count=0
def dfs_mat(v):
    visited[v]=count; out.append(v)
    for w in range(8):
        if A[v][w] and not visited[w]: dfs_mat(w)
for i in range(8):
    if not visited[i]: count+=1; dfs_mat(i)
print('p10',out,visited,'count',count)
# boundary: count==0 trap check (visited=count where count>=1 so ok)
