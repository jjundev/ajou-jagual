# 자료구조및알고리즘이해 복습 1008 문제설명

왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.

문제의 첫 줄부터 검산까지 설명해요.

**목차**

- [문항별 설명](#problems)
  - [P1. 스택의 공백과 포화](#p1)
  - [P2. ListType 삭제 래퍼의 메모리 누수 찾기](#p2)
  - [P3. push·pop·peek의 순서 복원](#p3)
  - [P4. 위치 인자를 선행 노드로 바꾸기](#p4)
  - [P5. 함수 호출과 복귀 순서의 스택](#p5)

<a id="problems"></a>

## 문항별 설명

<a id="p1"></a>

### P1. 스택의 공백과 포화

textbook-ch04-q05 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack-%EB%AC%B8%EC%A0%9C.pdf#page=1)

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

#### 문제를 내 말로 읽어요

배열 스택의 빈 상태와 가득 찬 상태를 각각 골라요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

길이 M=MAX_STACK_SIZE 배열의 유효 index는 0..M−1이에요. top은 마지막 index, 아무 원소가 없을 때는 −1이라는 sentinel이에요.

#### 종이에 적을 첫 줄

빈 상태 top=−1을 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

공백은 (1) top==−1, 포화는 (3) top==MAX_STACK_SIZE−1이에요. top==0은 하나 저장된 상태이고 top==M은 배열 밖 인덱스예요.

#### 완성 답과 검산

M=5에서 top=−1이면 size=0, top=4이면 size=5예요. 각각 실제 칸 수와 맞아요.

#### 이 문제에서 조심할 점

“가득 참”을 top==M으로 검사하면 이미 범위를 넘어서요.

#### 설명을 닫고 다시 해 봐요

1. 빈 상태 top=−1을 적어요.
2. empty −1, full M−1
3. 조건·끝 상태와 검산 근거를 직접 다시 확인해요.

**페이지 요약**

#### 첫 줄

빈 상태 top=−1을 적어요.

#### 떠올릴 개념·공식

empty −1, full M−1

#### 검산

본문의 조건과 독립 추적을 함께 확인해요.

#### 조건·구분과 확인

- 공백은 (1) top=-1, 포화는 (3) top=M-1이에요. top=0은 원소 1개이고 top=M은 이미 배열 범위 밖이에요.

---

<a id="p2"></a>

### P2. ListType 삭제 래퍼의 메모리 누수 찾기

lecture-s04-p48-list-delete-leak · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack-%EB%AC%B8%EC%A0%9C.pdf#page=2)

**강의 예제 기반 자체 출제** S4 p48

`ListType`은 첫 노드를 가리키는 `head`와 노드 개수 `length`를 보관해요. `get_node_at(list, pos)`는 `pos < 0`이면 `NULL`을 돌려주고, 그 밖에는 `head`에서 `link`를 `pos`번 따라간 노드를 돌려줘요. 아래는 `remove_node` 함수와 비어 있지 않은 리스트에서 유효한 위치 `pos`(`0 <= pos < length`)의 노드를 삭제하는 래퍼 본문이에요.

`// p: 삭제될 노드의 선행 노드, removed: 삭제될 노드
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
list->length--;`

#### 구할 것

- (a) 노드 `A` 하나뿐인 길이 `1` 리스트(`list->head = A, list->length = 1`)에서 `pos = 0`을 삭제할 때, `p`와 `removed` 인자에 전달되는 값과 실행 후 발생하는 메모리 누수 문제를 설명하세요.
- (b) `pos == 0`일 때도 첫 노드가 정상적으로 해제되도록 `remove_node` 호출문의 세 번째 인자 식을 고치세요.

<details><summary>강의 예제 보기</summary>

S4 p48 · 추가 근거 p28,47 · Software_4_List.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`ListNode *p=get_node_at(list,pos-1);
remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
list->length--;`

</details>

#### 문제를 내 말로 읽어요

길이 `1`인 리스트에서 첫 노드(`pos = 0`)를 삭제할 때 래퍼 함수가 잘못된 `removed` 인자를 넘겨 메모리 누수가 발생하는 원인을 찾고 삼항 연산자 식을 고치는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “ListType 삭제 래퍼의 메모리 누수 찾기”예요. `pos = 0`이면 `pos - 1 = -1`이므로 `get_node_at`은 `NULL`을 반환하고, 이때 실제 삭제되어 `free`되어야 할 대상은 호출 시점의 첫 노드인 `list->head`예요.

#### 종이에 적을 첫 줄

`pos = 0`일 때 `p = get_node_at(list, -1) = NULL`을 먼저 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `pos = 0`이면 `p = NULL`이므로 `(p != NULL) ? p->link : NULL`의 결과로 `removed = NULL`이 넘어가요. `remove_node`는 `*phead`를 다음 노드(`NULL`)로 바꾸고 래퍼는 `list->length`를 `0`으로 줄이지만, `free(NULL)`은 아무 메모리도 해제하지 않아 원래 첫 노드 `A`가 누수돼요.

(b) `p == NULL`일 때 해제할 노드는 `*phead`가 바뀌기 전의 첫 노드 `list->head`이므로, 세 번째 인자를 `(p != NULL) ? p->link : list->head`로 고쳐야 해요.

#### 완성 답과 검산

(a) 수정 전 식에 `p = NULL`을 대입하면 `removed = NULL`이 되어 `free(NULL)`이 실행되고 노드 `A`의 주소를 잃어버림을 확인할 수 있어요.

(b) 수정 후 식에 `p = NULL`을 대입하면 `removed = list->head`(`A`)가 전달되어 `*phead` 갱신 뒤 `free(A)`가 정상 실행돼요.

#### 이 문제에서 조심할 점

이 문제는 래퍼 코드의 결함을 찾는 문제예요. 코드를 몰래 고쳐 쓰거나 누수를 정상 동작으로 승인하지 않아요.

#### 설명을 닫고 다시 해 봐요

1. `pos = 0`일 때 `get_node_at(list, pos - 1)`의 반환값을 구해요.
2. `remove_node` 내부에서 `*phead` 갱신과 `free(removed)`가 어떻게 실행되는지 추적해요.
3. 삼항 연산자의 거짓 분기를 올바른 노드 포인터로 고쳐 적어요.

**페이지 요약**

#### 첫 줄

`pos = 0`일 때 `p = get_node_at(list, -1) = NULL`을 먼저 적어요.

#### 떠올릴 개념·공식

선행 노드 `p == NULL`이면 삭제할 노드는 `list->head`예요.

#### 검산

(a) `p = NULL, removed = NULL`로 첫 노드 `A` 누수 (b) `(p != NULL) ? p->link : list->head`

#### 조건·구분과 확인

- free(NULL)은 아무 블록도 해제하지 않아요. head를 옮기기 전 첫 노드 주소를 removed 인자로 넘겨야 실제 A가 free돼요.

---

<a id="p3"></a>

### P3. push·pop·peek의 순서 복원

lecture-s05-p11-stack-adt · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack-%EB%AC%B8%EC%A0%9C.pdf#page=3)

**강의 예제 기반 자체 출제** S5 p11

인덱스 `0`부터 쓰는 용량 `3`의 배열 스택이며 초기 상태는 `top = -1`이에요.

`push(S, x)
    if is_full(S) then error "overflow"
    else top <- top + 1
         stack[top] <- x

pop(S)
    if is_empty(S) then error "underflow"
    else e <- stack[top]
         top <- top - 1
         return e`

#### 구할 것

- (a) 빈 스택에서 `push(5)`, `push(8)`, `peek()`, `pop()`, `push(2)`, `pop()`을 순서대로 실행할 때 각 연산 직후의 `top` 값과 `peek`·`pop`의 반환값, 최종 남은 스택 원소를 쓰세요.
- (b) `peek()`을 `pop()`과 구별하는 차이점과, `pop()`에서 공백 검사 없이 `top`을 먼저 줄여 읽으면 안 되는 이유를 설명하세요.

<details><summary>강의 예제 보기</summary>

S5 p11 · 추가 근거 p12 · Software_5_Stack.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`push(S,x)
    if is_full(S) then error "overflow"
    else top <- top+1
         stack[top] <- x

pop(S)
    if is_empty(S) then error "underflow"
    else e <- stack[top]
         top <- top-1
         return e`

</details>

#### 문제를 내 말로 읽어요

초기 `top = -1`인 용량 `3` 배열 스택에서 `push`, `peek`, `pop` 연산 열을 단계별로 추적하고 `peek`과 `pop`의 차이를 설명하는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “push·pop·peek의 순서 복원”이에요. `top = -1`은 공백 상태이고, `push`는 먼저 `top`을 `1` 올린 뒤 저장하며, `pop`은 현재 `stack[top]`을 꺼낸 뒤 `top`을 `1` 줄이고, `peek`은 `top`을 바꾸지 않고 읽기만 해요.

#### 종이에 적을 첫 줄

초기 상태 `top = -1`, 빈 스택 `[]`로 상태 표를 시작해요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `push(5)`로 `top = 0`(`[5]`), `push(8)`로 `top = 1`(`[5, 8]`)이 돼요. `peek()`은 `8`을 반환하고 `top = 1`을 유지해요. 첫 `pop()`은 `8`을 반환하고 `top = 0`(`[5]`)으로 줄여요. `push(2)`로 `top = 1`(`[5, 2]`)이 된 뒤 마지막 `pop()`은 `2`를 반환하고 `top = 0`이 되어 `{5}`가 남아요.

(b) `peek()`은 원소를 제거하지 않고 맨 위 값만 확인하므로 `top`을 변경하지 않아요. `pop()`에서 공백 검사 없이 `top`을 먼저 줄여 읽으면 꺼낼 원소가 아닌 그 아래 원소를 읽게 되고, 빈 스택(`top == -1`)에서는 배열 범위 밖 접근이 일어나요.

#### 완성 답과 검산

(a) 총 `push` 3회, `pop` 2회가 실행되었으므로 최종 원소 개수는 `1`개(`{5}`)이고 마지막 `top = 0`과 일치해요.

(b) `top = 0`(원소 `1`개)일 때 `top`을 먼저 줄이면 `stack[-1]`을 읽게 되어 잘못된 접근임이 바로 확인돼요.

#### 이 문제에서 조심할 점

`peek`에도 `top--`를 적용하면 단순 조회가 삭제로 바뀌어요.

#### 설명을 닫고 다시 해 봐요

1. 6개 연산을 순서대로 적고 매 단계의 `top`과 반환값을 채워요.
2. `peek()`과 `pop()` 실행 후 `top`의 차이를 비교해요.
3. `top` 감소와 배열 읽기의 순서가 바뀔 때 생기는 오류를 확인해요.

**페이지 요약**

#### 첫 줄

초기 상태 `top = -1`, 빈 스택 `[]`로 상태 표를 시작해요.

#### 떠올릴 개념·공식

`push`는 선증가 후 저장, `pop`은 선읽기 후 감소, `peek`은 `top` 유지예요.

#### 검산

(a) `top`: `0, 1, 1, 0, 1, 0`, 반환 `8, 8, 2`, 남은 스택 `{5}` (b) `peek`은 `top` 유지, 선감소 및 미검사는 범위 밖 접근 유발

---

<a id="p4"></a>

### P4. 위치 인자를 선행 노드로 바꾸기

lecture-s04-p47-list-position-adapter · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack-%EB%AC%B8%EC%A0%9C.pdf#page=4)

**강의 예제 기반 자체 출제** S4 p47

`ListType`은 첫 노드 포인터 `head`와 노드 개수 `length`를 함께 보관하며 위치 `position`은 `0`부터 세요. 아래는 위치 기반 삽입 함수 `add`가 사용하는 보조 함수 계약과 호출 흐름이에요.

`// get_node_at(list, pos): pos < 0이면 NULL, 그 밖에는 head에서 link를 pos번 따라간 노드 반환
// insert_node(phead, p, new_node): p == NULL이면 맨 앞(*phead)에, 아니면 선행 노드 p 바로 뒤에 삽입
ListNode *p = get_node_at(list, position - 1);
insert_node(&(list->head), p, new_node);
list->length++;`

#### 구할 것

- (a) `A -> B -> C -> NULL`(`length = 3`)인 리스트에서 `position = 2`에 새 노드 `N`을 넣을 때와 `position = 0`에 `N`을 넣을 때, 선행 노드 `p`의 값, `insert_node`에 넘기는 세 인자, 삽입 후 리스트 상태와 `length`를 각각 쓰세요.
- (b) `get_node_at(list, position)`처럼 `position`을 그대로 넘기면 어떤 위치 오류가 생기는지 설명하고, `length` 필드를 둔 덕에 가능한 길이 조회 비용과 선행 노드 탐색을 포함한 `add`의 최악 시간 복잡도를 쓰세요.

<details><summary>강의 예제 보기</summary>

S4 p47 · 추가 근거 p44,45,46,25 · Software_4_List.pdf. 1008에 재강조한 S4 p44·47의 함수 재사용 설명과 코드 흐름을 문장형 질문으로 직접 작성했습니다. insert_node 자체의 세 경우는 기존1005 문제와 구별하여 호출 인자 변환을 평가합니다. 질문·입력 조건·검산은 자체 작성했어요.

</details>

#### 문제를 내 말로 읽어요

위치 정수 `position`을 받아 노드를 삽입하는 `add` 함수가 `get_node_at(list, position - 1)`로 선행 노드를 찾아 `insert_node`를 재사용하는 원리와 시간 복잡도를 묻는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

‘`get_node_at`으로 구한 선행 노드로 `insert_node`를 호출한다’는 단서는 인터페이스 어댑터(adapter)를 뜻해요. 사용자는 위치 `position`을 주고 `insert_node`는 선행 노드 주소 `p`를 원하므로 `position - 1` 위치 탐색으로 둘을 이어 줘요.

#### 종이에 쓰는 첫 줄

`position = 2 -> position - 1 = 1 -> 선행 노드 p = B`를 먼저 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `position = 2`는 현재 `C`의 자리이므로 바로 앞인 인덱스 `1`의 `B`를 찾아 `insert_node(&(list->head), B, N)`을 호출하고, 결과는 `A -> B -> N -> C`(`length = 4`)가 돼요. `position = 0`이면 `get_node_at(list, -1) = NULL`이므로 `insert_node(&(list->head), NULL, N)`을 호출해 `N`이 새 `head`가 돼요.

(b) 만약 `get_node_at(list, position)`을 호출하면 `position = 2`에서 `C`가 선행 노드가 되어 `C` 뒤에 들어가므로 한 칸 뒤로 밀려요. `length` 필드를 유지하므로 길이 조회는 `O(1)`이고, 선행 노드를 찾는 탐색 때문에 삽입의 최악 시간 복잡도는 `O(n)`(링크 갱신 자체는 `O(1)`)이에요.

#### 완성 답과 검산

(a) 결과 `A -> B -> N -> C`의 인덱스를 다시 세면 `A:0, B:1, N:2, C:3`이어서 요청한 `position = 2`에 `N`이 정확히 놓였어요.

(b) 잘못된 선행 노드 `C` 뒤에 넣으면 `N`의 인덱스가 `3`이 되어 한 칸 늦어진다는 사실이 바로 확인돼요.

#### 이 문제에서 조심할 점

`position`번째 노드를 선행 노드라고 혼동하지 않아요. `head` 필드의 주소와 `head`가 가리키는 첫 노드의 주소도 구분해요.

#### 설명을 닫고 다시 해 봐요

1. `position = 2`와 `position = 0`에서 `get_node_at(list, position - 1)`의 반환값을 각각 구해요.
2. `insert_node`에 전달되는 세 인자와 결과 체인을 적어요.
3. 길이 조회 비용과 선행 노드 탐색을 포함한 삽입 비용을 비교해요.

**페이지 요약**

#### 떠올릴 개념·공식

위치 `position` 삽입의 선행 노드는 `get_node_at(list, position - 1)`이며, `position = 0`일 때는 `NULL`을 반환해 맨 앞 삽입으로 연결해요.

#### 첫 줄

`position = 2 -> position - 1 = 1 -> 선행 노드 p = B`를 먼저 적어요.

#### 핵심 답

(a) `position = 2`: `p = B`, `A -> B -> N -> C`(`length = 4`); `position = 0`: `p = NULL`, `N`이 새 `head` (b) `position` 그대로 전달 시 한 칸 뒤 삽입, 길이 조회 `O(1)`, 탐색 포함 삽입 `O(n)`

#### 조건·구분과 확인

- insert_node(&(list-&gt;head),p,new_node)는 첫 노드 주소가 아니라 head 필드 자신의 주소를 첫 인자로 받아요.

---

<a id="p5"></a>

### P5. 함수 호출과 복귀 순서의 스택

lecture-s05-p8-activation-record-return · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack-%EB%AC%B8%EC%A0%9C.pdf#page=5)

**강의 예제 기반 자체 출제** S5 p8

아래 순서로 함수가 중첩 호출될 때 시스템 스택의 활성 레코드(복귀 위치와 지역 변수)와 배열 스택의 경계 검사를 살펴봐요. 복귀 위치는 실제 기계 주소가 아니라 "호출문 바로 다음"이라는 개념으로만 다뤄요.

`main (i = 3)  --호출-->  sub1(i) (a = 3, j = 5)  --호출-->  sub2(j) (b = 5)`

#### 구할 것

- (a) `sub2` 실행 중 시스템 스택에 아래부터 쌓여 있는 호출 정보 순서와 `sub2`, `sub1`이 차례로 `return`할 때 복귀하는 함수 순서를 쓰고, 지역 변수만 저장하면 부족한 이유와 되돌리기(undo)와의 공통 규칙을 설명하세요.
- (b) 용량 `M = 3`인 배열 스택에서 `top = 2`일 때의 `push`와 `top = -1`일 때의 `pop`이 각각 `top` 변경·배열 접근보다 먼저 수행해야 하는 검사와, 거부된 연산 뒤 상태가 보존되어야 하는 이유를 쓰세요.

<details><summary>강의 예제 보기</summary>

S5 p8 · 추가 근거 p10,11,12 · Software_5_Stack.pdf. 강의 개념·그림을 근거로 질문을 직접 작성했습니다. 강의 원문 코드의 전사가 아닙니다. 질문·입력 조건·검산은 자체 작성했어요.

</details>

#### 문제를 내 말로 읽어요

`main -> sub1 -> sub2` 중첩 호출에서 시스템 스택에 쌓이는 호출 정보와 복귀 순서를 추적하고, 배열 스택의 포화·공백 경계 검사를 확인하는 문제예요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

‘호출했다가 돌아온다’는 말에서 시스템 스택(system stack)의 활성 레코드(activation record)와 후입선출(LIFO) 규칙을 떠올려요. 배열 스택에서는 인덱스 변경이나 배열 접근 전에 반드시 `is_full`·`is_empty`를 먼저 검사해야 해요.

#### 종이에 쓰는 첫 줄

바닥: `main`(복귀 위치, `i = 3`) / 그 위: `sub1`(복귀 위치, `a = 3, j = 5`)을 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

(a) `main`이 `sub1`을 부르고 `sub1`이 `sub2`를 부르므로 스택 아래부터 `main`(복귀 위치, `i = 3`), 그 위에 `sub1`(복귀 위치, `a = 3, j = 5`)이 쌓여요. `sub2`가 끝나면 맨 위의 `sub1`로, `sub1`이 끝나면 `main`으로 복귀해요. 지역 변수만 저장하면 돌아갈 코드 위치를 알 수 없으며, 가장 최근 호출·작업부터 되돌리는 LIFO 규칙이 함수 복귀와 undo에 공통으로 쓰여요.

(b) 용량 `M = 3`인 배열 스택에서 `top = 2`일 때의 `push`는 `is_full`을 먼저 검사해 거부해야 하고, `top = -1`일 때의 `pop`은 `is_empty`를 먼저 검사해 거부해야 해요. 먼저 검사하지 않으면 배열 범위(`0..2`) 밖 메모리에 접근하거나 실패한 연산이 기존 스택 상태를 훼손하기 때문이에요.

#### 완성 답과 검산

(a) 호출 순서 `main -> sub1 -> sub2`와 복귀 순서 `sub2 -> sub1 -> main`이 정확히 역순(LIFO)을 이루어요.

(b) 용량 `3`의 유효 인덱스는 `0..2`이므로 `top = 2`에서 증가하면 `3`, `top = -1`에서 읽으면 `-1`이 되어 범위 밖임이 확인돼요.

#### 이 문제에서 조심할 점

복귀 위치를 배열 인덱스나 실제 기계 주소로 계산하지 않아요. 이 문제는 개념 모형의 복귀 관계를 물어요.

#### 설명을 닫고 다시 해 봐요

1. `sub2` 실행 시점에 스택 아래부터 쌓인 호출 정보를 적어요.
2. 복귀 순서와 LIFO·undo의 공통점을 정리해요.
3. `top = 2`에서의 `push`와 `top = -1`에서의 `pop`이 먼저 검사할 조건을 적어요.

**페이지 요약**

#### 떠올릴 개념·공식

시스템 스택은 복귀 위치와 지역 상태를 함께 저장하며 가장 최근 호출부터 복귀(LIFO)해요.

#### 첫 줄

바닥: `main`(복귀 위치, `i = 3`) / 그 위: `sub1`(복귀 위치, `a = 3, j = 5`)을 적어요.

#### 핵심 답

(a) `main` 위에 `sub1` 저장, 복귀는 `sub2 -> sub1 -> main`(LIFO, undo와 동일) (b) `top = 2` `push`는 `is_full`, `top = -1` `pop`은 `is_empty` 선검사 및 상태 보존

---

원 문제·정리노트·PDF는 보존해요.
