# 자료구조및알고리즘이해 복습 1015 문제설명

왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.

문제의 첫 줄부터 검산까지 설명해요.

**목차**

- [문항별 설명](#problems)
  - [P1. 원형 큐의 get_count](#p1)
  - [P2. 두 스택으로 큐 만들기](#p2)
  - [P3. 덱으로 회문 검사하기](#p3)
  - [P4. 연결 큐 의사코드를 대입문으로 옮기기](#p4)
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

### P4. 연결 큐 의사코드를 대입문으로 옮기기

lecture-s06-p11-linked-queue · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p4)

**강의 예제 기반 자체 출제** S6 p11

단순 연결 큐의 노드는 `data`, `link` 필드를 가지며 공백 큐 상태는 `front = rear = NULL`이에요. 아래 의사코드를 C 포인터 대입문으로 옮겨 보세요.

`/* 대입문으로 옮길 연산의 의사코드 */
enqueue: 새 노드 N(이미 할당되어 N->link = NULL)을 rear 뒤에 연결하고 rear를 갱신
dequeue: front 노드(old)의 값을 보관하고 front를 다음으로 이동한 뒤 old를 해제`

#### 구할 것

- (a) 이미 할당·초기화되어 `N->link = NULL`인 새 노드 `N`을 삽입할 때, 공백 큐(`front == NULL`)인 경우와 비공백 큐인 경우를 처리하는 `enqueue`의 포인터 대입문을 쓰세요.
- (b) 비어 있지 않은 큐에서 첫 노드 `old = front`를 꺼내는 `dequeue`의 대입문을 쓰고, 노드가 하나뿐이어서 삭제 후 `front == NULL`이 되었을 때 `rear = NULL`까지 함께 갱신해야 하는 이유를 설명하세요.

<details><summary>강의 예제 보기</summary>

S6 p11 · Software_6_Queue.pdf. 강의 연결 그림의 동작을 요약한 자체 의사코드이며 강의 원문 C 코드는 아닙니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`/* 강의 연결 큐 그림을 바탕으로 작성할 의사코드 */
enqueue: 새 노드를 rear 뒤에 연결하고 rear를 갱신
dequeue: front 노드의 값을 보관하고 front를 다음으로 이동`

</details>

#### 문제를 내 말로 읽어요

단순 연결 큐의 `enqueue`와 `dequeue` 의사코드를 공백·단일 노드 경계 조건에 주의하며 C 포인터 대입문으로 옮기는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “연결 큐 의사코드를 대입문으로 옮기기”예요. 첫 노드를 넣을 때는 기존 `rear`가 없으므로 `front = N`으로 두고, 마지막 노드를 꺼내 `front == NULL`이 되면 `rear = NULL`까지 함께 초기화해야 해요.

#### 종이에 적을 첫 줄

공백 큐 조건 `front == NULL`(양 끝 모두 `NULL`)을 먼저 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `enqueue`에서 큐가 비어 있으면(`front == NULL`) `front = N;`으로 첫 노드를 가리키게 하고, 비어 있지 않으면 `rear->link = N;`으로 기존 꼬리 뒤에 연결한 뒤, 두 경우 모두 `rear = N;`으로 꼬리 포인터를 갱신해요.

(b) `dequeue`에서는 `old = front; item = old->data; front = old->link;`로 값을 꺼내고 머리를 옮긴 뒤, 만약 `front == NULL`이면 마지막 노드가 삭제된 것이므로 `rear = NULL;`로 함께 비워 주고 `free(old);`를 호출해요. 그렇지 않으면 `rear`가 해제된 노드를 가리키게 돼요.

#### 완성 답과 검산

(a) 빈 큐에 `N` 하나를 `enqueue`하면 `front = rear = N`, `N->link = NULL`이 되어 단일 노드 큐 불변식이 성립해요.

(b) 그 유일한 노드 `N`을 `dequeue`하면 `front = N->link = NULL`이 되고 `if (front == NULL) rear = NULL;`에 의해 초기 공백 상태 `front = rear = NULL`로 정확히 돌아와요.

#### 이 문제에서 조심할 점

의사코드의 각 단계를 빠짐없이 대입문으로 옮기세요. 빈 큐와 노드가 하나뿐인 경우를 따로 확인해요.

#### 설명을 닫고 다시 해 봐요

1. `front == NULL`일 때와 아닐 때 `enqueue`의 대입문을 각각 적어요.
2. `dequeue`에서 노드 해제 전후로 수행할 포인터 갱신문을 순서대로 적어요.
3. `front == NULL`일 때 `rear = NULL`을 생략하면 남는 문제를 확인해요.

**페이지 요약**

#### 첫 줄

공백 큐 조건 `front == NULL`(양 끝 모두 `NULL`)을 먼저 적어요.

#### 떠올릴 개념·공식

빈 큐 삽입은 `front = rear = N`, 마지막 노드 삭제 후에는 `front = rear = NULL`로 맞춰요.

#### 검산

(a) `if (front == NULL) front = N; else rear->link = N; rear = N;` (b) `old = front; item = old->data; front = old->link; if (front == NULL) rear = NULL; free(old);`

---

<a id="p5"></a>

### P5. 시뮬레이션의 if/else가 만드는 한 틱

lecture-s06-p22-simulation · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p5)

**강의 예제 기반 자체 출제** S6 p22

은행 대기열 시뮬레이션에서 시각 `clock`이 `1`씩 증가할 때마다 실행되는 루프 본문이에요. `clock = 1`에서 아래 코드 실행 직전 `service_time = 1`이고 고객 `B`(서비스 시간 `2`)가 방금 도착하며, `clock = 2, 3`에는 새 고객 도착이 없다고 가정해요(`remove_customer()`는 큐에서 고객을 꺼내 서비스 시간을 반환하고 대기 시간을 기록해요).

`if (is_customer_arrived()) insert_customer(clock);
if (service_time > 0) service_time--;
else service_time = remove_customer();`

#### 구할 것

- (a) `clock = 1, 2, 3` 각 시각에서 위 코드가 실행된 직후 `service_time`의 변화와, 고객 `B`의 서비스 시작 시각 및 대기 시간을 쓰세요.
- (b) 만약 두 번째 문장의 `else`를 떼어 별도의 `if (service_time == 0) service_time = remove_customer();`로 바꾸면, `clock = 1`에서의 동작과 고객 `B`의 대기 시간이 어떻게 달라지는지 설명하세요.

<details><summary>강의 예제 보기</summary>

S6 p22 · Software_6_Queue.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`if(is_customer_arrived()) insert_customer(clock);
if(service_time>0) service_time--;
else service_time=remove_customer();`

</details>

#### 문제를 내 말로 읽어요

은행 대기열 시뮬레이션 루프에서 `if (service_time > 0) ... else ...` 구조 때문에 한 틱에 시간 감소와 새 고객 서비스 시작 중 하나만 실행되는 흐름을 추적하는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “시뮬레이션의 if/else가 만드는 한 틱”예요. `if` 조건이 참이어서 `service_time--`로 `0`이 되었더라도 그 `if`에 묶인 `else`는 같은 틱에 실행되지 않고 다음 틱에 실행돼요.

#### 종이에 적을 첫 줄

`clock = 1` 진입 시점의 상태 `service_time = 1`을 먼저 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `clock = 1`에 고객 `B`가 도착해 큐에 들어가고, 진입 시 `service_time = 1 > 0`이므로 `service_time`이 `1 -> 0`으로 줄며 `else`는 건너뛰어요. `clock = 2`에는 처음부터 `service_time == 0`이므로 `else`가 실행되어 고객 `B`를 꺼내 `service_time = 0 -> 2`가 되고 대기 시간은 `2 - 1 = 1`이 돼요. `clock = 3`에는 `service_time`이 `2 -> 1`로 줄어요.

(b) 만약 `else` 대신 별도의 `if (service_time == 0)`를 쓰면, `clock = 1`에서 `service_time`이 `1 -> 0`이 된 직후 같은 틱에 두 번째 `if` 조건도 참이 되어 고객 `B`가 `clock = 1`에 즉시 시작하고 대기 시간이 `0`이 돼요.

#### 완성 답과 검산

(a) `if/else`는 상호 배타적이므로 `clock = 1`에서는 감소만, `clock = 2`에서는 꺼내기만, `clock = 3`에서는 감소만 일어나요.

(b) 두 개의 독립된 `if`로 분리하면 한 틱 안에서 상태 변경 후 재평가가 일어나 이벤트 시각이 `1`틱 앞당겨짐을 확인할 수 있어요.

#### 이 문제에서 조심할 점

말로 된 설명과 실제 `if/else` 순서를 구별하세요. 서비스가 `0`이 된 직후 같은 틱에 즉시 다음 고객을 꺼내는 코드가 아니에요.

#### 설명을 닫고 다시 해 봐요

1. `clock = 1, 2, 3`마다 분기 진입 전 `service_time`과 실행 후 `service_time`을 적어요.
2. 고객 `B`의 도착 시각과 서비스 시작 시각으로 대기 시간을 계산해요.
3. `else`를 별도 `if (service_time == 0)`로 바꿨을 때 `clock = 1`의 실행 흐름을 비교해요.

**페이지 요약**

#### 첫 줄

`clock = 1` 진입 시점의 상태 `service_time = 1`을 먼저 적어요.

#### 떠올릴 개념·공식

`if/else`는 한 틱에 한 분기만 실행하므로 `1 -> 0` 감소와 새 고객 시작은 서로 다른 틱에 일어나요.

#### 검산

(a) `clock = 1`: `1 -> 0`, `clock = 2`: `0 -> 2`(`B` 시작, 대기 `1`), `clock = 3`: `2 -> 1` (b) 별도 `if` 사용 시 `clock = 1`에 즉시 시작해 대기 `0`

---

<a id="p6"></a>

### P6. 원형 큐의 인덱스를 먼저 옮기기

lecture-s06-p9-circular-queue · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p6)

**강의 예제 기반 자체 출제** S6 p9

배열 크기 `MAX_QUEUE_SIZE = 5`(`M = 5`)인 원형 큐에서 현재 `front = 3, rear = 1`이며 유효 원소는 `queue[4] = A, queue[0] = B, queue[1] = C`예요.

`/* enqueue의 정상 경로 */
q->rear = (q->rear + 1) % MAX_QUEUE_SIZE;
q->queue[q->rear] = item;
/* dequeue의 정상 경로 */
q->front = (q->front + 1) % MAX_QUEUE_SIZE;
return q->queue[q->front];`

#### 구할 것

- (a) 위 상태에서 `dequeue()`, `enqueue(D)`, `enqueue(E)`를 순서대로 실행할 때, 각 연산의 반환값(해당 시), 실행 직후 `(front, rear)`, 큐의 논리적 원소 나열을 쓰고 마지막 상태의 포화 여부를 판정하세요.
- (b) 크기 `M = 5`인 원형 큐에서 한 칸을 비워 둘 때의 최대 저장 가능 원소 수(유효 용량)와 포화 상태 판정식을 쓰세요.

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

크기 `M = 5`인 원형 큐에서 나머지 연산(`% M`)으로 인덱스를 먼저 한 칸 옮긴 뒤 읽거나 쓰는 동작을 추적하고 유효 용량과 포화 조건식을 구하는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “원형 큐의 인덱스를 먼저 옮기기”예요. `front`는 첫 원소 하나 앞을, `rear`는 마지막 원소를 가리키며, 한 칸을 비워 공백(`front == rear`)과 포화(`(rear + 1) % M == front`)를 구별해요.

#### 종이에 적을 첫 줄

첫 연산 `dequeue()`에서 `front = (3 + 1) % 5 = 4`부터 계산해요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `dequeue()`는 `front`를 `4`로 옮겨 `queue[4] = A`를 반환하고 `(front, rear) = (4, 1)`, 원소 `[B, C]`가 남아요. 이어 `enqueue(D)`는 `rear`를 `2`로 옮겨 `(4, 2)`, `[B, C, D]`가 되고, `enqueue(E)`는 `rear`를 `3`으로 옮겨 `(4, 3)`, `[B, C, D, E]`가 되며 `(3 + 1) % 5 == 4 == front`이므로 포화 상태가 돼요.

(b) 크기 `M = 5`인 배열에서 공백과 포화를 구별하기 위해 항상 한 칸을 비워 두므로 유효 용량은 `M - 1 = 4`이고, 포화 판정식은 `(rear + 1) % M == front`예요.

#### 완성 답과 검산

(a) 최종 상태에서 원소는 `queue[0]=B, queue[1]=C, queue[2]=D, queue[3]=E` 총 `4`개이고 `queue[4]`(`front = 4`) 한 칸만 비어 있어 포화 상태와 일치해요.

(b) 만약 `queue[4]`까지 채우면 `rear = 4`가 되어 공백 조건 `front == rear`와 같아지므로 한 칸을 비워 두어야 함을 확인할 수 있어요.

#### 이 문제에서 조심할 점

`front` 자리의 값을 먼저 반환하면 이미 삭제한 자리나 빈자리를 읽어요.

#### 설명을 닫고 다시 해 봐요

1. `dequeue()`, `enqueue(D)`, `enqueue(E)` 실행 직후의 `(front, rear)`와 원소 목록을 차례대로 적어요.
2. 마지막 상태에서 `(rear + 1) % 5`를 계산해 `front`와 비교해요.
3. 유효 용량 `M - 1`과 포화 판정식을 적어요.

**페이지 요약**

#### 첫 줄

첫 연산 `dequeue()`에서 `front = (3 + 1) % 5 = 4`부터 계산해요.

#### 떠올릴 개념·공식

원형 큐는 인덱스를 먼저 `(idx + 1) % M`으로 옮긴 뒤 접근하며, 포화 조건은 `(rear + 1) % M == front`예요.

#### 검산

(a) `dequeue`: `A, (4, 1), [B, C]`; `enqueue(D)`: `(4, 2), [B, C, D]`; `enqueue(E)`: `(4, 3), [B, C, D, E]`, 포화 (b) 유효 용량 `M - 1 = 4`, 포화식 `(rear + 1) % M == front`

---

<a id="p7"></a>

### P7. 덱의 첫 삽입과 양 끝 포인터

lecture-s06-p16-deque-add · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p7)

**강의 예제 기반 자체 출제** S6 p16

이중 연결 리스트로 구현한 덱(deque)에서 `create_node(left, item, right)`는 새 노드의 `llink`, `data`, `rlink`를 각각 설정해 반환해요. 아래는 꼬리에 원소를 넣는 `add_rear` 함수예요.

`void add_rear(DequeType *dq, element item)
{
    DlistNode *new_node = create_node(dq->tail, item, NULL);
    if (is_empty(dq)) dq->head = new_node;
    else dq->tail->rlink = new_node;
    dq->tail = new_node;
}`

#### 구할 것

- (a) 빈 덱(`dq->head = dq->tail = NULL`)에 `add_rear(dq, A)`를 실행한 직후와 이어서 `add_rear(dq, B)`를 실행한 직후, `dq->head`, `dq->tail` 및 각 노드의 `llink`, `rlink` 값을 모두 쓰세요.
- (b) `create_node` 내부에서 새 노드의 세 필드를 초기화하는 대입문을 쓰고, `is_empty(dq)`가 참일 때 `dq->head = new_node;`도 함께 설정해야 하는 이유를 설명하세요.

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

이중 연결 리스트 기반 덱의 빈 상태에서 `add_rear`를 두 번 호출할 때 양 끝 포인터(`head, tail`)와 노드 링크(`llink, rlink`)가 어떻게 연결되는지 추적하는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “덱의 첫 삽입과 양 끝 포인터”예요. 빈 덱에서는 첫 노드가 `head`이자 `tail`이 되며, `create_node(left, item, right)`가 새 노드의 세 필드를 초기화해요.

#### 종이에 적을 첫 줄

첫 삽입의 `create_node(NULL, A, NULL)` 호출부터 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) 빈 덱에 `A`를 넣으면 `create_node(NULL, A, NULL)`로 `A.llink = A.rlink = NULL`이 되고, `is_empty(dq)`가 참이어서 `head = tail = A`가 돼요. 이어서 `B`를 넣으면 `create_node(A, B, NULL)`로 `B.llink = A, B.rlink = NULL`이 되고, `else` 분기로 `A.rlink = B`를 연결한 뒤 `tail = B`가 되어 `head = A, tail = B`가 돼요.

