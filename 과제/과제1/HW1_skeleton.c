#include <stdio.h>

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

int read_state(void)
{
    return 1;
}

void calculate_need(void)
{
}

int can_run(int process)
{
    return 1;
}

int search_safe_sequence(int depth)
{
    int count = 0;

    if (depth == system_state.n_process) {
        return 1;
    }


    return count;
}

int main(void)
{
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
