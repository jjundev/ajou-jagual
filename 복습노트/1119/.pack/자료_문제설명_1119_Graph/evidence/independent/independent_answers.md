# Independent answers (Graph review pack, problems p1-p10)

Solved without reading any answer/explanation files. Edges were extracted programmatically from the SVG
(`<line>` endpoints snapped to nearest `<circle>` center, labels from nearest `<text>`); for p1/p2 the
extracted edges match the aria-label/figcaption exactly. No segment passes through a non-endpoint circle.
Conventions: adjacency-matrix DFS scans w = 0..n-1 (smaller first); BFS marks visited at enqueue.

## p1  (exact)
Edges: 0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7, 4-7, 5-7, 6-7
- DFS(0) order 0 1 3 7 4 5 2 6; tree edges (discovery order) 0-1, 1-3, 3-7, 7-4, 7-5, 5-2, 2-6
  -> set {0-1, 1-3, 3-7, 4-7, 5-7, 2-5, 2-6}; non-tree: 0-2, 1-4, 6-7
- BFS(0) order 0 1 2 3 4 5 6 7; tree edges {0-1, 0-2, 1-3, 1-4, 2-5, 2-6, 3-7}; non-tree: 4-7, 5-7, 6-7
Ambiguity: none (smaller-number-first fixes everything).

## p2  (exact)
Edges: 0-2, 0-5, 0-7, 1-7, 2-6, 3-4, 3-5, 4-5, 4-6, 4-7
- DFS(0) order 0 2 6 4 3 5 7 1; tree edges (discovery) 0-2, 2-6, 6-4, 4-3, 3-5, 4-7, 7-1
  -> set {0-2, 2-6, 4-6, 3-4, 3-5, 4-7, 1-7}; non-tree: 0-5, 0-7, 4-5
- BFS(0) order 0 2 5 7 6 3 4 1; tree edges {0-2, 0-5, 0-7, 2-6, 3-5, 4-5, 1-7}; non-tree: 3-4, 4-6, 4-7
Notes: in BFS, 4 is reached from 5 (5 dequeued before 6 and 7), so tree edge is 5-4, not 6-4 or 7-4.
1 is reached from 7. Ambiguity: wording "지그재그 선으로 진하게" is odd but does not affect the answer;
figure layout (positions 0,2,1,7,6,3,5,4) does not match numeric order, so read labels carefully.

## p3  (exact)
Adjacency list is symmetric (checked). Header node of each list is the vertex itself.
BFS(0) visit order: **0 1 5 2 3 4** (tree: 0-1, 0-5, 1-2, 5-3, 5-4).
Ambiguity: none; ascending-order BFS gives the same order.

## p4  (exact; own implementation tested)
BFS (or DFS) from vertex 0 over the 6x6 matrix, count visited vertices; return 'y' iff count == MAX_SIZE,
else 'n'. See connected_graph.c; 8 tests (path, K6, two triangles, dead-end at end of BFS level
0-1,0-2,1-3,3-4,4-5, isolated vertex 5, isolated vertex 0, no edges, star) all pass, compiled with
-std=c11 -Wall -Wextra with zero warnings.
Pitfalls to check in other solutions: stopping early when a dequeued vertex has no new neighbor
(dead-end case 2 must not cause 'n'); checking only row sums/degrees (degree>0 for all vertices does not
imply connected, e.g. two triangles); forgetting the start vertex in the count; queue overflow.

## p5  (qualitative / terminology)
**가중치 그래프 (weighted graph)**; also called **네트워크 (network)** in the textbook. Either should be accepted.

## p6  (qualitative)
Answer **(2) 너비 우선 탐색 (BFS)**.
- (1) DFS: uses a stack (or recursion = call stack), not a queue.
- (2) BFS: uses a FIFO queue — the defining data structure.
- (3) 최단 거리 (Dijkstra/Floyd): Dijkstra in the textbook uses a distance array + repeated min selection
  (or a priority queue in heap-based versions); Floyd uses a 2-D matrix. Not a (FIFO) queue.
- (4) MST (Kruskal/Prim): Kruskal uses edge sorting + union-find; Prim uses min selection/priority queue.
Ambiguity: if "큐" includes priority queue, (3)/(4) could be argued; standard intended answer is (2).

## p7  (exact; adjacency matrix -> ascending neighbor order)
Edges: 0-1, 1-2, 1-3, 2-4, 3-4, 3-5, 5-6, 5-7, 6-7, 7-8, 7-9
1. DFS(3): **3 1 0 2 4 5 6 7 8 9**
2. DFS(6): **6 5 3 1 0 2 4 7 8 9**
3. BFS(3): **3 1 4 5 0 2 6 7 8 9**
4. BFS(6): **6 5 7 3 8 9 1 4 0 2**
Ambiguity: none once matrix order is assumed (figure labels 6 bottom, 7 middle, 8 top in the right column).

## p8  (exact for this graph; function is open-ended)
Same graph as p7. Bridges (brute force: remove each edge, test connectivity):
**(0,1), (3,5), (7,8), (7,9)**. Non-bridges: 1-2, 1-3, 2-4, 3-4 (cycle 1-2-4-3) and 5-6, 5-7, 6-7 (triangle).
Function: for each edge (u,v): set adj[u][v]=adj[v][u]=0, run DFS/BFS from u, if v (or any vertex)
unvisited then it's a bridge, restore edge. O(E(V+E)) or O(E*V^2) with matrix; Tarjan low-link O(V+E)
is the efficient alternative.
Ambiguity: problem asks for a function (code), so grading is qualitative; the bridge set is exact.

## p9  (exact, counting; vertices unlabeled)
Square C4 (4 vertices, 4 edges). Spanning trees = remove exactly one of the 4 sides -> **4 spanning trees**
(each is a path of 3 edges). With TL=A, TR=B, BR=C, BL=D: {AB,BC,CD}, {BC,CD,DA}, {CD,DA,AB}, {DA,AB,BC}.
Ambiguity: figure has no labels, so the answer must be drawn/described; count 4 is unambiguous
(no diagonals in the figure).

## p10  (exact; simulated in Python and in C with the code verbatim)
(a) printed: **0 2 5 1 3 6 4 7**
(b) visited[0..7] = **1 2 1 2 2 1 2 3**
(c) count = **3** = number of connected components ({0,2,5}, {1,3,4,6}, {7}); visited[v] holds the
    component number of v.
Notes: inside component 2, DFS goes 1 -> 3 -> 6 -> 4 (4 reached via 6), so print order is 1 3 6 4.
No UB: visited/count are globals (zero-init); count is set to 0 then incremented before the first
dfs_mat, so visited values are >=1 and act as both "visited" flag and component id.
