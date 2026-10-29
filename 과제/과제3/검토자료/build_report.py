"""Build the provisional HW3 report manuscript (Notion-flavored Markdown) from HW3.c and live runs."""

from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "HW3.c"
OUT = ROOT / "보고서_초안.md"
CAPTURES = json.loads((ROOT / "검토자료/터미널_캡처기록.json").read_text(encoding="utf-8"))
assert CAPTURES["source_sha256"] == hashlib.sha256(SOURCE.read_bytes()).hexdigest(), "stale terminal captures"
LINES = SOURCE.read_text(encoding="utf-8").split("\n")


def lines(a, b):
    """1-based inclusive line range of HW3.c."""
    return "\n".join(LINES[a - 1:b])


def esc(text):
    for ch in "\\*<>{}[]|~":
        text = text.replace(ch, "\\" + ch)
    return text


def cell_code(code):
    return esc(code).replace("\n", "<br>")


def cell_text(text):
    return "<br><br>".join(esc(p.strip()) for p in text.strip().split("\n\n"))


def code_table(rows):
    longest = max(len(l) for code, _ in rows for l in code.split("\n"))
    width = min(600, max(300, longest * 8 + 40))
    out = ['<table header-row="true">', "<colgroup>", f'<col width="{width}">', "<col>", "</colgroup>",
           "<tr>", "<td>소스코드</td>", "<td>기능 명세와 분석</td>", "</tr>"]
    for code, text in rows:
        out += ["<tr>", f"<td>{cell_code(code)}</td>", f"<td>{cell_text(text)}</td>", "</tr>"]
    out.append("</table>")
    return "\n".join(out)


def plain_table(header, rows):
    out = ['<table header-row="true">', "<tr>"] + [f"<td>{esc(h)}</td>" for h in header] + ["</tr>"]
    for r in rows:
        out += ["<tr>"] + [f"<td>{esc(c)}</td>" for c in r] + ["</tr>"]
    out.append("</table>")
    return "\n".join(out)


# ---------------------------------------------------------------- source analysis

