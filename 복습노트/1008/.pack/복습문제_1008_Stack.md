# 복습문제 5선 — 1008 수업 범위

강의노트의 핵심 개념과 예제 코드를 함께 복습해요. 먼저 직접 풀고 원문·힌트·풀이를 확인하세요.

> 복습문제_1008_Stack.html를 마크다운으로 옮겼어요. 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [A. 검토한 기출·교과서 문제](#partA)
  - [P1. 스택의 공백과 포화](#p1)
- [B. 강의노트 기반 생성문제](#partB)
  - [P2. ListType 삭제 래퍼의 메모리 누수 찾기](#p2)
  - [P3. push·pop·peek의 순서 복원](#p3)
  - [P4. 위치 인자를 선행 노드로 바꾸기](#p4)
  - [P5. 함수 호출과 복귀 순서의 스택](#p5)

<a id="partA"></a>

## A. 검토한 기출·교과서 문제

<a id="p1"></a>

### P1. 스택의 공백과 포화

다음 중 배열로 구현된 스택에서 공백상태에 해당하는 조건은? 또 포화상태에 해당되는 조건은?

(1)

top == -1

(2)

top == 0

(3)

top == (MAX_STACK_SIZE-1)

(4)

top == MAX_STACK_SIZE

<details><summary>교과서 원문 보기</summary>

4장 스택 · 05번 · 책 142쪽

다음 중 배열로 구현된 스택에서 공백상태에 해당하는 조건은? 또 포화상태에 해당되는 조건은?

(1)

top == -1

(2)

top == 0

(3)

top == (MAX_STACK_SIZE-1)

(4)

top == MAX_STACK_SIZE

</details>

<details><summary>힌트 보기</summary>

top은 개수가 아니라 마지막 원소의 인덱스예요.

</details>

<details><summary>풀이 보기</summary>

1. 빈 스택은 원소가 없으므로 top=-1이에요.
2. 길이 M인 배열의 마지막 유효한 인덱스는 M-1이에요.
3. 그 자리에 원소가 있으면 포화예요. top=M이면 이미 배열 밖이에요.
4. 수업과의 연결: 1008 수업 정리노트의 “3. 배열과 top으로 상태 표현하기” 토픽과 강의록에서 다룬 연산·표현을 적용해요.

**정답:** 공백 (1) top==-1 / 포화 (3) top==MAX_STACK_SIZE-1

</details>

---

<a id="partB"></a>

## B. 강의노트 기반 생성문제

<a id="p2"></a>

### P2. ListType 삭제 래퍼의 메모리 누수 찾기

**강의 예제 기반 자체 출제** S4 p48

`ListType`은 첫 노드를 가리키는 `head`와 노드 개수 `length`를 보관해요. `get_node_at(list, pos)`는 `pos < 0`이면 `NULL`을 돌려주고, 그 밖에는 `head`에서 `link`를 `pos`번 따라간 노드를 돌려줘요. 아래는 `remove_node` 함수와 비어 있지 않은 리스트에서 유효한 위치 `pos`(`0 <= pos < length`)의 노드를 삭제하는 래퍼 본문이에요.

```c
// p: 삭제될 노드의 선행 노드, removed: 삭제될 노드
void remove_node(ListNode **phead, ListNode *p, ListNode *removed)
{
    if( p == NULL )
        *phead = (*phead)->link;
    else
        p->link = removed->link;
    free(removed);
}

// delete(list, pos) 래퍼 본문 (결함이 있는 코드)
ListNode *p = get_node_at(list, pos - 1);
remove_node(&(list->head), p, (p != NULL) ? p->link : NULL);
list->length--;
```

- (a) 노드 `A` 하나뿐인 길이 `1` 리스트(`list->head = A, list->length = 1`)에서 `pos = 0`을 삭제할 때, `p`와 `removed` 인자에 전달되는 값과 실행 후 발생하는 메모리 누수 문제를 설명하세요.
- (b) `pos == 0`일 때도 첫 노드가 정상적으로 해제되도록 `remove_node` 호출문의 세 번째 인자 식을 고치세요.

<details><summary>강의 예제 보기</summary>

S4 p48 · 추가 근거 p28,47 · Software_4_List.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
ListNode *p=get_node_at(list,pos-1);
remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
list->length--;
```

</details>

<details><summary>힌트 보기</summary>

`pos - 1 = -1`이므로 `get_node_at`은 `NULL`을 반환하고, 삼항 연산자의 거짓 분기도 `NULL`을 넘겨요.

</details>

<details><summary>풀이 보기</summary>

- (a) `pos = 0`이면 `pos - 1 = -1`이므로 `p = get_node_at(list, -1) = NULL`이 돼요. 삼항 연산자 `(p != NULL) ? p->link : NULL`의 거짓 분기가 선택되어 `removed = NULL`이 전달되므로, `remove_node` 안에서 `*phead = (*phead)->link`로 `list->head`는 `NULL`이 되고 `list->length`도 `0`이 되지만 `free(NULL)`이 실행되어 원래 첫 노드 `A`가 해제되지 않고 누수돼요.
- (b) `p == NULL`(즉 `pos == 0`)일 때 삭제 대상은 현재 첫 노드 `list->head`예요. 따라서 세 번째 인자를 `(p != NULL) ? p->link : list->head`로 고쳐야 `*phead`가 갱신되기 전의 첫 노드 주소가 `removed`로 전달되어 정상 해제돼요.

**정답:** (a) `p = NULL`, `removed = NULL`이 전달되어 `list->head = NULL`, `list->length = 0`으로 갱신되지만 `free(NULL)`이 호출되어 원래 첫 노드 `A`가 해제되지 않고 메모리 누수가 발생한다. (b) 세 번째 인자를 `(p != NULL) ? p->link : list->head`로 고친다.

이 문제는 래퍼 코드의 결함을 찾는 문제예요. 코드를 몰래 고쳐 쓰거나 누수를 정상 동작으로 승인하지 않아요.

</details>

---

<a id="p3"></a>

### P3. push·pop·peek의 순서 복원

**강의 예제 기반 자체 출제** S5 p11

인덱스 `0`부터 쓰는 용량 `3`의 배열 스택이며 초기 상태는 `top = -1`이에요.

```c
push(S, x)
    if is_full(S) then error "overflow"
    else top <- top + 1
         stack[top] <- x

pop(S)
    if is_empty(S) then error "underflow"
    else e <- stack[top]
         top <- top - 1
         return e
```

- (a) 빈 스택에서 `push(5)`, `push(8)`, `peek()`, `pop()`, `push(2)`, `pop()`을 순서대로 실행할 때 각 연산 직후의 `top` 값과 `peek`·`pop`의 반환값, 최종 남은 스택 원소를 쓰세요.
- (b) `peek()`을 `pop()`과 구별하는 차이점과, `pop()`에서 공백 검사 없이 `top`을 먼저 줄여 읽으면 안 되는 이유를 설명하세요.

<details><summary>강의 예제 보기</summary>

S5 p11 · 추가 근거 p12 · Software_5_Stack.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
push(S,x)
    if is_full(S) then error "overflow"
    else top <- top+1
         stack[top] <- x

pop(S)
    if is_empty(S) then error "underflow"
    else e <- stack[top]
         top <- top-1
         return e
```

</details>

<details><summary>힌트 보기</summary>

`top = -1`은 원소가 없다는 뜻이에요. `push`는 먼저 `top`을 올리고 그 위치에 저장해요.

</details>

<details><summary>풀이 보기</summary>

- (a) `push(5)` 후 `top = 0`(`[5]`), `push(8)` 후 `top = 1`(`[5, 8]`)이에요. `peek()`은 맨 위 값 `8`만 읽고 `top = 1`을 유지해요. 첫 `pop()`은 `8`을 반환하고 `top = 0`(`[5]`)으로 줄여요. 이어 `push(2)` 후 `top = 1`(`[5, 2]`), 마지막 `pop()`은 `2`를 반환하고 `top = 0`이 되어 스택에는 `{5}`만 남아요.
- (b) `peek()`은 `top`을 바꾸지 않고 맨 위 원소를 조회만 하는 연산이에요. `pop()`에서 `top`을 먼저 줄여 읽으면 현재 맨 위 원소가 아니라 그 아래 원소를 잘못 읽게 되고, 공백 스택(`top == -1`)에서는 배열 범위 밖 접근이 발생하므로 반드시 접근 전에 `is_empty`를 먼저 검사해야 해요.

**정답:** (a) 단계별 `top`: `0, 1, 1, 0, 1, 0`; 반환값: `peek() = 8`, 첫 `pop() = 8`, 마지막 `pop() = 2`; 남은 스택: `{5}` (b) `peek()`은 `top`을 바꾸지 않고 맨 위 원소만 읽는다. `top`을 먼저 줄여 읽으면 아래 원소를 잘못 읽고 공백 스택에서 범위 밖 접근이 발생하므로 먼저 공백 여부를 검사해야 한다.

`peek`에도 `top--`를 적용하면 단순 조회가 삭제로 바뀌어요.

</details>

---

<a id="p4"></a>

### P4. 위치 인자를 선행 노드로 바꾸기

**강의 예제 기반 자체 출제** S4 p47

`ListType`은 첫 노드 포인터 `head`와 노드 개수 `length`를 함께 보관하며 위치 `position`은 `0`부터 세요. 아래는 위치 기반 삽입 함수 `add`가 사용하는 보조 함수 계약과 호출 흐름이에요.

```c
// get_node_at(list, pos): pos < 0이면 NULL, 그 밖에는 head에서 link를 pos번 따라간 노드 반환
// insert_node(phead, p, new_node): p == NULL이면 맨 앞(*phead)에, 아니면 선행 노드 p 바로 뒤에 삽입
ListNode *p = get_node_at(list, position - 1);
insert_node(&(list->head), p, new_node);
list->length++;
```

- (a) `A -> B -> C -> NULL`(`length = 3`)인 리스트에서 `position = 2`에 새 노드 `N`을 넣을 때와 `position = 0`에 `N`을 넣을 때, 선행 노드 `p`의 값, `insert_node`에 넘기는 세 인자, 삽입 후 리스트 상태와 `length`를 각각 쓰세요.
- (b) `get_node_at(list, position)`처럼 `position`을 그대로 넘기면 어떤 위치 오류가 생기는지 설명하고, `length` 필드를 둔 덕에 가능한 길이 조회 비용과 선행 노드 탐색을 포함한 `add`의 최악 시간 복잡도를 쓰세요.

<details><summary>강의 예제 보기</summary>

S4 p47 · 추가 근거 p44,45,46,25 · Software_4_List.pdf. 1008에 재강조한 S4 p44·47의 함수 재사용 설명과 코드 흐름을 문장형 질문으로 직접 작성했습니다. insert_node 자체의 세 경우는 기존1005 문제와 구별하여 호출 인자 변환을 평가합니다. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

`position = 2`이면 `position - 1 = 1`이므로 선행 노드는 `B`예요.

</details>

<details><summary>풀이 보기</summary>

- (a) `position = 2`는 현재 `C`의 자리이므로 바로 앞인 인덱스 `1`의 노드 `B`가 선행 노드 `p`가 돼요. 따라서 `insert_node(&(list->head), B, N)`을 호출해 `A -> B -> N -> C -> NULL`(`length = 4`)이 돼요. 반면 `position = 0`에서는 `get_node_at(list, -1) = NULL`이므로 `insert_node(&(list->head), NULL, N)`을 호출해 `N`이 새 `head`가 돼요.
- (b) `position - 1` 대신 `position`을 그대로 넘기면 `position = 2`에서 `C`가 선행 노드로 선택되어 `C` 뒤에 들어가므로 목표 위치보다 한 칸 뒤에 삽입돼요. `length`를 저장하므로 길이 조회는 `O(1)`이고, 선행 노드 탐색은 최악 `O(n)`, 포인터 연결 변경 자체는 `O(1)`이에요.

**정답:** (a) `position = 2`: `p = B`, `insert_node(&(list->head), B, N)` 호출, 결과 `A -> B -> N -> C`(`length = 4`); `position = 0`: `p = NULL`, `insert_node(&(list->head), NULL, N)` 호출로 `N`이 새 `head`가 된다. (b) `position`을 그대로 넘기면 `C` 뒤에 삽입되어 한 칸 뒤로 밀린다. 길이 조회는 `O(1)`, 선행 노드 탐색을 포함한 삽입은 최악 `O(n)`(링크 갱신 자체는 `O(1)`)이다.

`position`번째 노드를 선행 노드라고 혼동하지 않아요. `head` 필드의 주소와 `head`가 가리키는 첫 노드의 주소도 구분해요.

</details>

---

<a id="p5"></a>

### P5. 함수 호출과 복귀 순서의 스택

**강의 예제 기반 자체 출제** S5 p8

아래 순서로 함수가 중첩 호출될 때 시스템 스택의 활성 레코드(복귀 위치와 지역 변수)와 배열 스택의 경계 검사를 살펴봐요. 복귀 위치는 실제 기계 주소가 아니라 "호출문 바로 다음"이라는 개념으로만 다뤄요.

```c
main (i = 3)  --호출-->  sub1(i) (a = 3, j = 5)  --호출-->  sub2(j) (b = 5)
```

- (a) `sub2` 실행 중 시스템 스택에 아래부터 쌓여 있는 호출 정보 순서와 `sub2`, `sub1`이 차례로 `return`할 때 복귀하는 함수 순서를 쓰고, 지역 변수만 저장하면 부족한 이유와 되돌리기(undo)와의 공통 규칙을 설명하세요.
- (b) 용량 `M = 3`인 배열 스택에서 `top = 2`일 때의 `push`와 `top = -1`일 때의 `pop`이 각각 `top` 변경·배열 접근보다 먼저 수행해야 하는 검사와, 거부된 연산 뒤 상태가 보존되어야 하는 이유를 쓰세요.

<details><summary>강의 예제 보기</summary>

S5 p8 · 추가 근거 p10,11,12 · Software_5_Stack.pdf. 강의 개념·그림을 근거로 질문을 직접 작성했습니다. 강의 원문 코드의 전사가 아닙니다. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

바닥: `main`의 복귀 위치와 `i = 3` / 그 위: `sub1`의 복귀 위치와 `a = 3, j = 5`.

</details>

<details><summary>풀이 보기</summary>

- (a) `main`이 `sub1`을 호출하고 `sub1`이 `sub2`를 호출하므로, 스택 아래에는 `main`의 복귀 위치와 `i = 3`, 그 위에는 `sub1`의 복귀 위치와 `a = 3, j = 5`가 쌓여요(현재 활성 문맥 `sub2`는 `b = 5`). `sub2`가 끝나면 맨 위의 `sub1` 호출 다음으로, `sub1`이 끝나면 `main` 호출 다음으로 돌아가요. 지역 변수만 저장하면 돌아갈 실행 위치를 알 수 없고, 가장 최근 호출·변경부터 처리하는 후입선출(LIFO) 규칙이 함수 복귀와 undo에 공통으로 적용돼요.
- (b) 용량 `M = 3`의 유효 인덱스는 `0..2`이므로, `top = 2`에서의 `push`는 `is_full`을 먼저 검사해 증가·저장을 거부해야 하고, `top = -1`에서의 `pop`은 `is_empty`를 먼저 검사해 읽기·감소를 거부해야 해요. 실패한 연산이 `top`이나 배열을 건드리면 범위 밖 접근이 일어나거나 기존 스택 상태가 깨지기 때문이에요.

**정답:** (a) 스택 아래부터 `main`(복귀 위치, `i = 3`), 그 위에 `sub1`(복귀 위치, `a = 3, j = 5`)을 기억하며, 복귀 순서는 `sub2 -> sub1 -> main`이다. 지역 변수만으로는 다음 실행 위치를 알 수 없으며, 함수 복귀와 undo 모두 가장 최근 항목부터 처리하는 LIFO 규칙을 따른다. (b) `top = 2`인 `push`는 `is_full`을, `top = -1`인 `pop`은 `is_empty`를 먼저 검사해 거부해야 하며, 실패한 연산은 범위 밖 접근을 막고 기존 스택 상태를 그대로 유지해야 한다.

복귀 위치를 배열 인덱스나 실제 기계 주소로 계산하지 않아요. 이 문제는 개념 모형의 복귀 관계를 물어요.

</details>

---

기출·교과서 원문과 강의 예제 기반 자체 출제. 강의 코드는 발췌 여부를 표시했으며 질문·풀이·실행 검산은 별도로 작성했습니다.
