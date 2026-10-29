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
_CRT_SECURE_NO_WARNINGS는 MSVC가 scanf에 내는 보안 경고를 끄는 매크로다. stdio.h는 scanf·printf 때문에, stdlib.h는 오류가 나면 프로그램을 끝내는 exit 때문에 포함했다.

MAX_PROCESSES(8)와 MAX_INTERRUPTS(16)는 입력할 수 있는 프로세스·인터럽트 수의 상한이고, MAX_STACK_SIZE(16)는 중단된 문맥을 쌓아 둘 칸 수다. MAX_QUEUE_SIZE가 MAX_PROCESSES보다 하나 많은 9인 데는 이유가 있다. 원형 큐는 빈 상태와 가득 찬 상태를 구분하려고 한 칸을 늘 비워 두기 때문에, 8개를 다 담으려면 9칸이 필요하다.

QUANTUM(2)은 프로세스가 CPU를 한 번 배정받았을 때 연달아 실행할 수 있는 최대 tick이다. MAX_DURATION(10)은 작업 하나의 실행 시간 상한, MAX_ARRIVAL_TIME(1000)은 인터럽트 도착 시각 상한이다.

MAX_SIMULATION_TICKS는 1000 + (8 + 16) × 10 = 1240이다. 마지막 인터럽트가 시각 1000에 와도 그 뒤에 남은 일은 모든 작업 시간의 합인 240을 넘지 못해, 정상 입력이라면 이 안에서 끝난다. tick이 이 값에 이르면 상태 전이가 꼬여 끝나지 않는 것으로 보고 main이 반복을 멈춘다.
"""),
    (lines(17, 32), """
TaskType은 CPU가 지금 하는 일의 종류다. IDLE은 실행할 작업이 없는 상태, PROCESS는 라운드로빈으로 도는 프로세스, INTERRUPT는 인터럽트 처리를 뜻한다.

Context는 실행 중이거나 중단된 작업 하나의 문맥이다. kind는 종류, id는 입력 순서대로 매긴 번호, remaining은 남은 실행 시간, quantum_left는 이번 배정에서 남은 할당 시간이다. 멈췄던 작업을 이어서 돌리는 데 필요한 값은 이 네 개뿐이라, 스택과 큐에는 Context를 값 그대로 복사해 넣는다. 인터럽트는 라운드로빈 대상이 아니어서 quantum_left를 0으로 둔다.

IDLE_CONTEXT는 모든 값이 0인 IDLE 문맥이고, CPU를 비울 때 current에 대입한다. 열거형의 첫 값인 IDLE이 0이라서, 0으로 초기화한 Context는 IDLE_CONTEXT와 같다.
"""),
    (lines(34, 44), """
ReadyQueue는 CPU를 기다리는 프로세스를 담는 원형 큐다. front는 첫 원소 바로 앞 칸을, rear는 마지막 원소가 있는 칸을 가리킨다. 먼저 들어온 프로세스가 먼저 나가는 구조라서, 퀀텀을 다 쓴 프로세스를 뒤에 넣으면 나머지 프로세스가 한 번씩 돈 다음에야 차례가 다시 온다.

ContextStack에는 인터럽트 때문에 멈춘 문맥이 쌓인다. top은 가장 최근에 넣은 칸의 인덱스이고, 비어 있을 때는 -1이다. 인터럽트가 겹치면 가장 나중에 멈춘 작업부터 다시 돌려야 하는데, 나중에 넣은 것을 먼저 꺼내는 스택이 바로 그 순서를 만든다.
"""),
    (lines(46, 61), """
Scheduler는 시뮬레이션 상태 전체를 한데 묶은 구조체다. ready는 준비 큐, suspended는 중단 문맥 스택, current는 지금 CPU에서 돌고 있는 문맥이다. tick은 지금까지 흐른 tick 수이자 현재 시각이다. finished_processes와 finished_interrupts는 끝난 작업 수로, main의 반복 종료 조건에 쓰인다.

current는 포인터가 아니라 값이다. 그래서 큐에서 꺼내거나 스택에서 복원한 문맥은 current로 복사된다.

