from pathlib import Path
import html
import re
import subprocess

root = Path('/tmp/ds-review-pack/1015')
markup = (root/'cards/p8.html').read_text()
code = html.unescape(re.search(r'<pre><code class="language-c">(.*?)</code></pre>', markup, re.S).group(1))
harness = r'''
#include <assert.h>
#include <stdio.h>
int main(void) {
    assert(is_palindrome("eye") == 1);
    assert(is_palindrome("Race, car!") == 1);
    assert(is_palindrome("A man, a plan, a canal: Panama!") == 1);
    assert(is_palindrome("가나") == 0);
    assert(is_palindrome("가나가") == 1);
    assert(is_palindrome("가 나, 가") == 1);
    assert(is_palindrome("abca") == 0);
    assert(is_palindrome("") == 1);
    assert(is_palindrome("A") == 1);
    assert(is_palindrome(NULL) == -1);
    char bad[] = {(char)0xff, 0};
    assert(is_palindrome(bad) == -1);
    char long_s[CAP+2];
    for (int i=0; i<CAP+1; ++i) long_s[i] = 'a';
    long_s[CAP+1] = 0;
    assert(is_palindrome(long_s) == -1);
    puts("UTF-8 and error cases pass");
    return 0;
}
'''
cfile = root/'work/final-independent-p8.c'
exe = root/'work/final-independent-p8'
cfile.write_text(code+'\n'+harness)
subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',str(cfile),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
