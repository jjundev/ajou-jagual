#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <limits.h>

typedef struct {
    
} Edge;

int find() {
    //코드 작성
}
void unionSet(int a, int b) {
    //코드 작성
}

int compare() {
    //코드 작성
}
void shuffle() {
    //코드 작성
}

int kruskalMST() {
    //코드 작성
}

int primMST() {
    //코드 작성
}


int main() {
   
    printf("정점 수 입력: ");
    scanf("%d", &n);
    printf("간선 수 입력 (최대 %d개): ", n * (n - 1) / 2);
    scanf("%d", &m);

    srand((unsigned int)time(NULL));

    // 동적 메모리 할당
    edges = malloc(sizeof(Edge) * m);
    parent = malloc(sizeof(int) * n);

    adjMatrix = malloc(sizeof(int*) * n);
    used = malloc(sizeof(int*) * n);
    for (int i = 0; i < n; i++) {
        adjMatrix[i] = calloc(n, sizeof(int));
        used[i] = calloc(n, sizeof(int));
    }

    //코드 작성
    
    // 메모리 해제
    for (int i = 0; i < n; i++) {
        free(adjMatrix[i]);
        free(used[i]);
    }
    free(adjMatrix);
    free(used);
    free(edges);
    free(parent);
    free(weights);

    return 0;
}
