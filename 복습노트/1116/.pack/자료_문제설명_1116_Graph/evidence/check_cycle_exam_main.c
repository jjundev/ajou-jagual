/* p3: 문제의 main 그대로 + 설명의 check_cycle */
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

int main(){
    int i, n;
    int adj_matrix[6][6] = {
    { 0, 0, 1, 0, 1, 0 },
    { 0, 0, 1, 0, 0, 0 },
    { 1, 1, 0, 1, 1, 0 },
    { 0, 0, 1, 0, 1, 1 },
    { 1, 0, 1, 1, 0, 0 },
    { 0, 0, 0, 1, 0, 0 } };

    if ( check_cycle(adj_matrix, "0240") == 'y' )
        printf("Cycle?: Yes");
    else
        printf("Cycle?: No");

    return 0;
}
