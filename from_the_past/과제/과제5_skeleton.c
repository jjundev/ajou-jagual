#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <string.h>

#define MAX_TASKS 100

typedef struct {
    char name[50];
    int priority;
} Task;

Task heap[MAX_TASKS];
int size = 0;

void swap() {
 // 코드 작성
}

void enqueue() {
    // 코드 작성
}

Task dequeue() {

    // 코드 작성
}

// 트리 시각화 함수 
void printHeapTreeEdgesOnly() {
    if (index >= size) return;

    printf("%s", prefix);
    if (index != 0) printf("└── ");
    printf("(%s:%d)\n", heap[index].name, heap[index].priority);

    // 코드 작성
}

void printHeapTree() {
    // 코드 작성
}

int main() {
    enqueue("Task A", 3);
    enqueue("Task B", 1);
    enqueue("Task C", 4);
    enqueue("Task D", 2);
    enqueue("Task E", 5);
    enqueue("Task F", 6);
    enqueue("Task G", 7);

    printHeapTree();

    printf("\n[ 작업 처리 순서 ]\n");
    while (size > 0) {
        Task t = dequeue();
        printf("→ 처리된 작업: %s (우선순위 %d)\n", t.name, t.priority);
        printHeapTree();
    }

    return 0;
}
