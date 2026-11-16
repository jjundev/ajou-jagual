"""Build the provisional HW4 report manuscript (Notion-flavored Markdown) from HW4.c and live runs.

Code cells are cut from HW4.c by line range, and every output block comes from a fresh run of HW4.c.
Run: python3 검토자료/build_report.py   (from 과제/과제4)
"""

from pathlib import Path
import re
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


def strip_comments(code):
    """표 소스 칸용: /* */·// 주석을 지우고, 주석 때문에 빈 줄이 된 줄은 뺀다. 원래 빈 줄은 남긴다."""
    marked = re.sub(r"/\*.*?\*/", lambda m: "\n".join(["\0"] * (m.group(0).count("\n") + 1)), code, flags=re.S)
    marked = re.sub(r"//[^\n]*", "\0", marked)
    out = []
    for line in marked.split("\n"):
        bare = line.replace("\0", "")
        if "\0" in line and not bare.strip():
            continue
        out.append(bare.rstrip())
    while out and not out[0]:
        out.pop(0)
    while out and not out[-1]:
        out.pop()
    result = "\n".join(out)
    assert "//" not in result and "/*" not in result and "*/" not in result, result
    return result


def cell_code(code):
    return esc(code).replace("\n", "<br>")


def cell_text(text):
    """'#기능 명세' / '#분석' 표시와 '•' 항목을 쓴 칸 글. 줄바꿈은 그대로 <br>이 된다."""
    return esc(text.strip()).replace("\n", "<br>")


def code_table(rows):
    rows = [(strip_comments(code), text) for code, text in rows]
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
#기능 명세
• _CRT_SECURE_NO_WARNINGS: MSVC가 scanf에 내는 보안 경고를 끈다.
• stdio.h: 입출력, stdlib.h: malloc·free, string.h: 명령어 비교(strcmp)와 트리 그림(memset·memcpy)
• MAX_TIME(99): 만료 시각과 ADVANCE 목표 시각의 상한, MAX_TIMER_ID(31): 타이머 개수이자 id의 상한
• TIMER_LABEL_WIDTH(6): PRINT에서 50(01)처럼 노드 하나를 찍는 폭

#분석
• TREE_PRINT_COLUMNS(248)·TREE_PRINT_ROWS(61)는 타이머 31개가 한 줄로 이어져도 노드 줄 31개와 가지 줄 30개가 들어가는 캔버스 크기다.
"""),
    (lines(13, 22), """
#기능 명세
• Timer: 타이머 하나. expires(만료 시각), id(입력 순서 번호)
• TimerNode: Timer 하나와 왼쪽·오른쪽 자식 포인터를 가진 트리 노드

#분석
• (expires, id) 쌍이 트리의 키다. id가 겹치지 않아 키도 겹치지 않는다.
• 노드가 Timer를 값으로 들고 있어서, 자식이 둘인 노드를 지울 때 노드를 옮기지 않고 root->timer만 덮어쓸 수 있다.
"""),
    (lines(24, 44), """
#기능 명세
• 제공 함수 7개, 트리를 그리는 함수 3개(분석 대상 아님), 직접 작성한 함수 4개의 원형

#분석
• find_min_timer·print_timers는 const 포인터를 받아 트리를 읽기만 한다.
• insert_timer·delete_timer는 바뀌었을 수 있는 서브트리 루트를 돌려주고, 호출한 쪽이 그 값을 다시 대입받는다.
• 12쪽 조건대로 함수 형식·매크로·구조체는 그대로 두고 함수를 새로 만들지 않았다.
"""),
]

FUNCS = [
    ("compare_timer", "제공 함수", [(lines(46, 63), """
#기능 명세
• 만료 시각을 먼저 비교하고, 같으면 id를 비교한다. a가 작으면 -1, b가 작으면 1, 두 타이머가 아예 같으면 0을 반환한다.

