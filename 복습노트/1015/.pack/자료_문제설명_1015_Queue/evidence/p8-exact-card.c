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

#include <stdio.h>
int main(void) {
    char too_many[258];
    for (int i = 0; i < 257; ++i) too_many[i] = 'a';
    too_many[257] = '\0';
    const char bad[] = {(char)0xff, '\0'};
    printf("radar=%d\n", is_palindrome("radar"));
    printf("panama=%d\n", is_palindrome("A man, a plan, a canal: Panama!"));
    printf("korean=%d\n", is_palindrome("가나"));
    printf("empty=%d\n", is_palindrome(""));
    printf("single=%d\n", is_palindrome("a"));
    printf("invalid=%d\n", is_palindrome(bad));
    printf("capacity=%d\n", is_palindrome(too_many));
    printf("null=%d\n", is_palindrome(NULL));
    return 0;
}
