# Content review — 0921 구조체 대입과 포인터 필드 복사

대조 자료: Software_3_ArrayStructureList.pdf p17(person, `person a, b; b = a; // 가능`, `if( a > b ) // 불가능`), p18(ListNode, `struct ListNode *link;`) 렌더링, 정리노트 `s4-struct-assign`(대입 가능·비교 불가·a.age > b.age 보충), `s4-self-ref`, STT 0921 1687–1763행(철가방 규격이 같으면 내용물이 왔다 갔다, 몇 층을 비교할지).

## 코드 보존
- source.c에 p17·p18 원문을 주석으로 그대로 보존. 화면 코드는 name[10] 생략, height int, ListNode data int로 단순화했고 코드 줄 주석·코드 아래 안내·brief에 밝혔다.
- `b = a;  // 가능` 줄은 원문 그대로. 비교 줄은 원문 `if( a > b )`가 불가능하므로 정리노트 보충의 `if( a.age > b.age )`를 쓰고 설명에서 원문이 왜 안 되는지 말한다.

## 단계별 C 의미
- copy(기본 20, 170): 8줄 초기화 a.age=20, a.height=170, b 미초기화 → 9줄 b = a를 필드 순서대로 read a.age → write b.age, read a.height → write b.height(구조체 값 복사 = 필드별 값 복사, 깊은 공유 없음) → 10줄 a.age 읽고 21 쓰기, b.age=20 그대로 → 11줄 a.age, b.age 읽기, 21 > 20 참 → 출력.
- 같은 값(7,7), 경계 -999/999: 더하기 1이 int 범위 안. 값이 같아도 a와 b의 Cell은 별개.
- uninit(강의 main): `person a, b;` 뒤 `b = a;`에서 a.age 첫 읽기 → UNINITIALIZED_READ로 중단. a의 주소를 쓰지 않는 미초기화 자동 객체 읽기는 정의되지 않은 동작이라 실행 값을 꾸미지 않았다. 설명은 강의 요지(대입 문법은 가능)와 실제 사용(먼저 값을 넣어야 함)을 구분.
- link(10, 20): n2={20, NULL}, n1={10, &n2} → c = n1에서 data 값 복사, link는 주소 값 &n2 복사(n2 노드 복제 없음) → c.data=11, n1.data=10 그대로 → `c.link->data = 0`은 c.link를 따라 n2.data에 쓰기(through 사슬 검사) → `n1.link->data`를 따라 읽으면 0(별칭), seen=0.
- 포인터 대상은 구조체 첫 필드 Cell(n2.data)로 표현하고 주소를 `&n2.data (= &n2)`로 표시(첫 멤버 주소 = 구조체 주소).

## 문구
- 화살표 → 표시는 레이블 폰트 합자일 뿐 코드 줄은 `->` 그대로.
- 판정: pass.
