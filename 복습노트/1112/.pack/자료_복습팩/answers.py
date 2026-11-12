"""1112 복습팩 정답 재계산 (저장소를 바꾸지 않는다).

- 허프만: 최소 힙(heapq)에서 가장 작은 두 빈도를 꺼내 합을 다시 넣는다. 같은 빈도는 먼저 들어간 것이 먼저.
  코드 길이(깊이)는 트리에서 구하고, 총 비트 = sum(빈도 * 길이).
- 힙(최대/최소): 강의록 S8 p7 1-기반 배열, insert=upheap(S8 p10), delete=downheap(S8 p11-13; 오른쪽 자식 없을 때 왼쪽).
- heap_sort: S8 p15 프로그램 그대로(insert n번, i=n-1..0 에 delete 결과 저장).
- 이산 이벤트: 시각이 작은 이벤트부터 꺼내는 최소 우선순위 큐(heapq).
"""
import heapq, itertools


# ---------- 힙 ----------
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
        c = i + 1 if (i < n and better(A[i + 1], A[i], mx)) else i
        if not better(A[c], A[c // 2], mx):
            break
        A[c], A[c // 2] = A[c // 2], A[c]
        i = 2 * c
    return item


def arr(A):
    return " ".join(map(str, A[1:]))


# ---------- 허프만 ----------
def huffman(freqs):
    """freqs: list of (sym, f). 반환: (병합 기록, 길이 dict, 총비트, 트리)"""
    cnt = itertools.count()
    h = [(f, next(cnt), s) for s, f in freqs]
    heapq.heapify(h)
    merges = []
    while len(h) > 1:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        merges.append(f"{a[0]}+{b[0]}={a[0]+b[0]}")
        heapq.heappush(h, (a[0] + b[0], next(cnt), (a[2], b[2])))
    tree = h[0][2]
    depth = {}

    def walk(t, d):
        if isinstance(t, tuple):
            walk(t[0], d + 1)
            walk(t[1], d + 1)
        else:
            depth[t] = d

    walk(tree, 0)
    f = dict(freqs)
    total = sum(f[s] * depth[s] for s in f)
    return merges, depth, total, tree


def fixed_bits(n):
    b = 0
    while (1 << b) < n:
        b += 1
    return b


out = {}

# P1 2016-final-ljw-q4
fr = [("A", 15), ("B", 8), ("C", 20), ("D", 1), ("E", 5), ("F", 40), ("G", 9), ("H", 2)]
m, d, t, _ = huffman(fr)
out["p1"] = dict(fixed=(fixed_bits(8), fixed_bits(8) * 100), merges=m, lengths=d, total=t)

# P2 2021-mock1-q5
fr2 = [("s", 16), ("t", 35), ("u", 4), ("v", 8), ("w", 23), ("x", 19)]
m, d, t, _ = huffman(fr2)
out["p2"] = dict(merges=m, lengths=d, total=t)

# P3 textbook ch09-q04 : 정답 ① (S8 p14 "가장 큰 값 몇 개만 필요할 때")
out["p3"] = "①"

# P4 textbook ch09-q10
xs = [10, 40, 30, 5, 12, 6, 15, 9, 60]
A = [None]
steps = []
for x in xs:
    insert(A, x)
    steps.append(arr(A))
built = arr(A)
mx = delete(A)
out["p4"] = dict(steps=steps, array=built, deleted=mx, after=arr(A))

# P5 textbook ch09-q17
fr5 = [("a", 1), ("b", 1), ("c", 2), ("d", 3), ("e", 5), ("f", 8), ("g", 13), ("h", 21)]
m, d, t, _ = huffman(fr5)
out["p5"] = dict(merges=m, lengths=d, total=t, fixed=(fixed_bits(8), fixed_bits(8) * sum(f for _, f in fr5)))

# P6 heap_sort (S8 p15) on 1, 23, 7, 8, 20
a = [1, 23, 7, 8, 20]
H = [None]
ins = []
for x in a:
    insert(H, x)
    ins.append(arr(H))
outs = []
for i in range(len(a) - 1, -1, -1):
    a[i] = delete(H)
    outs.append((i, a[i], arr(H), list(a)))
out["p6"] = dict(insert_steps=ins, delete_steps=outs, result=a)

# P7 허프만 etnis — 최소 힙 배열 추적
fr7 = [("e", 15), ("t", 12), ("n", 8), ("i", 6), ("s", 4)]
m, d, t, _ = huffman(fr7)
N = sum(f for _, f in fr7)
fb = fixed_bits(len(fr7))
Hm = [None]
for f in sorted(f for _, f in fr7):  # 오름차순으로 넣음(강의: 오름차순 단말 노드화)
    insert(Hm, f, mx=False)
trace = [arr(Hm)]
while len(Hm) > 2:
    x = delete(Hm, mx=False)
    y = delete(Hm, mx=False)
    insert(Hm, x + y, mx=False)
    trace.append(f"{x}+{y}={x+y} -> [{arr(Hm)}]")
out["p7"] = dict(fixed=(fb, fb * N), merges=m, lengths=d, total=t,
                 saved=fb * N - t, ratio=round((fb * N - t) / (fb * N) * 100, 1), minheap=trace)

# P8 이산 이벤트 시뮬레이션
seats = 5
q = []
c = itertools.count()
for tm, k in [(6, 2), (1, 3), (8, 4), (3, 3)]:
    heapq.heappush(q, (tm, next(c), "arrival", k))
log, turned = [], 0
while q:
    tm, _, kind, k = heapq.heappop(q)
    if kind == "arrival":
        if seats >= k:
            seats -= k
            heapq.heappush(q, (tm + 1, next(c), "order", k))
            log.append(f"t={tm} arrival {k}명 착석(남은 의자 {seats})")
        else:
            turned += k
            log.append(f"t={tm} arrival {k}명 그냥 나감(남은 의자 {seats})")
    elif kind == "order":
        heapq.heappush(q, (tm + 3, next(c), "leave", k))
        log.append(f"t={tm} order {k}명")
    else:
        seats += k
        log.append(f"t={tm} leave {k}명(남은 의자 {seats})")
out["p8"] = dict(log=log, turned=turned, seats=seats)

if __name__ == "__main__":
    import json
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
