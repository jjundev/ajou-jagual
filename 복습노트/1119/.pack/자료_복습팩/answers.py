"""1119 복습팩 정답 재계산 (저장소를 바꾸지 않는다).

DFS는 강의 S10 p14 dfs_mat 그대로(작은 번호부터 재귀), BFS는 S10 p16 bfs_mat 그대로(큐).
C 코드 문항은 work/ 에서 cc -std=c11 -Wall 로 컴파일·실행한다.
"""
from collections import deque
from itertools import combinations
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "work")


def adj_from_edges(n, edges):
    a = [[0] * n for _ in range(n)]
    for u, v in edges:
        a[u][v] = a[v][u] = 1
    return a


def dfs(a, s):
    seen, order, tree = set(), [], []

    def go(v):
        seen.add(v)
        order.append(v)
        for w in range(len(a)):
            if a[v][w] and w not in seen:
                tree.append((v, w))
                go(w)

    go(s)
    return order, tree


def bfs(a, s):
    seen, order, tree = {s}, [s], []
    q = deque([s])
    while q:
        v = q.popleft()
        for w in range(len(a)):
            if a[v][w] and w not in seen:
                seen.add(w)
                order.append(w)
                tree.append((v, w))
                q.append(w)
    return order, tree


def bfs_list(lists, s):
    seen, order, q = {s}, [s], deque([s])
    while q:
        v = q.popleft()
        for w in lists[v]:
            if w not in seen:
                seen.add(w)
                order.append(w)
                q.append(w)
    return order


def connected(a):
    return len(dfs(a, 0)[0]) == len(a)


def fmt(order):
    return ", ".join(map(str, order))


def fmt_tree(tree):
    return ", ".join(f"{u}-{v}" for u, v in tree)


def run_c(name):
    src = os.path.join(WORK, name + ".c")
    exe = os.path.join(WORK, name)
    subprocess.run(["cc", "-std=c11", "-Wall", "-o", exe, src], check=True)
    return subprocess.run([exe], check=True, capture_output=True, text=True).stdout


R = {}

# p1 2016-final-ljw-q6
g16 = adj_from_edges(8, [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6), (3, 7), (4, 7), (5, 7), (6, 7)])
d, dt = dfs(g16, 0)
b, bt = bfs(g16, 0)
R["p1"] = f"DFS(0) 방문 순서 {fmt(d)} / 트리 간선 {fmt_tree(dt)} | BFS(0) 방문 순서 {fmt(b)} / 트리 간선 {fmt_tree(bt)}"

# p2 2015-ljw-q6
g15 = adj_from_edges(8, [(0, 2), (0, 5), (0, 7), (1, 7), (2, 6), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7)])
d, dt = dfs(g15, 0)
b, bt = bfs(g15, 0)
R["p2"] = f"DFS(0) 방문 순서 {fmt(d)} / 트리 간선 {fmt_tree(dt)} | BFS(0) 방문 순서 {fmt(b)} / 트리 간선 {fmt_tree(bt)}"

# p3 2017-final-kdh-q3 (인접 리스트 순서 그대로)
lists = {0: [1, 5], 1: [0, 5, 2], 2: [1, 3], 3: [2, 4, 5], 4: [3, 5], 5: [0, 1, 3, 4]}
R["p3"] = "노드 방문순서 : " + fmt(bfs_list(lists, 0))

# p4 2017-final-kdh-q7: C11로 연결/비연결 행렬 시험
p4_out = run_c("p4_connected")
R["p4"] = "큐 BFS(또는 DFS)로 0에서 도달한 정점 수가 MAX_SIZE이면 'y', 아니면 'n' | 실행: " + p4_out.strip().replace("\n", " / ")

# p5 2019-final-q1
R["p5"] = "가중치 그래프"

# p6 textbook-ch10-q05
R["p6"] = "② 너비 우선 탐색"

# p7 textbook-ch10-q13 (그림: 0-1,1-2,1-3,2-4,3-4,3-5,5-6,5-7,6-7,7-8,7-9)
E13 = [(0, 1), (1, 2), (1, 3), (2, 4), (3, 4), (3, 5), (5, 6), (5, 7), (6, 7), (7, 8), (7, 9)]
g13 = adj_from_edges(10, E13)
R["p7"] = (f"1) DFS(3): {fmt(dfs(g13, 3)[0])} 2) DFS(6): {fmt(dfs(g13, 6)[0])} "
           f"3) BFS(3): {fmt(bfs(g13, 3)[0])} 4) BFS(6): {fmt(bfs(g13, 6)[0])}")

# p8 textbook-ch10-q14: 같은 그림에서 간선 하나씩 지우고 연결 여부 검사
bridges = []
for u, v in E13:
    a = adj_from_edges(10, [e for e in E13 if e != (u, v)])
    if not connected(a):
        bridges.append((u, v))
p8_out = run_c("p8_bridge")
R["p8"] = "브리지 " + ", ".join(f"({u}, {v})" for u, v in bridges) + " | C 실행: " + p8_out.strip()

# p9 textbook-ch11-q01: 정사각형(4정점 사이클) 신장 트리 = 간선 4개 중 3개 고르기, 사이클 없는 것
sq = [(0, 1), (1, 2), (2, 3), (3, 0)]
trees = []
for pick in combinations(sq, 3):
    if connected(adj_from_edges(4, pick)):
        trees.append(pick)
R["p9"] = f"{len(trees)}개 (네 간선 중 하나씩 빼낸 경로 모양)"

# p10 lecture-s10-p17 연결 성분: visited[v]=count 로 바꾼 dfs_mat
E_cc = [(0, 2), (0, 5), (1, 3), (2, 5), (3, 6), (4, 6)]
gcc = adj_from_edges(8, E_cc)
visited = [0] * 8
count = 0
printed = []


def dfs_count(v):
    visited[v] = count
    printed.append(v)
    for w in range(8):
        if gcc[v][w] and not visited[w]:
            dfs_count(w)


for i in range(8):
    if not visited[i]:
        count += 1
        dfs_count(i)
p10_out = run_c("p10_component")
assert p10_out.split("\n")[0].strip() == " ".join(map(str, printed)), p10_out
R["p10"] = f"(a) 출력 {' '.join(map(str, printed))} (b) visited = [{', '.join(map(str, visited))}] (c) count = {count}"

if __name__ == "__main__":
    for k, v in R.items():
        print(k, "=>", v)
