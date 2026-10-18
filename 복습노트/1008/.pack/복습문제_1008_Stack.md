# 복습문제 5선 — 1008 수업 범위

강의노트의 핵심 개념과 예제 코드를 함께 복습해요. 먼저 직접 풀고 원문·힌트·풀이를 확인하세요.

> 원문, 힌트, 풀이는 접혀 있어요. 먼저 풀어 보고 펼쳐 보세요.

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

<a id="p4"></a>

### P4. 위치 인자를 선행 노드로 바꾸기

**강의 예제 기반 자체 출제** S4 p47 · 추가 근거 p44,45,46,25

ListType은 head와 length를 함께 보관해요. A→B→C→NULL,length=3인 리스트에서 위치2에 N을 넣는 add가 get_node_at(list,position-1)를 호출한 뒤 기존 insert_node를 재사용합니다. 반환되는 선행 노드, 함수에 넘기는 세 인자와 결과를 쓰세요. 위치0 삽입에서는 선행 노드와 head가 어떻게 되는지, position을 그대로 get_node_at에 넘기면 생기는 위치 오류, length를 따로 저장하는 이점과 탐색을 포함한 최악 비용도 설명하세요.

<details><summary>강의 예제 보기</summary>

S4 p47 · 추가 근거 p44,45,46,25 · Software_4_List.pdf. 1008에 재강조한 S4 p44·47의 함수 재사용 설명과 코드 흐름을 문장형 질문으로 직접 작성했습니다. insert_node 자체의 세 경우는 기존1005 문제와 구별하여 호출 인자 변환을 평가합니다. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

position=2 → position−1=1 → 선행 노드B.

</details>

<details><summary>풀이 보기</summary>

1. 위치 2는 현재 C의 자리이므로 바로 앞의 인덱스 1에 있는 B를 찾아야 해요.
2. 기존 insert_node가 요구하는 것은 위치 정수가 아닌 선행 노드의 주소예요.
3. 호출자의 head를 바꿀 가능성이 있으므로 head 필드의 주소와 B, N을 전달해요.
4. 위치 0에서는 음수 −1에 대해 NULL을 반환하는 약속으로 맨 앞 삽입을 표현해요.
5. 래퍼는 삽입 성공 후 length를 1 늘려요. 길이 조회와 선행 노드 탐색은 서로 다른 연산이에요.

**정답:** 위치 2의 선행 노드는 B이며 insert_node(&(list-&gt;head),B,N)을 호출합니다. 결과는 A→B→N→C, length=4입니다. 위치 0에서는 get_node_at(-1)=NULL이므로 N이 새 head가 됩니다. position을 그대로 쓰면 C 뒤에 넣어 한 칸 늦어집니다. length를 저장하므로 길이 조회는 O(1)입니다. 위치 변환을 위한 탐색은 최악 O(n)이고 삽입의 링크 변경 자체는 O(1)입니다.

position번째 노드를 선행 노드라고 혼동하지 않아요. head 필드의 주소와 head가 가리키는 첫 노드의 주소도 구분해요.

</details>

---

<a id="p5"></a>

### P5. 함수 호출과 복귀 순서의 스택

**강의 예제 기반 자체 출제** S5 p8 · 추가 근거 p10,11,12

강의 예처럼 main의 i=3에서 sub1(i)를 호출하고 sub1의 a=3,j=5에서 sub2(j)를 호출했어요. sub2 실행 중 기억해야 할 호출 정보의 순서와, sub2와 sub1이 차례로 return할 때 복귀하는 함수 순서를 쓰세요. 지역 변수만 저장하고 돌아올 위치를 버리면 왜 부족한지, 가장 오래된 호출로 먼저 돌아가면 안 되는 이유, 되돌리기(undo)와의 공통 규칙도 설명하세요. PC 숫자는 실제 C 주소가 아닌 강의 그림의 복귀 위치 표시로만 다루세요. 이어 용량 M=3인 배열 스택에서 top=2일 때 push, top=-1일 때 pop을 요청했어요(두 상황은 독립적이에요). 각 경우 어떤 검사가 top 변경과 배열 접근보다 먼저여야 하며, 거부된 연산 뒤 상태가 유지돼야 하는 이유를 쓰세요.

<details><summary>강의 예제 보기</summary>

S5 p8 · 추가 근거 p10,11,12 · Software_5_Stack.pdf. 강의 개념·그림을 근거로 질문을 직접 작성했습니다. 강의 원문 코드의 전사가 아닙니다. 질문·입력 조건·검산은 자체 작성했어요.

</details>

<details><summary>힌트 보기</summary>

바닥: main의 복귀 위치와 i=3 / 그 위: sub1의 복귀 위치와 a=3, j=5.

</details>

<details><summary>풀이 보기</summary>

1. main은 sub1을 호출하며 실행을 잠시 멈추므로 돌아올 위치와 현재 지역 상태를 남겨요.
2. sub1이 sub2를 호출할 때도 같은 정보를 그 위에 쌓아요.
3. sub2의 return은 맨 위의 sub1 정보를 사용해 sub1의 호출 다음으로 돌아가요.
4. 그 뒤 sub1이 끝나면 아래에 남은 main 정보로 돌아가요.
5. 가장 최근 정보를 먼저 사용한다는 점에서 undo의 최근 변경 취소와 같은 LIFO예요.

**정답:** 호출 정보는 아래부터 main의 복귀 위치·i=3, 그 위에 sub1의 복귀 위치·a=3,j=5를 기억합니다. sub2가 끝나면 sub1의 호출 다음으로, sub1이 끝나면 main의 호출 다음으로 돌아갑니다. 지역 변수만으로는 다음 실행 위치를 알 수 없습니다. 가장 최근에 중단한 호출부터 복귀하는 LIFO이며 undo도 마지막 변경부터 되돌립니다. 현재 실행 중인 sub2의 문맥에는 b=5도 있어요. main·sub1은 복귀를 기다리는 호출자이며 sub2가 현재 활성 문맥이에요. top=2인 push는 is_full을 먼저 검사하여 증가·저장을 거부하고, top=-1인 pop은 is_empty를 먼저 검사하여 읽기·감소를 거부해요. 실패한 연산은 유효 범위 밖에 접근하거나 상태를 바꾸지 않아야 해요.

PC 값을 배열 인덱스나 실제 기계 주소로 계산하지 않아요. 이 문제는 개념 모형의 복귀 관계를 물어요.

</details>

---

기출·교과서 원문과 강의 예제 기반 자체 출제. 강의 코드는 발췌 여부를 표시했으며 질문·풀이·실행 검산은 별도로 작성했습니다.
