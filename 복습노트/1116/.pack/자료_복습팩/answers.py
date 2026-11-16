"""1116 복습팩 정답 재계산 (저장소를 바꾸지 않는다).

- 그래프는 정점 번호/이름 -> 인접 정점 목록(dict)으로 두고, 인접 행렬은 2차원 리스트로 만든다(S10 p9).
- 인접 리스트는 강의록 S10 p10처럼 정점 번호 오름차순으로 노드를 잇는다(교과서 문항은 순서를 정하지 않는다).
- 차수 = 그 정점에 연결된 간선 수(S10 p7). 오일러: 모든 정점 차수가 짝수여야 한 번씩 건너 제자리 복귀(S10 p3).
- C 코드 문제는 work/ 아래에서 cc -std=c11 -Wall 로 컴파일·실행한다.
"""
import itertools, os, subprocess, tempfile, pathlib

HERE = pathlib.Path(__file__).resolve().parent


def matrix(n, edges, directed=False):
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] = 1
        if not directed:
            M[b][a] = 1
    return M


def adj_list(M):
    return {i: [j for j, x in enumerate(row) if x] for i, row in enumerate(M)}


def fmt_list(L, names=None):
    nm = (lambda i: names[i]) if names else str
    return '; '.join(f"{nm(v)} → " + (' → '.join(nm(u) for u in L[v]) + ' → NULL' if L[v] else 'NULL') for v in L)


def fmt_mat(M):
    return ' / '.join(' '.join(map(str, r)) for r in M)


# ---------- 2019-final-q2: 사이클 정의 ----------
def q_2019_q2():
    # 단순 경로의 시작=끝 -> 사이클(S10 p7: 사이클 0,1,2,0)
    return '사이클'


# ---------- 2019-final-q5: 10정점 무방향 완전 그래프 간선 수 ----------
def q_2019_q5():
    n = 10
    e = sum(1 for _ in itertools.combinations(range(n), 2))
    assert e == n * (n - 1) // 2
    return f'{e} (10 × 9 / 2, 공식 n(n-1)/2)'


# ---------- 2017-final2-q8: check_cycle (C11 실행) ----------
C_CHECK = r'''
#include <stdio.h>
#include <string.h>
char check_cycle(int adj_matrix[6][6], char *path) {
    int len, i, s, e;
    int used_edge[6][6] = { 0 };
    int seen[6] = { 0 };
    len = (int)strlen(path);
    if (len < 4 || path[0] != path[len - 1]) return 'n';
    for (i = 0; i < len - 1; i++) {
        s = path[i] - '0';
        e = path[i + 1] - '0';
        if (adj_matrix[s][e] != 1) return 'n';
        if (used_edge[s][e]) return 'n';
        used_edge[s][e] = used_edge[e][s] = 1;
        if (seen[s]) return 'n';
        seen[s] = 1;
    }
    return 'y';
}
int main(void) {
    int adj_matrix[6][6] = {
    { 0, 0, 1, 0, 1, 0 },
    { 0, 0, 1, 0, 0, 0 },
    { 1, 1, 0, 1, 1, 0 },
    { 0, 0, 1, 0, 1, 1 },
    { 1, 0, 1, 1, 0, 0 },
    { 0, 0, 0, 1, 0, 0 } };
    const char *tests[] = {"0240", "02340", "0242", "020", "0230", "024", "235432"};
    int k;
    if (check_cycle(adj_matrix, "0240") == 'y') printf("Cycle?: Yes\n");
    else printf("Cycle?: No\n");
    for (k = 0; k < 7; k++) printf("%s %c\n", tests[k], check_cycle(adj_matrix, (char *)tests[k]));
    return 0;
}
'''


def run_c(src, name):
    work = HERE / 'work'
    work.mkdir(exist_ok=True)
    c = work / f'{name}.c'
    c.write_text(src)
    exe = work / name
    subprocess.run(['cc', '-std=c11', '-Wall', '-o', str(exe), str(c)], check=True)
    return subprocess.run([str(exe)], capture_output=True, text=True, check=True).stdout


def q_2017_q8():
    out = run_c(C_CHECK, 'check_cycle')
    lines = out.strip().splitlines()
    assert lines[0] == 'Cycle?: Yes', out
    res = dict(l.split() for l in lines[1:])
    assert res == {'0240': 'y', '02340': 'y', '0242': 'n', '020': 'n', '0230': 'n', '024': 'n', '235432': 'n'}, res
    return 'Cycle?: Yes (0-2, 2-4, 4-0 간선이 모두 있고 시작=끝, 간선·정점 반복 없음)'


# ---------- textbook ch10-q02: 인접 행렬 -> 인접 리스트 ----------
def q_ch10_q02():
    M = [[0, 1, 0, 0], [1, 0, 1, 1], [0, 1, 0, 0], [0, 1, 0, 0]]
    return fmt_list(adj_list(M))


# ---------- textbook ch10-q03: 인접 행렬에서 한 정점 차수 ----------
def q_ch10_q03():
    # 행 v의 n칸을 모두 본다 -> O(n), 보기 2
    return '② O(n)'


# ---------- textbook ch10-q04: 인접 리스트 총 노드 수 ----------
def q_ch10_q04():
    # 무방향 간선 하나가 양 끝 정점의 리스트에 한 번씩 -> 2e (S10 p10 G1: 간선 5, 노드 10)
    E = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
    L = adj_list(matrix(4, E))
    assert sum(len(v) for v in L.values()) == 2 * len(E)
    return '② 2e개'


