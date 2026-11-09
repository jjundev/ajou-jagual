"""1109 복습팩 정답 재계산 (저장소를 바꾸지 않는다).

힙은 강의록 S8 p7 대로 1-기반 배열(0번 비움)이다.
삽입은 S8 p10 insert_max_heap(upheap), 삭제는 S8 p13 delete_max_heap(downheap)을 옮겼다.
단, 오른쪽 자식이 없는 경우(i == heap_size)는 왼쪽 자식을 고르도록 보정했다(슬라이드 문자 그대로는
literal_delete 로 따로 재현해 P11 (b)에서 결함을 보인다).
"""


def better(a, b, mx):
    return a > b if mx else a < b


def insert(A, key, mx=True):
    A.append(key)
    i = len(A) - 1
    while i != 1 and better(A[i], A[i // 2], mx):
        A[i], A[i // 2] = A[i // 2], A[i]
        i //= 2


def delete(A, mx=True):
    item = A[1]
    A[1] = A[-1]
    A.pop()
    n = len(A) - 1
    i = 2
    while i <= n:
        if i < n and better(A[i + 1], A[i], mx):
            c = i + 1
        else:
            c = i
        if not better(A[c], A[c // 2], mx):
            break
        A[c], A[c // 2] = A[c // 2], A[c]
        i = 2 * c
    return item


def build(xs, mx=True):
    A = [None]
    for x in xs:
        insert(A, x, mx)
    return A


def literal_delete(A):
    """슬라이드 S8 p13 의사코드를 글자 그대로 (heap_size+1 칸의 옛 값까지 읽는다)."""
    A = A[:]
    n = len(A) - 1
    item = A[1]
    A[1] = A[n]
    n -= 1
    i = 2
    trace = []
    while i <= n:
        largest = i if (i < n and A[i] > A[i + 1]) else i + 1
        stop = A[largest // 2] > A[largest]
        trace.append((i, largest, "break" if stop else "swap"))
        if stop:
            break
        A[largest // 2], A[largest] = A[largest], A[largest // 2]
        i = 2 * largest
    return item, A[1:n + 1], trace


def is_heap(B, mx=True):
    return all(not better(B[k], B[(k - 1) // 2], mx) for k in range(1, len(B)))


R = {}

# P1 2015-ljw-q4: 15,16,18,17,19,20,12 → max heap, 힙 정렬
A = [None]
steps = []
for x in [15, 16, 18, 17, 19, 20, 12]:
    insert(A, x)
    steps.append(A[1:])
R["p1-insert"] = steps
out, rest = [], []
while len(A) > 1:
    out.append(delete(A))
    rest.append(A[1:])
R["p1-delete"] = rest
R["p1-order"] = out

# P2 2017-final-kdh-q1
A = build([16, 28, 41, 20, 25]); R["p2-a"] = A[1:]
insert(A, 30); R["p2-b"] = A[1:]
delete(A); R["p2-c"] = A[1:]

# P3 2017-final2-q1
A = build([10, 40, 30, 5, 12, 6, 60, 15]); R["p3-a"] = A[1:]
delete(A); R["p3-b"] = A[1:]

# P4 2019-final-q6
A = build([16, 9, 50, 41, 48, 24, 31]); R["p4-7ins"] = A[1:]
delete(A); R["p4-del1"] = A[1:]
for x in [53, 71, 50, 68, 64]:
    insert(A, x)
R["p4-5ins"] = A[1:]
delete(A); delete(A); R["p4-final"] = A[1:]

# P5 unk-final-ltk-q5 (min heap)
A = build([90, 85, 80, 75, 70, 65], mx=False); R["p5-ins"] = A[1:]
delete(A, mx=False); R["p5-final"] = A[1:]

# P6 textbook ch09-q02: 배열로 표현 가능한 이유 → ① 완전 이진 트리
R["p6"] = "①"

# P7 textbook ch09-q07: 10개 노드 힙의 높이 (S8 p6: 깊이 1,2,3,4 에 1,2,4,3개)
n, h, cap = 10, 0, 0
while cap < n:
    h += 1
    cap += 2 ** (h - 1)
R["p7"] = h

# P8 textbook ch09-q12: 레벨 순서 1,2,10,4,6,11,12,6,7,5,9
T = [1, 2, 10, 4, 6, 11, 12, 6, 7, 5, 9]
R["p8-violations"] = [(T[(k - 1) // 2], T[k]) for k in range(1, len(T)) if T[k] < T[(k - 1) // 2]]

# P9 textbook ch09-q13 (min heap)
A = [None]
log = []
for op in ["i20", "i12", "i3", "i2", "d", "i5", "i16", "d", "i1"]:
    if op == "d":
        log.append(("delete", delete(A, mx=False), A[1:]))
    else:
        insert(A, int(op[1:]), mx=False)
        log.append(("insert", int(op[1:]), A[1:]))
R["p9-log"] = log
R["p9-final"] = A[1:]
R["p9-is_empty"] = len(A) == 1

# P10 lecture-s08-p04: 비교표·인덱스
R["p10-table"] = {
    "순서 없는 배열": ("O(1)", "O(n)"),
    "순서 없는 연결 리스트": ("O(1)", "O(n)"),
    "정렬된 배열": ("O(n)", "O(1)"),
    "정렬된 연결 리스트": ("O(n)", "O(1)"),
    "히프": ("O(log n)", "O(log n)"),
}
i, size = 5, 10
R["p10-index"] = {"left": 2 * i, "right": 2 * i + 1 if 2 * i + 1 <= size else None, "parent": i // 2}

# P11 lecture-s08-p13
R["p11-a"] = literal_delete([None, 9, 7, 6, 5, 4, 3, 2, 2, 1, 3])
R["p11-b-literal"] = literal_delete([None, 50, 40, 30, 20, 10])
A = [None, 50, 40, 30, 20, 10]; delete(A); R["p11-b-fixed"] = A[1:]

if __name__ == "__main__":
    for k, v in R.items():
        print(k, v)
    assert R["p1-insert"][-1] == [20, 18, 19, 15, 17, 16, 12]
    assert R["p1-order"] == [20, 19, 18, 17, 16, 15, 12]
    assert R["p2-a"] == [41, 25, 28, 16, 20] and R["p2-b"] == [41, 25, 30, 16, 20, 28] and R["p2-c"] == [30, 25, 28, 16, 20]
    assert R["p3-a"] == [60, 15, 40, 12, 10, 6, 30, 5] and R["p3-b"] == [40, 15, 30, 12, 10, 6, 5]
    assert R["p4-final"] == [64, 53, 48, 50, 24, 16, 31, 9, 41]
    assert R["p5-final"] == [70, 75, 85, 90, 80]
    assert R["p7"] == 4
    assert R["p8-violations"] == [(6, 5)]
    assert R["p9-final"] == [1, 5, 12, 20, 16] and R["p9-is_empty"] is False
    assert R["p10-index"] == {"left": 10, "right": None, "parent": 2}
    assert R["p11-a"][1] == [7, 5, 6, 3, 4, 3, 2, 2, 1]
    assert R["p11-b-literal"][1] == [40, 10, 30, 20] and not is_heap(R["p11-b-literal"][1])
    assert R["p11-b-fixed"] == [40, 20, 30, 10] and is_heap(R["p11-b-fixed"])
    print("ALL OK")
