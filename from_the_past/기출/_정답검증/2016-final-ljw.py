"""2016-final-ljw 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
SRC = "2016-final-ljw"
INF = float("inf")


def q1():
    # 1) 코드를 돌려 정렬되는지만 확인(삽입 정렬). 이름·장단점·2)는 서술·정의형이라 실행으로 확인할 수 없음
    import random
    for s in range(20):
        lst = [random.Random(s).randint(0, 99) for _ in range(15)]; a = lst[:]
        for i in range(1, len(a)):
            key, j = a[i], i - 1
            while j >= 0 and a[j] > key: a[j + 1] = a[j]; j -= 1
            a[j + 1] = key
        assert a == sorted(lst)
    return "1) 삽입 정렬(코드 실행으로 정렬 확인) 2) 서술형"


def q2():
    a, levels = [27, 4, 37, 2, 62, 12, 59, 16, 49, 18], {}
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
    # 한 단계 = 같은 깊이의 파티션을 모두 나눈 뒤
    stage, rows = [(0, 9)], []
    while stage:
        nxt = []
        for l, r in stage:
            if l < r:
                q = part(l, r); nxt += [(l, q - 1), (q + 1, r)]
        nxt = [(l, r) for l, r in nxt if l < r]
        piv = {l for l, r in nxt}
        rows.append(" ".join(f"({v})" if i in piv else str(v) for i, v in enumerate(a)))
        stage = nxt
    return " / ".join(f"{i + 1}단계: {r}" for i, r in enumerate(rows))


def bst(keys):
    def ins(t, k):
        if t is None: return [k, None, None]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        return t
    t = None
    for k in keys: t = ins(t, k)
    return t


def avl(keys):
    H = lambda t: t[3] if t else 0
    def fix(t): t[3] = 1 + max(H(t[1]), H(t[2])); return t
    def rr(t): l = t[1]; t[1] = l[2]; l[2] = fix(t); return fix(l)
    def rl(t): r = t[2]; t[2] = r[1]; r[1] = fix(t); return fix(r)
    rot = []
    def ins(t, k):
        if t is None: return [k, None, None, 1]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        fix(t); b = H(t[1]) - H(t[2])
        if b > 1:
            if k > t[1][0]: rot.append(f"{k} 삽입 LR({t[0]})"); t[1] = rl(t[1])
            else: rot.append(f"{k} 삽입 LL({t[0]})")
            return rr(t)
        if b < -1:
            if k < t[2][0]: rot.append(f"{k} 삽입 RL({t[0]})"); t[2] = rr(t[2])
            else: rot.append(f"{k} 삽입 RR({t[0]})")
            return rl(t)
        return t
    t = None
    for k in keys: t = ins(t, k)
    return t, rot


def level(t):
    out, q = [], [t]
    while q:
        n = q.pop(0)
        if n: out.append(n[0]); q += [n[1], n[2]]
    return out


def ino(t): return [] if t is None else ino(t[1]) + [t[0]] + ino(t[2])


def q3():
    keys = (10, 20, 30, 40, 15, 35, 45)
    b = bst(keys)
    h = [None]
    for x in keys:
        h.append(x); i = len(h) - 1
        while i > 1 and h[i // 2] < h[i]: h[i // 2], h[i] = h[i], h[i // 2]; i //= 2
    heap = h[1:]
    hin = lambda i: [] if i > len(heap) else hin(2 * i) + [heap[i - 1]] + hin(2 * i + 1)
    ino_heap = hin(1)
    dels = []
    while len(h) > 1:
        top, last = h[1], h.pop()
        if len(h) > 1:
            h[1] = last; i = 1
            while 2 * i < len(h):
                c = 2 * i
                if c + 1 < len(h) and h[c + 1] > h[c]: c += 1
                if h[i] >= h[c]: break
                h[i], h[c] = h[c], h[i]; i = c
        dels.append(f"{top} 삭제 → {h[1:]}")
    a, rot = avl(keys)
    j = lambda xs: " ".join(map(str, xs))
    return (f"1) BST 레벨 순서 {j(level(b))} 2) Max Heap {heap} 3) ① {j(ino(b))} ② {j(ino_heap)} "
            f"4) {'; '.join(dels)} 5) {', '.join(rot)}; AVL 레벨 순서 {j(level(a))} 6) 서술형")


def q4():
    import heapq
    f = {"A": 15, "B": 8, "C": 20, "D": 1, "E": 5, "F": 40, "G": 9, "H": 2}
    h = [(v, i, k) for i, (k, v) in enumerate(f.items())]; heapq.heapify(h); d = {k: 0 for k in f}; n = len(h)
    while len(h) > 1:
        a, b = heapq.heappop(h), heapq.heappop(h)
        for s in a[2] + b[2]: d[s] += 1
        heapq.heappush(h, (a[0] + b[0], n, a[2] + b[2])); n += 1
    bits = (len(f) - 1).bit_length()
    return (f"1) {bits} bit, {bits * 100} bit 2) {sum(f[k] * d[k] for k in f)} bit; 코드 길이 "
            + ", ".join(f"{k}{d[k]}" for k in f))


def q5():
    t = [None] * 11
    for k in (12, 44, 13, 88, 23, 94, 11, 39, 20, 16, 5):
        h, s = k % 11, 7 - k % 7
        while t[h] is not None: h = (h + s) % 11
        t[h] = k
    return " ".join(f"[{i}]{v}" for i, v in enumerate(t))


def q6():
    E = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 7), (5, 7), (6, 7)]
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
    return d + f". BFS(0) 방문 {','.join(map(str, order))} 간선 {', '.join(te)}"


def q7():
    a, x = list(range(1, 21)), 19
    lo, hi, nb = 0, len(a) - 1, 0
    while lo <= hi:
        nb += 1; m = (lo + hi) // 2
        if a[m] == x: break
        lo, hi = (m + 1, hi) if a[m] < x else (lo, m - 1)
    lo, hi, ni = 0, len(a) - 1, 0
    while lo <= hi:
        ni += 1; p = lo + (x - a[lo]) * (hi - lo) // (a[hi] - a[lo])
        if a[p] == x: break
        lo, hi = (p + 1, hi) if a[p] < x else (lo, p - 1)
    return f"① {nb}회 ② {ni}회"


def q8():
    E = [("Prague", "Helsinki", 1845), ("Prague", "London", 1264), ("Beijing", "Tokyo", 1303),
         ("Helsinki", "Tokyo", 7815), ("Beijing", "New York", 11550), ("Beijing", "Jakarta", 4616),
         ("Beijing", "London", 8132), ("Tokyo", "Jakarta", 5782), ("Tokyo", "London", 9566),
         ("Tokyo", "New York", 10838), ("London", "New York", 5567)]
    V = sorted({x for a, b, _ in E for x in (a, b)})
    w = {}
    for a, b, c in E: w[a, b] = w[b, a] = c
    dist = {v: INF for v in V}; dist["Prague"] = 0; S = []
    while len(S) < len(V):
        u = min((dist[v], v) for v in V if v not in S)[1]; S.append(u)  # 동률이면 이름 알파벳순
        for v in V:
            if (u, v) in w: dist[v] = min(dist[v], dist[u] + w[u, v])
    return f"1) {{{', '.join(S)}}} 3) " + ", ".join(f"{v} {dist[v]}" for v in ("Beijing", "Helsinki", "Tokyo", "Jakarta", "New York", "London"))


if __name__ == "__main__":
    for i in range(1, 9):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