(b) `create_node` 내부 대입문은 `node->llink = left; node->data = item; node->rlink = right;`예요. 공백 덱에서 첫 노드를 넣을 때 `dq->head = new_node;`를 설정하지 않으면 `head`가 계속 `NULL`로 남아 앞쪽에서 첫 노드를 참조할 수 없어요.

#### 완성 답과 검산

(a) 두 번 삽입한 뒤 `head(A)->rlink == B`이고 `tail(B)->llink == A`이며 양 끝 외곽 링크(`A.llink, B.rlink`)는 모두 `NULL`이어서 이중 연결 불변식이 성립해요.

(b) 첫 삽입에서 `head`와 `tail`이 모두 `A`를 가리켜야 이후 `delete_front`나 두 번째 `add_rear`가 정상 동작함을 확인할 수 있어요.

#### 이 문제에서 조심할 점

`tail`만 새 노드로 옮기면 이전 노드에서 새 노드로 가는 오른쪽 연결(`rlink`)이 생기지 않아요.

#### 설명을 닫고 다시 해 봐요

1. 첫 삽입 직후 `head, tail, A.llink, A.rlink`를 적어요.
2. 두 번째 삽입 직후 `head, tail`과 `A, B`의 양쪽 링크를 모두 적어요.
3. `create_node`의 세 필드 대입문과 빈 덱에서 `head`를 갱신하는 이유를 적어요.

