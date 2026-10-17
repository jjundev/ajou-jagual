# 자료구조및알고리즘이해 복습 1008 문제설명

왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.

문제의 첫 줄부터 검산까지 설명해요.

**목차**

- [문항별 설명](#problems)
  - [P1. 스택의 공백과 포화](#p1)
  - [P2. ListType 삭제 래퍼의 메모리 누수 찾기](#p2)
  - [P3. push·pop·peek의 순서 복원](#p3)

<a id="problems"></a>

## 문항별 설명

<a id="p1"></a>

### P1. 스택의 공백과 포화

textbook-ch04-q05 · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack.html#p1)

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

---

<a id="p2"></a>

### P2. ListType 삭제 래퍼의 메모리 누수 찾기

lecture-s04-p48-list-delete-leak · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack.html#p2)

**강의 예제 기반 자체 출제** S4 p48 · 추가 근거 p28,47

강의 p47에서 get_node_at의 음수 위치 반환은 NULL이고 p28의 remove_node는 p==NULL이면 head를 다음으로 옮긴 뒤 free(removed)를 실행해요. 길이 1인 리스트에서 pos=0을 삭제하면 head와 length는 바뀌지만 어떤 메모리 문제가 남나요? removed 인자를 고치세요.

`ListNode *p=get_node_at(list,pos-1);
remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
list->length--;`

<details><summary>강의 예제 보기</summary>

S4 p48 · 추가 근거 p28,47 · Software_4_List.pdf. 강의 코드의 해당 연산을 발췌해 들여쓰기를 정리했습니다. 주변 선언·main·입출력을 생략한 발췌·번역은 완전한 실행 프로그램과 구별해요. 아래 질문·입력 조건은 자체 출제예요.

`ListNode *p=get_node_at(list,pos-1);
remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);
list->length--;`

</details>

#### 문제를 내 말로 읽어요

강의 p47에서 get_node_at의 음수 위치 반환은 NULL이고 p28의 remove_node는 p==NULL이면 head를 다음으로 옮긴 뒤 free(removed)를 실행해요. 길이 1인 리스트에서 pos=0을 삭제하면 head와 length는 바뀌지만 어떤 메모리 문제가 남나요? removed 인자를 고치세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “ListType 삭제 래퍼의 메모리 누수 찾기”예요. pos-1=-1이므로 get_node_at은 NULL을 반환해요. 삼항식의 거짓 분기도 NULL을 넘겨요. 호출 시점의 list-&gt;head를 removed로 넘기면 remove_node가 갱신 전에 받은 첫 노드 주소를 해제할 수 있어요. 비어 있지 않고 위치가 유효하다는 래퍼의 검사는 유지해요.

#### 종이에 적을 첫 줄

pos-1=-1이므로 p=NULL이라고 적어요.

#### 왜 이렇게 푸는지 함께 따라가요

1. pos-1=-1이므로 get_node_at은 NULL을 반환해요. 삼항식의 거짓 분기도 NULL을 넘겨요.
2. remove_node는 head를 다음으로 옮기지만 free(NULL)은 아무 메모리도 반납하지 않아요. 기존 첫 노드 주소를 잃으므로 누수가 남아요.
3. 호출 시점의 list-&gt;head를 removed로 넘기면 remove_node가 갱신 전에 받은 첫 노드 주소를 해제할 수 있어요. 비어 있지 않고 위치가 유효하다는 래퍼의 검사는 유지해요.

p=NULL,removed=NULL로 전달되어 head=NULL,length=0이지만 실제 첫 노드는 free되지 않아 누수된다. removed 인자는 (p!=NULL)?p-&gt;link:list-&gt;head로 고친다.

#### 완성 답과 검산

p=NULL,removed=NULL로 전달되어 head=NULL,length=0이지만 실제 첫 노드는 free되지 않아 누수된다. removed 인자는 (p!=NULL)?p-&gt;link:list-&gt;head로 고친다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. 호출 시점의 list-&gt;head를 removed로 넘기면 remove_node가 갱신 전에 받은 첫 노드 주소를 해제할 수 있어요. 비어 있지 않고 위치가 유효하다는 래퍼의 검사는 유지해요.

#### 이 문제에서 조심할 점

이 예제는 강의 원문의 결함을 찾는 문제예요. 원문을 몰래 수정하거나 누수를 정상 동작으로 승인하지 않아요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

pos-1=-1이므로 p=NULL이라고 적어요.

#### 떠올릴 개념·공식

pos-1=-1이므로 get_node_at은 NULL을 반환해요. 삼항식의 거짓 분기도 NULL을 넘겨요.

#### 검산

p=NULL,removed=NULL로 전달되어 head=NULL,length=0이지만 실제 첫 노드는 free되지 않아 누수된다. removed 인자는 (p!=NULL)?p-&gt;link:list-&gt;head로 고친다.

---

<a id="p3"></a>

### P3. push·pop·peek의 순서 복원

lecture-s05-p11-stack-adt · [원 문제 보기](../%EB%B3%B5%EC%8A%B5%EB%AC%B8%EC%A0%9C_1008_Stack.html#p3)

**강의 예제 기반 자체 출제** S5 p11 · 추가 근거 p12

인덱스 0부터 쓰는 용량 3의 스택이며 초기 top=-1이에요. push(5),push(8),peek(),pop(),push(2),pop()의 반환값과 각 단계 top을 쓰세요. peek를 pop과 구별하고 빈 스택에서 먼저 top을 줄여 읽으면 안 되는 이유도 설명하세요.

`push(S,x)
    if is_full(S) then error "overflow"
    else top <- top+1
         stack[top] <- x

pop(S)
    if is_empty(S) then error "underflow"
    else e <- stack[top]
         top <- top-1
         return e`

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

인덱스 0부터 쓰는 용량 3의 스택이며 초기 top=-1이에요. push(5),push(8),peek(),pop(),push(2),pop()의 반환값과 각 단계 top을 쓰세요. peek를 pop과 구별하고 빈 스택에서 먼저 top을 줄여 읽으면 안 되는 이유도 설명하세요.

#### 이 문제를 봤을 때 떠올릴 개념과 공식

문제의 단서는 “push·pop·peek의 순서 복원”예요. top=-1은 원소가 없다는 뜻이에요. push는 먼저 top을 올리고 그 위치에 저장해요. top을 먼저 줄여 읽으면 꺼낼 원소가 아닌 그 아래를 읽어요. 빈 상태에서는 배열 범위 밖 접근이 될 수 있어요.

#### 종이에 적을 첫 줄

top=-1, 빈 스택 []로 상태 표를 시작해요.

#### 왜 이렇게 푸는지 함께 따라가요

1. top=-1은 원소가 없다는 뜻이에요. push는 먼저 top을 올리고 그 위치에 저장해요.
2. 5와 8을 넣으면 top=1이에요. peek는 8을 읽기만 해서 top=1을 유지해요.
3. pop은 현재 top의 8을 보관한 뒤 top을 0으로 줄여요. 2를 넣고 꺼내면 다시 5만 남아요.
4. top을 먼저 줄여 읽으면 꺼낼 원소가 아닌 그 아래를 읽어요. 빈 상태에서는 배열 범위 밖 접근이 될 수 있어요.

top: 0,1,1,0,1,0. peek=8, 첫 pop=8, 마지막 pop=2. 남은 스택 {5}. peek는 top을 바꾸지 않는다. 빈 스택은 접근 전에 검사해야 한다.

#### 완성 답과 검산

top: 0,1,1,0,1,0. peek=8, 첫 pop=8, 마지막 pop=2. 남은 스택 {5}. peek는 top을 바꾸지 않는다. 빈 스택은 접근 전에 검사해야 한다.

시작 조건에서 다시 추적한 결과가 위 답과 일치해요. top을 먼저 줄여 읽으면 꺼낼 원소가 아닌 그 아래를 읽어요. 빈 상태에서는 배열 범위 밖 접근이 될 수 있어요.

#### 이 문제에서 조심할 점

peek에도 top--를 적용하면 조회가 삭제로 바뀌어요.

#### 설명을 닫고 다시 해 봐요

1. 주어진 시작 상태와 필요한 입력 조건을 적어요.
2. 첫 줄부터 연산 순서를 따라 답을 완성해요.
3. 경계 경우와 오류 경로를 확인해요.

**페이지 요약**

#### 첫 줄

top=-1, 빈 스택 []로 상태 표를 시작해요.

#### 떠올릴 개념·공식

top=-1은 원소가 없다는 뜻이에요. push는 먼저 top을 올리고 그 위치에 저장해요.

#### 검산

top: 0,1,1,0,1,0. peek=8, 첫 pop=8, 마지막 pop=2. 남은 스택 {5}. peek는 top을 바꾸지 않는다. 빈 스택은 접근 전에 검사해야 한다.

---

원 문제·정리노트·PDF는 보존해요.
