#include <stdio.h>
#define MAX_VERTICES 8
typedef struct GraphType { int n; int adj_mat[MAX_VERTICES][MAX_VERTICES]; } GraphType;
int visited[MAX_VERTICES];
int count;
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
int main(void) {
	GraphType g = { 8, {{0}} };
	int e[][2] = {{0,2},{0,5},{1,3},{2,5},{3,6},{4,6}};
	for (int i = 0; i < 6; i++) g.adj_mat[e[i][0]][e[i][1]] = g.adj_mat[e[i][1]][e[i][0]] = 1;
	find_connected_component(&g);
	printf("\n");
	for (int i = 0; i < 8; i++) printf("%d ", visited[i]);
	printf("\ncount=%d\n", count);
	return 0;
}
