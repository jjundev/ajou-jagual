"""1109 Heap 복습문제 p1~p4 독립 검산 (문제설명 저작자 작성).

answers.py 를 import 하지 않고 처음부터 새로 쓴 시뮬레이션이에요.
- 배열은 첨자 1부터 쓰고 [0] 은 비워요(S8 p7: 왼쪽 2i, 오른쪽 2i+1, 부모 i//2).
- 삽입은 맨 끝에 놓고 upheap(부모보다 크면 교환), 삭제는 루트를 꺼내고
  마지막 요소를 루트로 올린 뒤 downheap(두 자식 중 큰 쪽과 교환).
- 매 연산 뒤 불변식(부모 >= 자식)을 검사해요. 배열 첨자 1..n 이 빈틈 없이 차므로
  완전 이진 트리 모양은 배열 표현 자체가 보장해요.
- 비교용으로 S8 p13 의사코드를 글자 그대로 옮긴 삭제도 돌려 차이를 기록해요.
"""


class MaxHeap:
    def __init__(self):
        self.a = [None]  # [0] 비움

    @property
    def n(self):
        return len(self.a) - 1

    def level(self):
        return self.a[1:]

    def check(self):
        for i in range(2, self.n + 1):
            assert self.a[i // 2] >= self.a[i], (i, self.a)

    def insert(self, k):
        self.a.append(k)
        i = self.n
        swaps = []
        while i > 1 and self.a[i // 2] < self.a[i]:
            swaps.append(self.a[i // 2])
            self.a[i // 2], self.a[i] = self.a[i], self.a[i // 2]
            i //= 2
        self.check()
        return swaps

    def delete(self):
        top = self.a[1]
        last = self.a.pop()
        swaps = []
        if self.n >= 1:
            self.a[1] = last
            i = 1
            while 2 * i <= self.n:
                c = 2 * i
                if c + 1 <= self.n and self.a[c + 1] > self.a[c]:
                    c += 1
                if self.a[i] >= self.a[c]:
                    break
                swaps.append(self.a[c])
                self.a[i], self.a[c] = self.a[c], self.a[i]
                i = c
        self.check()
        return top, last, swaps


def literal_slide_delete(level):
    """S8 p13 delete_max_heap 를 글자 그대로. 배열 200칸, 옛 값은 남아요."""
    A = [None] + list(level) + [None] * (200 - len(level))
    hs = len(level)
    item = A[1]
    A[1] = A[hs]
    hs -= 1
    i = 2
    while i <= hs:
        if i < hs and A[i] > A[i + 1]:
            largest = i
        else:
            largest = i + 1
        if A[largest // 2] > A[largest]:
            break
        A[largest // 2], A[largest] = A[largest], A[largest // 2]
        i = largest * 2
    return item, A[1:hs + 1]


def fmt(xs):
    return " ".join(map(str, xs)) if xs else "(빈 힙)"


def is_max_heap(level):
    return all(level[(j + 1) // 2 - 1] >= level[j] for j in range(1, len(level)))


out = []
P = out.append

# ---------------- p1 ----------------
P("[p1] 1) 삽입 15 16 18 17 19 20 12")
h = MaxHeap()
for k in [15, 16, 18, 17, 19, 20, 12]:
    sw = h.insert(k)
    P(f"  insert {k:>2}: 교환 상대 {sw or '-'} -> {fmt(h.level())}")
p1_built = h.level()
P("[p1] 2) 7번 삭제(힙정렬)")
removed = []
sorted_arr = [None] * 7
for idx in range(6, -1, -1):
    before = h.level()
    top, last, sw = h.delete()
    removed.append(top)
    sorted_arr[idx] = top  # S8 p15 처럼 a[n-1] 부터 채움
    lit_item, lit = literal_slide_delete(before)
    note = "" if lit == h.level() else f"  [슬라이드 글자 그대로면 {fmt(lit)} / 힙? {is_max_heap(lit)}]"
    P(f"  delete -> {top:>2}, 루트로 올린 값 {last}, 교환 상대 {sw or '-'} -> {fmt(h.level())}{note}")
P(f"  제거 순서 {removed}")
P(f"  a[n-1]부터 채운 결과 {sorted_arr} == sorted? {sorted_arr == sorted(p1_built)}")

# ---------------- p2 ----------------
P("[p2]")
h = MaxHeap()
for k in [16, 28, 41, 20, 25]:
    sw = h.insert(k)
    P(f"  insert {k}: 교환 상대 {sw or '-'} -> {fmt(h.level())}")
P(f"  (a) {fmt(h.level())}")
sw = h.insert(30)
P(f"  (b) insert 30: 교환 상대 {sw} -> {fmt(h.level())}")
before = h.level()
top, last, sw = h.delete()
lit_item, lit = literal_slide_delete(before)
P(f"  (c) delete -> {top}, 루트로 올린 값 {last}, 교환 상대 {sw} -> {fmt(h.level())}  [슬라이드 글자 그대로 {fmt(lit)}]")
arr = ["비움"] + h.level() + ["비움"] * (12 - h.n)
P("  (d) " + ", ".join(f"[{i}]={v}" for i, v in enumerate(arr)))
for i in range(1, h.n + 1):
    l, r = 2 * i, 2 * i + 1
    P(f"      i={i} 값 {h.a[i]}: 부모 [{i // 2 if i > 1 else '-'}] 왼쪽 [{l if l <= h.n else '없음'}] 오른쪽 [{r if r <= h.n else '없음'}]")
zero = h.level()
P(f"  첨자 0 시작으로 잘못 담으면 [0]={zero[0]} 의 자식을 2*0=0, 2*0+1=1 로 찾게 돼 자기 자신을 가리켜요")

# ---------------- p3 ----------------
P("[p3]")
h = MaxHeap()
for k in [10, 40, 30, 5, 12, 6, 60, 15]:
    sw = h.insert(k)
    P(f"  insert {k:>2}: 교환 상대 {sw or '-'} -> {fmt(h.level())}")
P(f"  (a) {fmt(h.level())}")
before = h.level()
top, last, sw = h.delete()
lit_item, lit = literal_slide_delete(before)
P(f"  (b) delete -> {top}, 루트로 올린 값 {last}, 교환 상대 {sw} -> {fmt(h.level())}  [슬라이드 글자 그대로 {fmt(lit)}]")

# ---------------- p4 ----------------
def run_p4(ops, label):
    P(f"[p4] 해석: {label}")
    h = MaxHeap()
    step = 0
    for op in ops:
        step += 1
        if op == "D":
            before = h.level()
            top, last, sw = h.delete()
            lit_item, lit = literal_slide_delete(before)
            P(f"  {step:>2} delete -> {top}, 루트로 올린 값 {last}, 교환 상대 {sw or '-'} -> {fmt(h.level())}"
              + ("" if lit == h.level() else f"  [슬라이드 글자 그대로 {fmt(lit)}]"))
        else:
            sw = h.insert(op)
            P(f"  {step:>2} insert {op}: 교환 상대 {sw or '-'} -> {fmt(h.level())}")
    P(f"  최종 {fmt(h.level())} (노드 {h.n}개)")
    return h.level()


first = [16, 9, 50, 41, 48, 24, 31]
second = [53, 71, 50, 68, 64]
a = run_p4(first + ["D"] + second + ["D", "D"], "삭제 1번 = 1회, 삭제 2번 = 2회(횟수)")
b = run_p4(first + ["D"] + second + ["D"], "삭제 2번 = 두 번째 삭제 1회(순번)")
P(f"  두 해석 결과가 다른가? {a != b}")

P("ALL CHECKS PASSED (모든 연산 뒤 부모 >= 자식 불변식 성립)")
print("\n".join(out))
