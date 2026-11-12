#!/usr/bin/env python3
"""1112 Heap 복습문제 독립 검산 (표준 라이브러리만).

작성자 정답·풀이를 보지 않고 problems-only.txt 의 문제 문장만으로 계산한다.
대상: p1, p2, p5, p7 (허프만), p4 (최대 힙 삽입·삭제), p7(b) (최소 힙 시뮬레이션),
      p8 (이산 이벤트 시뮬레이션, 최소 우선순위 큐 vs FIFO).
"""
import heapq
import itertools
import math
import random
from collections import Counter, deque

# ---------------------------------------------------------------- 허프만 공통

class Node:
    def __init__(self, freq, sym=None, left=None, right=None):
        self.freq, self.sym, self.left, self.right = freq, sym, left, right

    def is_leaf(self):
        return self.sym is not None

    def __repr__(self):
        return self.sym if self.is_leaf() else f"({self.left!r},{self.right!r})"


def huffman(freqs, tie="fifo", seed=None):
    """우선순위 큐 허프만. 먼저 꺼낸 것을 왼쪽 자식으로 둔다.

    tie: 같은 빈도 사이의 꺼내는 순서를 바꾸는 규칙
      fifo      먼저 들어온 노드 먼저
      lifo      나중에 들어온 노드 먼저
      leaf      단말 먼저
      internal  내부 노드 먼저
      random    임의 (seed)
    """
    rng = random.Random(seed)
    counter = itertools.count()
    pq = []

    def key(node):
        c = next(counter)
        if tie == "fifo":
            k = c
        elif tie == "lifo":
            k = -c
        elif tie == "leaf":
            k = (0 if node.is_leaf() else 1, c)
        elif tie == "internal":
            k = (1 if node.is_leaf() else 0, c)
        else:
            k = rng.random()
        return (node.freq, k, c)

    for s, f in freqs.items():
        n = Node(f, sym=s)
        heapq.heappush(pq, (key(n), n))
    merges = []
    while len(pq) > 1:
        _, a = heapq.heappop(pq)
        _, b = heapq.heappop(pq)
        p = Node(a.freq + b.freq, left=a, right=b)
        merges.append((a.freq, b.freq, p.freq, repr(a), repr(b)))
        heapq.heappush(pq, (key(p), p))
    return pq[0][1], merges


def codes_of(root, prefix=""):
    if root.is_leaf():
        return {root.sym: prefix or "0"}
    d = {}
    d.update(codes_of(root.left, prefix + "0"))
    d.update(codes_of(root.right, prefix + "1"))
    return d


def total_bits(freqs, codes):
    return sum(freqs[s] * len(codes[s]) for s in freqs)


def fixed_bits(n_symbols):
    return max(1, math.ceil(math.log2(n_symbols)))


def tie_variation_report(freqs, label):
    """같은 빈도 동점 처리를 바꿔도 길이 다중집합·총 비트가 같은지 본다."""
    results = set()
    per_symbol = set()
    variants = ["fifo", "lifo", "leaf", "internal"] + [("random", s) for s in range(200)]
    for v in variants:
        if isinstance(v, tuple):
            root, _ = huffman(freqs, tie="random", seed=v[1])
        else:
            root, _ = huffman(freqs, tie=v)
        c = codes_of(root)
        lens = tuple(sorted(len(x) for x in c.values()))
        results.add((lens, total_bits(freqs, c)))
        per_symbol.add(tuple(sorted((s, len(c[s])) for s in freqs)))
    print(f"[{label}] 동점 변형 {len(variants)}가지 → (길이 다중집합, 총 비트) 종류 수 = {len(results)}")
    for r in sorted(results):
        print(f"    길이 다중집합 {r[0]}  총 {r[1]} bit")
    print(f"    글자별 코드 길이 배정 종류 수 = {len(per_symbol)}")
    for r in sorted(per_symbol):
        print(f"      {dict(r)}")
    return results, per_symbol


def equal_freqs(freqs):
    c = Counter(freqs.values())
    return {f: n for f, n in c.items() if n > 1}


