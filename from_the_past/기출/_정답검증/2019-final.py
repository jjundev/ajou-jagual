"""2019-final 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
SRC = "2019-final"
INF = float("inf")


# 1~4: 정의형 빈칸 — 실행으로 확인할 수 없음(원본 답)
def q1(): return "가중치 그래프"
def q2(): return "사이클"
def q3(): return "균형 인수"
def q4(): return "해시 함수"


def q5():
    n = 10
    return str(sum(1 for i in range(n) for j in range(i + 1, n)))


def heap_push(h, x):
    h.append(x); i = len(h) - 1
    while i > 1 and h[i // 2] < h[i]: h[i // 2], h[i] = h[i], h[i // 2]; i //= 2


def heap_pop(h):
    top, last = h[1], h.pop()
    if len(h) > 1:
        h[1] = last; i = 1
        while 2 * i < len(h):
            c = 2 * i
            if c + 1 < len(h) and h[c + 1] > h[c]: c += 1
            if h[i] >= h[c]: break
            h[i], h[c] = h[c], h[i]; i = c
    return top


def q6():
    h = [None]
    for x in (16, 9, 50, 41, 48, 24, 31): heap_push(h, x)
    heap_pop(h)
    for x in (53, 71, 50, 68, 64): heap_push(h, x)
    heap_pop(h); heap_pop(h)
    return f"레벨 순서(배열): {h[1:]}"


def q7():
    V = "ABCDEFG"
    E = {("A", "B"): 4, ("A", "F"): 9, ("B", "F"): 9, ("B", "G"): 3, ("B", "C"): 5, ("F", "G"): 8, ("F", "D"): 6,
         ("F", "E"): 8, ("C", "G"): 1, ("C", "D"): 8, ("G", "D"): 5, ("D", "E"): 3}
    w = lambda u, v: 0 if u == v else E.get((u, v), E.get((v, u), INF))
    dist = {v: w("A", v) for v in V}; S = ["A"]
    while len(S) < 5:
        u = min((dist[v], v) for v in V if v not in S)[1]; S.append(u)
        for v in V: dist[v] = min(dist[v], dist[u] + w(u, v))
    return f"S = {{{', '.join(S)}}} (추가 순서). distance: " + ", ".join(f"{v}={dist[v]}" for v in "ABCDEF") + f" (표에 없는 G={dist['G']})"


def q8(): return "원본에 키 값이 복원되어 있지 않아 풀 수 없음"


# 9: M=3 B-트리(노드 키 1~2개). 삭제: 내부 키는 중위 후속자로 바꾸고,
# 부족하면 왼쪽 형제 → 오른쪽 형제 순으로 빌리고, 못 빌리면 왼쪽(없으면 오른쪽) 형제와 합친다.
class N:
    def __init__(s, keys=None, kids=None): s.keys, s.kids = keys or [], kids or []
    leaf = property(lambda s: not s.kids)


def ins(root, k):
    def go(n):
        if n.leaf: n.keys.append(k); n.keys.sort()
        else:
            i = sum(x < k for x in n.keys); r = go(n.kids[i])
            if r: m, right = r; n.keys.insert(i, m); n.kids.insert(i + 1, right)
        if len(n.keys) > 2:
            m = n.keys[1]; right = N(n.keys[2:], n.kids[2:]); n.keys, n.kids = n.keys[:1], n.kids[:2]
            return m, right
    r = go(root)
    return N([r[0]], [root, r[1]]) if r else root


def delete(root, k):
    def fix(p, i):
        c = p.kids[i]
        if c.keys: return
        L = p.kids[i - 1] if i > 0 else None; R = p.kids[i + 1] if i + 1 < len(p.kids) else None
        if L and len(L.keys) > 1:
            c.keys.insert(0, p.keys[i - 1]); p.keys[i - 1] = L.keys.pop()
            if L.kids: c.kids.insert(0, L.kids.pop())
        elif R and len(R.keys) > 1:
            c.keys.append(p.keys[i]); p.keys[i] = R.keys.pop(0)
            if R.kids: c.kids.append(R.kids.pop(0))
        elif L:
            L.keys += [p.keys.pop(i - 1)] + c.keys; L.kids += c.kids; p.kids.pop(i)
        else:
            c.keys += [p.keys.pop(i)] + R.keys; c.kids += R.kids; p.kids.pop(i + 1)
    def go(n, k):
        if k in n.keys:
            j = n.keys.index(k)
            if n.leaf: n.keys.pop(j); return
            m = n.kids[j + 1]
            while not m.leaf: m = m.kids[0]
            n.keys[j] = m.keys[0]; go(n.kids[j + 1], m.keys[0]); fix(n, j + 1); return
        i = sum(x < k for x in n.keys); go(n.kids[i], k); fix(n, i)
    go(root, k)
    return root.kids[0] if not root.keys and root.kids else root


def levels(root):
    out, lv = [], [root]
    while lv:
        out.append(" ".join("[" + " ".join(map(str, n.keys)) + "]" for n in lv))
        lv = [c for n in lv for c in n.kids]
    return " / ".join(out)


def q9():
    t = N()
    for k in (30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80): t = ins(t, k)
    a = levels(t)
    t = delete(t, 40); t = delete(t, 80); t = ins(t, 25)
    return f"{levels(t)} (80까지 삽입 후 {a})"


VAL = {c: 101 + i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")}


def boundary_fold(s):  # 짝수 번째 문자 값은 자릿수를 뒤집어 더한다
    return sum(int(str(VAL[c])[::-1]) if i % 2 else VAL[c] for i, c in enumerate(s))


def shift_fold(s): return sum(VAL[c] for c in s)


def q10():
    keys = ["find", "cafe", "hill", "keep", "team", "wave", "vine", "have"]
    t, coll, over = [[] for _ in range(10)], 0, 0
    for k in keys:
        a = boundary_fold(k) % 10
        if t[a]: coll += 1
        if len(t[a]) == 2:
            over += 1; step = 7 - shift_fold(k) % 7
            while len(t[a]) == 2:
                a = (a + step) % 10
                if t[a]: coll += 1
        t[a].append(k)
    tbl = " / ".join(f"{i}: {', '.join(b)}" for i, b in enumerate(t) if b)
    return f"충돌 횟수 {coll}, 오버플로우 횟수 {over}. 테이블: {tbl}"


def q11():
    V = "ABCDE"
    E = {("A", "B"): 4, ("B", "A"): 3, ("A", "C"): 6, ("D", "A"): 2, ("D", "B"): 7, ("B", "E"): 5,
         ("C", "D"): 5, ("E", "D"): 6, ("C", "E"): 7, ("E", "C"): 4}
    d = [[0 if i == j else E.get((V[i], V[j]), INF) for j in range(5)] for i in range(5)]
    for k in range(3):  # A^0(A 경유) → A^1(B) → A^2(C)
        d = [[min(d[i][j], d[i][k] + d[k][j]) for j in range(5)] for i in range(5)]
    f = lambda x: "∞" if x == INF else str(x)
    return "A^2: " + " / ".join(f"{V[i]}: [{', '.join(map(f, d[i]))}]" for i in range(5))


if __name__ == "__main__":
    for i in range(1, 12):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
