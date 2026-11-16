"""Build the provisional HW4 report manuscript (Notion-flavored Markdown) from HW4.c and live runs.

Code cells are cut from HW4.c by line range, and every output block comes from a fresh run of HW4.c.
Run: python3 검토자료/build_report.py   (from 과제/과제4)
"""

from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "HW4.c"
OUT = ROOT / "보고서_노션.md"
SHOTS = ROOT / "터미널_스크린샷"
LINES = SOURCE.read_text(encoding="utf-8").split("\n")

# Line anchors checked against HW4.c so a later edit to the source fails loudly instead of cutting wrong code.
ANCHORS = {
    1: "#define _CRT_SECURE_NO_WARNINGS",
    13: "typedef struct {",
    24: "/* 제공 함수 */",
    53: "int compare_timer(Timer a, Timer b) {",
    65: "TimerNode *create_timer_node(Timer timer) {",
    74: "void print_timer(Timer timer) {",
    78: "void print_expired(Timer timer) {",
    173: "void destroy_tree(TimerNode *root) {",
    181: "int advance_time(TimerNode **root, int target) {",
    207: "int read_timers(TimerNode **root) {",
    223: "TimerNode *insert_timer(TimerNode *root, Timer timer) {",
    241: "const TimerNode *find_min_timer(const TimerNode *root) {",
    256: "TimerNode *delete_timer(TimerNode *root, Timer key, int *removed) {",
    338: "int print_timers(const TimerNode *root, int from, int to) {",
    358: "int main(void) {",
    428: "}",
}
for n, text in ANCHORS.items():
    assert LINES[n - 1] == text, (n, LINES[n - 1])


def lines(a, b):
    """1-based inclusive line range of HW4.c."""
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
    (lines(1, 11), """
_CRT_SECURE_NO_WARNINGS는 Visual Studio가 scanf에 내는 경고를 끄는 매크로다. stdio.h는 입출력, stdlib.h는 malloc·free, string.h는 명령어를 고르는 strcmp와 트리 그림의 memset·memcpy 때문에 포함한다.

MAX_TIME(99)은 만료 시각과 ADVANCE 목표 시각의 상한이다. MAX_TIMER_ID(31)는 타이머 개수의 상한인데, read_timers가 id를 1부터 개수까지 붙여서 id의 상한도 된다.

TIMER_LABEL_WIDTH(6)는 PRINT에서 노드 하나를 50(01)처럼 여섯 글자로 찍는 폭이다. TREE_PRINT_COLUMNS(248)와 TREE_PRINT_ROWS(61)는 트리 그림을 그릴 캔버스 크기로, 타이머 31개가 한 줄로 이어져도 노드 줄 31개와 가지 줄 30개가 들어간다.
"""),
    (lines(13, 22), """
Timer는 타이머 하나의 값으로, expires는 만료 시각이고 id는 입력 순서대로 붙는 번호다. 두 값을 합친 것이 트리의 키다.

TimerNode는 Timer 하나와 왼쪽·오른쪽 자식 포인터를 가진 트리 노드다. 노드가 Timer를 값으로 들고 있어서, delete_timer에서 자식이 둘인 노드를 지울 때 노드를 옮기지 않고 root->timer만 다른 타이머로 덮어쓸 수 있다.
"""),
    (lines(24, 44), """
제공 함수, 트리를 그리는 함수 3개(분석 대상 아님), 직접 작성한 함수 4개의 원형이다.

find_min_timer와 print_timers는 const TimerNode *를 받아 트리를 읽기만 한다. insert_timer와 delete_timer는 TimerNode *를 돌려주고, 호출한 쪽은 그 값을 다시 대입받아 바뀌었을 수 있는 서브트리 루트를 연결한다.

과제 12쪽 조건대로 함수 형식·매크로·구조체는 그대로 두었고 함수를 새로 만들지 않았다.
"""),
]