**페이지 요약**

#### 첫 줄

첫 삽입의 `create_node(NULL, A, NULL)` 호출부터 적어요.

#### 떠올릴 개념·공식

빈 덱에 첫 원소를 넣을 때는 `head`와 `tail`을 모두 새 노드로 설정하고, 비공백 덱에서는 기존 `tail->rlink`와 새 노드의 `llink`를 상호 연결해요.

#### 검산

(a) 1회: `head = tail = A`; 2회: `head = A, tail = B, A.rlink = B, B.llink = A` (b) `node->llink = left; node->data = item; node->rlink = right;`, 빈 덱 첫 노드 접근 보장

---

<a id="p8"></a>

### P8. 덱에서 마지막 원소를 삭제할 때

lecture-s06-p17-deque-delete · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1015_Queue.html#p8)

**강의 예제 기반 자체 출제** S6 p17

이중 연결 리스트로 구현한 덱에서 맨 앞 노드를 꺼내는 `delete_front` 함수예요.

`element delete_front(DequeType *dq)
{
    element item; DlistNode *removed_node;
    if (is_empty(dq)) error("공백 덱에서 삭제");
    else {
        removed_node = dq->head;
        item = removed_node->data;
        dq->head = dq->head->rlink;
        free(removed_node);
        if (dq->head == NULL) dq->tail = NULL;
        else dq->head->llink = NULL;
    }
    return item;
}`

