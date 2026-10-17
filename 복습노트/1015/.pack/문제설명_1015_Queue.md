# 자료구조및알고리즘이해 복습 1015 문제설명

왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.

문제의 첫 줄부터 검산까지 설명해요.

**목차**

- [문항별 설명](#problems)
  - [P1. 원형 큐의 get_count](#p1)
  - [P2. 두 스택으로 큐 만들기](#p2)
  - [P3. 덱으로 회문 검사하기](#p3)
  - [P4. 연결 큐 그림에서 갱신 코드 만들기](#p4)
  - [P5. 시뮬레이션의 if/else가 만드는 한 틱](#p5)
  - [P6. 원형 큐의 인덱스를 먼저 옮기기](#p6)
  - [P7. 덱의 첫 삽입과 양 끝 포인터](#p7)
  - [P8. 덱에서 마지막 원소를 삭제할 때](#p8)
  - [P9. 원형 큐의 front와 rear](#p9)
  - [P10. 원형 큐 상태 두 번 그리기](#p10)

<a id="problems"></a>

## 문항별 설명

<a id="p1"></a>

### P1. 원형 큐의 get_count

textbook-ch05-q08 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p1)

구현 조건: 강의처럼 front는 첫 원소 직전, rear는 마지막 원소의 인덱스이며 M칸 중 한 칸을 비워요. 0≤front,rear&lt;M이에요.

원형큐에 큐에 존재하는 요소의 개수를 반환하는 연산 get_count를 추가하여 보라. C언어를 이용하여 구현하여 보라.

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 08번 · 책 172쪽

원형큐에 큐에 존재하는 요소의 개수를 반환하는 연산 get_count를 추가하여 보라. C언어를 이용하여 구현하여 보라.

</details>

front는 첫 원소 직전, rear는 마지막 원소이며 한 칸을 비우는 강의 규약이에요.

#### 문제를 읽어 볼게요

빙글 돌아가는 줄에서 앞 표시와 뒤 표시만 보고, 실제로 몇 칸이 차 있는지 세는 함수를 만들어요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

‘원형 큐’, ‘요소의 개수’, ‘get_count’라는 단서에서 두 인덱스 사이의 순환 거리를 떠올려요. 수업의 원형 큐에서 `front`는 첫 요소 하나 앞, `rear`는 마지막 요소의 칸이에요. 크기 $M$인 배열에서 다음 칸은 $(i+1)\bmod M$이고 한 칸을 비워 실제 개수는 $0$부터 $M-1$까지예요. 그래서 순환 거리 `(rear - front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE`가 개수예요. $M$은 `MAX_QUEUE_SIZE`, 나머지 연산은 끝에서 0으로 돌아간 위치를 정규화해요.

#### 첫 줄을 이렇게 써요

종이에 `front` 다음 칸부터 `rear`까지 시계 방향으로 세어 보고, “개수 = 순환 거리”라고 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

`front`가 3이고 `rear`가 5라면 방문 칸은 4, 5이므로 두 개예요. 7에서 1로 감겨도 방문 칸은 0, 1이므로 두 개예요. 단순 차이는 음수가 될 수 있어 $M$을 더한 뒤 나머지를 취해요. 공백이면 두 인덱스가 같아 0이에요.

`#define MAX_QUEUE_SIZE 8
typedef struct {
    int front;
    int rear;
} QueueType;

int get_count(const QueueType *q) {
    return (q->rear - q->front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE;
}`

이 함수는 유효한 인덱스와 한 칸 비우는 원형 큐 규칙을 전제해요. 인덱스 두 개를 읽고 일정 횟수로 계산해 $O(1)$이에요.

#### 완성 답과 검산

정답은 `(rear - front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE`예요. $M=8$에서 $(5-3+8)\bmod8=2$, $(1-7+8)\bmod8=2$예요. 별도의 시계 방향 순회 계산으로 유효한 `front`·`rear` 조합 64개를 모두 대조했고 값이 일치했어요. 포화 상태도 한 칸 비워 7로 나와요.

#### 여기서 헷갈리기 쉬워요

`front` 칸 자체를 세면 하나가 많아져요. `rear - front`만 쓰면 인덱스가 7에서 0으로 돌아갈 때 음수가 돼요. 모든 칸을 채우는 다른 원형 큐 구현에는 별도의 포화 구분 정보가 필요하므로 이 식을 그대로 적용할 수 없어요.

#### 설명을 닫고 다시 해 봐요

1. `front=7, rear=1`에서 실제 점유 칸을 적으세요.
2. 순환 거리 식에 대입하세요.
3. 공백과 포화 경계에서 각각 0과 7이 되는지 확인하세요.

**페이지 요약**

#### 첫 줄

`front` 다음부터 `rear`까지 세어요.

#### 떠올릴 개념·공식

원형 큐의 순환 거리: `(rear - front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE`.

#### 답과 검산

64개 인덱스 쌍을 직접 순회한 개수와 식이 모두 같아요.

---

<a id="p2"></a>

### P2. 두 스택으로 큐 만들기

textbook-ch05-q09 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p2)

2개의 스택을 사용하여 큐를 구현할 수 있을까? 2개의 스택을 사용하여 큐를 구현해보자. 입력이 들어오면 스택 #1에 넣는다. 출력 요청이 들어오면 스택 #2에서 요소를 꺼낸다. 스택 #2가 비어 있을 때는 스택 #1의 모든 요소를 꺼내서 스택 #2에 넣는다. 프로그램으로 작성해보자.

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 09번 · 책 172쪽

2개의 스택을 사용하여 큐를 구현할 수 있을까? 2개의 스택을 사용하여 큐를 구현해보자. 입력이 들어오면 스택 #1에 넣는다. 출력 요청이 들어오면 스택 #2에서 요소를 꺼낸다. 스택 #2가 비어 있을 때는 스택 #1의 모든 요소를 꺼내서 스택 #2에 넣는다. 프로그램으로 작성해보자.

</details>

#### 문제를 읽어 볼게요

위에서만 꺼낼 수 있는 두 통으로, 먼저 넣은 물건을 먼저 꺼내는 줄을 만들어요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

‘두 스택’, ‘입력은 스택 #1’, ‘출력은 스택 #2’라는 단서에서 스택의 후입선출(LIFO) 순서를 두 번 뒤집어 큐의 선입선출(FIFO)을 만드는 방법을 떠올려요. 입력 스택 `in`에는 새 값을 쌓아요. 출력 스택 `out`이 비었을 때에만 `in`의 값을 모두 옮기면, 가장 오래된 값이 `out`의 맨 위에 와요. `out`에 값이 남아 있을 때 옮기면 나중에 온 값이 먼저 나오는 오류가 생겨요.

각 값은 입력·이동·출력에서 상수 번만 다뤄지므로 여러 연산을 합친 분할상환(amortized) 비용은 연산당 $O(1)$이에요. 한 번의 이동을 포함한 `dequeue` 최악 비용은 $O(n)$이에요.

#### 첫 줄을 이렇게 써요

“`enqueue`는 #1에 push, `dequeue`는 #2가 빌 때만 #1 전체를 #2로 이동한 뒤 pop”이라고 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

아래 C 함수는 원 카드의 용량 256, 두 `top` 초기값 0, 성공 1·실패 0 계약을 그대로 사용해요. `in.top + out.top`은 전체 저장 개수라 용량 검사는 두 스택을 합쳐야 해요.

`#define CAP 256
typedef struct { int a[CAP], top; } Stack;
typedef struct { Stack in, out; } TwoStackQueue;
/* 두 top은 0으로 초기화해 사용해요. 1은 성공, 0은 실패예요. */
int enqueue(TwoStackQueue *q, int value) {
    if (q->in.top + q->out.top >= CAP) return 0;
    q->in.a[q->in.top++] = value;
    return 1;
}
int dequeue(TwoStackQueue *q, int *value) {
    if (q->out.top == 0) {
        while (q->in.top > 0)
            q->out.a[q->out.top++] = q->in.a[--q->in.top];
    }
    if (q->out.top == 0) return 0;
    *value = q->out.a[--q->out.top];
    return 1;
}`

1. 10, 20, 30을 넣으면 `in`의 아래에서 위로 10, 20, 30이에요.
2. 첫 삭제 때 #2가 비었으므로 30, 20, 10 순서로 옮겨 `out`의 위가 10이 돼요. 10을 꺼내요.
3. 40을 새로 넣어도 `out`에 20, 30이 남아 있으므로 이동하지 않아요. 이어서 20, 30을 꺼내요.
4. 그다음 #2가 비면 #1의 40을 옮겨 꺼내요. 전체 출력은 10, 20, 30, 40이에요.

#### 완성 답과 검산

두 스택으로 FIFO 큐를 구현할 수 있어요. 독립 시뮬레이션에서 `enqueue(10), enqueue(20), enqueue(30), dequeue(), enqueue(40), dequeue(), dequeue(), dequeue()`의 출력이 10, 20, 30, 40이었어요. 빈 큐 삭제는 0을 반환하고 출력 포인터의 기존 값을 유지해요. 총 256개 저장 후 추가 삽입은 0을 반환해요. `q`와 `value`는 유효한 포인터여야 해요.

#### 여기서 헷갈리기 쉬워요

#2에 값이 남았는데 #1을 옮기면 나중에 들어온 40이 먼저 나올 수 있어요. #1만 보고 용량을 검사하면 두 스택의 합이 배열 용량을 넘어갈 수 있어요.

#### 설명을 닫고 다시 해 봐요

1. #1과 #2의 아래·위 방향을 그리세요.
2. 10, 20, 30을 넣고 한 번 꺼낸 뒤 40을 넣으세요.
3. #2가 남은 동안 다음 값이 무엇인지 쓰세요.

**페이지 요약**

#### 첫 줄

입력은 #1, 출력은 #2가 빌 때만 옮긴 뒤 pop.

#### 떠올릴 개념·공식

스택을 두 번 뒤집으면 FIFO. 분할상환 $O(1)$, 이동하는 한 번은 최악 $O(n)$.

#### 답과 검산

교차 삽입·삭제의 출력은 10, 20, 30, 40이에요.

---

<a id="p3"></a>

### P3. 덱으로 회문 검사하기

textbook-ch05-q11 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p3)

회문(palindrome)이란 앞뒤 어느 쪽에서 읽어도 같은 말·구·문 등을 의미한다. 예를 들면 “eye”, “madam, “radar” 등이다. 여기서 물론 구두점이나 스페이스, 대소문자 등은 무시하여야 한다. 덱을 이용하여 주어진 문자열이 회문인지 아닌지를 결정하는 프로그램을 작성하라. 다음 그림을 참조한다.

![rear와 front, radar 문자열과 양 끝 문자 r](figures_문제설명_1015_Queue/explain-fig-1.svg)

*rear와 front, radar 문자열과 양 끝 문자 r · 넓은 그림은 옆으로 스크롤해 보세요.*

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 11번 · 책 172쪽

회문(palindrome)이란 앞뒤 어느 쪽에서 읽어도 같은 말·구·문 등을 의미한다. 예를 들면 “eye”, “madam, “radar” 등이다. 여기서 물론 구두점이나 스페이스, 대소문자 등은 무시하여야 한다. 덱을 이용하여 주어진 문자열이 회문인지 아닌지를 결정하는 프로그램을 작성하라. 다음 그림을 참조한다.

![rear와 front, radar 문자열과 양 끝 문자 r](figures_문제설명_1015_Queue/explain-fig-2.svg)

*rear와 front, radar 문자열과 양 끝 문자 r · 넓은 그림은 옆으로 스크롤해 보세요.*

</details>

#### 문제를 읽어 볼게요

문장의 양끝 글자를 하나씩 꺼내 비교해요. 쉼표와 빈칸은 건너뛰고, 끝까지 같으면 거꾸로 읽어도 같은 말이에요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

‘앞뒤 어느 쪽에서 읽어도 같음’, ‘덱을 이용’이라는 단서에서 덱(deque)의 앞·뒤 삭제를 떠올려요. 회문(palindrome)은 무시할 구두점·공백을 걷어 내고 대소문자를 맞춘 문자들의 양 끝이 매번 같은 문자열이에요. 양끝이 다르면 즉시 거짓이고, 길이가 0 또는 1이 되도록 모두 맞으면 참이에요. 문자 수가 $k$이면 비교는 최대 $\lfloor k/2\rfloor$번이에요.

교과서에는 C 구현을 위한 인코딩·로캘 규칙이 없어요. 아래 카드의 C 코드는 UTF-8 입력과 실행 환경의 UTF-8 로캘을 전제로 `wchar_t` 문자로 해독해요. 이 해독과 `iswalnum`·`towlower`는 수업의 덱 원리에서 유도한 내용이 아니라 구현 보충이에요. 로캘별 문자 분류와 한 글자씩의 소문자화에 한정하며 모든 유니코드 정규화·완전한 대소문자 접기는 수행하지 않아요.

#### 첫 줄을 이렇게 써요

“문자를 정리해 덱에 넣고, 두 개 이상 남는 동안 앞과 뒤를 하나씩 꺼내 비교한다”라고 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

원 카드의 코드에서는 `head`와 `tail`이 배열 덱의 양쪽 경계예요. 유효한 문자만 뒤에 추가해 `d[head..tail)`을 만들고, 앞에서는 `d[head++]`, 뒤에서는 `d[--tail]`을 꺼내요. 코드 자체는 카드와 같은 구현이에요.

`#include <locale.h>
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
}`

1. `radar`: r와 r, a와 a가 같고 d 한 글자가 남아 참이에요.
2. `A man, a plan, a canal: Panama!`: 빈칸·구두점·대소문자를 정리하면 `amanaplanacanalpanama`가 되어 양끝 비교가 모두 같아요.
3. `가나`: UTF-8 로캘에서 가와 나가 달라 거짓이에요. 한글 바이트를 버리고 빈 문자열로 오판하지 않아요.

#### 완성 답과 검산

양 끝에서 꺼낸 문자가 모두 같으면 회문이에요. 제시한 코드의 반환값은 회문 1, 비회문 0, 입력·로캘 오류나 용량 초과 -1이에요. 독립 실행에서 `radar`, 문장 예시, 빈 문자열, 한 글자는 1이고 `가나`는 0이에요. 잘못된 UTF-8 바이트와 정리 후 257자는 -1이에요. 입력이 `NULL`인 경우도 -1이에요. 양 끝을 하나씩 없애므로 덱에서 $O(k)$번의 삭제를 해요.

#### 여기서 헷갈리기 쉬워요

바이트마다 `isalnum`을 호출하면 UTF-8 한글을 문자로 읽지 못해 `가나`를 잘못 참으로 판단할 수 있어요. 실행 환경에 UTF-8 로캘이 없으면 이 코드는 -1을 반환해요. 배열 크기 `CAP`은 원본 바이트가 아니라 정리 후 문자 수의 상한이에요. 원문 그림의 `rear`·`front` 방향보다 양 끝에서 같은 문자를 하나씩 꺼낸다는 규칙이 핵심이에요.

#### 설명을 닫고 다시 해 봐요

1. 구두점·공백·대소문자를 어떻게 처리할지 적으세요.
2. `radar`의 양끝을 두 차례 비교하세요.
3. 비회문과 잘못된 입력에서 반환값을 구별하세요.

**페이지 요약**

#### 첫 줄

정리한 문자를 덱에 넣고 양 끝을 하나씩 비교해요.

#### 떠올릴 개념·공식

덱 양끝 삭제로 최대 $\lfloor k/2\rfloor$번 비교해요. UTF-8 문자 해독은 구현 보충이에요.

#### 답과 검산

같으면 1, 다르면 0, 입력·로캘·용량 오류는 -1이에요.

---

<a id="p4"></a>

### P4. 연결 큐 그림에서 갱신 코드 만들기

lecture-s06-p11-linked-queue · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p4)

**강의 예제 기반 자체 출제** S6 p11

강의 그림을 바탕으로 직접 코드를 작성하는 문제예요. 단순 연결 큐의 노드는 data,link를 가지며 빈 큐 front=rear=NULL이에요. 이미 할당·초기화한 새 노드 N의 link=NULL일 때 enqueue의 빈 경우·나머지 경우 대입문을 쓰세요. 유일한 노드를 dequeue한 뒤 rear도 NULL로 만들어야 하는 이유를 설명하세요.

`/* 강의 연결 큐 그림을 바탕으로 작성할 의사코드 */
enqueue: 새 노드를 rear 뒤에 연결하고 rear를 갱신
dequeue: front 노드의 값을 보관하고 front를 다음으로 이동`

<details><summary>강의 예제 보기</summary>

S6 p11 · Software_6_Queue.pdf. 강의 연결 그림의 동작을 요약한 자체 의사코드이며 강의 원문 C 코드는 아닙니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`/* 강의 연결 큐 그림을 바탕으로 작성할 의사코드 */
enqueue: 새 노드를 rear 뒤에 연결하고 rear를 갱신
dequeue: front 노드의 값을 보관하고 front를 다음으로 이동`

</details>

#### 문제를 내 말로 읽어요

강의 그림을 바탕으로 직접 코드를 작성하는 문제예요. 단순 연결 큐의 노드는 data,link를 가지며 빈 큐 front=rear=NULL이에요. 이미 할당·초기화한 새 노드 N의 link=NULL일 때 enqueue의 빈 경우·나머지 경우 대입문을 쓰세요. 유일한 노드를 dequeue한 뒤 rear도 NULL로 만들어야 하는 이유를 설명하세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “연결 큐 그림에서 갱신 코드 만들기”예요. 첫 노드를 넣을 때는 기존 rear가 없으므로 rear-&gt;link에 접근하지 않아요. front부터 N으로 정한 뒤 공통으로 rear=N을 실행해요. 삭제는 값을 보관하고 front를 이동한 다음 old를 해제해요. front가 NULL이면 마지막 노드였으므로 rear도 NULL로 바꿔 해제된 주소가 남지 않게 해요.

#### 종이에 적을 첫 줄

빈 경우 front=rear=NULL을 먼저 그려요.

#### 왜 이렇게 푸는지 함께 따라가요

1. 첫 노드를 넣을 때는 기존 rear가 없으므로 rear-&gt;link에 접근하지 않아요. front부터 N으로 정한 뒤 공통으로 rear=N을 실행해요.
2. 기존 노드가 있으면 rear-&gt;link=N으로 이어 주고 rear=N으로 옮겨요.
3. 삭제는 값을 보관하고 front를 이동한 다음 old를 해제해요. front가 NULL이면 마지막 노드였으므로 rear도 NULL로 바꿔 해제된 주소가 남지 않게 해요.

enqueue: if(front==NULL) front=N; else rear-&gt;link=N; rear=N;. dequeue는 old=front; item=old-&gt;data; front=old-&gt;link; if(front==NULL) rear=NULL; free(old);. 빈 큐는 양 끝이 모두 NULL이어야 한다.

#### 완성 답과 검산

enqueue: if(front==NULL) front=N; else rear-&gt;link=N; rear=N;. dequeue는 old=front; item=old-&gt;data; front=old-&gt;link; if(front==NULL) rear=NULL; free(old);. 빈 큐는 양 끝이 모두 NULL이어야 한다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. 삭제는 값을 보관하고 front를 이동한 다음 old를 해제해요. front가 NULL이면 마지막 노드였으므로 rear도 NULL로 바꿔 해제된 주소가 남지 않게 해요.

#### 이 문제에서 조심할 점

이 카드는 슬라이드의 연결 그림으로부터 코드를 작성하는 자체 출제예요. 원문에 없던 C 코드를 원문이라고 제시하지 않아요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

빈 경우 front=rear=NULL을 먼저 그려요.

#### 떠올릴 개념·공식

첫 노드를 넣을 때는 기존 rear가 없으므로 rear-&gt;link에 접근하지 않아요. front부터 N으로 정한 뒤 공통으로 rear=N을 실행해요.

#### 검산

enqueue: if(front==NULL) front=N; else rear-&gt;link=N; rear=N;. dequeue는 old=front; item=old-&gt;data; front=old-&gt;link; if(front==NULL) rear=NULL; free(old);. 빈 큐는 양 끝이 모두 NULL이어야 한다.

---

<a id="p5"></a>

### P5. 시뮬레이션의 if/else가 만드는 한 틱

lecture-s06-p22-simulation · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p5)

**강의 예제 기반 자체 출제** S6 p22

강의 루프의 일부예요. clock=1에서 처리 직전 service_time=1이고 B가 방금 도착해 기다려요. clock=2,3에는 새 도착이 없고 B의 서비스 시간은 2예요. remove_customer는 큐가 비면 0을 반환하고 꺼낼 때 대기시간을 기록한다고 가정해요. clock=1,2,3에서 service_time이 어떻게 바뀌고 B는 언제 시작하나요? else를 별도의 if(service_time==0)로 바꾸면 어떤 차이가 생기나요?

`if(is_customer_arrived()) insert_customer(clock);
if(service_time>0) service_time--;
else service_time=remove_customer();`

<details><summary>강의 예제 보기</summary>

S6 p22 · Software_6_Queue.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`if(is_customer_arrived()) insert_customer(clock);
if(service_time>0) service_time--;
else service_time=remove_customer();`

</details>

#### 문제를 내 말로 읽어요

강의 루프의 일부예요. clock=1에서 처리 직전 service_time=1이고 B가 방금 도착해 기다려요. clock=2,3에는 새 도착이 없고 B의 서비스 시간은 2예요. remove_customer는 큐가 비면 0을 반환하고 꺼낼 때 대기시간을 기록한다고 가정해요. clock=1,2,3에서 service_time이 어떻게 바뀌고 B는 언제 시작하나요? else를 별도의 if(service_time==0)로 바꾸면 어떤 차이가 생기나요?

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “시뮬레이션의 if/else가 만드는 한 틱”예요. if 조건은 해당 분기로 들어갈 때 평가해요. 1을 0으로 줄였더라도 그 if에 연결된 else가 뒤이어 실행되지는 않아요. clock=3에서는 2를 1로 줄이기만 해요. 별도 if로 쓰면 같은 틱 안에 두 번째 조건을 새로 평가하므로 이벤트 순서가 달라져요.

#### 종이에 적을 첫 줄

clock=1의 시작 상태 service_time=1을 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

1. if 조건은 해당 분기로 들어갈 때 평가해요. 1을 0으로 줄였더라도 그 if에 연결된 else가 뒤이어 실행되지는 않아요.
2. 다음 틱 clock=2에서 처음부터 service_time=0이므로 B를 꺼내요. 시작 시각-도착 시각=1이 대기시간이에요.
3. clock=3에서는 2를 1로 줄이기만 해요. 별도 if로 쓰면 같은 틱 안에 두 번째 조건을 새로 평가하므로 이벤트 순서가 달라져요.

clock1:1→0, 같은 틱에 else는 실행하지 않음. clock2:0→2이며 B 시작, 대기 2-1=1. clock3:2→1. else를 별도 if(service_time==0)로 바꾸면 clock1에 B를 바로 시작시켜 대기시간이 0이 된다.

#### 완성 답과 검산

clock1:1→0, 같은 틱에 else는 실행하지 않음. clock2:0→2이며 B 시작, 대기 2-1=1. clock3:2→1. else를 별도 if(service_time==0)로 바꾸면 clock1에 B를 바로 시작시켜 대기시간이 0이 된다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. clock=3에서는 2를 1로 줄이기만 해요. 별도 if로 쓰면 같은 틱 안에 두 번째 조건을 새로 평가하므로 이벤트 순서가 달라져요.

#### 이 문제에서 조심할 점

강의 문장 설명과 실제 if/else 순서를 구별하세요. 서비스가 0이 된 직후 즉시 다음 고객을 꺼내는 코드가 아니에요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

clock=1의 시작 상태 service_time=1을 적어요.

#### 떠올릴 개념·공식

if 조건은 해당 분기로 들어갈 때 평가해요. 1을 0으로 줄였더라도 그 if에 연결된 else가 뒤이어 실행되지는 않아요.

#### 검산

clock1:1→0, 같은 틱에 else는 실행하지 않음. clock2:0→2이며 B 시작, 대기 2-1=1. clock3:2→1. else를 별도 if(service_time==0)로 바꾸면 clock1에 B를 바로 시작시켜 대기시간이 0이 된다.

---

<a id="p6"></a>

### P6. 원형 큐의 인덱스를 먼저 옮기기

lecture-s06-p9-circular-queue · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p6)

**강의 예제 기반 자체 출제** S6 p9

크기 M=5, front=3,rear=1이며 유효 원소는 queue[4]=A,queue[0]=B,queue[1]=C예요. dequeue,enqueue(D),enqueue(E)의 반환값·front·rear·논리적 원소를 순서대로 쓰고 마지막 포화 여부를 판단하세요. 배열의 유효 용량과 포화식을 설명하세요.

`/* enqueue의 정상 경로 */
q->rear=(q->rear+1)%MAX_QUEUE_SIZE;
q->queue[q->rear]=item;
/* dequeue의 정상 경로 */
q->front=(q->front+1)%MAX_QUEUE_SIZE;
return q->queue[q->front];`

<details><summary>강의 예제 보기</summary>

S6 p9 · Software_6_Queue.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`/* enqueue의 정상 경로 */
q->rear=(q->rear+1)%MAX_QUEUE_SIZE;
q->queue[q->rear]=item;
/* dequeue의 정상 경로 */
q->front=(q->front+1)%MAX_QUEUE_SIZE;
return q->queue[q->front];`

</details>

#### 문제를 내 말로 읽어요

크기 M=5, front=3,rear=1이며 유효 원소는 queue[4]=A,queue[0]=B,queue[1]=C예요. dequeue,enqueue(D),enqueue(E)의 반환값·front·rear·논리적 원소를 순서대로 쓰고 마지막 포화 여부를 판단하세요. 배열의 유효 용량과 포화식을 설명하세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “원형 큐의 인덱스를 먼저 옮기기”예요. front는 첫 원소 바로 앞자리예요. 먼저 (3+1)%5=4로 옮기고 A를 꺼내요. 마지막 rear의 다음 자리는 4로 front와 같아요. 한 칸을 비워 공백 front==rear와 포화를 구별해요.

#### 종이에 적을 첫 줄

dequeue에서 front=(3+1)%5=4부터 계산해요.

#### 왜 이렇게 푸는지 함께 따라가요

1. front는 첫 원소 바로 앞자리예요. 먼저 (3+1)%5=4로 옮기고 A를 꺼내요.
2. rear는 마지막 원소 자리예요. 1에서 2로 옮겨 D를 저장하고 3으로 옮겨 E를 저장해요.
3. 마지막 rear의 다음 자리는 4로 front와 같아요. 한 칸을 비워 공백 front==rear와 포화를 구별해요.

dequeue: A, front=4,rear=1, [B,C]. enqueue(D): front=4,rear=2,[B,C,D]. enqueue(E): front=4,rear=3,[B,C,D,E], 포화. 유효 용량 M-1=4, (rear+1)%M==front가 포화식이다.

#### 완성 답과 검산

dequeue: A, front=4,rear=1, [B,C]. enqueue(D): front=4,rear=2,[B,C,D]. enqueue(E): front=4,rear=3,[B,C,D,E], 포화. 유효 용량 M-1=4, (rear+1)%M==front가 포화식이다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. 마지막 rear의 다음 자리는 4로 front와 같아요. 한 칸을 비워 공백 front==rear와 포화를 구별해요.

#### 이 문제에서 조심할 점

front 자리의 값을 먼저 반환하면 이미 삭제한 자리나 빈자리를 읽어요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

dequeue에서 front=(3+1)%5=4부터 계산해요.

#### 떠올릴 개념·공식

front는 첫 원소 바로 앞자리예요. 먼저 (3+1)%5=4로 옮기고 A를 꺼내요.

#### 검산

dequeue: A, front=4,rear=1, [B,C]. enqueue(D): front=4,rear=2,[B,C,D]. enqueue(E): front=4,rear=3,[B,C,D,E], 포화. 유효 용량 M-1=4, (rear+1)%M==front가 포화식이다.

---

<a id="p7"></a>

### P7. 덱의 첫 삽입과 양 끝 포인터

lecture-s06-p16-deque-add · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p7)

**강의 예제 기반 자체 출제** S6 p16

create_node(left,item,right)는 새 노드의 llink,data,rlink를 각각 설정하며 할당 실패는 종료한다고 가정해요. 빈 덱 head=tail=NULL에 A를 넣고 이어 B를 넣은 뒤 모든 포인터를 쓰세요. 비어 있을 때 head도 바꾸는 이유와 create_node의 세 필드 대입문을 쓰세요.

`void add_rear(DequeType *dq,element item)
{
    DlistNode *new_node=create_node(dq->tail,item,NULL);
    if(is_empty(dq)) dq->head=new_node;
    else dq->tail->rlink=new_node;
    dq->tail=new_node;
}`

<details><summary>강의 예제 보기</summary>

S6 p16 · Software_6_Queue.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`void add_rear(DequeType *dq,element item)
{
    DlistNode *new_node=create_node(dq->tail,item,NULL);
    if(is_empty(dq)) dq->head=new_node;
    else dq->tail->rlink=new_node;
    dq->tail=new_node;
}`

</details>

#### 문제를 내 말로 읽어요

create_node(left,item,right)는 새 노드의 llink,data,rlink를 각각 설정하며 할당 실패는 종료한다고 가정해요. 빈 덱 head=tail=NULL에 A를 넣고 이어 B를 넣은 뒤 모든 포인터를 쓰세요. 비어 있을 때 head도 바꾸는 이유와 create_node의 세 필드 대입문을 쓰세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “덱의 첫 삽입과 양 끝 포인터”예요. 빈 덱에서는 새 노드가 첫 노드이자 마지막 노드예요. create_node(NULL,A,NULL)가 양 끝 NULL을 만들어요. 할당과 필드 초기화는 create_node의 책임이고 덱 전체의 head,tail 연결은 add_rear의 책임이에요. 두 책임을 합쳐 검산해요.

#### 종이에 적을 첫 줄

첫 노드 A=create_node(NULL,A,NULL)에서 시작해요.

#### 왜 이렇게 푸는지 함께 따라가요

1. 빈 덱에서는 새 노드가 첫 노드이자 마지막 노드예요. create_node(NULL,A,NULL)가 양 끝 NULL을 만들어요.
2. B를 넣을 때 create_node(A,B,NULL)이 B의 왼쪽을 A로 설정해요. 기존 tail=A의 오른쪽을 B로 연결하고 tail을 B로 옮겨요.
3. 할당과 필드 초기화는 create_node의 책임이고 덱 전체의 head,tail 연결은 add_rear의 책임이에요. 두 책임을 합쳐 검산해요.

첫 삽입 head=tail=A,A.llink=A.rlink=NULL. 두 번째 head=A,tail=B,A.rlink=B,B.llink=A,A.llink=B.rlink=NULL. create_node는 node-&gt;llink=left; node-&gt;data=item; node-&gt;rlink=right;. 빈 덱에서 head를 설정하지 않으면 첫 노드에 접근할 수 없다.

#### 완성 답과 검산

첫 삽입 head=tail=A,A.llink=A.rlink=NULL. 두 번째 head=A,tail=B,A.rlink=B,B.llink=A,A.llink=B.rlink=NULL. create_node는 node-&gt;llink=left; node-&gt;data=item; node-&gt;rlink=right;. 빈 덱에서 head를 설정하지 않으면 첫 노드에 접근할 수 없다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. 할당과 필드 초기화는 create_node의 책임이고 덱 전체의 head,tail 연결은 add_rear의 책임이에요. 두 책임을 합쳐 검산해요.

#### 이 문제에서 조심할 점

tail만 새 노드로 옮기면 이전 노드에서 새 노드로 가는 연결이 생기지 않아요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

첫 노드 A=create_node(NULL,A,NULL)에서 시작해요.

#### 떠올릴 개념·공식

빈 덱에서는 새 노드가 첫 노드이자 마지막 노드예요. create_node(NULL,A,NULL)가 양 끝 NULL을 만들어요.

#### 검산

첫 삽입 head=tail=A,A.llink=A.rlink=NULL. 두 번째 head=A,tail=B,A.rlink=B,B.llink=A,A.llink=B.rlink=NULL. create_node는 node-&gt;llink=left; node-&gt;data=item; node-&gt;rlink=right;. 빈 덱에서 head를 설정하지 않으면 첫 노드에 접근할 수 없다.

---

<a id="p8"></a>

### P8. 덱에서 마지막 원소를 삭제할 때

lecture-s06-p17-deque-delete · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p8)

**강의 예제 기반 자체 출제** S6 p17

error는 종료해요. A↔B인 덱에서 delete_front를 두 번 실행한 뒤 반환값과 head,tail 상태를 쓰세요. 마지막 if/else 두 분기가 각각 지키는 불변식과 이 검사를 생략했을 때의 문제를 설명하세요.

`element delete_front(DequeType *dq)
{
    element item; DlistNode *removed_node;
    if(is_empty(dq)) error("공백 덱에서 삭제");
    else {
        removed_node=dq->head;
        item=removed_node->data;
        dq->head=dq->head->rlink;
        free(removed_node);
        if(dq->head==NULL) dq->tail=NULL;
        else dq->head->llink=NULL;
    }
    return item;
}`

<details><summary>강의 예제 보기</summary>

S6 p17 · Software_6_Queue.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`element delete_front(DequeType *dq)
{
    element item; DlistNode *removed_node;
    if(is_empty(dq)) error("공백 덱에서 삭제");
    else {
        removed_node=dq->head;
        item=removed_node->data;
        dq->head=dq->head->rlink;
        free(removed_node);
        if(dq->head==NULL) dq->tail=NULL;
        else dq->head->llink=NULL;
    }
    return item;
}`

</details>

#### 문제를 내 말로 읽어요

error는 종료해요. A↔B인 덱에서 delete_front를 두 번 실행한 뒤 반환값과 head,tail 상태를 쓰세요. 마지막 if/else 두 분기가 각각 지키는 불변식과 이 검사를 생략했을 때의 문제를 설명하세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “덱에서 마지막 원소를 삭제할 때”예요. A의 값을 item에 보관한 다음 head를 B로 옮기고 A를 해제해요. B가 있으므로 B의 왼쪽을 NULL로 끊어요. free 전에 값을 저장했으므로 반환은 유효해요. 남아 있는 포인터가 해제된 노드를 가리키지 않는지도 함께 검사해야 해요.

#### 종이에 적을 첫 줄

removed_node=A,item=A의 값을 먼저 보관해요.

#### 왜 이렇게 푸는지 함께 따라가요

1. A의 값을 item에 보관한 다음 head를 B로 옮기고 A를 해제해요. B가 있으므로 B의 왼쪽을 NULL로 끊어요.
2. 두 번째는 B의 오른쪽이 NULL이어서 head=NULL이 돼요. 이때 tail도 NULL로 만들어 빈 상태를 일치시켜요.
3. free 전에 값을 저장했으므로 반환은 유효해요. 남아 있는 포인터가 해제된 노드를 가리키지 않는지도 함께 검사해야 해요.

첫 반환 A, head=tail=B,B.llink=NULL. 두 번째 반환 B, head=tail=NULL. 빈 덱의 양 끝은 모두 NULL이고 비어 있지 않은 덱의 head.llink는 NULL이다. 생략하면 tail이 해제된 노드를 가리키거나 새 head의 왼쪽이 해제된 노드를 가리킨다.

#### 완성 답과 검산

첫 반환 A, head=tail=B,B.llink=NULL. 두 번째 반환 B, head=tail=NULL. 빈 덱의 양 끝은 모두 NULL이고 비어 있지 않은 덱의 head.llink는 NULL이다. 생략하면 tail이 해제된 노드를 가리키거나 새 head의 왼쪽이 해제된 노드를 가리킨다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. free 전에 값을 저장했으므로 반환은 유효해요. 남아 있는 포인터가 해제된 노드를 가리키지 않는지도 함께 검사해야 해요.

#### 이 문제에서 조심할 점

head=NULL인 경우 head-&gt;llink=NULL을 실행하면 NULL 역참조예요. 빈 경우와 남은 경우를 나눠야 해요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

removed_node=A,item=A의 값을 먼저 보관해요.

#### 떠올릴 개념·공식

A의 값을 item에 보관한 다음 head를 B로 옮기고 A를 해제해요. B가 있으므로 B의 왼쪽을 NULL로 끊어요.

#### 검산

첫 반환 A, head=tail=B,B.llink=NULL. 두 번째 반환 B, head=tail=NULL. 빈 덱의 양 끝은 모두 NULL이고 비어 있지 않은 덱의 head.llink는 NULL이다. 생략하면 tail이 해제된 노드를 가리키거나 새 head의 왼쪽이 해제된 노드를 가리킨다.

---

<a id="p9"></a>

### P9. 원형 큐의 front와 rear

2019-mid-q7 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p9)

강의 규약: front는 첫 원소 직전, rear는 마지막 원소 인덱스이며 한 칸을 비워요. 삭제한 칸의 잔여 값은 현재 큐 원소로 세지 않아요.

크기가 8인 원형 큐에서 front와 rear가 0이에요. 10, 20, 30, 04, 50, 60을 차례로 넣고 4개를 삭제해요. 이어서 70, 80, 90, 100을 넣으면 front와 rear는 각각 얼마인가요?

<details><summary>기출 원문 보기</summary>

2019 중간 7번 · 4점 · 출제자 미상

“배열로 구현된 크기가 8인 원형 큐 (circular queue)에서 front와 rear가 모두 0으로 초기화되었다.<br>그 다음에 10, 20, 30, 04, 50, 60을 원형 큐에 추가하고 그 다음에 4개의 항목을 삭제하고<br>다시 원형 큐에 70, 80, 90, 100을 추가하였을 때 front의 값은 ( ) 이고 rear의 값은 ( ) 이다. (4점)”

</details>

#### 문제를 먼저 읽어요

여덟 칸짜리 원형 줄에서 처음 앞·뒤 표시가 0이에요. 여섯 값을 넣고 넷을 빼고 다시 넷을 넣은 뒤 두 표시의 위치를 구해요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

“원형 큐”, “크기 8”, “front와 rear”가 단서예요. 이 강의의 원형 큐(circular queue)는 `front`가 첫 원소 **하나 앞**, `rear`가 마지막 원소를 가리켜요. 삽입(enqueue)은 rear만 한 칸 옮기고 저장하고, 삭제(dequeue)는 front만 한 칸 옮긴 뒤 그 칸의 값을 읽어요.

배열 인덱스는 0부터 7까지라 다음 칸은 `(현재 인덱스 + 1) % 8`이에요. 포화 조건 `(rear + 1) % 8 == front`를 확인해야 해요. 한 칸을 비워 실제 용량은 7개예요. 이 문제의 최대 점유는 6개라 모든 삽입이 가능해요. 값 `04`는 원문 그대로 보관하고, 인덱스 계산에는 값의 크기를 쓰지 않아요.

#### 첫 줄을 이렇게 써요

종이에 `크기 8, front=0, rear=0`을 적고, 첫 삽입을 `rear=(0+1)%8=1, 1번 칸=10`으로 시작해요.

#### 왜 이렇게 푸는지 함께 따라가요

넣을 때는 rear만, 뺄 때는 front만 움직여요. 아래 표에서 ·는 현재 큐에 속하지 않는 칸이에요.

| 연산 | front | rear | 0–7번 칸 |
|---|---|---|---|
| 넣기 10 | 0 | 1 | ·, 10, ·, ·, ·, ·, ·, · |
| 넣기 20 | 0 | 2 | ·, 10, 20, ·, ·, ·, ·, · |
| 넣기 30 | 0 | 3 | ·, 10, 20, 30, ·, ·, ·, · |
| 넣기 04 | 0 | 4 | ·, 10, 20, 30, 04, ·, ·, · |
| 넣기 50 | 0 | 5 | ·, 10, 20, 30, 04, 50, ·, · |
| 넣기 60 | 0 | 6 | ·, 10, 20, 30, 04, 50, 60, · |
| 삭제 10 | 1 | 6 | ·, ·, 20, 30, 04, 50, 60, · |
| 삭제 20 | 2 | 6 | ·, ·, ·, 30, 04, 50, 60, · |
| 삭제 30 | 3 | 6 | ·, ·, ·, ·, 04, 50, 60, · |
| 삭제 04 | 4 | 6 | ·, ·, ·, ·, ·, 50, 60, · |
| 넣기 70 | 4 | 7 | ·, ·, ·, ·, ·, 50, 60, 70 |
| 넣기 80 | 4 | 0 | 80, ·, ·, ·, ·, 50, 60, 70 |
| 넣기 90 | 4 | 1 | 80, 90, ·, ·, ·, 50, 60, 70 |
| 넣기 100 | 4 | 2 | 80, 90, 100, ·, ·, 50, 60, 70 |

삭제 네 번 뒤 front는 4예요. 마지막 네 삽입에서 rear는 6에서 7, 0, 1, 2로 돌아와요. 따라서 **front=4, rear=2**예요.

#### 완성 답과 검산

정답은 **front=4, rear=2**예요. 독립 계산으로 front는 삭제 횟수만큼 `(0+4)%8=4`, rear는 총 삽입 10회만큼 `(0+10)%8=2`예요. 현재 원소는 6개이고 `(2-4+8)%8=6`도 맞아요. 큐 순서는 50, 60, 70, 80, 90, 100이에요.

#### 여기서 실수하기 쉬워요

`04`를 임의로 `40`으로 고치지 않아요. 값의 표기는 인덱스 답에 영향을 주지 않아요. 7번 칸 다음 rear는 8이 아니라 0이에요.

#### 설명을 닫고 다시 해 봐요

1. 각 삽입·삭제가 어느 포인터를 움직이는지 적어요.
2. 7 다음에 0으로 돌아가는 지점을 표시해요.
3. 마지막 요소 수를 별도로 세어 검산해요.

**페이지 요약**

#### 떠올릴 개념·공식

원형 큐: 다음 인덱스=(현재+1)%8, front는 첫 원소 하나 앞이에요.

#### 첫 줄

front=rear=0에서 첫 삽입의 rear를 1로 옮겨요.

#### 핵심 판단

삭제 4회와 삽입 10회를 각각 세어 front=4, rear=2예요.

#### 검산

(rear-front+8)%8=6이며 실제 남은 값도 6개예요.

---

<a id="p10"></a>

### P10. 원형 큐 상태 두 번 그리기

2017-mid-c050-q7 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p10)

강의 규약: front는 첫 원소 직전, rear는 마지막 원소 인덱스이며 한 칸을 비워요. 삭제한 칸의 잔여 값은 현재 큐 원소로 세지 않아요.

크기가 8인 원형 큐에서 front와 rear가 모두 0이에요. 다음 상태를 각각 그려 보세요. front와 rear도 표시해요.

- (a) 10, 20, 30, 40, 50을 넣고 세 항목을 삭제해요.
- (b) (a)의 상태에 60, 70, 80, 90을 넣어요.

그림을 그릴 0–7번 칸이에요.

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

<details><summary>기출 원문 보기</summary>

2017 중간 7번 · 10점 · 출제자 미상

“7. 크기가 8인 원형 큐(circular queue)에서 front와 rear가 모두 0으로 초기화되었다고 가정하고 다음 각 물음에 답하라. [10 points]<br>(a) 10, 20, 30, 40, 50을 큐에 넣었다가 세 개의 항목을 삭제하였다고 가정하고, 그 때의 큐의 모양을 그려라. front와 rear도 표시하시오. [5 points]<br>(b) (a)의 결과 상태의 큐에 60, 70, 80, 90을 추가로 넣은 후의 큐의 모양을 그려라. front와 rear도 표시하라. [5 points]”

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

</details>

#### 문제를 먼저 읽어요

먼저 다섯 값을 줄에 넣고 세 값을 빼요. 그 모습을 그린 뒤, 그 자리에서 네 값을 더 넣고 다시 그려요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

“크기 8의 원형 큐”, “큐의 모양”, “front와 rear 표시”가 단서예요. 원형 큐(circular queue)에서 `front`는 첫 원소 하나 앞, `rear`는 마지막 원소의 칸이에요. 삽입(enqueue)은 `rear=(rear+1)%8` 뒤 저장하고, 삭제(dequeue)는 `front=(front+1)%8` 뒤 읽어요.

그림의 0–7번 칸에 현재 남은 값만 적어요. 빈칸의 오래된 값은 지워 표시해요. 한 칸을 비우는 구현이라 최대 7개이고, (b)의 마지막 점유는 6개라 포화되지 않아요. (b)는 (a) 결과에서 계속해야 해요.

#### 첫 줄을 이렇게 써요

(a)의 첫 행을 `front=0, rear=0, 모든 칸 비어 있음`으로 적고, `10 삽입 → rear=1, 1번 칸=10`을 채워요. (b)의 첫 행은 (a)의 최종 `front=3, rear=5`에서 시작해요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) 다섯 번 삽입할 때 rear만 1부터 5까지 이동해요. 세 번 삭제할 때 front만 1부터 3까지 이동하며 10, 20, 30이 나가요.

