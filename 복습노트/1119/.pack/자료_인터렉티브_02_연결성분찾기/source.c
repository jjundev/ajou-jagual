#include <stdio.h>

enum { N = 5 };
typedef struct { int adj_mat[N][N]; } GraphType;
int visited[N];
int parent[N];
int count;

void dfs_mat(GraphType *g, int v)
{
  visited[v] = count;
  printf("%d ", v);
  for (int w = 0; w < N; w++) {
    if (g->adj_mat[v][w] && !visited[w]) {
      parent[w] = v;
      dfs_mat(g, w);
    }
  }
}

void find_connected_component(GraphType *g)
{
  count = 0;
  for (int i = 0; i < N; i++) {
    if (!visited[i]) {
      count++;
      dfs_mat(g, i);
    }
  }
}