# ---------- textbook ch10-q06 ----------
Q06_E = [(0, 1), (1, 2), (1, 3), (3, 4), (2, 4), (0, 4)]


def q_ch10_q06():
    M = matrix(5, Q06_E)
    names = [f'v{i}' for i in range(5)]
    return 'matrix ' + fmt_mat(M) + ' | list ' + fmt_list(adj_list(M), names)


# ---------- textbook ch10-q08: 방향 그래프 ----------
Q08_E = [(1, 2), (1, 3), (1, 4), (2, 1), (2, 3), (2, 5), (3, 1), (3, 2), (3, 4), (3, 5), (4, 2), (5, 1), (5, 3)]


def q_ch10_q08():
    out = {v: [b for a, b in Q08_E if a == v] for v in range(1, 6)}
    both = sorted({tuple(sorted(e)) for e in Q08_E if (e[1], e[0]) in Q08_E})
    one = [e for e in Q08_E if (e[1], e[0]) not in Q08_E]
    return ('out ' + '; '.join(f'{v} → ' + ', '.join(map(str, out[v])) for v in out)
            + f' | 양방향 쌍 {both} | 한 방향만 {one}')


# ---------- textbook ch10-q09: 진출/진입 차수, 간선 수 ----------
C_DEG = r'''
#include <stdio.h>
#define N 5
int out_degree(int a[N][N], int n, int v) { int j, d = 0; for (j = 0; j < n; j++) d += a[v][j]; return d; }
int in_degree(int a[N][N], int n, int v) { int i, d = 0; for (i = 0; i < n; i++) d += a[i][v]; return d; }
int edge_count(int a[N][N], int n) { int i, j, e = 0; for (i = 0; i < n; i++) for (j = 0; j < n; j++) e += a[i][j]; return e; }
int main(void) {
    /* ch10-q08 의 방향 그래프(정점 1..5 를 0..4 로) 로 함수 확인 */
    int a[N][N] = {0};
    int E[13][2] = {{1,2},{1,3},{1,4},{2,1},{2,3},{2,5},{3,1},{3,2},{3,4},{3,5},{4,2},{5,1},{5,3}};
    int k, v;
    for (k = 0; k < 13; k++) a[E[k][0]-1][E[k][1]-1] = 1;
    for (v = 0; v < N; v++) printf("%d out=%d in=%d\n", v + 1, out_degree(a, N, v), in_degree(a, N, v));
    printf("edges=%d\n", edge_count(a, N));
    return 0;
}
'''


def q_ch10_q09():
    out = run_c(C_DEG, 'degree')
    exp = []
    for v in range(1, 6):
        exp.append(f'{v} out={sum(1 for a, b in Q08_E if a == v)} in={sum(1 for a, b in Q08_E if b == v)}')
    exp.append('edges=13')
    assert out.strip().splitlines() == exp, out
    return '1) 진출차수: j=0..n-1 의 a[v][j] 합, O(n) 2) 진입차수: i=0..n-1 의 a[i][v] 합, O(n) 3) 간선 수: 행렬 전체 합, O(n^2) (무방향 그래프라면 합/2)'


# ---------- textbook ch10-q11 ----------
def q_ch10_q11():
    r = []
    for n in (3, 4, 5):
        e = len(list(itertools.combinations(range(n), 2)))
        assert e == n * (n - 1) // 2
        r.append(f'{n}정점 {e}개')
    return ', '.join(r)


# ---------- lecture S10 p3: 쾨니히스베르크 ----------
KON = [('A', 'C', 'c'), ('A', 'C', 'd'), ('A', 'B', 'a'), ('A', 'B', 'b'), ('A', 'D', 'e'), ('C', 'D', 'g'), ('B', 'D', 'f')]


def q_lecture_euler():
    deg = {}
    for u, v, _ in KON:
        deg[u] = deg.get(u, 0) + 1
        deg[v] = deg.get(v, 0) + 1
    odd = [v for v in sorted(deg) if deg[v] % 2]
    assert deg == {'A': 5, 'B': 3, 'C': 3, 'D': 3}
    # 실제로 모든 다리를 한 번씩 건너 제자리로 오는 순서가 없음을 전수 확인
    def circuit_exists():
        for perm in itertools.permutations(range(len(KON))):
            for start in 'ABCD':
                cur, ok = start, True
                for i in perm:
                    u, v, _ = KON[i]
                    if cur == u: cur = v
                    elif cur == v: cur = u
                    else: ok = False; break
                if ok and cur == start:
                    return True
        return False
    assert not circuit_exists()
    # 다리 하나(e) 더 놓으면? A,D 가 짝수 -> 홀수 B,C 2개 남음
    return (f"정점 4개(A·B·C·D), 간선 7개, 차수 A=5 B=3 C=3 D=3, 홀수 차수 정점 {len(odd)}개 -> 불가능")


ANSWERS = {
    '2019-final-q2': q_2019_q2,
    '2019-final-q5': q_2019_q5,
    '2017-final2-q8': q_2017_q8,
    'textbook-ch10-q02': q_ch10_q02,
    'textbook-ch10-q03': q_ch10_q03,
    'textbook-ch10-q04': q_ch10_q04,
    'textbook-ch10-q06': q_ch10_q06,
    'textbook-ch10-q08': q_ch10_q08,
    'textbook-ch10-q09': q_ch10_q09,
    'textbook-ch10-q11': q_ch10_q11,
    'lecture-s10-p3-konigsberg': q_lecture_euler,
}

if __name__ == '__main__':
    for k, f in ANSWERS.items():
        print(f'{k}\t{f()}')