| 연산 | front | rear |
|---|---|---|
| 넣기 10 | 0 | 1 |
| 넣기 20 | 0 | 2 |
| 넣기 30 | 0 | 3 |
| 넣기 40 | 0 | 4 |
| 넣기 50 | 0 | 5 |
| 삭제 10 | 1 | 5 |
| 삭제 20 | 2 | 5 |
| 삭제 30 | 3 | 5 |

최종 4번 칸=40, 5번 칸=50이고 다른 칸은 비어요. **front=3, rear=5**예요.

| 칸 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| 값 | · | · | · | · | 40 | 50 | · | · |
| 표시 | — | — | — | front | — | rear | — | — |

(b) (a)의 상태를 유지해요. 삽입할 때 rear가 6, 7, 0, 1로 순환해요.

| 연산 | front | rear |
|---|---|---|
| 넣기 60 | 3 | 6 |
| 넣기 70 | 3 | 7 |
| 넣기 80 | 3 | 0 |
| 넣기 90 | 3 | 1 |

최종 4번=40, 5번=50, 6번=60, 7번=70, 0번=80, 1번=90이에요. **front=3, rear=1**이에요.

| 칸 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| 값 | 80 | 90 | · | · | 40 | 50 | 60 | 70 |
| 표시 | — | rear | — | front | — | — | — | — |

