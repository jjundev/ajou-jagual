#include <stdio.h>
#include <stdlib.h>

// 프로세스 수와 자원 종류 수의 입력 상한
#define MAX_PROCESS 8
#define MAX_RESOURCE 5

typedef struct {
  int n_process, n_resource; // 프로세스 수와 자원 종류 수
  int available[MAX_RESOURCE]; // 현재 추가로 할당 가능한 자원
  int allocation[MAX_PROCESS][MAX_RESOURCE]; // 각 프로세스에 이미 할당된 자원
  int maximum[MAX_PROCESS][MAX_RESOURCE]; // 각 프로세스의 최대 요구량
  int need[MAX_PROCESS][MAX_RESOURCE]; // 추가로 필요한 자원
} SystemState;

typedef struct {
  int finish[MAX_PROCESS]; // 현재 탐색 경로에서 완료를 가정한 표시
  int safe_count; // 안전 순서의 총개수
} SearchState;

// 여러 함수에서 함께 사용하는 시스템 정보와 탐색 상태
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
         "종류 %d개): \n",
         system_state.n_resource);
  for (int i = 0; i < system_state.n_resource; ++i) {
    if (scanf("%d", &system_state.available[i]) != 1 ||
        system_state.available[i] < 0) {
      printf("잘못된 값을 입력하셨습니다.\n");
      return 0;
    }
  }

  printf("각 프로세스에 이미 할당된 자원의 수(ALLOCATION)를 입력하세요. (%d x "
         "%d): \n",
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
         "%d): \n",
         system_state.n_process, system_state.n_resource);
  for (int i = 0; i < system_state.n_process; ++i) {
    for (int j = 0; j < system_state.n_resource; ++j) {
      // 최대 요구량이 기존 할당량보다 작으면 Need가 음수가 되므로 오류 처리
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

  // depth는 현재까지 순서에 넣은 프로세스 수이다.
  if (depth == system_state.n_process) {
    // 모든 프로세스를 선택했으므로 안전 순서 하나를 찾은 것이다.
    return 1;
  }

  for (int i = 0; i < system_state.n_process; ++i) {
    if (!search_state.finish[i] && can_run(i)) {
      search_state.finish[i] = 1;

      for (int j = 0; j < system_state.n_resource; ++j) {
        // 완료 후에는 기존에 할당받았던 자원만큼 가용 자원이 늘어난다.
        system_state.available[j] += system_state.allocation[i][j];
      }

      // 다음 깊이 탐색에서 찾은 안전 순서의 개수를 누적
      count += search_safe_sequence(depth + 1);

      // 다른 후보도 같은 상태에서 검사하도록 자원과 완료 표시를 되돌린다.
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

  if (!read_state()) {
    return 0;
  }

  calculate_need();

  printf("\nNeed matrix:\n");
  for (i = 0; i < system_state.n_process; ++i) {
    printf("P%d:", i);
    for (j = 0; j < system_state.n_resource; ++j) {
      printf(" %d", system_state.need[i][j]);
    }
    printf("\n");
  }

  search_state.safe_count = 0;
  for (i = 0; i < system_state.n_process; ++i) {
    search_state.finish[i] = 0;
  }

  search_state.safe_count = search_safe_sequence(0);
  printf("가능한 시퀀스의 개수: %d\n", search_state.safe_count);

  return 0;
}
