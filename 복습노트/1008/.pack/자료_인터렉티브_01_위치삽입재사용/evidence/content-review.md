# Content review — 1008 list-add

대조 자료: S4 p25·p45·p47 렌더링(90dpi)과 pdftotext, 정리노트 HTML/.pack MD s0-adapter, STT 1008 Part 01–02.

코드: get_node_at·add 본문과 주석은 p47, insert_node 본문·주석은 p25와 글자 단위로 같다(줄 앞 공백만 정리, `ListNode*node=` 띄어쓰기 정리). ListType은 p45. #include·ListNode 정의·error·main·준비된 list1은 보충이며 화면 코드 아래 안내와 출처 상세가 이를 밝힌다.

단계별 C 의미 검토(기본 position=1, data=15, n=3 및 모든 preset):
- call→bind: list에는 &list1 주소 값, position·data에는 정수 값이 복사된다. 호출자 구조체를 복제하지 않는다. &list1을 첫 멤버 주소 &list1.head 기호로 표시함을 설명에 밝혔다.
- `ListNode *p;` 미초기화 선언 → 조건식은 && 단락 평가: position<0이면 list->length를 읽지 않는다(negative), position>length면 거짓(over) → 노드 생성 없이 반환, list1 불변.
- malloc: 새 객체의 data/link는 미초기화, 시작 주소가 node에 쓰인다. node==NULL 검사는 node 읽기. node->data=data는 node 경유 쓰기.
- get_node_at: list 주소 값 복사(fromCellId로 add.list 실제 값 일치 확인), pos=position-1 복사. tmp_node 초기화는 pos 검사보다 먼저 list->head를 읽는다(원문 순서). pos<0이면 NULL 반환. 아니면 i=0, i<pos마다 tmp_node->link 읽기→tmp_node 쓰기→i++ 순서이며 반환값은 add의 p에 쓰이고 get_node_at 지역 변수 수명이 끝난다.
- insert_node: phead에는 &(list->head) 즉 head 변수의 주소가 복사된다(head에 든 노드 주소가 아님). p·new_node는 add의 변수에서 값 복사. *phead 읽기로 분기: 빈 리스트(new->link=NULL, *phead=new), p==NULL(new->link=*phead, *phead=new), 그 외(new->link=p->link 먼저, p->link=new). phead 자신은 바뀌지 않고 대상 head가 바뀐다.
- list->length++ 읽기·쓰기, add 반환 후 malloc 노드는 연결되어 남는다. 마지막 설명의 리스트 순서는 최종 상태와 일치.

단순화: n->link, list->length처럼 첫 멤버가 아닌 멤버는 엔진의 포인터 사슬 검사가 대상 Cell과 일치를 요구하므로 해당 Cell을 직접 읽고/쓰며 설명에서 경유 포인터를 밝혔다. 첫 멤버(head, data)는 through 사슬로 실제 대상 일치를 검사했다. 조건식의 다른 피연산자 읽기(i<pos의 pos)는 대표 Cell 하나로 보였다. 주소는 기호이며 실제 배치를 주장하지 않는다.

노트와의 관계: 노트 s0-adapter의 "position=0이면 get_node_at이 NULL, insert_node가 head를 바꿔 앞에 삽입" 설명과 일치. 수업 표현을 고쳐 쓰지 않는다.

독립 검산: evidence/independent.json — Python 표 103사례(기본·preset 7 + 격자 96: n 0–3 × position -99,-1..4,99 × data -99/0/99), 1021개 bind/declare/allocate/write 값과 최종 리스트 순서·length·해제/누수 없음 일치. 변조 검사(마지막 정수 쓰기 +1)도 검출. C 컴파일러 없음(compiler_unavailable), UB 실행 없음.

판정: pass.
