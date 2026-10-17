# 복습문제 3선 — 1008 수업 범위

핵심 개념과 강의 예제 코드를 함께 복습해요. 먼저 직접 풀고 원문·힌트·풀이를 확인하세요.

> 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

**목차**

- [A. 검토한 기출·교과서 문제](#partA)
  - [P1. 스택의 공백과 포화](#p1)
- [B. 강의 예제 코드](#partB)
  - [P2. ListType 삭제 래퍼의 메모리 누수 찾기](#p2)
  - [P3. push·pop·peek의 순서 복원](#p3)

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

## B. 강의 예제 코드

<a id="p2"></a>

### P2. ListType 삭제 래퍼의 메모리 누수 찾기

**강의 예제 기반 자체 출제** S4 p48 · 추가 근거 p28,47

강의 p47에서 get_node_at의 음수 위치 반환은 NULL이고 p28의 remove_node는 p==NULL이면 head를 다음으로 옮긴 뒤 free(removed)를 실행해요. 길이 1인 리스트에서 pos=0을 삭제하면 head와 length는 바뀌지만 어떤 메모리 문제가 남나요? removed 인자를 고치세요.

```c
ListNode *p=get_node_at(list,pos-1);
remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
list->length--;
```

<details><summary>강의 예제 보기</summary>

S4 p48 · 추가 근거 p28,47 · Software_4_List.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

```c
ListNode *p=get_node_at(list,pos-1);
remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
list->length--;
```

</details>

<details><summary>힌트 보기</summary>

pos-1=-1이므로 get_node_at은 NULL을 반환해요. 삼항식의 거짓 분기도 NULL을 넘겨요.

</details>

<details><summary>풀이 보기</summary>

1. pos-1=-1이므로 get_node_at은 NULL을 반환해요. 삼항식의 거짓 분기도 NULL을 넘겨요.
2. remove_node는 head를 다음으로 옮기지만 free(NULL)은 아무 메모리도 반납하지 않아요. 기존 첫 노드 주소를 잃으므로 누수가 남아요.
3. 호출 시점의 list-&gt;head를 removed로 넘기면 remove_node가 갱신 전에 받은 첫 노드 주소를 해제할 수 있어요. 비어 있지 않고 위치가 유효하다는 래퍼의 검사는 유지해요.

**정답:** p=NULL,removed=NULL로 전달되어 head=NULL,length=0이지만 실제 첫 노드는 free되지 않아 누수된다. removed 인자는 (p!=NULL)?p-&gt;link:list-&gt;head로 고친다.

이 예제는 강의 원문의 결함을 찾는 문제예요. 원문을 몰래 수정하거나 누수를 정상 동작으로 승인하지 않아요.

</details>

---

<a id="p3"></a>

### P3. push·pop·peek의 순서 복원

**강의 예제 기반 자체 출제** S5 p11 · 추가 근거 p12

인덱스 0부터 쓰는 용량 3의 스택이며 초기 top=-1이에요. push(5),push(8),peek(),pop(),push(2),pop()의 반환값과 각 단계 top을 쓰세요. peek를 pop과 구별하고 빈 스택에서 먼저 top을 줄여 읽으면 안 되는 이유도 설명하세요.

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

top=-1은 원소가 없다는 뜻이에요. push는 먼저 top을 올리고 그 위치에 저장해요.

</details>

<details><summary>풀이 보기</summary>

1. top=-1은 원소가 없다는 뜻이에요. push는 먼저 top을 올리고 그 위치에 저장해요.
2. 5와 8을 넣으면 top=1이에요. peek는 8을 읽기만 해서 top=1을 유지해요.
3. pop은 현재 top의 8을 보관한 뒤 top을 0으로 줄여요. 2를 넣고 꺼내면 다시 5만 남아요.
4. top을 먼저 줄여 읽으면 꺼낼 원소가 아닌 그 아래를 읽어요. 빈 상태에서는 배열 범위 밖 접근이 될 수 있어요.

**정답:** top: 0,1,1,0,1,0. peek=8, 첫 pop=8, 마지막 pop=2. 남은 스택 {5}. peek는 top을 바꾸지 않는다. 빈 스택은 접근 전에 검사해야 한다.

peek에도 top--를 적용하면 조회가 삭제로 바뀌어요.

</details>

---

기출·교과서 원문과 강의 예제 기반 자체 출제. 강의 코드는 발췌 여부를 표시했으며 질문·풀이·실행 검산은 별도로 작성했습니다.
