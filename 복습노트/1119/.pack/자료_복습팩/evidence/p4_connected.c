#include <stdio.h>
#define MAX_SIZE 6
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
int main(){
	/* 연결: 0-1,0-2,1-3,3-4,4-5 (2는 막다른 노드) */
	int a[MAX_SIZE][MAX_SIZE] = {
		{0,1,1,0,0,0},{1,0,0,1,0,0},{1,0,0,0,0,0},
		{0,1,0,0,1,0},{0,0,0,1,0,1},{0,0,0,0,1,0} };
	/* 비연결: 0-1,1-2 / 3-4,4-5 */
	int b[MAX_SIZE][MAX_SIZE] = {
		{0,1,0,0,0,0},{1,0,1,0,0,0},{0,1,0,0,0,0},
		{0,0,0,0,1,0},{0,0,0,1,0,1},{0,0,0,0,1,0} };
	printf( "Graph is connected?(y/n): %c \n", connected_graph(a) );
	printf( "Graph is connected?(y/n): %c \n", connected_graph(b) );
	return 0;
}
