#include <stdio.h>
#include <stdlib.h>
typedef int element;
typedef struct StackNode {
    element item;
    struct StackNode *link;
} StackNode;               /* 강의록 p16 인쇄본은 StackeNode (오타) */
typedef struct {
    StackNode *top;
} LinkedStackType;
/* 검산용 보충: p18이 호출하지만 싣지 않은 is_empty */
int is_empty(LinkedStackType *s)
{
    return (s->top == NULL);
}
// 삽입 함수 (강의록 p17)
void push(LinkedStackType *s, element item)
{
    StackNode *temp=(StackNode *)malloc(sizeof(StackNode));
    if( temp == NULL ){
        fprintf(stderr, "메모리 할당에러
");
        return;
    }
    else{
        temp->item = item;
        temp->link = s->top;
        s->top = temp;
    }
}
// 삭제 함수 (강의록 p18)
element pop(LinkedStackType *s)
{
    if( is_empty(s) ) {
        fprintf(stderr, "스택이 비어있음
");
        exit(1);
    }
    else{
        StackNode *temp=s->top;
        int item = temp->item;
        s->top = s->top->link;
        free(temp);
        return item;
    }
}
/* ---- 이하 검산용 보충: 시작 상태(n=3, 맨 위 30)를 실제 push로 만든 뒤 관찰 호출 ---- */
int main(void)
{
    LinkedStackType s = { NULL };
    push(&s, 10);          /* A */
    push(&s, 20);          /* B */
    push(&s, 30);          /* C */
    int x = pop(&s);       /* 관찰 대상 */
    return 0;
}
