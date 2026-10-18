/* 0921 · Software_3_ArrayStructureList.pdf p7(polynomial 구조체), p8(프로그램 3.2 while 루프).
 * 강의 루프 본문(while ~ 닫는 중괄호)은 원문 그대로다. 나머지는 보충:
 *  - coef: 강의는 float. 예제 계수가 정수라 int로 단순화(정리노트 s2-poly-method1 설명과 같음).
 *  - MAX_DEGREE: 강의 값 미표기. 화면용으로 6.
 *  - main, 선언, degree_a/degree_b 초기화(p8 하단 "A.degree와 B.degree를 복사함"), C.degree 계산,
 *    후처리 while 두 개(정리노트 s2-poly-add1 보충 코드).
 * 독립 검산: 컴파일러 없음(compiler_unavailable) → evidence/independent_0921.py 표 사용.
 */
#include <stdio.h>
#define MAX_DEGREE 6
typedef struct {
    int degree;
    int coef[MAX_DEGREE];   /* 강의는 float */
} polynomial;
int main(void)
{
    polynomial A = { 5, {10, 0, 0, 0, 6, 3} };   /* 화면 사례별로 바뀜 */
    polynomial B = { 3, {10, 3, 0, 1} };
    polynomial C;
    int Apos=0, Bpos=0, Cpos=0;
    int degree_a=A.degree, degree_b=B.degree;
    C.degree = (A.degree > B.degree) ? A.degree : B.degree;
    while( Apos<=A.degree && Bpos<=B.degree ){
        if( degree_a > degree_b ){ // A항 > B항
            C.coef[Cpos++]= A.coef[Apos++];
            degree_a--;
        }
        else if( degree_a == degree_b ){ // A항 == B항
            C.coef[Cpos++]=A.coef[Apos++]+B.coef[Bpos++];
            degree_a--; degree_b--;
        }
        else {                 // B항 > A항
            C.coef[Cpos++]= B.coef[Bpos++];
            degree_b--;
        }
    }
    /* 후처리: 남은 항을 C 끝으로 (보충) */
    while( Apos<=A.degree )
        C.coef[Cpos++]= A.coef[Apos++];
    while( Bpos<=B.degree )
        C.coef[Cpos++]= B.coef[Bpos++];
    for (int i = 0; i <= C.degree; i++) printf("%d ", C.coef[i]);   /* 검산 출력 */
    printf("\n");
    return 0;
}