DECLS = [
    (lines(1, 15), """
_CRT_SECURE_NO_WARNINGS는 MSVC에서 scanf 사용 시 나오는 보안 경고를 끄는 매크로다. stdio.h는 scanf와 printf, stdlib.h는 오류 시 프로그램을 끝내는 exit를 위해 포함한다.

MAX_PROCESSES(8)와 MAX_INTERRUPTS(16)는 입력할 수 있는 프로세스·인터럽트 수의 상한이다. MAX_STACK_SIZE(16)는 중단된 문맥을 쌓을 수 있는 칸 수다. MAX_QUEUE_SIZE는 MAX_PROCESSES + 1 = 9다. 원형 큐는 비어 있음과 가득 참을 구분하려고 한 칸을 항상 비워 두므로, 9칸으로 프로세스 8개를 모두 담을 수 있다.

QUANTUM(2)은 프로세스가 한 번 CPU를 배정받아 연속으로 실행할 수 있는 최대 tick이다. MAX_DURATION(10)은 작업 하나의 실행 시간 상한, MAX_ARRIVAL_TIME(1000)은 인터럽트 도착 시각 상한이다.

MAX_SIMULATION_TICKS는 1000 + (8 + 16) × 10 = 1240이다. 마지막 인터럽트가 시각 1000에 도착해도, 그 뒤에 남은 일은 모든 작업 시간의 합 240을 넘지 않으므로 정상 입력은 이 안에 끝난다. 이 값을 넘으면 상태 전이가 잘못되어 끝나지 않는 것으로 보고 main이 반복을 멈춘다.
"""),
    (lines(17, 32), """
TaskType은 CPU가 지금 무엇을 하는지 나타낸다. IDLE은 실행할 작업이 없는 상태, PROCESS는 라운드로빈으로 실행되는 프로세스, INTERRUPT는 인터럽트 처리다.

Context는 실행 중이거나 중단된 작업 하나의 문맥이다. kind는 종류, id는 입력 순서로 매긴 번호, remaining은 남은 실행 시간, quantum_left는 이번 배정에서 남은 할당 시간이다. 중단했다가 이어서 실행하려면 이 네 값만 있으면 되므로, 스택과 큐에는 Context를 값 그대로 복사해 저장한다. 인터럽트는 라운드로빈 대상이 아니므로 quantum_left를 0으로 둔다.

IDLE_CONTEXT는 모든 값이 0인 IDLE 문맥으로, CPU를 비울 때 current에 대입한다. IDLE이 열거형의 첫 값 0이므로 0으로 초기화한 Context는 IDLE_CONTEXT와 같다.
"""),
    (lines(34, 44), """
ReadyQueue는 CPU를 기다리는 프로세스의 원형 큐다. front는 첫 원소의 바로 앞 칸, rear는 마지막 원소가 있는 칸을 가리킨다. 먼저 들어온 프로세스가 먼저 나가므로, 퀀텀을 다 쓴 프로세스를 뒤에 넣으면 다른 프로세스가 모두 한 번씩 실행된 뒤 다시 차례가 온다.

ContextStack은 인터럽트 때문에 중단된 문맥을 저장한다. top은 가장 최근에 넣은 칸의 인덱스이며 비어 있으면 -1이다. 중첩 인터럽트에서는 가장 나중에 중단된 작업부터 다시 실행해야 하므로 나중에 넣은 것을 먼저 꺼내는 스택을 쓴다.
"""),
    (lines(46, 61), """
Scheduler는 시뮬레이션 전체 상태를 한데 묶는다. ready는 준비 큐, suspended는 중단 문맥 스택, current는 지금 CPU에서 실행 중인 문맥이다. tick은 지금까지 지난 tick 수로 현재 시각과 같다. finished_processes와 finished_interrupts는 완료된 작업 수이며 main의 반복 종료 조건에 쓰인다.

current를 포인터가 아닌 값으로 두므로, 프로세스를 큐에서 꺼내거나 스택에서 복원하면 그 문맥이 current로 복사된다.

InterruptEvent는 미리 입력받은 인터럽트 정보다. Context와 달리 도착 시각 arrival_time이 있고, duration은 처리에 필요한 시간이다. 도착 시각이 되면 start_interrupt가 이 정보로 INTERRUPT 문맥을 만든다.
"""),
    (lines(63, 71), """
앞의 다섯 개는 제공 함수 중 큐·스택 조작과 1 tick 실행 함수, 뒤의 세 개는 구현 대상 함수의 원형이다. 원형을 먼저 선언하므로 정의 순서와 관계없이 서로 호출할 수 있다. 과제 조건에 따라 함수 형식·매크로·구조체는 바꾸지 않았고 추가 함수도 만들지 않았다.
"""),
]

