#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define SIZE 20
#define WALL 1
#define PATH 0
#define VISITED 2

typedef struct {
    int x, y;
} Point;

typedef struct {
    Point data[SIZE * SIZE];
    int top;
} Stack;

// 기본 맵 설정
int map[SIZE][SIZE] = {
    {4,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0},
    {1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0},
    {1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0},
    {1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0,1,1,1,0},
    {0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0},
    {1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0},
    {1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0},
    {1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0},
    {1,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0},
    {1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,0},
    {1,0,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0},
    {1,0,1,1,1,0,1,0,1,1,1,0,1,1,1,1,1,1,1,0},
    {1,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,0},
    {1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0},
    {1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0},
    {1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,0,1,0},
    {1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0},
    {1,0,1,1,1,0,1,1,1,1,1,1,1,0,1,0,1,0,1,0},
    {1,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0},
    {1,1,1,0,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,3}
};

int visited[SIZE][SIZE];
Point bestPath[SIZE * SIZE];
int bestPathLen = INT_MAX;

int dx[] = { -1, 1, 0, 0 };
int dy[] = { 0, 0, -1, 1 };

void initStack(Stack* s) {
    // 코드 작성
}

void push(Stack* s, Point p) {
    // 코드 작성
}

Point pop(Stack* s) {
    // 코드 작성
}

int isEmpty(Stack* s) {
    // 코드 작성
}

void saveBestPath(Stack* s) {
    // 코드 작성
}

// 방문여부 확인을 통한 최적 경로 탐색
void dfs(Point curr, Point goal, Stack* path) {
   // 코드 작성
}

//맵 상황 출력, 배열 내부 원소 값에 따라 다른 문자열 출력
void printMap() {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (map[i][j] == WALL)
                printf("■ ");
            else if (map[i][j] == VISITED)
                printf(" . ");
            else if (map[i][j] == 4)
                printf(" S ");
            else if (map[i][j] == 3)
                printf(" G ");
            else
                printf("□ ");
        }
        printf("\n");
    }
}

int main() {
    Point start = { 0, 0 };
    Point goal = { 19, 19 };
    printf("지도 표시\n");
    printMap();
    printf("\n");
    printf("\n");

    Stack path;
    initStack(&path);

    dfs(start, goal, &path);

    // 최적 경로 표시
    for (int i = 0; i < bestPathLen; i++) {
        Point p = bestPath[i];
        map[p.x][p.y] = VISITED;
    }

    printf(" 최적 경로 탐색 결과 \n");
    printMap();
    printf("\n 최단 경로 길이: %d 칸\n", bestPathLen);

    return 0;
}
