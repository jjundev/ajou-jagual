# 복습문제 8선 — 1015 수업 범위

다른 기출 2개와 교과서 6개로 복습해요. 먼저 풀어 보고, 막히면 힌트를 열어 보세요.

> `복습문제_1015_Queue.html`를 마크다운으로 옮겼어요. 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [B. 다른 기출](#partB)
  - [P1. 원형 큐의 front와 rear](#p1)
  - [P2. 원형 큐 상태 두 번 그리기](#p2)
- [D. 교과서 연습문제](#partD)
  - [P3. 원형 큐의 요소 수](#p3)
  - [P4. 원형 큐의 공백 조건](#p4)
  - [P5. 큐 연산의 시간 복잡도](#p5)
  - [P6. 원형 큐의 get_count](#p6)
  - [P7. 두 스택으로 큐 만들기](#p7)
  - [P8. 덱으로 회문 검사하기](#p8)

<a id="partB"></a>

## B. 다른 기출

<a id="p1"></a>

### P1. 원형 큐의 front와 rear

크기가 8인 원형 큐에서 front와 rear가 0이에요. 10, 20, 30, 04, 50, 60을 차례로 넣고 4개를 삭제해요. 이어서 70, 80, 90, 100을 넣으면 front와 rear는 각각 얼마인가요?

<details><summary>기출 원문 보기</summary>

2019 중간 7번 · 4점 · 출제자 미상

“배열로 구현된 크기가 8인 원형 큐 (circular queue)에서 front와 rear가 모두 0으로 초기화되었다.<br>그 다음에 10, 20, 30, 04, 50, 60을 원형 큐에 추가하고 그 다음에 4개의 항목을 삭제하고<br>다시 원형 큐에 70, 80, 90, 100을 추가하였을 때 front의 값은 ( ) 이고 rear의 값은 ( ) 이다. (4점)”

</details>

<details><summary>힌트 보기</summary>

넣을 때 rear, 삭제할 때 front를 한 칸 움직여요. 7 다음은 0이에요.

</details>

<details><summary>풀이 보기</summary>

1. | 연산 | front | rear | 0–7번 칸 |
   |---|---|---|---|
   | 넣기(10) | 0 | 1 | [·, 10, ·, ·, ·, ·, ·, ·] |
   | 넣기(20) | 0 | 2 | [·, 10, 20, ·, ·, ·, ·, ·] |
   | 넣기(30) | 0 | 3 | [·, 10, 20, 30, ·, ·, ·, ·] |
   | 넣기(04) | 0 | 4 | [·, 10, 20, 30, 04, ·, ·, ·] |
   | 넣기(50) | 0 | 5 | [·, 10, 20, 30, 04, 50, ·, ·] |
   | 넣기(60) | 0 | 6 | [·, 10, 20, 30, 04, 50, 60, ·] |
   | 삭제 | 1 | 6 | [·, ·, 20, 30, 04, 50, 60, ·] |
   | 삭제 | 2 | 6 | [·, ·, ·, 30, 04, 50, 60, ·] |
   | 삭제 | 3 | 6 | [·, ·, ·, ·, 04, 50, 60, ·] |
   | 삭제 | 4 | 6 | [·, ·, ·, ·, ·, 50, 60, ·] |
   | 넣기(70) | 4 | 7 | [·, ·, ·, ·, ·, 50, 60, 70] |
   | 넣기(80) | 4 | 0 | [80, ·, ·, ·, ·, 50, 60, 70] |
   | 넣기(90) | 4 | 1 | [80, 90, ·, ·, ·, 50, 60, 70] |
   | 넣기(100) | 4 | 2 | [80, 90, 100, ·, ·, 50, 60, 70] |
2. front는 네 번 삭제해 4, rear는 열 번 넣어 2가 돼요.
3. 수업과의 연결: 1015 원형 큐 삽입·삭제에서 인덱스를 나머지 연산으로 순환시켰어요.

**정답:** front=4, rear=2

</details>

---

<a id="p2"></a>

### P2. 원형 큐 상태 두 번 그리기

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

<details><summary>힌트 보기</summary>

front는 첫 요소 바로 앞 칸이에요. 삭제 후 그 칸에 남은 값은 현재 요소가 아니에요.

</details>

<details><summary>풀이 보기</summary>

1. (a)의 모든 연산을 따라가요.

   | 연산 | front | rear | 0–7번 칸 |
   |---|---|---|---|
   | 넣기(10) | 0 | 1 | [·, 10, ·, ·, ·, ·, ·, ·] |
   | 넣기(20) | 0 | 2 | [·, 10, 20, ·, ·, ·, ·, ·] |
   | 넣기(30) | 0 | 3 | [·, 10, 20, 30, ·, ·, ·, ·] |
   | 넣기(40) | 0 | 4 | [·, 10, 20, 30, 40, ·, ·, ·] |
   | 넣기(50) | 0 | 5 | [·, 10, 20, 30, 40, 50, ·, ·] |
   | 삭제 | 1 | 5 | [·, ·, 20, 30, 40, 50, ·, ·] |
   | 삭제 | 2 | 5 | [·, ·, ·, 30, 40, 50, ·, ·] |
   | 삭제 | 3 | 5 | [·, ·, ·, ·, 40, 50, ·, ·] |
2. (a)의 결과:

   | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
   |---|---|---|---|---|---|---|---|
   | · | · | · | · | 40 | 50 | · | · |
   | — | — | — | front | — | —rear | — | — |
3. (b)는 그 상태에서 네 번 더 넣어요.

   | 연산 | front | rear | 0–7번 칸 |
   |---|---|---|---|
   | 넣기(60) | 3 | 6 | [·, ·, ·, ·, 40, 50, 60, ·] |
   | 넣기(70) | 3 | 7 | [·, ·, ·, ·, 40, 50, 60, 70] |
   | 넣기(80) | 3 | 0 | [80, ·, ·, ·, 40, 50, 60, 70] |
   | 넣기(90) | 3 | 1 | [80, 90, ·, ·, 40, 50, 60, 70] |
4. (b)의 결과:

   | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
   |---|---|---|---|---|---|---|---|
   | 80 | 90 | · | · | 40 | 50 | 60 | 70 |
   | — | —rear | — | front | — | — | — | — |
5. 수업과의 연결: 1015 원형 큐에서 front는 첫 요소 하나 앞, rear는 마지막 요소 칸이라고 배웠어요.

**정답:** (a) front=3, rear=5; (b) front=3, rear=1

</details>

---

<a id="partD"></a>

## D. 교과서 연습문제

<a id="p3"></a>

### P3. 원형 큐의 요소 수

원형큐에서 front가 3이고 rear가 5라고 하면 현재 원형큐에 저장된 요소들의 개수는? (단, MAX_QUEUE_SIZE는 8이다.)

(a)

1

(b)

2

(c)

3

(d)

4

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 02번 · 책 171쪽

원형큐에서 front가 3이고 rear가 5라고 하면 현재 원형큐에 저장된 요소들의 개수는? (단, MAX_QUEUE_SIZE는 8이다.)

(a)

1

(b)

2

(c)

3

(d)

4

</details>

<details><summary>힌트 보기</summary>

front=3, rear=5라면 두 인덱스 사이를 순환하며 세어요.

</details>

<details><summary>풀이 보기</summary>

1. front=3 다음 칸은 4, rear=5 칸까지 요소가 있어요.
2. front 다음부터 rear까지 4번과 5번, 두 칸이에요.
3. 수업과의 연결: 1015 수업에서 front를 첫 요소 하나 앞이라고 정의했어요.

**정답:** (b) 2개

</details>

---

<a id="p4"></a>

### P4. 원형 큐의 공백 조건

다음 중 원형큐에서 공백상태에 해당하는 조건은?

(a)

front ==0 && rear == 0

(b)

front == (MAX_QUEUE_SIZE-1) && rear == (MAX_QUEUE_SIZE-1)

(c)

front == rear

(d)

front == (rear+1) % MAX_QUEUE_SIZE

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 04번 · 책 171쪽

다음 중 원형큐에서 공백상태에 해당하는 조건은?

(a)

front ==0 && rear == 0

(b)

front == (MAX_QUEUE_SIZE-1) && rear == (MAX_QUEUE_SIZE-1)

(c)

front == rear

(d)

front == (rear+1) % MAX_QUEUE_SIZE

</details>

<details><summary>힌트 보기</summary>

초기값 0에만 매이지 말고, 삭제가 모두 끝난 뒤의 인덱스도 생각해요.

</details>

<details><summary>풀이 보기</summary>

1. front와 rear는 둘 다 이동하므로 0일 필요가 없어요.
2. 원형 큐는 위치가 어디든 front와 rear가 같으면 비어 있어요.
3. 수업과의 연결: 1015 수업의 원형 큐 공백 검사 조건이 front == rear였어요.

**정답:** (c) front == rear

</details>

---

<a id="p5"></a>

### P5. 큐 연산의 시간 복잡도

큐에 항목들을 삽입하고 삭제하는 연산은 시간 복잡도가 어떻게 되는가?

(a)

O(1)

(b)

O(log₂ n)

(c)

O(n)

(d)

O(n²)

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 07번 · 책 171쪽

큐에 항목들을 삽입하고 삭제하는 연산은 시간 복잡도가 어떻게 되는가?

(a)

O(1)

(b)

O(log₂ n)

(c)

O(n)

(d)

O(n²)

</details>

<details><summary>힌트 보기</summary>

원형 큐에서는 원소를 옮기지 않고 인덱스만 바꿔요.

</details>

<details><summary>풀이 보기</summary>

1. enqueue는 rear를, dequeue는 front를 한 칸씩 옮겨요.
2. 삽입과 삭제마다 인덱스 갱신과 한 칸 접근만 하므로 O(1)이에요.
3. 수업과의 연결: 1015 원형 큐 enqueue·dequeue 코드는 인덱스를 한 번씩 움직여요.

**정답:** (a) O(1)

</details>

---

<a id="p6"></a>

### P6. 원형 큐의 get_count

원형큐에 큐에 존재하는 요소의 개수를 반환하는 연산 get_count를 추가하여 보라. C언어를 이용하여 구현하여 보라.

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 08번 · 책 172쪽

원형큐에 큐에 존재하는 요소의 개수를 반환하는 연산 get_count를 추가하여 보라. C언어를 이용하여 구현하여 보라.

</details>

<details><summary>힌트 보기</summary>

rear에서 front를 뺀 뒤 음수 보정을 위해 크기를 더하고 나머지를 구해요.

</details>

<details><summary>풀이 보기</summary>

1. front 다음 칸부터 rear까지의 거리는 순환 차이로 계산해요.
2. ```c
   #define MAX_QUEUE_SIZE 8
   typedef struct {
       int front;
       int rear;
   } QueueType;

   int get_count(const QueueType *q) {
       return (q->rear - q->front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE;
   }
   ```
3. 예: front=3, rear=5면 (5 - 3 + 8) % 8 = 2예요. front=7, rear=1이면 (1 - 7 + 8) % 8 = 2예요.
4. 수업과의 연결: 1015 원형 큐의 front·rear 정의와 나머지 연산을 그대로 써요.

**정답:** (rear - front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE

</details>

---

<a id="p7"></a>

### P7. 두 스택으로 큐 만들기

2개의 스택을 사용하여 큐를 구현할 수 있을까? 2개의 스택을 사용하여 큐를 구현해보자. 입력이 들어오면 스택 #1에 넣는다. 출력 요청이 들어오면 스택 #2에서 요소를 꺼낸다. 스택 #2가 비어 있을 때는 스택 #1의 모든 요소를 꺼내서 스택 #2에 넣는다. 프로그램으로 작성해보자.

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 09번 · 책 172쪽

2개의 스택을 사용하여 큐를 구현할 수 있을까? 2개의 스택을 사용하여 큐를 구현해보자. 입력이 들어오면 스택 #1에 넣는다. 출력 요청이 들어오면 스택 #2에서 요소를 꺼낸다. 스택 #2가 비어 있을 때는 스택 #1의 모든 요소를 꺼내서 스택 #2에 넣는다. 프로그램으로 작성해보자.

</details>

<details><summary>힌트 보기</summary>

스택 #2가 비었을 때만 #1을 전부 옮기면 오래된 값이 #2의 맨 위로 와요.

</details>

<details><summary>풀이 보기</summary>

1. #1에 넣은 순서를 #2로 옮길 때 뒤집으면 먼저 넣은 값이 먼저 나와 FIFO가 돼요.
2. ```c
   #define CAP 256
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
   }
   ```
3. 예: 10, 20, 30을 넣고 꺼내면 10이에요. 그 뒤 40을 넣어도 다음 출력은 #2에 남은 20이에요.
4. 두 top을 0으로 초기화하고, 실패 때 출력 포인터의 값은 바꾸지 않아요. 전체 CAP개면 삽입 실패, 빈 큐면 삭제 실패예요.
5. 수업과의 연결: 교과서 응용이에요. 1015 수업의 FIFO와 큐 입출력 원리로 동작을 확인할 수 있어요.

**정답:** 두 스택으로 FIFO를 구현할 수 있어요.

</details>

---

<a id="p8"></a>

### P8. 덱으로 회문 검사하기

회문(palindrome)이란 앞뒤 어느 쪽에서 읽어도 같은 말·구·문 등을 의미한다. 예를 들면 “eye”, “madam, “radar” 등이다. 여기서 물론 구두점이나 스페이스, 대소문자 등은 무시하여야 한다. 덱을 이용하여 주어진 문자열이 회문인지 아닌지를 결정하는 프로그램을 작성하라. 다음 그림을 참조한다.

![rear와 front, radar 문자열과 양 끝 문자 r](figures_1015/review-fig-1.svg)

*rear와 front, radar 문자열과 양 끝 문자 r · 넓은 그림은 옆으로 스크롤해 보세요.*

<details><summary>교과서 원문 보기</summary>

교과서 5장 큐 11번 · 책 172쪽

회문(palindrome)이란 앞뒤 어느 쪽에서 읽어도 같은 말·구·문 등을 의미한다. 예를 들면 “eye”, “madam, “radar” 등이다. 여기서 물론 구두점이나 스페이스, 대소문자 등은 무시하여야 한다. 덱을 이용하여 주어진 문자열이 회문인지 아닌지를 결정하는 프로그램을 작성하라. 다음 그림을 참조한다.

![rear와 front, radar 문자열과 양 끝 문자 r](figures_1015/review-fig-2.svg)

*rear와 front, radar 문자열과 양 끝 문자 r · 넓은 그림은 옆으로 스크롤해 보세요.*

</details>

<details><summary>힌트 보기</summary>

대소문자를 통일하고 문자·숫자만 남긴 뒤 양 끝을 비교해요.

</details>

<details><summary>풀이 보기</summary>

1. 덱의 앞뒤에서 하나씩 꺼내 같으면 계속하고, 다르면 회문이 아니에요.
2. ```c
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
   ```
3. “A man, a plan, a canal: Panama!”는 정리하면 양 끝이 모두 맞아요. “가나”는 달라서 회문이 아니에요. 빈 문자열과 한 글자는 회문으로 처리해요.
4. 입력은 UTF-8이어야 해요. 실행 환경의 UTF-8 로캘을 선택하고, 잘못된 문자 시퀀스나 정규화한 문자 CAP개 초과는 -1을 반환해요. 문자 해독과 대소문자 처리는 교과서 구현을 위한 보충이에요.
5. 수업과의 연결: 교과서 응용이에요. 1015 수업의 덱 양끝 삭제 연산으로 비교할 수 있어요.

**정답:** 양 끝에서 꺼낸 문자가 모두 같으면 회문이에요.

</details>

---

출처: 2019 중간·2017 중간(출제자 미상), 교과서 5장 큐 02·04·07·08·09·11번(p171–172). 풀이는 자체 작성하며 답은 Python 시뮬레이션·C11 실행·강의 근거 대조로 검증했어요.
