"""2015-ljw 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
SRC = "2015-ljw"
INF = float("inf")


def q1():
    # 2) 수식 트리만 계산으로 확인. 1)·3)~6)은 서술·정의형이라 실행으로 확인할 수 없음(원본 답)
    y, z = 3, 3
    val = ((-y) - 6 * 3) / z + 2
    return f"2) ② {val:g} (나머지 소문항은 서술·정의형)"


def ins(t, k):
    if t is None: return [k, None, None]
    if k < t[0]: t[1] = ins(t[1], k)
    else: t[2] = ins(t[2], k)
    return t


def dele(t, k, succ=True):
    if t is None: return None
    if k < t[0]: t[1] = dele(t[1], k, succ)
    elif k > t[0]: t[2] = dele(t[2], k, succ)
    else:
        if t[1] is None: return t[2]
        if t[2] is None: return t[1]
        if succ:
            m = t[2]
            while m[1]: m = m[1]
            t[0] = m[0]; t[2] = dele(t[2], m[0], succ)
        else:
            m = t[1]
            while m[2]: m = m[2]
            t[0] = m[0]; t[1] = dele(t[1], m[0], succ)
    return t


def levels(t):
    out, lv = [], [t]
    while any(lv):
        out.append(" ".join(str(n[0]) for n in lv if n))
        lv = [c for n in lv if n for c in (n[1], n[2])]
    return " / ".join(out)


def q2():
    res = []
    for succ in (True, False):
        t = None
        for k in (15, 5, 16, 3, 12, 20, 10, 13, 18, 23, 6, 7): t = ins(t, k)
        for k in (13, 16, 5): t = dele(t, k, succ)
        res.append(levels(t))
    return f"후계자 규칙: {res[0]} (선행자 규칙: {res[1]})"


def q3():
    # 문제 글이 가려져 있어 전사 에이전트가 답안 계산 흔적으로 추정한 조건으로 돌린다
    t = [None] * 11
    for k in (12, 44, 13, 88, 23, 94, 11, 39, 20, 16, 5):
        h, s = k % 11, 7 - k % 7
        while t[h] is not None: h = (h + s) % 11
        t[h] = k
    return ", ".join(f"{i}:{v}" for i, v in enumerate(t))


def q4():
    h, rows = [], []
    for x in (15, 16, 18, 17, 19, 20, 12):
        h.append(x); i = len(h) - 1
        while i > 0 and h[(i - 1) // 2] < h[i]: h[(i - 1) // 2], h[i] = h[i], h[(i - 1) // 2]; i = (i - 1) // 2
        rows.append(str(h))
    dels = []
    while h:
        top = h[0]; last = h.pop()
        if h:
            h[0] = last; i = 0
            while 2 * i + 1 < len(h):
                c = 2 * i + 1
                if c + 1 < len(h) and h[c + 1] > h[c]: c += 1
                if h[i] >= h[c]: break
                h[i], h[c] = h[c], h[i]; i = c
        dels.append(f"{top} 제거 → {h}")
    return f"1) {' → '.join(rows)} 2) {' / '.join(dels)}"


def q5():
    a = [14, 5, 43, 27, 18, 31, 37, 88, 6, 35]; out = []
    for gap in (5, 3, 1):
        for s in range(gap):  # 부분 리스트마다 삽입 정렬
            for i in range(s + gap, len(a), gap):
                k, j = a[i], i - gap
                while j >= 0 and a[j] > k: a[j + gap] = a[j]; j -= gap
                a[j + gap] = k
        out.append(f"gap={gap}: {' '.join(map(str, a))}")
    b, edges = [9, 73, 42, 1, 80, 39, 72, 30, 100, 46, 82, 32, 17], []
    def part(l, r):
        p, low, high = b[l], l, r + 1
        while True:
            low += 1
            while low <= r and b[low] < p: low += 1
            high -= 1
            while high >= l and b[high] > p: high -= 1
            if low < high: b[low], b[high] = b[high], b[low]
            else: break
        b[l], b[high] = b[high], b[l]
        return high
    def qs(l, r, parent, side):
        if l > r: return
        if l == r: edges.append(f"{parent}의 {side} {b[l]}"); return
        q = part(l, r)
        if parent is not None: edges.append(f"{parent}의 {side} {b[q]}")
        qs(l, q - 1, b[q], "왼쪽"); qs(q + 1, r, b[q], "오른쪽")
    qs(0, len(b) - 1, None, "")
    return f"1) {' / '.join(out)} 2) pivot 트리(루트 9): {', '.join(edges)}"


def q6():
    E = [(0, 2), (0, 5), (0, 7), (1, 7), (2, 6), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7)]
    adj = {v: sorted([b for a, b in E if a == v] + [a for a, b in E if b == v]) for v in range(8)}
    seen, order, te = set(), [], []
    def dfs(v):
        seen.add(v); order.append(v)
        for w in adj[v]:
            if w not in seen: te.append(f"{v}-{w}"); dfs(w)
    dfs(0)
    d = f"DFS(0): 방문 {', '.join(map(str, order))} / 간선 {', '.join(te)}"
    seen, q, order, te = {0}, [0], [], []
    while q:
        v = q.pop(0); order.append(v)
        for w in adj[v]:
            if w not in seen: seen.add(w); q.append(w); te.append(f"{v}-{w}")
    return d + f" | BFS(0): 방문 {', '.join(map(str, order))} / 간선 {', '.join(te)}"


def q7():
    E = [("Mayor's House", "Brewery", 10), ("Mayor's House", "Bakery", 10), ("Brewery", "Inn", 7),
         ("Brewery", "McFane's Farm", 20), ("Inn", "Library", 5), ("Inn", "Dry Cleaner", 15),
         ("Library", "City Hall", 18), ("Dry Cleaner", "City Hall", 5), ("Bakery", "McFane's Farm", 12),
         ("McFane's Farm", "Thomas Farm", 15)]
    V = sorted({x for a, b, _ in E for x in (a, b)})
    w = {}
    for a, b, c in E: w[a, b] = w[b, a] = c
    dist = {v: INF for v in V}; dist["Library"] = 0; S = []
    while len(S) < len(V):
        u = min((dist[v], v) for v in V if v not in S)[1]; S.append(u)
        for v in V:
            if (u, v) in w: dist[v] = min(dist[v], dist[u] + w[u, v])
    cols = ["City Hall", "Inn", "Dry Cleaner", "Brewery", "Mayor's House", "McFane's Farm", "Bakery", "Thomas Farm"]
    return "distance: " + ", ".join(f"{c} {dist[c]}" for c in cols) + f"; 확정 순서 {', '.join(S)}"


if __name__ == "__main__":
    for i in range(1, 8):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