#### 완성 답과 검산

(a) **front=3, rear=5**, 남은 순서는 40, 50이에요. 독립적으로 점유 수를 계산하면 `(5-3+8)%8=2`로 그림의 두 값과 맞아요. 원 기출 PDF 1쪽 그림도 3번에 front, 5번에 rear를 표시해요.

(b) **front=3, rear=1**, 큐 순서는 40, 50, 60, 70, 80, 90이에요. `(1-3+8)%8=6`으로 여섯 칸과 맞고, 7번 다음에 0번으로 순환했어요. 원 기출 PDF 2쪽 그림의 위치와 같아요.

#### 여기서 실수하기 쉬워요

(b)를 빈 큐에서 다시 시작하면 front가 틀려요. 삭제된 값이 물리적 메모리에 남아 있더라도 현재 큐의 칸으로 그리지 않아요. front가 40이 있는 4번이 아니라 그 앞 3번이라는 점도 확인해요.

#### 설명을 닫고 다시 해 봐요

1. (a)의 모든 연산에서 front·rear를 갱신해요.
2. (a)의 8칸 그림을 완성한 뒤 그대로 (b)를 시작해요.
3. 두 그림의 원소 수를 인덱스 차이로 검산해요.

**페이지 요약**

#### 떠올릴 개념·공식

원형 큐: front는 첫 원소 하나 앞, rear는 마지막 칸이에요.

#### 첫 줄

(a) front=rear=0에서 rear를 1로 옮기고 10을 넣어요.

#### 핵심 판단

(a) front=3, rear=5; 이어서 (b) front=3, rear=1이에요.

#### 검산

(a)는 2개, (b)는 6개가 남아 각각 인덱스 차이와 같아요.

---

원 문제·정리노트·PDF는 보존해요.
