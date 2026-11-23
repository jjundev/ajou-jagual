#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>

#define MAX_VERTICES 20
#define MAX_QUEUE_SIZE (MAX_VERTICES + 1)
#define UNCOLORED 0
#define GROUP_ONE 1
#define GROUP_TWO 2

typedef struct
{
    int vertex_count;
    int adjacency_matrix[MAX_VERTICES][MAX_VERTICES];
} Graph;

typedef struct
{
    int vertices[MAX_QUEUE_SIZE];
    int front;
    int rear;
} Queue;

void initialize_colors(int colors[]);
void initialize_queue(Queue *queue);
int is_empty_queue(const Queue *queue);
int is_full_queue(const Queue *queue);
void enqueue(Queue *queue, int vertex);
int dequeue(Queue *queue);
int is_bipartite_dfs(const Graph *graph, int colors[]);
int is_bipartite_bfs(const Graph *graph, int colors[]);
void print_result(const char *method, int possible,
                  const Graph *graph, const int colors[]);

int check_component_dfs(const Graph *graph, int start, int group, int colors[]);
int check_component_bfs(const Graph *graph, int start, int group, int colors[]);

void initialize_colors(int colors[])
{
    int vertex;

    for (vertex = 0; vertex < MAX_VERTICES; vertex++)
    {
        colors[vertex] = UNCOLORED;
    }
}

void initialize_queue(Queue *queue)
{
    queue->front = 0;
    queue->rear = 0;
}

int is_empty_queue(const Queue *queue)
{
    return queue->front == queue->rear;
}

int is_full_queue(const Queue *queue)
{
    return (queue->rear + 1) % MAX_QUEUE_SIZE == queue->front;
}

void enqueue(Queue *queue, int vertex)
{
    if (is_full_queue(queue))
    {
        printf("QUEUE_ERROR\n");
        exit(1);
    }
    queue->vertices[queue->rear] = vertex;
    queue->rear = (queue->rear + 1) % MAX_QUEUE_SIZE;
}

int dequeue(Queue *queue)
{
    int vertex;

    if (is_empty_queue(queue))
    {
        printf("QUEUE_ERROR\n");
        exit(1);
    }
    vertex = queue->vertices[queue->front];
    queue->front = (queue->front + 1) % MAX_QUEUE_SIZE;
    return vertex;
}

/* 전체 그래프 검사*/
int is_bipartite_dfs(const Graph *graph, int colors[])
{
    int vertex;

    initialize_colors(colors);
    for (vertex = 0; vertex < graph->vertex_count; vertex++)
    {
        if (colors[vertex] == UNCOLORED &&
            !check_component_dfs(graph, vertex, GROUP_ONE, colors))
        {
            return 0;
        }
    }
    return 1;
}

int is_bipartite_bfs(const Graph *graph, int colors[])
{
    int vertex;

    initialize_colors(colors);
    for (vertex = 0; vertex < graph->vertex_count; vertex++)
    {
        if (colors[vertex] == UNCOLORED &&
            !check_component_bfs(graph, vertex, GROUP_ONE, colors))
        {
            return 0;
        }
    }
    return 1;
}

void print_result(const char *method, int possible,
                  const Graph *graph, const int colors[])
{
    int vertex;

    printf("%s %s\n", method, possible ? "YES" : "NO");
    if (possible)
    {
        printf("%s_GROUPS", method);
        for (vertex = 0; vertex < graph->vertex_count; vertex++)
        {
            printf(" %d", colors[vertex]);
        }
        printf("\n");
    }
}

/* DFS
 * start에 group을 배정하고 인접 정점을 확인
 * 미배정 이웃은 반대 그룹으로 재귀 검사
 * 재귀 검사 실패 또는 같은 그룹의 이웃 발견 시 즉시 0을 반환
 * 모든 이웃 검사에 성공하면 1을 반환 */
int check_component_dfs(const Graph *graph, int start, int group, int colors[])
{
    int next;
    int opposite_group = (group == GROUP_ONE) ? GROUP_TWO : GROUP_ONE;

    colors[start] = group;

    ////////////////////////////

    ////////////////////////////

    return 1;
}

/* BFS
 * 미배정 이웃은 현재 정점과 반대 그룹으로 배정하여 큐에 넣음
 * 같은 그룹의 이웃을 발견하면 0, 끝까지 충돌이 없으면 1을 반환 */
int check_component_bfs(const Graph *graph, int start, int group, int colors[])
{
    Queue queue;
    int current, next;
    int opposite_group;

    initialize_queue(&queue);
    colors[start] = group;
    enqueue(&queue, start);

    while (!is_empty_queue(&queue))
    {
        current = dequeue(&queue);
        opposite_group = (colors[current] == GROUP_ONE) ? GROUP_TWO : GROUP_ONE;

        ////////////////////////////

        ////////////////////////////
    }
    return 1;
}

int main(void)
{
    // const Graph graph = {
    //     4,
    //     {{0, 1, 0, 1},
    //      {1, 0, 1, 0},
    //      {0, 1, 0, 1},
    //      {1, 0, 1, 0}}};
    const Graph graph = {
        3,
        {{0, 1, 1},
         {1, 0, 1},
         {1, 1, 0}}};
    int dfs_colors[MAX_VERTICES];
    int bfs_colors[MAX_VERTICES];
    int dfs_possible, bfs_possible;

    dfs_possible = is_bipartite_dfs(&graph, dfs_colors);
    bfs_possible = is_bipartite_bfs(&graph, bfs_colors);
    print_result("DFS", dfs_possible, &graph, dfs_colors);
    print_result("BFS", bfs_possible, &graph, bfs_colors);
    return 0;
}