#분석
• 결국 'a가 작으면 음수, b가 작으면 양수'로 읽으면 부호만으로 결과를 가를 수 있다. 다만 -1도 C 조건식에서는 참이라, 쓰는 쪽에서 > 0, == 0처럼 부호를 직접 비교해야 한다.
• id가 겹치지 않아 0은 같은 타이머일 때만 나오고, delete_timer는 이 0을 '찾았다'는 신호로 쓴다.
""")]),
    ("create_timer_node", "제공 함수", [(lines(65, 71), """
#기능 명세
• malloc으로 노드를 만들어 timer를 넣고 left·right를 NULL로 비운 뒤 주소를 반환한다.
""")]),
    ("print_timer", "제공 함수", [(lines(73, 76), """
#기능 명세
• TIMER 만료시각 id 형식으로 한 줄 출력한다. print_timers가 RANGE 출력에 쓴다. 출력 형식을 고정하려고 제공된 함수다.
""")]),
    ("print_expired", "제공 함수", [(lines(78, 80), """
#기능 명세
• EXPIRED 만료시각 id 형식으로 한 줄 출력한다. advance_time이 삭제한 뒤 부른다.
""")]),
    ("destroy_tree", "제공 함수", [(lines(173, 179), """
#기능 명세
• 후위순회로 왼쪽·오른쪽 서브트리를 먼저 해제하고 자기 노드를 마지막에 free한다.

#분석
• 자기 노드를 먼저 해제하면 root->left·right를 더는 읽을 수 없어 이 순서다.
• 트리에 연결된 노드만 정리한다. 그래서 CANCEL·ADVANCE로 떼어 낸 노드는 delete_timer가 그때 free해야 한다.
""")]),
    ("advance_time", "제공 함수", [(lines(181, 203), """
#기능 명세
• TIME target을 출력하고, 만료 시각이 target 이하인 타이머를 빠른 순서대로 지우며 EXPIRED를 출력한다. 오류면 0, 아니면 1을 반환한다.

#분석
• 매번 find_min_timer로 가장 왼쪽 노드만 보고, 그 만료 시각이 target보다 크면 멈춘다.
• 출력할 Timer 값을 expired에 미리 복사해 둔다. 지운 뒤에는 first가 해제된 노드를 가리킨다.
• root를 이중 포인터로 받아 *root에 결과를 다시 넣어서, 루트가 지워지면 main의 root도 바뀐다(추가 사례 2).
• find_min_timer가 NULL이거나 removed가 0이면 STATE_ERROR를 출력한다. 정상 동작에서는 가지 않는 분기다.
""")]),
    ("read_timers", "제공 함수", [(lines(205, 221), """
#기능 명세
• 개수와 만료 시각들을 읽어 id 1, 2, …를 붙여 insert_timer로 넣는다. 개수가 1~31, 만료 시각이 1~99를 벗어나면 0을 반환한다.

#분석
• TimerNode **로 받는 것은 main의 root 변수 자체를 바꾸기 위해서다.
• *root = insert_timer(…)는 매번 대입하지만 값이 실제로 바뀌는 건 첫 삽입(NULL → 첫 노드) 한 번뿐이다. 그 뒤로는 insert_timer가 받은 루트를 그대로 돌려준다.
""")]),
    ("insert_timer", "직접 작성한 함수", [(lines(223, 238), """
#기능 명세
• 인자: 서브트리 루트 root, 넣을 timer / 반환값: 삽입 후 서브트리 루트
• 상태 변경: 탐색이 실패한 NULL 자리에 create_timer_node로 만든 노드를 연결한다.

#분석
• compare_timer(root->timer, timer) > 0이면 root가 더 늦게 만료되므로 왼쪽, 아니면 오른쪽으로 내려간다. > 0 없이 쓰면 -1도 참이라 모두 왼쪽으로 간다.
• 재귀 결과를 root->left·right에 다시 대입해서, 내려간 쪽이 NULL이었으면 새 노드가 그 자리에 붙는다.
• 만료 시각이 같으면 나중 타이머의 id가 커서 오른쪽으로 가므로, 4쪽의 'id가 작은 쪽이 왼쪽' 규칙이 따로 처리하지 않아도 지켜진다(추가 사례 2).
""")]),
    ("find_min_timer", "직접 작성한 함수", [(lines(240, 252), """
