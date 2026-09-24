#include <stdio.h>
#include <stdlib.h>

// 프로세스 수와 자원 종류 수의 입력 상한
#define MAX_PROCESS 8
#define MAX_RESOURCE 5

// available: 현재 추가로 할당할 수 있는 자원의 수
// allocation: 각 프로세스에 이미 할당된 자원의 수
// maximum: 각 프로세스가 최대로 요구하는 자원의 수
// need: 완료하기 위해 추가로 필요한 자원의 수
typedef struct {
  int n_process, n_resource;
  int available[MAX_RESOURCE];
  int allocation[MAX_PROCESS][MAX_RESOURCE];
  int maximum[MAX_PROCESS][MAX_RESOURCE];
  int need[MAX_PROCESS][MAX_RESOURCE];
} SystemState;

// finish: 현재 탐색 경로에서 완료를 가정한 프로세스 표시
// safe_count: 탐색이 끝난 뒤 저장하는 안전 순서의 총개수
typedef struct {
  int finish[MAX_PROCESS];
  int safe_count;
} SearchState;

// 여러 함수에서 함께 사용하는 시스템 정보와 탐색 상태
static SystemState system_state;
static SearchState search_state;

int read_state(void);
void calculate_need(void);
int can_run(int process);
int search_safe_sequence(int depth);

int read_state(void) {
  // 시스템 상태를 입력받는다. 입력이 잘못되면 0, 모두 읽으면 1을 반환한다.
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
      // 최대 요구량이 이미 할당된 양보다 작으면 올바른 상태가 아니다.
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
  // 최대 요구량에서 이미 가진 양을 빼서 추가로 필요한 양을 구한다.
  for (int i = 0; i < system_state.n_process; ++i) {
    for (int j = 0; j < system_state.n_resource; ++j) {
      system_state.need[i][j] =
          system_state.maximum[i][j] - system_state.allocation[i][j];
    }
  }
}

// 모든 자원 종류에서 필요량을 만족해야 이 프로세스를 완료할 수 있다.
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
      // 현재 경로에서 이 프로세스를 다시 고르지 않도록 표시한다.
      search_state.finish[i] = 1;

      for (int j = 0; j < system_state.n_resource; ++j) {
        // 완료 후에는 기존에 할당받았던 자원만큼 가용 자원이 늘어난다.
        system_state.available[j] += system_state.allocation[i][j];
      }

      // 이 프로세스 다음에 이어질 수 있는 안전 순서의 개수를 더한다.
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

  // 사용자 입력으로 시스템 상태 초기화
  if (!read_state()) {
    return 0;
  }

  // 추가 필요량 계산
  calculate_need();

  // 계산한 Need 행렬 출력
  printf("\nNeed matrix:\n");
  for (i = 0; i < system_state.n_process; ++i) {
    printf("P%d:", i);
    for (j = 0; j < system_state.n_resource; ++j) {
      printf(" %d", system_state.need[i][j]);
    }
    printf("\n");
  }

  // 안전 순서 탐색 상태 초기화
  search_state.safe_count = 0;
  for (i = 0; i < system_state.n_process; ++i) {
    search_state.finish[i] = 0;
  }

  search_state.safe_count = search_safe_sequence(0);
  printf("가능한 시퀀스의 개수: %d\n", search_state.safe_count);

  return 0;
}
