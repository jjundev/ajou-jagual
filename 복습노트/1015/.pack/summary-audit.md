# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_1015_Queue.html#p1 | 일반 | 순환거리개수수식이다. | 원형 큐의 순환 거리: (rear - front + MAX_QUEUE_SIZE) % MAX_QUEUE_SIZE. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p1 | 조건 | 유효0..M-1한칸비움전제와경계,상수시간이다. | 0≤front,rear<M이며 한 칸 비우는 구현에만 적용해요. 공백 0·포화 M-1개이고 계산 O(1)이에요. 모든 칸을 채우는 구현은 별도 포화 구분이 필요해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p2 | 일반 | out빈때만전체이동두번반전FIFO,분할상환O1최악On이다. | 스택을 두 번 뒤집으면 FIFO. 분할상환 $O(1)$, 이동하는 한 번은 최악 $O(n)$. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p2 | 조건 | 총용량256,top0,성공1실패0,유효포인터,빈출력불변이다. | 두 top은 0으로 시작하고 in.top+out.top으로 총 용량 256을 검사해요. 성공 1·실패 0이며 빈 삭제는 출력값을 유지하고 q·value는 유효해야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p2 | 주의 | out값있을때이동하면순서깨진다. | out에 값이 남아 있으면 in을 옮기지 않아요. 먼저 옮기면 새로 온 값이 앞서 FIFO가 깨져요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p3 | 일반 | 양끝최대k/2비교,UTF8보충,반환3상태이다. | 덱 양끝 삭제로 최대 $\lfloor k/2\rfloor$번 비교해요. UTF-8 문자 해독은 구현 보충이에요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p3 | 일반 | 정규화대소문자공백구두점무시후0/1개기저이다. | 구두점·공백을 빼고 대소문자를 맞춘 뒤 양끝이 다르면 거짓, 0개나 1개만 남을 때까지 같으면 참이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p3 | 보충 | UTF8로캘/wcharCAP256보충,완전unicode정규화없다. | 구현 보충: UTF-8 로캘에서 wchar_t로 해독하고 정리 후 문자 최대 256개를 다뤄요. 로캘별 분류·한 문자 소문자화에 한정하며 완전한 유니코드 정규화·대소문자 접기는 하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p4 | 일반 | 첫양끝N,마지막양끝NULL와수명순서있다. | 빈 큐 삽입은 front = rear = N, 마지막 노드 삭제 후에는 front = rear = NULL로 맞춰요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p4 | 일반 | 값보관front옮김rear필요갱신후free다. | old = front; item = old->data; front = old->link; if (front == NULL) rear = NULL; free(old); | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p5 | 일반 | ifelse한분기틱과별도if차이정확추적이다. | if/else는 한 틱에 한 분기만 실행하므로 1 -> 0 감소와 새 고객 시작은 서로 다른 틱에 일어나요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p5 | 일반 | 대기1대0과상태101/02/21이다. | clock = 1: 1 -> 0, clock = 2: 0 -> 2(B 시작, 대기 1), clock = 3: 2 -> 1 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p6 | 일반 | 선이동modM,한칸비움포화조건과추적있다. | 원형 큐는 인덱스를 먼저 (idx + 1) % M으로 옮긴 뒤 접근하며, 포화 조건은 (rear + 1) % M == front예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p6 | 일반 | 용량M-1=4이다. | 유효 용량 M - 1 = 4 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p7 | 일반 | 첫양끝동일,기존tail반대링크와생성계약있다. | 빈 덱에 첫 원소를 넣을 때는 head와 tail을 모두 새 노드로 설정하고, 비공백 덱에서는 기존 tail->rlink와 새 노드의 llink를 상호 연결해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p7 | 조건 | 바깥끝링크NULL유지조건이다. | 첫 A의 llink는 NULL, 새 B의 rlink도 NULL로 유지해 양 끝 바깥으로 연결되지 않게 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p8 | 일반 | 삭제후공백양끝NULL/아니면headllinkNULL이다. | 삭제 후 dq->head == NULL이면 dq->tail = NULL로, 아니면 dq->head->llink = NULL로 갱신해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p8 | 주의 | 생략시해제노드참조와무조건역참조NULL오류다. | 분기를 빼면 tail이나 새 머리의 llink가 해제 노드를 가리켜요. 공백에서 무조건 head->llink를 쓰면 NULL 역참조예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p9 | 일반 | 총삽입10삭제4로f4r2점유6이다. | 삭제 4회와 삽입 10회를 각각 세어 front=4, rear=2예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p9 | 주의 | 한칸비움최대6삽입가능,04원문보존,잔여값비원소다. | 한 칸을 비우는 용량 7에서 최대 점유는 6이라 모든 삽입이 가능해요. 원문 04를 바꾸지 않고 삭제된 칸의 잔여 값은 현재 원소로 세지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1015_Queue.html#p10 | 일반 | a3,5이어서b3,1과점유2/6이다. | (a) front=3, rear=5; 이어서 (b) front=3, rear=1이에요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1015_Queue.html#p10 | 주의 | b재초기화금지,a40,50위치45와b60708090위치6701이다. | (a)는 4번=40·5번=50이고 그대로 이어 (b)에 6번=60·7번=70·0번=80·1번=90을 넣어요. (b)를 빈 큐에서 다시 시작하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 복습문제_1015_Queue.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_1015_Queue.html#s0-buffer | 일반 | 원형은FIFO유지하며앞빈칸재사용한다. | 원형 큐는 도착 순서를 지키면서 배열 앞쪽의 빈칸을 다시 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s0-buffer | 일반 | rear삽입front삭제,선형끝삽입불가,논리적순환이다. | 삽입은 rear·삭제는 front예요. 선형 배열은 뒤 인덱스가 끝이면 앞이 비어도 못 넣으므로, 마지막 다음을 0으로 보는 논리적 순환으로 재사용해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s0-index | 일반 | front첫원소직전rear마지막이다. | front는 첫 요소 하나 앞, rear는 마지막 요소를 가리켜요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s0-index | 조건 | 공백f=r은0아니어도되고개수모듈러차이다. | 공백은 front=rear이면 0번이 아니어도 돼요. 원소 수는 (rear-front+MAX_QUEUE_SIZE)%MAX_QUEUE_SIZE예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s0-state | 일반 | 한빈칸으로공백포화분리한다. | 한 칸을 비워야 두 인덱스로 공백과 포화를 구별해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s0-state | 조건 | 다음modM과용량M-1이다. | 다음 위치는 (index+1)%M이라 끝 다음 0으로 돌아가요. M칸 중 실제 용량은 M-1이고 마지막까지 채우면 front==rear로 공백과 같아져요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s0-ops | 일반 | 포화/공백검사후rear/front옮기고접근한다. | 넣을 때 rear를 먼저 옮기고, 꺼낼 때 front를 먼저 옮겨요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s0-ops | 일반 | 상수시간일정접근이다. | enqueue·dequeue는 일정한 인덱스 계산과 한 칸 접근만 하므로 O(1)이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s1-linked | 일반 | 실제front첫rear끝,공백둘NULL,끝연산O1이다. | 연결 큐는 앞과 뒤 노드를 포인터로 기억해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s1-linked | 조건 | 첫삽입front함께,마지막삭제rearNULL,우회후해제다. | 공백 삽입은 front도 새 노드로 정하고 rear를 갱신해요. 삭제는 옛 front를 보관하고 다음으로 옮긴 뒤 해제하며, 마지막이면 rear도 NULL로 맞춰요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s1-linked | 구분 | 원형front직전인덱스와연결front실노드차이다. | 연결 큐 front는 실제 첫 노드로, 원형 배열의 첫 요소 하나 앞 인덱스와 의미가 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s1-deque | 일반 | 양끝삽입삭제와이중링크O1이다. | 덱은 양 끝에서 넣고 꺼내요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s1-deque | 구분 | 양끝조회는삭제없음,headtail이중연결구현채택이다. | add_front·add_rear는 삽입, delete_front·delete_rear는 삭제·반환, get_front·get_rear는 삭제 없는 조회예요. 수업은 head·tail을 둔 이중 연결 구현을 사용해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s1-add | 일반 | 새연결후머리꼬리이동이다. | 새 노드의 연결을 만든 다음 머리나 꼬리를 옮겨요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s1-add | 조건 | create인자leftdata right,빈경우양끝함께와비공백양방향연결이다. | create_node(left,item,right)로 두 링크를 정해요. 공백이면 head·tail을 모두 새 노드로, 비공백이면 옛 이웃의 반대 링크도 이은 뒤 해당 끝 포인터를 옮겨요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s1-delete | 일반 | 노드와값보관후연결변경해제다. | 삭제할 노드를 보관하고 값을 읽은 뒤 연결을 바꿔 해제해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s1-delete | 주의 | 마지막양끝NULL아니면headllinkNULL,error중단전제다. | 삭제 후 head가 NULL이면 tail도 NULL, 아니면 새 head->llink를 NULL로 정해요. 공백 error()가 중단해야 안전하며 복귀하면 미초기화 item 반환 문제가 있어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s1-delete | 구분 | element는호출결과타입이지함수변수아니다. | element는 함수 호출 결과의 자료형이며 함수 자체가 변수라는 뜻은 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s2-lock | 일반 | 버퍼생산소비속도차이와lock권한이다. | 큐가 생산과 소비의 속도 차이를 흡수하고 접근을 조정해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s2-lock | 조건 | 생산full아닐때소비empty아닐때,lock해제관리다. | 생산자는 비포화 때 enqueue, 소비자는 비공백 때 dequeue하고 공유 갱신은 lock으로 권한을 얻어 작업 뒤 unlock해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s2-lock | 주의 | whilelockSUCCESS모호해실행가능잠금코드아니다. | 슬라이드 while(lock(buffer)==SUCCESS);는 구두 설명과 맞지 않고 성공·실패·동시성 보장이 불명확해 실행 가능한 C 잠금 구현으로 쓰지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s2-simulation | 일반 | 구두평균은서비스시작한3명대기합8/3이다. | 구두 예시에서는 세 고객의 서비스 시작 시점 대기를 평균 냈어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s2-simulation | 주의 | 대기시작-도착,완료아님;구술시각과p22코드차이이다. | 대기는 서비스 시작-도착 시각이며 평균 대상은 완료한 고객이 아닌 시작한 3명이에요. 구술 시작 1·4·9와 p22 코드의 1·5·11은 달라 2.67을 코드 실행 결과로 단정하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s2-code | 일반 | 시계틱도착서비스검사한다. | 시계를 늘리며 도착과 서비스 상태를 검사해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1015_Queue.html#s2-code | 주의 | ifelse감소0같은틱새시작없고빈반환미확정,시험범위확정아니다. | if/else 때문에 service_time이 막 0이 된 틱에는 다음 고객을 꺼내지 않아요. 빈 큐 remove_customer 반환은 발췌로 확정할 수 없고, 연습문제·코드 언급은 새 시험 범위 확정이 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1015_Queue.html#s3-cheatsheet | 구조 | 기존요약·예고·링크화면구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1015_Queue.html#s3-next | 구조 | 기존요약·예고·링크화면구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1015_Queue.html#s3-links | 구조 | 기존요약·예고·링크화면구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
