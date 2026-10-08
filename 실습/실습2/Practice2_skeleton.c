#include <stdio.h>
#include <stdlib.h>

#define MAX_PROCESS 100

typedef struct
{
    int pid;
    int priority;
} Process;

typedef struct ProcessNode
{
    Process data;
    struct ProcessNode *prev;
    struct ProcessNode *next;
} ProcessNode;

typedef struct
{
    ProcessNode head;
    int length;
} ProcessList;

void init_list(ProcessList *list);
ProcessNode *create_node(int pid, int priority);
void insert_after(ProcessNode *position, ProcessNode *new_node);
void detach_node(ProcessNode *node);
int append_process(ProcessList *list, int pid, int priority);
void sort_by_priority(ProcessList *list);
void print_list(const ProcessList *list);
void destroy_list(ProcessList *list);

void init_list(ProcessList *list)
{
    list->head.data.pid = -1;
    list->head.data.priority = -1;
    list->head.prev = &list->head;
    list->head.next = &list->head;
    list->length = 0;
}

ProcessNode *create_node(int pid, int priority)
{
    ProcessNode *new_node;

    new_node = (ProcessNode *)malloc(sizeof(ProcessNode));
    if (new_node == NULL)
    {
        return NULL;
    }

    new_node->data.pid = pid;
    new_node->data.priority = priority;
    new_node->prev = NULL;
    new_node->next = NULL;

    return new_node;
}

void insert_after(ProcessNode *position, ProcessNode *new_node)
{
    if (position == NULL || new_node == NULL)
    {
        return;
    }

    new_node->prev = position;
    new_node->next = position->next;
    position->next->prev = new_node;
    position->next = new_node;
}

void detach_node(ProcessNode *node)
{
    if (node == NULL || node->prev == NULL || node->next == NULL)
    {
        return;
    }

    node->prev->next = node->next;
    node->next->prev = node->prev;
    node->prev = NULL;
    node->next = NULL;
}

int append_process(ProcessList *list, int pid, int priority)
{
    ProcessNode *new_node;

    if (list == NULL || pid <= 0 || priority < 0)
    {
        return 0;
    }

    new_node = create_node(pid, priority);
    if (new_node == NULL)
    {
        return 0;
    }

    insert_after(list->head.prev, new_node);
    list->length++;
    return 1;
}

/*
 * 우선순위 숫자가 작은 프로세스가 앞으로 오도록 정렬합니다.
 * 노드의 data를 교환하지 않고 노드 자체를 이동합니다.
 * 같은 우선순위의 프로세스는 기존 순서를 유지합니다.
 */
void sort_by_priority(ProcessList *list)
{
    ProcessNode *current;
    ProcessNode *next_unsorted;
    ProcessNode *position;

    if (list == NULL || list->length < 2)
    {
        return;
    }

    /*
     * 첫 번째 노드는 이미 정렬된 것으로 간주하고
     * 두 번째 노드부터 삽입 위치를 찾습니다.
     */
    current = list->head.next->next;

    while (current != &list->head)
    {
        /*
         * current를 다른 위치로 옮기면 current->next가 변경됩니다.
         * 이동하기 전에 다음 정렬 대상 노드를 저장하세요.
         * current 바로 이전 노드부터 탐색을 시작하세요.
         */
        next_unsorted = NULL;
        position = NULL;

        /*
         * 다음 조건을 모두 만족하는 동안 이전 방향으로 이동하세요.
         *
         * 1. position이 헤드 노드가 아님
         * 2. position의 우선순위가 current의 우선순위보다 큼
         */
        while ()
        {
        }

        /*
         * currnet를 현재 위치에서 제거하세요.
         * current를 탐색한 위치에 삽입하세요.
         */

        /*
         * 다음 정렬 대상 노드로 이동합니다.
         */
        current = next_unsorted;
    }
}

void print_list(const ProcessList *list)
{
    const ProcessNode *current;

    if (list == NULL)
    {
        return;
    }

    printf("HEAD");
    current = list->head.next;

    while (current != &list->head)
    {
        printf(" <-> P%d(%d)",
               current->data.pid,
               current->data.priority);
        current = current->next;
    }

    printf(" <-> HEAD\n");
}

void destroy_list(ProcessList *list)
{
    ProcessNode *current;

    if (list == NULL)
    {
        return;
    }

    while (list->head.next != &list->head)
    {
        current = list->head.next;
        detach_node(current);
        free(current);
    }

    list->length = 0;
}

int main(void)
{
    ProcessList process_list;
    const Process sample_processes[] = {
        {1, 3},
        {2, 1},
        {3, 4},
        {4, 2}};
    const int n_process =
        (int)(sizeof(sample_processes) / sizeof(sample_processes[0]));
    int i;

    init_list(&process_list);

    for (i = 0; i < n_process; ++i)
    {
        if (!append_process(&process_list,
                            sample_processes[i].pid,
                            sample_processes[i].priority))
        {
            printf("프로세스 노드를 생성할 수 없습니다.\n");
            destroy_list(&process_list);
            return 0;
        }
    }

    printf("\n정렬 전:\n");
    print_list(&process_list);

    sort_by_priority(&process_list);

    printf("정렬 후:\n");
    print_list(&process_list);

    destroy_list(&process_list);
    return 0;
}
