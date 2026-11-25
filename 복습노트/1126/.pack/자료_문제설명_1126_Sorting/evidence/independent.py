from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]

def trace(name, title, states):
    trace_data = {
        "version": 1, "id": name, "title": title,
        "structures": [{"id": "a", "kind": "array", "label": "배열", "size": len(states[0][1])}],
        "steps": [{"text": label, "state": {"a": {"values": values, "hi": marks, "ptr": {}}}, "key": i in {0, len(states)//2, len(states)-1}}
                  for i,(label, values, marks) in enumerate(states)]
    }
    (root / "traces" / (name + ".json")).write_text(json.dumps(trace_data, ensure_ascii=False, indent=2), encoding="utf-8")

def quick(values):
    data = list(values)
    swaps, partitions, leaves = [], [], []
    def split(a, b, depth=0, parent=None, side=None):
        if a == b:
            leaves.append((parent, side, data[a]))
        if a >= b:
            return
        pivot = data[a]
        i, j = a + 1, b
        def swap(i, j):
            if i != j:
                label = f"{data[i]} ↔ {data[j]}  (피벗 {pivot})"
                data[i], data[j] = data[j], data[i]
                swaps.append((label, data[:], [i, j]))
        while i <= j:
            while i <= j and data[i] < pivot:
                i += 1
            while j >= i and data[j] > pivot:
                j -= 1
            if i >= j:
                break
            swap(i, j)
            i += 1
            j -= 1
        swap(a, j)
        assert j == a + sum(x < pivot for x in data[a:b+1])
        assert all(x < pivot for x in data[a:j]) and all(x > pivot for x in data[j+1:b+1])
        partitions.append((depth, a, b, j, pivot, parent, side, data[:]))
        split(a, j - 1, depth + 1, pivot, "L")
        split(j + 1, b, depth + 1, pivot, "R")
    split(0, len(data) - 1)
    assert data == sorted(values)
    return swaps, partitions, leaves

p1 = [27,4,37,2,62,12,59,16,49,18]
p1_swaps, p1_rows, p1_leaves = quick(p1)
print("p1: partition order, breadth levels, pivot rank and swaps", p1_rows, p1_swaps, sep="\n")
trace("p1-partitions", "P1 퀵 정렬 분할", [("초기 피벗 27", p1, [0])] + [(f"피벗 {p} 확정", values, [j]) for _,_,_,j,p,_,_,values in p1_rows])

shell = [14,5,43,27,18,31,37,88,6,35]
for g in (5,3,1):
    previous = shell[:]
    for r in range(g):
        shell[r::g] = sorted(previous[r::g])
        assert Counter(shell[r::g]) == Counter(previous[r::g])
    print("p2 Shell",g,shell)
p2 = [9,73,42,1,80,39,72,30,100,46,82,32,17]
_, p2_rows, p2_leaves = quick(p2)
print("p2 partition and singleton successors",[(p, parent, side) for _,_,_,_,p,parent,side,_ in p2_rows],p2_leaves)
trace("p2-partitions", "P2 실제 피벗의 확정 순서", [("초기 피벗 9", p2, [0])] + [(f"피벗 {p} 확정", values, [j]) for _,_,_,j,p,_,_,values in p2_rows])

p3 = [7,4,9,6,3,8]
a = p3[:]
states = [("초기 배열", p3, [])]
passes = []
for i in range(1,len(a)):
    j = i
    while j > 0 and a[j-1] < a[j]:
        label = f"{a[j-1]} ↔ {a[j]}"
        a[j-1], a[j] = a[j], a[j-1]
        states.append((label, a[:], [j-1,j]))
        j -= 1
    assert a[:i+1] == sorted(p3[:i+1], reverse=True)
    passes.append(a[:])
assert len(states)-1 == sum(x < y for x,y in combinations(p3,2)) == 7
print("p3 swaps, passes",states,passes)
trace("p3-swaps","P3 내림차순 삽입 정렬 교환",states)

p4 = [25,3,50,72,9,46,15]
swaps, rows, leaves = quick(p4)
print("p4 swaps and ranks",swaps,[(row[4],row[3]) for row in rows])
trace("p4-swaps","P4 퀵 정렬 교환",[("초기 피벗 25",p4,[0])] + swaps)

p5 = [(2,"A"),(2,"B"),(1,"")]
assert [p5[2],p5[1],p5[0]] == [(1,""), (2,"B"), (2,"A")]
assert sorted(p5,key=lambda it:it[0]) == [(1,""),(2,"A"),(2,"B")]
print("p5:a exchange crosses B; p5:b equal predecessors are not shifted, so equal pairs never cross")

def bubble(a, n_pass=None):
    a = a[:]
    counts, stages = [], []
    for end in range(len(a)-1,0,-1):
        if n_pass is not None and len(stages) == n_pass:
            break
        moves = 0
        for i in range(end):
            if a[i] > a[i+1]:
                a[i],a[i+1] = a[i+1],a[i]
                moves += 3
        counts.append((end,moves))
        stages.append(a[:])
    return counts, stages
for p in ([1,2,3,4,5],[5,4,3,2,1]):
    stats, stages = bubble(p)
    assert sum(m for _,m in stats) == 3 * sum(x>y for x,y in combinations(p,2))
    print("p6",p,stats,stages)

for tie_first in ("A","B"):
    left,right = [2,5,7],[1,4,5]
    l,r=0,0
    moves,stages = [],[]
    while l < len(left) and r < len(right):
        x,y = left[l],right[r]
        use_left = x < y or x == y and tie_first == "A"
        moves.append((x,y))
        stages.append(f"{x}{'A' if x==5 else ''}" if use_left else f"{y}{'B' if y==5 else ''}")
        l+=use_left
        r+=not use_left
    assert (len(stages), left[l:]+right[r:]) == ((5,[7]) if tie_first=="A" else (4,[5,7]))
    assert [s for s in stages if s.startswith("5")][0] == "5"+tie_first
    print("p7",tie_first,moves,stages,left[l:]+right[r:])
    if tie_first == "A":
        trace("p7-merge","P7 임시 배열에 기록한 합병 결과",
            [("임시 배열 초기 상태",["·"]*6,[])] +
            [(f"{i}번째 선두 비교 뒤 기록" if i<6 else "남은 7을 비교 없이 복사",
              (stages+["7"])[:i]+["·"]*(6-i),[i-1]) for i in range(1,7)])
assert 4*2*2 + 2*4*2 + 1*8*2 == 48
print("p7:c one write per direction per record in each of 3 layers")

assert bubble([9,6,7,3,5],1)[1][0] == [6,7,3,5,9]
print("p8: option 2")

a=[8,3,4,9,7]
for i in range(3):
    m=min(range(i,len(a)),key=a.__getitem__)
    a[i],a[m]=a[m],a[i]
    assert a[:i+1] == sorted(a)[:i+1]
    print("p9",i+1,a)
assert a == [3,4,7,9,8]

def insertion(a, option):
    a = list(a)
    shifts = 0
    for i in range(1,len(a)):
        j,k=i-1,a[i]
        while (j>=0 if option in (1,4) else j>0) and ((k>a[j]) if option==1 else (k>=a[j]) if option==2 else (k<a[j])):
            if option in (1,4):
                a[j+1] = a[j]
            elif option == 2:
                a[j-1] = a[j]
            else:
                a[j] = a[j+1]
            shifts += 1
            j -= 1
        a[j+1]=k
    return a,shifts
for option in range(1,4):
    for seq in ([2,1],[2,4,1],[1,4,2]):
        print("p10 distractor",option,seq,insertion(seq,option)[0])
for n in range(6):
    for seq in product((0,1,2),repeat=n):
        ordered, shifts = insertion(seq,4)
        assert ordered == sorted(seq) and shifts == sum(x>y for x,y in combinations(seq,2))
print("p10 option 4: exhaustive sequences of lengths 0..5 with keys 0,1,2")
for seq in ([1,3,2,4],[4,3,2,1]):
    print("p11 shifts",seq,insertion(seq,4)[1])


