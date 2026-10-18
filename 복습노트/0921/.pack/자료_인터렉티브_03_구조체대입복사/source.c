/* 0921 · Software_3_ArrayStructureList.pdf p17(구조체의 대입과 비교), p18(자체 참조 구조체).
 * ── 강의 원문(p17) ──────────────────────────────────────────────
 * typedef struct person {
 *     char name[10];      // 문자배열로 된 이름
 *     int age;            // 나이를 나타내는 정수값
 *     float height;       // 키를 나타내는 실수값
 * } person;
 * main()
 * {
 *     person a, b;
 *     b = a;              // 가능
 * }
 * main()
 * {
 *     if( a > b )
 *         printf("a가 b보다 나이가 많음");    // 불가능
 * }
 * ── 강의 원문(p18) ──────────────────────────────────────────────
 * typedef struct ListNode {
 *     char data[10];
 *     struct ListNode *link;
 * } ListNode;
 * ────────────────────────────────────────────────────────────────
 * 화면은 정수·포인터 값만 그리므로 다음을 단순화했다(보충 표시):
 *  - person: name[10] 생략, height를 int(cm)로. ListNode: data를 int로.
 *  - 초기값, a.age 변경, 필드 비교 a.age > b.age(정리노트 보충), ListNode 예제의 main은 보충.
 *  - uninit 모드는 강의 main 그대로 a를 초기화하지 않고 b = a를 실행한다. a의 주소를 쓰지 않는
 *    미초기화 자동 변수를 읽으므로 정의되지 않은 동작이며 실행하지 않는다(첫 필드 읽기에서 중단).
 * 독립 검산: 컴파일러 없음(compiler_unavailable) → evidence/independent_0921.py 표 사용.
 */
#include <stdio.h>
#include <stddef.h>
typedef struct person {
    int age;            // 나이를 나타내는 정수값
    int height;         // 키(cm) · 강의는 float
} person;
typedef struct ListNode {
    int data;               // 강의는 char data[10]
    struct ListNode *link;
} ListNode;
static void copy_mode(int x, int y)
{
    person a = { x, y }, b;
    b = a;                  // 가능
    a.age = a.age + 1;      // a만 바꾸면?
    if( a.age > b.age )     // 필드를 골라 비교
        printf("a가 b보다 나이가 많음");
    printf(" a={%d,%d} b={%d,%d}\n", a.age, a.height, b.age, b.height);
}
static void link_mode(int x, int y)
{
    ListNode n2 = { y, NULL };
    ListNode n1 = { x, &n2 };
    ListNode c;
    c = n1;                 // 필드별 복사
    c.data = c.data + 1;    // c만 바뀜
    c.link->data = 0;       // n2를 바꿈
    int seen = n1.link->data;   // n1에서 보면?
    printf("n1={%d,%s} c={%d,%s} n2.data=%d seen=%d\n", n1.data, n1.link == &n2 ? "&n2" : "?",
           c.data, c.link == &n2 ? "&n2" : "?", n2.data, seen);
}
int main(void)
{
    copy_mode(20, 170);
    link_mode(10, 20);
    return 0;
}
