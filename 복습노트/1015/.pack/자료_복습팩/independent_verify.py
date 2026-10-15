from pathlib import Path
import html
import re
import subprocess

root = Path('/tmp/ds-review-pack/1015')
cases = {
    'p6': r'''
#include <assert.h>
int main(void) {
    QueueType q = {0};
    for (int f = 0; f < 8; ++f) {
        for (int r = 0; r < 8; ++r) {
            q.front=f; q.rear=r;
            int expected=0, i=f;
            while (i != r) { i=(i+1)%8; ++expected; }
            assert(get_count(&q)==expected);
        }
    }
    return 0;
}''',
    'p7': r'''
#include <assert.h>
int main(void) {
    TwoStackQueue q={0}; int v=-10;
    assert(!dequeue(&q,&v) && v==-10);
    for(int i=0;i<256;++i) assert(enqueue(&q,i));
    assert(!enqueue(&q,999));
    for(int i=0;i<100;++i) { assert(dequeue(&q,&v)); assert(v==i); }
    for(int i=256;i<356;++i) assert(enqueue(&q,i));
    for(int i=100;i<356;++i) { assert(dequeue(&q,&v)); assert(v==i); }
    assert(!dequeue(&q,&v));
    return 0;
}''',
    'p8': r'''
#include <assert.h>
#include <string.h>
int main(void) {
    assert(is_palindrome("radar")==1);
    assert(is_palindrome("Race, car!")==1);
    assert(is_palindrome("A man, a plan, a canal: Panama!")==1);
    assert(is_palindrome("abca")==0);
    assert(is_palindrome("")==1);
    assert(is_palindrome("1a1")==1);
    char s[258]; memset(s,'a',257); s[257]=0;
    assert(is_palindrome(s)==-1);
    return 0;
}''',
}
for pid, harness in cases.items():
    src = (root / 'cards' / f'{pid}.html').read_text()
    match = re.search(r'<pre><code class="language-c">(.*?)</code></pre>', src, re.S)
    assert match, pid
    code = html.unescape(match.group(1))
    cfile = root / 'work' / f'independent-{pid}.c'
    exe = root / 'work' / f'independent-{pid}'
    cfile.write_text(code + '\n' + harness)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(cfile),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
    print(pid, 'C11 compile and independent cases pass')