def print_huffman(freqs, label):
    root, merges = huffman(freqs, tie="fifo")
    print(f"[{label}] 빈도 {freqs}  합 {sum(freqs.values())}")
    print(f"    같은 빈도(단말끼리): {equal_freqs(freqs) or '없음'}")
    for i, (a, b, s, ra, rb) in enumerate(merges, 1):
        print(f"    병합 {i}: {a} + {b} = {s}    (왼 {ra}, 오른 {rb})")
    c = codes_of(root)
    for s in freqs:
        print(f"    {s}: 빈도 {freqs[s]:>3}  코드 {c[s]:<8} 길이 {len(c[s])}")
    tb = total_bits(freqs, c)
    fb = fixed_bits(len(freqs))
    n = sum(freqs.values())
    print(f"    트리: {root!r}")
    print(f"    허프만 총 비트 = {tb}")
    print(f"    고정 길이: 글자 {len(freqs)}종 → {fb} bit/글자, 총 {fb * n} bit")
    print(f"    절약 = {fb * n - tb} bit ({(fb * n - tb) / (fb * n) * 100:.4f}%)")
    return root, merges, c, tb


def shape(node):
    """좌우 교환을 허용한 모양 (정규형)."""
    if node.is_leaf():
        return "L"
    a, b = sorted([shape(node.left), shape(node.right)])
    return f"({a},{b})"


class T:  # 틀의 노드 (sym 없음)
    def __init__(self, left=None, right=None):
        self.left, self.right = left, right

    def is_leaf(self):
        return self.left is None


def tshape(t):
    if t.is_leaf():
        return "L"
    a, b = sorted([tshape(t.left), tshape(t.right)])
    return f"({a},{b})"


def orient(node, tmpl):
    """node 를 틀의 좌우 배치에 맞춰 돌린다. 맞으면 새 Node, 아니면 None."""
    if tmpl.is_leaf():
        return node if node.is_leaf() else None
    if node.is_leaf():
        return None
    for l, r in ((node.left, node.right), (node.right, node.left)):
        ol, orr = orient(l, tmpl.left), orient(r, tmpl.right)
        if ol is not None and orr is not None:
            return Node(node.freq, left=ol, right=orr)
    return None


def all_orientations(node, tmpl):
    if tmpl.is_leaf():
        return [node] if node.is_leaf() else []
    if node.is_leaf():
        return []
    out = []
    for l, r in ((node.left, node.right), (node.right, node.left)):
        for ol in all_orientations(l, tmpl.left):
            for orr in all_orientations(r, tmpl.right):
                out.append(Node(node.freq, left=ol, right=orr))
    return out


def draw(node, indent="    ", edge=""):
    label = f"{node.sym}:{node.freq}" if node.is_leaf() else f"[{node.freq}]"
    print(f"{indent}{edge}{label}")
    if not node.is_leaf():
        draw(node.left, indent + "    ", "0─ ")
        draw(node.right, indent + "    ", "1─ ")


# ---------------------------------------------------------------- 문제별

def p1():
    print("=" * 70)
    print("p1 허프만 (A~H, 100글자)")
    freqs = dict(A=15, B=8, C=20, D=1, E=5, F=40, G=9, H=2)
    print(f"    표의 글자 수 = {len(freqs)} (문제 문장은 '7가지'), 빈도 합 = {sum(freqs.values())}")
    print(f"    7가지라고 해도 ceil(log2 7) = {fixed_bits(7)}, 8가지면 {fixed_bits(8)} → 어느 쪽이든 3bit, 300bit")
    root, _, c, tb = print_huffman(freqs, "p1")
    draw(root)
    tie_variation_report(freqs, "p1")
    return c, tb


