#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <stdlib.h>

#define MAX_PROCESSES 8
#define MAX_INTERRUPTS 16
#define MAX_STACK_SIZE 16
#define MAX_QUEUE_SIZE (MAX_PROCESSES + 1)

#define QUANTUM 2
#define MAX_DURATION 10
#define MAX_ARRIVAL_TIME 1000
#define MAX_SIMULATION_TICKS \
    (MAX_ARRIVAL_TIME + (MAX_PROCESSES + MAX_INTERRUPTS) * MAX_DURATION)

typedef enum
{
    IDLE,
    PROCESS,
    INTERRUPT
} TaskType;

typedef struct
{
    TaskType kind;
    int id;
    int remaining;
    int quantum_left;
} Context;

const Context IDLE_CONTEXT = {IDLE, 0, 0, 0};

typedef struct
{
    Context queue[MAX_QUEUE_SIZE];
    int front, rear;
} ReadyQueue;

typedef struct
{
    Context stack[MAX_STACK_SIZE];
    int top;
} ContextStack;

typedef struct
{
    ReadyQueue ready;
    ContextStack suspended;
    Context current;
    int tick;
    int finished_processes;
    int finished_interrupts;
} Scheduler;

typedef struct
{
    int arrival_time;
    int id;
    int duration;
} InterruptEvent;

int enqueue(ReadyQueue *q, Context value);
Context dequeue(ReadyQueue *q);
int push(ContextStack *s, Context value);
Context pop(ContextStack *s);
int execute_tick(Scheduler *s);

void select_process(Scheduler *s);
void start_interrupt(Scheduler *s, InterruptEvent event);
void finish_tick(Scheduler *s);

void init_queue(ReadyQueue *q)
{
    q->front = q->rear = 0;
}

int is_empty_queue(const ReadyQueue *q)
{
    return q->front == q->rear;
}

int is_full_queue(const ReadyQueue *q)
{
    return (q->rear + 1) % MAX_QUEUE_SIZE == q->front;
}

int enqueue(ReadyQueue *q, Context value)
{
    if (q == NULL || is_full_queue(q))
    {
        return 0;
    }
    q->rear = (q->rear + 1) % MAX_QUEUE_SIZE;
    q->queue[q->rear] = value;
    return 1;
}

Context dequeue(ReadyQueue *q)
{
    if (q == NULL || is_empty_queue(q))
    {
        printf("QUEUE_ERROR\n");
        exit(1);
    }
    q->front = (q->front + 1) % MAX_QUEUE_SIZE;
    return q->queue[q->front];
}

void init_stack(ContextStack *s)
{
    s->top = -1;
}

int is_empty_stack(const ContextStack *s)
{
    return s->top == -1;
}

int is_full_stack(const ContextStack *s)
{
    return s->top == MAX_STACK_SIZE - 1;
}

int push(ContextStack *s, Context value)
{
    if (s == NULL || is_full_stack(s))
    {
        return 0;
    }
    s->stack[++(s->top)] = value;
    return 1;
}

Context pop(ContextStack *s)
{
    if (s == NULL || is_empty_stack(s))
    {
        printf("STACK_ERROR\n");
        exit(1);
    }
    return s->stack[(s->top)--];
}

void select_process(Scheduler *s)
{
    if (s->current.kind != IDLE || is_empty_queue(&s->ready))
    {
        return;
    }
    s->current = dequeue(&s->ready);
    s->current.quantum_left = QUANTUM;
}

void start_interrupt(Scheduler *s, InterruptEvent event)
{
    if (s->current.kind != IDLE && !push(&s->suspended, s->current))
    {
        printf("SIMULATION_ERROR\n");
        exit(2);
    }
    s->current.kind = INTERRUPT;
    s->current.id = event.id;
    s->current.remaining = event.duration;
    s->current.quantum_left = 0;
}