#### 구할 것

- (a) 두 노드가 `A <-> B`로 연결된 덱(`dq->head = A, dq->tail = B`)에서 `delete_front(dq)`를 연속으로 두 번 호출할 때, 각 호출의 반환값과 호출 직후 `dq->head`, `dq->tail` 및 남은 노드의 링크 상태를 쓰세요.
- (b) 함수 마지막의 `if (dq->head == NULL) dq->tail = NULL; else dq->head->llink = NULL;` 두 분기가 각각 유지하는 불변식과, 이 분기를 생략했을 때 생기는 문제를 설명하세요.

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

`A <-> B` 두 노드가 있는 덱에서 `delete_front`를 두 번 호출할 때 포인터 변화를 추적하고, 삭제 후 남은 노드가 있는지 여부에 따라 갈리는 마지막 `if/else`의 역할을 확인하는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “덱에서 마지막 원소를 삭제할 때”예요. 머리 노드를 지운 뒤 `dq->head == NULL`이면 빈 덱이므로 `dq->tail = NULL`로 맞추고, 노드가 남아 있으면 새 머리의 왼쪽 링크 `dq->head->llink = NULL`로 끊어 줘요.

#### 종이에 적을 첫 줄

첫 호출에서 `removed_node = A, item = A`를 먼저 보관해요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) 첫 호출에서는 `A`를 꺼내고 `dq->head`를 `B`로 옮긴 뒤 `else` 분기로 `B.llink = NULL`로 만들어 `head = tail = B`(`B.llink = B.rlink = NULL`)가 돼요. 두 번째 호출에서는 `B`를 꺼내고 `dq->head = NULL`이 되어 `if` 분기로 `dq->tail = NULL`로 맞추므로 `head = tail = NULL`이 돼요.

