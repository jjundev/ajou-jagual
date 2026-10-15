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
