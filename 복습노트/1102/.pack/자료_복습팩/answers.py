"""1102 복습팩 정답 재계산 (저장소를 바꾸지 않는다).

트리는 {노드: (왼쪽, 오른쪽)} 딕셔너리로 적고, 슬라이드의 preorder·inorder·postorder·레벨 순회를
그대로 재귀/큐로 흉내 낸다.
"""
from collections import deque


def pre(t, r):
    if r is None:
        return []
    l, rr = t.get(r, (None, None))
    return [r] + pre(t, l) + pre(t, rr)


def ino(t, r):
    if r is None:
        return []
    l, rr = t.get(r, (None, None))
    return ino(t, l) + [r] + ino(t, rr)


def post(t, r):
    if r is None:
        return []
    l, rr = t.get(r, (None, None))
    return post(t, l) + post(t, rr) + [r]


def level(t, r):
    out, q = [], deque([r])
    while q:
        n = q.popleft()
        out.append(n)
        for c in t.get(n, (None, None)):
            if c is not None:
                q.append(c)
    return out


def array_rep(t, r):
    """배열 표현: 루트=1, 왼쪽 2i, 오른쪽 2i+1."""
    pos, stack = {}, [(r, 1)]
    while stack:
        n, i = stack.pop()
        pos[i] = n
        l, rr = t.get(n, (None, None))
        if l is not None:
            stack.append((l, 2 * i))
        if rr is not None:
            stack.append((rr, 2 * i + 1))
    return dict(sorted(pos.items()))


def build_in_post(inorder, postorder):
    """중위+후위 → 트리. 후위의 마지막이 루트, 중위에서 그 위치로 좌우를 나눈다."""
    t = {}

    def go(ino_, post_):
        if not ino_:
            return None
        root = post_[-1]
        k = ino_.index(root)
        l = go(ino_[:k], post_[:k])
        r = go(ino_[k + 1:], post_[k:-1])
        t[root] = (l, r)
        return root

    root = go(list(inorder), list(postorder))
    return t, root


def node_count(t, r):
    if r is None:
        return 0
    l, rr = t.get(r, (None, None))
    return 1 + node_count(t, l) + node_count(t, rr)


def height(t, r):
    if r is None:
        return 0
    l, rr = t.get(r, (None, None))
    return 1 + max(height(t, l), height(t, rr))


def fmt_arr(a):
    return ", ".join(f"[{i}]={v}" for i, v in a.items())


ans = {}

# 2018-mid-c024-q11: A(B(C, D(-, E)), F(G(H, -), -))
T11 = {'A': ('B', 'F'), 'B': ('C', 'D'), 'D': (None, 'E'), 'F': ('G', None), 'G': ('H', None)}
a11 = array_rep(T11, 'A')
assert a11 == {1: 'A', 2: 'B', 3: 'F', 4: 'C', 5: 'D', 6: 'G', 11: 'E', 12: 'H'}
ans['2018-mid-c024-q11'] = (
    f"(1) {fmt_arr(a11)} (2) {', '.join(pre(T11, 'A'))} "
    f"(3) {', '.join(post(T11, 'A'))} (4) {', '.join(ino(T11, 'A'))}")

# 2021-mock1-q6: 후위·중위 → 트리
t6, r6 = build_in_post("D F G E H R T N S M P K".split(), "F D E G R T S N P M K H".split())
assert post(t6, r6) == "F D E G R T S N P M K H".split()
assert ino(t6, r6) == "D F G E H R T N S M P K".split()
ans['2021-mock1-q6'] = "루트 H, 레벨 순서 " + " ".join(level(t6, r6))

# 2019-mid-q11: 후위 원문의 첫 P 는 F 의 오기(중위에 F 가 있고 후위에 P 가 두 번). F 로 읽고 푼다.
in11 = "G F H E K C B D O M R P T".split()
po11_raw = "G H P K E C O R T P M D B".split()
assert po11_raw.count('P') == 2 and 'F' not in po11_raw
po11 = "G H F K E C O R T P M D B".split()
t11b, r11b = build_in_post(in11, po11)
assert post(t11b, r11b) == po11 and ino(t11b, r11b) == in11
a11b = array_rep(t11b, r11b)
assert a11b == {1: 'B', 2: 'C', 3: 'D', 4: 'E', 7: 'M', 8: 'F', 9: 'K', 14: 'O', 15: 'P',
                16: 'G', 17: 'H', 30: 'R', 31: 'T'}