#기능 명세
• 인자: 서브트리 루트 root / 반환값: 가장 먼저 만료될 타이머의 노드, 빈 트리면 NULL
• 상태 변경: 없음(const로 읽기만 한다)

#분석
• 먼저 만료될수록 왼쪽에 있어서, 왼쪽의 왼쪽을 계속 따라가 left가 NULL인 노드에서 멈추면 그 노드가 가장 먼저 만료될 타이머다.
• root == NULL 검사가 없으면 타이머가 모두 사라진 뒤 NEXT에서 NULL을 역참조한다(추가 사례 2·3의 EMPTY).
""")]),
    ("delete_timer", "직접 작성한 함수", [
        (lines(254, 262), """
#기능 명세
• 인자: 서브트리 루트 root, 지울 key, 결과 플래그 removed / 반환값: 삭제가 끝난 뒤 그 서브트리의 새 루트 포인터
• 상태 변경: 지운 노드를 free하고, 성공하면 *removed = 1, 못 찾으면 0

#분석
• root가 NULL이면 끝까지 내려왔는데 key가 없다는 뜻이라 removed = 0으로 두고 NULL을 반환한다.
"""),
        (lines(264, 280), """
#분석
• compare_timer 결과를 플래그 셋 중 하나로 옮긴다. -1이면 key는 오른쪽, 1이면 왼쪽, 0이면 지금 노드가 지울 타이머다.
• case마다 break가 있어 플래그 하나만 1이 된다.
"""),
        (lines(282, 284), """
#분석
• key가 오른쪽에 있으면 재귀 결과를 root->right에 다시 받는다. 오른쪽 자식이 지워지면 그 자리가 남은 자식이나 NULL로 바뀌기 때문이다.
"""),
        (lines(286, 303), """
#분석
• 자식 0개: free 후 NULL 반환. 자식 1개: child를 먼저 받아 두고 free 후 child 반환(free한 뒤에는 root->left·right를 읽을 수 없다).
• (root->left == NULL) != (root->right == NULL)은 정확히 한쪽만 빌 때 참이라, 오른쪽 자식만 있는 경우도 잡는다(추가 사례 2의 CANCEL 30 2).
• 떼어 낸 노드는 destroy_tree가 볼 수 없으므로 여기서 free해야 한다.
"""),
        (lines(305, 325), """
#분석
• 자식 2개: 노드는 그대로 두고 root->timer만 가장 가까운 타이머로 덮어쓴 뒤, 그 후보를 서브트리에서 지운다.
• 왼쪽 최댓값은 함수를 새로 만들 수 없어(12쪽) while로 찾는다. 조건이 left_max->right != NULL이라 마지막 노드에서 멈춘다. 오른쪽 최솟값은 find_min_timer를 쓴다.
• left_diff < right_diff일 때만 왼쪽을 고른다. 차이가 같으면 오른쪽이다(8쪽, 공식 예시 2의 CANCEL 20 1).
• 후보에는 한쪽 자식이 없어 재귀가 자식 0·1개 경우로 끝나고, free와 *removed = 1도 거기서 처리된다.
"""),
        (lines(326, 333), """
#분석
• key가 왼쪽에 있으면 오른쪽과 같은 방식으로 root->left에 다시 받는다.
• 지나온 노드는 바뀌지 않아 마지막에 root를 그대로 반환한다. 이 return이 없으면 부모가 자식 주소를 돌려받지 못한다.
"""),
    ]),
    ("print_timers", "직접 작성한 함수", [(lines(335, 356), """
#기능 명세
• 인자: 서브트리 루트 root, 범위 from·to / 반환값: 출력한 타이머 수
• 상태 변경: 없음(범위 [from, to] 안의 타이머를 print_timer로 출력)

