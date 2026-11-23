#include <stdio.h>

enum { N = 5 };
typedef struct { int adj_mat[N][N]; } GraphType;
int visited[N];
int parent[N];

void dfs_mat(GraphType *g, int v)
{
  visited[v] = 1;
  printf("%d ", v);
  for (int w = 0; w < N; w++) {
    if (g->adj_mat[v][w] && !visited[w]) {
      parent[w] = v;
      dfs_mat(g, w);
    }
  }
}

void bfs_mat(GraphType *g, int v)
{
  int w, q[N];
  int head = 0, tail = 0;
  visited[v] = 1;
  printf("%d ", v);
  q[tail] = v; tail++;
  while (head < tail) {
    v = q[head]; head++;
    for (w = 0; w < N; w++) {
      if (g->adj_mat[v][w] && !visited[w]) {
        visited[w] = 1;
        parent[w] = v;
        printf("%d ", w);
        q[tail] = w; tail++;
      }
    }
  }
}
