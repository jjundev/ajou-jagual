"""P9~P11 독립 검산 (저작자 작성, answers.py 를 import 하지 않음)."""
import heapq, math, random

# ---------- P9: 최소 히프, 배열 1번 칸부터 ----------
def min_insert(a, x):
    a.append(x); i = len(a) - 1           # a[0] 은 비워 둔 칸
    while i > 1 and a[i // 2] > a[i]:
        a[i // 2], a[i] = a[i], a[i // 2]; i //= 2

def min_delete(a):
    top = a[1]; last = a.pop()
    n = len(a) - 1
    if n == 0: return top
    a[1] = last; i = 1
    while 2 * i <= n:
        c = 2 * i
        if c + 1 <= n and a[c + 1] < a[c]: c += 1
        if a[i] <= a[c]: break
        a[i], a[c] = a[c], a[i]; i = c
    return top

def is_min_heap(v):
    return all(v[(k - 1) // 2] <= v[k] for k in range(1, len(v)))

ops = [("insert", 20), ("insert", 12), ("insert", 3), ("insert", 2), ("delete", None),
       ("insert", 5), ("insert", 16), ("delete", None), ("insert", 1), ("is_empty", None)]
a = [None]; ref = []
print("P9")
for name, x in ops:
    if name == "insert":
        min_insert(a, x); heapq.heappush(ref, x); out = ""
    elif name == "delete":
        r = min_delete(a); rr = heapq.heappop(ref); assert r == rr; out = f" -> {r}"
    else:
        out = f" -> {len(a) - 1 == 0}"
    assert is_min_heap(a[1:]) and sorted(a[1:]) == sorted(ref)
    print(f"  {name}({'' if x is None else x}){out}: {a[1:]}")
assert a[1:] == [1, 5, 12, 20, 16]
print("  final", a[1:], "is_empty", len(a) - 1 == 0)

# ---------- P10 ----------
print("P10")
# (a) 최악 경우 기본 동작 수를 직접 센다
def worst_counts(n):
    data = list(range(n))
    # 순서 없는 배열 삭제: 최댓값 찾으려 전부 비교
    unsorted_del = n - 1
    # 정렬된 배열(오름차순, 끝이 최대) 삽입: 새 최솟값이면 n칸 이동
    arr = data[:]; moves = 0; arr.append(None); x = -1; j = n - 1
    while j >= 0 and arr[j] > x: arr[j + 1] = arr[j]; j -= 1; moves += 1
    arr[j + 1] = x
    # 히프: 최악 이동 = 높이-1
    h = math.ceil(math.log2(n + 1))
    return unsorted_del, moves, h - 1
for n in (10, 1000, 1_000_000):
    c, m, sw = worst_counts(n)
    print(f"  n={n}: unsorted-array delete compares={c}, sorted-array insert moves={m}, heap path swaps<={sw}")
# (c)
n, i = 10, 5
left = 2 * i if 2 * i <= n else None
right = 2 * i + 1 if 2 * i + 1 <= n else None
print("  (c) left", left, "right", right, "parent", i // 2)
assert (left, right, i // 2) == (10, None, 2)

# ---------- P11: 슬라이드 의사코드 글자 그대로 ----------
def delete_max(A, heap_size, literal=True):
    log = []
    item = A[1]; A[1] = A[heap_size]; heap_size -= 1; i = 2
    while i <= heap_size:
        if literal:
            largest = i if (i < heap_size and A[i] > A[i + 1]) else i + 1
        else:
            largest = i + 1 if (i < heap_size and A[i + 1] > A[i]) else i
        p = largest // 2
        if A[p] > A[largest]:
            log.append((i, largest, "break")); break
        A[p], A[largest] = A[largest], A[p]
        log.append((i, largest, "swap")); i = largest * 2
    return item, heap_size, log

def is_max_heap(v):
    return all(v[(k - 1) // 2] >= v[k] for k in range(1, len(v)))

print("P11")
A = [0] * 200; A[1:11] = [9, 7, 6, 5, 4, 3, 2, 2, 1, 3]
item, hs, log = delete_max(A, 10)
print("  (a) log", log, "result", A[1:hs + 1], "item", item, "max-heap", is_max_heap(A[1:hs + 1]))
assert log == [(2, 2, "swap"), (4, 4, "swap"), (8, 8, "break")] and A[1:hs+1] == [7, 5, 6, 3, 4, 3, 2, 2, 1] and item == 9

A = [0] * 200; A[1:6] = [50, 40, 30, 20, 10]
item, hs, log = delete_max(A, 5)
print("  (b) literal log", log, "result", A[1:hs + 1], "A[5]", A[5], "item", item, "max-heap", is_max_heap(A[1:hs + 1]))
assert A[1:hs + 1] == [40, 10, 30, 20] and not is_max_heap(A[1:hs + 1])
A = [0] * 200; A[1:6] = [50, 40, 30, 20, 10]
item, hs, log = delete_max(A, 5, literal=False)
print("  (b) fixed   log", log, "result", A[1:hs + 1], "item", item, "max-heap", is_max_heap(A[1:hs + 1]))
assert A[1:hs + 1] == [40, 20, 30, 10] and is_max_heap(A[1:hs + 1])

# 고친 조건의 무작위 검사: 매번 최댓값을 돌려주고 힙 성질 유지
random.seed(1109); bad_literal = 0
for trial in range(3000):
    n = random.randint(1, 30)
    vals = [random.randint(0, 50) for _ in range(n)]
    heap = [-v for v in vals]; heapq.heapify(heap); lv = [-v for v in heap]  # 최대 힙 배치
    for literal in (False, True):
        A = [0] * 200; A[1:n + 1] = lv
        item, hs, _ = delete_max(A, n, literal)
        ok = item == max(vals) and is_max_heap(A[1:hs + 1])
        if literal: bad_literal += (not ok)
        else: assert ok
print("  random fixed: 3000 trials OK; literal broken cases:", bad_literal)
print("ALL OK")
