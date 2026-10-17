/* C11 harness: adds declarations, headers, renamed functions and assertions.
   Slide excerpts stay unchanged in lecture PDFs. Undefined examples are NOT run. */
#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct Node {int data; struct Node *link;} Node;
typedef struct DNode {int data;struct DNode *llink,*rlink;} DNode;
typedef struct {DNode *head,*tail;} Deque;
static int fib3calls;
static int fib(int n){if(n==3)fib3calls++;if(n<2)return n;return fib(n-1)+fib(n-2);}
static int factorial(int n){if(n<=1)return 1;return n*factorial(n-1);}
static double power(double x,int n){if(n==0)return 1;if(n%2==0)return power(x*x,n/2);return x*power(x*x,(n-1)/2);}
static void swap(int *a,int *b){int t=*a;*a=*b;*b=t;}
static int max_score(const int *a,int n){int t=a[0];for(int i=1;i<n;i++)if(a[i]>t)t=a[i];return t;}
static Node *node(int data){Node *n=malloc(sizeof *n);assert(n);n->data=data;n->link=NULL;return n;}
static void insert(Node **head,Node *p,Node *n){if(*head==NULL){n->link=NULL;*head=n;}else if(p==NULL){n->link=*head;*head=n;}else{n->link=p->link;p->link=n;}}
static void remove_node(Node **head,Node *p,Node *removed){if(p==NULL)*head=(*head)->link;else p->link=removed->link;free(removed);}
static Node *reverse(Node *head){Node *p=head,*q=NULL,*r;while(p!=NULL){r=q;q=p;p=p->link;q->link=r;}return q;}
static Node *concat(Node *a,Node *b){if(!a)return b;if(!b)return a;Node *p=a;while(p->link)p=p->link;p->link=b;return a;}
static void circular_last(Node **head,Node *n){if(!*head){*head=n;n->link=n;}else{n->link=(*head)->link;(*head)->link=n;*head=n;}}
static void dinsert(DNode *a,DNode *n){n->llink=a;n->rlink=a->rlink;a->rlink->llink=n;a->rlink=n;}
static void dremove(DNode *n){n->llink->rlink=n->rlink;n->rlink->llink=n->llink;}
static DNode *dnode(DNode *l,int item,DNode *r){DNode *n=malloc(sizeof *n);assert(n);n->llink=l;n->data=item;n->rlink=r;return n;}
static void add_rear(Deque *dq,int item){DNode *n=dnode(dq->tail,item,NULL);if(!dq->head)dq->head=n;else dq->tail->rlink=n;dq->tail=n;}
static int delete_front(Deque *dq){assert(dq->head);DNode *n=dq->head;int item=n->data;dq->head=n->rlink;free(n);if(!dq->head)dq->tail=NULL;else dq->head->llink=NULL;return item;}
static char hanoi_trace[128];static int hpos;
static void hanoi(int n,char from,char tmp,char to){if(n>1)hanoi(n-1,from,to,tmp);hpos+=snprintf(hanoi_trace+hpos,sizeof hanoi_trace-(size_t)hpos,"%d%c%c ",n,from,to);if(n>1)hanoi(n-1,tmp,from,to);}
int main(void){
 int score[]={-8,-3,-10,-1};assert(max_score(score,4)==-1);
 assert(factorial(0)==1&&factorial(3)==6);assert(power(2,5)==32);assert(fib(6)==8&&fib3calls==3);
 int last=0,current=1;for(int i=2;i<=6;i++){int tmp=current;current+=last;last=tmp;}assert(current==8);
 hanoi(3,'A','B','C');assert(strcmp(hanoi_trace,"1AC 2AB 1CB 3AC 1BA 2BC 1AC ")==0);
 int a=1,b=2;swap(&a,&b);assert(a==2&&b==1);
 struct Example {int number;char name[10];};struct Example *p=malloc(2*sizeof *p);assert(p);p->number=1;strcpy(p->name,"Park");(p+1)->number=2;strcpy((p+1)->name,"Kim");assert(p[0].number==1&&p[1].number==2&&strcmp(p[1].name,"Kim")==0);assert((char *)(p+1)-(char *)p==(int)sizeof *p);free(p);
 int values[8]={10,20,30,40},len=4;
 for(int i=len-1;i>=1;i--)values[i+1]=values[i];values[1]=99;len++;int expected[]={10,99,20,30,40};assert(memcmp(values,expected,sizeof expected)==0&&len==5);
 int deleted=values[1];for(int i=1;i<len-1;i++)values[i]=values[i+1];len--;assert(deleted==99&&len==4&&values[1]==20);
 Node *head=NULL,*n=node(1);insert(&head,NULL,n);assert(head==n&&!n->link);Node *second=node(2);insert(&head,n,second);Node *first=node(0);insert(&head,NULL,first);assert(head==first&&first->link==n&&n->link==second);
 remove_node(&head,n,second);assert(!n->link);remove_node(&head,NULL,first);assert(head==n);remove_node(&head,NULL,n);assert(!head);
 Node *x=node(1),*y=node(2),*z=node(3);x->link=y;y->link=z;head=reverse(x);assert(head==z&&z->link==y&&y->link==x&&!x->link);assert(reverse(NULL)==NULL);
 Node *w=node(4);assert(concat(head,w)==z&&x->link==w);assert(concat(NULL,head)==head);free(z);free(y);free(x);free(w);
 x=node(1);y=node(2);x->link=y;y->link=x;head=y;z=node(3);circular_last(&head,z);assert(head==z&&z->link==x&&y->link==z);free(x);free(y);free(z);
 DNode da={1,NULL,NULL},db={2,NULL,NULL},dn={3,NULL,NULL};da.rlink=&db;db.llink=&da;db.rlink=&da;da.llink=&db;dinsert(&da,&dn);assert(dn.llink==&da&&dn.rlink==&db&&db.llink==&dn&&da.rlink==&dn);dremove(&dn);assert(da.rlink==&db&&db.llink==&da);
 Deque dq={0};add_rear(&dq,1);assert(dq.head==dq.tail&&!dq.head->llink&&!dq.head->rlink);add_rear(&dq,2);assert(dq.head->rlink==dq.tail&&dq.tail->llink==dq.head);assert(delete_front(&dq)==1&&dq.head==dq.tail&&!dq.head->llink);assert(delete_front(&dq)==2&&!dq.head&&!dq.tail);
 int stack[5],top=-1;stack[++top]=5;stack[++top]=8;assert(stack[top]==8&&top==1);assert(stack[top--]==8);stack[++top]=2;assert(stack[top--]==2&&top==0&&stack[0]==5);
 int qs[5]={2,3,0,0,1},front=3,rear=1;front=(front+1)%5;assert(qs[front]==1);rear=(rear+1)%5;qs[rear]=4;rear=(rear+1)%5;qs[rear]=5;assert(front==4&&rear==3&&(rear+1)%5==front);
 unsigned int ua=INT_MAX,ub=1;int capped=ua>(unsigned int)INT_MAX-ub?INT_MAX:(int)(ua+ub);assert(capped==INT_MAX);
 int matrix[3][3]={{2,3,0},{8,9,1},{7,0,5}},terms=0;for(int i=0;i<3;i++)for(int j=0;j<3;j++)if(matrix[i][j])terms++;assert(terms==7&&terms*3>9);
 puts("C11: numeric recursion, Hanoi, swap/malloc, array/list/circular/double links, deque boundaries, stack and circular queue assertions passed");
 return 0;
}
