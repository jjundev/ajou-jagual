#include <stdio.h>
#define N 10
int adj[N][N], visited[N];
void dfs(int v) {
    visited[v] = 1;
    for (int w = 0; w < N; w++)
        if (adj[v][w] && !visited[w]) dfs(w);
}
int is_connected(void) {
    for (int i = 0; i < N; i++) visited[i] = 0;
    dfs(0);
    for (int i = 0; i < N; i++) if (!visited[i]) return 0;
    return 1;
}
void find_bridges(void) {
    for (int u = 0; u < N; u++)
        for (int v = u + 1; v < N; v++)
            if (adj[u][v]) {
                adj[u][v] = adj[v][u] = 0;          /* 간선 하나 지우기 */
                if (!is_connected()) printf("(%d, %d) ", u, v);
                adj[u][v] = adj[v][u] = 1;          /* 되돌리기 */
            }
    printf("\n");
}
int main(void) {
    int e[][2] = {{0,1},{1,2},{1,3},{2,4},{3,4},{3,5},
                   {5,6},{5,7},{6,7},{7,8},{7,9}};
    for (int i = 0; i < 11; i++)
        adj[e[i][0]][e[i][1]] = adj[e[i][1]][e[i][0]] = 1;
    find_bridges();
    return 0;
}