FUNCS = [
    ("init_queue", "제공 함수", [(lines(73, 76), """
인자: 초기화할 큐. 반환값: 없음. 변경 상태: front, rear.

front와 rear를 같은 칸 0으로 맞춘다. 이 큐에서 front == rear는 비어 있음을 뜻하므로 원소가 없는 큐가 된다.
""")]),
    ("is_empty_queue", "제공 함수", [(lines(78, 81), """
인자: 검사할 큐(const로 받아 수정하지 않음). 반환값: 비어 있으면 1, 아니면 0.

front는 첫 원소의 앞 칸이므로, rear와 같으면 꺼낼 원소가 없다. select_process는 이 함수로 먼저 확인한 뒤에만 dequeue를 호출한다.
""")]),
    ("is_full_queue", "제공 함수", [(lines(83, 86), """
인자: 검사할 큐. 반환값: 가득 찼으면 1, 아니면 0.

rear의 다음 칸이 front면 가득 찬 것으로 본다. 한 칸을 비워 두지 않고 9칸을 다 채우면 rear가 한 바퀴 돌아 front와 같아져 빈 큐와 구분할 수 없다. 그래서 9칸 중 8칸만 쓴다. % MAX_QUEUE_SIZE는 마지막 칸 다음을 0번 칸으로 되돌린다.
""")]),
    ("enqueue", "제공 함수", [(lines(88, 97), """
인자: 큐와 넣을 Context. 반환값: 성공 1, 큐가 없거나 가득 차면 0. 변경 상태: rear와 그 칸의 값.

rear를 원형으로 한 칸 옮긴 뒤 그 칸에 문맥을 복사한다. 실패하면 큐를 바꾸지 않고 0을 돌려주므로, 호출한 쪽에서 실패를 처리할 수 있다. main은 처음 프로세스를 넣을 때, finish_tick은 퀀텀을 다 쓴 프로세스를 다시 넣을 때 사용한다.
""")]),
    ("dequeue", "제공 함수", [(lines(99, 108), """
인자: 큐. 반환값: 맨 앞 Context. 변경 상태: front.

front를 한 칸 옮기면 그 칸이 맨 앞 원소이므로 그 값을 돌려준다. 칸의 값을 지우지 않고 인덱스만 옮기며, 그 칸은 이후 enqueue가 덮어쓴다. 빈 큐에서 호출하면 돌려줄 값이 없으므로 QUEUE_ERROR를 출력하고 exit(1)로 끝낸다.
""")]),
    ("init_stack", "제공 함수", [(lines(110, 113), """
인자: 스택. 변경 상태: top.

top을 -1로 두어 빈 스택으로 만든다. 첫 push에서 top이 0이 되어 0번 칸부터 사용한다.
""")]),
    ("is_empty_stack", "제공 함수", [(lines(115, 118), """
인자: 스택. 반환값: 비어 있으면 1.

top이 -1이면 저장된 문맥이 없다. finish_tick은 인터럽트가 끝났을 때 이 함수로 복원할 문맥이 있는지 확인한다.
""")]),
    ("is_full_stack", "제공 함수", [(lines(120, 123), """
인자: 스택. 반환값: 가득 찼으면 1.

top이 마지막 인덱스 15(MAX_STACK_SIZE - 1)이면 더 넣을 칸이 없다.
""")]),
    ("push", "제공 함수", [(lines(125, 133), """
인자: 스택과 넣을 Context. 반환값: 성공 1, 스택이 없거나 가득 차면 0. 변경 상태: top과 그 칸의 값.

top을 먼저 1 늘린 뒤(++top) 그 칸에 문맥을 복사한다. start_interrupt가 중단되는 작업의 문맥을 저장할 때 사용한다.
""")]),
    ("pop", "제공 함수", [(lines(135, 143), """
인자: 스택. 반환값: 가장 최근에 넣은 Context. 변경 상태: top.

현재 top 칸의 값을 돌려준 뒤 top을 1 줄인다(top--). 빈 스택이면 STACK_ERROR를 출력하고 exit(1)로 끝낸다. finish_tick은 인터럽트가 끝났을 때 가장 최근에 중단된 작업을 이 함수로 되돌린다.
""")]),
    ("select_process", "구현 함수", [(lines(145, 153), """
인자: 스케줄러. 반환값: 없음. 변경 상태: current, 준비 큐의 front.

CPU가 비어 있을 때 준비 큐의 맨 앞 프로세스를 꺼내 current로 만든다. main은 이 함수를 매 tick 호출하므로, 이미 프로세스나 인터럽트가 실행 중이면(current.kind가 IDLE이 아니면) 아무것도 바꾸지 않고 돌아가야 한다. 그렇지 않으면 실행 중인 작업이 매 tick 교체된다.

준비 큐가 비어 있어도 바꾸지 않는다. 그러면 current가 IDLE로 남아 execute_tick이 시간만 흐르게 한다. 이 검사를 먼저 하므로 dequeue가 빈 큐에서 QUEUE_ERROR로 끝나는 경우가 생기지 않는다.

꺼낸 프로세스의 quantum_left를 QUANTUM(2)으로 정한다. 큐에 다시 들어오는 프로세스는 quantum_left가 0인 상태이므로, CPU를 새로 배정받을 때마다 2 tick을 새로 받는다. 인터럽트가 끝나 스택에서 복원된 프로세스는 current가 IDLE이 아니므로 이 함수에서 바뀌지 않고, 중단 전에 남았던 quantum_left를 이어서 쓴다.
""")]),
    ("start_interrupt", "구현 함수", [(lines(155, 166), """
인자: 스케줄러, 도착한 인터럽트 정보. 반환값: 없음. 변경 상태: 중단 문맥 스택, current.

현재 작업이 IDLE이 아니면 그 문맥을 스택에 push한다. 프로세스든 처리 중이던 인터럽트든 remaining과 quantum_left가 중단된 시점의 값 그대로 저장되므로, 나중에 꺼내면 같은 상태에서 이어서 실행된다. IDLE은 되돌아갈 작업이 없으므로 저장하지 않는다. &&의 단락 평가 때문에 current가 IDLE이면 push 자체가 호출되지 않는다.

push가 실패하면 문맥을 잃게 된다. 잃은 작업은 끝나지 않아 반복이 멈추지 않으므로, main의 다른 시뮬레이션 오류와 같이 SIMULATION_ERROR를 출력하고 종료 코드 2로 끝낸다. 정상 입력에서는 스택에 실행 중인 인터럽트 하나를 뺀 인터럽트 최대 15개와 프로세스 1개, 모두 16개까지만 쌓이므로 이 분기에 도달하지 않는다.

이어서 current를 새 인터럽트로 바꾼다. id와 남은 시간은 입력 정보에서 가져오고, 인터럽트는 퀀텀을 적용하지 않으므로 quantum_left는 0이다. execute_tick은 인터럽트의 quantum_left를 검사하거나 줄이지 않으므로 인터럽트는 끝날 때까지 계속 실행된다.
""")]),
    ("finish_tick", "구현 함수", [
        (lines(168, 187), """
인자: 스케줄러. 반환값: 없음. 변경 상태: current, 완료 수, 준비 큐, 중단 문맥 스택.

execute_tick으로 1 tick을 실행한 직후, 그 결과에 따라 다음 tick의 current를 정리한다. current는 s->current를 가리키는 포인터라 이를 통해 바꾼 값이 스케줄러에 바로 반영된다.

프로세스이고 remaining이 0이면 완료다. 완료 수를 늘리고 CPU를 IDLE로 비워 다음 tick에 select_process가 다른 프로세스를 고르게 한다.

완료가 아니고 quantum_left만 0이면 퀀텀을 다 쓴 것이다. 프로세스를 준비 큐 맨 뒤에 넣고 CPU를 비운다. 완료를 먼저 검사하는 이유는 두 값이 같은 tick에 0이 될 수 있기 때문이다(실행 사례 2·3). 순서가 반대면 끝난 프로세스가 큐에 들어가 완료 수가 늘지 않고, 나중에 다시 선택될 때 execute_tick이 남은 시간 0을 발견해 SIMULATION_ERROR로 끝난다.

enqueue 실패는 정상 입력에서 일어나지 않는다. 실행 중인 프로세스가 큐 밖에 있으므로 큐에는 최대 7개만 있기 때문이다. 문맥을 잃지 않도록 start_interrupt와 같은 방식으로 처리했다. 두 조건 모두 아니면 아무것도 하지 않아 다음 tick에도 같은 프로세스가 실행된다.
"""),
        (lines(188, 200), """
인터럽트이고 remaining이 0이면 처리가 끝난 것이다. 인터럽트 완료 수를 늘린 뒤, 스택이 비어 있으면 돌아갈 작업이 없으므로 IDLE로 바꾼다. 비어 있지 않으면 pop으로 가장 최근에 중단된 문맥을 current로 되돌린다. 중첩 인터럽트에서는 이것이 바깥 인터럽트이고, 그 인터럽트가 끝나면 다음 pop이 처음 중단된 프로세스를 꺼낸다.

빈 스택을 먼저 확인하므로 pop이 STACK_ERROR로 끝나는 경우가 없다. 인터럽트가 끝나지 않았거나 current가 IDLE이면 아무것도 바꾸지 않는다. 다음 프로세스를 고르는 일은 select_process가 맡는다.
"""),
    ]),
    ("execute_tick", "제공 함수", [
        (lines(202, 210), """
인자: 스케줄러. 반환값: 1 tick을 실행했으면 1, 실행할 수 없는 상태면 0. 변경 상태: current의 남은 시간과 퀀텀, tick.

먼저 current가 실행 가능한 상태인지 검사한다. IDLE이 아닌 작업의 남은 시간이 0 이하이거나, 프로세스의 퀀텀이 0 이하이면 0을 돌려준다. finish_tick이 끝난 작업과 퀀텀을 다 쓴 프로세스를 제대로 치웠다면 이런 상태는 생기지 않는다. 즉 구현 함수의 상태 전이를 검사하는 역할을 하며, main은 0을 받으면 SIMULATION_ERROR로 끝낸다.
"""),
        (lines(211, 231), """
IDLE이 아니면 남은 시간을 1 줄이고, 모든 경우에 tick을 1 늘린다. IDLE일 때는 실행 없이 시간만 흐른다.

프로세스면 퀀텀도 1 줄인다. 출력하는 T 값은 tick을 늘린 뒤의 시각이므로, T 1은 시각 0에서 1 사이의 실행 결과다. 프로세스는 번호·남은 시간(R)·남은 퀀텀(Q), 인터럽트는 번호와 남은 시간, IDLE은 IDLE을 출력한다. 출력이 끝난 뒤 완료·재등록·복원은 finish_tick이 처리한다.
"""),
    ]),
    ("main", "제공 함수", [
        (lines(233, 247), """
인자: 없음. 반환값: 정상 종료 0, 입력 오류 1, 시뮬레이션 오류 2.

입력받을 프로세스·인터럽트 배열과 개수, 스케줄러 s, 다음에 처리할 인터럽트 인덱스 next_interrupt를 선언한다. s = {0}이므로 tick과 완료 수는 0이고, current는 kind가 IDLE(0)이라 IDLE_CONTEXT와 같다.

첫 줄의 프로세스 수 N과 인터럽트 수 M을 읽고, N은 1~8, M은 0~16 범위인지 확인한다. 과제는 입력이 정상이라고 가정하지만 제공 코드에는 이 검사가 들어 있다.
"""),
        (lines(249, 259), """
N줄에 걸쳐 각 프로세스의 실행 시간을 remaining에 읽고 1~10 범위인지 확인한다. id는 입력 순서대로 1부터 매기고 kind는 PROCESS로 정한다. quantum_left는 0으로 남겨 두며, 실제 값은 select_process가 CPU를 배정할 때 정한다.
"""),
        (lines(261, 273), """
M줄에 걸쳐 인터럽트의 도착 시각과 처리 시간을 읽는다. 도착 시각이 0~1000, 처리 시간이 1~10인지, 그리고 앞 인터럽트보다 도착 시각이 큰지 확인한다. 도착 시각이 순서대로 커지므로 main은 next_interrupt 하나만 보며 차례로 처리할 수 있고, 한 시각에 인터럽트가 둘 이상 도착하지 않는다.
"""),
        (lines(275, 285), """
큐와 스택을 초기화하고 모든 프로세스를 입력 순서대로 준비 큐에 넣는다. 모든 프로세스가 시각 0에 도착한다는 규칙을 이렇게 표현한다. 프로세스는 최대 8개이고 큐도 8개를 담을 수 있으므로 정상 입력에서는 enqueue가 실패하지 않는다.
"""),
        (lines(287, 309), """
모든 프로세스와 모든 인터럽트가 끝날 때까지 1 tick씩 반복한다. 프로세스가 모두 끝나도 아직 도착하지 않은 인터럽트가 있으면 IDLE로 시간을 보내며 기다린다(실행 사례 5).

한 번의 반복은 과제의 실행 흐름 순서와 같다. ① 현재 시각에 도착한 인터럽트가 있으면 start_interrupt로 시작한다. ② select_process로 CPU가 비었을 때 프로세스를 고른다. ③ execute_tick으로 1 tick 실행·출력한다. ④ finish_tick으로 완료·재등록·복원을 처리한다.

인터럽트를 프로세스 선택보다 먼저 처리하므로, 같은 시각에 CPU가 비어 있으면 인터럽트가 먼저 CPU를 차지하고 프로세스는 큐에서 그대로 기다린다(실행 사례 4). execute_tick은 성공하면 tick을 항상 1 늘리므로 도착 시각을 건너뛰는 일이 없다. tick이 상한에 이르거나 execute_tick이 0을 돌려주면 SIMULATION_ERROR로 끝낸다.
"""),
        (lines(311, 314), """
반복이 끝나면 완료한 프로세스 수, 인터럽트 수, 전체 경과 tick을 한 줄로 출력하고 0을 반환한다.
"""),
    ]),
]

