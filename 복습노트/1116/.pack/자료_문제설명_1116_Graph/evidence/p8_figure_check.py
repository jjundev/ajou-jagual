"""p8: 설명에 넣는 방향 그래프 SVG의 화살표(선 시작→끝, 화살촉 위치)를 가장 가까운 정점으로 읽어 E와 비교한다."""
import re, sys, math
svg = open(sys.argv[1]).read()
V = {t: (float(x), float(y)) for x, y, t in re.findall(r'<circle class="fig-ink" cx="([\d.]+)" cy="([\d.]+)" r="18"/><text[^>]*>(\d)</text>', svg)}
def near(x, y):
    return min(V, key=lambda k: math.dist(V[k], (x, y)))
lines = re.findall(r'<line class="fig-ink" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"/>', svg)
got = sorted((int(near(float(a), float(b))), int(near(float(c), float(d)))) for a, b, c, d in lines)
E8 = sorted([(1,2),(1,3),(1,4),(2,1),(2,3),(2,5),(3,1),(3,2),(3,4),(3,5),(4,2),(5,1),(5,3)])
print("vertices", sorted(V)); print("arrows read", got); print("match E:", got == E8, "count", len(got))