FUNCS = [
    ("compare_timer", "제공 함수", [(lines(46, 63), """
두 타이머의 순서를 정한다. 만료 시각이 다르면 먼저 만료되는 쪽이 앞이고, 같으면 id가 작은 쪽이 앞이다. a가 앞이면 -1, 뒤면 1, 둘 다 같으면 0을 돌려준다.

위 주석처럼 'a가 더 작으면 음수, b가 더 작으면 양수'로 읽으면 된다. 다만 -1도 C의 조건식에서는 참이라, 결과를 쓰는 쪽에서 > 0이나 == 0처럼 부호를 직접 비교해야 한다.

id가 겹치지 않으니 트리 안의 서로 다른 두 타이머를 비교해서 0이 나오는 일은 없다. delete_timer는 0을 지울 타이머를 찾았다는 신호로 쓴다.
""")]),
    ("create_timer_node", "제공 함수", [(lines(65, 71), """
malloc으로 노드를 만들어 timer를 복사하고 left·right를 NULL로 비운 뒤 그 주소를 돌려준다. insert_timer가 빈 자리(NULL)에 닿았을 때 이 반환값이 그 자리에 연결된다.
""")]),
    ("print_timer", "제공 함수", [(lines(73, 76), """
타이머 하나를 TIMER 만료시각 id 형식으로 출력한다. print_timers가 범위 안의 타이머마다 이 함수를 불러 RANGE의 출력 형식을 맞춘다.
""")]),
    ("print_expired", "제공 함수", [(lines(78, 80), """
만료된 타이머 하나를 EXPIRED 만료시각 id로 출력한다. advance_time이 삭제에 성공한 다음에 부른다.
""")]),
    ("destroy_tree", "제공 함수", [(lines(173, 179), """
왼쪽, 오른쪽 서브트리를 먼저 해제하고 마지막에 자기 노드를 free하는 후위순회다. 자기 노드를 먼저 해제하면 root->left와 root->right를 더는 읽을 수 없어 순서가 이렇게 된다.

main이 끝날 때 트리에 아직 연결된 노드만 정리한다. CANCEL이나 ADVANCE로 트리에서 떼어 낸 노드는 이 함수가 볼 수 없으니, delete_timer가 떼어 내는 순간 free해야 한다.
""")]),
    ("advance_time", "제공 함수", [(lines(181, 203), """
현재 시각을 target으로 옮기면서 그때까지 만료되는 타이머를 빠른 순서대로 지운다.

반복마다 find_min_timer로 가장 먼저 만료될 타이머를 보고, 그 만료 시각이 target보다 크면 더 지울 것이 없어 멈춘다. target 이하이면 그 Timer 값을 expired에 복사해 두고 delete_timer로 지운 다음 EXPIRED를 출력한다. 최솟값 노드는 왼쪽 자식이 없어서 언제나 자식 0·1개 경우로 지워지고 free된다. 지운 뒤에는 first가 해제된 노드를 가리키므로 출력할 값을 미리 복사해 두는 것이다.

root를 이중 포인터로 받아 delete_timer의 반환값을 *root에 다시 넣는다. 지운 타이머가 전체 루트였다면 main의 root도 여기서 바뀐다(추가 사례 2).

find_min_timer가 NULL을 주거나 removed가 0이면 트리 상태가 어긋난 것으로 보고 STATE_ERROR를 출력한 뒤 0을 돌려주며, main은 종료 코드 2로 끝난다. 반복 조건이 *root != NULL이고 최솟값은 트리 안에 있는 타이머라 정상 동작에서는 이 분기에 가지 않는다.
""")]),
    ("read_timers", "제공 함수", [(lines(205, 221), """
첫 줄의 개수와 그 개수만큼의 만료 시각을 읽어, 읽은 순서대로 id 1, 2, …를 붙여 insert_timer로 넣는다. 개수가 1~31을 벗어나거나 만료 시각이 1~99를 벗어나면 0을 돌려주고, main은 INPUT_ERROR를 출력한다.

root를 TimerNode **로 받는 것은 main에 있는 root 변수 자체를 바꾸기 위해서다. *root = insert_timer(*root, timer)는 타이머마다 대입하지만 값이 실제로 바뀌는 것은 첫 삽입에서 NULL이 첫 노드 주소로 바뀔 때 한 번뿐이다. 그 뒤로는 insert_timer가 받은 루트를 그대로 돌려준다.
""")]),
    ("insert_timer", "직접 작성한 함수", [(lines(223, 238), """
timer를 root 서브트리에 넣고, 넣은 뒤의 서브트리 루트를 돌려준다.

root가 NULL이면 탐색이 실패한 자리라서 create_timer_node로 만든 새 노드가 이 서브트리의 루트가 된다. 그렇지 않으면 compare_timer(root->timer, timer) > 0, 곧 root가 새 타이머보다 늦게 만료될 때 왼쪽으로, 아닐 때 오른쪽으로 내려간다. > 0 없이 반환값을 바로 조건에 쓰면 -1도 참이 되어 모든 타이머가 왼쪽으로만 들어간다.

재귀 호출의 반환값을 root->left나 root->right에 다시 대입하는 이유는, 내려간 쪽이 NULL이었다면 그 자리에 새 노드를 이어 붙여야 해서다. 이미 자식이 있던 쪽은 같은 주소가 다시 들어간다. root 자신은 바뀌지 않았으니 root를 그대로 돌려준다.

만료 시각이 같으면 나중에 들어온 타이머의 id가 더 커서 항상 오른쪽으로 간다. 그래서 '같은 시각이면 id가 작은 쪽이 왼쪽'이라는 4쪽 규칙이 따로 처리하지 않아도 지켜진다(추가 사례 2).
""")]),
    ("find_min_timer", "직접 작성한 함수", [(lines(240, 252), """
가장 먼저 만료될 타이머의 노드를 돌려주고, 트리가 비었으면 NULL을 돌려준다. 트리를 바꾸지 않아서 const 포인터로 받고 돌려준다.

먼저 만료되는 타이머일수록 왼쪽에 있으니, left가 NULL인 노드가 나올 때까지 왼쪽으로만 내려가면 그 노드가 답이다. 만료 시각이 같은 타이머도 id가 작은 쪽이 왼쪽에 들어가 있어 오른쪽 서브트리는 볼 필요가 없다.

맨 앞의 root == NULL 검사는 타이머가 모두 만료되거나 취소된 뒤 NEXT가 들어올 때 필요하다. 검사 없이 root->left를 읽으면 NULL을 역참조한다. main은 NULL을 받으면 EMPTY를 출력한다(추가 사례 2, 3).
""")]),
    ("delete_timer", "직접 작성한 함수", [
        (lines(254, 262), """
key와 같은 타이머를 root 서브트리에서 지우고, 지운 뒤의 서브트리 루트를 돌려준다. 지웠으면 *removed에 1, 찾지 못했으면 0을 넣는다.

root가 NULL이면 key를 따라 끝까지 내려왔는데 없었다는 뜻이다. removed를 0으로 두고 빈 서브트리인 NULL을 그대로 돌려준다.
"""),
        (lines(264, 280), """
compare_timer의 결과를 세 플래그 중 하나로 옮긴다. -1은 root가 key보다 먼저 만료된다는 뜻이라 key는 오른쪽에 있고, 1이면 왼쪽에 있으며, 0이면 지금 노드가 지울 타이머다.

case마다 break를 두어 플래그 하나만 1이 된다. break가 없으면 case -1에서 아래 case까지 이어서 실행되어 세 플래그가 모두 1이 된다.
"""),
        (lines(282, 284), """
key가 오른쪽 서브트리에 있는 경우다. 재귀 호출의 결과를 root->right에 다시 받는 이유는 오른쪽 자식이 바로 지울 노드였을 때 그 자리가 남은 자식이나 NULL로 바뀌기 때문이다. 대입 후에는 함수 끝의 return root;로 간다.
"""),
        (lines(286, 303), """
지울 노드를 찾은 경우다. 자식이 없으면 노드를 free하고 NULL을 돌려준다. 자식이 하나면 그 자식을 child에 받아 둔 뒤 free하고 child를 돌려준다. free한 다음에는 root->left나 root->right를 읽을 수 없으니 child를 먼저 저장한다.

자식 하나 조건 (root->left == NULL) != (root->right == NULL)은 둘 중 정확히 하나만 비었을 때 참이다. 왼쪽 자식만 있는 경우와 오른쪽 자식만 있는 경우를 모두 잡고, child도 삼항 연산자로 있는 쪽을 고른다(추가 사례 2의 CANCEL 30 2는 오른쪽 자식만 있는 경우).

C에는 쓰지 않는 메모리를 알아서 거둬 가는 장치가 없고 destroy_tree도 트리에 연결된 노드만 해제한다. 여기서 free하지 않으면 떼어 낸 노드는 프로그램이 끝날 때까지 남는다.
"""),
        (lines(305, 325), """
자식이 둘이면 노드는 그대로 두고 root->timer만 만료 시각이 가장 가까운 타이머로 덮어쓴 다음, 그 타이머가 원래 있던 노드를 서브트리에서 지운다.

왼쪽 후보는 왼쪽 서브트리의 최댓값이다. find_min_timer는 최솟값만 찾고 함수를 새로 만들 수 없어서(12쪽) while로 오른쪽 끝까지 내려가 찾았다. 조건이 left_max->right != NULL이라 마지막 노드에서 멈추고, left_max가 NULL이 되는 일이 없다. 오른쪽 후보는 오른쪽 서브트리의 최솟값이라 find_min_timer를 그대로 쓰고, 반환형에 맞춰 const로 받았다.

left_diff(삭제 노드 − 왼쪽 최댓값)가 right_diff(오른쪽 최솟값 − 삭제 노드)보다 작을 때만 왼쪽을 고른다. 둘이 같으면 if를 건너뛰어 오른쪽 후보로 대체하므로 8쪽의 '같으면 오른쪽' 규칙이 지켜진다(공식 예시 11쪽의 CANCEL 20 1).

후보를 지우는 재귀 호출은 후보 노드에서 자식 0·1개 경우로 들어간다. 왼쪽 최댓값에는 오른쪽 자식이, 오른쪽 최솟값에는 왼쪽 자식이 없기 때문이다. free와 *removed = 1은 그 호출이 처리하고, 결과를 root->left나 root->right에 다시 받아 후보가 바로 아래 자식이었을 때 바뀐 자리를 연결한다. 이 노드 자체는 남아 있으니 root를 돌려준다.
"""),
        (lines(326, 333), """
key가 왼쪽 서브트리에 있는 경우로, 오른쪽과 같은 방식으로 결과를 root->left에 다시 받는다.

탐색하며 지나온 노드는 바뀌지 않았으므로 마지막에 root를 돌려준다. 이 return이 없으면 탐색하며 지나온 노드가 부모에게 자기 주소를 돌려주지 못한다.
"""),
    ]),
    ("print_timers", "직접 작성한 함수", [(lines(335, 356), """
만료 시각이 [from, to]에 드는 타이머를 출력하고 출력한 개수를 돌려준다.

왼쪽 서브트리 → 자기 노드 → 오른쪽 서브트리 순서의 중위순회라 만료 시각 순, 같은 시각이면 id 순으로 출력된다. 양 끝 시각도 포함해야 해서 >=와 <=로 비교한다.

cnt는 호출마다 0에서 시작하는 지역 변수다. 왼쪽과 오른쪽 서브트리가 돌려준 개수에 자기 노드가 범위 안이면 1을 더해 돌려주고, 맨 위에서 받은 합이 0이면 main이 EMPTY를 출력한다(추가 사례 3).

위 주석에 적은 것처럼 root의 만료 시각이 from보다 작으면 왼쪽 서브트리는, to보다 크면 오른쪽 서브트리는 볼 필요가 없다. 8쪽 요구사항에 없어서 넣지 않았고, 지금은 범위 밖 노드도 모두 방문한다.
""")]),
    ("main", "제공 함수", [
        (lines(358, 375), """
트리 루트 root를 NULL, 현재 시각 current_time을 0으로 두고 read_timers로 타이머를 넣는다. 읽기에 실패하면 exit_code가 1이 되어 명령을 받지 않는다.

exit_code가 0인 동안 명령어를 하나씩 읽는다. 더 읽을 입력이 없으면 입력 오류, EXIT이면 정상 종료로 반복을 끝낸다.
"""),
        (lines(376, 392), """
CANCEL은 만료 시각과 id를 읽어 범위를 확인한 뒤 delete_timer로 지우고, removed에 따라 OK나 NOT_FOUND를 출력한다. 반환값을 root에 다시 받아 지운 타이머가 루트였어도 연결이 맞는다.

NEXT는 find_min_timer의 결과가 NULL이면 EMPTY를, 아니면 그 타이머를 NEXT 만료시각 id로 출력한다. 트리는 바뀌지 않는다.
"""),
        (lines(393, 417), """
ADVANCE는 목표 시각이 현재 시각보다 작거나 99를 넘으면 입력 오류로 처리한다. 시간은 앞으로만 간다. 통과하면 current_time을 갱신하고 advance_time을 부르며, 그 함수가 0을 돌려주면 exit_code 2로 끝낸다.

PRINT는 PRINT 한 줄을 찍고 print_timer_tree로 트리 모양을 그린다. 빈 트리면 EMPTY가 나온다.

RANGE는 0 ≤ from ≤ to ≤ 99를 확인하고 머리줄을 출력한 다음 print_timers를 부른다. 돌려받은 개수가 0이면 EMPTY를 출력한다.
"""),
        (lines(418, 428), """
알 수 없는 명령어도 입력 오류다. 반복이 끝나면 exit_code가 1일 때만 INPUT_ERROR를 출력하고, destroy_tree로 남은 노드를 해제한 뒤 exit_code를 프로그램 종료 코드로 돌려준다.
"""),
    ]),
]