def p2():
    print("=" * 70)
    print("p2 허프만 (s~x, 105글자) + 틀 모양 비교")
    freqs = dict(s=16, t=35, u=4, v=8, w=23, x=19)
    root, _, _, tb = print_huffman(freqs, "p2")
    # 틀: 루트(왼 I(L, I(I(L,L), L)), 오른 I(L,L))
    tmpl = T(T(T(), T(T(T(), T()), T())), T(T(), T()))
    print(f"    틀 모양(정규형)   = {tshape(tmpl)}")
    print(f"    병합 트리(정규형) = {shape(root)}")
    print(f"    좌우 교환 허용 시 같은 모양? {tshape(tmpl) == shape(root)}")
    ors = all_orientations(root, tmpl)
    print(f"    틀 배치에 맞는 좌우 배치 수 = {len(ors)}")
    for o in ors:
        c = codes_of(o)
        print("      " + "  ".join(f"{s}={c[s]}" for s in freqs) + f"   총 {total_bits(freqs, c)} bit")
    o = ors[0]
    print("    제시 코드(틀 배치, left 0 / right 1, 첫 배치):")
    draw(o)
    c = codes_of(o)
    for s in freqs:
        print(f"      {s}: {c[s]}")
    tie_variation_report(freqs, "p2")
    return c, tb


