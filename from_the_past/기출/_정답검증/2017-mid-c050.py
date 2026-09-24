"""2017-mid-c050 정답 검증. 실행하면 '<문항 id>\t<답>'을 출력한다."""
import os, subprocess, tempfile

SRC = "2017-mid-c050"


def run_c(code, stdin=""):
    with tempfile.TemporaryDirectory() as d:
        c, exe = os.path.join(d, "a.c"), os.path.join(d, "a.out")
        open(c, "w").write(code)
        subprocess.run(["cc", "-std=c11", "-Wall", "-o", exe, c], check=True, capture_output=True)
        return subprocess.run([exe], input=stdin, capture_output=True, text=True, check=True).stdout


# 1~5: 정의형 빈칸 — 실행으로 확인할 수 없음(원본 답)
def q1(): return "스택"
def q2(): return "큐"
def q3(): return "트리"
def q4(): return "완전이진트리"
def q5(): return "전위순회/preorder traversal"


def q6():
    st, rows = [], []
    for t in "7 6 2 / - 5 4 * +".split():
        if t.isdigit():
            st.append(int(t))
        else:
            b, a = st.pop(), st.pop()
            st.append({"+": a + b, "-": a - b, "*": a * b, "/": a // b}[t])
        rows.append(f"{t}:" + ",".join(map(str, st)))
    return " | ".join(rows)


def q7():
    N, q, front, rear = 8, [None] * 8, 0, 0
    def add(x):
        nonlocal rear
        rear = (rear + 1) % N; q[rear] = x
    def delete():
        nonlocal front
        front = (front + 1) % N; x = q[front]; q[front] = None; return x
    for x in (10, 20, 30, 40, 50): add(x)
    for _ in range(3): delete()
    a = f"(a) {q} front={front} rear={rear}"
    for x in (60, 70, 80, 90): add(x)
    return a + f" (b) {q} front={front} rear={rear}"


def q8():
    ch = {0: [1, 2, 3], 1: [4], 2: [5, 6], 3: [7, 8, 9], 4: [10, 11], 5: [12, 13], 6: [14, 15], 8: [16, 17], 16: [18]}
    par = {c: p for p, cs in ch.items() for c in cs}
    lvl = {0: 1}
    for v in range(1, 19): lvl[v] = lvl[par[v]] + 1
    desc = lambda v: sum(([c] + desc(c) for c in ch.get(v, [])), [])
    a = [v for v in lvl if lvl[v] == 3]
    b = [c for c in ch[par[8]] if c != 8]
    f = lambda xs: ", ".join(f"v{x}" for x in xs)
    return f"(a) {f(a)} (b) {f(b)} (c) {f(sorted(desc(8)))} (d) {max(lvl.values())} (e) {len(ch[8])}"


def bst_insert(t, k):
    if t is None: return [k, None, None]
    if k < t[0]: t[1] = bst_insert(t[1], k)
    else: t[2] = bst_insert(t[2], k)
    return t


def bst_delete(t, k):
    if t is None: return None
    if k < t[0]: t[1] = bst_delete(t[1], k)
    elif k > t[0]: t[2] = bst_delete(t[2], k)
    else:
        if t[1] is None: return t[2]
        if t[2] is None: return t[1]
        m = t[2]
        while m[1]: m = m[1]
        t[0] = m[0]; t[2] = bst_delete(t[2], m[0])
    return t


def pre(t): return [] if t is None else [t[0]] + pre(t[1]) + pre(t[2])
def ino(t): return [] if t is None else ino(t[1]) + [t[0]] + ino(t[2])
def post(t): return [] if t is None else post(t[1]) + post(t[2]) + [t[0]]


def q9():
    t = None
    for k in (55, 16, 92, 4, 29, 60, 30, 75): t = bst_insert(t, k)
    j = lambda xs: ", ".join(map(str, xs))
    path, n = [], t
    while n:
        path.append(n[0])
        if n[0] == 75: break
        n = n[1] if 75 < n[0] else n[2]
    r = f"(a) {j(pre(t))} (b) {j(ino(t))} (c) {j(post(t))} (d) {j(path)}"
    t = bst_delete(t, 55)
    return r + f" (e) 전위 {j(pre(t))}"


Q10 = r'''
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define MAX_STACK_SIZE 100
typedef int element;
typedef struct { element stack[MAX_STACK_SIZE]; int top; } StackType;
void init(StackType *s){ s->top = -1; }
int is_empty(StackType *s){ return (s->top == -1); }
int is_full(StackType *s){ return (s->top == (MAX_STACK_SIZE - 1)); }
void push(StackType *s, element item){
    if (is_full(s)) { fprintf(stderr, "full\n"); }
    else { s->top = s->top + 1; s->stack[s->top] = item; }
}
element pop(StackType *s) {
    element item;
    if (is_empty(s)) { fprintf(stderr, "empty\n"); exit(1); }
    else { item = s->stack[s->top]; s->top = s->top - 1; return item; }
}
int main(){
    char str[100]; int i, len, op1, op2; int op;
    StackType s; init(&s);
    scanf("%s", str); len = strlen(str);
    for (i = 0; i < len; i++){
        if (str[i] == '+'){ op1 = pop(&s); op2 = pop(&s); push(&s, op1 + op2); }
        else if (str[i] == '*'){ op1 = pop(&s); op2 = pop(&s); push(&s, op1 * op2); }
        else { op = str[i] - '0'; push(&s, op); }
    }
    printf("result:%d", pop(&s));
    return 0;
}
'''


def q10():
    outs = [run_c(Q10, e) for e in ("34+5*", "234*+", "9")]
    return "모범답안 코드 실행: 34+5* → " + outs[0] + ", 234*+ → " + outs[1] + ", 9 → " + outs[2]


Q11 = r'''
#include <stdio.h>
void dec_to_bin(int n){ if (n == 0) return; else { dec_to_bin(n / 2); printf("%d", n % 2); } }
int main(){ int d; scanf("%d", &d); dec_to_bin(d); return 0; }
'''


def q11():
    return "모범답안 코드 실행: 10 → " + run_c(Q11, "10") + ", 13 → " + run_c(Q11, "13")


if __name__ == "__main__":
    for i in range(1, 12):
        print(f"{SRC}-q{i}\t{globals()[f'q{i}']()}")
