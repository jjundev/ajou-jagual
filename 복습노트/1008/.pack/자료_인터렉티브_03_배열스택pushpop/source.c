#include <stdio.h>
#include <stdlib.h>
#define MAX_STACK_SIZE 5
typedef int element;
typedef struct {
    element stack[MAX_STACK_SIZE];
    int top;
} StackType;
// 공백 상태 검출 함수
int is_empty(StackType *s)
{
    return (s->top == -1);
}
// 포화 상태 검출 함수
int is_full(StackType *s)
{
    return (s->top == (MAX_STACK_SIZE-1));
}
// 삽입함수
void push(StackType *s, element item)
{
    if( is_full(s) ) {
        fprintf(stderr,"스택 포화 에러\n");
        return;
    }
    else s->stack[++(s->top)] = item;
}
// 삭제함수
element pop(StackType *s)
{
    if( is_empty(s) ) {
        fprintf(stderr, "스택 공백 에러\n");
        exit(1);
    }
    else return s->stack[(s->top)--];
}
int main(void)
{
    StackType s;
    /* 검산용 보충: 아래 줄은 화면의 준비된 s(10, 20, top 1)를 실제 C로 만든다. */
    s.top = -1; s.stack[++s.top] = 10; s.stack[++s.top] = 20;
    push(&s, 5);
    return 0;
}
