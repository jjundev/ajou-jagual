#include <stdio.h>
#include <stdlib.h>
#define MAX_STACK_SIZE 5   /* 검산용 보충: 강의록은 값을 정하지 않음 */
typedef int element;
typedef struct {
    element stack[MAX_STACK_SIZE];
    int top;
} StackType;
// 스택 초기화 함수 (강의록 p13)
void init(StackType *s)
{
    s->top = -1;
}
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
// 삽입 함수 (강의록 p14)
void push(StackType *s, element item)
{
    if( is_full(s) ) {
        fprintf(stderr,"스택 포화 에러
");
        return;
    }
    else s->stack[++(s->top)] = item;
}
// 삭제 함수
element pop(StackType *s)
{
    if( is_empty(s) ) {
        fprintf(stderr, "스택 공백 에러
");
        exit(1);
    }
    else return s->stack[(s->top)--];
}
// 피크 함수
element peek(StackType *s)
{
    if( is_empty(s) ) {
        fprintf(stderr, "스택 공백 에러
");
        exit(1);
    }
    else return s->stack[s->top];
}
/* ---- 이하 검산용 보충: 시작 상태(n=2: [7, 9])를 init·push로 만든 뒤 관찰 호출 ---- */
int main(void)
{
    StackType s;
    init(&s);
    push(&s, 7);
    push(&s, 9);
    push(&s, 4);           /* 관찰 대상 */
    int x = pop(&s);       /* 관찰 대상 */
    return 0;
}
