#include <stdio.h>

#define MAX_SIZE 100

int heap[MAX_SIZE];
int size = 0;

void swap() {
    
}

void insert() {
 
}

void heapify() {
 
}

void heapSort() {
  
}

int main() {
    int n, val;
    printf("입력할 숫자의 개수: ");
    scanf("%d", &n);

    printf("숫자를 입력하세요: ");
    for (int i = 0; i < n; i++) {
        scanf("%d", &val);
        insert(val);
    }

    heapSort();

    printf("오름차순 정렬 결과: ");
    for (int i = 0; i < n; i++) {
        printf("%d ", heap[i]);
    }

    return 0;
}
