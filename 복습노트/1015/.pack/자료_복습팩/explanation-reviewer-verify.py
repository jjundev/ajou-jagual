"""Independent semantic checks against explanation fragments, not bank answers."""
from pathlib import Path
import html
import re
import subprocess

root = Path(__file__).resolve().parent.parent
evidence = root / 'evidence'

def circular(inputs, deletes, more):
    a = [None] * 8
    f = r = 0
    for v in inputs:
        assert (r + 1) % 8 != f
        r = (r + 1) % 8
        a[r] = v
    for _ in range(deletes):
        assert f != r
        f = (f + 1) % 8
        a[f] = None
    first = (f, r, a.copy())
    for v in more:
        assert (r + 1) % 8 != f
        r = (r + 1) % 8
        a[r] = v
    return first, (f, r, a.copy())

p1a, p1b = circular([10, 20, 30, '04', 50, 60], 4, [70, 80, 90, 100])
assert p1b == (4, 2, [80, 90, 100, None, None, 50, 60, 70])
p2a, p2b = circular([10, 20, 30, 40, 50], 3, [60, 70, 80, 90])
assert p2a == (3, 5, [None, None, None, None, 40, 50, None, None])
assert p2b == (3, 1, [80, 90, None, None, 40, 50, 60, 70])
print('p1', p1b)
print('p2a', p2a)
print('p2b', p2b)

# P3: one multiple-choice question. Judge each option against the one count.
count = (5 - 3 + 8) % 8
assert count == 2
assert {k: (v == count) for k,v in {'a':1,'b':2,'c':3,'d':4}.items()} == {'a':False,'b':True,'c':False,'d':False}
print('p3 options a,b,c,d = false,true,false,false; count=2')

# P4: one multiple-choice question. 0 and 7 are empty but not all empty states.
empty_states = [(i,i) for i in range(8)]
assert not all(f == 0 and r == 0 for f,r in empty_states)
assert not all(f == 7 and r == 7 for f,r in empty_states)
assert all(f == r for f,r in empty_states)
full = (3,2)
assert (full[1] + 1) % 8 == full[0] and (full[1]-full[0]+8)%8 == 7
print('p4 options a,b,c,d = false,false,true,false; d denotes full at f3/r2')

# P5: slide S6 p9 enqueue/dequeue have bounded arithmetic, tests, and one array access.
# For a single operation the step count does not depend on n; the choice is O(1).
print('p5 options a,b,c,d = true,false,false,false; constant-step S6 p9 operations')

def card_code(pid):
    frag = (root/'explanations'/f'{pid}.html').read_text()
    card = (Path('/tmp/ds-review-pack/1015/cards')/f'{pid}.html').read_text()
    pat = r'<pre><code class="language-c">(.*?)</code></pre>'
    code = html.unescape(re.search(pat, frag, re.S).group(1))
    reference = html.unescape(re.search(pat, card, re.S).group(1))
    assert code == reference, f'{pid} explanation code differs from final card'
    return code

cases = {
    'p6': r'''
#include <assert.h>
int main(void) {
    QueueType q;
    for (int f=0; f<8; ++f) for (int r=0; r<8; ++r) {
        q.front=f; q.rear=r;
        int n=0, i=f;
        while(i!=r) { i=(i+1)%8; ++n; }
        assert(get_count(&q)==n);
    }
    return 0;
}''',
    'p7': r'''
#include <assert.h>
int main(void) {
    TwoStackQueue q={0}; int v=-1;
    assert(!dequeue(&q,&v) && v==-1);
    for(int i=0;i<CAP;++i) assert(enqueue(&q,i));
    assert(!enqueue(&q,999));
    for(int i=0;i<100;++i) { assert(dequeue(&q,&v)); assert(v==i); }
    for(int i=CAP;i<CAP+100;++i) assert(enqueue(&q,i));
    for(int i=100;i<CAP+100;++i) { assert(dequeue(&q,&v)); assert(v==i); }
    assert(!dequeue(&q,&v));
    return 0;
}''',
    'p8': r'''
#include <assert.h>
#include <string.h>
int main(void) {
    assert(is_palindrome("radar")==1);
    assert(is_palindrome("A man, a plan, a canal: Panama!")==1);
    assert(is_palindrome("가나")==0);
    assert(is_palindrome("가나가")==1);
    assert(is_palindrome("")==1);
    assert(is_palindrome("a")==1);
    assert(is_palindrome(NULL)==-1);
    char bad[]={(char)0xff,0};
    assert(is_palindrome(bad)==-1);
    char long_s[CAP+2]; memset(long_s,'a',CAP+1); long_s[CAP+1]=0;
    assert(is_palindrome(long_s)==-1);
    return 0;
}''',
}
for pid, harness in cases.items():
    src = evidence/f'reviewer-{pid}.c'
    exe = evidence/f'reviewer-{pid}'
    src.write_text(card_code(pid)+'\n'+harness)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(src),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
    print(pid, 'exact explanation/card code C11 pass')
