# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_1008_Stack.html#p1 | 일반 | 공백-1포화M-1이다. | empty −1, full M−1 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1008_Stack.html#p1 | 주의 | top0은1개,M범위밖,size top+1이다. | 공백은 (1) top=-1, 포화는 (3) top=M-1이에요. top=0은 원소 1개이고 top=M은 이미 배열 범위 밖이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1008_Stack.html#p2 | 일반 | 첫삭제시removedNULL누수와수정거짓분기listhead이다. | (a) p = NULL, removed = NULL로 첫 노드 A 누수 (b) (p != NULL) ? p->link : list->head | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1008_Stack.html#p2 | 일반 | freeNULL아무것도해제안하고옛head변경전에대상확보다. | free(NULL)은 아무 블록도 해제하지 않아요. head를 옮기기 전 첫 노드 주소를 removed 인자로 넘겨야 실제 A가 free돼요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1008_Stack.html#p3 | 일반 | push선증가,pop읽고감소,peek불변및최종값이다. | push는 선증가 후 저장, pop은 선읽기 후 감소, peek은 top 유지예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1008_Stack.html#p3 | 일반 | 미검사/선감소범위밖오류이다. | peek은 top 유지, 선감소 및 미검사는 범위 밖 접근 유발 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1008_Stack.html#p4 | 일반 | position-1선행,0NULL첫삽입,탐색On길이O1이다. | 위치 position 삽입의 선행 노드는 get_node_at(list, position - 1)이며, position = 0일 때는 NULL을 반환해 맨 앞 삽입으로 연결해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1008_Stack.html#p4 | 주의 | head자신주소와첫노드주소구분이다. | insert_node(&(list->head),p,new_node)는 첫 노드 주소가 아니라 head 필드 자신의 주소를 첫 인자로 받아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1008_Stack.html#p5 | 일반 | 활성레코드복귀위치지역값LIFO,배열검사선행이다. | 시스템 스택은 복귀 위치와 지역 상태를 함께 저장하며 가장 최근 호출부터 복귀(LIFO)해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1008_Stack.html#p5 | 일반 | full/empty실패상태보존이다. | top = 2 push는 is_full, top = -1 pop은 is_empty 선검사 및 상태 보존 | pass | pass / 기존 충족, 수정 없음 |
| 복습문제_1008_Stack.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_1008_Stack.html#s0-adapter | 일반 | 위치에서선행노드로변환해함수재사용한다. | 위치를 선행 노드로 바꿔 기존 삽입·삭제 함수를 재사용해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s0-adapter | 조건 | 0기반position-1,음수NULL첫삽입,head자신주소전달이다. | 위치는 0부터 세고 get_node_at(position-1)로 선행 노드를 찾아요. 음수는 NULL이라 첫 삽입으로 이어지며 &(list->head)로 head 변수의 주소를 넘겨요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s0-adapter | 보충 | 원본삭제첫노드누수는슬라이드대조해설이지수업수정아니다. | 구현 해설: 원본 p48은 pos=0에서 removed=NULL을 넘겨 첫 노드가 해제되지 않아요. 실제 첫 노드를 전달해야 하며, 수업에서 수정 코드를 제시했다는 뜻은 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s0-readable | 일반 | 함수역할구분읽기와재사용돕는다. | 역할별로 함수를 나누면 읽기 쉽고 다시 쓰기 쉬워요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s1-lifo | 일반 | top에서만입출해LIFO이다. | 스택은 top에서만 넣고 꺼내므로 가장 나중에 넣은 요소가 먼저 나와요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s1-adt | 일반 | push추가,pop삭제반환,peek불변반환이다. | push는 위에 넣고, pop은 꺼내며, peek는 그대로 두고 보기만 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s1-adt | 일반 | create생성,isempty/full상태,위치인자없다. | create는 생성, is_empty·is_full은 상태 검사예요. push·pop은 위치가 언제나 top이라 위치나 선행 노드 인자가 필요 없어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s1-trace | 일반 | ABC넣고popC,AB잔류한다. | A, B, C를 차례로 넣고 pop()을 하면 C가 반환되고 A, B가 남아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s1-trace | 구분 | peek는C읽어도ABC유지다. | pop 전 peek는 C를 읽어도 [A,B,C]를 유지해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s2-undo | 일반 | 최근수정부터취소LIFO와FIFO대비다. | undo는 수정 기록을 쌓고 가장 최근 수정부터 되돌려요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s2-call | 일반 | 활성레코드는지역상태와복귀위치보존이다. | 함수는 활성 레코드에 돌아올 곳과 지역 변수를 보존해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s2-call | 구분 | main→sub1→sub2는재귀아닌중첩,복귀역순이다. | 호출 main→sub1→sub2의 복귀는 sub2→sub1→main이에요. 서로 다른 함수의 중첩 호출이며 자기 호출인 재귀와 구별해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s2-array | 일반 | top마지막원소인덱스와bottom방향이다. | 배열 스택의 top은 현재 맨 위 요소의 인덱스를 가리켜요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s2-array | 조건 | 0기반공백-1포화M-1;1기반설계와혼합금지다. | 0번부터 채우면 공백 top=-1, 포화 top=MAX_STACK_SIZE-1이에요. 1번부터 쓰는 다른 설계의 공백 표지와 섞지 말고 일관되게 맞춰요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s2-pushpop | 일반 | 검사→증가저장,검사→읽기감소이다. | 넣을 때는 검사 후 위치를 올려 저장하고, 꺼낼 때는 검사 후 읽어 위치를 내려요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s2-pushpop | 보충 | O1은슬라이드외자체분석이다. | 슬라이드 외 분석: 배열 push·pop은 검사·인덱스 변경·한 원소 접근만 하므로 O(1)이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-sort | 일반 | priority작은순삽입정렬이다. | 정렬된 영역에 노드를 하나씩 넣어 우선순위가 작은 것부터 놓아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s3-sort | 주의 | 데이터아닌노드재연결,엄격>안정순서,헤드설계자료대조이다. | 데이터 교환 대신 노드를 옮기며 앞 priority가 더 큰(>) 동안만 찾아 같은 값의 상대 순서를 지켜요. 배포 설명의 헤드 유무 충돌은 제공 코드의 헤드 노드 설계를 따라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-sort | 보충 | On²은자체분석이다. | 자체 분석(강의·배포 자료에 명시되지 않음): 정렬된 영역을 거슬러 찾는 최악 비용은 O(n²)이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-move | 일반 | 연결바꾸기전next대피이다. | 현재 노드의 연결을 바꾸기 전에 다음 정렬 대상을 저장해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s3-move | 일반 | detach해제아닌분리,재삽입후nextunsorted재개,헤드중지다. | next_unsorted=current->next를 보관하고 왼쪽 탐색 → detach_node → insert_after 뒤 current=next_unsorted로 계속해요. detach는 해제가 아닌 분리이고 헤드에서 탐색을 멈춰요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-firstfit | 일반 | 낮은주소첫충분한연속빈블록이다. | First-Fit은 앞에서부터 처음 만나는 충분히 큰 연속 빈 블록을 골라요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s3-firstfit | 조건 | 정확크기전체,크면분할;총량60최대25에30실패다. | 크기가 같으면 전체 할당하고 크면 남은 빈 부분을 분할해요. 빈칸 합이 60이어도 최대 연속 구간이 25이면 30 요청은 실패해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-merge | 일반 | 빈양옆인접구간병합이다. | 해제한 블록의 양옆이 비어 있으면 이어서 한 구간으로 만들어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s3-merge | 주의 | start..start+size-1,헤드할당삭제금지;PDF기준P3 10칸이다. | 실제 구간은 start..start+size-1이고 헤드는 실제 블록으로 할당·삭제하지 않아요. 추적은 조교 구술 15칸이 아닌 과제 PDF p17의 P3 10칸을 적용해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-requirements | 일반 | 다섯함수와c/PDF기한제출이다. | 다섯 함수를 직접 구현하고 소스와 PDF 보고서를 기한 안에 제출해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1008_Stack.html#s3-requirements | 일반 | 함수역할과실패불변,중복PID거부다. | find_first_fit·find_process_block은 대상 탐색, allocate_memory는 중복 PID 거절·할당·분할, merge_free_blocks는 이웃 병합, release_memory는 반납·병합해요. 성공 1·실패 0이며 실패해도 상태를 보존해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s3-requirements | 조건 | 제공선언유지/추가함수금지/양수입력/제출형식및기한이다. | 제공 선언과 함수 형식은 유지하고 추가 함수 없이 지정 부분만 채워요. 양의 정수 입력을 전제하며 .c와 PDF를 10월 28일→29일 자정까지 제출해요. 코드 분석은 2칼럼, 결과 분석 형식은 선택 가능해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1008_Stack.html#s4-cheatsheet | 구조 | 기존요약·예고·링크화면구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1008_Stack.html#s4-next | 구조 | 기존요약·예고·링크화면구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1008_Stack.html#s4-links | 구조 | 기존요약·예고·링크화면구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
