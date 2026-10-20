# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_1012_Queue.html#p1 | 일반 | push9pop8결과31잔류이다. | push 9,pop 8,결과 31 남음 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p1 | 조건 | 피연산자5결과4push,4연산각2pop,최종추가pop금지다. | 피연산자 5개와 연산 결과 4개가 push 9회, 연산자 4개의 두 값 읽기가 pop 8회예요. 계산용 스택만 세고 최종 결과를 추가 pop하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p2 | 일반 | 두소문제값25와31이다. | (1) 후위식 값25 / (2) 표 최종31 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p2 | 주의 | 입력별개이고1변환정확형식과좌결합이다. | (1)은 2 4 + 7 * 6 3 * − 1 +로 25, (2)는 별도 토큰 5 6 * 4 2 / + 1 −로 31이에요. 두 입력을 섞지 말고 같은 우선순위는 좌결합을 지켜요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p3 | 일반 | 최근열린순괄호스택이다. | 최근 열린 괄호 먼저 닫기 → 스택 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p3 | 조건 | 여는push닫는비었거나다름실패끝남아도실패이다. | 여는 괄호는 push하고 닫을 때 빈 스택·종류 불일치이면 실패해요. 끝에 남아도 실패하며, 개수가 같아도 ([)]처럼 잘못될 수 있어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p4 | 일반 | 선증가저장,읽기감소,문자수변환결과push이다. | ++top 저장, top 읽고--, digit 변환·연산 결과 push | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p4 | 주의 | 99이하유효숫자+*무공백,int중간범위,원오류보장아니다. | 길이≤99·무공백·한 자리 숫자와 +,*의 올바른 식이며 중간값은 int 범위라는 전제예요. scanf 폭 제한과 공백 오류 종료는 별도 보완이고 원문 자체의 보장이 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p4 | 구분 | 23+4*최종20main마지막pop하여앞횟수조건과다르다. | 23+4*는 20을 구하고 main에서 마지막 pop으로 출력해요. 최종 값을 남기는 앞 문항과 횟수 조건이 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p5 | 일반 | 세dequeue후4050이다. | 세 dequeue → [40,50] | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p5 | 일반 | front에서102030순삭제와길이2다. | FIFO로 front의 10,20,30을 차례로 제거해 40,50 두 개가 남아요. rear에서 빼는 스택 순서와 구별해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p6 | 일반 | 새여는번호push닫는짝pop이다. | 열면 새 번호 push, 닫으면 짝 번호 pop | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p6 | 주의 | counter닫을때감소금지,둘째예제불균형미닫힘4있다. | 번호 counter는 여는 때만 증가하고 닫을 때 줄이지 않아요. ((((()는 1 2 3 4 5 5를 출력해도 미닫힌 1..4가 남으므로 균형식은 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p7 | 일반 | ++top과top--식값차이,역전둘다-1접근이다. | push는 ++(s->top)으로 선증가 후 저장, pop은 (s->top)--로 선읽기 후 감소해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p7 | 주의 | 후위갱신을문장종료까지미룬다고말하면안된다. | 후위 연산은 식의 평가값이 갱신 전 값이라는 뜻이지, 문장 전체가 끝날 때까지 변수 갱신을 안 한다는 뜻은 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p8 | 일반 | push새연결먼저,pop값연결변경후free이다. | temp->link = s->top;을 먼저 수행해 기존 리스트를 보존하고, pop에서는 값·포인터 갱신 후 free(temp)를 호출해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p8 | 일반 | 역전N자기참조,조기free접근오류이다. | 순서 역전 시 N->link = N 자기 참조, 조기 free 시 해제 후 접근 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p9 | 일반 | op2먼저,한자리변환,82/3-결과1,공백다자리미지원다. | 숫자 문자는 ch - '0'으로 변환해 push하고, 연산자에서는 먼저 꺼낸 값이 오른쪽 피연산자 op2예요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p9 | 주의 | 보이는switch는부분코드다. | 표시된 switch는 뺄셈·나눗셈 부분만이고 전체 eval에는 +와 * 처리도 있어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p10 | 일반 | 최종24와pop순서이다. | 스택 추적 최종24, pop 순서 주의 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p10 | 일반 | 상태7,76,762,73,4,45,454,420,24와firstopsecond다. | 토큰 뒤 스택은 [7]→[7,6]→[7,6,2]→[7,3]→[4]→[4,5]→[4,5,4]→[4,20]→[24]예요. 둘째 pop을 왼쪽으로 두어 first op second를 계산해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p11 | 일반 | 최근두피연산결합스택이다. | 후위식 최근 두 값 결합 → 스택 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p11 | 일반 | 부분식결과다시push,큐와차이다. | 계산한 부분식도 한 피연산자로 다시 push해요. 2 3 + 4 *는 5를 쌓은 뒤 4와 곱해 20이며, 큐처럼 오래된 값부터 꺼내지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p12 | 일반 | 도착순서은행큐이다. | 은행 도착 순서 유지 → 큐 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p12 | 조건 | rear대기front서비스와정책범위이다. | rear에 도착하고 front에서 서비스하므로 A,B,C는 같은 순서로 나가요. 별도 우선순위 고객 정책은 원문에 없어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_1012_Queue.html#p13 | 일반 | 스택LIFO라전체X이다. | 스택은 LIFO → 전체 X | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_1012_Queue.html#p13 | 구분 | 괄호검사는맞지만FIFO주장이틀렸다. | 스택의 괄호 검사 이용은 맞지만 FIFO라는 앞부분이 틀려 전체 X예요. A 뒤 B를 넣고 B부터 꺼내는 반례로 확인해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 복습문제_1012_Queue.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_1012_Queue.html#s0-array | 일반 | 배열과top묶고-1초기공백이다. | 배열과 top을 묶고 top을 -1로 두면 빈 스택이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s0-array | 조건 | 유효범위0..top,포화M-1,고정용량과배열지우기불필요다. | 배열은 지우지 않아도 0..top만 유효해요. 포화는 top==MAX_STACK_SIZE-1이고 용량은 배열 크기로 제한돼요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s0-pushpop | 일반 | push증가후저장,pop현재읽고감소,peek불변이다. | push는 top을 올리고 쓰며 pop은 현재 값을 읽고 top을 내려요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s0-pushpop | 주의 | fullpush반환,empty poppeek exit프로세스종료이다. | 포화 push는 오류 후 함수에서 돌아오고, 공백 pop·peek의 exit(1)은 루프가 아니라 프로세스를 종료해요. 검사 후에만 인덱스와 값을 다뤄요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s0-choice | 일반 | 입력상한알면배열,모르면연결고려다. | 입력 상한을 알면 배열, 가늠하기 어려우면 연결 스택을 고려해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s0-choice | 주의 | 연결무한아니며재귀내부반드시연결아니다. | 연결 스택도 가용 메모리 한계와 포인터·할당 관리가 있으며, 재귀 내부 스택이 반드시 연결 스택이라는 뜻은 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s0-node | 일반 | top은필드아닌첫노드구조체시작주소다. | top은 첫 StackNode의 시작 주소를 가리켜요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s0-node | 주의 | 초기NULL,끝linkNULL이며슬라이드오타교정이다. | 초기 top은 NULL이고 마지막 노드 link도 NULL이에요. 슬라이드 별칭 StackeNode는 후속 코드와 맞춰 StackNode로 바로잡았어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s0-linkedpush | 일반 | 새노드기존top연결후top수정이다. | 새 노드를 기존 top에 연결한 뒤 top을 새 노드로 바꿔요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s0-linkedpush | 조건 | 할당실패시변경안하고반환,역순자기참조위험이다. | malloc이 NULL이면 오류 후 돌아오고 성공하면 item 저장 → temp->link=s->top → s->top=temp 순서예요. top을 먼저 덮으면 기존 연결을 잃을 수 있어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s0-linkedpop | 일반 | 값대피,top이동후기존노드free다. | 첫 노드 값을 보관하고 top을 옮긴 뒤 기존 노드를 해제해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s0-linkedpop | 주의 | empty는topNULL,비면exit,해제후읽기금지다. | 연결 스택 공백은 top==NULL이며 비면 exit(1)로 종료해요. temp·item에 보관 → top 이동 → free(temp) → item 반환 순서로 해제 뒤 필드를 읽지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-brackets | 일반 | 가장최근열린같은종류부터닫는다. | 괄호는 가장 최근에 연 것부터 같은 종류로 닫아야 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-brackets | 조건 | 개수/순서/포함세조건이며개수만으로불충분다. | 개수가 같고 같은 종류의 왼쪽이 먼저 나오며 쌍은 교차 없이 포함돼야 해요. 개수만 세면 잘못된 포함 관계를 놓쳐요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-matching | 일반 | 닫는때공백/종류불일치실패다. | 닫는 괄호를 읽을 때 스택이 비거나 짝이 다르면 실패해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-matching | 조건 | 여는push,닫는검사pop,끝남은열림실패다. | 여는 괄호를 push하고 닫는 괄호에서 공백 검사 후 pop해 종류를 맞춰요. 끝나도 왼쪽 괄호가 남으면 실패예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-notation | 일반 | 중위/전위/후위구분과우선순위보존14이다. | 2+3*4는 후위 2 3 4 * +로 바꾸며 결과는 14예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-notation | 주의 | 모든컴파일러CPU의필수내부형식이아니다. | 여기 후위식 변환은 수업의 수식 처리 알고리즘이며, 모든 컴파일러·CPU가 반드시 후위 문자열로 바꾼다는 뜻은 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-eval | 일반 | 먼저오른쪽,다음왼쪽계산이다. | 먼저 꺼낸 수가 second이고 다음 수가 first라서 결과는 7이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-eval | 조건 | 숫자push,두값first op second결과push,전후개수조건이다. | 숫자를 push하고 연산자는 first op second 결과를 다시 push해요. 연산 전 값이 둘 미만이거나 끝에 여러 값이 남으면 정상 이항식이 아니에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-evalcode | 일반 | ch-0로숫자변환한다. | 숫자 문자는 0 문자를 빼서 한 자리 정수로 만들어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-evalcode | 주의 | op2후op1 pop계산push마지막pop,입력제한명시다. | op2부터 pop하고 op1을 꺼내 계산 결과를 push한 뒤 마지막 값을 반환해요. 한 자리 숫자 예제이며 공백·다자리·잘못된 문자·0 나눗셈 검사는 없어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-convert | 일반 | 피연산자바로출력,연산자우선순위스택다. | 피연산자는 바로 출력하고 연산자는 우선순위에 따라 꺼내요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-convert | 조건 | 높거나같으면pop해좌결합,+-*/대상,괄호경계자체미출력이다. | 스택 위 우선순위가 새 연산자보다 높거나 같으면 꺼내 +,-,*,/의 왼쪽 결합을 지켜요. (는 경계로 넣고 )에서는 (까지 꺼내되 괄호 자체는 출력하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-convertalgo | 일반 | 끝스택연산자모두출력이다. | 입력이 끝나면 스택의 남은 연산자 전부를 출력해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-convertalgo | 주의 | peek전공백검사보완과정상식끝왼괄호없다. | peek 전에 공백을 확인하고 왼쪽 괄호 경계에서 멈춰요. 이는 원 의사코드의 생략 단계를 명시한 것이며 정상 입력은 끝에 (가 남지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s1-maze | 일반 | 후보스택과출구종료이다. | 스택에는 다음 후보가 남고 출구에 닿으면 후보가 남아도 끝나요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s1-maze | 구분 | 방문표시재방문방지,후보없음실패,먼저볼후보나중push,물리경로아니다. | 방문 표시로 반복 방문을 막고 갈 수 있는 미방문 이웃을 넣어요. 후보가 없으면 실패하며 먼저 볼 곳을 나중에 push해요. 후보 스택은 실제 걸은 경로 기록과 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s2-fifo | 일반 | 앞dequeue뒤enqueue FIFO이다. | 큐는 먼저 들어온 요소를 앞에서 먼저 꺼내요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s2-fifo | 일반 | peek전단미삭제,create/init/is상태계약이다. | enqueue는 rear 삽입, dequeue는 front 삭제·반환, peek는 전단을 제거 없이 반환해요. create·init은 생성·초기화, is_empty·is_full은 상태 검사예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s2-buffer | 일반 | 생산소비속도차이순서대로대기한다. | 속도가 다른 두 작업 사이에서 큐가 데이터를 순서대로 기다리게 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s2-buffer | 조건 | 시뮬레이션사례만코드안배웠다. | 은행·공항의 대기 시뮬레이션은 실제 상황을 소프트웨어로 모의실험하는 예이며, 이번 수업에서 구체적 코드는 다루지 않았어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s2-linear | 일반 | rear끝이면앞빈칸있어도삽입안된다. | 선형 큐는 앞 칸이 비어도 뒤 인덱스가 끝에 이르면 삽입할 수 없어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s2-linear | 주의 | 앞당김복사비용,매연산필수아님,원형구상만이다. | 남은 원소를 앞당기면 빈칸을 재사용하지만 복사가 들어요. 대이동이 매 연산 필수라는 뜻은 아니며 원형의 순환 갱신식은 아직 다루지 않았어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s2-structure | 일반 | front첫요소하나전,rear마지막인덱스다. | 원형 큐는 front와 rear를 옮겨 배열의 빈자리를 다시 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_1012_Queue.html#s2-structure | 조건 | front0rear2AB에C추가rear3,A삭제front1,공백포화다음범위다. | front=0·rear=2에서 C를 넣으면 rear=3, A를 꺼내면 front=1이에요. front를 하나 앞에 두는 이유와 공백·포화·순환식은 다음 범위예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_1012_Queue.html#s3-cheatsheet | 구조 | 기존요약·예고·링크구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1012_Queue.html#s3-next | 구조 | 기존요약·예고·링크구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_1012_Queue.html#s3-links | 구조 | 기존요약·예고·링크구조 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