#분석
• 왼쪽 → 자기 → 오른쪽 중위순회라 만료 시각 순, 같으면 id 순으로 출력된다.
• 양 끝을 포함해야 해서 >=, <=로 비교하고, 양쪽 서브트리의 개수에 자기 노드(0 또는 1)를 더해 반환한다. 합이 0이면 main이 EMPTY를 출력한다.
• root의 만료 시각이 from보다 작으면 왼쪽 서브트리를, to보다 크면 오른쪽 서브트리를 볼 필요가 없다. 이 가지치기는 8쪽 요구사항에 없어서 넣지 않았고, 모든 노드를 방문한다.
""")]),
    ("main", "제공 함수", [
        (lines(358, 375), """
#기능 명세
• 반환값: 종료 코드(0 정상, 1 입력 오류, 2 상태 오류)
• read_timers로 타이머를 넣고, 실패하면 exit_code = 1이 되어 명령을 받지 않는다.

#분석
• exit_code가 0인 동안 명령어를 읽는다. 입력이 끝나면 입력 오류, EXIT이면 정상 종료다.
"""),
        (lines(376, 392), """
#분석
• CANCEL: 범위를 확인하고 delete_timer로 지운 뒤 OK나 NOT_FOUND를 출력한다. 반환값을 root에 다시 받아 루트가 지워져도 연결이 맞는다.
• NEXT: find_min_timer가 NULL이면 EMPTY, 아니면 NEXT 만료시각 id를 출력한다.
"""),
        (lines(393, 417), """
#분석
• ADVANCE: 목표 시각이 현재보다 작거나 99를 넘으면 입력 오류다. advance_time이 0을 반환하면 exit_code 2로 끝낸다.
• PRINT: print_timer_tree로 트리 모양을 그린다.
• RANGE: 0 ≤ from ≤ to ≤ 99를 확인하고, print_timers가 0을 반환하면 EMPTY를 출력한다.
"""),
        (lines(418, 428), """
