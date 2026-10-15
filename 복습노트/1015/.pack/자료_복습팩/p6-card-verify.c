#define MAX_QUEUE_SIZE 8
typedef struct {
    int front;
    int rear;
} QueueType;

int get_count(const QueueType *q) {
    return (q->rear - q->front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE;
}
#include <assert.h>
int main(void){QueueType q={3,5};assert(get_count(&q)==2);q.front=7;q.rear=1;assert(get_count(&q)==2);return 0;}