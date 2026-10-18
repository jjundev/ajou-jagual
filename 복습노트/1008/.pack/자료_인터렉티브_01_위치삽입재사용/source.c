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
void error(char *message) { fprintf(stderr, "%s\n", message); exit(1); }
// phead: 리스트의 헤드 포인터의 포인터
// p : 선행 노드
// new_node : 삽입될 노드
void insert_node(ListNode **phead, ListNode *p, ListNode *new_node)
{
    if( *phead == NULL ){        // 공백리스트인 경우
        new_node->link = NULL;
        *phead = new_node;
    }
    else if( p == NULL ){ // p가 NULL이면 첫번째 노드로 삽입
        new_node->link = *phead;
        *phead = new_node;
    }
    else {                       // p 다음에 삽입
        new_node->link = p->link;
        p->link = new_node;
    }
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
// 주어진 위치에 데이터를 삽입한다.
void add(ListType *list, int position, element data)
{
    ListNode *p;
    if ((position >= 0) && (position <= list->length)){
        ListNode *node = (ListNode *)malloc(sizeof(ListNode));
        if( node == NULL ) error("메모리 할당에러");
        node->data = data;
        p = get_node_at(list, position-1);
        insert_node(&(list->head), p, node);
        list->length++;
    }
}
int main(void)
{
    ListType list1;
    /* 검산용 보충: 아래 줄은 화면의 준비된 list1(10 → 20 → 30, length 3)을 실제 C로 만든다. */
    ListNode *n3 = malloc(sizeof(ListNode)), *n2 = malloc(sizeof(ListNode)), *n1 = malloc(sizeof(ListNode));
    n3->data = 30; n3->link = NULL; n2->data = 20; n2->link = n3; n1->data = 10; n1->link = n2;
    list1.head = n1; list1.length = 3;
    add(&list1, 1, 15);
    return 0;
}
