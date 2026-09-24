"""2018-mid-c024 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다.
2018-mid-c102는 5~16번이 이 시험과 같은 문항이라 verify_2018-mid-c102.py가 이 파일의 함수를 쓴다."""
import os, subprocess, tempfile

SRC = "2018-mid-c024"


def run_c(code, stdin=""):
    with tempfile.TemporaryDirectory() as d:
        c, exe = os.path.join(d, "a.c"), os.path.join(d, "a.out")
        open(c, "w").write(code)
        subprocess.run(["cc", "-std=c11", "-Wall", "-o", exe, c], check=True, capture_output=True)
        return subprocess.run([exe], input=stdin, capture_output=True, text=True, check=True).stdout


# 1~7: 정의형 빈칸·OX — 실행으로 확인할 수 없음(원본 답)
def q1(): return "스택"
def q2(): return "큐"
def q3(): return "후위 순회"
def q4(): return "완전이진트리"
def q5(): return "X"
def q6(): return "X"
def q7(): return "X"


def q8():
    for n in range(1, 30):
        cnt = sum(1 for i in range(n) for j in range(i, n) for k in range(30))
        assert cnt == 30 * n * (n + 1) // 2
    return "T(n) = 30n(n+1)/2, 빅오 표기법: O(n^2)"


def to_postfix(tokens):
    prec, out, ops = {"+": 1, "-": 1, "*": 2, "/": 2}, [], []
    for t in tokens:
        if t == "(": ops.append(t)
        elif t == ")":
            while ops[-1] != "(": out.append(ops.pop())
            ops.pop()
        elif t in prec:
            while ops and ops[-1] != "(" and prec[ops[-1]] >= prec[t]: out.append(ops.pop())
            ops.append(t)
        else: out.append(t)
    return out + ops[::-1]


def q9():
    a = " ".join(to_postfix("( 2 + 4 ) * 7 - 6 * 3 + 1".split()))
    st, rows = [], []
    for t in "5 6 * 4 2 / + 1 -".split():
        if t.isdigit(): st.append(int(t))
        else:
            y, x = st.pop(), st.pop()
            st.append({"+": x + y, "-": x - y, "*": x * y, "/": x // y}[t])
        rows.append(f"{t}→{st}")
    return f"(1) {a} (2) {' / '.join(rows)}. 결과 {st[0]}"


def q10():
    N, q, front, rear = 8, [None] * 8, 0, 0
    def add(x):
        nonlocal rear
        rear = (rear + 1) % N; q[rear] = x
    def delete():
        nonlocal front
        front = (front + 1) % N; q[front] = None
    for x in (10, 20, 30, 40, 50): add(x)
    for _ in range(3): delete()
    for x in (60, 70, 80, 90): add(x)
    return ", ".join(f"[{i}]={'빈칸' if v is None else v}" for i, v in enumerate(q)) + f", front={front}, rear={rear}"


def q11():
    # (루트, 왼쪽, 오른쪽)
    T = ("A", ("B", ("C", None, None), ("D", None, ("E", None, None))), ("F", ("G", ("H", None, None), None), None))
    arr = {}
    def put(t, i):
        if t: arr[i] = t[0]; put(t[1], 2 * i); put(t[2], 2 * i + 1)
    put(T, 1)
    pre = lambda t: [] if t is None else [t[0]] + pre(t[1]) + pre(t[2])
    ino = lambda t: [] if t is None else ino(t[1]) + [t[0]] + ino(t[2])
    post = lambda t: [] if t is None else post(t[1]) + post(t[2]) + [t[0]]
    j = lambda xs: ", ".join(xs)
    return (f"(1) {', '.join(f'[{i}]={v}' for i, v in sorted(arr.items()))}, 나머지 빈칸 "
            f"(2) {j(pre(T))} (3) {j(post(T))} (4) {j(ino(T))}")


def build(ino, post):
    if not ino: return None
    r = post[-1]; i = ino.index(r)
    return (r, build(ino[:i], post[:i]), build(ino[i + 1:], post[i:-1]))


def level(t):
    out, q = [], [t]
    while q:
        n = q.pop(0)
        if n: out.append(n[0]); q += [n[1], n[2]]
    return out


def q12():
    t = build("D,B,A,E,G,C,F,H".split(","), "D,B,G,E,H,F,C,A".split(","))
    edges = []
    def walk(n):
        if n is None: return
        if n[1]: edges.append(f"{n[0]}의 왼쪽 {n[1][0]}")
        if n[2]: edges.append(f"{n[0]}의 오른쪽 {n[2][0]}")
        walk(n[1]); walk(n[2])
    walk(t)
    return f"레벨 순서 {', '.join(level(t))}; " + ", ".join(edges)


def bst_from(order):
    def ins(t, k):
        if t is None: return [k, None, None]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        return t
    t = None
    for k in order: t = ins(t, k)
    return t


def shape(t): return None if t is None else (shape(t[1]), shape(t[2]))
def mirror(s): return None if s is None else (mirror(s[1]), mirror(s[0]))
def height(t): return 0 if t is None else 1 + max(height(t[1]), height(t[2]))


def q13():
    order = [5, 3, 7, 2, 4, 6, 8, 1, 9]
    t = bst_from(order); s = shape(t)
    assert s == mirror(s) and height(t) == 4  # 9개면 최소 높이 4
    return f"입력순서: {', '.join(map(str, order))} (좌우대칭·높이 4 확인)"


def q14():
    n = 16; arr, it = {}, iter(range(1, n + 1))
    def fill(i):
        if i > n: return
        fill(2 * i); arr[i] = next(it); fill(2 * i + 1)
    fill(1)
    order = [arr[i] for i in range(1, n + 1)]  # 레벨 순서로 넣으면 그 모양이 된다
    t = bst_from(order)
    lv = level(t)
    assert lv == order and height(t) == 5
    return "입력순서(레벨 순서): " + ", ".join(map(str, order))


GCD = r'''
#include <stdio.h>
int gcd(int i, int j){ if ( j == 0 ) return i; else return gcd( j, i%j ); }
int main(){ int i, j; while (scanf("%d %d", &i, &j) == 2) printf("%d ", gcd(i, j)); return 0; }
'''


def q15():
    import math
    pairs = [(12, 18), (18, 12), (7, 13), (100, 75), (1, 1)]
    out = run_c(GCD, " ".join(f"{a} {b}" for a, b in pairs)).split()
    ok = out == [str(math.gcd(a, b)) for a, b in pairs]
    return "모범답안 코드 실행: " + " ".join(f"gcd{p}={o}" for p, o in zip(pairs, out)) + ("" if ok else " (불일치)")


D2B = r'''
#include <stdio.h>
void dec_to_bin(int n){ if (n == 0) return; else { dec_to_bin(n / 2); printf("%d", n % 2); } }
int main(){ int d; scanf("%d", &d); dec_to_bin(d); return 0; }
'''


def q16():
    return "모범답안 코드 실행: " + ", ".join(f"{n} → {run_c(D2B, str(n))}" for n in (10, 13, 1))


if __name__ == "__main__":
    for i in range(1, 17):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
