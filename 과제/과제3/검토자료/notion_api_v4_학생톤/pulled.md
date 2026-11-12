<table_of_contents color="gray"/>
<empty-block/>
# 구현 목적
CPU 하나가 프로세스 여러 개를 2 tick씩 돌아가며 실행하다가, 인터럽트가 오면 하던 일을 멈추고 인터럽트부터 처리하는 과정을 큐와 스택으로 구현하는 과제이다.
<empty-block/>
<empty-block/>
# 소스코드 분석
뼈대 코드에서 내가 채운 함수는 select_process, start_interrupt, finish_tick 세 개이고, 나머지는 주어진 코드를 그대로 썼다.
## 헤더·매크로·구조체·함수 원형
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>#define _CRT_SECURE_NO_WARNINGS<br><br>#include \<stdio.h\><br>#include \<stdlib.h\><br><br>#define MAX_PROCESSES 8<br>#define MAX_INTERRUPTS 16<br>#define MAX_STACK_SIZE 16<br>#define MAX_QUEUE_SIZE (MAX_PROCESSES + 1)<br><br>#define QUANTUM 2<br>#define MAX_DURATION 10<br>#define MAX_ARRIVAL_TIME 1000<br>#define MAX_SIMULATION_TICKS \\<br>    (MAX_ARRIVAL_TIME + (MAX_PROCESSES + MAX_INTERRUPTS) \* MAX_DURATION)</td>
<td>#기능 명세<br>• _CRT_SECURE_NO_WARNINGS: MSVC가 scanf에 내는 보안 경고를 끈다.<br>• stdio.h: scanf·printf, stdlib.h: 오류 시 종료하는 exit 호출을 위해 포함한다.<br>• MAX_PROCESSES(8)·MAX_INTERRUPTS(16): 입력 개수 상한, MAX_STACK_SIZE(16): 중단 문맥을 저장할 칸 수<br>• QUANTUM(2): 한 번 배정받아 연속 실행할 수 있는 최대 tick<br>• MAX_DURATION(10)·MAX_ARRIVAL_TIME(1000): 실행 시간과 인터럽트 도착 시각의 상한<br><br>#분석<br>• MAX_QUEUE_SIZE = 8 + 1: 큐 크기가 8이 아니라 9인 것은 수업에서 배운 원형 큐가 한 칸을 비워 두기 때문이다. 그래서 프로세스 8개를 넣으려면 9칸이 있어야 한다.<br>• MAX_SIMULATION_TICKS = 1000 + (8 + 16) × 10 = 1240: 계산하면 1240이다. 입력이 정상이면 이보다 오래 걸릴 수 없으므로 무한 반복을 막는 값이라고 이해했다.</td>
</tr>
<tr>
<td>typedef enum<br>\{<br>    IDLE,<br>    PROCESS,<br>    INTERRUPT<br>\} TaskType;<br><br>typedef struct<br>\{<br>    TaskType kind;<br>    int id;<br>    int remaining;<br>    int quantum_left;<br>\} Context;<br><br>const Context IDLE_CONTEXT = \{IDLE, 0, 0, 0\};</td>
<td>#기능 명세<br>• TaskType: CPU가 하는 일의 종류. IDLE(실행할 작업 없음), PROCESS(라운드로빈 대상 프로세스), INTERRUPT(인터럽트 처리)<br>• Context: 작업 하나의 문맥. kind(종류), id(입력 순서 번호), remaining(남은 실행 시간), quantum_left(이번 배정에서 남은 할당 시간)<br>• IDLE_CONTEXT: 모든 값이 0인 IDLE 문맥으로, CPU를 비울 때 current에 대입한다.<br><br>#분석<br>• Context에는 종류, 번호, 남은 시간, 남은 퀀텀이 들어 있다. 큐나 스택에 넣을 때는 포인터가 아니라 구조체를 통째로 복사한다.<br>• 인터럽트는 라운드로빈 대상이 아니므로 quantum_left를 0으로 둔다.<br>• IDLE이 열거형의 첫 값(0)이라, 0으로 초기화한 Context는 IDLE_CONTEXT와 같다.</td>
</tr>
<tr>
<td>typedef struct<br>\{<br>    Context queue\[MAX_QUEUE_SIZE\];<br>    int front, rear;<br>\} ReadyQueue;<br><br>typedef struct<br>\{<br>    Context stack\[MAX_STACK_SIZE\];<br>    int top;<br>\} ContextStack;</td>
<td>#기능 명세<br>• ReadyQueue: CPU를 기다리는 프로세스의 원형 큐. front는 첫 원소 바로 앞 칸, rear는 마지막 원소가 있는 칸<br>• ContextStack: 인터럽트로 중단된 문맥의 스택. top은 가장 최근에 넣은 칸의 인덱스이고, 비어 있으면 -1<br><br>#분석<br>• 큐는 선입선출(FIFO)이므로 퀀텀을 다 쓴 프로세스를 뒤에 넣으면 나머지 프로세스가 한 번씩 돈 뒤에 차례가 다시 온다.<br>• 스택은 후입선출(LIFO)이므로 인터럽트가 겹쳐도 가장 나중에 멈춘 작업부터 재개된다.</td>
</tr>
<tr>
<td>typedef struct<br>\{<br>    ReadyQueue ready;<br>    ContextStack suspended;<br>    Context current;<br>    int tick;<br>    int finished_processes;<br>    int finished_interrupts;<br>\} Scheduler;<br><br>typedef struct<br>\{<br>    int arrival_time;<br>    int id;<br>    int duration;<br>\} InterruptEvent;</td>
<td>#기능 명세<br>• Scheduler: 시뮬레이션 상태 전체. ready(준비 큐), suspended(중단 문맥 스택), current(실행 중인 문맥), tick(현재 시각), finished_processes·finished_interrupts(완료 수, main의 반복 종료 조건)<br>• InterruptEvent: 미리 입력받은 인터럽트 정보. arrival_time(도착 시각), id, duration(처리 시간)<br><br>#분석<br>• current는 포인터가 아닌 값이므로, 큐에서 꺼내거나 스택에서 복원한 문맥은 current로 복사된다.<br>• 도착 시각이 되면 start_interrupt가 InterruptEvent로 INTERRUPT 문맥을 만든다.</td>
</tr>
<tr>
<td>int enqueue(ReadyQueue \*q, Context value);<br>Context dequeue(ReadyQueue \*q);<br>int push(ContextStack \*s, Context value);<br>Context pop(ContextStack \*s);<br>int execute_tick(Scheduler \*s);<br><br>void select_process(Scheduler \*s);<br>void start_interrupt(Scheduler \*s, InterruptEvent event);<br>void finish_tick(Scheduler \*s);</td>
<td>#기능 명세<br>• 위의 다섯 개는 주어진 함수이고 아래 세 개가 내가 구현한 함수의 원형이다.</td>
</tr>
</table>
<empty-block/>
## init_queue
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void init_queue(ReadyQueue \*q)<br>\{<br>    q-\>front = q-\>rear = 0;<br>\}</td>
<td>#기능 명세<br>• front = rear = 0으로 빈 큐를 만든다. 이 큐에서는 front == rear가 빈 상태다.</td>
</tr>
</table>
<empty-block/>
## is_empty_queue
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_empty_queue(const ReadyQueue \*q)<br>\{<br>    return q-\>front == q-\>rear;<br>\}</td>
<td>#기능 명세<br>• front == rear이면 꺼낼 원소가 없으므로 1, 아니면 0을 반환한다.</td>
</tr>
</table>
<empty-block/>
## is_full_queue
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_full_queue(const ReadyQueue \*q)<br>\{<br>    return (q-\>rear + 1) % MAX_QUEUE_SIZE == q-\>front;<br>\}</td>
<td>#기능 명세<br>• rear의 다음 칸이 front이면 가득 찬 것으로 보고 1을 반환한다.<br><br>#분석<br>• 9칸을 다 채우면 front와 rear가 같아져서 빈 큐와 똑같이 보인다. 그래서 8개까지만 넣을 수 있다.<br>• % MAX_QUEUE_SIZE는 마지막 칸 다음을 0번 칸으로 되돌린다.</td>
</tr>
</table>
<empty-block/>
## enqueue
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int enqueue(ReadyQueue \*q, Context value)<br>\{<br>    if (q == NULL \|\| is_full_queue(q))<br>    \{<br>        return 0;<br>    \}<br>    q-\>rear = (q-\>rear + 1) % MAX_QUEUE_SIZE;<br>    q-\>queue\[q-\>rear\] = value;<br>    return 1;<br>\}</td>
<td>#기능 명세<br>• 인자: 큐 q, 넣을 문맥 value<br>• 반환값: 성공하면 1, 큐가 NULL이거나 가득 차면 0(상태 변경 없음)<br>• 상태 변경: rear를 원형으로 한 칸 옮기고 그 칸에 value를 복사<br><br>#분석<br>• 실패 시 처리는 호출한 쪽이 정한다. main의 초기 등록과 finish_tick의 재등록에서 쓰인다.</td>
</tr>
</table>
<empty-block/>
## dequeue
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>Context dequeue(ReadyQueue \*q)<br>\{<br>    if (q == NULL \|\| is_empty_queue(q))<br>    \{<br>        printf("QUEUE_ERROR\\n");<br>        exit(1);<br>    \}<br>    q-\>front = (q-\>front + 1) % MAX_QUEUE_SIZE;<br>    return q-\>queue\[q-\>front\];<br>\}</td>
<td>#기능 명세<br>• 반환값: 맨 앞 문맥<br>• 상태 변경: front를 원형으로 한 칸 옮긴다. 빈 큐이면 QUEUE_ERROR를 출력하고 exit(1)로 종료<br><br>#분석<br>• 꺼낸 칸의 값은 지우지 않으며, 이후 enqueue가 덮어쓴다.</td>
</tr>
</table>
<empty-block/>
## init_stack
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void init_stack(ContextStack \*s)<br>\{<br>    s-\>top = -1;<br>\}</td>
<td>#기능 명세<br>• top = -1로 빈 스택을 만든다.</td>
</tr>
</table>
<empty-block/>
## is_empty_stack
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_empty_stack(const ContextStack \*s)<br>\{<br>    return s-\>top == -1;<br>\}</td>
<td>#기능 명세<br>• top == -1이면 저장된 문맥이 없으므로 1을 반환한다. finish_tick이 복원할 문맥이 있는지 확인할 때 쓴다.</td>
</tr>
</table>
<empty-block/>
## is_full_stack
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_full_stack(const ContextStack \*s)<br>\{<br>    return s-\>top == MAX_STACK_SIZE - 1;<br>\}</td>
<td>#기능 명세<br>• top이 마지막 인덱스 15이면 1을 반환한다.</td>
</tr>
</table>
<empty-block/>
## push
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int push(ContextStack \*s, Context value)<br>\{<br>    if (s == NULL \|\| is_full_stack(s))<br>    \{<br>        return 0;<br>    \}<br>    s-\>stack\[++(s-\>top)\] = value;<br>    return 1;<br>\}</td>
<td>#기능 명세<br>• 반환값: 성공하면 1, 스택이 NULL이거나 가득 차면 0<br>• 상태 변경: top을 먼저 1 올리고(++top) 그 칸에 value를 복사<br><br>#분석<br>• start_interrupt가 중단되는 작업의 문맥을 저장할 때 쓴다.</td>
</tr>
</table>
<empty-block/>
## pop
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>Context pop(ContextStack \*s)<br>\{<br>    if (s == NULL \|\| is_empty_stack(s))<br>    \{<br>        printf("STACK_ERROR\\n");<br>        exit(1);<br>    \}<br>    return s-\>stack\[(s-\>top)--\];<br>\}</td>
<td>#기능 명세<br>• 반환값: top 칸의 문맥. 반환 후 top을 1 내린다(top--).<br>• 빈 스택이면 STACK_ERROR를 출력하고 exit(1)로 종료<br><br>#분석<br>• finish_tick이 인터럽트 종료 후 가장 최근에 중단된 문맥을 되돌릴 때 쓴다.</td>
</tr>
</table>
<empty-block/>
## select_process (구현)
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void select_process(Scheduler \*s)<br>\{<br>    if (s-\>current.kind != IDLE \|\| is_empty_queue(&s-\>ready))<br>    \{<br>        return;<br>    \}<br>    s-\>current = dequeue(&s-\>ready);<br>    s-\>current.quantum_left = QUANTUM;<br>\}</td>
<td>#기능 명세<br>• 인자: 스케줄러 s / 반환값: 없음<br>• 상태 변경: CPU가 비어 있고 준비 큐가 비어 있지 않으면 맨 앞 프로세스를 current로 꺼내 quantum_left = QUANTUM(2)으로 설정<br><br>#분석<br>• current.kind != IDLE 검사: main이 매 tick 호출하므로, 실행 중인 프로세스나 인터럽트를 덮어쓰지 않게 막는다.<br>• 빈 큐를 먼저 검사해 dequeue의 QUEUE_ERROR 종료를 피한다. 큐가 비면 current는 IDLE로 남고 execute_tick은 시간만 흘려보낸다.<br>• 큐로 돌아온 프로세스는 quantum_left가 0이므로 선택될 때마다 퀀텀 2를 새로 받는다.<br>• 인터럽트가 끝나고 돌아온 프로세스는 이 함수를 다시 거치지 않는다. 그래서 퀀텀을 새로 받지 않고 남아 있던 만큼만 쓴다. 공식 예시의 T5에서 Q가 0으로 나오는 것이 이 때문이다.</td>
</tr>
</table>
<empty-block/>
## start_interrupt (구현)
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void start_interrupt(Scheduler \*s, InterruptEvent event)<br>\{<br>    if (s-\>current.kind != IDLE && !push(&s-\>suspended, s-\>current))<br>    \{<br>        printf("SIMULATION_ERROR\\n");<br>        exit(2);<br>    \}<br>    s-\>current.kind = INTERRUPT;<br>    s-\>current.id = event.id;<br>    s-\>current.remaining = event.duration;<br>    s-\>current.quantum_left = 0;<br>\}</td>
<td>#기능 명세<br>• 인자: 스케줄러 s, 도착한 인터럽트 event / 반환값: 없음<br>• 상태 변경: current가 IDLE이 아니면 스택에 push한 뒤, current를 새 인터럽트(id, remaining = duration, quantum_left = 0)로 바꾼다.<br><br>#분석<br>• 실행 중이던 작업을 스택에 넣어 두는 부분이다. 남은 시간과 남은 퀀텀이 같이 저장되기 때문에 나중에 꺼내면 멈춘 곳부터 이어서 실행된다.<br>• CPU가 비어 있을 때는 저장할 것이 없어서 push를 하지 않는다. 조건문에서 IDLE인지를 먼저 검사하게 썼기 때문에 이 경우에는 push가 실행되지 않는다.<br>• push가 실패하면 main과 같은 방식으로 SIMULATION_ERROR를 출력하고 끝내게 했다. 인터럽트가 최대 16개라 스택 16칸이 넘치지는 않을 것으로 보았다.<br>• execute_tick은 인터럽트의 quantum_left를 검사하거나 줄이지 않으므로, 인터럽트는 퀀텀 소진으로 중단되지 않는다.</td>
</tr>
</table>
<empty-block/>
## finish_tick (구현)
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void finish_tick(Scheduler \*s)<br>\{<br>    Context \*current = &s-\>current;<br>    if (current-\>kind == PROCESS)<br>    \{<br>        if (current-\>remaining == 0)<br>        \{<br>            s-\>finished_processes++;<br>            \*current = IDLE_CONTEXT;<br>        \}<br>        else if (current-\>quantum_left == 0)<br>        \{<br>            if (!enqueue(&s-\>ready, \*current))<br>            \{<br>                printf("SIMULATION_ERROR\\n");<br>                exit(2);<br>            \}<br>            \*current = IDLE_CONTEXT;<br>        \}<br>    \}</td>
<td>#기능 명세<br>• 인자: 스케줄러 s / 반환값: 없음<br>• 상태 변경: execute_tick 직후 결과에 따라 완료 처리, 큐 재등록, 문맥 복원을 하고 current를 정리한다.<br>• 지역 변수 current는 s-\>current를 가리키는 포인터라, 변경이 스케줄러에 바로 반영된다.<br><br>#분석<br>• 프로세스의 remaining == 0: 완료 수를 늘리고 IDLE로 비워, 다음 tick에 select_process가 다른 프로세스를 고르게 한다.<br>• quantum_left == 0: 퀀텀 소진이므로 준비 큐 맨 뒤에 넣고 IDLE로 비운다. 둘 다 아니면 다음 tick에도 같은 프로세스가 실행된다.<br>• 남은 시간이 0인지를 퀀텀보다 먼저 검사했다. 둘이 같은 tick에 0이 되는 경우가 있는데(추가 사례 2), 퀀텀을 먼저 보면 이미 끝난 프로세스가 큐에 다시 들어간다고 생각했기 때문이다.<br>• 실행 중인 프로세스는 큐 밖에 있어 큐에는 최대 7개뿐이므로 정상 입력에서 enqueue는 실패하지 않는다. 실패 시 처리는 start_interrupt와 같다.</td>
</tr>
<tr>
<td>    else if (current-\>kind == INTERRUPT && current-\>remaining == 0)<br>    \{<br>        s-\>finished_interrupts++;<br>        if (is_empty_stack(&s-\>suspended))<br>        \{<br>            \*current = IDLE_CONTEXT;<br>        \}<br>        else<br>        \{<br>            \*current = pop(&s-\>suspended);<br>        \}<br>    \}<br>\}</td>
<td>#분석<br>• 인터럽트의 remaining == 0: 완료 수를 늘리고, 스택이 비었으면 IDLE로, 아니면 pop으로 가장 최근에 중단된 문맥을 current로 복원한다.<br>• 인터럽트가 여러 개 겹쳐 있으면 나중에 멈춘 것부터 다시 실행되고, 맨 처음에 멈춘 프로세스는 가장 마지막에 돌아온다.<br>• 빈 스택을 먼저 확인하므로 pop의 STACK_ERROR 종료는 일어나지 않는다. 다음 프로세스 선택은 select_process가 맡는다.</td>
</tr>
</table>
<empty-block/>
## execute_tick
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int execute_tick(Scheduler \*s)<br>\{<br>    Context \*current = &s-\>current;<br>    if ((current-\>kind != IDLE && current-\>remaining \<= 0) \|\|<br>        (current-\>kind == PROCESS && current-\>quantum_left \<= 0))<br>    \{<br>        return 0;<br>    \}</td>
<td>#기능 명세<br>• 인자: 스케줄러 s<br>• 반환값: 1 tick을 실행했으면 1, 실행할 수 없는 상태면 0<br><br>#분석<br>• 남은 시간이 0인 작업이나 퀀텀이 0인 프로세스가 들어오면 실행하지 않고 바로 0을 반환한다.<br>• finish_tick이 상태를 올바르게 정리했다면 나올 수 없는 상태라, 구현 함수의 상태 전이를 점검하는 역할을 한다. main은 0을 받으면 SIMULATION_ERROR로 끝낸다.</td>
</tr>
<tr>
<td>    if (current-\>kind != IDLE)<br>    \{<br>        current-\>remaining--;<br>    \}<br>    s-\>tick++;<br>    if (current-\>kind == PROCESS)<br>    \{<br>        current-\>quantum_left--;<br>        printf("T%3d P%2d R%2d Q%2d\\n", s-\>tick,<br>               current-\>id, current-\>remaining, current-\>quantum_left);<br>    \}<br>    else if (current-\>kind == INTERRUPT)<br>    \{<br>        printf("T%3d I%2d R%2d\\n", s-\>tick, current-\>id, current-\>remaining);<br>    \}<br>    else<br>    \{<br>        printf("T%3d IDLE\\n", s-\>tick);<br>    \}<br>    return 1;<br>\}</td>
<td>#기능 명세<br>• 상태 변경: IDLE이 아니면 remaining을 1 줄이고, 프로세스면 quantum_left도 1 줄인다. tick은 항상 1 늘린다.<br>• 출력: 프로세스는 T·P·R·Q, 인터럽트는 T·I·R, IDLE은 T와 IDLE<br><br>#분석<br>• T는 tick을 늘린 뒤의 시각이므로, T 1은 시각 0부터 1까지의 실행 결과다.<br>• 완료·재등록·복원은 출력 뒤 finish_tick이 맡는다.</td>
</tr>
</table>
<empty-block/>
## main
<table header-row="true">
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int main(void)<br>\{<br>    Context processes\[MAX_PROCESSES\] = \{0\};<br>    InterruptEvent interrupts\[MAX_INTERRUPTS\] = \{0\};<br>    int process_count, interrupt_count;<br>    Scheduler s = \{0\};<br>    int next_interrupt = 0;<br><br>    if (scanf("%d %d", &process_count, &interrupt_count) != 2 \|\|<br>        process_count \< 1 \|\| process_count \> MAX_PROCESSES \|\|<br>        interrupt_count \< 0 \|\| interrupt_count \> MAX_INTERRUPTS)<br>    \{<br>        printf("INPUT_ERROR\\n");<br>        return 1;<br>    \}</td>
<td>#기능 명세<br>• 반환값: 정상 종료 0, 입력 오류 1(INPUT_ERROR), 시뮬레이션 오류 2(SIMULATION_ERROR)<br>• 입력: 첫 줄에서 프로세스 수 N(1\~8)과 인터럽트 수 M(0\~16)<br><br>#분석<br>• s = \{0\}이므로 tick과 완료 수는 0이고, current도 IDLE_CONTEXT와 같은 상태로 시작한다.</td>
</tr>
<tr>
<td>    for (int i = 0; i \< process_count; i++)<br>    \{<br>        if (scanf("%d", &processes\[i\].remaining) != 1 \|\|<br>            processes\[i\].remaining \< 1 \|\| processes\[i\].remaining \> MAX_DURATION)<br>        \{<br>            printf("INPUT_ERROR\\n");<br>            return 1;<br>        \}<br>        processes\[i\].id = i + 1;<br>        processes\[i\].kind = PROCESS;<br>    \}</td>
<td>#기능 명세<br>• 프로세스마다 실행 시간(1\~10)을 remaining에 읽고, id는 입력 순서대로 1부터, kind는 PROCESS로 둔다.<br><br>#분석<br>• quantum_left는 0으로 두며, 실제 값은 select_process가 CPU를 배정할 때 정한다.</td>
</tr>
<tr>
<td>    for (int i = 0; i \< interrupt_count; i++)<br>    \{<br>        if (scanf("%d %d", &interrupts\[i\].arrival_time,<br>                  &interrupts\[i\].duration) != 2 \|\|<br>            interrupts\[i\].arrival_time \< 0 \|\| interrupts\[i\].arrival_time \> MAX_ARRIVAL_TIME \|\|<br>            interrupts\[i\].duration \< 1 \|\| interrupts\[i\].duration \> MAX_DURATION \|\|<br>            (i \> 0 && interrupts\[i\].arrival_time \<= interrupts\[i - 1\].arrival_time))<br>        \{<br>            printf("INPUT_ERROR\\n");<br>            return 1;<br>        \}<br>        interrupts\[i\].id = i + 1;<br>    \}</td>
<td>#기능 명세<br>• 인터럽트마다 도착 시각(0\~1000)과 처리 시간(1\~10)을 읽고, 도착 시각이 앞 인터럽트보다 큰지 검사한다.<br><br>#분석<br>• 도착 시각이 계속 커지므로 next_interrupt 하나로 차례대로 처리할 수 있고, 한 시각에 인터럽트가 둘 이상 오지 않는다.</td>
</tr>
<tr>
<td>    init_queue(&s.ready);<br>    init_stack(&s.suspended);<br><br>    for (int i = 0; i \< process_count; i++)<br>    \{<br>        if (!enqueue(&s.ready, processes\[i\]))<br>        \{<br>            printf("SIMULATION_ERROR\\n");<br>            return 2;<br>        \}<br>    \}</td>
<td>#기능 명세<br>• 큐와 스택을 초기화하고 모든 프로세스를 입력 순서대로 준비 큐에 넣는다.<br><br>#분석<br>• 모든 프로세스가 시각 0에 도착한다는 규칙을 이 코드로 표현한다. 프로세스는 최대 8개라 정상 입력에서 enqueue는 실패하지 않는다.</td>
</tr>
<tr>
<td>    while (s.finished_processes \< process_count \|\|<br>           s.finished_interrupts \< interrupt_count)<br>    \{<br>        if (s.tick \>= MAX_SIMULATION_TICKS)<br>        \{<br>            printf("SIMULATION_ERROR\\n");<br>            return 2;<br>        \}<br><br>        if (next_interrupt \< interrupt_count &&<br>            interrupts\[next_interrupt\].arrival_time == s.tick)<br>        \{<br>            start_interrupt(&s, interrupts\[next_interrupt\]);<br>            next_interrupt++;<br>        \}<br>        select_process(&s);<br>        if (!execute_tick(&s))<br>        \{<br>            printf("SIMULATION_ERROR\\n");<br>            return 2;<br>        \}<br>        finish_tick(&s);<br>    \}</td>
<td>#기능 명세<br>• 프로세스와 인터럽트가 모두 끝날 때까지 1 tick씩 반복한다.<br>• 반복 1회: ① 현재 시각에 도착한 인터럽트를 start_interrupt로 시작 ② select_process로 프로세스 선택 ③ execute_tick으로 1 tick 실행·출력 ④ finish_tick으로 완료·재등록·복원<br><br>#분석<br>• main은 인터럽트를 먼저 확인하고 그다음에 프로세스를 고른다. 그래서 CPU가 비어 있는 시각에 인터럽트가 오면 기다리던 프로세스보다 인터럽트가 먼저 실행된다(추가 사례 3).<br>• 프로세스가 모두 끝나도 아직 오지 않은 인터럽트가 있으면 IDLE로 기다린다(추가 사례 4).<br>• execute_tick이 성공하면 tick이 반드시 1 늘어 도착 시각을 건너뛰지 않는다. tick이 상한에 닿거나 execute_tick이 0을 반환하면 SIMULATION_ERROR로 끝낸다.</td>
</tr>
<tr>
<td>    printf("FINISHED %d INTERRUPTS %d TICKS %d\\n",<br>           s.finished_processes, s.finished_interrupts, s.tick);<br>    return 0;<br>\}</td>
<td>#기능 명세<br>• 완료한 프로세스 수, 인터럽트 수, 전체 tick을 한 줄로 출력하고 0을 반환한다.</td>
</tr>
</table>
<empty-block/>
<empty-block/>
# 실행결과 및 분석
## 공식 예시: 중첩 인터럽트와 라운드로빈
**입력:**
```plain text
2 2
3
1
1 2
2 1
```
**실제 출력:**
```plain text
T  1 P 1 R 2 Q 1
T  2 I 1 R 1
T  3 I 2 R 0
T  4 I 1 R 0
T  5 P 1 R 1 Q 0
T  6 P 2 R 0 Q 1
T  7 P 1 R 0 Q 1
FINISHED 2 INTERRUPTS 2 TICKS 7
```
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/0d75e8a4-c83e-4379-8571-cfd17c35cd1b/hw3-case-01.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SQQ3VAYI%2F20261111%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261111T145023Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEI7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCOl5DExrASDyBxc2chpOm%2BmsIPQIQGaTLpxdrXXj89FwIgYxX1Nu7HwaNHMUyCSsq4L%2Fw%2BymITre2dAE0O4Ir6A0wq%2FwMIVhAAGgw2Mzc0MjMxODM4MDUiDB43uZsLr3aHAHX1hircA5GB0qOPJnGk3E4AJ%2BoN75rphDdZMz%2B5RtkhJ9UHBaEa%2FFlVobph93RnBdew%2FscwvgaXQRnFrkZ5wYYM0bRy7z7d5yQ6731GUc6WR2cSfmwH0zm8d6p7g6hzv8PRRWp2ld4KUaG%2B%2B4n4DPuK0D%2BzFqsfGKXqDndtRyEtUXWV0X7175PRw8S4b%2FnTW%2F16d2jYA%2FaaUAmKC38jxvjrkuzXT%2BSqAboKtmYB48rwt1MUqcLpIFqAOfbtiQFwpF8vJC2N48ZCyIgPug0yC56U8hKzSxdhfWJ5MMZNAr86EcjOcCm38Kki3zV9KfW66zNdh2XTfYA995d20GwBSTIBIikIW3Bz9htgRmevFe79D6tfup73QoEjdGrSjLdjY5wzDA9sC73ljUA8cexoWVBvfyqd3XJs%2BIqWCpzkLmygFcG%2BLrXkcPWAO06NraVoczplL1KSxtivqwd4HlLlXWVzg9S5zPsrkp2JZgQ2REW0S%2BdrjrDSQ7bQHA71hmL4FAProdwv6qajQWxd1mSYBY8XUY%2F8l2kFi2ZDFH8xae1K%2BnqpOpvr3eS7iybeaNU0zc0Xaxsh8twauR5HwqN3X1d%2F0FIZ3i2fMDbjHI1%2FhLYVwlZYEIgdi92xiZwqmZGngrj3MO7a0dcGOqUBbnN2cHqUf9Wim8lWiqXWpi%2BjNQ0ZqOPs2BDpn1cHHcf01F6ZFnUZq4rmUqQ9zwi1bpfiEPcoQQ5f5YKhW4KMW3mQo7KoivnLc45DZOlh6mSrwqzXfnswujaOlvSOJdYMBqCVkVizBDy%2FhI9yr2FXVF6sL8g%2BM9h0VubabTvoFtd1DkCNMNInrpfQzZmBwxxH91rnLcpjC86fSZcVnodeFVBpyRAb&X-Amz-Signature=d065d48f5a8947ca67c7ec9d4dc5b1167a8487836525d11972b621e0e9d51004&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.415b06d2-63bc-81ad-a685-ec84509940ad.bb202fe9-e653-4278-8d2f-0d12906a5653)
<table header-row="true">
<tr>
<td>시각</td>
<td>실행</td>
<td>상태 변화의 이유</td>
</tr>
<tr>
<td>0→1</td>
<td>P1</td>
<td>준비 큐 \[P1, P2\]에서 P1을 꺼내 Q=2를 준다. 1 tick 실행 후 R2 Q1, 두 값 모두 0이 아니므로 계속 실행한다.</td>
</tr>
<tr>
<td>1→2</td>
<td>I1</td>
<td>I1 도착. P1(R2, Q1)을 push해 스택 \[P1\]. I1 R2→1.</td>
</tr>
<tr>
<td>2→3</td>
<td>I2</td>
<td>I2 도착. I1(R1)을 push해 스택 \[P1, I1\]. I2 R1→0으로 완료, 맨 위 I1을 pop한다.</td>
</tr>
<tr>
<td>3→4</td>
<td>I1</td>
<td>I1 R1→0으로 완료, 스택에 남은 P1을 pop해 스택이 빈다.</td>
</tr>
<tr>
<td>4→5</td>
<td>P1</td>
<td>복원된 P1은 Q1을 이어 써서 R1 Q0. 퀀텀 소진으로 큐 뒤에 넣어 \[P2, P1\], CPU는 IDLE.</td>
</tr>
<tr>
<td>5→6</td>
<td>P2</td>
<td>P2를 꺼내 Q=2. R1→0으로 완료.</td>
</tr>
<tr>
<td>6→7</td>
<td>P1</td>
<td>P1을 다시 꺼내 Q=2. R1→0으로 완료. 모든 작업이 끝나 반복 종료.</td>
</tr>
</table>
**결과 분석:** 출력 순서 P1 I1 I2 I1 P1 P2 P1은 과제 18쪽 실행 화면·간트 차트와 같다. 시각 2에 I2가 들어와서 I1이 멈췄다. I2가 끝난 뒤에는 P1이 아니라 I1이 먼저 이어서 실행되었는데, 스택이라서 마지막에 넣은 것이 먼저 나오기 때문이다.
<empty-block/>
## 추가 사례 1: 세 겹 중첩 인터럽트
**입력:**
```plain text
1 3
4
1 3
2 3
3 1
```
**실제 출력:**
```plain text
T  1 P 1 R 3 Q 1
T  2 I 1 R 2
T  3 I 2 R 2
T  4 I 3 R 0
T  5 I 2 R 1
T  6 I 2 R 0
T  7 I 1 R 1
T  8 I 1 R 0
T  9 P 1 R 2 Q 0
T 10 P 1 R 1 Q 1
T 11 P 1 R 0 Q 0
FINISHED 1 INTERRUPTS 3 TICKS 11
```
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/382b482a-d69b-4736-ba5e-e1002c78b514/hw3-case-02.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SQQ3VAYI%2F20261111%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261111T145023Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEI7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCOl5DExrASDyBxc2chpOm%2BmsIPQIQGaTLpxdrXXj89FwIgYxX1Nu7HwaNHMUyCSsq4L%2Fw%2BymITre2dAE0O4Ir6A0wq%2FwMIVhAAGgw2Mzc0MjMxODM4MDUiDB43uZsLr3aHAHX1hircA5GB0qOPJnGk3E4AJ%2BoN75rphDdZMz%2B5RtkhJ9UHBaEa%2FFlVobph93RnBdew%2FscwvgaXQRnFrkZ5wYYM0bRy7z7d5yQ6731GUc6WR2cSfmwH0zm8d6p7g6hzv8PRRWp2ld4KUaG%2B%2B4n4DPuK0D%2BzFqsfGKXqDndtRyEtUXWV0X7175PRw8S4b%2FnTW%2F16d2jYA%2FaaUAmKC38jxvjrkuzXT%2BSqAboKtmYB48rwt1MUqcLpIFqAOfbtiQFwpF8vJC2N48ZCyIgPug0yC56U8hKzSxdhfWJ5MMZNAr86EcjOcCm38Kki3zV9KfW66zNdh2XTfYA995d20GwBSTIBIikIW3Bz9htgRmevFe79D6tfup73QoEjdGrSjLdjY5wzDA9sC73ljUA8cexoWVBvfyqd3XJs%2BIqWCpzkLmygFcG%2BLrXkcPWAO06NraVoczplL1KSxtivqwd4HlLlXWVzg9S5zPsrkp2JZgQ2REW0S%2BdrjrDSQ7bQHA71hmL4FAProdwv6qajQWxd1mSYBY8XUY%2F8l2kFi2ZDFH8xae1K%2BnqpOpvr3eS7iybeaNU0zc0Xaxsh8twauR5HwqN3X1d%2F0FIZ3i2fMDbjHI1%2FhLYVwlZYEIgdi92xiZwqmZGngrj3MO7a0dcGOqUBbnN2cHqUf9Wim8lWiqXWpi%2BjNQ0ZqOPs2BDpn1cHHcf01F6ZFnUZq4rmUqQ9zwi1bpfiEPcoQQ5f5YKhW4KMW3mQo7KoivnLc45DZOlh6mSrwqzXfnswujaOlvSOJdYMBqCVkVizBDy%2FhI9yr2FXVF6sL8g%2BM9h0VubabTvoFtd1DkCNMNInrpfQzZmBwxxH91rnLcpjC86fSZcVnodeFVBpyRAb&X-Amz-Signature=2176b37def0faebab55b15ad652cef4ac8a883063ccb2c47d2dbb1d38d66cd04&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.415b06d2-63bc-815c-8c4a-da4149ac8497.bb202fe9-e653-4278-8d2f-0d12906a5653)
<table header-row="true">
<tr>
<td>시각</td>
<td>실행</td>
<td>상태 변화의 이유</td>
</tr>
<tr>
<td>0→1</td>
<td>P1</td>
<td>P1 선택, Q=2. R3 Q1.</td>
</tr>
<tr>
<td>1→4</td>
<td>I1, I2, I3</td>
<td>시각 1·2·3에 차례로 도착하며 P1, I1, I2를 push. 스택 \[P1, I1, I2\]. I3은 1 tick에 완료하고 I2를 pop.</td>
</tr>
<tr>
<td>4→6</td>
<td>I2</td>
<td>I2가 남은 2 tick을 실행해 완료, I1을 pop.</td>
</tr>
<tr>
<td>6→8</td>
<td>I1</td>
<td>I1이 남은 2 tick을 실행해 완료, P1을 pop. 스택이 빈다.</td>
</tr>
<tr>
<td>8→9</td>
<td>P1</td>
<td>Q1을 이어 써서 R2 Q0. 퀀텀 소진으로 큐 \[P1\]에 넣고 IDLE.</td>
</tr>
<tr>
<td>9→11</td>
<td>P1</td>
<td>큐에 P1밖에 없어서 다시 P1이 실행된다. T11에서 R과 Q가 같이 0이 되었는데 완료로 처리되었다.</td>
</tr>
</table>
**결과 분석:** 인터럽트는 I1, I2, I3 순으로 시작해 I3, I2, I1 순으로 끝났다. 스택에 늦게 들어간 문맥일수록 먼저 복원되어(최대 3개 적재) P1이 가장 늦게 재개되었다. T11에는 R과 Q가 동시에 0이 되었지만 완료로 처리되어 FINISHED 1이 출력되었다.
<empty-block/>
## 추가 사례 2: 완료와 퀀텀 소진이 같은 tick
**입력:**
```plain text
2 0
2
1
```
**실제 출력:**
```plain text
T  1 P 1 R 1 Q 1
T  2 P 1 R 0 Q 0
T  3 P 2 R 0 Q 1
FINISHED 2 INTERRUPTS 0 TICKS 3
```
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/3e98fea9-79d6-4b57-8a53-2363ba641a87/hw3-case-03.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SQQ3VAYI%2F20261111%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261111T145023Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEI7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCOl5DExrASDyBxc2chpOm%2BmsIPQIQGaTLpxdrXXj89FwIgYxX1Nu7HwaNHMUyCSsq4L%2Fw%2BymITre2dAE0O4Ir6A0wq%2FwMIVhAAGgw2Mzc0MjMxODM4MDUiDB43uZsLr3aHAHX1hircA5GB0qOPJnGk3E4AJ%2BoN75rphDdZMz%2B5RtkhJ9UHBaEa%2FFlVobph93RnBdew%2FscwvgaXQRnFrkZ5wYYM0bRy7z7d5yQ6731GUc6WR2cSfmwH0zm8d6p7g6hzv8PRRWp2ld4KUaG%2B%2B4n4DPuK0D%2BzFqsfGKXqDndtRyEtUXWV0X7175PRw8S4b%2FnTW%2F16d2jYA%2FaaUAmKC38jxvjrkuzXT%2BSqAboKtmYB48rwt1MUqcLpIFqAOfbtiQFwpF8vJC2N48ZCyIgPug0yC56U8hKzSxdhfWJ5MMZNAr86EcjOcCm38Kki3zV9KfW66zNdh2XTfYA995d20GwBSTIBIikIW3Bz9htgRmevFe79D6tfup73QoEjdGrSjLdjY5wzDA9sC73ljUA8cexoWVBvfyqd3XJs%2BIqWCpzkLmygFcG%2BLrXkcPWAO06NraVoczplL1KSxtivqwd4HlLlXWVzg9S5zPsrkp2JZgQ2REW0S%2BdrjrDSQ7bQHA71hmL4FAProdwv6qajQWxd1mSYBY8XUY%2F8l2kFi2ZDFH8xae1K%2BnqpOpvr3eS7iybeaNU0zc0Xaxsh8twauR5HwqN3X1d%2F0FIZ3i2fMDbjHI1%2FhLYVwlZYEIgdi92xiZwqmZGngrj3MO7a0dcGOqUBbnN2cHqUf9Wim8lWiqXWpi%2BjNQ0ZqOPs2BDpn1cHHcf01F6ZFnUZq4rmUqQ9zwi1bpfiEPcoQQ5f5YKhW4KMW3mQo7KoivnLc45DZOlh6mSrwqzXfnswujaOlvSOJdYMBqCVkVizBDy%2FhI9yr2FXVF6sL8g%2BM9h0VubabTvoFtd1DkCNMNInrpfQzZmBwxxH91rnLcpjC86fSZcVnodeFVBpyRAb&X-Amz-Signature=accd4ad535851dd146cae3432004efffa53e620810f2445821dea91bafb42b4e&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.415b06d2-63bc-81c0-93eb-ce6d4cfe78a8.bb202fe9-e653-4278-8d2f-0d12906a5653)
<table header-row="true">
<tr>
<td>시각</td>
<td>실행</td>
<td>상태 변화의 이유</td>
</tr>
<tr>
<td>0→2</td>
<td>P1</td>
<td>Q=2로 2 tick 실행. T2에 R0 Q0. finish_tick이 remaining을 먼저 보고 완료 처리, IDLE.</td>
</tr>
<tr>
<td>2→3</td>
<td>P2</td>
<td>큐에 남은 P2를 꺼내 1 tick에 완료.</td>
</tr>
</table>
**결과 분석:** P1은 T2에 퀀텀과 남은 시간이 함께 0이 되어 준비 큐로 돌아가지 않고 완료되었다. 그래서 다음 tick에 바로 P2가 실행되었고 P1은 다시 선택되지 않았다.
<empty-block/>
## 추가 사례 3: CPU가 빈 순간에 도착한 인터럽트
**입력:**
```plain text
2 1
3
2
2 1
```
**실제 출력:**
```plain text
T  1 P 1 R 2 Q 1
T  2 P 1 R 1 Q 0
T  3 I 1 R 0
T  4 P 2 R 1 Q 1
T  5 P 2 R 0 Q 0
T  6 P 1 R 0 Q 1
FINISHED 2 INTERRUPTS 1 TICKS 6
```
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/3cab98b7-7d43-419f-8d86-7a9a3a477c4a/hw3-case-04.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SQQ3VAYI%2F20261111%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261111T145023Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEI7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCOl5DExrASDyBxc2chpOm%2BmsIPQIQGaTLpxdrXXj89FwIgYxX1Nu7HwaNHMUyCSsq4L%2Fw%2BymITre2dAE0O4Ir6A0wq%2FwMIVhAAGgw2Mzc0MjMxODM4MDUiDB43uZsLr3aHAHX1hircA5GB0qOPJnGk3E4AJ%2BoN75rphDdZMz%2B5RtkhJ9UHBaEa%2FFlVobph93RnBdew%2FscwvgaXQRnFrkZ5wYYM0bRy7z7d5yQ6731GUc6WR2cSfmwH0zm8d6p7g6hzv8PRRWp2ld4KUaG%2B%2B4n4DPuK0D%2BzFqsfGKXqDndtRyEtUXWV0X7175PRw8S4b%2FnTW%2F16d2jYA%2FaaUAmKC38jxvjrkuzXT%2BSqAboKtmYB48rwt1MUqcLpIFqAOfbtiQFwpF8vJC2N48ZCyIgPug0yC56U8hKzSxdhfWJ5MMZNAr86EcjOcCm38Kki3zV9KfW66zNdh2XTfYA995d20GwBSTIBIikIW3Bz9htgRmevFe79D6tfup73QoEjdGrSjLdjY5wzDA9sC73ljUA8cexoWVBvfyqd3XJs%2BIqWCpzkLmygFcG%2BLrXkcPWAO06NraVoczplL1KSxtivqwd4HlLlXWVzg9S5zPsrkp2JZgQ2REW0S%2BdrjrDSQ7bQHA71hmL4FAProdwv6qajQWxd1mSYBY8XUY%2F8l2kFi2ZDFH8xae1K%2BnqpOpvr3eS7iybeaNU0zc0Xaxsh8twauR5HwqN3X1d%2F0FIZ3i2fMDbjHI1%2FhLYVwlZYEIgdi92xiZwqmZGngrj3MO7a0dcGOqUBbnN2cHqUf9Wim8lWiqXWpi%2BjNQ0ZqOPs2BDpn1cHHcf01F6ZFnUZq4rmUqQ9zwi1bpfiEPcoQQ5f5YKhW4KMW3mQo7KoivnLc45DZOlh6mSrwqzXfnswujaOlvSOJdYMBqCVkVizBDy%2FhI9yr2FXVF6sL8g%2BM9h0VubabTvoFtd1DkCNMNInrpfQzZmBwxxH91rnLcpjC86fSZcVnodeFVBpyRAb&X-Amz-Signature=077760559e677ce982322a0cac4363fce03fe805f9803a52a81d931825c1f1ab&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.415b06d2-63bc-81f1-aa96-ee4db90f13ab.bb202fe9-e653-4278-8d2f-0d12906a5653)
<table header-row="true">
<tr>
<td>시각</td>
<td>실행</td>
<td>상태 변화의 이유</td>
</tr>
<tr>
<td>0→2</td>
<td>P1</td>
<td>P1이 퀀텀 2를 모두 써서 R1 Q0. 큐 뒤에 넣어 \[P2, P1\], IDLE.</td>
</tr>
<tr>
<td>2→3</td>
<td>I1</td>
<td>I1 도착. current가 IDLE이므로 push하지 않음. select_process는 current가 인터럽트라 P2를 꺼내지 않는다. I1 완료 후 스택이 비어 IDLE.</td>
</tr>
<tr>
<td>3→5</td>
<td>P2</td>
<td>P2를 꺼내 Q=2로 2 tick 실행, T5에 R0 Q0으로 완료.</td>
</tr>
<tr>
<td>5→6</td>
<td>P1</td>
<td>P1을 꺼내 1 tick에 완료.</td>
</tr>
</table>
**결과 분석:** 시각 2에는 P1이 이미 큐로 돌아가 CPU가 비어 있었으므로 I1은 아무 문맥도 push하지 않았고, I1이 끝나자 CPU는 IDLE이 되었다. CPU가 빈 시각에도 main이 인터럽트를 먼저 시작하므로 T3에는 P2가 아닌 I1이 실행되었고, 이후 큐 순서 \[P2, P1\]대로 실행되었다.
<empty-block/>
## 추가 사례 4: 프로세스가 모두 끝난 뒤의 인터럽트
**입력:**
```plain text
1 1
1
3 2
```
**실제 출력:**
```plain text
T  1 P 1 R 0 Q 1
T  2 IDLE
T  3 IDLE
T  4 I 1 R 1
T  5 I 1 R 0
FINISHED 1 INTERRUPTS 1 TICKS 5
```
![](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/200afe59-83d4-4489-b0da-11fc0a0e5c86/hw3-case-05.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466SQQ3VAYI%2F20261111%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261111T145023Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEI7%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLXdlc3QtMiJHMEUCIQCOl5DExrASDyBxc2chpOm%2BmsIPQIQGaTLpxdrXXj89FwIgYxX1Nu7HwaNHMUyCSsq4L%2Fw%2BymITre2dAE0O4Ir6A0wq%2FwMIVhAAGgw2Mzc0MjMxODM4MDUiDB43uZsLr3aHAHX1hircA5GB0qOPJnGk3E4AJ%2BoN75rphDdZMz%2B5RtkhJ9UHBaEa%2FFlVobph93RnBdew%2FscwvgaXQRnFrkZ5wYYM0bRy7z7d5yQ6731GUc6WR2cSfmwH0zm8d6p7g6hzv8PRRWp2ld4KUaG%2B%2B4n4DPuK0D%2BzFqsfGKXqDndtRyEtUXWV0X7175PRw8S4b%2FnTW%2F16d2jYA%2FaaUAmKC38jxvjrkuzXT%2BSqAboKtmYB48rwt1MUqcLpIFqAOfbtiQFwpF8vJC2N48ZCyIgPug0yC56U8hKzSxdhfWJ5MMZNAr86EcjOcCm38Kki3zV9KfW66zNdh2XTfYA995d20GwBSTIBIikIW3Bz9htgRmevFe79D6tfup73QoEjdGrSjLdjY5wzDA9sC73ljUA8cexoWVBvfyqd3XJs%2BIqWCpzkLmygFcG%2BLrXkcPWAO06NraVoczplL1KSxtivqwd4HlLlXWVzg9S5zPsrkp2JZgQ2REW0S%2BdrjrDSQ7bQHA71hmL4FAProdwv6qajQWxd1mSYBY8XUY%2F8l2kFi2ZDFH8xae1K%2BnqpOpvr3eS7iybeaNU0zc0Xaxsh8twauR5HwqN3X1d%2F0FIZ3i2fMDbjHI1%2FhLYVwlZYEIgdi92xiZwqmZGngrj3MO7a0dcGOqUBbnN2cHqUf9Wim8lWiqXWpi%2BjNQ0ZqOPs2BDpn1cHHcf01F6ZFnUZq4rmUqQ9zwi1bpfiEPcoQQ5f5YKhW4KMW3mQo7KoivnLc45DZOlh6mSrwqzXfnswujaOlvSOJdYMBqCVkVizBDy%2FhI9yr2FXVF6sL8g%2BM9h0VubabTvoFtd1DkCNMNInrpfQzZmBwxxH91rnLcpjC86fSZcVnodeFVBpyRAb&X-Amz-Signature=e828df138560abd2ca6aef8c62db79a0297a07e22fdc82536e0181046cc969e4&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.415b06d2-63bc-815f-9537-d10a019357d1.bb202fe9-e653-4278-8d2f-0d12906a5653)
<table header-row="true">
<tr>
<td>시각</td>
<td>실행</td>
<td>상태 변화의 이유</td>
</tr>
<tr>
<td>0→1</td>
<td>P1</td>
<td>P1이 1 tick에 완료, IDLE.</td>
</tr>
<tr>
<td>1→3</td>
<td>IDLE</td>
<td>인터럽트 완료 수가 0이라 반복이 계속된다. 큐가 비어 select_process가 아무것도 고르지 않아 시간만 흐른다.</td>
</tr>
<tr>
<td>3→5</td>
<td>I1</td>
<td>시각 3에 I1 도착, IDLE이므로 push 없음. 2 tick 처리 후 스택이 비어 IDLE로 끝난다.</td>
</tr>
</table>
**결과 분석:** P1은 T1에 끝났지만 아직 인터럽트가 남아 있어서 프로그램이 끝나지 않았다. 그동안 할 일이 없어 IDLE이 두 번 찍혔고, 이 2 tick도 TICKS 5에 들어갔다.
<empty-block/>
<empty-block/>
# 전체 소스코드
```c
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
```