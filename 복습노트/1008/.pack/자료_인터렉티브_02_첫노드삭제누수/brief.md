# 첫 위치를 삭제하면 무엇이 해제될까?

1008 수업 S4 p48 delete와 S4 p28 remove_node의 조합을 노드 수명 변화로 확인한다. 노트 절: s0-adapter (노트가 이미 pos=0 경계 문제를 설명).

**핵심 질문**: 원본 delete(list, 0)은 셋째 인자로 NULL을 넘긴다. remove_node는 head를 옮기고 free(NULL)을 부르므로 첫 노드는 해제되지 않고 아무 포인터도 가리키지 않게 된다(누수). 이를 실제 상태로 보인다.

입력: pos -99–99(유효 범위 0–length-1), 처음 노드 수 n 0–3, 셋째 인자 모드(원본 NULL / 보충 list->head). 사례: 원본 첫 노드(누수), 보충 첫 노드(해제), 가운데, 마지막, 노드 하나 pos 0(누수·head NULL), 빈 리스트(is_empty), 범위 밖 3, 음수 -1.

원문: delete는 S4 p48, remove_node(주석 포함)는 S4 p28, is_empty는 S4 p46, get_node_at은 S4 p47, ListType은 S4 p45. 원본의 경계 문제를 고치지 않고 그대로 실행한다. 보충 비교 모드는 셋째 인자 한 줄만 list->head로 바꾼 학습용 대조이며 강의 수정 코드가 아니라고 화면·출처에 표시한다. 보충: #include, ListNode 정의, main과 준비된 list1.

단순화: 멤버 접근은 해당 Cell 직접 읽기/쓰기(설명에 경유 포인터 명시). is_empty 반환값은 조건식에서 소비되므로 별도 Cell 없이 설명으로 표시한다. free(NULL)은 무동작, 해제 후 removed는 사용 불가 값. 누수는 할당 객체가 살아 있으나 가리키는 살아 있는 포인터가 없음으로 판정한다.

독립 검산: compiler_unavailable. Python 표로 모든 값 복사·쓰기, 최종 리스트, 해제 객체, 누수 객체를 비교한다.
