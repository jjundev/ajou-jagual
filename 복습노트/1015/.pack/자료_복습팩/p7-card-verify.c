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
#include <assert.h>
int main(void){TwoStackQueue q={0};int v=-1;assert(!dequeue(&q,&v)&&v==-1);assert(enqueue(&q,10));assert(enqueue(&q,20));assert(dequeue(&q,&v)&&v==10);assert(enqueue(&q,30));assert(dequeue(&q,&v)&&v==20);assert(dequeue(&q,&v)&&v==30);assert(!dequeue(&q,&v));return 0;}