#분석
• 알 수 없는 명령어도 입력 오류다. exit_code가 1일 때만 INPUT_ERROR를 출력하고, destroy_tree로 남은 노드를 해제한 뒤 exit_code를 반환한다.
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
            ("삽입 7개", "50(01) 루트, 25(02)·75(03) 자식, 10·30·60·90 잎. 10쪽의 ADVANCE 이전 그림과 같다."),
            ("반복 1", "10(04) ≤ 25 → 잎이라 free, 25(02)의 left = NULL"),
            ("반복 2", "25(02) ≤ 25 → 오른쪽 자식만 있어 30(05)이 50(01)의 왼쪽 자식이 된다."),
            ("반복 3", "30(05) > 25 → 멈춤"),
        ]),
        "analysis": "EXPIRED가 10, 25 순으로 찍힌 것은 advance_time이 매번 가장 왼쪽 노드만 지웠기 때문이다. 25(02)는 목표 시각과 같아 지워졌고, 자식 30(05)이 그 자리를 이어받아 50(01) 바로 아래로 올라왔다. 출력과 트리 모양이 10쪽 화면과 같다.",
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
            ("NEXT", "20(01) → 왼쪽 10(02), left = NULL이라 10(02) 반환"),
            ("RANGE 10 20", "중위순회 10 → 20 → 30, 30은 범위 밖이라 2개 출력"),
            ("CANCEL 20 1", "left_diff = 20 − 10 = 10, right_diff = 30 − 20 = 10. 같으므로 오른쪽: 루트 timer를 30(03)으로 덮고 30(03) 잎 삭제"),
            ("NEXT", "가장 왼쪽은 여전히 10(02)"),
        ]),
        "analysis": "CANCEL 20 1 뒤 루트가 30(03)이 된 것은 두 후보와의 차이가 10으로 같아 오른쪽을 골랐기 때문이다. RANGE에서 10(02)이 20(01)보다 먼저 찍힌 것은 id가 아니라 만료 시각 순으로 방문해서다. 출력과 두 트리 모양이 11쪽 화면과 같다.",
    },
    {
        "id": "03-왼쪽후보-대체",
        "title": "추가 사례 1: 왼쪽 후보가 더 가까운 루트 취소",
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
            ("왼쪽 최댓값", "20(02) → 오른쪽 45(04), right = NULL이라 멈춤"),
            ("오른쪽 최솟값", "find_min_timer(root->right) = 80(03)"),
            ("차이 비교", "left_diff = 50 − 45 = 5 < right_diff = 80 − 50 = 30 → 왼쪽"),
            ("대체와 삭제", "루트 timer를 45(04)로 덮고 왼쪽 서브트리의 45(04) 잎을 free → 20(02)의 right = NULL"),
        ]),
        "analysis": "루트 자리에 45(04)가 들어가고 20(02) 아래의 45(04)가 사라졌다. 루트 노드는 그대로이고 timer 값만 바뀌었으며, free된 것은 원래 45(04) 잎이다. 왼쪽 최댓값이 왼쪽 자식이 아니라 그 오른쪽 아래에 있어서 while이 끝까지 내려가야 맞는 후보가 나온다.",
    },
    {
        "id": "04-같은-만료시각",
        "title": "추가 사례 2: 만료 시각이 모두 같은 타이머",
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
        "analysis": "만료 시각이 같으면 id가 큰 나중 타이머가 매번 오른쪽으로 가서 한 줄로 늘어섰고, NEXT·RANGE·EXPIRED도 모두 id 순으로 나왔다. CANCEL 30 2에서는 오른쪽 자식만 있던 30(02)의 자리를 30(03)이 이어받았다. ADVANCE 30에서 루트부터 지워져 트리가 비었고, 마지막 NEXT는 find_min_timer의 NULL을 받아 EMPTY를 출력했다.",
    },
    {
        "id": "05-찾지못함-빈트리",
        "title": "추가 사례 3: 없는 타이머 취소와 빈 트리",
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
            ("CANCEL 20 2", "NOT_FOUND", "(20, 1)보다 뒤 → 오른쪽 30(03), (30, 3)보다 앞 → 왼쪽 NULL, removed = 0"),
            ("CANCEL 99 1", "NOT_FOUND", "오른쪽으로만 내려가 NULL"),
            ("RANGE 21 29", "EMPTY", "세 타이머 모두 범위 밖, 0 반환"),
            ("ADVANCE 99", "EXPIRED 10 2, 20 1, 30 3", "가장 왼쪽부터 세 번 지워 트리가 빈다."),
            ("NEXT", "EMPTY", "root가 NULL이라 find_min_timer가 NULL 반환"),
            ("PRINT", "EMPTY", "print_timer_tree가 빈 트리에서 EMPTY 출력"),
        ]),
        "analysis": "취소 실패 두 번은 트리를 바꾸지 않았다. 이어진 ADVANCE 99에서 세 타이머가 모두 만료된 것이 그 근거다. CANCEL 20 2는 만료 시각만 맞고 id가 달라 다른 키로 비교되어 실패했다.",
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
        heading = f"{name} (구현)" if label == "직접 작성한 함수" else name
        md += ["<empty-block/>", f"## {heading}", code_table(rows)]
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
        md.append("**결과 분석:** " + esc(case["analysis"]))
        if case["image"]:
            md += ["<empty-block/>", "**실제 터미널 실행 화면**", f"![]({case['image']})"]
    md += ["<empty-block/>", "<empty-block/>", "# 전체 소스코드", "```c", SOURCE.read_text(encoding="utf-8").rstrip("\n"), "```", ""]
    OUT.write_text("\n".join(md), encoding="utf-8")
    missing = [c["id"] for c in CASES if not c["image"]]
    print(f"wrote {OUT} ({len(CASES)} cases, screenshots missing: {missing or 'none'})")


if __name__ == "__main__":
    build()
