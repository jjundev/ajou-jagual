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
/* ---- 이하 검산용 보충: 시나리오 시작 상태(n=3: C→B→A)를 실제 push로 만든 뒤 관찰 호출 ---- */
int main(void)
{
    LinkedStackType s = { NULL };
    push(&s, 10);          /* A */
    push(&s, 20);          /* B */
    push(&s, 30);          /* C */
    push(&s, 40);          /* 관찰 대상: D */
    return 0;
}
