#include <assert.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

/* Standalone C11 harness: declarations/main/asserts are added for execution. */
#define MAX_LIST_SIZE 3
typedef struct { int list[MAX_LIST_SIZE]; int length; } ArrayListType;
void init(ArrayListType *L) { L->length=0; }
int is_empty(ArrayListType *L) { return L->length==0; }
int is_full(ArrayListType *L) { return L->length==MAX_LIST_SIZE; }
typedef struct ListNode { int data; struct ListNode *link; } ListNode;
void display_recur(ListNode *head) {
    ListNode *p=head;
    if(p!=NULL) { printf("%d->",p->data); display_recur(p->link); }
}
ListNode *search(ListNode *head,int x) {
    ListNode *p=head;
    while(p!=NULL) { if(p->data==x) return p; p=p->link; }
    return p;
}
typedef struct { char name[10]; int age; float height; } person;
int main(void) {
    int a[]={10,20,30}; int *p=a; int **pp=&p;
    int x=*p++;
    assert(x==10 && p==a+1 && a[1]==20);
    int y=(*p)++;
    assert(y==20 && p==a+1 && a[1]==21);
    **pp=40;
    assert(a[0]==10 && a[1]==40 && a[2]==30);
    assert((char *)p-(char *)a==(ptrdiff_t)sizeof(int));
    assert(sizeof(unsigned int)==sizeof(int));
    person original={"A",20,1.75f},copy=original;
    copy.age=21;copy.name[0]='B';
    assert(original.age==20 && strcmp(original.name,"A")==0);
    ArrayListType L={{7,8,9},3}; init(&L);
    assert(L.length==0 && is_empty(&L)==1 && is_full(&L)==0);
    assert(L.list[0]==7 && L.list[1]==8 && L.list[2]==9);
    for(int n=0;n<=MAX_LIST_SIZE;n++) {
        L.length=n; assert(is_empty(&L)==(n==0));
        assert(is_full(&L)==(n==MAX_LIST_SIZE));
    }
    ListNode C={30,NULL},B={20,&C},A={10,&B};
    assert(search(&A,20)==&B && search(&A,99)==NULL);
    assert(search(NULL,20)==NULL);
    display_recur(&A); puts(""); display_recur(NULL);
    assert(A.link==&B && B.link==&C && C.link==NULL);
    puts("PASS: pointer expressions, struct/array-member copy, int/unsigned size, logical array state, recursive visit and search.");
    return 0;
}
