/* 0921 · Software_2_Recursion.pdf p6 "순환 알고리즘의 구조" factorial.
 * 슬라이드 원문은 `if( n <= 1 )  return 1` 뒤에 세미콜론이 없어 그대로는 컴파일되지 않는다.
 * 아래는 그 세미콜론만 보충하고 검산용 #include와 main을 덧붙인 프로그램이다(보충 표시).
 * 독립 검산: 컴파일러 없음(compiler_unavailable) → evidence/independent_0921.py 표 사용.
 * n = 13은 int(32비트)에서 13! = 6227020800이 범위를 넘으므로 실행하지 않는다(부호 있는 정수 오버플로 UB).
 */
#include <stdio.h>                                   /* 보충 */
int factorial(int n)
{
    if( n <= 1 )  return 1;                          /* 슬라이드: return 1 (세미콜론 누락) */
    else return n * factorial(n-1);
}
int main(void)                                       /* 보충: 슬라이드에는 호출자 없음 */
{
    int r = factorial(4);                            /* 화면 입력 n (-3..12 정의됨) */
    printf("%d\n", r);
    return 0;
}

/* 비교용 보충(nobase): 슬라이드 질문 "순환 호출을 멈추는 부분이 없다면?"
 * int factorial(int n) { return n * factorial(n-1); }
 * → 종료 조건 없이 호출이 쌓여 스택이 넘칠 때까지 진행(시스템 오류). 실행하지 않는다.
 */
