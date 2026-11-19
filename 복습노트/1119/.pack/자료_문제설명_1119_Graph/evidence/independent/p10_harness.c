#include <stdio.h>
#define MAX_VERTICES 8
typedef struct GraphType { int n; int adj_mat[MAX_VERTICES][MAX_VERTICES]; } GraphType;
int visited[MAX_VERTICES];
int count;

/* ---- given code, verbatim ---- */
void dfs_mat(GraphType *g, int v)
{
    int w;
    visited[v] = count;
    printf("%d ", v);
    for(w=0; w<g->n; w++)
        if( g->adj_mat[v][w] && !visited[w] )
            dfs_mat(g, w);
}
void find_connected_component(GraphType *g)
{
    int i;
    count = 0;
    for(i=0; i<g->n; i++)
        if(!visited[i]){
            count++;
            dfs_mat(g, i);
        }
}
/* ------------------------------ */

int main(void) {
    static GraphType g;
    int e[][2] = {{0,2},{0,5},{1,3},{2,5},{3,6},{4,6}};
    g.n = 8;
    for (int k = 0; k < 6; k++) { g.adj_mat[e[k][0]][e[k][1]] = 1; g.adj_mat[e[k][1]][e[k][0]] = 1; }
    printf("(a) printed: ");
    find_connected_component(&g);
    printf("\n(b) visited[0..7]:");
    for (int i = 0; i < 8; i++) printf(" %d", visited[i]);
    printf("\n(c) count = %d\n", count);
    return 0;
}