(b) 마지막 `if/else`는 공백 덱의 `head = tail = NULL` 불변식과 비공백 덱의 `head->llink = NULL` 불변식을 각각 유지해요. 이를 생략하면 빈 덱의 `tail`이나 남은 첫 노드의 `llink`가 이미 해제된 노드를 가리키는 댕글링 포인터가 돼요.

#### 완성 답과 검산

(a) 첫 호출에서는 `else` 분기가, 두 번째 호출에서는 `if` 분기가 각각 한 번씩 실행되어 두 경계 경우를 모두 거치게 돼요.

(b) 두 번째 호출에서 `if (dq->head == NULL)` 검사 없이 무조건 `dq->head->llink = NULL`을 실행하면 `NULL` 포인터 역참조 오류가 발생함도 확인할 수 있어요.

#### 이 문제에서 조심할 점

`dq->head == NULL`인 경우 `dq->head->llink = NULL`을 실행하면 `NULL` 역참조가 발생하므로 반드시 두 경우를 나눠야 해요.

#### 설명을 닫고 다시 해 봐요

1. 첫 번째 `delete_front` 후 반환값과 `head, tail, B.llink`를 적어요.
2. 두 번째 `delete_front` 후 반환값과 `head, tail`을 적어요.
3. 마지막 `if/else`를 생략했을 때 남는 잘못된 포인터를 설명해요.

**페이지 요약**

#### 첫 줄

첫 호출에서 `removed_node = A, item = A`를 먼저 보관해요.

#### 떠올릴 개념·공식

삭제 후 `dq->head == NULL`이면 `dq->tail = NULL`로, 아니면 `dq->head->llink = NULL`로 갱신해요.

#### 검산

(a) 1회: 반환 `A`, `head = tail = B, B.llink = NULL`; 2회: 반환 `B`, `head = tail = NULL` (b) 양 끝 `NULL` 불변식 유지 및 해제 노드 참조 방지

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