InterruptEvent는 미리 입력받아 둔 인터럽트 정보다. Context에는 없는 도착 시각 arrival_time이 있고, duration은 처리에 걸리는 시간이다. 도착 시각이 되면 start_interrupt가 이 정보로 INTERRUPT 문맥을 만든다.
"""),
    (lines(63, 71), """
앞의 다섯 개는 제공 함수 가운데 큐·스택 조작 함수와 1 tick 실행 함수, 뒤의 세 개는 구현할 함수의 원형이다. 원형이 위에 있어 정의 순서와 상관없이 서로 부를 수 있다. 과제 조건대로 함수 형식·매크로·구조체는 손대지 않았고 함수도 새로 만들지 않았다.
"""),
]

FUNCS = [
    ("init_queue", "제공 함수", [(lines(73, 76), """
front와 rear를 둘 다 0으로 맞춘다. 이 큐에서는 front == rear가 빈 상태라, 호출 직후 큐는 비어 있다.
""")]),
    ("is_empty_queue", "제공 함수", [(lines(78, 81), """
front가 첫 원소의 앞 칸을 가리키는 구조라서, front와 rear가 같으면 꺼낼 원소가 없다. 비었으면 1, 아니면 0을 돌려준다. select_process는 이 함수로 확인한 다음에만 dequeue를 부른다.
""")]),
    ("is_full_queue", "제공 함수", [(lines(83, 86), """
rear 다음 칸이 front면 가득 찼다고 보고 1을 돌려준다. 9칸을 다 채우면 rear가 한 바퀴 돌아 front와 겹쳐 빈 큐와 구별이 안 되기 때문에, 9칸 중 8칸까지만 쓴다. % MAX_QUEUE_SIZE는 마지막 칸 다음을 0번 칸으로 돌려놓는 역할이다.
""")]),
    ("enqueue", "제공 함수", [(lines(88, 97), """
rear를 원형으로 한 칸 옮기고 그 칸에 문맥을 복사한 뒤 1을 돌려준다. 큐가 없거나 가득 차 있으면 아무것도 바꾸지 않고 0을 돌려줘서, 실패했을 때 어떻게 할지는 호출한 쪽이 정한다. main이 처음 프로세스를 넣을 때와 finish_tick이 퀀텀을 다 쓴 프로세스를 되돌려 넣을 때 쓰인다.
""")]),
    ("dequeue", "제공 함수", [(lines(99, 108), """
front를 한 칸 옮기면 그 칸이 맨 앞 원소다. 그 Context를 돌려주되 칸의 값은 지우지 않고, 나중에 enqueue가 덮어쓴다. 빈 큐에서 부르면 돌려줄 값이 없어 QUEUE_ERROR를 출력하고 exit(1)로 끝난다.
""")]),
    ("init_stack", "제공 함수", [(lines(110, 113), """
top을 -1로 두어 빈 스택을 만든다. 첫 push에서 top이 0이 되면서 0번 칸부터 채워진다.
""")]),
    ("is_empty_stack", "제공 함수", [(lines(115, 118), """
top이 -1이면 저장된 문맥이 없다는 뜻이라 1을 돌려준다. finish_tick은 인터럽트가 끝났을 때 이 함수로 복원할 문맥이 있는지 본다.
""")]),
    ("is_full_stack", "제공 함수", [(lines(120, 123), """
top이 마지막 인덱스 15(MAX_STACK_SIZE - 1)에 닿았으면 더 넣을 칸이 없어 1을 돌려준다.
""")]),
    ("push", "제공 함수", [(lines(125, 133), """
top을 먼저 1 올리고(++top) 그 칸에 문맥을 복사한 뒤 1을 돌려준다. 스택이 없거나 가득 찼으면 0이다. start_interrupt가 중단되는 작업의 문맥을 저장할 때 쓴다.
""")]),
    ("pop", "제공 함수", [(lines(135, 143), """
top 칸의 Context를 돌려주고 top을 1 내린다(top--). 빈 스택에서 부르면 STACK_ERROR를 출력하고 exit(1)로 끝난다. finish_tick은 인터럽트가 끝나면 이 함수로 가장 최근에 멈춘 작업을 되돌린다.
""")]),
    ("select_process", "구현 함수", [(lines(145, 153), """