def p4():
    print("=" * 70)
    print("p4 최대 힙 (1번 칸부터)")
    data = [10, 40, 30, 5, 12, 6, 15, 9, 60]
    h = [None]
    print("  (1) 삽입 과정")
    for x in data:
        h.append(x)
        i = len(h) - 1
        steps = []
        while i > 1 and h[i] > h[i // 2]:
            steps.append(f"{h[i]}<->{h[i // 2]}(칸{i}↔{i // 2})")
            h[i], h[i // 2] = h[i // 2], h[i]
            i //= 2
        print(f"    insert {x:>2}: 교환 {steps or '없음'} → {h[1:]}")
    final = h[1:]
    print(f"  (2) 최종 배열 heap[1..9] = {final}")
    print("  (3) 최댓값 삭제")
    mx = h[1]
    last = h.pop()
    h[1] = last
    print(f"    루트 {mx} 제거, 마지막 원소 {last} 를 루트로 → {h[1:]}")
    i = 1
    n = len(h) - 1
    while 2 * i <= n:
        c = 2 * i
        if c + 1 <= n and h[c + 1] > h[c]:
            c += 1
        if h[i] >= h[c]:
            print(f"    {h[i]} >= 큰 자식 {h[c]} → 멈춤")
            break
        print(f"    {h[i]} < 큰 자식 {h[c]}(칸{c}) → 교환")
        h[i], h[c] = h[c], h[i]
        print(f"      → {h[1:]}")
        i = c
    else:
        print(f"    칸{i} 는 자식 없음 → 멈춤")
    print(f"    삭제 후 배열 = {h[1:]}")
    return final, h[1:]


def p5():
    print("=" * 70)
    print("p5 허프만 (a~h 피보나치 빈도)")
    freqs = dict(a=1, b=1, c=2, d=3, e=5, f=8, g=13, h=21)
    root, _, c, tb = print_huffman(freqs, "p5")
    draw(root)
    tie_variation_report(freqs, "p5")
    return c, tb


def p7():
    print("=" * 70)
    print("p7 허프만 (e t n i s, 45글자) + 최소 힙 시뮬레이션")
    freqs = dict(e=15, t=12, n=8, i=6, s=4)
    n = sum(freqs.values())
    fb = fixed_bits(len(freqs))
    print(f"  (a) {len(freqs)}글자 → {fb} bit/글자, 총 {fb * n} bit")

    # (b) 문제 규칙 그대로의 최소 힙 (1번 칸, upheap, downheap 더 작은 자식)
    h = [None]
    tie_events = []

    def ins(x):
        h.append(x)
        i = len(h) - 1
        while i > 1 and h[i] < h[i // 2]:
            h[i], h[i // 2] = h[i // 2], h[i]
            i //= 2

    def dele():
        top = h[1]
        last = h.pop()
        if len(h) > 1:
            h[1] = last
            i = 1
            m = len(h) - 1
            while 2 * i <= m:
                c = 2 * i
                if c + 1 <= m:
                    if h[c + 1] == h[c]:
                        tie_events.append(("자식 동점", list(h[1:])))
                    if h[c + 1] < h[c]:
                        c += 1
                if h[i] == h[c]:
                    tie_events.append(("부모=자식", list(h[1:])))
                if h[i] > h[c]:
                    h[i], h[c] = h[c], h[i]
                    i = c
                else:
                    break
        return top

    print("  (b) 초기 삽입")
    for x in [4, 6, 8, 12, 15]:
        ins(x)
        print(f"    insert {x:>2} → {h[1:]}")
    k = 0
    while len(h) > 2:
        k += 1
        a = dele()
        after1 = list(h[1:])
        b = dele()
        after2 = list(h[1:])
        ins(a + b)
        print(f"    반복 {k}: 꺼냄 {a}, {b} (첫 삭제 뒤 {after1}, 둘째 삭제 뒤 {after2}) → 합 {a + b} 삽입 직후 {h[1:]}")
    print(f"    downheap 동점 발생: {tie_events or '없음'}")

    root, _, c, tb = print_huffman(freqs, "p7(c)")
    draw(root)
    tie_variation_report(freqs, "p7")
    saved = fb * n - tb
    print(f"  (c) 총 {tb} bit, 절약 {saved} bit = {saved}/{fb * n} = {saved / (fb * n) * 100:.4f}%")
    return c, tb


def p8():
    print("=" * 70)
    print("p8 아이스크림 가게 이산 이벤트 시뮬레이션")
    init = [(6, "arrival", 2), (1, "arrival", 3), (8, "arrival", 4), (3, "arrival", 3)]

    def run(kind):
        chairs = 5
        lost = 0
        seq = itertools.count()
        if kind == "pq":
            q = []
            for e in init:
                heapq.heappush(q, (e[0], next(seq), e))

            def push(e):
                heapq.heappush(q, (e[0], next(seq), e))

            def pop():
                return heapq.heappop(q)[2]
        else:
            q = deque(init)

            def push(e):
                q.append(e)

            def pop():
                return q.popleft()
        log = []
        times_seen = Counter()
        while q:
            t, typ, k = pop()
            times_seen[t] += 1
            note = ""
            if typ == "arrival":
                if chairs >= k:
                    chairs -= k
                    push((t + 1, "order", k))
                    note = f"착석 {k}, order@{t + 1}"
                else:
                    lost += k
                    note = f"의자 부족 → {k}명 나감"
            elif typ == "order":
                push((t + 3, "leave", k))
                note = f"leave@{t + 3}"
            else:
                chairs += k
                note = f"의자 {k} 반납"
            log.append((t, typ, k, chairs, note))
        return log, lost, chairs, times_seen

    for kind, name in (("pq", "최소 우선순위 큐(시각 기준)"), ("fifo", "FIFO 큐")):
        log, lost, chairs, seen = run(kind)
        print(f"  [{name}]")
        for i, (t, typ, k, ch, note) in enumerate(log, 1):
            print(f"    {i:>2}. ({t}, {typ}, {k})  남은 의자 {ch}   {note}")
        times = [x[0] for x in log]
        print(f"    처리 시각 열 = {times}  단조 증가? {times == sorted(times)}")
        dup = {t: c for t, c in seen.items() if c > 1}
        print(f"    같은 시각 이벤트(동점) = {dup or '없음'}")
        print(f"    주문 없이 나간 손님 = {lost}, 마지막 남은 의자 = {chairs}")
    print("  비교: 두 큐의 최종 수치(나간 손님·남은 의자)는 이번 입력에서 우연히 같다.")
    print("        그러나 FIFO 는 시각 6 도착을 시각 1 도착보다 먼저 처리해, 시각 3 도착 시점의")
    print("        의자 상태가 '미래' 손님 때문에 0 으로 계산되는 등 인과 순서가 깨진다.")


if __name__ == "__main__":
    p1()
    p2()
    p4()
    p5()
    p7()
    p8()
