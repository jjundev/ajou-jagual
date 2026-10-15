from pathlib import Path
import re, html, subprocess
R=Path('/tmp/ds-review-pack/1015');W=R/'work'
checks={
'p6':'''#include <assert.h>
int main(void){QueueType q={3,5};assert(get_count(&q)==2);q.front=7;q.rear=1;assert(get_count(&q)==2);return 0;}''',
'p7':'''#include <assert.h>
int main(void){TwoStackQueue q={0};int v=-1;assert(!dequeue(&q,&v)&&v==-1);assert(enqueue(&q,10));assert(enqueue(&q,20));assert(dequeue(&q,&v)&&v==10);assert(enqueue(&q,30));assert(dequeue(&q,&v)&&v==20);assert(dequeue(&q,&v)&&v==30);assert(!dequeue(&q,&v));return 0;}''',
'p8':'''#include <assert.h>
#include <string.h>
int main(void){
    assert(is_palindrome("radar")==1);
    assert(is_palindrome("A man, a plan, a canal: Panama!")==1);
    assert(is_palindrome("가나")==0);
    assert(is_palindrome("가나다가")==0);
    assert(is_palindrome("가나다나가")==1);
    assert(is_palindrome("한글글한")==1);
    assert(is_palindrome("")==1);
    assert(is_palindrome("a")==1);
    assert(is_palindrome("abba")==1);
    assert(is_palindrome("abc")==0);
    char bad[]={ (char)0xc3, (char)0x28, 0 };
    assert(is_palindrome(bad)==-1);
    char long_s[CAP+2];memset(long_s,'a',CAP+1);long_s[CAP+1]=0;
    assert(is_palindrome(long_s)==-1);
    return 0;
}'''}
for pid,harness in checks.items():
 s=(R/'cards'/f'{pid}.html').read_text()
 code=html.unescape(re.search(r'<pre><code class="language-c">(.*?)</code></pre>',s,re.S).group(1))
 src=W/f'{pid}-card-verify.c';src.write_text(code+'\n'+harness)
 exe=W/f'{pid}-card-verify'
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(src),'-o',str(exe)],check=True)
 subprocess.run([str(exe)],check=True)
 print(pid,'C11 pass')
