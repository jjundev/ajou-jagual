#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FREE_PID (-1)
#define HEAD_PID (-2)
#define MAX_COMMANDS 10000
#define COMMAND_LENGTH 16

typedef struct MemoryBlock
{
    int start;
    int size;
    int pid;
    struct MemoryBlock *prev;
    struct MemoryBlock *next;
} MemoryBlock;

typedef struct
{
    MemoryBlock head;
    int total_size;
} MemoryList;

int init_list(MemoryList *list, int total_size);
MemoryBlock *create_block(int start, int size, int pid);
void insert_after(MemoryBlock *position, MemoryBlock *new_block);
void remove_block(MemoryBlock *removed);
void destroy_list(MemoryList *list);
void print_memory_map(const MemoryList *list);

/* 학생 구현 함수 */
MemoryBlock *find_first_fit(MemoryList *list, int size);
MemoryBlock *find_process_block(MemoryList *list, int pid);
int allocate_memory(MemoryList *list, int pid, int size);
MemoryBlock *merge_free_blocks(MemoryList *list, MemoryBlock *current);
int release_memory(MemoryList *list, int pid);

int init_list(MemoryList *list, int total_size)
{
    MemoryBlock *initial_block;

    if (list == NULL || total_size <= 0)
    {
        return 0;
    }

    list->head.start = -1;
    list->head.size = 0;
    list->head.pid = HEAD_PID;
    list->head.prev = &list->head;
    list->head.next = &list->head;
    list->total_size = total_size;

    initial_block = create_block(0, total_size, FREE_PID);
    if (initial_block == NULL)
    {
        list->total_size = 0;
        return 0;
    }

    insert_after(&list->head, initial_block);
    return 1;
}

MemoryBlock *create_block(int start, int size, int pid)
{
    MemoryBlock *block;

    block = (MemoryBlock *)malloc(sizeof(MemoryBlock));
    if (block == NULL)
    {
        return NULL;
    }

    block->start = start;
    block->size = size;
    block->pid = pid;
    block->prev = NULL;
    block->next = NULL;
    return block;
}

void insert_after(MemoryBlock *position, MemoryBlock *new_block)
{
    if (position == NULL || new_block == NULL)
    {
        return;
    }

    new_block->prev = position;
    new_block->next = position->next;
    position->next->prev = new_block;
    position->next = new_block;
}

void remove_block(MemoryBlock *removed)
{
    if (removed == NULL || removed->pid == HEAD_PID ||
        removed->prev == NULL || removed->next == NULL)
    {
        return;
    }

    removed->prev->next = removed->next;
    removed->next->prev = removed->prev;
    removed->prev = NULL;
    removed->next = NULL;
    free(removed);
}

void destroy_list(MemoryList *list)
{
    if (list == NULL)
    {
        return;
    }

    while (list->head.next != &list->head)
    {
        remove_block(list->head.next);
    }

    list->head.prev = &list->head;
    list->head.next = &list->head;
    list->total_size = 0;
}

void print_memory_map(const MemoryList *list)
{
    const MemoryBlock *block;

    if (list == NULL)
    {
        return;
    }

    printf("Memory map: ");
    block = list->head.next;
    while (block != &list->head)
    {
        printf("[%d-%d, ", block->start, block->start + block->size - 1);
        if (block->pid == FREE_PID)
        {
            printf("FREE]");
        }
        else
        {
            printf("P%d]", block->pid);
        }

        block = block->next;
        if (block != &list->head)
        {
            printf(" <-> ");
        }
    }
    printf("\n");
}

MemoryBlock *find_first_fit(MemoryList *list, int size)
{
    /* TODO: 요청 크기 이상인 첫 번째 빈 블록을 반환합니다. */
    return NULL;
}

MemoryBlock *find_process_block(MemoryList *list, int pid)
{
    /* TODO: pid가 할당된 블록을 반환합니다. */
    return NULL;
}

int allocate_memory(MemoryList *list, int pid, int size)
{
    /* TODO: First-Fit으로 블록을 찾고, 필요한 경우 블록을 분할합니다. */
    return 0;
}

MemoryBlock *merge_free_blocks(MemoryList *list, MemoryBlock *current)
{
    /* TODO: current를 이전 및 다음의 빈 블록과 병합합니다. */
    return current;
}

int release_memory(MemoryList *list, int pid)
{
    /* TODO: pid의 블록을 빈 블록으로 만들고 병합합니다. */
    return 0;
}

int main(void)
{
    MemoryList memory;
    char command[COMMAND_LENGTH];
    int total_size;
    int command_count;
    int i;
    int pid;
    int size;
    int result;

    printf("전체 메모리 크기를 입력하세요: ");
    if (scanf("%d", &total_size) != 1 || total_size <= 0)
    {
        printf("잘못된 전체 메모리 크기입니다.\n");
        return 0;
    }

    if (!init_list(&memory, total_size))
    {
        printf("메모리 리스트를 초기화할 수 없습니다.\n");
        return 0;
    }

    printf("명령의 개수를 입력하세요: ");
    if (scanf("%d", &command_count) != 1 ||
        command_count < 0 || command_count > MAX_COMMANDS)
    {
        printf("잘못된 명령 개수입니다.\n");
        destroy_list(&memory);
        return 0;
    }

    for (i = 0; i < command_count; ++i)
    {
        if (scanf("%15s", command) != 1)
        {
            printf("명령을 읽을 수 없습니다.\n");
            break;
        }

        if (strcmp(command, "ALLOC") == 0)
        {
            if (scanf("%d %d", &pid, &size) != 2)
            {
                printf("ALLOC 명령 형식이 잘못되었습니다.\n");
                break;
            }
            result = allocate_memory(&memory, pid, size);
            printf("ALLOC P%d %d: %s\n",
                   pid, size, result ? "SUCCESS" : "FAIL");
        }
        else if (strcmp(command, "FREE") == 0)
        {
            if (scanf("%d", &pid) != 1)
            {
                printf("FREE 명령 형식이 잘못되었습니다.\n");
                break;
            }
            result = release_memory(&memory, pid);
            printf("FREE P%d: %s\n",
                   pid, result ? "SUCCESS" : "FAIL");
        }
        else
        {
            printf("알 수 없는 명령입니다: %s\n", command);
        }
        print_memory_map(&memory);
    }

    destroy_list(&memory);
    return 0;
}
