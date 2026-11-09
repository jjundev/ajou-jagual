"""Independent heap simulator (1-based array, S8 rules). Written from scratch."""
import math


class Heap:
    def __init__(self, kind="max", tie_child="right", swap_equal=False, log=True):
        # kind: max/min. tie_child: which child when children equal (lecture pseudocode -> right).
        # swap_equal: downheap swaps when parent == chosen child (lecture pseudocode does, via '>' break).
        self.a = [None]
        self.kind = kind
        self.tie_child = tie_child
        self.swap_equal = swap_equal
        self.log = log

    def better(self, x, y):  # strictly higher priority
        return x > y if self.kind == "max" else x < y

    @property
    def n(self):
        return len(self.a) - 1

    def arr(self):
        return self.a[1:]

    def insert(self, k):
        self.a.append(k)
        i = self.n
        steps = []
        while i > 1 and self.better(self.a[i], self.a[i // 2]):  # equal -> stop
            steps.append(f"{self.a[i]}<->{self.a[i//2]}")
            self.a[i], self.a[i // 2] = self.a[i // 2], self.a[i]
            i //= 2
        if self.log:
            print(f"  insert {k}: swaps={steps or '-'} -> {self.arr()}")

    def _down(self, i):
        steps = []
        while 2 * i <= self.n:
            l, r = 2 * i, 2 * i + 1
            c = l
            if r <= self.n:
                if self.better(self.a[r], self.a[l]):
                    c = r
                elif self.a[r] == self.a[l] and self.tie_child == "right":
                    c = r
            if self.better(self.a[c], self.a[i]) or (self.swap_equal and self.a[c] == self.a[i]):
                steps.append(f"{self.a[i]}<->{self.a[c]}")
                self.a[i], self.a[c] = self.a[c], self.a[i]
                i = c
            else:
                break
        return steps

    def _up(self, i):
        while i > 1 and self.better(self.a[i], self.a[i // 2]):
            self.a[i], self.a[i // 2] = self.a[i // 2], self.a[i]
            i //= 2

    def delete(self, idx=1):
        item = self.a[idx]
        last = self.a.pop()
        steps = []
        if idx <= self.n:
            self.a[idx] = last
            before = self.a[:]
            steps = self._down(idx)
            if self.a == before:
                self._up(idx)
        if self.log:
            print(f"  delete(idx {idx}) -> removed {item}, swaps={steps or '-'} -> {self.arr()}")
        return item

    def is_heap(self):
        return all(not self.better(self.a[i], self.a[i // 2]) for i in range(2, self.n + 1))


def levels(arr):
    out, i, w = [], 0, 1
    while i < len(arr):
        out.append(arr[i:i + w]); i += w; w *= 2
    return " / ".join(" ".join(map(str, l)) for l in out)


def build_heapify(keys, kind="max"):
    h = Heap(kind, log=False)
    h.a = [None] + list(keys)
    for i in range(h.n // 2, 0, -1):
        h._down(i)
    return h.arr()


def sec(t):
    print("\n" + "=" * 8, t)


sec("p1 max heap insert 15,16,18,17,19,20,12")
h = Heap("max")
for k in [15, 16, 18, 17, 19, 20, 12]:
    h.insert(k)
print("  heap:", h.arr(), "| levels:", levels(h.arr()))
print("  heap sort (7 deletions; in-place: removed goes to end):")
out = []
for _ in range(7):
    out.append(h.delete())
    print(f"     heap={h.arr()} sorted-tail={list(reversed(out))}")
print("  ascending:", list(reversed(out)))

sec("p2")
h = Heap("max")
for k in [16, 28, 41, 20, 25]:
    h.insert(k)
print("  (a)", h.arr(), "|", levels(h.arr()), "| heapify alt:", build_heapify([16, 28, 41, 20, 25]))
h.insert(30); print("  (b)", h.arr(), "|", levels(h.arr()))
h.delete(); print("  (c)", h.arr(), "|", levels(h.arr()))
print("  (d) [0]=empty,", {i: v for i, v in enumerate(h.arr(), 1)})
# heapify-alt chain
ha = Heap("max", log=False); ha.a = [None] + build_heapify([16, 28, 41, 20, 25])
ha.insert(30); b = ha.arr(); ha.delete()
print("  heapify-alt chain: (b)", b, "(c)", ha.arr())

sec("p3")
h = Heap("max")
for k in [10, 40, 30, 5, 12, 6, 60, 15]:
    h.insert(k)
print("  (a)", h.arr(), "|", levels(h.arr()))
h.delete(); print("  (b)", h.arr(), "|", levels(h.arr()))
alt = build_heapify([10, 40, 30, 5, 12, 6, 60, 15])
ha = Heap("max", log=False); ha.a = [None] + alt; ha.delete()
print("  heapify-alt: (a)", alt, "(b)", ha.arr())

sec("p4")
for tie, se in [("right", True), ("right", False), ("left", False), ("left", True)]:
    print(f" -- variant tie_child={tie} swap_equal={se}")
    h = Heap("max", tie_child=tie, swap_equal=se)
    for k in [16, 9, 50, 41, 48, 24, 31]:
        h.insert(k)
    h.delete()
    for k in [53, 71, 50, 68, 64]:
        h.insert(k)
    import copy
    hb = copy.deepcopy(h)
    h.delete(); h.delete()
    print("   A: delete twice ->", h.arr(), "|", levels(h.arr()), "heap?", h.is_heap())
    hb.delete(2)
    print("   B: '삭제 2번'=delete node at index 2 ->", hb.arr(), "|", levels(hb.arr()), "heap?", hb.is_heap())

sec("p5 min heap")
h = Heap("min")
for k in [90, 85, 80, 75, 70, 65]:
    h.insert(k)
h.delete()
print("  result", h.arr(), "|", levels(h.arr()))

sec("p7 height of 10-node complete tree")
n = 10
print("  levels(root=1):", math.floor(math.log2(n)) + 1, " edges:", math.floor(math.log2(n)))

sec("p8 min-heap check")
t = [None, 1, 2, 10, 4, 6, 11, 12, 6, 7, 5, 9]
bad = [(i // 2, t[i // 2], i, t[i]) for i in range(2, len(t)) if t[i] < t[i // 2]]
print("  complete (11 nodes idx1..11 filled): True; violations (parentIdx,parent,childIdx,child):", bad)

sec("p9 min heap ops")
h = Heap("min")
for op in ["i20", "i12", "i3", "i2", "d", "i5", "i16", "d", "i1", "e"]:
    if op[0] == "i":
        h.insert(int(op[1:]))
    elif op == "d":
        h.delete()
    else:
        print("  is_empty() ->", h.n == 0)
print("  result", h.arr(), "|", levels(h.arr()))

sec("p10 (c) n=10, i=5")
n, i = 10, 5
print("  left", 2 * i if 2 * i <= n else "없음", "right", 2 * i + 1 if 2 * i + 1 <= n else "없음", "parent", i // 2)


def literal_delete(A, hs):
    """Lecture S8 p13 pseudocode, literal (stale cells kept)."""
    A = A[:]
    item = A[1]; A[1] = A[hs]; hs -= 1; i = 2; trace = []
    while i <= hs:
        largest = i if (i < hs and A[i] > A[i + 1]) else i + 1
        p = largest // 2
        if A[p] > A[largest]:
            trace.append((i, largest, "break")); break
        A[p], A[largest] = A[largest], A[p]
        trace.append((i, largest, f"swap A[{p}]<->A[{largest}]"))
        i = largest * 2
    return item, A[1:hs + 1], trace, A


sec("p11 literal pseudocode")
A = [None] + [9, 7, 6, 5, 4, 3, 2, 2, 1, 3] + [0] * 189
item, res, tr, _ = literal_delete(A, 10)
print("  (a) trace", tr, "result", res, "return", item)
A = [None] + [50, 40, 30, 20, 10] + [0] * 194
item, res, tr, full = literal_delete(A, 5)
print("  (b) trace", tr, "result", res, "return", item, "A[5] stale", full[5])
h = Heap("max", log=False); h.a = [None] + res
print("      max heap?", h.is_heap())
