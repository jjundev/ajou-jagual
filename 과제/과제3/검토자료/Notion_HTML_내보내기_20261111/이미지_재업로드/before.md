<table_of_contents color="gray"/>
<empty-block/>
# 구현 목적
하나의 CPU에서 프로세스와 인터럽트가 어떤 순서로 실행되는지 tick 단위로 시뮬레이션하는 프로그램이다. 프로세스는 퀀텀 2의 라운드로빈(round-robin)으로 돌고, 인터럽트가 오면 실행 중이던 작업을 스택에 넣어 두었다가 인터럽트가 끝나면 가장 최근에 멈춘 것부터 되돌린다.
<empty-block/>
<empty-block/>
# 소스코드 분석
HW3_skeleton.c의 선언, 제공 함수, main은 그대로 두고 비어 있던 select_process, start_interrupt, finish_tick을 구현한 HW3.c를 분석한다.
## 헤더·매크로·구조체·함수 원형
<table header-row="true">
<colgroup>
<col width="622">
<col width="390">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>#define _CRT_SECURE_NO_WARNINGS<br><br>#include \<stdio.h\><br>#include \<stdlib.h\><br><br>#define MAX_PROCESSES 8<br>#define MAX_INTERRUPTS 16<br>#define MAX_STACK_SIZE 16<br>#define MAX_QUEUE_SIZE (MAX_PROCESSES + 1)<br><br>#define QUANTUM 2<br>#define MAX_DURATION 10<br>#define MAX_ARRIVAL_TIME 1000<br>#define MAX_SIMULATION_TICKS \\<br>    (MAX_ARRIVAL_TIME + (MAX_PROCESSES + MAX_INTERRUPTS) \* MAX_DURATION)</td>
<td>_CRT_SECURE_NO_WARNINGS는 MSVC가 scanf에 내는 보안 경고를 끄는 매크로다. stdio.h는 scanf·printf 때문에, stdlib.h는 오류가 나면 프로그램을 끝내는 exit 때문에 포함했다.<br><br>MAX_PROCESSES(8)와 MAX_INTERRUPTS(16)는 입력할 수 있는 프로세스·인터럽트 수의 상한이고, MAX_STACK_SIZE(16)는 중단된 문맥을 쌓아 둘 칸 수다. MAX_QUEUE_SIZE가 MAX_PROCESSES보다 하나 많은 9인 데는 이유가 있다. 원형 큐는 빈 상태와 가득 찬 상태를 구분하려고 한 칸을 늘 비워 두기 때문에, 8개를 다 담으려면 9칸이 필요하다.<br><br>QUANTUM(2)은 프로세스가 CPU를 한 번 배정받았을 때 연달아 실행할 수 있는 최대 tick이다. MAX_DURATION(10)은 작업 하나의 실행 시간 상한, MAX_ARRIVAL_TIME(1000)은 인터럽트 도착 시각 상한이다.<br><br>MAX_SIMULATION_TICKS는 1000 + (8 + 16) × 10 = 1240이다. 마지막 인터럽트가 시각 1000에 와도 그 뒤에 남은 일은 모든 작업 시간의 합인 240을 넘지 못해, 정상 입력이라면 이 안에서 끝난다. tick이 이 값에 이르면 상태 전이가 꼬여 끝나지 않는 것으로 보고 main이 반복을 멈춘다.</td>
</tr>
<tr>
<td>typedef enum<br>\{<br>    IDLE,<br>    PROCESS,<br>    INTERRUPT<br>\} TaskType;<br><br>typedef struct<br>\{<br>    TaskType kind;<br>    int id;<br>    int remaining;<br>    int quantum_left;<br>\} Context;<br><br>const Context IDLE_CONTEXT = \{IDLE, 0, 0, 0\};</td>
<td>TaskType은 CPU가 지금 하는 일의 종류다. IDLE은 실행할 작업이 없는 상태, PROCESS는 라운드로빈으로 도는 프로세스, INTERRUPT는 인터럽트 처리를 뜻한다.<br><br>Context는 실행 중이거나 중단된 작업 하나의 문맥이다. kind는 종류, id는 입력 순서대로 매긴 번호, remaining은 남은 실행 시간, quantum_left는 이번 배정에서 남은 할당 시간이다. 멈췄던 작업을 이어서 돌리는 데 필요한 값은 이 네 개뿐이라, 스택과 큐에는 Context를 값 그대로 복사해 넣는다. 인터럽트는 라운드로빈 대상이 아니어서 quantum_left를 0으로 둔다.<br><br>IDLE_CONTEXT는 모든 값이 0인 IDLE 문맥이고, CPU를 비울 때 current에 대입한다. 열거형의 첫 값인 IDLE이 0이라서, 0으로 초기화한 Context가 IDLE_CONTEXT와 같다.</td>
</tr>
<tr>
<td>typedef struct<br>\{<br>    Context queue\[MAX_QUEUE_SIZE\];<br>    int front, rear;<br>\} ReadyQueue;<br><br>typedef struct<br>\{<br>    Context stack\[MAX_STACK_SIZE\];<br>    int top;<br>\} ContextStack;</td>
<td>ReadyQueue는 CPU를 기다리는 프로세스를 담는 원형 큐다. front는 첫 원소 바로 앞 칸을, rear는 마지막 원소가 있는 칸을 가리킨다. 먼저 들어온 프로세스가 먼저 나가는 구조(FIFO)라서, 퀀텀을 다 쓴 프로세스를 뒤에 넣으면 나머지 프로세스가 한 번씩 돈 다음에야 차례가 다시 온다.<br><br>ContextStack에는 인터럽트 때문에 멈춘 문맥이 쌓인다. top은 가장 최근에 넣은 칸의 인덱스이고, 비어 있을 때는 -1이다. 인터럽트가 겹치면 가장 나중에 멈춘 작업부터 다시 돌려야 하는데, 나중에 넣은 것을 먼저 꺼내는 스택(LIFO)이 바로 그 순서를 만든다.</td>
</tr>
<tr>
<td>typedef struct<br>\{<br>    ReadyQueue ready;<br>    ContextStack suspended;<br>    Context current;<br>    int tick;<br>    int finished_processes;<br>    int finished_interrupts;<br>\} Scheduler;<br><br>typedef struct<br>\{<br>    int arrival_time;<br>    int id;<br>    int duration;<br>\} InterruptEvent;</td>
<td>Scheduler는 시뮬레이션 상태 전체를 한데 묶은 구조체다. ready는 준비 큐, suspended는 중단 문맥 스택, current는 지금 CPU에서 돌고 있는 문맥이다. tick은 지금까지 흐른 tick 수이자 현재 시각이다. finished_processes와 finished_interrupts는 끝난 작업 수로, main의 반복 종료 조건에 쓰인다.<br><br>current는 포인터가 아니라 값이다. 그래서 큐에서 꺼내거나 스택에서 복원한 문맥은 current로 복사된다.<br><br>InterruptEvent는 미리 입력받아 둔 인터럽트 정보다. Context에는 없는 도착 시각 arrival_time이 있고, duration은 처리에 걸리는 시간이다. 도착 시각이 되면 start_interrupt가 이 정보로 INTERRUPT 문맥을 만든다.</td>
</tr>
<tr>
<td>int enqueue(ReadyQueue \*q, Context value);<br>Context dequeue(ReadyQueue \*q);<br>int push(ContextStack \*s, Context value);<br>Context pop(ContextStack \*s);<br>int execute_tick(Scheduler \*s);<br><br>void select_process(Scheduler \*s);<br>void start_interrupt(Scheduler \*s, InterruptEvent event);<br>void finish_tick(Scheduler \*s);</td>
<td>앞의 다섯 개는 제공 함수 가운데 큐·스택 조작 함수와 1 tick 실행 함수, 뒤의 세 개는 구현할 함수의 원형이다. 원형이 위에 있어 정의 순서와 상관없이 서로 부를 수 있다. 과제 조건대로 함수 형식·매크로·구조체는 손대지 않았고 함수도 새로 만들지 않았다.</td>
</tr>
</table>
<empty-block/>
## init_queue
제공 함수
<table header-row="true">
<colgroup>
<col width="329.6328125">
<col width="731">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void init_queue(ReadyQueue \*q)<br>\{<br>    q-\>front = q-\>rear = 0;<br>\}</td>
<td>front와 rear를 둘 다 0으로 맞춘다. 이 큐에서는 front == rear가 빈 상태라, 호출 직후 큐는 비어 있다.</td>
</tr>
</table>
<empty-block/>
## is_empty_queue
제공 함수
<table header-row="true">
<colgroup>
<col width="357">
<col width="713">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_empty_queue(const ReadyQueue \*q)<br>\{<br>    return q-\>front == q-\>rear;<br>\}</td>
<td>front와 rear가 같으면 꺼낼 원소가 없으므로 1을 돌려준다.</td>
</tr>
</table>
<empty-block/>
## is_full_queue
제공 함수
<table header-row="true">
<colgroup>
<col width="479">
<col width="592">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_full_queue(const ReadyQueue \*q)<br>\{<br>    return (q-\>rear + 1) % MAX_QUEUE_SIZE == q-\>front;<br>\}</td>
<td>rear 다음 칸이 front면 가득 찼다고 보고 1을 돌려준다. 9칸을 다 채우면 rear가 한 바퀴 돌아 front와 겹쳐 빈 큐와 구별이 안 되기 때문에, 9칸 중 8칸까지만 쓴다. % MAX_QUEUE_SIZE는 마지막 칸 다음을 0번 칸으로 돌려놓는 역할이다.</td>
</tr>
</table>
<empty-block/>
## enqueue
제공 함수
<table header-row="true">
<colgroup>
<col width="406">
<col width="665">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int enqueue(ReadyQueue \*q, Context value)<br>\{<br>    if (q == NULL \|\| is_full_queue(q))<br>    \{<br>        return 0;<br>    \}<br>    q-\>rear = (q-\>rear + 1) % MAX_QUEUE_SIZE;<br>    q-\>queue\[q-\>rear\] = value;<br>    return 1;<br>\}</td>
<td>rear를 원형으로 한 칸 옮기고 그 칸에 문맥을 복사한 뒤 1을 돌려준다. 큐가 없거나 가득 차 있으면 아무것도 바꾸지 않고 0을 돌려줘서, 실패했을 때 어떻게 할지는 호출한 쪽이 정한다. main이 처음 프로세스를 넣을 때와 finish_tick이 퀀텀을 다 쓴 프로세스를 되돌려 넣을 때 쓰인다.</td>
</tr>
</table>
<empty-block/>
## dequeue
제공 함수
<table header-row="true">
<colgroup>
<col width="422">
<col width="649">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>Context dequeue(ReadyQueue \*q)<br>\{<br>    if (q == NULL \|\| is_empty_queue(q))<br>    \{<br>        printf("QUEUE_ERROR\\n");<br>        exit(1);<br>    \}<br>    q-\>front = (q-\>front + 1) % MAX_QUEUE_SIZE;<br>    return q-\>queue\[q-\>front\];<br>\}</td>
<td>front를 한 칸 옮기면 그 칸이 맨 앞 원소다. 그 Context를 돌려주되 칸의 값은 지우지 않고, 나중에 enqueue가 덮어쓴다. 빈 큐에서 부르면 돌려줄 값이 없어 QUEUE_ERROR를 출력하고 exit(1)로 끝난다.</td>
</tr>
</table>
<empty-block/>
## init_stack
제공 함수
<table header-row="true">
<colgroup>
<col width="331.8125">
<col width="738">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void init_stack(ContextStack \*s)<br>\{<br>    s-\>top = -1;<br>\}</td>
<td>top을 -1로 두어 빈 스택을 만든다.</td>
</tr>
</table>
<empty-block/>
## is_empty_stack
제공 함수
<table header-row="true">
<colgroup>
<col width="374">
<col width="696">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_empty_stack(const ContextStack \*s)<br>\{<br>    return s-\>top == -1;<br>\}</td>
<td>top이 -1이면 저장된 문맥이 없다는 뜻이라 1을 돌려준다. finish_tick은 인터럽트가 끝났을 때 이 함수로 복원할 문맥이 있는지 본다.</td>
</tr>
</table>
<empty-block/>
## is_full_stack
제공 함수
<table header-row="true">
<colgroup>
<col width="366">
<col width="705">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int is_full_stack(const ContextStack \*s)<br>\{<br>    return s-\>top == MAX_STACK_SIZE - 1;<br>\}</td>
<td>top이 마지막 인덱스 15에 닿으면 1을 돌려준다.</td>
</tr>
</table>
<empty-block/>
## push
제공 함수
<table header-row="true">
<colgroup>
<col width="366">
<col width="705">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int push(ContextStack \*s, Context value)<br>\{<br>    if (s == NULL \|\| is_full_stack(s))<br>    \{<br>        return 0;<br>    \}<br>    s-\>stack\[++(s-\>top)\] = value;<br>    return 1;<br>\}</td>
<td>top을 먼저 1 올리고(++top) 그 칸에 문맥을 복사한 뒤 1을 돌려준다. 스택이 없거나 가득 찼으면 0이다. start_interrupt가 중단되는 작업의 문맥을 저장할 때 쓴다.</td>
</tr>
</table>
<empty-block/>
## pop
제공 함수
<table header-row="true">
<colgroup>
<col width="357">
<col width="713">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>Context pop(ContextStack \*s)<br>\{<br>    if (s == NULL \|\| is_empty_stack(s))<br>    \{<br>        printf("STACK_ERROR\\n");<br>        exit(1);<br>    \}<br>    return s-\>stack\[(s-\>top)--\];<br>\}</td>
<td>top 칸의 Context를 돌려주고 top을 1 내린다(top--). 빈 스택에서 부르면 STACK_ERROR를 출력하고 exit(1)로 끝난다. finish_tick은 인터럽트가 끝나면 이 함수로 가장 최근에 멈춘 작업을 되돌린다.</td>
</tr>
</table>
<empty-block/>
## select_process
구현 함수
<table header-row="true">
<colgroup>
<col width="535">
<col width="535">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void select_process(Scheduler \*s)<br>\{<br>    if (s-\>current.kind != IDLE \|\| is_empty_queue(&s-\>ready))<br>    \{<br>        return;<br>    \}<br>    s-\>current = dequeue(&s-\>ready);<br>    s-\>current.quantum_left = QUANTUM;<br>\}</td>
<td>CPU가 비어 있으면 준비 큐 맨 앞 프로세스를 꺼내 current로 삼는다. main이 이 함수를 매 tick 부르기 때문에, 프로세스든 인터럽트든 이미 무언가 실행 중이면(current.kind가 IDLE이 아니면) 그대로 돌아가야 한다. 이 검사가 없으면 실행 중인 작업이 tick마다 바뀌어 버린다.<br><br>준비 큐가 비어 있을 때도 손대지 않는다. current가 IDLE로 남고, execute_tick은 시간만 흘려보낸다. 큐가 비었는지 먼저 확인하니 dequeue가 빈 큐에서 QUEUE_ERROR로 끝날 일도 없다.<br><br>꺼낸 프로세스의 quantum_left는 QUANTUM(2)으로 정한다. 큐로 돌아온 프로세스는 quantum_left가 0이라, CPU를 새로 받을 때마다 2 tick을 다시 받는다. 반면 인터럽트가 끝나 스택에서 복원된 프로세스는 current가 IDLE이 아니어서 이 함수가 건드리지 않는다. 그래서 중단 전에 남아 있던 quantum_left를 그대로 이어 쓴다.</td>
</tr>
</table>
<empty-block/>
## start_interrupt
구현 함수
<table header-row="true">
<colgroup>
<col width="591">
<col width="480">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void start_interrupt(Scheduler \*s, InterruptEvent event)<br>\{<br>    if (s-\>current.kind != IDLE && !push(&s-\>suspended, s-\>current))<br>    \{<br>        printf("SIMULATION_ERROR\\n");<br>        exit(2);<br>    \}<br>    s-\>current.kind = INTERRUPT;<br>    s-\>current.id = event.id;<br>    s-\>current.remaining = event.duration;<br>    s-\>current.quantum_left = 0;<br>\}</td>
<td>인자: 스케줄러, 도착한 인터럽트 정보. 반환값: 없음.<br><br>current가 IDLE이 아니면 그 문맥을 스택에 push한다. 문맥 전환(context switch)에서 저장에 해당하는 단계다. 멈춘 것이 프로세스든 처리 중이던 인터럽트든 remaining과 quantum_left가 중단 시점 값 그대로 저장되고, 나중에 꺼내면 그 상태에서 다시 이어진다. IDLE은 돌아갈 작업이 아니라서 저장하지 않는다. &&의 단락 평가(short-circuit evaluation) 덕분에 current가 IDLE이면 push는 호출조차 되지 않는다.<br><br>push 실패를 무시하고 current를 바꾸면 문맥이 사라진다. 사라진 작업은 완료되지 않아 정상 종료할 수 없으니, main의 다른 시뮬레이션 오류처럼 SIMULATION_ERROR를 출력하고 종료 코드 2로 끝내도록 했다. 정상 입력이라면 스택에는 실행 중인 하나를 뺀 인터럽트 최대 15개와 프로세스 1개, 합쳐 16개까지만 쌓여 이 분기에 오지 않는다.<br><br>그다음 current를 새 인터럽트로 바꾼다. id와 남은 시간은 입력 정보에서 가져오고, 인터럽트에는 퀀텀이 없어 quantum_left는 0이다. execute_tick은 인터럽트의 quantum_left를 검사하지도 줄이지도 않기 때문에, 인터럽트는 퀀텀 소진으로 중단되지 않는다.</td>
</tr>
</table>
<empty-block/>
## finish_tick
구현 함수
<table header-row="true">
<colgroup>
<col width="583">
<col width="487">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>void finish_tick(Scheduler \*s)<br>\{<br>    Context \*current = &s-\>current;<br>    if (current-\>kind == PROCESS)<br>    \{<br>        if (current-\>remaining == 0)<br>        \{<br>            s-\>finished_processes++;<br>            \*current = IDLE_CONTEXT;<br>        \}<br>        else if (current-\>quantum_left == 0)<br>        \{<br>            if (!enqueue(&s-\>ready, \*current))<br>            \{<br>                printf("SIMULATION_ERROR\\n");<br>                exit(2);<br>            \}<br>            \*current = IDLE_CONTEXT;<br>        \}<br>    \}</td>
<td>execute_tick으로 1 tick을 돌린 직후, 그 결과를 보고 다음 tick의 current를 정리한다. 지역 변수 current는 s-\>current를 가리키는 포인터여서, 이것으로 바꾼 값은 스케줄러에 바로 반영된다.<br><br>current가 프로세스인 경우.<br><br>프로세스의 remaining이 0이면 완료다. 완료 수를 1 늘리고 CPU를 IDLE로 비워, 다음 tick에 select_process가 다른 프로세스를 고를 수 있게 한다.<br><br>완료는 아닌데 quantum_left가 0이면 퀀텀을 다 쓴 경우다. 프로세스를 준비 큐 맨 뒤에 넣고 CPU를 비운다. 완료 검사를 앞에 둔 건 두 값이 같은 tick에 함께 0이 될 수 있기 때문이다(추가 사례 1·2). 순서가 반대라면 끝난 프로세스가 큐로 들어가 완료 수가 늘지 않는다. 그러다 다시 선택되면 execute_tick이 남은 시간 0을 보고 SIMULATION_ERROR로 끝난다.<br><br>정상 입력에서 enqueue가 실패할 일은 없다. 실행 중인 프로세스는 큐 밖에 있어 큐에는 많아야 7개만 들어 있기 때문이다. 그래도 문맥을 잃지 않도록 start_interrupt와 같은 방식으로 처리했다. 두 조건 모두 아니면 아무것도 하지 않고, 다음 tick에도 같은 프로세스가 이어서 실행된다.</td>
</tr>
<tr>
<td>    else if (current-\>kind == INTERRUPT && current-\>remaining == 0)<br>    \{<br>        s-\>finished_interrupts++;<br>        if (is_empty_stack(&s-\>suspended))<br>        \{<br>            \*current = IDLE_CONTEXT;<br>        \}<br>        else<br>        \{<br>            \*current = pop(&s-\>suspended);<br>        \}<br>    \}<br>\}</td>
<td>인터럽트가 끝난 경우.<br><br>인터럽트의 remaining이 0이면 처리가 끝난 것이다. 인터럽트 완료 수를 늘리고, 스택이 비어 있으면 돌아갈 작업이 없으니 IDLE로 바꾼다. 비어 있지 않으면 pop으로 가장 최근에 멈춘 문맥을 current로 되돌린다. 인터럽트가 겹쳤던 경우라면 이때 나오는 것은 바깥쪽 인터럽트이고, 바깥쪽 인터럽트들이 모두 끝나야 처음 멈췄던 프로세스가 나온다.<br><br>빈 스택인지 먼저 확인하기 때문에 pop이 STACK_ERROR로 끝나는 일은 없다. 인터럽트가 아직 남았거나 current가 IDLE이면 아무것도 바꾸지 않는다. 다음 프로세스를 고르는 일은 select_process의 몫이다.</td>
</tr>
</table>
<empty-block/>
## execute_tick
제공 함수
<table header-row="true">
<colgroup>
<col width="664">
<col width="407">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int execute_tick(Scheduler \*s)<br>\{<br>    Context \*current = &s-\>current;<br>    if ((current-\>kind != IDLE && current-\>remaining \<= 0) \|\|<br>        (current-\>kind == PROCESS && current-\>quantum_left \<= 0))<br>    \{<br>        return 0;<br>    \}</td>
<td>반환값: 1 또는 0.<br><br>1 tick을 실행했으면 1, 실행할 수 없는 상태면 0을 돌려준다.<br><br>먼저 current가 실행 가능한지 본다. IDLE이 아닌 작업의 남은 시간이 0 이하이거나 프로세스의 퀀텀이 0 이하이면 바로 0이다(조기 반환, early return). finish_tick이 끝난 작업과 퀀텀을 다 쓴 프로세스를 제대로 치웠다면 나올 수 없는 상태라, 사실상 구현 함수의 상태 전이를 점검하는 장치다. main은 0을 받으면 SIMULATION_ERROR로 끝낸다.</td>
</tr>
<tr>
<td>    if (current-\>kind != IDLE)<br>    \{<br>        current-\>remaining--;<br>    \}<br>    s-\>tick++;<br>    if (current-\>kind == PROCESS)<br>    \{<br>        current-\>quantum_left--;<br>        printf("T%3d P%2d R%2d Q%2d\\n", s-\>tick,<br>               current-\>id, current-\>remaining, current-\>quantum_left);<br>    \}<br>    else if (current-\>kind == INTERRUPT)<br>    \{<br>        printf("T%3d I%2d R%2d\\n", s-\>tick, current-\>id, current-\>remaining);<br>    \}<br>    else<br>    \{<br>        printf("T%3d IDLE\\n", s-\>tick);<br>    \}<br>    return 1;<br>\}</td>
<td>IDLE이 아니면 남은 시간을 1 줄이고, 어떤 경우든 tick은 1 늘린다. IDLE이면 실행 없이 시간만 지나간다.<br><br>프로세스라면 퀀텀도 1 줄인다. 출력하는 T 값은 tick을 늘린 뒤의 시각이라, T 1은 시각 0부터 1까지의 실행 결과다. 프로세스는 번호·남은 시간(R)·남은 퀀텀(Q)을, 인터럽트는 번호와 남은 시간을, IDLE은 IDLE을 찍는다. 완료·재등록·복원은 출력 뒤에 finish_tick이 맡는다.</td>
</tr>
</table>
<empty-block/>
## main
제공 함수
<table header-row="true">
<colgroup>
<col width="684">
<col width="387">
</colgroup>
<tr>
<td>소스코드</td>
<td>기능 명세와 분석</td>
</tr>
<tr>
<td>int main(void)<br>\{<br>    Context processes\[MAX_PROCESSES\] = \{0\};<br>    InterruptEvent interrupts\[MAX_INTERRUPTS\] = \{0\};<br>    int process_count, interrupt_count;<br>    Scheduler s = \{0\};<br>    int next_interrupt = 0;<br><br>    if (scanf("%d %d", &process_count, &interrupt_count) != 2 \|\|<br>        process_count \< 1 \|\| process_count \> MAX_PROCESSES \|\|<br>        interrupt_count \< 0 \|\| interrupt_count \> MAX_INTERRUPTS)<br>    \{<br>        printf("INPUT_ERROR\\n");<br>        return 1;<br>    \}</td>
<td>정상 종료면 0, 입력 오류면 1, 시뮬레이션 오류면 2를 돌려준다.<br><br>입력받을 프로세스·인터럽트 배열과 개수, 스케줄러 s, 다음에 처리할 인터럽트 인덱스 next_interrupt를 선언한다. s = \{0\}이라 tick과 완료 수는 0이고, current도 모든 필드가 0이어서 IDLE_CONTEXT와 같다.<br><br>첫 줄에서 프로세스 수 N과 인터럽트 수 M을 읽고, N이 1\~8, M이 0\~16 안에 드는지 확인한다. 과제는 입력이 정상이라고 가정하지만 제공 코드에는 이 검사가 들어 있다.</td>
</tr>
<tr>
<td>    for (int i = 0; i \< process_count; i++)<br>    \{<br>        if (scanf("%d", &processes\[i\].remaining) != 1 \|\|<br>            processes\[i\].remaining \< 1 \|\| processes\[i\].remaining \> MAX_DURATION)<br>        \{<br>            printf("INPUT_ERROR\\n");<br>            return 1;<br>        \}<br>        processes\[i\].id = i + 1;<br>        processes\[i\].kind = PROCESS;<br>    \}</td>
<td>다음 N줄에서 프로세스마다 실행 시간을 remaining에 읽고, 1\~10 범위인지 본다. id는 입력 순서대로 1부터 붙이고 kind는 PROCESS로 둔다. quantum_left는 0인 채로 두는데, 실제 값은 select_process가 CPU를 배정할 때 정한다.</td>
</tr>
<tr>
<td>    for (int i = 0; i \< interrupt_count; i++)<br>    \{<br>        if (scanf("%d %d", &interrupts\[i\].arrival_time,<br>                  &interrupts\[i\].duration) != 2 \|\|<br>            interrupts\[i\].arrival_time \< 0 \|\| interrupts\[i\].arrival_time \> MAX_ARRIVAL_TIME \|\|<br>            interrupts\[i\].duration \< 1 \|\| interrupts\[i\].duration \> MAX_DURATION \|\|<br>            (i \> 0 && interrupts\[i\].arrival_time \<= interrupts\[i - 1\].arrival_time))<br>        \{<br>            printf("INPUT_ERROR\\n");<br>            return 1;<br>        \}<br>        interrupts\[i\].id = i + 1;<br>    \}</td>
<td>그다음 M줄에서 인터럽트의 도착 시각과 처리 시간을 읽는다. 도착 시각은 0\~1000, 처리 시간은 1\~10이어야 하고, 앞 인터럽트보다 늦게 도착해야 한다. 도착 시각이 계속 커지니 main은 next_interrupt 하나만 보면서 차례로 처리하면 되고, 한 시각에 인터럽트가 둘 이상 오는 일도 없다.</td>
</tr>
<tr>
<td>    init_queue(&s.ready);<br>    init_stack(&s.suspended);<br><br>    for (int i = 0; i \< process_count; i++)<br>    \{<br>        if (!enqueue(&s.ready, processes\[i\]))<br>        \{<br>            printf("SIMULATION_ERROR\\n");<br>            return 2;<br>        \}<br>    \}</td>
<td>큐와 스택을 초기화한 뒤 모든 프로세스를 입력 순서대로 준비 큐에 넣는다. 모든 프로세스가 시각 0에 도착한다는 규칙이 이 코드로 표현된다. 프로세스는 많아야 8개이고 큐도 8개까지 담을 수 있어, 정상 입력이라면 enqueue가 실패하지 않는다.</td>
</tr>
<tr>
<td>    while (s.finished_processes \< process_count \|\|<br>           s.finished_interrupts \< interrupt_count)<br>    \{<br>        if (s.tick \>= MAX_SIMULATION_TICKS)<br>        \{<br>            printf("SIMULATION_ERROR\\n");<br>            return 2;<br>        \}<br><br>        if (next_interrupt \< interrupt_count &&<br>            interrupts\[next_interrupt\].arrival_time == s.tick)<br>        \{<br>            start_interrupt(&s, interrupts\[next_interrupt\]);<br>            next_interrupt++;<br>        \}<br>        select_process(&s);<br>        if (!execute_tick(&s))<br>        \{<br>            printf("SIMULATION_ERROR\\n");<br>            return 2;<br>        \}<br>        finish_tick(&s);<br>    \}</td>
<td>프로세스와 인터럽트가 모두 끝날 때까지 1 tick씩 반복한다. 프로세스가 다 끝났더라도 아직 오지 않은 인터럽트가 있으면 IDLE로 시간을 보내며 기다린다(추가 사례 4).<br><br>반복 한 번은 과제가 정한 실행 흐름을 그대로 따른다. ① 현재 시각에 도착한 인터럽트가 있으면 start_interrupt로 시작한다. ② CPU가 비었다면 select_process가 프로세스를 고른다. ③ execute_tick이 1 tick을 실행하고 출력한다. ④ finish_tick이 완료·재등록·복원을 처리한다.<br><br>인터럽트 처리가 프로세스 선택보다 앞서 있어서, 같은 시각에 CPU가 비어 있으면 인터럽트가 먼저 CPU를 잡고 프로세스는 큐에서 계속 기다린다(추가 사례 3). execute_tick은 성공할 때마다 tick을 반드시 1 늘리니 도착 시각을 건너뛸 일이 없다. tick이 상한에 닿거나 execute_tick이 0을 돌려주면 SIMULATION_ERROR로 끝낸다.</td>
</tr>
<tr>
<td>    printf("FINISHED %d INTERRUPTS %d TICKS %d\\n",<br>           s.finished_processes, s.finished_interrupts, s.tick);<br>    return 0;<br>\}</td>
<td>반복을 빠져나오면 완료한 프로세스 수, 인터럽트 수, 전체 tick을 한 줄로 출력하고 0을 반환한다.</td>
</tr>
</table>
<empty-block/>
<empty-block/>
# 실행결과 및 분석
과제 18쪽의 공식 예시 1건과, 공식 예시에서 드러나지 않는 동작을 보여 주는 추가 사례 4건을 실행했다. 각 사례에서 입력과 실제 출력을 제시하고, tick마다 큐·스택·current가 어떻게 바뀌어 그 출력이 나왔는지 분석한다.
<empty-block/>
## 공식 예시: 중첩 인터럽트와 라운드로빈
**입력**
```plain text
2 2
3
1
1 2
2 1
```
<empty-block/>
**실제 출력**
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
<table header-row="true">
<colgroup>
<col>
<col>
<col width="830">
</colgroup>
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
결과 분석: 출력 순서 P1 I1 I2 I1 P1 P2 P1은 과제 18쪽 실행 화면·간트 차트와 같다. 시각 2에 I2가 I1을 끊었고(선점, preemption), I2가 끝나자 처음 멈춘 P1이 아니라 가장 최근에 멈춘 I1이 먼저 다시 실행되었다. 같은 P1인데 T5에는 Q 0, T7에는 Q 1이 찍힌 것도 차이가 있다. T5는 T1에서 쓰고 남긴 퀀텀 1을 복원 뒤 이어 쓴 결과이고, T7은 큐에서 다시 선택되며 퀀텀 2를 새로 받은 결과다.
<empty-block/>
**실제 터미널 실행 화면**
![T3에서 I2가 I1을 끊고, T3·T4 종료 후 I1 → P1 순서로 스택이 풀린다.](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/9bd1ea8c-6cb8-45e0-af44-188de766f29d/01-%EA%B3%B5%EC%8B%9D%EC%98%88%EC%8B%9C.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466WLIUTVBM%2F20261110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261110T155020Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEHYaCXVzLXdlc3QtMiJHMEUCIQCRz6RFCksLB4BIzOQifXDu0eRCWM9PGAfM%2Bo9nE4VSMgIgYQfo%2BYvDQETvXIpi33U9qcKdj8lzP8p%2B9mUqrkycXswq%2FwMIPhAAGgw2Mzc0MjMxODM4MDUiDK0%2FtSe9tbguWGgMqyrcAxMt5neww5QnFaJLROdIT9AmURl%2FqmktGxWnB5gs0xNa5EURMluajnYwI9i7yWJdDeQpdddNi9uQSgfMTs994BhSr4gHh6doq2PwKeSPADm1u8W3vErOUX8oYwLqu8Sfd2ny7NtvQmjLakPDMPWFA362xpHKXqYANtZDv257bT38RK%2Fiy6%2BdeA4LNuFFU5eKyPhajYWKu%2FNPk6FL96MUSZ%2Fk%2B6IRDM%2FqqWpRkC4vCjVq2BlTxkPbkW8TJRplVG2L73LDklwVuMlACYMb2YNRyG5vhaL5B2HVKYMV%2FvuEULxOi8yhe8yKRF1nxehJOxtLv%2FPgY%2B1dZjfM0AWJq5Gc0umBTbEZpORntXlqaVvHEYSo59ws1NDTJ4SjS4ADypMy4KB%2BFahB1IH2EcAqRWmRZFBq0VCuPJmMVmKLBplBeARcVujCJ3%2Fijh%2F4g7eQMpFrRenTwgJdlWnF9O%2FHgNlnSQ%2FTSjm%2BUn6rABeUDuegr%2FZBOqtzapEkbN7YjnfzEepSN%2BLEAH%2BvmNfzKb1ZSWVe07ef3BG2Dmga7UGX%2FZEPTN0bl0Yhzs2lg5uFtlHq7Km05VY5jAbooUbYXGyprR1IsccpOtimK89U7UJflIe77PzFML0dS0IVUYQxPJ5mMKyzzNcGOqUB9%2BQvWeySMjOQdwPR6WskUIKvq3x6AlS6nogcqVpQ9eM2MCjtTYoBWkRPOZeg9N%2FBshEBqdla0CIDNOOHcMKGnhUNj6hzAZM9spDq%2B2gW%2FWKAFVM4lrf9nsGwqpxQL1cRz%2FXG5T%2BxbkbDJKLS%2BLoM35gAWxp4UauDdjILOAocLby%2F5K6st0f1cz%2BrRQr3EGtU9ILqjt4iW8t6jnpSxefUbuuvISkl&X-Amz-Signature=9e1a7e657bc04e4e327fc687ff1fc5c419a75b0edf80317ac61fd166a399aa14&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.408b06d2-63bc-8131-ac8f-d7876599315d.bb202fe9-e653-4278-8d2f-0d12906a5653)
<empty-block/>
## 추가 사례 1: 세 겹 중첩 인터럽트
인터럽트가 세 번 겹칠 때도 스택이 중단된 역순으로 문맥을 복원하는지 확인한다.
**입력**
```plain text
1 3
4
1 3
2 3
3 1
```
<empty-block/>
**실제 출력**
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
<table header-row="true">
<colgroup>
<col>
<col>
<col width="830">
</colgroup>
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
<td>큐에 P1뿐이므로 다시 꺼내 Q=2. T11에 R0과 Q0이 동시에 되고, 완료가 먼저 검사되어 완료로 처리.</td>
</tr>
</table>
결과 분석: 인터럽트는 I1, I2, I3 순으로 시작했는데 끝난 순서는 I3, I2, I1이다. 스택에 늦게 들어간 문맥일수록 먼저 나와서, 마지막에 넣은 I2가 가장 먼저, 처음 넣은 P1이 가장 늦게 복원되었다. 이 과정에서 스택에는 문맥이 최대 3개까지 쌓였다. 중첩 깊이가 셋이라서 그렇다. I2와 I1은 멈추기 전에 남아 있던 2 tick씩을 이어서 실행했다. 맨 끝 T11에서는 남은 시간과 퀀텀이 동시에 0이 됐지만 완료로 처리되어 FINISHED 1이 출력되었다.
<empty-block/>
**실제 터미널 실행 화면**
![I1·I2·I3가 순서대로 시작되고 역순으로 완료된다. T4·T6·T8이 끝날 때마다 pop이 일어나 T5·T7·T9에 I2·I1·P1이 이어서 실행된다.](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/7cfcb9a1-ee2c-44a3-87de-82e044e365de/02-%EC%84%B8%EA%B2%B9%EC%A4%91%EC%B2%A9.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466WLIUTVBM%2F20261110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261110T155020Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEHYaCXVzLXdlc3QtMiJHMEUCIQCRz6RFCksLB4BIzOQifXDu0eRCWM9PGAfM%2Bo9nE4VSMgIgYQfo%2BYvDQETvXIpi33U9qcKdj8lzP8p%2B9mUqrkycXswq%2FwMIPhAAGgw2Mzc0MjMxODM4MDUiDK0%2FtSe9tbguWGgMqyrcAxMt5neww5QnFaJLROdIT9AmURl%2FqmktGxWnB5gs0xNa5EURMluajnYwI9i7yWJdDeQpdddNi9uQSgfMTs994BhSr4gHh6doq2PwKeSPADm1u8W3vErOUX8oYwLqu8Sfd2ny7NtvQmjLakPDMPWFA362xpHKXqYANtZDv257bT38RK%2Fiy6%2BdeA4LNuFFU5eKyPhajYWKu%2FNPk6FL96MUSZ%2Fk%2B6IRDM%2FqqWpRkC4vCjVq2BlTxkPbkW8TJRplVG2L73LDklwVuMlACYMb2YNRyG5vhaL5B2HVKYMV%2FvuEULxOi8yhe8yKRF1nxehJOxtLv%2FPgY%2B1dZjfM0AWJq5Gc0umBTbEZpORntXlqaVvHEYSo59ws1NDTJ4SjS4ADypMy4KB%2BFahB1IH2EcAqRWmRZFBq0VCuPJmMVmKLBplBeARcVujCJ3%2Fijh%2F4g7eQMpFrRenTwgJdlWnF9O%2FHgNlnSQ%2FTSjm%2BUn6rABeUDuegr%2FZBOqtzapEkbN7YjnfzEepSN%2BLEAH%2BvmNfzKb1ZSWVe07ef3BG2Dmga7UGX%2FZEPTN0bl0Yhzs2lg5uFtlHq7Km05VY5jAbooUbYXGyprR1IsccpOtimK89U7UJflIe77PzFML0dS0IVUYQxPJ5mMKyzzNcGOqUB9%2BQvWeySMjOQdwPR6WskUIKvq3x6AlS6nogcqVpQ9eM2MCjtTYoBWkRPOZeg9N%2FBshEBqdla0CIDNOOHcMKGnhUNj6hzAZM9spDq%2B2gW%2FWKAFVM4lrf9nsGwqpxQL1cRz%2FXG5T%2BxbkbDJKLS%2BLoM35gAWxp4UauDdjILOAocLby%2F5K6st0f1cz%2BrRQr3EGtU9ILqjt4iW8t6jnpSxefUbuuvISkl&X-Amz-Signature=93eea7dbb49f90e0ee6f577e0476bb316e72c6bfadc0db23c6f16765484b7509&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.408b06d2-63bc-811f-95ef-e062bd2bcfaa.bb202fe9-e653-4278-8d2f-0d12906a5653)
<empty-block/>
## 추가 사례 2: 완료와 퀀텀 소진이 같은 tick
실행 시간이 퀀텀과 같은 2인 프로세스가 큐로 돌아가지 않고 완료되는지 확인한다.
**입력**
```plain text
2 0
2
1
```
<empty-block/>
**실제 출력**
```plain text
T  1 P 1 R 1 Q 1
T  2 P 1 R 0 Q 0
T  3 P 2 R 0 Q 1
FINISHED 2 INTERRUPTS 0 TICKS 3
```
<table header-row="true">
<colgroup>
<col>
<col>
<col width="830">
</colgroup>
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
결과 분석: P1은 T2에 퀀텀을 다 썼지만 남은 시간도 0이 되어 준비 큐로 돌아가지 않았다. 그래서 바로 다음 tick에 P2가 실행됐고, P1이 다시 선택되는 일은 없었다.
<empty-block/>
**실제 터미널 실행 화면**
![T2에서 R·Q가 함께 0이 되자 P1이 큐에 되들어가지 않고 그대로 종료된다.](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/a6ce555e-db10-4d71-8282-42abc8bb1155/03-%EC%99%84%EB%A3%8C%EC%99%80%ED%80%80%ED%85%80%EB%8F%99%EC%8B%9C.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466WLIUTVBM%2F20261110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261110T155020Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEHYaCXVzLXdlc3QtMiJHMEUCIQCRz6RFCksLB4BIzOQifXDu0eRCWM9PGAfM%2Bo9nE4VSMgIgYQfo%2BYvDQETvXIpi33U9qcKdj8lzP8p%2B9mUqrkycXswq%2FwMIPhAAGgw2Mzc0MjMxODM4MDUiDK0%2FtSe9tbguWGgMqyrcAxMt5neww5QnFaJLROdIT9AmURl%2FqmktGxWnB5gs0xNa5EURMluajnYwI9i7yWJdDeQpdddNi9uQSgfMTs994BhSr4gHh6doq2PwKeSPADm1u8W3vErOUX8oYwLqu8Sfd2ny7NtvQmjLakPDMPWFA362xpHKXqYANtZDv257bT38RK%2Fiy6%2BdeA4LNuFFU5eKyPhajYWKu%2FNPk6FL96MUSZ%2Fk%2B6IRDM%2FqqWpRkC4vCjVq2BlTxkPbkW8TJRplVG2L73LDklwVuMlACYMb2YNRyG5vhaL5B2HVKYMV%2FvuEULxOi8yhe8yKRF1nxehJOxtLv%2FPgY%2B1dZjfM0AWJq5Gc0umBTbEZpORntXlqaVvHEYSo59ws1NDTJ4SjS4ADypMy4KB%2BFahB1IH2EcAqRWmRZFBq0VCuPJmMVmKLBplBeARcVujCJ3%2Fijh%2F4g7eQMpFrRenTwgJdlWnF9O%2FHgNlnSQ%2FTSjm%2BUn6rABeUDuegr%2FZBOqtzapEkbN7YjnfzEepSN%2BLEAH%2BvmNfzKb1ZSWVe07ef3BG2Dmga7UGX%2FZEPTN0bl0Yhzs2lg5uFtlHq7Km05VY5jAbooUbYXGyprR1IsccpOtimK89U7UJflIe77PzFML0dS0IVUYQxPJ5mMKyzzNcGOqUB9%2BQvWeySMjOQdwPR6WskUIKvq3x6AlS6nogcqVpQ9eM2MCjtTYoBWkRPOZeg9N%2FBshEBqdla0CIDNOOHcMKGnhUNj6hzAZM9spDq%2B2gW%2FWKAFVM4lrf9nsGwqpxQL1cRz%2FXG5T%2BxbkbDJKLS%2BLoM35gAWxp4UauDdjILOAocLby%2F5K6st0f1cz%2BrRQr3EGtU9ILqjt4iW8t6jnpSxefUbuuvISkl&X-Amz-Signature=04af3f1962e67c7ee722fb50a4d42163ae6b00d90d3777d8a3791c49244ff2f1&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.408b06d2-63bc-8127-84f5-e7e8f0babba5.bb202fe9-e653-4278-8d2f-0d12906a5653)
<empty-block/>
## 추가 사례 3: CPU가 빈 순간에 도착한 인터럽트
퀀텀 소진 직후 IDLE인 시각에 인터럽트가 오면 아무것도 저장하지 않고, 큐 순서가 유지되는지 확인한다.
**입력**
```plain text
2 1
3
2
2 1
```
<empty-block/>
**실제 출력**
```plain text
T  1 P 1 R 2 Q 1
T  2 P 1 R 1 Q 0
T  3 I 1 R 0
T  4 P 2 R 1 Q 1
T  5 P 2 R 0 Q 0
T  6 P 1 R 0 Q 1
FINISHED 2 INTERRUPTS 1 TICKS 6
```
<table header-row="true">
<colgroup>
<col>
<col>
<col width="830">
</colgroup>
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
결과 분석: 시각 2에는 P1이 이미 큐로 돌아간 뒤라 멈춰 둘 작업이 없었다. 그래서 I1이 끝났을 때 스택은 비어 있었고 CPU는 IDLE이 되었다. 그 뒤로는 큐 순서 \[P2, P1\] 그대로 P2, P1이 실행되었다. T3에 P2가 아니라 I1이 실행된 건, CPU가 빈 같은 시각이라도 main이 인터럽트를 먼저 시작하기 때문이다.
<empty-block/>
**실제 터미널 실행 화면**
![I1이 끝난 T3에서 스택이 비어 CPU가 비고, T4부터 큐의 P2가 실행된다.](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/722583e0-d4a0-4b8f-adfd-f7867cd4491e/04-IDLE%EC%A4%91%EC%9D%B8%ED%84%B0%EB%9F%BD%ED%8A%B8.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466WLIUTVBM%2F20261110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261110T155020Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEHYaCXVzLXdlc3QtMiJHMEUCIQCRz6RFCksLB4BIzOQifXDu0eRCWM9PGAfM%2Bo9nE4VSMgIgYQfo%2BYvDQETvXIpi33U9qcKdj8lzP8p%2B9mUqrkycXswq%2FwMIPhAAGgw2Mzc0MjMxODM4MDUiDK0%2FtSe9tbguWGgMqyrcAxMt5neww5QnFaJLROdIT9AmURl%2FqmktGxWnB5gs0xNa5EURMluajnYwI9i7yWJdDeQpdddNi9uQSgfMTs994BhSr4gHh6doq2PwKeSPADm1u8W3vErOUX8oYwLqu8Sfd2ny7NtvQmjLakPDMPWFA362xpHKXqYANtZDv257bT38RK%2Fiy6%2BdeA4LNuFFU5eKyPhajYWKu%2FNPk6FL96MUSZ%2Fk%2B6IRDM%2FqqWpRkC4vCjVq2BlTxkPbkW8TJRplVG2L73LDklwVuMlACYMb2YNRyG5vhaL5B2HVKYMV%2FvuEULxOi8yhe8yKRF1nxehJOxtLv%2FPgY%2B1dZjfM0AWJq5Gc0umBTbEZpORntXlqaVvHEYSo59ws1NDTJ4SjS4ADypMy4KB%2BFahB1IH2EcAqRWmRZFBq0VCuPJmMVmKLBplBeARcVujCJ3%2Fijh%2F4g7eQMpFrRenTwgJdlWnF9O%2FHgNlnSQ%2FTSjm%2BUn6rABeUDuegr%2FZBOqtzapEkbN7YjnfzEepSN%2BLEAH%2BvmNfzKb1ZSWVe07ef3BG2Dmga7UGX%2FZEPTN0bl0Yhzs2lg5uFtlHq7Km05VY5jAbooUbYXGyprR1IsccpOtimK89U7UJflIe77PzFML0dS0IVUYQxPJ5mMKyzzNcGOqUB9%2BQvWeySMjOQdwPR6WskUIKvq3x6AlS6nogcqVpQ9eM2MCjtTYoBWkRPOZeg9N%2FBshEBqdla0CIDNOOHcMKGnhUNj6hzAZM9spDq%2B2gW%2FWKAFVM4lrf9nsGwqpxQL1cRz%2FXG5T%2BxbkbDJKLS%2BLoM35gAWxp4UauDdjILOAocLby%2F5K6st0f1cz%2BrRQr3EGtU9ILqjt4iW8t6jnpSxefUbuuvISkl&X-Amz-Signature=5c2668dcddedbcba8ff30f8eaa935387c3298cd324245e8aa0cad980125eb21f&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.408b06d2-63bc-81da-8ae6-cf723f96e1f1.bb202fe9-e653-4278-8d2f-0d12906a5653)
<empty-block/>
## 추가 사례 4: 프로세스가 모두 끝난 뒤의 인터럽트
실행할 작업이 없는 동안 IDLE로 시간이 흐르고, 늦게 도착한 인터럽트까지 처리한 뒤 끝나는지 확인한다.
**입력**
```plain text
1 1
1
3 2
```
<empty-block/>
**실제 출력**
```plain text
T  1 P 1 R 0 Q 1
T  2 IDLE
T  3 IDLE
T  4 I 1 R 1
T  5 I 1 R 0
FINISHED 1 INTERRUPTS 1 TICKS 5
```
<table header-row="true">
<colgroup>
<col>
<col>
<col width="822">
</colgroup>
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
결과 분석: P1은 시각 1에 끝났지만, main의 반복 조건이 인터럽트 완료 수까지 보기 때문에 프로그램이 바로 끝나지 않았다. 시각 1\~3에는 실행할 작업이 없어 IDLE이 두 번 찍혔고, 이 2 tick도 TICKS 5에 들어간다.
<empty-block/>
**실제 터미널 실행 화면**
![T1에 P1이 끝났지만 아직 도착하지 않은 I1 때문에 반복이 이어지는 구간.](https://prod-files-secure.s3.us-west-2.amazonaws.com/bb202fe9-e653-4278-8d2f-0d12906a5653/033443fa-185f-4c5d-bbee-4b6eae8afed0/05-%ED%94%84%EB%A1%9C%EC%84%B8%EC%8A%A4%EC%A2%85%EB%A3%8C%ED%9B%84%EC%9D%B8%ED%84%B0%EB%9F%BD%ED%8A%B8.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=ASIAZI2LB466WLIUTVBM%2F20261110%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20261110T155020Z&X-Amz-Expires=3600&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEHYaCXVzLXdlc3QtMiJHMEUCIQCRz6RFCksLB4BIzOQifXDu0eRCWM9PGAfM%2Bo9nE4VSMgIgYQfo%2BYvDQETvXIpi33U9qcKdj8lzP8p%2B9mUqrkycXswq%2FwMIPhAAGgw2Mzc0MjMxODM4MDUiDK0%2FtSe9tbguWGgMqyrcAxMt5neww5QnFaJLROdIT9AmURl%2FqmktGxWnB5gs0xNa5EURMluajnYwI9i7yWJdDeQpdddNi9uQSgfMTs994BhSr4gHh6doq2PwKeSPADm1u8W3vErOUX8oYwLqu8Sfd2ny7NtvQmjLakPDMPWFA362xpHKXqYANtZDv257bT38RK%2Fiy6%2BdeA4LNuFFU5eKyPhajYWKu%2FNPk6FL96MUSZ%2Fk%2B6IRDM%2FqqWpRkC4vCjVq2BlTxkPbkW8TJRplVG2L73LDklwVuMlACYMb2YNRyG5vhaL5B2HVKYMV%2FvuEULxOi8yhe8yKRF1nxehJOxtLv%2FPgY%2B1dZjfM0AWJq5Gc0umBTbEZpORntXlqaVvHEYSo59ws1NDTJ4SjS4ADypMy4KB%2BFahB1IH2EcAqRWmRZFBq0VCuPJmMVmKLBplBeARcVujCJ3%2Fijh%2F4g7eQMpFrRenTwgJdlWnF9O%2FHgNlnSQ%2FTSjm%2BUn6rABeUDuegr%2FZBOqtzapEkbN7YjnfzEepSN%2BLEAH%2BvmNfzKb1ZSWVe07ef3BG2Dmga7UGX%2FZEPTN0bl0Yhzs2lg5uFtlHq7Km05VY5jAbooUbYXGyprR1IsccpOtimK89U7UJflIe77PzFML0dS0IVUYQxPJ5mMKyzzNcGOqUB9%2BQvWeySMjOQdwPR6WskUIKvq3x6AlS6nogcqVpQ9eM2MCjtTYoBWkRPOZeg9N%2FBshEBqdla0CIDNOOHcMKGnhUNj6hzAZM9spDq%2B2gW%2FWKAFVM4lrf9nsGwqpxQL1cRz%2FXG5T%2BxbkbDJKLS%2BLoM35gAWxp4UauDdjILOAocLby%2F5K6st0f1cz%2BrRQr3EGtU9ILqjt4iW8t6jnpSxefUbuuvISkl&X-Amz-Signature=8d1e3c82dfeaef58c84ad67bdf327dbbeec952d24c6739777cfbc331846899ba&X-Amz-SignedHeaders=host&x-amz-checksum-mode=ENABLED&x-id=GetObject#notion_record=block.408b06d2-63bc-8196-8eb7-e5cba454711d.bb202fe9-e653-4278-8d2f-0d12906a5653)
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