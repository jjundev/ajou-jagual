#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define MAX_STACK_SIZE 100

typedef int element;
typedef struct {
	element stack[MAX_STACK_SIZE];
	int top;
} StackType;

void init(StackType *s){       // 스택초기화함수
	s->top = -1;
}

int is_empty(StackType *s){   // 공백상태검출함수
	return (s->top == -1);
}

int is_full(StackType *s){    // 포화상태검출함수
	return (s->top == (MAX_STACK_SIZE - 1));
}

void push(StackType *s, element item){
	if (is_full(s)) {
		fprintf(stderr, "스택 포화 에러\n");
	} else {
s->top = s->top + 1;
s->stack[s->top] = item;

	}
}
element pop(StackType *s) {
	element item;

	if (is_empty(s)) {
		fprintf(stderr, "스택 공백 에러\n");
	}
	else {
item = s->stack[s->top];
s->top = s->top - 1;
return item;
	}
}
int main(){
	char str[100];
	int i, len, op1, op2;

	StackType s;

	init(&s);
	printf("input postfix equation using 0~9,+,*:");
	scanf("%s", str);
	len = strlen(str);


	for (i = 0; i < len; i++){
if (str[i] == '+') {
    op1 = pop(&s);
    op2 = pop(&s);
    push(&s, op1 + op2);
} else if (str[i] == '*') {
    op1 = pop(&s);
    op2 = pop(&s);
    push(&s, op1 * op2);
} else {
    push(&s, str[i] - '0');
}
	} // end of for
	printf("result:%d", pop(&s));
	return 0;
}