# ---------------------------------------------------------------- execution cases

CASES = [
    {
        "id": "01-공식예시-10쪽",
        "title": "공식 예시 1 (10쪽): 시간 진행과 만료",
        "input": "7\n50 25 75 10 30 60 90\nADVANCE 25\nPRINT\nEXIT\n",
        "expected": """TIME 25
EXPIRED 10 4
EXPIRED 25 2
PRINT
    __50(01)___
   /           \\
30(05)      75(03)_
           /       \\
        60(06)  90(07)""",
        "table": (["단계", "트리에서 일어난 일"], [
            ("삽입 7개", "50(01)이 루트, 25(02)·75(03)가 그 자식, 10(04)·30(05)·60(06)·90(07)이 잎이 된다. 10쪽 오른쪽 위의 ADVANCE 이전 그림이 이 상태다."),
            ("반복 1", "가장 왼쪽 10(04)은 10 ≤ 25라 지운다. 잎이므로 free되고 25(02)의 left가 NULL이 된다."),
            ("반복 2", "가장 왼쪽은 이제 25(02)다. 25 ≤ 25라 지우는데, 오른쪽 자식 30(05)만 남아 자식 1개 경우다. delete_timer가 30(05)을 돌려줘 50(01)의 왼쪽 자식이 된다."),
            ("반복 3", "가장 왼쪽 30(05)은 30 > 25라 반복을 멈춘다."),
        ]),
        "analysis": "EXPIRED가 10, 25 순서로 찍힌 것은 advance_time이 매번 가장 왼쪽 노드 하나만 지웠기 때문이다. 25(02)는 만료 시각이 목표 시각과 같아 지워졌고, 30(05)부터는 목표 시각보다 늦어 남았다. PRINT에서 30(05)이 50(01) 바로 아래로 올라온 것은 자식이 하나 남은 25(02)를 지울 때 그 자식이 25(02)의 자리를 이어받은 결과다. 출력과 트리 모양이 10쪽 화면과 같다.",
    },
    {
        "id": "02-공식예시-11쪽",
        "title": "공식 예시 2 (11쪽): 조회·범위 출력·루트 취소",
        "input": "3\n20 10 30\nNEXT\nRANGE 10 20\nPRINT\nCANCEL 20 1\nPRINT\nNEXT\nEXIT\n",
        "expected": """NEXT 10 2
RANGE 10 20
TIMER 10 2
TIMER 20 1
PRINT
    20(01)_
   /       \\
10(02)  30(03)
CANCEL 20 1 OK
PRINT
    ____30(03)
   /
10(02)
NEXT 10 2""",
        "table": (["명령", "트리에서 일어난 일"], [
            ("NEXT", "루트 20(01)에서 왼쪽 10(02)로 내려가면 left가 NULL이라 10(02)를 돌려준다."),
            ("RANGE 10 20", "중위순회로 10(02) → 20(01) → 30(03)을 방문한다. 30은 범위 밖이라 두 개만 출력하고 2를 돌려준다."),
            ("CANCEL 20 1", "루트가 자식 둘이다. 왼쪽 최댓값 10, 오른쪽 최솟값 30으로 left_diff = 20 − 10 = 10, right_diff = 30 − 20 = 10이다. 같으므로 오른쪽을 골라 루트의 timer를 30(03)으로 덮어쓰고, 오른쪽 서브트리의 30(03) 잎을 지운다."),
            ("NEXT", "가장 왼쪽은 여전히 10(02)이다."),
        ]),
        "analysis": "CANCEL 20 1 뒤 루트가 30(03)이 된 것은 양쪽 후보와의 차이가 10으로 같아 오른쪽 후보를 고른 결과다. left_diff < right_diff일 때만 왼쪽으로 가는 조건이 이 동률 규칙을 만든다. RANGE에서 20(01)이 10(02)보다 뒤에 찍힌 것은 id가 아니라 만료 시각 순으로 방문했기 때문이다. 출력과 두 트리 모양이 11쪽 화면과 같다.",
    },
    {
        "id": "03-왼쪽후보-대체",
        "title": "추가 사례 1: 왼쪽 후보가 더 가까운 루트 취소",
        "purpose": "공식 예시 11쪽은 두 후보의 차이가 같아 오른쪽이 골라졌다. 왼쪽 후보가 더 가까울 때와, 왼쪽 최댓값이 왼쪽 자식보다 더 아래에 있을 때를 확인한다.",
        "input": "5\n50 20 80 45 90\nPRINT\nCANCEL 50 1\nPRINT\nEXIT\n",
        "expected": """PRINT
    ____50(01)_____
   /               \\
20(02)_____     80(03)_____
           \\               \\
        45(04)          90(05)
CANCEL 50 1 OK
PRINT
    45(04)_
   /       \\
20(02)  80(03)_____
                   \\
                90(05)""",
        "table": (["단계", "값"], [
            ("왼쪽 최댓값", "left_max는 20(02)에서 시작해 오른쪽 45(04)로 간다. 45(04)의 right가 NULL이라 멈춘다."),
            ("오른쪽 최솟값", "find_min_timer(root->right)는 80(03)이다."),
            ("차이 비교", "left_diff = 50 − 45 = 5, right_diff = 80 − 50 = 30. 5 < 30이라 왼쪽을 고른다."),
            ("대체와 삭제", "루트의 timer를 45(04)로 덮어쓰고, 왼쪽 서브트리에서 45(04)를 지운다. 20(02)보다 늦으니 오른쪽으로 가서 잎을 free하고 20(02)의 right가 NULL이 된다."),
        ]),
        "analysis": "루트 자리에 45(04)가 들어가고 20(02) 아래의 45(04)가 사라졌다. 노드를 옮긴 것이 아니라 루트 노드의 timer 값만 바뀌었고, 실제로 free된 것은 45(04)가 원래 있던 잎이다. 왼쪽 최댓값이 왼쪽 자식 20(02)이 아니라 그 오른쪽 아래의 45(04)였으므로, while이 오른쪽 끝까지 내려가야 맞는 후보가 나온다.",
    },
    {
        "id": "04-같은-만료시각",
        "title": "추가 사례 2: 만료 시각이 모두 같은 타이머",
        "purpose": "만료 시각이 같을 때 id 순서가 삽입·조회·범위 출력·만료에 모두 지켜지는지, 오른쪽 자식만 있는 노드를 지울 때와 전체 루트가 지워질 때를 확인한다.",
        "input": "4\n30 30 30 30\nPRINT\nNEXT\nRANGE 30 30\nCANCEL 30 2\nPRINT\nADVANCE 30\nNEXT\nEXIT\n",
        "expected": """PRINT
30(01)_____
           \\
        30(02)_____
                   \\
                30(03)_____
                           \\
                        30(04)
NEXT 30 1
RANGE 30 30
TIMER 30 1
TIMER 30 2
TIMER 30 3
TIMER 30 4
CANCEL 30 2 OK
PRINT
30(01)_____
           \\
        30(03)_____
                   \\
                30(04)
TIME 30
EXPIRED 30 1
EXPIRED 30 3
EXPIRED 30 4
EMPTY""",
        "analysis": "모든 타이머가 앞 타이머의 오른쪽으로 들어가 한 줄로 늘어섰다. 만료 시각이 같으면 compare_timer가 id를 비교하고, 나중에 들어온 타이머일수록 id가 커서 insert_timer가 매번 오른쪽을 골랐다. NEXT가 30 1을, RANGE 30 30이 id 1~4 순서를 출력한 것도 이 배치에서 나온다. from과 to가 같아도 양 끝을 포함해 네 개가 모두 나왔다. CANCEL 30 2에서 30(02)은 오른쪽 자식만 있어 그 자식 30(03)이 30(01)의 오른쪽에 이어졌다. ADVANCE 30에서는 루트 30(01)이 먼저 지워져 main의 root가 30(03)으로 바뀌었고, 이어서 30(03)과 30(04)가 지워져 트리가 비었다. 마지막 NEXT의 EMPTY는 find_min_timer가 빈 트리에서 NULL을 돌려준 결과다.",
    },
    {
        "id": "05-찾지못함-빈트리",
        "title": "추가 사례 3: 없는 타이머 취소와 빈 트리",
        "purpose": "지울 타이머가 없을 때, 범위에 타이머가 없을 때, 모든 타이머가 만료된 뒤의 명령을 확인한다.",
        "input": "3\n20 10 30\nCANCEL 20 2\nCANCEL 99 1\nRANGE 21 29\nADVANCE 99\nNEXT\nPRINT\nEXIT\n",
        "expected": """CANCEL 20 2 NOT_FOUND
CANCEL 99 1 NOT_FOUND
RANGE 21 29
EMPTY
TIME 99
EXPIRED 10 2
EXPIRED 20 1
EXPIRED 30 3
EMPTY
PRINT
EMPTY""",
        "table": (["명령", "실제 출력", "이유"], [
            ("CANCEL 20 2", "NOT_FOUND", "만료 시각 20인 타이머는 id 1이다. (20, 1)보다 뒤라 오른쪽 30(03)으로, (30, 3)보다 앞이라 왼쪽으로 가서 NULL에 닿아 removed = 0이다."),
            ("CANCEL 99 1", "NOT_FOUND", "오른쪽으로만 내려가다 NULL에 닿는다."),
            ("RANGE 21 29", "EMPTY", "세 타이머 모두 범위 밖이라 print_timers가 0을 돌려준다."),
            ("ADVANCE 99", "EXPIRED 10 2, 20 1, 30 3", "가장 왼쪽부터 세 번 지워 트리가 빈다."),
            ("NEXT", "EMPTY", "root가 NULL이라 find_min_timer가 NULL을 돌려준다."),
            ("PRINT", "EMPTY", "print_timer_tree가 빈 트리에서 EMPTY를 출력한다."),
        ]),
        "analysis": "취소 실패 두 번은 트리를 바꾸지 않았다. 바로 뒤 ADVANCE 99에서 처음 넣은 세 타이머가 모두 만료된 것이 그 근거다. CANCEL 20 2가 실패한 것은 만료 시각만 맞고 id가 달라서다. 삭제 키는 만료 시각과 id를 함께 비교하므로 다른 타이머로 취급된다.",
    },
]