# ---------------------------------------------------------------- execution cases

CASES = [
    {
        "title": "공식 예시: 중첩 인터럽트와 라운드로빈",
        "kind": "공식",
        "input": "2 2\n3\n1\n1 2\n2 1\n",
        "expected": """T  1 P 1 R 2 Q 1
T  2 I 1 R 1
T  3 I 2 R 0
T  4 I 1 R 0
T  5 P 1 R 1 Q 0
T  6 P 2 R 0 Q 1
T  7 P 1 R 0 Q 1
FINISHED 2 INTERRUPTS 2 TICKS 7""",
        "table": [
            ("0→1", "P1", "준비 큐 [P1, P2]에서 P1을 꺼내 Q=2를 준다. 1 tick 실행 후 R2 Q1, 두 값 모두 0이 아니므로 계속 실행한다."),
            ("1→2", "I1", "I1 도착. P1(R2, Q1)을 push해 스택 [P1]. I1 R2→1."),
            ("2→3", "I2", "I2 도착. I1(R1)을 push해 스택 [P1, I1]. I2 R1→0으로 완료, 맨 위 I1을 pop한다."),
            ("3→4", "I1", "I1 R1→0으로 완료, 스택에 남은 P1을 pop해 스택이 빈다."),
            ("4→5", "P1", "복원된 P1은 Q1을 이어 써서 R1 Q0. 퀀텀 소진으로 큐 뒤에 넣어 [P2, P1], CPU는 IDLE."),
            ("5→6", "P2", "P2를 꺼내 Q=2. R1→0으로 완료."),
            ("6→7", "P1", "P1을 다시 꺼내 Q=2. R1→0으로 완료. 모든 작업이 끝나 반복 종료."),
        ],
        "analysis": "출력 순서 P1 I1 I2 I1 P1 P2 P1은 과제 18쪽 실행 화면·간트 차트와 같다. 시각 2에 I2가 I1을 중단시켰고, I2가 끝난 뒤에는 처음 중단된 P1이 아니라 가장 최근에 중단된 I1이 먼저 재개되었다. T5의 Q 0은 P1이 T1에서 퀀텀 1을 쓰고 남은 1을 복원 후 이어 썼기 때문이다. 반면 T7의 Q 1은 큐에서 다시 선택되며 퀀텀을 2로 새로 받았기 때문이다. 전체 일의 양은 프로세스 3 + 1과 인터럽트 2 + 1을 합한 7이고, IDLE 없이 실행되어 TICKS 7이 된다.",
    },
    {
        "title": "추가 사례 1: 세 겹 중첩 인터럽트",
        "kind": "추가",
        "purpose": "인터럽트가 세 번 겹칠 때도 스택이 중단된 역순으로 문맥을 복원하는지 확인한다.",
        "input": "1 3\n4\n1 3\n2 3\n3 1\n",
        "expected": """T  1 P 1 R 3 Q 1
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
FINISHED 1 INTERRUPTS 3 TICKS 11""",
        "table": [
            ("0→1", "P1", "P1 선택, Q=2. R3 Q1."),
            ("1→4", "I1, I2, I3", "시각 1·2·3에 차례로 도착하며 P1, I1, I2를 push. 스택 [P1, I1, I2]. I3은 1 tick에 완료하고 I2를 pop."),
            ("4→6", "I2", "I2가 남은 2 tick을 실행해 완료, I1을 pop."),
            ("6→8", "I1", "I1이 남은 2 tick을 실행해 완료, P1을 pop. 스택이 빈다."),
            ("8→9", "P1", "Q1을 이어 써서 R2 Q0. 퀀텀 소진으로 큐 [P1]에 넣고 IDLE."),
            ("9→11", "P1", "큐에 P1뿐이므로 다시 꺼내 Q=2. T11에 R0과 Q0이 동시에 되고, 완료가 먼저 검사되어 완료로 처리."),
        ],
        "analysis": "인터럽트는 I1, I2, I3 순서로 시작했지만 끝난 순서는 I3, I2, I1이다. 스택에 마지막으로 넣은 I2가 먼저 나오고 처음 넣은 P1이 마지막에 나왔기 때문이다. I2와 I1은 각각 중단 전의 남은 시간(2, 2)에서 이어서 실행되었다. 스택에는 최대 3개의 문맥이 쌓였다. 마지막 T11은 남은 시간과 퀀텀이 함께 0이 된 경우인데, 완료로 처리되어 FINISHED 1이 출력되었다.",
    },
    {
        "title": "추가 사례 2: 완료와 퀀텀 소진이 같은 tick",
        "kind": "추가",
        "purpose": "실행 시간이 퀀텀과 같은 2인 프로세스가 큐로 돌아가지 않고 완료되는지 확인한다.",
        "input": "2 0\n2\n1\n",
        "expected": """T  1 P 1 R 1 Q 1
T  2 P 1 R 0 Q 0
T  3 P 2 R 0 Q 1
FINISHED 2 INTERRUPTS 0 TICKS 3""",
        "table": [
            ("0→2", "P1", "Q=2로 2 tick 실행. T2에 R0 Q0. finish_tick이 remaining을 먼저 보고 완료 처리, IDLE."),
            ("2→3", "P2", "큐에 남은 P2를 꺼내 1 tick에 완료."),
        ],
        "analysis": "P1은 T2에 퀀텀도 다 썼지만 남은 시간도 0이므로 준비 큐에 다시 들어가지 않았다. 그래서 바로 다음 tick에 P2가 실행되었고, P1이 다시 선택되는 tick은 없다. 3 tick 동안 IDLE 없이 실행해 FINISHED 2 TICKS 3이 되었다.",
    },
    {
        "title": "추가 사례 3: CPU가 빈 순간에 도착한 인터럽트",
        "kind": "추가",
        "purpose": "퀀텀 소진 직후 IDLE인 시각에 인터럽트가 오면 아무것도 저장하지 않고, 큐 순서가 유지되는지 확인한다.",
        "input": "2 1\n3\n2\n2 1\n",
        "expected": """T  1 P 1 R 2 Q 1
T  2 P 1 R 1 Q 0
T  3 I 1 R 0
T  4 P 2 R 1 Q 1
T  5 P 2 R 0 Q 0
T  6 P 1 R 0 Q 1
FINISHED 2 INTERRUPTS 1 TICKS 6""",
        "table": [
            ("0→2", "P1", "P1이 퀀텀 2를 모두 써서 R1 Q0. 큐 뒤에 넣어 [P2, P1], IDLE."),
            ("2→3", "I1", "I1 도착. current가 IDLE이므로 push하지 않음. select_process는 current가 인터럽트라 P2를 꺼내지 않는다. I1 완료 후 스택이 비어 IDLE."),
            ("3→5", "P2", "P2를 꺼내 Q=2로 2 tick 실행, T5에 R0 Q0으로 완료."),
            ("5→6", "P1", "P1을 꺼내 1 tick에 완료."),
        ],
        "analysis": "시각 2에는 P1이 이미 큐로 돌아간 뒤라 중단된 작업이 없었다. 그래서 I1이 끝났을 때 스택이 비어 있었고 CPU는 IDLE이 되었다. 이후 큐 순서 [P2, P1]대로 P2와 P1이 실행되었다. 같은 시각에 CPU가 비어 있어도 main이 인터럽트를 먼저 시작하므로, T3에 P2가 아니라 I1이 실행되었다.",
    },
    {
        "title": "추가 사례 4: 프로세스가 모두 끝난 뒤의 인터럽트",
        "kind": "추가",
        "purpose": "실행할 작업이 없는 동안 IDLE로 시간이 흐르고, 늦게 도착한 인터럽트까지 처리한 뒤 끝나는지 확인한다.",
        "input": "1 1\n1\n3 2\n",
        "expected": """T  1 P 1 R 0 Q 1
T  2 IDLE
T  3 IDLE
T  4 I 1 R 1
T  5 I 1 R 0
FINISHED 1 INTERRUPTS 1 TICKS 5""",
        "table": [
            ("0→1", "P1", "P1이 1 tick에 완료, IDLE."),
            ("1→3", "IDLE", "인터럽트 완료 수가 0이라 반복이 계속된다. 큐가 비어 select_process가 아무것도 고르지 않아 시간만 흐른다."),
            ("3→5", "I1", "시각 3에 I1 도착, IDLE이므로 push 없음. 2 tick 처리 후 스택이 비어 IDLE로 끝난다."),
        ],
        "analysis": "P1이 시각 1에 끝났지만 main의 반복 조건은 인터럽트 완료 수도 확인하므로 바로 끝나지 않았다. 시각 1~3에는 실행할 작업이 없어 IDLE이 두 번 출력되었다. TICKS 5에는 이 IDLE 2 tick이 포함되어, 실제 작업량 1 + 2 = 3보다 크다.",
    },
]


