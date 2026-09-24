"""2017-final2 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
import os, subprocess, tempfile

SRC = "2017-final2"
INF = float("inf")


def run_c(code, stdin=""):
    with tempfile.TemporaryDirectory() as d:
        c, exe = os.path.join(d, "a.c"), os.path.join(d, "a.out")
        open(c, "w").write(code)
        subprocess.run(["cc", "-std=c11", "-Wall", "-o", exe, c], check=True, capture_output=True)
        return subprocess.run([exe], input=stdin, capture_output=True, text=True, check=True).stdout


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


def q1():
    h = [None]
    for x in (10, 40, 30, 5, 12, 6, 60, 15): heap_push(h, x)
    a = h[1:]; heap_pop(h)
    return f"(a) {a} (b) {h[1:]}"


def q2():  # 삽입 정렬(내림차순), 한 원소를 끼워 넣을 때마다 한 줄
    a = [7, 4, 9, 6, 3, 8]; rows = [list(a)]
    for i in range(1, len(a)):
        x, j = a[i], i - 1
        while j >= 0 and a[j] < x: a[j + 1] = a[j]; j -= 1
        a[j + 1] = x
        if i > 1: rows.append(list(a))
    return "\n".join(", ".join(map(str, r)) for r in rows)


def q3():
    adj = {0: [1, 5], 1: [0, 5, 2], 2: [1, 3], 3: [2, 4, 5], 4: [3, 5], 5: [0, 1, 3, 4]}
    seen, q, order = {0}, [0], []
    while q:
        v = q.pop(0); order.append(v)
        for w in adj[v]:
            if w not in seen: seen.add(w); q.append(w)
    return ", ".join(map(str, order))


def q4():
    V = "ABCDEF"
    M = [[0, 4, INF, INF, INF, 9], [4, 0, 8, INF, INF, 11], [INF, 8, 0, 2, INF, INF],
         [INF, INF, 2, 0, 6, 7], [INF, INF, INF, 6, 0, 1], [9, 11, INF, 7, 1, 0]]
    s = 2; inT, Vs, Es = {s}, [V[s]], []
    while len(inT) < 6:
        w, i, j = min((M[i][j], i, j) for i in inT for j in range(6) if j not in inT)
        inT.add(j); Vs.append(V[j]); Es.append(f"({V[i]}, {V[j]})")
    return f"(b) V ={{ {', '.join(Vs)} }} E ={{ {', '.join(Es)} }}"


def q5():
    E = {(0, 1): 50, (0, 2): 35, (0, 3): 10, (3, 0): 20, (1, 2): 10, (1, 3): 15, (3, 4): 15,
         (4, 1): 20, (4, 2): 35, (2, 4): 30, (4, 5): 3}
    w = lambda u, v: 0 if u == v else E.get((u, v), INF)
    dist, S, rows = [w(0, v) for v in range(6)], [0], []
    f = lambda d: ", ".join("∞" if x == INF else str(x) for x in d)
    rows.append(f"1 | {{0}} | {f(dist)}")
    while len(S) < 6:
        u = min((dist[v], v) for v in range(6) if v not in S)[1]; S.append(u)
        for v in range(6): dist[v] = min(dist[v], dist[u] + w(u, v))
        rows.append(f"{len(S)} | {{{','.join(map(str, S))}}} | {f(dist)}")
    return "\n".join(rows)


def q6():
    t, coll = [None] * 11, 0
    for k in (66, 158, 8, 72, 22, 24, 130, 35):
        i = k % 11
        if t[i] is not None: coll += 1
        while t[i] is not None: i = (i + 1) % 11
        t[i] = k
    return ", ".join(f"[{i}]={'빈칸' if v is None else v}" for i, v in enumerate(t)) + f"\n충돌횟수: {coll}"


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
    h = lambda t: t[3] if t else 0
    def fix(t): t[3] = 1 + max(h(t[1]), h(t[2])); return t
    def rr(t): l = t[1]; t[1] = l[2]; l[2] = fix(t); return fix(l)
    def rl(t): r = t[2]; t[2] = r[1]; r[1] = fix(t); return fix(r)
    def ins(t, k):
        if t is None: return [k, None, None, 1]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        fix(t); b = h(t[1]) - h(t[2])
        if b > 1:
            if k > t[1][0]: t[1] = rl(t[1])
            return rr(t)
        if b < -1:
            if k < t[2][0]: t[2] = rr(t[2])
            return rl(t)
        return t
    t = None
    for k in keys: t = ins(t, k)
    return t


def level(t):
    out, q = [], [t]
    while q:
        n = q.pop(0)
        if n: out.append(n[0]); q += [n[1], n[2]]
    return out


def path(t, k):
    p = []
    while t:
        p.append(t[0])
        if t[0] == k: break
        t = t[1] if k < t[0] else t[2]
    return p


def q7():
    keys = (60, 50, 20, 80, 90, 70, 55, 10, 40, 35)
    a, b = bst(keys), avl(keys)
    j = lambda xs: ", ".join(map(str, xs))
    return f"(a) 레벨 순서 {j(level(a))}, 방문 {j(path(a, 35))} (b) 레벨 순서 {j(level(b))}, 방문 {j(path(b, 35))}"


KEY8 = r'''
#include <stdio.h>
#include <string.h>
char check_cycle(int adj_matrix[6][6], char *path) {
    int len, i, snode, enode;
    int a_m[6][6] = { 0 };
    len = strlen(path);
    if (path[0] != path[len - 1]) return 'n';
    for (i = 0; i < len - 1 ; i++){
        snode = path[i] - '0'; enode = path[i + 1] - '0';
        if (adj_matrix[snode][enode] != 1) return 'n';
        if (a_m[snode][enode] == 1) return 'n';
        else if (a_m[enode][snode] == 1) return 'n';
        else { a_m[snode][enode] = 1; a_m[enode][snode] = 1; }
    }
    return 'y';
}
int main(){
    int adj_matrix[6][6] = {
    { 0, 0, 1, 0, 1, 0 }, { 0, 0, 1, 0, 0, 0 }, { 1, 1, 0, 1, 1, 0 },
    { 0, 0, 1, 0, 1, 1 }, { 1, 0, 1, 1, 0, 0 }, { 0, 0, 0, 1, 0, 0 } };
    char p[32];
    while (scanf("%31s", p) == 1) printf("%s:%c ", p, check_cycle(adj_matrix, p));
    return 0;
}
'''


def q8():
    # 주어진 경로 0240, 사이클 2342, 간선 없음 0150, 되돌아옴 0200, 시작≠끝 024
    return "모범답안 코드 실행: " + run_c(KEY8, "0240 2342 0150 020 024").strip() + " (주어진 main: Cycle?: Yes)"


KEY9 = r'''
#include <stdio.h>
#define MAX_SIZE 50
int main(){
    int i; int list[MAX_SIZE];
    int j, smaller, temp, sum = 0, prime_flag;
    for (i = 0; i < MAX_SIZE; i++) scanf("%d", &list[i]);
    for (i = 0; i < MAX_SIZE - 1; i++) {
        smaller = i;
        for (j = i + 1; j<MAX_SIZE; j++) if (list[j] < list[smaller]) smaller = j;
        temp = list[i]; list[i] = list[smaller]; list[smaller] = temp;
    }
    for (i = 0; i < MAX_SIZE; i++){
        prime_flag = 1;
        for (j = 2; j < list[i]; j++) if (list[i] % j == 0) prime_flag = 0;
        if (prime_flag == 1) if (sum + list[i] < 50) sum = sum + list[i];
    }
    printf("sum:%d \n", sum);
    return 0;
}
'''


def q9():
    # 원본 모범답안은 for 문 세미콜론이 빠져 있어(MAX_SIZE i++) 세미콜론만 넣어 돌린다
    import random
    isp = lambda n: n >= 2 and all(n % d for d in range(2, n))
    res = []
    for seed in range(5):
        r = random.Random(seed); lst = [r.randint(2, 50) for _ in range(50)]
        s = 0
        for x in sorted(lst):
            if isp(x) and s + x < 50: s += x
        out = run_c(KEY9, " ".join(map(str, lst)))
        res.append(out.strip() == f"sum:{s}")
    return "모범답안 코드(세미콜론 보정) 난수 5벌 모두 일치" if all(res) else f"불일치 {res}"


if __name__ == "__main__":
    for i in range(1, 10):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
