"""2021-mock1 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
SRC = "2021-mock1"
INF = float("inf")


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


def q1():
    res = []
    for succ in (True, False):
        t = None
        for k in (15, 5, 16, 3, 12, 20, 10, 13, 18, 23, 6, 7): t = ins(t, k)
        for k in (13, 16, 5): t = dele(t, k, succ)
        res.append(levels(t))
    return f"후속자 규칙: {res[0]} (선행자 규칙: {res[1]})"


def q2():
    h, rows = [], []
    for x in (15, 16, 18, 17, 19, 20, 12):
        h.append(x); i = len(h) - 1
        while i > 0 and h[(i - 1) // 2] < h[i]: h[(i - 1) // 2], h[i] = h[i], h[(i - 1) // 2]; i = (i - 1) // 2
        rows.append(f"{x} → {h}")
    out, dels = [], []
    while h:
        out.append(h[0]); last = h.pop()
        if h:
            h[0] = last; i = 0
            while 2 * i + 1 < len(h):
                c = 2 * i + 1
                if c + 1 < len(h) and h[c + 1] > h[c]: c += 1
                if h[i] >= h[c]: break
                h[i], h[c] = h[c], h[i]; i = c
        dels.append(f"{out[-1]} 제거 → {h}")
    return f"1) {'; '.join(rows)} 2) {'; '.join(dels)}. 정렬 결과 {', '.join(map(str, sorted(out)))}"


def q3():
    E = [(0, 2), (0, 5), (0, 7), (1, 7), (2, 6), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7)]
    adj = {v: sorted([b for a, b in E if a == v] + [a for a, b in E if b == v]) for v in range(8)}
    seen, order, te = set(), [], []
    def dfs(v):
        seen.add(v); order.append(v)
        for w in adj[v]:
            if w not in seen: te.append(f"{v}-{w}"); dfs(w)
    dfs(0)
    d = f"DFS(0) 방문 {','.join(map(str, order))} 간선 {', '.join(te)}"
    seen, q, order, te = {0}, [0], [], []
    while q:
        v = q.pop(0); order.append(v)
        for w in adj[v]:
            if w not in seen: seen.add(w); q.append(w); te.append(f"{v}-{w}")
    return d + f" / BFS(0) 방문 {','.join(map(str, order))} 간선 {', '.join(te)}"


def q4():
    V = "ABCDE"
    E = {("A", "B"): 4, ("B", "A"): 3, ("A", "C"): 6, ("D", "A"): 2, ("D", "B"): 7, ("B", "E"): 5,
         ("C", "D"): 5, ("E", "D"): 6, ("C", "E"): 7, ("E", "C"): 4}
    d = [[0 if i == j else E.get((V[i], V[j]), INF) for j in range(5)] for i in range(5)]
    for k in range(3):
        d = [[min(d[i][j], d[i][k] + d[k][j]) for j in range(5)] for i in range(5)]
    f = lambda x: "∞" if x == INF else str(x)
    return "A^C: " + " / ".join(f"{V[i]}: {', '.join(map(f, d[i]))}" for i in range(5))


def q5():
    import heapq
    freq = {"s": 16, "t": 35, "u": 4, "v": 8, "w": 23, "x": 19}
    h = [(f, i, s) for i, (s, f) in enumerate(freq.items())]; heapq.heapify(h); depth = {s: 0 for s in freq}
    cnt = len(h)
    while len(h) > 1:
        a, b = heapq.heappop(h), heapq.heappop(h)
        for grp in (a[2], b[2]):
            for s in grp: depth[s] += 1
        heapq.heappush(h, (a[0] + b[0], cnt, a[2] + b[2])); cnt += 1
    total = sum(freq[s] * depth[s] for s in freq)
    return "코드 길이 " + ", ".join(f"{s}{depth[s]}" for s in freq) + f"; 총 {total} bits"


def build(ino, post):
    if not ino: return None
    r = post[-1]; i = ino.index(r)
    return [r, build(ino[:i], post[:i]), build(ino[i + 1:], post[i:-1])]


def q6():
    return "레벨 순서: " + levels(build("D,F,G,E,H,R,T,N,S,M,P,K".split(","), "F,D,E,G,R,T,S,N,P,M,K,H".split(",")))


def q7():
    # 1) 코드는 삽입 정렬 — 돌려서 정렬되는지만 확인. 장단점·2)는 서술형이라 실행으로 확인할 수 없음
    import random
    for s in range(20):
        lst = [random.Random(s).randint(0, 99) for _ in range(15)]; n = len(lst); a = lst[:]
        for i in range(1, n):
            key, j = a[i], i - 1
            while j >= 0 and a[j] > key: a[j + 1] = a[j]; j -= 1
            a[j + 1] = key
        assert a == sorted(lst)
    return "1) 삽입 정렬 (코드 실행으로 정렬 확인) 2) 서술형"


def q8():
    a, rows = [27, 4, 37, 2, 62, 12, 59, 16, 49, 18], []
    def part(l, r):
        p, low, high = a[l], l, r + 1
        while True:
            low += 1
            while low <= r and a[low] < p: low += 1
            high -= 1
            while high >= l and a[high] > p: high -= 1
            if low < high: a[low], a[high] = a[high], a[low]
            else: break
        a[l], a[high] = a[high], a[l]
        return high
    def qs(l, r):
        if l < r:
            q = part(l, r); rows.append(f"pivot {a[q]}: {' '.join(map(str, a))}")
            qs(l, q - 1); qs(q + 1, r)
    qs(0, 9)
    return " / ".join(rows)


def q9():
    keys, M = [12, 44, 13, 88, 23, 94, 11, 39, 20, 16, 5], 11
    def probe(step):
        t = [None] * M
        for k in keys:
            h, i = k % M, 0
            while t[(h + step(k, i)) % M] is not None: i += 1
            t[(h + step(k, i)) % M] = k
        return ", ".join(map(str, t))
    lin = probe(lambda k, i: i)
    quad = probe(lambda k, i: i * i)
    dbl = probe(lambda k, i: i * (7 - k % 7))
    ch = [[] for _ in range(M)]
    for k in keys: ch[k % M].append(k)
    chain = ", ".join(f"[{i}] {'→'.join(map(str, b)) or '없음'}" for i, b in enumerate(ch))
    return f"(1) {lin} (2) {quad} (3) {dbl} (4) {chain}"


if __name__ == "__main__":
    for i in range(1, 10):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
