/*
 * Codex가 작성한 학습용 참고 구현입니다.
 * 제공된 HW2_skeleton.c의 학생 구현 함수 5개를 채웠습니다.
 * 과제 지시문의 본인 구현·작성 조건과 구분해 사용하세요.
 */

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
    MemoryBlock *current;

    if (list == NULL || size <= 0)
    {
        return NULL;
    }

    current = list->head.next;
    while (current != &list->head)
    {
        if (current->pid == FREE_PID && current->size >= size)
        {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

MemoryBlock *find_process_block(MemoryList *list, int pid)
{
    MemoryBlock *current;

    if (list == NULL || pid <= 0)
    {
        return NULL;
    }

    current = list->head.next;
    while (current != &list->head)
    {
        if (current->pid == pid)
        {
            return current;
        }
        current = current->next;
    }
    return NULL;
}

int allocate_memory(MemoryList *list, int pid, int size)
{
    MemoryBlock *block;
    MemoryBlock *remaining;

    if (list == NULL || pid <= 0 || size <= 0)
    {
        return 0;
    }

    if (find_process_block(list, pid) != NULL)
    {
        return 0;
    }

    block = find_first_fit(list, size);
    if (block == NULL)
    {
        return 0;
    }

    if (block->size > size)
    {
        /* 새 노드 생성에 실패해도 기존 리스트는 바뀌지 않도록 먼저 생성한다. */
        remaining = create_block(block->start + size,
                                 block->size - size, FREE_PID);
        if (remaining == NULL)
        {
            return 0;
        }

        block->size = size;
        insert_after(block, remaining);
    }

    block->pid = pid;
    return 1;
}

MemoryBlock *merge_free_blocks(MemoryList *list, MemoryBlock *current)
{
    MemoryBlock *previous;
    MemoryBlock *next;

    if (list == NULL || current == NULL ||
        current == &list->head || current->pid != FREE_PID)
    {
        return current;
    }

    previous = current->prev;
    if (previous != &list->head && previous->pid == FREE_PID)
    {
        previous->size += current->size;
        remove_block(current);
        /* current가 삭제되었으므로 살아 있는 이전 노드를 기준으로 바꾼다. */
        current = previous;
    }

    next = current->next;
    if (next != &list->head && next->pid == FREE_PID)
    {
        current->size += next->size;
        remove_block(next);
    }

    return current;
}

int release_memory(MemoryList *list, int pid)
{
    MemoryBlock *block;

    block = find_process_block(list, pid);
    if (block == NULL)
    {
        return 0;
    }

    block->pid = FREE_PID;
    merge_free_blocks(list, block);
    return 1;
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