def terminal_transcript(exe, stdin, stdout):
    """Rebuild what the IDE terminal shows: each typed line echoed, then the output that line produced.

    HW4 prints only after reading a whole command, so the output belonging to line k is the stdout
    difference between running the first k lines and the first k-1 lines (a truncated run ends with
    INPUT_ERROR at EOF, which is dropped). The result must reduce back to the full run's stdout.
    """
    typed = stdin.rstrip("\n").split("\n")
    prev, parts = "", []
    for k in range(1, len(typed) + 1):
        out = subprocess.run([str(exe)], input="\n".join(typed[:k]) + "\n", capture_output=True,
                             text=True, timeout=5).stdout
        if k < len(typed):
            assert out.endswith("INPUT_ERROR\n") or out == prev, (k, out)
            out = out[: -len("INPUT_ERROR\n")] if out.endswith("INPUT_ERROR\n") else out
        assert out.startswith(prev), (k, out)
        parts.append(typed[k - 1] + "\n" + out[len(prev):])
        prev = out
    assert prev == stdout
    return "".join(parts).rstrip("\n")


def run_cases():
    with tempfile.TemporaryDirectory() as tmp:
        exe = Path(tmp) / "hw4"
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-o", str(exe), str(SOURCE)], check=True)
        for case in CASES:
            proc = subprocess.run([str(exe)], input=case["input"], capture_output=True, text=True, timeout=5)
            assert proc.returncode == 0, (case["title"], proc.returncode)
            assert proc.stdout.rstrip("\n") == case["expected"], (case["title"], proc.stdout)
            case["output"] = terminal_transcript(exe, case["input"], proc.stdout)
            shot = SHOTS / f"{case['id']}.png"
            case["image"] = f"터미널_스크린샷/{shot.name}" if shot.exists() else None


