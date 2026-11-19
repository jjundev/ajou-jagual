#include <stdio.h>
#define MAX_SIZE 6
/* 2017 김도희 기말 7번 원본 모범답안(공지용 PDF p6) 그대로 */
char connected_graph_orig( int adj_matrix[MAX_SIZE][MAX_SIZE] ) {
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
	else return 'n';
}
/* 팩의 큐 BFS 답 */
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
static void build(int m[MAX_SIZE][MAX_SIZE], int e[][2], int k){
	for(int i=0;i<MAX_SIZE;i++)for(int j=0;j<MAX_SIZE;j++)m[i][j]=0;
	for(int i=0;i<k;i++){m[e[i][0]][e[i][1]]=1;m[e[i][1]][e[i][0]]=1;}
}
int main(void){
	int m[MAX_SIZE][MAX_SIZE];
	int a[][2]={{0,1},{0,2},{1,3},{3,4},{4,5}};
	int b[][2]={{0,1},{1,2},{3,4},{4,5}};
	int c[][2]={{0,1},{0,2},{1,2},{1,5},{2,5},{3,4}};
	int d[][2]={{0,1},{1,2},{2,3},{3,4},{4,5}};
	build(m,a,5); printf("dead-end 0-1,0-2,1-3,3-4,4-5: orig=%c queue=%c\n",connected_graph_orig(m),connected_graph(m));
	build(m,b,4); printf("split 0-1,1-2 | 3-4,4-5: orig=%c queue=%c\n",connected_graph_orig(m),connected_graph(m));
	build(m,c,6); printf("grading example {0,1,2,5}|{3,4}: orig=%c queue=%c\n",connected_graph_orig(m),connected_graph(m));
	build(m,d,5); printf("path 0-1-2-3-4-5: orig=%c queue=%c\n",connected_graph_orig(m),connected_graph(m));
	return 0;
}
