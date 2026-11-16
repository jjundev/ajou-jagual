/* p9 독립 검산: 진출차수·진입차수·간선 수 함수와 반복 횟수 계측 */
#include <stdio.h>
#define MAX_VERTICES 50

static long steps;

int out_degree(int a[][MAX_VERTICES], int n, int v)
{
    int j, count = 0;
    for (j = 0; j < n; j++) { count += a[v][j]; steps++; }
    return count;
}

int in_degree(int a[][MAX_VERTICES], int n, int v)
{
    int i, count = 0;
    for (i = 0; i < n; i++) { count += a[i][v]; steps++; }
    return count;
}

int edge_count(int a[][MAX_VERTICES], int n)
{
    int i, j, count = 0;
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++) { count += a[i][j]; steps++; }
    return count;
}

static int g[MAX_VERTICES][MAX_VERTICES];

static void clear(void) {
    int i, j;
    for (i = 0; i < MAX_VERTICES; i++) for (j = 0; j < MAX_VERTICES; j++) g[i][j] = 0;
}

int main(void)
{
    int v, n;
    /* G3: <0,1>, <1,0>, <1,2> */
    clear(); g[0][1] = g[1][0] = g[1][2] = 1;
    for (v = 0; v < 3; v++) printf("G3 v=%d out=%d in=%d\n", v, out_degree(g, 3, v), in_degree(g, 3, v));
    printf("G3 edges=%d\n", edge_count(g, 3));

    /* 교과서 8번 방향 그래프(정점 1~5를 0~4로) */
    {
        int E[13][2] = {{1,2},{1,3},{1,4},{2,1},{2,3},{2,5},{3,1},{3,2},{3,4},{3,5},{4,2},{5,1},{5,3}};
        int k, so = 0, si = 0;
        clear();
        for (k = 0; k < 13; k++) g[E[k][0]-1][E[k][1]-1] = 1;
        for (v = 0; v < 5; v++) {
            int o = out_degree(g, 5, v), i = in_degree(g, 5, v);
            so += o; si += i;
            printf("Q8 v=%d out=%d in=%d\n", v + 1, o, i);
        }
        printf("Q8 edges=%d sum_out=%d sum_in=%d\n", edge_count(g, 5), so, si);
    }

    /* 반복 횟수: 간선 수와 무관하게 n, n, n*n */
    for (n = 1; n <= 40; n *= 2) {
        long a, b, c;
        clear();
        steps = 0; out_degree(g, n, 0); a = steps;
        steps = 0; in_degree(g, n, 0);  b = steps;
        steps = 0; edge_count(g, n);    c = steps;
        printf("n=%d empty: out_steps=%ld in_steps=%ld edge_steps=%ld\n", n, a, b, c);
        { int i, j; for (i = 0; i < n; i++) for (j = 0; j < n; j++) g[i][j] = (i != j); }
        steps = 0; out_degree(g, n, 0); a = steps;
        steps = 0; in_degree(g, n, 0);  b = steps;
        steps = 0; printf("n=%d full: edges=%d", n, edge_count(g, n)); c = steps;
        printf(" out_steps=%ld in_steps=%ld edge_steps=%ld\n", a, b, c);
    }
    return 0;
}
