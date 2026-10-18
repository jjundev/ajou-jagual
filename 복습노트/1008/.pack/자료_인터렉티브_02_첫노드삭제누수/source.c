#include <stdio.h>
#include <stdlib.h>
typedef int element;
typedef struct ListNode {
    element data;
    struct ListNode *link;
} ListNode;
typedef struct {
    ListNode *head;
    int length;
} ListType;
// phead : 헤드 포인터에 대한 포인터
// p: 삭제될 노드의 선행 노드
// removed: 삭제될 노드
void remove_node(ListNode **phead, ListNode *p, ListNode *removed)
{
    if( p == NULL )
        *phead = (*phead)->link;
    else
        p->link = removed->link;
    free(removed);
}
int is_empty(ListType *list)
{
    if( list->head == NULL ) return 1;
    else return 0;
}
// 리스트안에서 pos 위치의 노드를 반환한다.
ListNode *get_node_at(ListType *list, int pos)
{
    int i;
    ListNode *tmp_node = list->head;
    if( pos < 0 ) return NULL;
    for (i=0; i<pos; i++)
        tmp_node = tmp_node->link;
    return tmp_node;
}
// 주어진 위치의 데이터를 삭제한다.
void delete(ListType *list, int pos)
{
    if (!is_empty(list) && (pos >= 0) && (pos < list->length)){
        ListNode *p = get_node_at(list, pos-1);
        remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
        list->length--;
    }
}
int main(void)
{
    ListType list1;
    /* 검산용 보충: 아래 줄은 화면의 준비된 list1(10 → 20 → 30, length 3)을 실제 C로 만든다. */
    ListNode *n3 = malloc(sizeof(ListNode)), *n2 = malloc(sizeof(ListNode)), *n1 = malloc(sizeof(ListNode));
    n3->data = 30; n3->link = NULL; n2->data = 20; n2->link = n3; n1->data = 10; n1->link = n2;
    list1.head = n1; list1.length = 3;
    delete(&list1, 0);
    return 0;
}
