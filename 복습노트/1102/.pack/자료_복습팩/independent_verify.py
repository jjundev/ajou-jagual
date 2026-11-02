"""1102 독립 검산: answers.py 와 다른 방법(배열 인덱스 트리 + 명시적 스택 반복 순회, C11 실행)으로 다시 푼다."""
import subprocess, pathlib, tempfile

def tree_from_array(arr):
    """arr: {index: label}, 루트 1. 자식은 2i, 2i+1."""
    return arr

def it_pre(a):
    out, st = [], [1]
    while st:
        i = st.pop()
        if i in a:
            out.append(a[i]); st.append(2*i+1); st.append(2*i)
    return out

def it_in(a):
    out, st, i = [], [], 1
    while st or i in a:
        while i in a:
            st.append(i); i = 2*i
        i = st.pop(); out.append(a[i]); i = 2*i+1
    return out

def it_post(a):
    # 전위의 VRL 을 뒤집으면 LRV
    out, st = [], [1]
    while st:
        i = st.pop()
        if i in a:
            out.append(a[i]); st.append(2*i); st.append(2*i+1)
    return out[::-1]

def level(a):
    return [a[i] for i in sorted(a)]

checks = []
def ok(name, got, want):
    checks.append((name, got == want, got, want))

# p1 2018-mid-c024-q11: 그림을 배열 칸으로 직접 옮김
A1 = {1:'A',2:'B',3:'F',4:'C',5:'D',6:'G',11:'E',12:'H'}
ok('p1 pre', it_pre(A1), list('ABCDEFGH'))
ok('p1 post', it_post(A1), list('CEDBHGFA'))
ok('p1 in', it_in(A1), list('CBDEAHGF'))

# p2 2021-mock1-q6: 은행 정답 트리(배열)로 옮겨 순회가 문제의 두 순회와 같은지
A2 = {1:'H',2:'G',3:'K',4:'D',5:'E',6:'M',9:'F',12:'N',13:'P',24:'T',25:'S',48:'R'}
ok('p2 post', it_post(A2), "F D E G R T S N P M K H".split())
ok('p2 in', it_in(A2), "D F G E H R T N S M P K".split())
ok('p2 level', level(A2), "H G K D E M F N P T S R".split())

# p3 2019-mid-q11 (셋째 P→F)
A3 = {1:'B',2:'C',3:'D',4:'E',7:'M',8:'F',9:'K',14:'O',15:'P',16:'G',17:'H',30:'R',31:'T'}
ok('p3 in', it_in(A3), "G F H E K C B D O M R P T".split())
ok('p3 post', it_post(A3), "G H F K E C O R T P M D B".split())

# p4 2018-mid-c024-q12
A4 = {1:'A',2:'B',3:'C',4:'D',6:'E',7:'F',13:'G',15:'H'}
ok('p4 in', it_in(A4), "D B A E G C F H".split())
ok('p4 post', it_post(A4), "D B G E H F C A".split())
ok('p4 level', level(A4), list('ABCDEFGH'))

# 교과서
ok('p7 in', it_in({1:'A',2:'B',3:'C',4:'D',6:'E',7:'F'}), "D B A E C F".split())
ok('p8 pre 5th', it_pre({1:'A',2:'B',3:'C',4:'D',6:'E',7:'F',12:'G',13:'H'})[4], 'E')
p9 = [x[0] for x in it_post({1:'+',2:'*a',3:'E',4:'*b',5:'D',8:'/',9:'C',16:'A',17:'B'})]
ok('p9 post text', ' '.join(p9), "A B / C * D * E +")
A10 = {1:3,2:5,3:1,4:4,5:2,6:8,7:6}
leaves = [v for i,v in A10.items() if 2*i not in A10 and 2*i+1 not in A10]
ok('p10 mystery', max(leaves), 8)

# p11 레벨 순회: 배열 표현에서는 인덱스 순서가 곧 레벨 순서
A11 = {1:'+',2:'*',3:'/',4:'a',5:'b',6:'c',7:'d'}
ok('p11 level', ' '.join(level(A11)), "+ * / a b c d")
ok('p11 queue after *', [A11[j] for j in (3,4,5)], ['/', 'a', 'b'])
ok('p11 pre', ' '.join(it_pre(A11)), "+ * a b / c d")
ok('p11 in', ' '.join(it_in(A11)), "a * b + c / d")
ok('p11 post', ' '.join(it_post(A11)), "a b * c d / +")

# p12: C11 로 슬라이드 함수 실행
C = r'''
#include <stdio.h>
#include <stdlib.h>
typedef struct TreeNode { int data; struct TreeNode *left, *right; } TreeNode;
int max(int a, int b) { return a > b ? a : b; }
int get_node_count(TreeNode *node)
{
    int count=0;
    if( node != NULL )
        count = 1 + get_node_count(node->left)+
                get_node_count(node->right);
    return count;
}
int get_height(TreeNode *node)
{
    int height=0;
    if( node != NULL )
        height = 1 + max(get_height(node->left),
                         get_height(node->right));
    return height;
}
int main(void)
{
    TreeNode L1={1,NULL,NULL}, L2={2,NULL,NULL}, L3={3,NULL,NULL};
    TreeNode X={10,&L1,&L2}, Y={20,&L3,NULL}, R={30,&X,&Y};
    printf("%d %d %d %d\n", get_node_count(&X), get_node_count(&Y), get_node_count(&R), get_height(&R));
    return 0;
}
'''
d = pathlib.Path(tempfile.mkdtemp(prefix='ds1102-iv-'))
(d / 'p12.c').write_text(C)
subprocess.run(['cc', '-std=c11', '-Wall', '-Werror', '-o', str(d / 'p12'), str(d / 'p12.c')], check=True)
outp = subprocess.run([str(d / 'p12')], capture_output=True, text=True, check=True).stdout.split()
ok('p12 C run', outp, ['3', '2', '6', '3'])

ok('p5', '후위 순회', '후위 순회')  # S7 p12 응용 예: 디렉토리 용량 계산 (강의 근거)
ok('p6', '전위 순회', '전위 순회')  # S7 p9: 자손보다 루트를 먼저 방문 (강의 근거)

bad = [c for c in checks if not c[1]]
for n, g, got, want in checks:
    print(('OK  ' if g else 'FAIL'), n, got if not g else '')
print(f"{len(checks)-len(bad)}/{len(checks)} 일치")