void finish_tick(Scheduler *s)
{
    Context *current = &s->current;
    if (current->kind == PROCESS)
    {
        if (current->remaining == 0)
        {
            s->finished_processes++;
            *current = IDLE_CONTEXT;
        }
        else if (current->quantum_left == 0)
        {
            if (!enqueue(&s->ready, *current))
            {
                printf("SIMULATION_ERROR\n");
                exit(2);
            }
            *current = IDLE_CONTEXT;
        }
    }
    else if (current->kind == INTERRUPT && current->remaining == 0)
    {
        s->finished_interrupts++;
        if (is_empty_stack(&s->suspended))
        {
            *current = IDLE_CONTEXT;
        }
        else
        {
            *current = pop(&s->suspended);
        }
    }
}

int execute_tick(Scheduler *s)
{
    Context *current = &s->current;
    if ((current->kind != IDLE && current->remaining <= 0) ||
        (current->kind == PROCESS && current->quantum_left <= 0))
    {
        return 0;
    }

    if (current->kind != IDLE)
    {
        current->remaining--;
    }
    s->tick++;
    if (current->kind == PROCESS)
    {
        current->quantum_left--;
        printf("T%3d P%2d R%2d Q%2d\n", s->tick,
               current->id, current->remaining, current->quantum_left);
    }
    else if (current->kind == INTERRUPT)
    {
        printf("T%3d I%2d R%2d\n", s->tick, current->id, current->remaining);
    }
    else
    {
        printf("T%3d IDLE\n", s->tick);
    }
    return 1;
}

int main(void)
{
    Context processes[MAX_PROCESSES] = {0};
    InterruptEvent interrupts[MAX_INTERRUPTS] = {0};
    int process_count, interrupt_count;
    Scheduler s = {0};
    int next_interrupt = 0;

    if (scanf("%d %d", &process_count, &interrupt_count) != 2 ||
        process_count < 1 || process_count > MAX_PROCESSES ||
        interrupt_count < 0 || interrupt_count > MAX_INTERRUPTS)
    {
        printf("INPUT_ERROR\n");
        return 1;
    }

    for (int i = 0; i < process_count; i++)
    {
        if (scanf("%d", &processes[i].remaining) != 1 ||
            processes[i].remaining < 1 || processes[i].remaining > MAX_DURATION)
        {
            printf("INPUT_ERROR\n");
            return 1;
        }
        processes[i].id = i + 1;
        processes[i].kind = PROCESS;
    }

    for (int i = 0; i < interrupt_count; i++)
    {
        if (scanf("%d %d", &interrupts[i].arrival_time,
                  &interrupts[i].duration) != 2 ||
            interrupts[i].arrival_time < 0 || interrupts[i].arrival_time > MAX_ARRIVAL_TIME ||
            interrupts[i].duration < 1 || interrupts[i].duration > MAX_DURATION ||
            (i > 0 && interrupts[i].arrival_time <= interrupts[i - 1].arrival_time))
        {
            printf("INPUT_ERROR\n");
            return 1;
        }
        interrupts[i].id = i + 1;
    }

    init_queue(&s.ready);
    init_stack(&s.suspended);

    for (int i = 0; i < process_count; i++)
    {
        if (!enqueue(&s.ready, processes[i]))
        {
            printf("SIMULATION_ERROR\n");
            return 2;
        }
    }

    while (s.finished_processes < process_count ||
           s.finished_interrupts < interrupt_count)
    {
        if (s.tick >= MAX_SIMULATION_TICKS)
        {
            printf("SIMULATION_ERROR\n");
            return 2;
        }

        if (next_interrupt < interrupt_count &&
            interrupts[next_interrupt].arrival_time == s.tick)
        {
            start_interrupt(&s, interrupts[next_interrupt]);
            next_interrupt++;
        }
        select_process(&s);
        if (!execute_tick(&s))
        {
            printf("SIMULATION_ERROR\n");
            return 2;
        }
        finish_tick(&s);
    }

    printf("FINISHED %d INTERRUPTS %d TICKS %d\n",
           s.finished_processes, s.finished_interrupts, s.tick);
    return 0;
}
