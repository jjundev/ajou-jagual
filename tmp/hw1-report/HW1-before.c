#include <stdio.h>
#include <stdlib.h>

#define MAX_PROCESS 8
#define MAX_RESOURCE 5

typedef struct {
  int n_process, n_resource;
  int available[MAX_RESOURCE];
  int allocation[MAX_PROCESS][MAX_RESOURCE];
  int maximum[MAX_PROCESS][MAX_RESOURCE];
  int need[MAX_PROCESS][MAX_RESOURCE];
} SystemState;

typedef struct {
  int finish[MAX_PROCESS];
  int safe_count;
} SearchState;

static SystemState system_state;
static SearchState search_state;

int read_state(void);
void calculate_need(void);
int can_run(int process);
int search_safe_sequence(int depth);

int read_state(void) {
  printf("프로세스의 수를 입력하세요. (1~8): ");
  if (scanf("%d", &system_state.n_process) != 1 ||
      system_state.n_process < 1 || system_state.n_process > MAX_PROCESS) {
    printf("잘못된 값을 입력하셨습니다.\n");
    return 0;
  }

  printf("자원의 종류의 개수를 입력하세요. (0~5): ");
  if (scanf("%d", &system_state.n_resource) != 1 ||
      system_state.n_resource < 0 || system_state.n_resource > MAX_RESOURCE) {
    printf("잘못된 값을 입력하셨습니다.\n");
    return 0;
  }

  printf("현재 추가로 할당 가능한 각 자원의 수(AVAILABLE)를 입력하세요. (자원 "
         "종류 %d개)\n",
         system_state.n_resource);
  for (int i = 0; i < system_state.n_resource; ++i) {
    if (scanf("%d", &system_state.available[i]) != 1 ||
        system_state.available[i] < 0) {
      printf("잘못된 값을 입력하셨습니다.\n");
      return 0;
    }
  }

  printf("각 프로세스에 이미 할당된 자원의 수(ALLOCATION)를 입력하세요. (%d x "
         "%d)\n",
         system_state.n_process, system_state.n_resource);
  for (int i = 0; i < system_state.n_process; ++i) {
    for (int j = 0; j < system_state.n_resource; ++j) {
      if (scanf("%d", &system_state.allocation[i][j]) != 1 ||
          system_state.allocation[i][j] < 0) {
        printf("잘못된 값을 입력하셨습니다.\n");
        return 0;
      }
    }
  }

  printf("각 프로세스가 최대로 요구하는 자원의 수(MAXIMUM)를 입력하세요. (%d x "
         "%d):\n",
         system_state.n_process, system_state.n_resource);
  for (int i = 0; i < system_state.n_process; ++i) {
    for (int j = 0; j < system_state.n_resource; ++j) {
      if (scanf("%d", &system_state.maximum[i][j]) != 1 ||
          system_state.maximum[i][j] < system_state.allocation[i][j]) {
        printf("잘못된 값을 입력하셨습니다.\n");
        return 0;
      }
    }
  }
  return 1;
}

void calculate_need(void) {
  for (int i = 0; i < system_state.n_process; ++i) {
    for (int j = 0; j < system_state.n_resource; ++j) {
      system_state.need[i][j] =
          system_state.maximum[i][j] - system_state.allocation[i][j];
    }
  }
}

// P_process가 현재 남은 자원으로 실행 가능한지 판단
int can_run(int process) {
  for (int i = 0; i < system_state.n_resource; ++i) {
    if (system_state.need[process][i] > system_state.available[i]) {
      return 0;
    }
  }

  return 1;
}

int search_safe_sequence(int depth) {
  int count = 0;

  if (depth == system_state.n_process) {
    return 1;
  }

  for (int i = 0; i < system_state.n_process; ++i) {
    if (!search_state.finish[i] && can_run(i)) {
      search_state.finish[i] = 1;

      for (int j = 0; j < system_state.n_resource; ++j) {
        system_state.available[j] += system_state.allocation[i][j];
      }

      count += search_safe_sequence(depth + 1);

      for (int j = 0; j < system_state.n_resource; ++j) {
        system_state.available[j] -= system_state.allocation[i][j];
      }

      search_state.finish[i] = 0;
    }
  }

  return count;
}

int main(void) {
  int i, j;

  // user input으로 system_state 필드 초기화
  if (!read_state()) {
    return 0;
  }

  // system_state.need 필드 초기화
  calculate_need();

  // system_state 객체 출력
  printf("\nNeed matrix:\n");
  for (i = 0; i < system_state.n_process; ++i) {
    printf("P%d:", i);
    for (j = 0; j < system_state.n_resource; ++j) {
      printf(" %d", system_state.need[i][j]);
    }
    printf("\n");
  }

  // search_state 객체 초기화
  search_state.safe_count = 0;
  for (i = 0; i < system_state.n_process; ++i) {
    search_state.finish[i] = 0;
  }

  search_state.safe_count = search_safe_sequence(0);
  printf("가능한 시퀀스의 개수: %d\n", search_state.safe_count);

  return 0;
}
