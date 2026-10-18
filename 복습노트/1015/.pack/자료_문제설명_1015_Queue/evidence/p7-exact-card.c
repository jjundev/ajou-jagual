#include <stdio.h>
#define CAP 256
typedef struct { int a[CAP], top; } Stack;
typedef struct { Stack in, out; } TwoStackQueue;
/* 두 top은 0으로 초기화해 사용해요. 1은 성공, 0은 실패예요. */
int enqueue(TwoStackQueue *q, int value) {
    if (q->in.top + q->out.top >= CAP) return 0;
    q->in.a[q->in.top++] = value;
    return 1;
}
int dequeue(TwoStackQueue *q, int *value) {
    if (q->out.top == 0) {
        while (q->in.top > 0)
            q->out.a[q->out.top++] = q->in.a[--q->in.top];
    }
    if (q->out.top == 0) return 0;
    *value = q->out.a[--q->out.top];
    return 1;
}

#include <stdio.h>
int main(void) {
    TwoStackQueue q = {0};
    int out = 777;
    int empty_result = dequeue(&q, &out); printf("empty=%d,out=%d\n", empty_result, out);
    enqueue(&q, 10); enqueue(&q, 20); enqueue(&q, 30);
    dequeue(&q, &out); printf("first=%d\n", out);
    enqueue(&q, 40);
    dequeue(&q, &out); printf("second=%d\n", out);
    dequeue(&q, &out); printf("third=%d\n", out);
    dequeue(&q, &out); printf("fourth=%d\n", out);
    for (int i = 0; i < CAP; ++i) enqueue(&q, i);
    printf("full=%d\n", enqueue(&q, 999));
    return 0;
}
