#include <locale.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <wctype.h>
#define CAP 256
/* UTF-8 로캘에서 1=회문, 0=비회문, -1=입력·로캘 오류/용량 초과 */
int is_palindrome(const char *s) {
    if (!s) return -1;
    const char *loc = setlocale(LC_CTYPE, "");
    if (!loc || !(strstr(loc, "UTF-8") || strstr(loc, "utf8"))) return -1;
    wchar_t d[CAP];
    size_t head = 0, tail = 0, i = 0;
    mbstate_t state = {0};
    while (s[i] != '\0') {
        wchar_t ch;
        size_t n = mbrtowc(&ch, s + i, strlen(s + i), &state);
        if (n == (size_t)-1 || n == (size_t)-2 || n == 0) return -1;
        if (iswalnum(ch)) {
            if (tail == CAP) return -1;
            d[tail++] = towlower(ch);
        }
        i += n;
    }
    while (tail - head > 1) {
        if (d[head++] != d[--tail]) return 0;
    }
    return 1;
}
#include <assert.h>
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
}