# ---------------------------------------------------------------- assemble

def build():
    run_cases()
    md = ['<table_of_contents color="gray"/>', "<empty-block/>", "# 구현 목적",
          esc("타이머를 만료 시각과 id를 키로 하는 이진 탐색 트리에 저장하고, 취소(CANCEL)·다음 타이머 조회(NEXT)·시간 진행(ADVANCE)·범위 출력(RANGE)·트리 출력(PRINT) 명령을 처리하는 프로그램이다. 가장 먼저 만료될 타이머가 늘 트리의 가장 왼쪽에 오도록 삽입과 삭제에서 순서를 지킨다."),
          "<empty-block/>", "<empty-block/>", "# 소스코드 분석",
          esc("HW4_skeleton.c의 선언·제공 함수·main은 그대로 두고 insert_timer, find_min_timer, delete_timer, print_timers를 직접 작성했다. 트리를 그리는 measure_timer_tree, draw_timer_tree, print_timer_tree는 과제에서 분석 대상이 아니라고 했으므로(7·14쪽) 전체 소스코드에만 싣는다."),
          "## 헤더·매크로·구조체·함수 원형", code_table(DECLS)]
    for name, label, rows in FUNCS:
        md += ["<empty-block/>", f"## {name}", label, code_table(rows)]
    md += ["<empty-block/>", "<empty-block/>", "# 실행결과 및 분석",
           esc(f"과제 10·11쪽의 공식 예시 2건과, 공식 예시에서 드러나지 않는 동작을 보여 주는 추가 사례 {len(CASES) - 2}건을 실행했다."),
           "<empty-block/>"]
    for i, case in enumerate(CASES):
        if i:
            md.append("<empty-block/>")
        md.append(f"## {case['title']}")
        if case.get("purpose"):
            md.append(esc(case["purpose"]))
        md += ["**입력**", "```plain text", case["input"].rstrip("\n"), "```", "<empty-block/>",
               "**실제 출력**", "```plain text", case["output"], "```"]
        if case.get("table"):
            header, rows = case["table"]
            md.append(plain_table(header, rows))
        md.append(esc("결과 분석: " + case["analysis"]))
        if case["image"]:
            md += ["<empty-block/>", "**실제 터미널 실행 화면**", f"![]({case['image']})"]
    md += ["<empty-block/>", "<empty-block/>", "# 전체 소스코드", "```c", SOURCE.read_text(encoding="utf-8").rstrip("\n"), "```", ""]
    OUT.write_text("\n".join(md), encoding="utf-8")
    missing = [c["id"] for c in CASES if not c["image"]]
    print(f"wrote {OUT} ({len(CASES)} cases, screenshots missing: {missing or 'none'})")


if __name__ == "__main__":
    build()
