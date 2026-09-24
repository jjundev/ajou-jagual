"""2019-mid 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
SRC = "2019-mid"


# 1~5: 정의형 OX — 실행으로 확인할 수 없음(원본 답)
def q1(): return "X"
def q2(): return "X"
def q3(): return "X"
def q4(): return "X"
def q5(): return "X"


def to_postfix(tokens):
    prec, out, ops = {"+": 1, "-": 1, "*": 2, "/": 2}, [], []
    for t in tokens:
        if t in prec:
            while ops and prec[ops[-1]] >= prec[t]: out.append(ops.pop())
            ops.append(t)
        else: out.append(t)
    return out + ops[::-1]


def q6():
    pf = to_postfix("5 * 6 + 4 / 2 - 1".split())
    push = pop = 0; st = []
    for t in pf:
        if t.isdigit(): st.append(int(t)); push += 1
        else:
            b, a = st.pop(), st.pop(); pop += 2
            st.append({"+": a + b, "-": a - b, "*": a * b, "/": a // b}[t]); push += 1
    return f"push {push}번, pop {pop}번 (후위식 {' '.join(pf)}, 결과 {st})"


def q7():
    N, front, rear = 8, 0, 0
    for _ in range(6): rear = (rear + 1) % N
    for _ in range(4): front = (front + 1) % N
    for _ in range(4): rear = (rear + 1) % N
    return f"front = {front}, rear = {rear}"


def q8():  # 코드를 여러 입력으로 돌려 gcd와 비교
    import math
    def foo(x, y): return y if x % y == 0 else foo(y, x % y)
    ok = all(foo(x, y) == math.gcd(x, y) for x in range(1, 60) for y in range(1, 60))
    return "x와 y의 최대공약수를 구해주는" + ("" if ok else " (불일치)")


def q9():
    # 복원본 코드가 깨져 있어(p 루프가 j를 증가, k 루프가 i를 증가) 그대로는 무한 루프다.
    # 실행으로 확인할 수 없음 → 원본 답
    return "T(n) = 30 * n(n-1) / 2\n빅오 표기법 : O(n^2)"


def bst_insert(t, k):
    if t is None: return [k, None, None]
    if k < t[0]: t[1] = bst_insert(t[1], k)
    else: t[2] = bst_insert(t[2], k)
    return t


def bst_delete(t, k):
    if t is None: return None
    if k < t[0]: t[1] = bst_delete(t[1], k)
    elif k > t[0]: t[2] = bst_delete(t[2], k)
    else:
        if t[1] is None: return t[2]
        if t[2] is None: return t[1]
        m = t[2]
        while m[1]: m = m[1]
        t[0] = m[0]; t[2] = bst_delete(t[2], m[0])
    return t


def to_array(t, i=1, arr=None):
    arr = {} if arr is None else arr
    if t: arr[i] = t[0]; to_array(t[1], 2 * i, arr); to_array(t[2], 2 * i + 1, arr)
    return arr


def fmt(arr): return ", ".join(f"{i}:{v}" for i, v in sorted(arr.items()))


def q10():
    t = None
    for k in (520, 490, 650, 380, 570, 250, 450, 610, 280, 430, 460, 580): t = bst_insert(t, k)
    for k in (250, 610): t = bst_delete(t, k)
    return fmt(to_array(t))


def build(ino, post):
    if not ino: return None
    r = post[-1]; i = ino.index(r)
    return [r, build(ino[:i], post[:i]), build(ino[i + 1:], post[i:-1])]


def q11():
    ino = "G F H E K C B D O M R P T".split()
    post = "G H P K E C O R T P M D B".split()
    post[2] = "F"  # 복원본 후위순회의 셋째 P는 F의 오기(F가 빠지고 P가 두 번)
    return fmt(to_array(build(ino, post)))


def q12():
    keys = list(range(110, 301, 10)); n = len(keys)
    # 완전이진트리 모양(1..n)에 중위 순서로 키를 채운다
    arr, it = {}, iter(keys)
    def fill(i):
        if i > n: return
        fill(2 * i); arr[i] = next(it); fill(2 * i + 1)
    fill(1)
    return fmt(arr)


def q13(): return "(원본 복원본에 문제 글이 없어 풀 수 없음)"


if __name__ == "__main__":
    for i in range(1, 14):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
