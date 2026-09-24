"""2017-final-kdh 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
import heapq, os, subprocess, tempfile

SRC = "2017-final-kdh"


def run_c(code, stdin=""):
    with tempfile.TemporaryDirectory() as d:
        c, exe = os.path.join(d, "a.c"), os.path.join(d, "a.out")
        open(c, "w").write(code)
        subprocess.run(["cc", "-std=c11", "-Wall", "-o", exe, c], check=True, capture_output=True)
        return subprocess.run([exe], input=stdin, capture_output=True, text=True, check=True).stdout


def heap_push(h, x):  # h[0] 비움, 1부터
    h.append(x); i = len(h) - 1
    while i > 1 and h[i // 2] < h[i]: h[i // 2], h[i] = h[i], h[i // 2]; i //= 2


def heap_pop(h):
    top, last = h[1], h.pop()
    if len(h) > 1:
        h[1] = last; i = 1
        while 2 * i < len(h):
            c = 2 * i
            if c + 1 < len(h) and h[c + 1] > h[c]: c += 1
            if h[i] >= h[c]: break
            h[i], h[c] = h[c], h[i]; i = c
    return top


def q1():
    h = [None]
    for x in (16, 28, 41, 20, 25): heap_push(h, x)
    a = h[1:]
    heap_push(h, 30); b = h[1:]
    heap_pop(h); c = h[1:]
    d = ", ".join(f"[{i}]={v}" for i, v in enumerate(h) if i)
    return f"(a) {a} (b) {b} (c) {c} (d) [0] 비움, {d}"


def q2():  # 교재(천인국) partition: 피벗=맨 왼쪽, low/high 교환, 마지막에 피벗과 high 교환
    a, rows = [25, 3, 50, 72, 9, 46, 15], []
    def part(l, r):
        p, low, high = a[l], l, r + 1
        while True:
            low += 1
            while low <= r and a[low] < p: low += 1
            high -= 1
            while high >= l and a[high] > p: high -= 1
            if low < high: a[low], a[high] = a[high], a[low]; rows.append(list(a))
            else: break
        if l != high: a[l], a[high] = a[high], a[l]; rows.append(list(a))
        return high
    def qs(l, r):
        if l < r: q = part(l, r); qs(l, q - 1); qs(q + 1, r)
    rows.append(list(a)); qs(0, 6)
    return "\n".join(" | ".join(map(str, r)) for r in rows)


def q3():
    adj = {0: [1, 5], 1: [0, 5, 2], 2: [1, 3], 3: [2, 4, 5], 4: [3, 5], 5: [0, 1, 3, 4]}
    seen, q, order = {0}, [0], []
    while q:
        v = q.pop(0); order.append(v)
        for w in adj[v]:
            if w not in seen: seen.add(w); q.append(w)
    return "노드 방문순서 : " + ", ".join(map(str, order))


INF = float("inf")
V4 = "ABCDEF"
M4 = [[0, 4, INF, INF, INF, 9], [4, 0, 8, INF, INF, 11], [INF, 8, 0, 2, INF, INF],
      [INF, INF, 2, 0, 6, 7], [INF, INF, INF, 6, 0, 1], [9, 11, INF, 7, 1, 0]]


def q4():
    edges = [f"{V4[i]}-{V4[j]} {M4[i][j]}" for i in range(6) for j in range(i + 1, 6) if M4[i][j] < INF]
    s = V4.index("C"); inT, Vs, Es = {s}, [V4[s]], []
    while len(inT) < 6:
        w, i, j = min((M4[i][j], i, j) for i in inT for j in range(6) if j not in inT)
        inT.add(j); Vs.append(V4[j]); Es.append(f"({V4[i]}, {V4[j]})")
    dist, S = M4[0][:], [0]
    while len(S) < 6:
        u = min((dist[v], v) for v in range(6) if v not in S)[1]; S.append(u)
        for v in range(6): dist[v] = min(dist[v], dist[u] + M4[u][v])
    return (f"(a) 간선: {', '.join(edges)}\n(b) V ={{ {', '.join(Vs)} }} E ={{ {', '.join(Es)} }}\n"
            f"(c) S ={{ {', '.join(V4[v] for v in S)} }} distance: " + ", ".join(f"{V4[v]}={dist[v]}" for v in range(6)))


def q5():
    t, coll = [None] * 11, 0
    for k in (66, 158, 8, 72, 22, 24, 130, 35):
        i = k % 11
        if t[i] is not None: coll += 1  # 충돌 = 홈 버킷이 차 있던 삽입 수
        while t[i] is not None: i = (i + 1) % 11
        t[i] = k
    return " | ".join(f"{i}:{'' if v is None else v}" for i, v in enumerate(t)) + f"\n충돌횟수: {coll}"


def bst(keys):
    t = None
    def ins(t, k):
        if t is None: return [k, None, None]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        return t
    for k in keys: t = ins(t, k)
    return t


def avl(keys):
    h = lambda t: t[3] if t else 0
    def fix(t): t[3] = 1 + max(h(t[1]), h(t[2])); return t
    def rr(t): l = t[1]; t[1] = l[2]; l[2] = fix(t); return fix(l)
    def rl(t): r = t[2]; t[2] = r[1]; r[1] = fix(t); return fix(r)
    def ins(t, k):
        if t is None: return [k, None, None, 1]
        if k < t[0]: t[1] = ins(t[1], k)
        else: t[2] = ins(t[2], k)
        fix(t); b = h(t[1]) - h(t[2])
        if b > 1:
            if k > t[1][0]: t[1] = rl(t[1])
            return rr(t)
        if b < -1:
            if k < t[2][0]: t[2] = rr(t[2])
            return rl(t)
        return t
    t = None
    for k in keys: t = ins(t, k)
    return t


def level(t):
    out, q = [], [t]
    while q:
        n = q.pop(0)
        if n: out.append(n[0]); q += [n[1], n[2]]
    return out


def path(t, k):
    p = []
    while t:
        p.append(t[0])
        if t[0] == k: break
        t = t[1] if k < t[0] else t[2]
    return p


def q6():
    keys = (55, 3, 7, 72, 9, 16)
    a, b = bst(keys), avl(keys)
    j = lambda xs: ", ".join(map(str, xs))
    return f"(a) 레벨 순서 {j(level(a))}, 방문 {j(path(a, 16))} (b) 레벨 순서 {j(level(b))}, 방문 {j(path(b, 16))}"


# 7: 모범답안 코드와 BFS 정답 코드를 같은 그래프로 돌려 비교한다
KEY7 = r'''
char connected_graph( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {
	int j, node, level_num=0, level_nodes_count=1, sum = 0;
	int level[MAX_SIZE][MAX_SIZE] = { 0 };
	int visited[MAX_SIZE] = { 0 };
	level[level_num][0] = 1;
	visited[0] = 1;
	while (level_nodes_count > 0){
		for (node = 0; node < MAX_SIZE; node++){
			if ( level[level_num][node] == 1 ){
				level_nodes_count = 0;
				for (j = 0; j < MAX_SIZE; j++)
				if ( adj_matrix[node][j] && !visited[j] ) {
					level[level_num + 1][j] = 1;
					level_nodes_count++;
					visited[j] = 1;
				}
			}
		}
		level_num++;
	}
	for (j = 0; j < MAX_SIZE; j++) sum += visited[j];
	if (sum == MAX_SIZE) return 'y';
	else                 return 'n';
}
'''
FIX7 = r'''
char connected_graph( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {
	int queue[MAX_SIZE], visited[MAX_SIZE] = { 0 };
	int front = 0, rear = 0, v, j, count = 0;
	queue[rear++] = 0;
	visited[0] = 1;
	while (front < rear) {
		v = queue[front++];
		count++;
		for (j = 0; j < MAX_SIZE; j++)
			if (adj_matrix[v][j] && !visited[j]) {
				visited[j] = 1;
				queue[rear++] = j;
			}
	}
	return (count == MAX_SIZE) ? 'y' : 'n';
}
'''


def graphs7():
    def m(edges):
        a = [[0] * 6 for _ in range(6)]
        for u, v in edges: a[u][v] = a[v][u] = 1
        return a
    return {"경로 0-1-2-3-4-5": (m([(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]), "y"),
            "0,1,2,5 / 3,4 분리": (m([(0, 1), (1, 2), (2, 5), (0, 5), (3, 4)]), "n"),
            "0-1,0-2,1-3,3-4,4-5 (2는 막다른 노드)": (m([(0, 1), (0, 2), (1, 3), (3, 4), (4, 5)]), "y")}


def run7(body):
    res = {}
    for name, (a, _) in graphs7().items():
        init = "{" + ",".join("{" + ",".join(map(str, r)) + "}" for r in a) + "}"
        code = f"#include <stdio.h>\n#define MAX_SIZE 6\n{body}\nint main(){{ int adj_matrix[MAX_SIZE][MAX_SIZE] = {init}; printf(\"%c\", connected_graph(adj_matrix)); return 0; }}\n"
        res[name] = run_c(code)
    return res


def q7():
    want = {k: v for k, (_, v) in graphs7().items()}
    key, fix = run7(KEY7), run7(FIX7)
    assert fix == want, fix
    if key == want:
        return "모범답안 코드가 모든 시험 그래프에서 맞음"
    bad = ", ".join(f"{k}: 모범답안 {key[k]} / 정답 {want[k]}" for k in want if key[k] != want[k])
    return ("모범답안 코드는 level_nodes_count를 노드마다 0으로 되돌려, 한 레벨의 마지막 노드가 새 이웃이 없으면 탐색을 멈춘다"
            f"({bad}). 큐 BFS로 고친 답:\n```c{FIX7}```")


# 8: 5번째로 큰 소수. 모범답안 코드와 정답 코드를 고정 배열로 비교한다
HEAD8 = "#include <stdio.h>\n#define MAX_SIZE 100\nint main() {\nint i;\nint list[MAX_SIZE];\nfor (i = 0; i<MAX_SIZE; i++) list[i] = (i * 7919 + 13) % 10000 + 1;\n"
KEY8 = r'''
int j, most, temp, prime_flag, prime_count=0;
for (i = 0; i < MAX_SIZE - 1; i++) {
	most = i;
	for (j = i + 1; j<MAX_SIZE; j++) if (list[j] > list[most]) most = j;
	temp = list[i]; list[i] = list[most]; list[most] = temp;
}
for (i = 0; i < MAX_SIZE; i++){
	prime_flag = 1;
	for (j = 2; j < list[i]; j++) if (list[i] % j == 0) prime_flag = 0;
	if (prime_flag == 1) prime_count++;
	if (prime_count == 1) { printf("%d", list[i]); break; }
}
return 0; }
'''
FIX8 = r'''
int j, most, temp, prime_flag, prime_count = 0;
// 내림차순으로 정렬
for (i = 0; i < MAX_SIZE - 1; i++) {
	most = i;
	for (j = i + 1; j < MAX_SIZE; j++)
		if (list[j] > list[most]) most = j;
	temp = list[i]; list[i] = list[most]; list[most] = temp;
}
// 큰 수부터 소수를 세어 5번째에서 출력
for (i = 0; i < MAX_SIZE; i++) {
	prime_flag = (list[i] >= 2);
	for (j = 2; j * j <= list[i]; j++)
		if (list[i] % j == 0) { prime_flag = 0; break; }
	if (prime_flag) prime_count++;
	if (prime_count == 5) { printf("5번째 큰 소수:%d ", list[i]); break; }
}
return 0; }
'''


def q8():
    lst = [(i * 7919 + 13) % 10000 + 1 for i in range(100)]
    isp = lambda n: n >= 2 and all(n % d for d in range(2, int(n ** .5) + 1))
    want = sorted((x for x in lst if isp(x)), reverse=True)[4]
    key, fix = run_c(HEAD8 + KEY8), run_c(HEAD8 + FIX8)
    assert fix == f"5번째 큰 소수:{want} ", fix
    if key == str(want):
        return "모범답안 코드가 맞음"
    return (f"모범답안 코드는 prime_count == 1 에서 멈춰 가장 큰 소수({key})를 출력한다(5번째는 {want}). "
            "또 1을 소수로 센다. 고친 답(int list[MAX_SIZE]; 다음 선언, rand 채우기 for문 다음·return 0; 앞 본문):\n```c" + FIX8.replace("return 0; }\n", "") + "```")


if __name__ == "__main__":
    for i in range(1, 9):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
