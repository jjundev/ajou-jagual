#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>

#define MAX_PROCESSES 20

typedef struct {
  int n;
  int adjacency_matrix[MAX_PROCESSES][MAX_PROCESSES];
} ProcessGraph;

int read_graph(ProcessGraph *graph);
void print_order(const int order[], int n);
void topological_sort(const ProcessGraph *graph, int order[]);

void calculate_indegree(const ProcessGraph *graph, int indegree[]);
int select_next_process(const ProcessGraph *graph, const int indegree[],
                        const int completed[]);
void complete_process(const ProcessGraph *graph, int pid, int indegree[],
                      int completed[]);

int read_graph(ProcessGraph *graph) {
  int edge_count;
  int i;
  int from, to;

  *graph = (ProcessGraph){0};
  if (scanf("%d %d", &graph->n, &edge_count) != 2 || graph->n < 1 ||
      graph->n > MAX_PROCESSES || edge_count < 0 ||
      edge_count > graph->n * (graph->n - 1) / 2) {
    return 0;
  }

  for (i = 0; i < edge_count; i++) {
    if (scanf("%d %d", &from, &to) != 2 || from < 0 || from >= graph->n ||
        to < 0 || to >= graph->n || from == to ||
        graph->adjacency_matrix[from][to] != 0) {
      return 0;
    }
    graph->adjacency_matrix[from][to] = 1;
  }
  return 1;
}

void print_order(const int order[], int n) {
  int i;

  printf("ORDER");
  for (i = 0; i < n; i++) {
    printf(" %d", order[i]);
  }
  printf("\n");
}

void topological_sort(const ProcessGraph *graph, int order[]) {
  int indegree[MAX_PROCESSES] = {0};
  int completed[MAX_PROCESSES] = {0};
  int step;
  int pid;

  calculate_indegree(graph, indegree);
  for (step = 0; step < graph->n; step++) {
    pid = select_next_process(graph, indegree, completed);

    if (pid == -1) {
      printf("STATE_ERROR\n");
      exit(1);
    }

    order[step] = pid;
    complete_process(graph, pid, indegree, completed);
  }
}

/*모든 프로세스의 진입차수를 계산한다.*/
void calculate_indegree(const ProcessGraph *graph, int indegree[]) {
  for (int row = 0; row < graph->n; row++) {
    for (int col = 0; col < graph->n; col++) {
      if (graph->adjacency_matrix[row][col] == 1) {
        indegree[col]++;
      }
    }
  }
}

/*completed 를 제외한 나머지 중에서 indegree 가 0 인 pid를 리턴한다. 하나도
 * 없다면 -1을 리턴한다. */
int select_next_process(const ProcessGraph *graph, const int indegree[],
                        const int completed[]) {
  for (int i = 0; i < graph->n; i++) {
    if (indegree[i] == 0 && completed[i] == 0) {
      return i;
    }
  }
  return -1;
}

/*pid를 완료처리한다.
후행 프로세스의 indegree를 하나씩 낮춘다 */
void complete_process(const ProcessGraph *graph, int pid, int indegree[],
                      int completed[]) {
  completed[pid] = 1;
  for (int i = 0; i < graph->n; i++) {
    if (completed[i] == 1)
      continue;

    if (graph->adjacency_matrix[pid][i] == 1) {
      indegree[i]--;
    }
  }
}

int main(void) {
  ProcessGraph graph;
  int order[MAX_PROCESSES] = {0};

  if (!read_graph(&graph)) {
    printf("INPUT_ERROR\n");
    return 1;
  }
  topological_sort(&graph, order);
  print_order(order, graph.n);
  return 0;
}