인자: 스케줄러. 반환값: 없음.

CPU가 비어 있으면 준비 큐 맨 앞 프로세스를 꺼내 current로 삼는다. main이 이 함수를 매 tick 부르기 때문에, 프로세스든 인터럽트든 이미 무언가 실행 중이면(current.kind가 IDLE이 아니면) 그대로 돌아가야 한다. 이 검사가 없으면 실행 중인 작업이 tick마다 바뀌어 버린다.

준비 큐가 비어 있을 때도 손대지 않는다. current가 IDLE로 남고, execute_tick은 시간만 흘려보낸다. 큐가 비었는지 먼저 확인하니 dequeue가 빈 큐에서 QUEUE_ERROR로 끝날 일도 없다.

꺼낸 프로세스의 quantum_left는 QUANTUM(2)으로 정한다. 큐로 돌아온 프로세스는 quantum_left가 0이라, CPU를 새로 받을 때마다 2 tick을 다시 받는 셈이다. 반면 인터럽트가 끝나 스택에서 복원된 프로세스는 current가 IDLE이 아니어서 이 함수가 건드리지 않는다. 그래서 중단 전에 남아 있던 quantum_left를 그대로 이어 쓴다.
""")]),
    ("start_interrupt", "구현 함수", [(lines(155, 166), """
인자: 스케줄러, 도착한 인터럽트 정보. 반환값: 없음.

current가 IDLE이 아니면 그 문맥을 스택에 push한다. 멈춘 것이 프로세스든 처리 중이던 인터럽트든 remaining과 quantum_left가 중단 시점 값 그대로 저장되고, 나중에 꺼내면 그 상태에서 다시 이어진다. IDLE은 돌아갈 작업이 아니라서 저장하지 않는다. &&의 단락 평가 덕분에 current가 IDLE이면 push는 호출조차 되지 않는다.

push가 실패하면 문맥이 사라진다. 사라진 작업은 영영 끝나지 않아 반복도 멈추지 않을 테니, main의 다른 시뮬레이션 오류처럼 SIMULATION_ERROR를 출력하고 종료 코드 2로 끝내도록 했다. 정상 입력이라면 스택에는 실행 중인 하나를 뺀 인터럽트 최대 15개와 프로세스 1개, 합쳐 16개까지만 쌓여 이 분기에 오지 않는다.

그다음 current를 새 인터럽트로 바꾼다. id와 남은 시간은 입력 정보에서 가져오고, 인터럽트에는 퀀텀이 없어 quantum_left는 0이다. execute_tick은 인터럽트의 quantum_left를 검사하지도 줄이지도 않기 때문에, 인터럽트는 끝날 때까지 계속 실행된다.
""")]),
    ("finish_tick", "구현 함수", [
        (lines(168, 187), """
인자: 스케줄러. 반환값: 없음.

execute_tick으로 1 tick을 돌린 직후, 그 결과를 보고 다음 tick의 current를 정리한다. 지역 변수 current는 s->current를 가리키는 포인터여서, 이것으로 바꾼 값은 스케줄러에 바로 반영된다.

프로세스의 remaining이 0이면 완료다. 완료 수를 1 늘리고 CPU를 IDLE로 비워, 다음 tick에 select_process가 다른 프로세스를 고를 수 있게 한다.

완료는 아닌데 quantum_left가 0이면 퀀텀을 다 쓴 경우다. 프로세스를 준비 큐 맨 뒤에 넣고 CPU를 비운다. 완료 검사를 앞에 둔 건 두 값이 같은 tick에 함께 0이 될 수 있어서다(실행 사례 2·3). 순서가 반대라면 끝난 프로세스가 큐로 들어가 완료 수가 늘지 않는다. 그러다 다시 선택되면 execute_tick이 남은 시간 0을 보고 SIMULATION_ERROR로 끝난다.

정상 입력에서 enqueue가 실패할 일은 없다. 실행 중인 프로세스는 큐 밖에 있어 큐에는 많아야 7개만 들어 있다. 그래도 문맥을 잃지 않도록 start_interrupt와 같은 방식으로 처리했다. 두 조건 모두 아니면 아무것도 하지 않고, 다음 tick에도 같은 프로세스가 이어서 실행된다.
"""),
        (lines(188, 200), """
