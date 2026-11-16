
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
