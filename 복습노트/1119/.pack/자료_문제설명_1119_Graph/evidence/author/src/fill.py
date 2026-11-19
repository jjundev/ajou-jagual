import math,re,sys,pathlib
SRC=pathlib.Path(__file__).parent; OUT=SRC.parents[2]/'explanations'
P1={0:(180,35),1:(100,110),2:(260,110),3:(40,190),4:(135,190),5:(225,190),6:(320,190),7:(180,270)}
P2={0:(50,40),2:(210,40),1:(103,127),7:(190,127),6:(327,127),3:(117,198),5:(50,270),4:(190,270)}
G1=[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6),(3,7),(4,7),(5,7),(6,7)]
G2=[(0,2),(0,5),(0,7),(1,7),(2,6),(3,4),(3,5),(4,5),(4,6),(4,7)]
TREES={
 'p1-dfs':(P1,G1,[(0,1),(1,3),(3,7),(7,4),(7,5),(5,2),(2,6)],'0 0 360 310','DFS(0) 신장 트리'),
 'p1-bfs':(P1,G1,[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6),(3,7)],'0 0 360 310','BFS(0) 신장 트리'),
 'p2-dfs':(P2,G2,[(0,2),(2,6),(6,4),(4,3),(3,5),(4,7),(7,1)],'0 0 370 310','DFS(0) 신장 트리'),
 'p2-bfs':(P2,G2,[(0,2),(0,5),(0,7),(2,6),(5,3),(5,4),(7,1)],'0 0 370 310','BFS(0) 신장 트리'),
}
def svg(key):
    P,G,T,vb,name=TREES[key]; r=21; tset={frozenset(e) for e in T}
    parts=[]
    for u,v in G:
        (x1,y1),(x2,y2)=P[u],P[v]; d=math.hypot(x2-x1,y2-y1); ux,uy=(x2-x1)/d,(y2-y1)/d
        a=(x1+ux*r,y1+uy*r,x2-ux*r,y2-uy*r)
        if frozenset((u,v)) in tset:
            parts.append('<line class="fig-accent" stroke-width="5" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'%a)
        else:
            parts.append('<line class="fig-ink" stroke-dasharray="5 5" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'%a)
    for v,(x,y) in sorted(P.items()):
        parts.append('<circle class="fig-ink" cx="%d" cy="%d" r="%d"/><text class="fig-text" x="%d" y="%d" text-anchor="middle" font-size="17">%d</text>'%(x,y,r,x,y+6,v))
    te=', '.join('%d-%d'%e for e in T); ne=', '.join('%d-%d'%e for e in G if frozenset(e) not in tset)
    return ('<figure class="figure"><svg id="fig-%s" viewBox="%s" role="img" aria-label="%s. 굵은 선은 트리 간선 %s, 점선은 트리에 들지 않은 간선 %s">%s</svg>'
            '<figcaption>%s: 굵은 선이 트리 간선(%s), 점선은 트리에 들지 않은 간선(%s)이에요.</figcaption></figure>')%(key,vb,name,te,ne,''.join(parts),name,te,ne)
for f in sorted(SRC.glob('p*.html')):
    t=f.read_text(encoding='utf-8')
    t=re.sub(r'\{\{SVG:([a-z0-9-]+)\}\}',lambda m:svg(m.group(1)),t)
    (OUT/f.name).write_text(t,encoding='utf-8'); print('wrote',f.name)
