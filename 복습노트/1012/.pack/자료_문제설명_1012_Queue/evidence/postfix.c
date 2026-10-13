#include <stdio.h>
#include <stdlib.h>
#define MAX_STACK_SIZE 100
typedef int element;
typedef struct {element stack[MAX_STACK_SIZE];int top;} StackType;
void init(StackType*s){s->top=-1;}
int is_empty(StackType*s){return s->top==-1;}
int is_full(StackType*s){return s->top==MAX_STACK_SIZE-1;}
void push(StackType*s,element item){if(is_full(s))exit(1);s->stack[++s->top]=item;}
element pop(StackType*s){if(is_empty(s))exit(1);element item=s->stack[s->top--];return item;}
int main(void){char str[100];StackType s;init(&s);if(scanf("%99s",str)!=1)return 1;
for(int i=0;str[i];++i){if(str[i]=='+'||str[i]=='*'){int op2=pop(&s),op1=pop(&s);if(str[i]=='+')push(&s,op1+op2);else push(&s,op1*op2);}else if(str[i]>='0'&&str[i]<='9')push(&s,str[i]-'0');else return 1;}
if(s.top!=0)return 1;printf("%d",pop(&s));return 0;}
