"""unk-final-ltk 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
import os, subprocess, tempfile

SRC = "unk-final-ltk"


def run_c(code, stdin=""):
    with tempfile.TemporaryDirectory() as d:
        c, exe = os.path.join(d, "a.c"), os.path.join(d, "a.out")
        open(c, "w").write(code)
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wno-unused-variable", "-o", exe, c], check=True, capture_output=True)
        return subprocess.run([exe], input=stdin, capture_output=True, text=True, check=True, timeout=10).stdout


# 1: 문제 코드를 글자 그대로 돌려 대입 횟수를 센다(셋째 루프가 j를 증가시키는 것도 출제 의도로 본다.
#    같은 꼴의 2019-mid 9번 원본 답 30n(n-1)/2가 이 읽기와 맞는다)
Q1 = r'''
#include <stdio.h>
static int buffer[200][200];
int main(){ int i, j, p, k, n; long cnt;
  while (scanf("%d", &n) == 1) { cnt = 0;
    for(i=1; i<n; i++){
      for(j=1; j<n; j++){
        for(p=1; j<=i; j++){
          for(k=1; k<30; k++){
            buffer[i][j] = 1; cnt++;
          }
        }
      }
    }
    printf("%ld ", cnt); }
  return 0; }
'''


def q1():
    ns = [2, 3, 5, 10, 50, 100]
    got = list(map(int, run_c(Q1, " ".join(map(str, ns))).split()))
    assert got == [29 * n * (n - 1) // 2 for n in ns], got
    return "T(n) = 29n(n-1)/2, 빅오 표기법: O(n^2) (코드 그대로: 셋째 루프가 j를 i까지 올려 i마다 29·i번)"


def q2():
    N, front, rear = 7, 0, 0
    def add():
        nonlocal rear
        if (rear + 1) % N == front: return False  # 포화(한 칸 비움)
        rear = (rear + 1) % N; return True
    for _ in range(7): add()
    for _ in range(4): front = (front + 1) % N
    for _ in range(3): add()
    return f"front : {front}, rear : {rear}"


def ins(t, k):
    if t is None: return [k, None, None]
    if k < t[0]: t[1] = ins(t[1], k)
    else: t[2] = ins(t[2], k)
    return t


def dele(t, k):
    if t is None: return None
    if k < t[0]: t[1] = dele(t[1], k)
    elif k > t[0]: t[2] = dele(t[2], k)
    else:
        if t[1] is None: return t[2]
        if t[2] is None: return t[1]
        m = t[2]
        while m[1]: m = m[1]
        t[0] = m[0]; t[2] = dele(t[2], m[0])
    return t


def levels(t):
    out, lv = [], [t]
    while any(lv):
        out.append(", ".join(str(n[0]) for n in lv if n))
        lv = [c for n in lv if n for c in (n[1], n[2])]
    return " / ".join(out)


def build(ino, post):
    if not ino: return None
    r = post[-1]; i = ino.index(r)
    return [r, build(ino[:i], post[:i]), build(ino[i + 1:], post[i:-1])]


def q3():
    return "레벨 순서: " + levels(build("D,F,G,E,H,R,T,N,S,M,P,K".split(","), "F,D,E,G,R,T,S,N,P,M,K,H".split(",")))


def q4():
    t = None
    for k in (610, 410, 720, 200, 600, 650, 920, 550, 810, 520, 580, 790): t = ins(t, k)
    for k in (600, 920): t = dele(t, k)
    arr = {}
    def put(n, i):
        if n: arr[i] = n[0]; put(n[1], 2 * i); put(n[2], 2 * i + 1)
    put(t, 1)
    return f"레벨 순서: {levels(t)}. 배열: " + " ".join(f"[{i}]{v}" for i, v in sorted(arr.items()))


def q5():
    h = []
    for x in (90, 85, 80, 75, 70, 65):
        h.append(x); i = len(h) - 1
        while i > 0 and h[(i - 1) // 2] > h[i]: h[(i - 1) // 2], h[i] = h[i], h[(i - 1) // 2]; i = (i - 1) // 2
    a = list(h); last = h.pop(); h[0] = last; i = 0
    while 2 * i + 1 < len(h):
        c = 2 * i + 1
        if c + 1 < len(h) and h[c + 1] < h[c]: c += 1
        if h[i] <= h[c]: break
        h[i], h[c] = h[c], h[i]; i = c
    return f"삽입 후 {a}, 한 번 삭제 후 {h}"


def q6(): return "풀 수 없음: 가중치 그래프가 첨부 파일로만 주어졌고 원본 PDF에 없다."


def avl_ops(inserts, deletes):
    H = lambda t: t[3] if t else 0
    def fix(t): t[3] = 1 + max(H(t[1]), H(t[2])); return t
    def rr(t): l = t[1]; t[1] = l[2]; l[2] = fix(t); return fix(l)
    def rl(t): r = t[2]; t[2] = r[1]; r[1] = fix(t); return fix(r)
    def bal(t):
        fix(t); b = H(t[1]) - H(t[2])
        if b > 1:
            if H(t[1][1]) < H(t[1][2]): t[1] = rl(t[1])
            return rr(t)
        if b < -1:
            if H(t[2][2]) < H(t[2][1]): t[2] = rr(t[2])
            return rl(t)
        return t
    def ins(t, k):
        if t is None: return [k, None, None, 1]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        return bal(t)
    def dele(t, k):
        if t is None: return None
        if k < t[0]: t[1] = dele(t[1], k)
        elif k > t[0]: t[2] = dele(t[2], k)
        else:
            if t[1] is None: return t[2]
            if t[2] is None: return t[1]
            m = t[2]
            while m[1]: m = m[1]
            t[0] = m[0]; t[2] = dele(t[2], m[0])
        return bal(t)
    t = None
    for k in inserts: t = ins(t, k)
    a = levels(t)
    for k in deletes: t = dele(t, k)
    return a, levels(t)


def q7():
    a, b = avl_ops((15, 75, 95, 45, 35, 85, 25), (85,))
    return f"삽입 후 레벨 순서 {a}; 85 삭제 후 레벨 순서 {b}"


VAL = {c: 101 + i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz")}


def q8():
    bf = lambda s: sum(int(str(VAL[c])[::-1]) if i % 2 else VAL[c] for i, c in enumerate(s))
    sf = lambda s: sum(VAL[c] for c in s)
    t, coll, over = [[] for _ in range(10)], 0, 0
    for k in ["fine", "hill", "keep", "wave", "vine", "have"]:
        a = bf(k) % 10
        if t[a]: coll += 1
        if len(t[a]) == 2:
            over += 1; step = 7 - sf(k) % 7
            while len(t[a]) == 2:
                a = (a + step) % 10
                if t[a]: coll += 1
        t[a].append(k)
    return f"충돌 {coll}회, 오버플로우 {over}회. 테이블: " + " / ".join(f"[{i}] {', '.join(b)}" for i, b in enumerate(t) if b)


def q9(): return "풀 수 없음: 그래프·가중치 행렬이 첨부 파일로만 주어졌고 원본 PDF에 없다."


# 10: M=3 B-트리. 내부 키 삭제는 중위 후속자로, 부족하면 왼쪽 형제 → 오른쪽 형제에서 빌리고, 못 빌리면 왼쪽(없으면 오른쪽)과 합친다
class N:
    def __init__(s, keys=None, kids=None): s.keys, s.kids = keys or [], kids or []
    leaf = property(lambda s: not s.kids)


def bins(root, k):
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


def bdel(root, k):
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


def blevels(root):
    out, lv = [], [root]
    while lv:
        out.append(" ".join("[" + ",".join(map(str, n.keys)) + "]" for n in lv))
        lv = [c for n in lv for c in n.kids]
    return " / ".join(out)


def q10():
    t = N()
    for k in (40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90): t = bins(t, k)
    a = blevels(t)
    for k in (90, 50): t = bdel(t, k)
    t = bins(t, 100)
    return f"최종 {blevels(t)} (삽입 후 {a})"


if __name__ == "__main__":
    for i in range(1, 11):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
