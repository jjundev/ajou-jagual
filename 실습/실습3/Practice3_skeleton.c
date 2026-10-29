#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>

#define MAX_STACK_SIZE 100
#define MAX_EXPRESSION_SIZE 100

typedef struct
{
    char data[MAX_STACK_SIZE];
    int top;
} Stack;

void init_stack(Stack *s);
int is_empty(const Stack *s);
void push(Stack *s, char value);
char pop(Stack *s);
char peek(const Stack *s);
int priority(char op);
void infix_to_postfix(const char infix[], char postfix[]);

void init_stack(Stack *s)
{
    s->top = -1;
}

int is_empty(const Stack *s)
{
    return s->top == -1;
}

void push(Stack *s, char value)
{
    s->data[++s->top] = value;
}

char pop(Stack *s)
{
    return s->data[s->top--];
}

char peek(const Stack *s)
{
    return s->data[s->top];
}

int priority(char op)
{
    if (op == '*' || op == '/')
    {
        return 2;
    }
    return 1;
}

void infix_to_postfix(const char infix[], char postfix[])
{
    Stack s;
    int postfix_index = 0;
    init_stack(&s);

    for (int i = 0; infix[i] != '\0'; i++)
    {
        char token = infix[i];

        if (token >= 'A' && token <= 'Z')
        {
            postfix[postfix_index++] = token;
        }
        else
        {
            /*
             * 스택이 비어 있지 않고, 맨 위 연산자의 우선순위가
             * 현재 연산자보다 높거나 같으면 반복
             */

            while ()
            {
                /* 연산자를 pop하여 postfix의 다음 위치에 저장 */
            }

            /* 현재 연산자 token을 스택에 push */
        }
    }

    while (!is_empty(&s))
    {
        postfix[postfix_index++] = pop(&s);
    }
    postfix[postfix_index] = '\0';
}

int main(void)
{
    char infix[MAX_EXPRESSION_SIZE];
    char postfix[MAX_EXPRESSION_SIZE];

    if (scanf("%s", infix) != 1)
    {
        return 1;
    }

    infix_to_postfix(infix, postfix);
    printf("%s\n", postfix);
    return 0;
}