인터럽트의 remaining이 0이면 처리가 끝난 것이다. 인터럽트 완료 수를 늘리고, 스택이 비어 있으면 돌아갈 작업이 없으니 IDLE로 바꾼다. 비어 있지 않으면 pop으로 가장 최근에 멈춘 문맥을 current로 되돌린다. 인터럽트가 겹쳤던 경우라면 이때 나오는 것은 바깥쪽 인터럽트이고, 그 인터럽트까지 끝나야 다음 pop에서 처음 멈췄던 프로세스가 나온다.

빈 스택인지 먼저 확인하기 때문에 pop이 STACK_ERROR로 끝나는 일은 없다. 인터럽트가 아직 남았거나 current가 IDLE이면 아무것도 바꾸지 않는다. 다음 프로세스를 고르는 일은 select_process의 몫이다.
"""),
    ]),
    ("execute_tick", "제공 함수", [
        (lines(202, 210), """
1 tick을 실행했으면 1, 실행할 수 없는 상태면 0을 돌려준다.

먼저 current가 실행 가능한지 본다. IDLE이 아닌 작업의 남은 시간이 0 이하이거나 프로세스의 퀀텀이 0 이하이면 바로 0이다. finish_tick이 끝난 작업과 퀀텀을 다 쓴 프로세스를 제대로 치웠다면 나올 수 없는 상태라, 사실상 구현 함수의 상태 전이를 점검하는 장치다. main은 0을 받으면 SIMULATION_ERROR로 끝낸다.
"""),
        (lines(211, 231), """
IDLE이 아니면 남은 시간을 1 줄이고, 어떤 경우든 tick은 1 늘린다. IDLE이면 실행 없이 시간만 지나간다.

프로세스라면 퀀텀도 1 줄인다. 출력하는 T 값은 tick을 늘린 뒤의 시각이라, T 1은 시각 0부터 1까지의 실행 결과다. 프로세스는 번호·남은 시간(R)·남은 퀀텀(Q)을, 인터럽트는 번호와 남은 시간을, IDLE은 IDLE을 찍는다. 완료·재등록·복원은 출력 뒤에 finish_tick이 맡는다.
"""),
    ]),
    ("main", "제공 함수", [
        (lines(233, 247), """
정상 종료면 0, 입력 오류면 1, 시뮬레이션 오류면 2를 돌려준다.

입력받을 프로세스·인터럽트 배열과 개수, 스케줄러 s, 다음에 처리할 인터럽트 인덱스 next_interrupt를 선언한다. s = {0}이라 tick과 완료 수는 0이고, current의 kind도 IDLE(0)이어서 IDLE_CONTEXT와 같다.

첫 줄에서 프로세스 수 N과 인터럽트 수 M을 읽고, N이 1~8, M이 0~16 안에 드는지 확인한다. 과제는 입력이 정상이라고 가정하지만 제공 코드에는 이 검사가 들어 있다.
"""),
        (lines(249, 259), """
다음 N줄에서 프로세스마다 실행 시간을 remaining에 읽고, 1~10 범위인지 본다. id는 입력 순서대로 1부터 붙이고 kind는 PROCESS로 둔다. quantum_left는 0인 채로 두는데, 실제 값은 select_process가 CPU를 배정할 때 정한다.
"""),
        (lines(261, 273), """
그다음 M줄에서 인터럽트의 도착 시각과 처리 시간을 읽는다. 도착 시각은 0~1000, 처리 시간은 1~10이어야 하고, 앞 인터럽트보다 늦게 도착해야 한다. 도착 시각이 계속 커지니 main은 next_interrupt 하나만 보면서 차례로 처리하면 되고, 한 시각에 인터럽트가 둘 이상 오는 일도 없다.
"""),
        (lines(275, 285), """
큐와 스택을 초기화한 뒤 모든 프로세스를 입력 순서대로 준비 큐에 넣는다. 모든 프로세스가 시각 0에 도착한다는 규칙이 이 코드로 표현된다. 프로세스는 많아야 8개이고 큐도 8개까지 담을 수 있어, 정상 입력이라면 enqueue가 실패하지 않는다.
"""),
        (lines(287, 309), """
