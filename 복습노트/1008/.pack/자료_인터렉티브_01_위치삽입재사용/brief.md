# 위치를 선행 노드로 바꿔 삽입하기

1008 수업 S4 p44·p47의 "리스트 기능 재사용"을 호출 프레임과 노드 연결 변화로 확인한다. 노트 절: s0-adapter.

**핵심 질문**: add(list, position, data)는 위치를 받는데, 왜 get_node_at(list, position-1)과 insert_node(&(list->head), p, node)를 부르는가? position=0이면 무엇이 바뀌는가?

입력: position -99–99(유효 범위 0–length), data -99–99, 처음 노드 수 n 0–3(10, 20, 30). 사례: 가운데·맨 앞·맨 뒤(position=length)·빈 리스트·범위 밖 4·음수 -1. 경계: position 0과 length, data -99/99, 빈 리스트의 *phead==NULL 분기.

원문: get_node_at·add는 S4 p47, insert_node(주석 포함)는 S4 p25, ListType은 S4 p45. 줄 앞 공백만 정리. 보충: #include, ListNode 정의, error 함수, main과 준비된 list1(앞선 add로 만들었다고 가정한 초기 상태). source.c는 준비 상태를 실제 C로 적은 검산용 판본이다.

단순화: 구조체 멤버 접근(n->link, list->length)은 엔진의 포인터 사슬 검사가 첫 멤버만 직접 대응하므로 해당 멤버 Cell을 직접 읽고 쓰며 설명에서 경유 포인터를 밝힌다. 구조체·노드 포인터는 첫 멤버 Cell(&list1.head, &n1.data)로 표시한다. 조건식의 여러 피연산자 읽기는 대표 Cell 하나로 보인다. 주소는 기호다.

독립 검산: C 컴파일러(gcc/clang/cl/tcc) 없음 → compiler_unavailable. 별도 Python 표로 모든 bind/declare/allocate/write 값과 최종 리스트를 비교한다.
