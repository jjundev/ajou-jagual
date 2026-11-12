#include <stdio.h>

#define MAX_CHILDREN 3

typedef struct Node
{
    const char *name;
    int is_file; /* 파일 1, 디렉터리 0 */
    int size;    /* 파일 크기. 디렉터리 자체의 크기는 0 */
    int child_count;
    const struct Node *children[MAX_CHILDREN];
} Node;

int calculate_size(const Node *node);
int main(void);

/* 파일이면 크기 반환, 디렉터리이면 자식 용량 합산 */
int calculate_size(const Node *node)
{
    /*
       1. 파일이면 자신의 size를 반환합니다.
       2. 디렉터리이면 모든 자식의 calculate_size 결과를 합산합니다.
       3. 빈 디렉터리의 용량은 0입니다.
       */
    return 0;
}

int main(void)
{
    const Node a = {"a.txt", 1, 10, 0, {NULL}};
    const Node b = {"b.txt", 1, 20, 0, {NULL}};
    const Node c = {"c.txt", 1, 5, 0, {NULL}};
    const Node docs = {"docs", 0, 0, 2, {&a, &b}};
    const Node empty = {"empty", 0, 0, 0, {NULL}};
    const Node root = {"root", 0, 0, 3, {&docs, &c, &empty}};

    puts("root/");
    puts("|-- docs/");
    puts("|   |-- a.txt (10)");
    puts("|   `-- b.txt (20)");
    puts("|-- c.txt (5)");
    puts("`-- empty/");
    printf("TOTAL %d\n", calculate_size(&root));

    return 0;
}