def run_cases():
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / "hw3"
        subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-Werror", "-o", str(exe), str(SOURCE)], check=True)
        for case in CASES:
            proc = subprocess.run([str(exe)], input=case["input"], capture_output=True, text=True, timeout=5)
            assert proc.returncode == 0, (case["title"], proc.returncode)
            assert proc.stdout.rstrip("\n") == case["expected"], (case["title"], proc.stdout)
            case["output"] = proc.stdout
        for case, cap in zip(CASES, CAPTURES["cases"]):
            assert cap["passed"] and cap["exit_status"] == 0 and cap["stdin"] == case["input"], case["title"]
            case["image"] = cap["final_png"]


# ---------------------------------------------------------------- assemble

def build():
    run_cases()
    md = ['<table_of_contents color="gray"/>', "<empty-block/>", "# 구현 목적",
          esc("하나의 CPU에서 프로세스와 인터럽트의 실행 순서를 tick 단위로 시뮬레이션한다. 프로세스는 준비 큐에서 꺼내 퀀텀 2의 라운드로빈으로 실행하고, 퀀텀을 다 쓰고도 일이 남으면 큐 뒤로 보낸다. 인터럽트가 도착하면 실행 중이던 작업의 문맥을 스택에 저장하고 인터럽트를 먼저 처리하며, 인터럽트가 끝나면 가장 최근에 중단된 문맥을 되돌린다. 매 tick 실행 결과를 출력하고 모든 작업이 끝나면 완료 수와 전체 시간을 출력한다."),
          "<empty-block/>", "<empty-block/>", "# 소스코드 분석",
          esc("HW3_skeleton.c의 선언, 제공 함수, main은 그대로 두고 비어 있던 select_process, start_interrupt, finish_tick을 구현한 HW3.c를 분석한다."),
          "## 헤더·매크로·구조체·함수 원형", code_table(DECLS)]
    for name, label, rows in FUNCS:
        md += ["<empty-block/>", f"## {name}", label, code_table(rows)]
    md += ["<empty-block/>", "<empty-block/>", "# 실행결과 및 분석",
           esc(f"과제 18쪽의 공식 예시 1건과, 공식 예시에서 드러나지 않는 동작을 보여 주는 추가 사례 {len(CASES) - 1}건을 실행했다. 각 사례에서 입력과 실제 출력을 제시하고, tick마다 큐·스택·current가 어떻게 바뀌어 그 출력이 나왔는지 분석한다."),
           "<empty-block/>"]
    for i, case in enumerate(CASES):
        if i:
            md.append("<empty-block/>")
        md.append(f"## {case['title']}")
        if case.get("purpose"):
            md.append(esc(case["purpose"]))
        md += ["**입력**", "```plain text", case["input"], "```", "<empty-block/>",
               "**실제 출력**", "```plain text", case["output"], "```",
               plain_table(["시각", "실행", "상태 변화의 이유"], case["table"]),
               esc("결과 분석: " + case["analysis"])]
        lines_in = case["input"].count("\n")
        md += ["<empty-block/>", "**실제 터미널 실행 화면**",
               f"![터미널의 실제 실행 화면. 입력 {lines_in}줄, tick별 출력과 FINISHED 요약, 종료 상태 0을 보여 준다.]({case['image']})"]
    md += ["<empty-block/>", "<empty-block/>", "# 전체 소스코드", "```c", SOURCE.read_text(encoding="utf-8").rstrip("\n"), "```", ""]
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT} ({len(CASES)} cases)")


if __name__ == "__main__":
    build()
