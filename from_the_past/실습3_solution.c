#define _CRT_SECURE_NO_WARNINGS
#define _CRT_NONSTDC_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX 100
#define NAME_LEN 100

typedef struct {
    char* data[MAX];
    int top;
} Stack;

void init(Stack* s) {
    s->top = -1;
}

int isEmpty(Stack* s) {
    return s->top == -1;
}

int isFull(Stack* s) {
    return s->top == MAX - 1;
}

void push(Stack* s, const char* str) {
    if (isFull(s)) return;
    s->data[++(s->top)] = _strdup(str);  
}

char* pop(Stack* s) {
    if (isEmpty(s)) return NULL;
    return s->data[(s->top)--];
}

char* peek(Stack* s) {
    if (isEmpty(s)) return NULL;
    return s->data[s->top];
}

void removeNewline(char* str) {
    str[strcspn(str, "\n")] = '\0';
}

int main() {
    Stack backStack, forwardStack;
    init(&backStack);
    init(&forwardStack);

    char current[NAME_LEN] = "Home";
    char command[NAME_LEN], input[NAME_LEN];

    while (1) {
        printf("\n[현재 페이지: %s]\n", current);
        printf("명령어 입력 (visit [page] / back / forward / quit): ");

        if (fgets(command, NAME_LEN, stdin) == NULL) break;
        removeNewline(command);

        if (strncmp(command, "visit", 5) == 0) {
            char* space = strchr(command, ' ');
            if (space != NULL && *(space + 1) != '\0') {
                push(&backStack, current);
                strcpy(current, space + 1);
                init(&forwardStack);
            }
            else {
                printf("페이지 이름을 입력하세요.\n");
            }
        }
        else if (strcmp(command, "back") == 0) {
            if (isEmpty(&backStack)) {
                printf("뒤로 갈 수 없습니다.\n");
            }
            else {
                push(&forwardStack, current);
                char* page = pop(&backStack);
                strcpy(current, page);
                free(page);
            }
        }
        else if (strcmp(command, "forward") == 0) {
            if (isEmpty(&forwardStack)) {
                printf("앞으로 갈 수 없습니다.\n");
            }
            else {
                push(&backStack, current);
                char* page = pop(&forwardStack);
                strcpy(current, page);
                free(page);
            }
        }
        else if (strcmp(command, "quit") == 0) {
            break;
        }
        else {
            printf("잘못된 명령입니다.\n");
        }
    }

    while (!isEmpty(&backStack)) free(pop(&backStack));
    while (!isEmpty(&forwardStack)) free(pop(&forwardStack));

    return 0;
}
