/* p3 독립 검산: 설명의 check_cycle(정점 반복까지 검사)과
   원본 모범답안(model_check_cycle, 간선 반복만 검사)을 같은 입력에 돌린다.
   입력 가정: path는 '0'~'5' 숫자로만 된 문자열(널 종료). */
#include <stdio.h>
#include <string.h>

char check_cycle(int adj_matrix[6][6], char *path) {
    int len, i, s, e;
    int used_edge[6][6] = { 0 };
    int seen[6] = { 0 };

    len = (int)strlen(path);
    if (len < 4 || path[0] != path[len - 1])
        return 'n';

    for (i = 0; i < len - 1; i++) {
        s = path[i] - '0';
        e = path[i + 1] - '0';
        if (adj_matrix[s][e] != 1) return 'n';
        if (used_edge[s][e] == 1)  return 'n';
        used_edge[s][e] = used_edge[e][s] = 1;
        if (seen[s] == 1)          return 'n';
        seen[s] = 1;
    }
    return 'y';
}

/* 2017 기말 8번 원본 답 (빈 문자열은 path[-1] 접근이라 호출하지 않는다) */
char model_check_cycle(int adj_matrix[6][6], char *path) {
    int len, i, snode, enode;
    int a_m[6][6] = { 0 };
    len = strlen(path);
    if (path[0] != path[len - 1]) return 'n';
    for (i = 0; i < len - 1; i++) {
        snode = path[i] - '0';
        enode = path[i + 1] - '0';
        if (adj_matrix[snode][enode] != 1) return 'n';
        if (a_m[snode][enode] == 1) return 'n';
        else if (a_m[enode][snode] == 1) return 'n';
        else { a_m[snode][enode] = 1; a_m[enode][snode] = 1; }
    }
    return 'y';
}

int main(void) {
    int adj_matrix[6][6] = {
    { 0, 0, 1, 0, 1, 0 },
    { 0, 0, 1, 0, 0, 0 },
    { 1, 1, 0, 1, 1, 0 },
    { 0, 0, 1, 0, 1, 1 },
    { 1, 0, 1, 1, 0, 0 },
    { 0, 0, 0, 1, 0, 0 } };
    /* 두 삼각형 0-1-2, 0-3-4가 정점 0에서만 만나는 나비 모양 그래프 */
    int bowtie[6][6] = {
    { 0, 1, 1, 1, 1, 0 },
    { 1, 0, 1, 0, 0, 0 },
    { 1, 1, 0, 0, 0, 0 },
    { 1, 0, 0, 0, 1, 0 },
    { 1, 0, 0, 1, 0, 0 },
    { 0, 0, 0, 0, 0, 0 } };
    char line[64];

    if (check_cycle(adj_matrix, "0240") == 'y') printf("Cycle?: Yes\n");
    else printf("Cycle?: No\n");
    printf("model main: %s\n", model_check_cycle(adj_matrix, "0240") == 'y' ? "Cycle?: Yes" : "Cycle?: No");
    printf("bowtie 0120340: mine=%c model=%c\n",
           check_cycle(bowtie, "0120340"), model_check_cycle(bowtie, "0120340"));
    /* 표준입력의 각 줄(경로)에 대해: 경로 mine model */
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = '\0';
        if (line[0] == '\0') continue;
        printf("%s %c %c\n", line, check_cycle(adj_matrix, line), model_check_cycle(adj_matrix, line));
    }
    return 0;
}
