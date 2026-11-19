#include <stdio.h>
#define MAX_SIZE 6

/* BFS from vertex 0; graph is connected iff every vertex gets visited. */
char connected_graph(int adj_matrix[MAX_SIZE][MAX_SIZE]) {
    int visited[MAX_SIZE] = {0};
    int queue[MAX_SIZE];
    int front = 0, rear = 0, cnt = 0;
    visited[0] = 1;
    queue[rear++] = 0;
    while (front < rear) {
        int v = queue[front++];
        cnt++;
        for (int w = 0; w < MAX_SIZE; w++)
            if (adj_matrix[v][w] && !visited[w]) {
                visited[w] = 1;
                queue[rear++] = w;
            }
    }
    return cnt == MAX_SIZE ? 'y' : 'n';
}

static void build(int m[MAX_SIZE][MAX_SIZE], const int (*e)[2], int ne) {
    for (int i = 0; i < MAX_SIZE; i++)
        for (int j = 0; j < MAX_SIZE; j++) m[i][j] = 0;
    for (int k = 0; k < ne; k++) { m[e[k][0]][e[k][1]] = 1; m[e[k][1]][e[k][0]] = 1; }
}

int main(void) {
    int m[MAX_SIZE][MAX_SIZE];
    struct { const char *name; int e[16][2]; int ne; char expect; } t[] = {
        {"path 0-1-2-3-4-5 (connected)", {{0,1},{1,2},{2,3},{3,4},{4,5}}, 5, 'y'},
        {"complete K6 (connected)", {{0,1},{0,2},{0,3},{0,4},{0,5},{1,2},{1,3},{1,4},{1,5},{2,3},{2,4},{2,5},{3,4},{3,5},{4,5}}, 15, 'y'},
        {"two triangles 0-1-2 / 3-4-5 (disconnected)", {{0,1},{1,2},{0,2},{3,4},{4,5},{3,5}}, 6, 'n'},
        {"dead-end at BFS level: 0-1,0-2,1-3,3-4,4-5 (connected)", {{0,1},{0,2},{1,3},{3,4},{4,5}}, 5, 'y'},
        {"isolated vertex 5: 0-1,1-2,2-3,3-4 (disconnected)", {{0,1},{1,2},{2,3},{3,4}}, 4, 'n'},
        {"isolated vertex 0: 1-2,2-3,3-4,4-5 (disconnected)", {{1,2},{2,3},{3,4},{4,5}}, 4, 'n'},
        {"no edges (disconnected)", {{0,0}}, 0, 'n'},
        {"star centered at 5 (connected)", {{5,0},{5,1},{5,2},{5,3},{5,4}}, 5, 'y'},
    };
    int nt = sizeof t / sizeof t[0], fails = 0;
    for (int i = 0; i < nt; i++) {
        build(m, (const int (*)[2])t[i].e, t[i].ne);
        char r = connected_graph(m);
        printf("%-58s Graph is connected?(y/n): %c  expected %c %s\n", t[i].name, r, t[i].expect, r == t[i].expect ? "OK" : "FAIL");
        if (r != t[i].expect) fails++;
    }
    printf("failures: %d\n", fails);
    return fails != 0;
}
