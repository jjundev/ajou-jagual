# Content review — 1008 list-delete

대조 자료: S4 p28·p45·p46·p47·p48 렌더링(90dpi)과 pdftotext, 정리노트 HTML/.pack MD s0-adapter(pos=0 경계 해설 포함), STT 1008 Part 01.

코드: delete 본문·주석은 p48, remove_node 본문·주석은 p28, is_empty는 p46, get_node_at은 p47, ListType은 p45 원문과 같다(줄 앞 공백만 정리). 원본의 pos=0 경계 문제를 고치지 않았다. "보충 · head" 모드는 셋째 인자 한 줄을 list->head로 바꾼 학습용 대조이며, 화면의 모드 라벨·코드 아래 안내·줄 끝 주석(// 보충 비교)·출처 상세가 강의 코드가 아님을 밝힌다.

단계별 C 의미 검토(기본 pos=0 원본 및 모든 preset):
- delete 호출: list에 &list1 주소 값, pos에 정수 복사.
- 조건 `!is_empty(list) && (pos >= 0) && (pos < list->length)`: is_empty 호출(list 주소 값 복사, list->head 읽기, 1/0 반환)을 먼저 계산하고 단락 평가를 따른다. 빈 리스트는 pos·length를 읽지 않는다. pos 음수는 length를 읽지 않는다. 범위 밖이면 아무것도 바꾸지 않고 반환.
- `ListNode *p = get_node_at(list, pos-1);` p 선언 후 호출 결과로 초기화. get_node_at 단계는 list-add와 같은 원문 순서.
- 셋째 인자 `(p!=NULL)?p->link:NULL`: p 읽기 → p가 있으면 p->link 읽기, 없으면 원본은 NULL(지울 노드 주소를 전달하지 않음), 보충은 list->head 읽기. 함수 인자 평가 순서는 C가 정하지 않지만 이 인자들에는 부수 효과가 없어 결과가 같다.
- remove_node: phead=&(list->head), p, removed 값 복사. p==NULL이면 *phead 읽기 → (*phead)->link 읽기 → *phead에 다음 노드 주소 쓰기. 아니면 removed->link 읽기 → p->link 쓰기.
- free(removed): 원본 pos=0에서는 free(NULL)이라 무동작이고 n1은 할당된 채 남는다. 마지막 단계에서 n1을 가리키는 살아 있는 포인터가 없다(누수). 그 외에는 지운 노드 객체의 수명이 끝나고 removed는 사용 불가 값이 된다. 해제 후 별칭을 따라가지 않는다.
- list->length-- 후 반환. 최종 설명의 리스트 순서·누수/해제 문구는 상태와 일치.

단순화: 첫 멤버가 아닌 멤버(link, length)는 해당 Cell 직접 읽기/쓰기(설명에 경유 포인터 명시). is_empty 반환값은 조건식에서 소비되어 별도 Cell 없이 설명으로 표시. 기호 주소.

노트와의 관계: 노트 s0-adapter의 "원본 p48은 pos=0에서 removed=NULL… 첫 노드 메모리를 해제하지 못한다" 해설을 실제 상태로 보인다. 수정 코드를 수업 코드로 소개하지 않는다.

독립 검산: evidence/independent.json — Python 표 65사례(기본·preset 9 + 격자 56: n 0–3 × pos -99,-1..3,99 × 두 모드), 419개 값 복사·쓰기와 최종 리스트, 해제된 객체, 누수 객체(원본·pos 0·n>0에서만 n1) 일치. 변조 검사 검출. 컴파일러 없음(compiler_unavailable), UB 실행 없음.

판정: pass.
