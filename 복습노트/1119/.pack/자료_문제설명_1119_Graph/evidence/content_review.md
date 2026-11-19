# content review — 1119 Graph 문제설명 (p1–p10)

Reviewer: content-review subagent (read-only on fragments)
Inputs read: authoring.md, verification.md, source.json, explanations/p1–p10.html, 정리노트_1119_Graph.html, evidence/author/p4_original_answer.c + outputs, evidence/author/p8_*_output.txt, 복습노트/1119/.pack/자료_복습팩/problems.md (p4 original model answer + grading note).

## Independent recomputation (own script, adjacency sorted ascending / given list order)
- p1 DFS(0) 0,1,3,7,4,5,2,6 edges 0-1,1-3,3-7,7-4,7-5,5-2,2-6; BFS(0) 0..7 edges 0-1,0-2,1-3,1-4,2-5,2-6,3-7 — matches fragment, figures' accent/dashed edges match.
- p2 DFS(0) 0,2,6,4,3,5,7,1 / BFS(0) 0,2,5,7,6,3,4,1 with stated tree edges — matches; figure edges match; original-figure positions (5 directly below 0, 1/7 middle row) match understand/pitfall claims.
- p3 BFS (list order) 0,1,5,2,3,4 — matches. Real DFS with the same lists = 0,1,5,3,2,4.
- p4 queue BFS code correct; trace for 0-1,0-2,1-3,3-4,4-5 → y; original model answer returns n on it (evidence output confirms); grading example {0,1,2,5}/{3,4} from original 채점 기준 confirmed.
- p7 edges from SVG: 0-1,1-2,1-3,2-4,3-4,3-5,5-6,5-7,6-7,7-8,7-9. DFS(3), DFS(6), BFS(3), BFS(6) all match; layer sets match.
- p8 bridges (0,1),(3,5),(7,8),(7,9); no-reset variant prints only (0,1); deg(3)=deg(5)=3; adding (0,2) → 3 bridges.
- p9 square A(TL)B(TR)C(BR)D(BL) matches SVG; 4 spanning trees.
- p10 output 0 2 5 1 3 6 4 7, visited [1,2,1,2,2,1,2,3], count 3; pitfall alt array [1,4,2,5,7,3,6,8] correct; lecture example (0,1),(0,2),(3,4) count=2 confirmed in note.
- Anchors used (s0-dfs-trace, s0-dfs-not-done, s0-dfs-code, s1-bfs-trace, s1-bfs-code, s1-compare, s2-components, s3-spanning, s3-mst, s3-greedy) all exist exactly once in 정리노트_1119_Graph.html.
- Structure: all 10 fragments have 7 sections in order + one `sum`; subpart markers in solve and verify: main / 1–4 / a–c correct. No evidence/*.py exposure, no meta declarations.
- Scope: no Kruskal/Prim/Dijkstra/union-find/topological sort teaching. p6 ③ has a one-sentence 보충-marked note on shortest path; ④ only uses the greedy concept from class. OK.
- Lecture-quote claims (p6 "재귀가 스택을 알아서", "BFS 큐는 직접 설계"; p5 MST 용도 4종, 네트워크 용어; p10 "바뀐 한 줄" visited[v]=count) verified in the note.

## Per item
| item | result | reason |
|---|---|---|
| p1:main | pass | traces, figures, verify (count, cycle, BFS depth) all correct |
| p2:main | pass | traces/figures correct; 20-degree check, parent cross-check valid |
| p3:main | **fail** | pitfall 1 states a wrong "DFS" result (0, 1, 2, 3, …); actual DFS with these lists is 0, 1, 5, 3, 2, 4 |
| p4:main | pass | correct code + trace; original-answer defect annotated consistently in understand/verify/pitfall/sum |
| p5:main | pass | correct, in scope |
| p6:main | pass | every option eliminated; out-of-scope items marked |
| p7:1 | pass | DFS(3) correct |
| p7:2 | pass | DFS(6) correct |
| p7:3 | pass | BFS(3) correct |
| p7:4 | **fail** (pitfall, shared) | pitfall 2 has no wrong result: sorting each BFS layer reproduces the correct answer in every layer here, so the "counterexample" is not one |
| p8:main | pass | code, table, no-reset counterexample all verified |
| p9:main | pass | correct and complete |
| p10:a | pass (advisory) | correct; verify (a) leans on a compile/run note |
| p10:b | pass | edge-endpoint label check is a real cross-check |
| p10:c | pass | correct |

## Required fixes
1. explanations/p3.html, pitfall item 1
   - Quote: `<li><strong>DFS처럼 1에서 바로 2로 내려가면</strong>: 0, 1, 2, 3, …처럼 깊이 순서가 나와요. BFS는 0의 이웃 1, 5를 먼저 다 방문해야 해서 5가 2보다 앞서요.</li>`
   - Problem: with the given list order, DFS from 1 goes to 5 (list 1: 0 → 5 → 2), not 2. The stated wrong output is not what a DFS-confused student gets.
   - Replace with: `<li><strong>DFS처럼 이웃으로 바로 내려가면</strong>: 리스트 순서대로 깊이 들어가 0, 1, 5, 3, 2, 4가 나와요. BFS는 거리 1층(1, 5)을 다 꺼낸 뒤 1의 리스트에서 2를 먼저 표시하니 2가 3보다 앞선 0, 1, 5, 2, 3, 4예요.</li>`
2. explanations/p7.html, pitfall item 2
   - Quote: `<li><strong>BFS(6)에서 층마다 번호순 정렬을 하면</strong>: 2층을 3, 8, 9로 우연히 맞힐 수 있지만 원리는 ‘꺼낸 순서’예요. …</li>`
   - Problem: no concrete wrong result — sorting every layer gives exactly the correct BFS(3)/BFS(6) answers, violating "오해 이유 → 실제 반례/틀린 결과".
   - Replace with: `<li><strong>BFS(6)에서 6과 바로 붙은 7 쪽을 먼저 펼치면</strong>: 6, 5, 7, 8, 9, 3, …처럼 8, 9가 3보다 앞서요. 큐는 [5, 7]이라 5를 먼저 꺼내 3을 넣고, 그다음 7을 꺼내 8, 9를 넣으니 2층 순서는 3, 8, 9예요.</li>`
   - (Alternatively keep the sorting idea but cite a real failure: p2 BFS(0) 2층 is 6, 3, 4; sorting gives 3, 4, 6, which is wrong.)

## Advisory (not blocking)
- p4/p8/p10 verify mention `cc -std=c11 -Wall로 실행하면 …`. Not an evidence file name, but p10 verify (a) relies mainly on it ("실행 검산(같은 두 함수 + 선언·main을 붙여 …)의 출력도 같아요"). Consider replacing with a student-checkable check, e.g. "출력을 count가 바뀌는 곳에서 끊으면 0 2 5 | 1 3 6 4 | 7이고, 각 묶음의 정점이 (b)에서 같은 번호를 받아요."
