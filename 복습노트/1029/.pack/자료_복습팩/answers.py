"""1029 복습팩 정답 재계산 (저장소를 바꾸지 않는다)."""

def tree_stats(children, root):
    level = {root: 1}
    order = [root]
    for n in order:
        for c in children.get(n, []):
            level[c] = level[n] + 1
            order.append(c)
    parent = {c: p for p, cs in children.items() for c in cs}
    def desc(n):
        out = []
        for c in children.get(n, []):
            out += [c] + desc(c)
        return out
    return level, parent, desc

# 2017-mid-c050-q8: 일반 트리
T8 = {'v0': ['v1', 'v2', 'v3'], 'v1': ['v4'], 'v2': ['v5', 'v6'], 'v3': ['v7', 'v8', 'v9'],
      'v4': ['v10', 'v11'], 'v5': ['v12', 'v13'], 'v6': ['v14', 'v15'], 'v8': ['v16', 'v17'], 'v16': ['v18']}
lv, par, desc = tree_stats(T8, 'v0')
a = [n for n in lv if lv[n] == 3]
b = [c for c in T8[par['v8']] if c != 'v8']
c = desc('v8')
d = max(lv.values())
e = len(T8.get('v8', []))
ans = {}
ans['2017-mid-c050-q8'] = f"(a) {', '.join(a)} (b) {', '.join(b)} (c) {', '.join(sorted(c, key=lambda x: int(x[1:])))} (d) {d} (e) {e}"

# textbook ch08-q04: 단말 노드 수 (SVG 간선: A-B, A-C, B-D, C-E, C-F, E-G, E-H)
T4 = {'A': ['B', 'C'], 'B': ['D'], 'C': ['E', 'F'], 'E': ['G', 'H']}
nodes4 = set(T4) | {x for cs in T4.values() for x in cs}
leaves4 = sorted(n for n in nodes4 if n not in T4)
ans['textbook-ch08-q04'] = f"③ 4 ({', '.join(leaves4)})"
assert len(leaves4) == 4

# textbook ch08-q05: 트리의 차수 = 노드 차수의 최댓값 (SVG: A-B, A-C, B-D, B-E, B-F, C-G, D-H)
T5 = {'A': ['B', 'C'], 'B': ['D', 'E', 'F'], 'C': ['G'], 'D': ['H']}
deg5 = max(len(v) for v in T5.values())
assert deg5 == 3
ans['textbook-ch08-q05'] = "① 3"

# textbook ch08-q07: 높이 h 이진트리 최대 노드 2^h - 1
h = 5
assert 2 ** h - 1 == 31
ans['textbook-ch08-q07'] = "(4) 31개"

# 2019-mid-q5: 높이 K, 노드 2^K-1 개 → 포화이진트리이므로 완전이진트리이기도 하다 → 진술은 거짓
for K in range(1, 8):
    full_nodes = sum(2 ** (l - 1) for l in range(1, K + 1))
    assert full_nodes == 2 ** K - 1  # 모든 레벨이 꽉 참 = 포화 → 완전 조건도 만족
ans['2019-mid-q5'] = "X"

ans['2018-mid-c102-q4'] = "높이"
ans['2017-mid-c050-q3'] = "트리"
ans['2017-mid-c050-q4'] = "완전이진트리"


# lecture-s07-p5-binary-tree-bounds: 노드 12개, 높이 4
import math
n = 12
edges = n - 1
h_max = n
h_min = math.ceil(math.log2(n + 1))
assert 2 ** (h_min - 1) - 1 < n <= 2 ** h_min - 1
h = 4
ans['lecture-s07-p5-binary-tree-bounds'] = f"(a) {edges} (b) 최대 {h_max}, 최소 {h_min} (c) 최소 {h}, 최대 {2**h - 1}"

# lecture-s07-p7-complete-binary-tree: A~J 를 레벨 순서(같은 레벨은 왼쪽부터)로 채운 트리
labels = 'ABCDEFGHIJ'
def place(k):  # k번째(1부터) 노드의 부모와 방향을 레벨 순서 채우기로 구한다
    slots = []
    for i, p in enumerate(labels, start=1):
        slots += [(p, '왼쪽'), (p, '오른쪽')]
    return slots[k - 2]
height = len(labels).bit_length()
is_full = len(labels) == 2 ** height - 1
assert (height, is_full) == (4, False)
parent, side = place(11)
assert (parent, side) == ('E', '오른쪽')
ans['lecture-s07-p7-complete-binary-tree'] = "(a) 완전 이진 트리(포화 이진 트리는 아님) (b) E의 오른쪽 자식 (c) 이진 트리는 맞지만 완전 이진 트리는 아님 → 기타 이진 트리"

if __name__ == '__main__':
    for k, v in ans.items():
        print(k, '=>', v)