프로세스와 인터럽트가 모두 끝날 때까지 1 tick씩 반복한다. 프로세스가 다 끝났더라도 아직 오지 않은 인터럽트가 있으면 IDLE로 시간을 보내며 기다린다(실행 사례 5).

반복 한 번은 과제가 정한 실행 흐름을 그대로 따른다. ① 현재 시각에 도착한 인터럽트가 있으면 start_interrupt로 시작한다. ② CPU가 비었다면 select_process가 프로세스를 고른다. ③ execute_tick이 1 tick을 실행하고 출력한다. ④ finish_tick이 완료·재등록·복원을 처리한다.

인터럽트 처리가 프로세스 선택보다 앞서 있어서, 같은 시각에 CPU가 비어 있으면 인터럽트가 먼저 CPU를 잡고 프로세스는 큐에서 계속 기다린다(실행 사례 4). execute_tick은 성공할 때마다 tick을 반드시 1 늘리니 도착 시각을 건너뛸 일이 없다. tick이 상한에 닿거나 execute_tick이 0을 돌려주면 SIMULATION_ERROR로 끝낸다.
"""),
        (lines(311, 314), """
반복을 빠져나오면 완료한 프로세스 수, 인터럽트 수, 전체 tick을 한 줄로 출력하고 0을 반환한다.
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
        "analysis": "출력 순서 P1 I1 I2 I1 P1 P2 P1은 과제 18쪽 실행 화면·간트 차트와 같다. 시각 2에 I2가 I1을 끊었고, I2가 끝나자 처음 멈춘 P1이 아니라 가장 최근에 멈춘 I1이 먼저 다시 실행되었다. 같은 P1인데 T5에는 Q 0, T7에는 Q 1이 찍힌 것도 차이가 있다. T5는 T1에서 쓰고 남긴 퀀텀 1을 복원 뒤 이어 쓴 결과이고, T7은 큐에서 다시 선택되며 퀀텀 2를 새로 받은 결과다.",
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
        "analysis": "인터럽트는 I1, I2, I3 순으로 시작했는데 끝난 순서는 I3, I2, I1이다. 스택에 늦게 들어간 문맥일수록 먼저 나와서, 마지막에 넣은 I2가 가장 먼저, 처음 넣은 P1이 가장 늦게 복원되었다. 이 과정에서 스택에는 문맥이 최대 3개까지 쌓였다. I2와 I1은 멈추기 전에 남아 있던 2 tick씩을 이어서 실행했다. 맨 끝 T11에서는 남은 시간과 퀀텀이 동시에 0이 됐지만 완료로 처리되어 FINISHED 1이 출력되었다.",
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
        "analysis": "P1은 T2에 퀀텀을 다 썼지만 남은 시간도 0이 되어 준비 큐로 돌아가지 않았다. 그래서 바로 다음 tick에 P2가 실행됐고, P1이 다시 선택되는 일은 없었다.",
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
        "analysis": "시각 2에는 P1이 이미 큐로 돌아간 뒤라 멈춰 둘 작업이 없었다. 그래서 I1이 끝났을 때 스택은 비어 있었고 CPU는 IDLE이 되었다. 그 뒤로는 큐 순서 [P2, P1] 그대로 P2, P1이 실행되었다. T3에 P2가 아니라 I1이 실행된 건, CPU가 빈 같은 시각이라도 main이 인터럽트를 먼저 시작하기 때문이다.",
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
        "analysis": "P1은 시각 1에 끝났지만, main의 반복 조건이 인터럽트 완료 수까지 보기 때문에 프로그램이 바로 끝나지 않았다. 시각 1~3에는 실행할 작업이 없어 IDLE이 두 번 찍혔고, 이 2 tick도 TICKS 5에 들어간다.",
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
          esc("하나의 CPU에서 프로세스와 인터럽트가 어떤 순서로 실행되는지 tick 단위로 시뮬레이션하는 프로그램이다. 프로세스는 퀀텀 2의 라운드로빈으로 돌고, 인터럽트가 오면 실행 중이던 작업을 스택에 넣어 두었다가 인터럽트가 끝나면 가장 최근에 멈춘 것부터 되돌린다."),
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