ans['2019-mid-q11'] = fmt_arr(a11b)

# 2018-mid-c024-q12: 중위·후위 → 트리 (문제 머리말은 "전위순회와 중위순회"지만 주어진 것은 중위·후위)
t12, r12 = build_in_post("D B A E G C F H".split(), "D B G E H F C A".split())
ans['2018-mid-c024-q12'] = "루트 A, 레벨 순서 " + " ".join(level(t12, r12))
assert level(t12, r12) == "A B C D E F G H".split()

ans['2018-mid-c024-q3'] = "후위 순회"
ans['2017-mid-c050-q5'] = "전위 순회"

# textbook ch08-q01: A(B(D, -), C(E, F)) 중위
TQ1 = {'A': ('B', 'C'), 'B': ('D', None), 'C': ('E', 'F')}
assert ino(TQ1, 'A') == "D B A E C F".split()
ans['textbook-ch08-q01'] = "④ D B A E C F"

# textbook ch08-q02: A(B(D, -), C(E(G, H), F)) 전위의 다섯 번째
TQ2 = {'A': ('B', 'C'), 'B': ('D', None), 'C': ('E', 'F'), 'E': ('G', 'H')}
p2 = pre(TQ2, 'A')
assert p2 == "A B D C E G H F".split() and p2[4] == 'E'
ans['textbook-ch08-q02'] = "② E"

# textbook ch08-q03: +( *( *( /(A,B), C ), D ), E ) 후위
TQ3 = {'+': ('*1', 'E'), '*1': ('*2', 'D'), '*2': ('/', 'C'), '/': ('A', 'B')}
p3 = [x.rstrip('12') for x in post(TQ3, '+')]
assert p3 == "A B / C * D * E +".split()
ans['textbook-ch08-q03'] = "④ A B / C * D * E +"

# textbook ch08-q12: 3(5(4, 2), 1(8, 6)), mystery = 단말 노드 값의 최댓값
TQ12 = {3: (5, 1), 5: (4, 2), 1: (8, 6)}


def mystery(t, p):
    if p is None:
        return 0
    l, r = t.get(p, (None, None))
    if l is None and r is None:
        return p
    return max(mystery(t, l), mystery(t, r))


assert mystery(TQ12, 3) == 8
ans['textbook-ch08-q12'] = "8"

# lecture-s07-p13-level-order: 수식 트리 a*b + c/d 의 레벨 순회와 큐 상태
TL = {'+': ('*', '/'), '*': ('a', 'b'), '/': ('c', 'd')}
q, states, visit = deque(['+']), [], []
while q:
    n = q.popleft()
    visit.append(n)
    for c in TL.get(n, (None, None)):
        if c is not None:
            q.append(c)
    states.append(f"{n} 방문 후 큐 [{' '.join(q)}]")
assert visit == "+ * / a b c d".split()
LEVEL_STATES = states
ans['lecture-s07-p13-level-order'] = (
    "(a) + * / a b c d (b) * 방문 직후 큐 [/ a b] (c) 전위 + * a b / c d, 중위 a * b + c / d, 후위 a b * c d / +")
assert states[1] == "* 방문 후 큐 [/ a b]"
assert pre(TL, '+') == "+ * a b / c d".split()
assert ino(TL, '+') == "a * b + c / d".split()
assert post(TL, '+') == "a b * c d / +".split()

# lecture-s07-p16-count-height: 수업 칠판 예 — 루트 R(왼쪽 X(왼 L1, 오 L2), 오른쪽 Y(왼 L3)) 6개
TC = {'R': ('X', 'Y'), 'X': ('L1', 'L2'), 'Y': ('L3', None)}
assert node_count(TC, 'X') == 3 and node_count(TC, 'Y') == 2 and node_count(TC, 'R') == 6
assert height(TC, 'R') == 3
ans['lecture-s07-p16-count-height'] = "(a) X 3, Y 2, R 6 (b) 3 (c) 1 + max(…) 의 1 은 루트 자기 자신(한 층)"

if __name__ == "__main__":
    for k, v in ans.items():
        print(k, "=>", v)
    print("레벨 순회 큐 상태:", *LEVEL_STATES, sep="\n  ")
    print("2021-mock1-q6 배열:", fmt_arr(array_rep(t6, r6)))
    print("2018-mid-c024-q12 배열:", fmt_arr(array_rep(t12, r12)))
