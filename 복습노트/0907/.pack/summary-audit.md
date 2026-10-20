# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_0907_Intro_DS_Algorithms.html#p1 | 일반 | 옛 a를 temp에 먼저 보존하고 a←b,b←temp로 교환한다. | 임시 보관 → a에 b → b에 옛 a | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p1 | 주의 | a←b;b←a는 옛 a를 잃는다. | a←b 뒤 b←a를 쓰면 옛 a를 잃어 두 값이 같아져요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p1 | 일반 | 검산에서 옛 A,B가 최종 B,A로 바뀐다. | 옛 값이 A,B이면 최종 a=B,b=A예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p2 | 일반 | 양의 정수 n에 대해 0에서 시작해 1..n을 정확히 한 번씩 더한다. | 양의 정수 n에 대해 sum=0에서 1..n을 한 번씩 더해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p2 | 주의 | i<n은 마지막 n을 빼먹고 C에서는 정수 범위도 확인해야 한다. | i<n이면 n이 빠지고, C에서는 합의 타입 범위도 확인해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p2 | 일반 | n=4는 10이고 누적 불변식과 별도 합 공식으로 검산한다. | i까지 끝나면 sum=1+…+i이고, n=4에서 10으로 n(n+1)/2와 일치해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p3 | 일반 | rear에 넣고 front에서 꺼내는 FIFO라 ABCDE이다. | 뒤(rear)에 넣고 앞(front)에서 꺼내므로 (a) ABCDE예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p3 | 주의 | EDCBA는 스택이고 순서를 바꾼 나머지 보기는 FIFO를 위반한다. | E부터 꺼내는 LIFO와 달리 첫 삭제는 A이고 D는 E보다 먼저 나와요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p5 | 일반 | 데이터·자료구조·알고리즘과 설계·분석 및 품질 기준을 구별한다. | 데이터(재료)·자료구조(조직 구조)·알고리즘(유한한 명령의 순서), 설계(방법 고안)와 분석(비용 계산). | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p5 | 강조 | 순서가 달라지면 결과가 달라지고 유한 번에 끝나야 결과를 얻는다. | 순서가 바뀌면 결과가 달라지고 유한 번 안에 끝나야 결과를 얻어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p5 | 주의 | 짧은 코드라는 이유로 실행이 빠르다고 단정할 수 없다. | 코드 길이만으로 빠르기를 판단하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p6 | 일반 | 지역은 범위·수명이 제한되나 재귀 동시 호출마다 배열을 만들면 공간이 늘어난다. | (a) 지역 변수는 범위·수명을 제한하나 동시 재귀 호출마다 배열이 생기면 메모리가 늘 수 있음 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p6 | 일반 | 함수 분리는 읽기·재사용성, 포인터는 복사 절약과 변경 공유가 있다. | (b) 함수 분리는 가독성·재사용성 향상, 포인터 공유는 복사 절감·변경 전파 주의, unsigned int 크기는 동일, 미사용 90칸. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p6 | 주의 | int와 unsigned int의 크기는 같으며 100-10=90칸이 남는다. | unsigned int 크기는 동일, 미사용 90칸. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p7 | 일반 | 리스트·그래프·트리·스택·큐·사전은 순서·연결·계층·입출 순서·키 조회로 선택한다. | 리스트(선형 순서), 그래프(연결), 트리(계층), 스택(LIFO), 큐(FIFO), 사전(키→값). | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p7 | 주의 | 연결이 있다고 모두 트리는 아니므로 계층인지 확인한다. | 연결이 있다는 이유만으로 트리라 하지 말고 계층 관계인지 확인해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p4 | 보충 | 최대값 문항은 0914에서 분석한 후속 수업 보충이며 0907 평가 핵심에서 제외한다. | 후속 수업 보충(0914 분석): 0907 핵심 평가 범위에서는 제외해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0907_Intro_DS_Algorithms.html#p4 | 일반 | 첫 원소 초기화로 음수 배열 최대 -1을 구하며 0 초기화는 잘못된 0을 반환한다. | (a) tmp: -8 → -3 → -3 → -1, 반환값 -1 (b) tmp = 0이면 음수 배열에서 0 오반환, 1 <= n <= MAX 및 i 증가로 유한 종료. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0907_Intro_DS_Algorithms.html#p4 | 주의 | 1<=n<=MAX이고 앞 n개 값이 초기화되어야 하며 i가 증가해 n에 도달하므로 끝난다. | 1 <= n <= MAX이고 앞 n개 원소가 초기화되어야 하며, i가 1씩 증가해 n에 도달하므로 종료해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 복습문제_0907_Intro_DS_Algorithms.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-brick-wall | 일반 | 통나무·자갈·모래는 원재료 데이터이고 창틀·벽돌·골조는 조직된 자료구조다. | 데이터는 원재료이고 자료구조는 쓰기 좋게 짜 놓은 재료예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-brick-wall | 강조 | 자료구조와 알고리즘은 함께 있어야 좋은 프로그램이 된다. | 자료구조는 벽돌 같은 재료이고, 알고리즘은 벽돌을 지그재그로 쌓는 방법이라 둘이 함께 있어야 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-algorithm-def | 일반 | 계산·데이터 처리를 위한 유한한 명령어들의 순서가 알고리즘이다. | 알고리즘은 계산이나 데이터 처리를 위한, 순서가 있는 유한한 명령어들이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-algorithm-def | 강조 | 명령 순서가 결과에 영향을 주므로 반드시 순서가 있어야 한다. | 명령어에는 반드시 순서가 있어요 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-middle-language | 일반 | 프로그래밍 언어는 사람의 사고를 0과 1을 이해하는 기계에 전달하는 중간 언어다. | 기계는 0과 1밖에 몰라서, 프로그래밍 언어가 사람과 컴퓨터 사이의 중간 언어 역할을 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-middle-language | 강조 | 수업의 임베디드 분야 권고에서는 C/C++이 중요하다. | 하드웨어에 맞고 계산에 특화된 언어, 임베디드(embedded)에서 중요 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s0-middle-language | 일반 | 언어가 달라도 자료구조 콘셉트는 같고 구현 방법이 다르다. | 언어가 달라도 자료구조의 콘셉트는 같고 구현 방법이 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-fast-storage | 일반 | 문제 해결 방법의 설계 목표는 빠른 시간과 적은 메모리다. | 알고리즘은 문제 해결 방법을 빠르게(Fast), 메모리를 적게(Little storage) 쓰도록 고안하려고 배워요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-fast-storage | 주의 | 임베디드 자원 제한을 넘기면 프로그램을 실행할 수 없다. | 임베디드에서는 기기 자원 한도를 넘으면 프로그램이 돌아가지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-elegant-reuse | 강조 | elegant/simple/general 및 재사용성을 강조한다. | 소프트웨어는 elegant, simple, general하게 짜고, 무엇보다 재사용성을 살려야 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-elegant-reuse | 일반 | C stdio 및 Java API/Python 라이브러리는 작성된 기능 재사용 사례다. | 만들어 둔 코드를 다시 쓰는 성질 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-readability | 강조 | elegant의 목적은 가독성을 높이는 것이다. | elegant하게 짜는 진짜 목적은 가독성이고, 함수 호출로 계층을 나누면 10만 라인도 금방 읽혀요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-readability | 주의 | 중첩 제어 흐름은 읽는 부담을 키우고 이름이 드러나는 함수 계층이 흐름 이해를 돕는다. | 중첩 제어문은 흐름을 읽는 부담을 키우고, 함수 이름으로 단계를 드러내면 이해하기 쉬워요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-function-bag | 일반 | 함수 분리는 사용자 편의와 문제가 생긴 부분의 국소 수리를 돕는다. | 함수는 짐을 나눠 담는 파우치라서, 찾기 쉽고 고장 나도 그 부분만 고치면 돼요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-function-bag | 강조 | 개발 목표를 사용자 편의에 둔다. | 개발자가 아니라 쓰는 사람을 중심에 둔 개발 목표 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-function-bag | 일반 | 정리 비용과 탐색·유지 비용의 tradeoff가 있다. | 넣을 때 빠른 것과 찾고 유지할 때 빠른 것 사이의 맞바꿈 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-design-analysis | 일반 | 설계는 자료구조로 효율적인 방법을 만드는 일이다. | tricky한 자료구조로 효율적인 알고리즘을 만드는 일 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s1-design-analysis | 일반 | 분석은 주어진 방법의 계산 복잡도를 정량화한다. | 주어진 알고리즘의 계산 복잡도를 계산하는 일 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-logic-min | 일반 | 불 대수·K-map으로 게이트를 줄이고 P&R로 블록 배치와 배선을 최적화한다. | 논리회로의 minimization은 게이트와 면적을 줄여 빠르고 작게 만드는 노력이고, 같은 목표가 프로그래밍에도 있어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-logic-min | 일반 | 흡수식 X+XY=X가 슬라이드 예시다. | X + XY = X | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-logic-min | 일반 | K-map은 게이트 감소를 위한 시각화 도구다. | 게이트를 줄이기 위한 시각화 도구예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-variables | 일반 | 변수는 메모리 영역에 붙인 이름이며 필요한 만큼의 타입·배열 크기를 고른다. | 변수는 메모리 칸의 별명이고, 값에 맞는 타입을 필요한 크기만큼만 잡아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-variables | 주의 | unsigned int는 int와 크기가 같고 음수 대신 양의 표현 범위를 늘린다. | int와 크기가 같고, 음수 대신 양의 범위를 넓혀 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-variables | 일반 | short·float·double 표는 보통 크기를 설명한다. | 크기 표는 보통의 구현 기준이며, 본문에서 short는 보통 16비트·float는 32비트·double은 64비트로 비교해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-global-local | 강조 | 함수 내부 지역 변수는 함수가 리턴할 때 자원을 반납하므로 전역 사용을 줄인다. | 함수는 리턴할 때 자원을 반납하니, 글로벌 변수보다 로컬 변수를 많이 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-global-local | 일반 | 파라미터에 명시된 것을 접근하게 한다는 수업의 설계 권고다. | 열거된 파라미터만 함수 안에서 접근하게 하는 견고한 방법이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-global-local | 보충 | 수업에서 유도하지 않은 캡슐화: 데이터와 코드를 묶고 외부 직접 변경을 제한한다. | 보충(수업에서 유도하지 않음): 캡슐화는 데이터·코드를 묶어 바깥의 직접 변경을 제한해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-global-local | 보충 | C는 값 전달이므로 함수 매개변수 변경은 호출자 값 변경이 아니며 원본 수정은 주소 전달이 필요하다. | 보충: C의 값 전달은 복사본을 바꾸며, 호출자의 자료를 고치려면 주소를 넘겨야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-pointer | 일반 | 포인터는 복사 대신 하나의 자원을 공유하여 공간을 줄인다. | 포인터는 자료를 복사하지 않고 가리켜서 하나의 자원을 공유하게 해 공간을 줄여요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-pointer | 일반 | student 배열 이름은 주소로 사용한다는 본문 설명이다. | 배열 이름 student는 *가 없어도 주소예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s2-pointer | 주의 | 공유한 원본은 양쪽에서 변경할 수 있다. | 공유한 자료는 한쪽에서 고치면 같은 원본에 반영돼요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-list | 일반 | 리스트는 순서 있는 선형 데이터다. | 할 일 리스트처럼 순서가 있는 선형 데이터가 리스트예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-list | 일반 | 배열은 인덱스로, 연결 리스트는 노드 연결로 순서를 표현한다. | 배열은 인덱스, 연결 리스트는 노드의 연결로 순서를 나타내요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-graph-tree | 일반 | 지도 연결은 그래프, 조직도 계층은 트리다. | 위치와 연결성이 있는 지도는 그래프로, 조직도 같은 계층 구조는 트리로 나타내요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-graph-tree | 일반 | 트리의 뿌리 위치는 조직도의 맨 위에 대응한다. | 조직도를 뒤집었을 때 맨 위 사장 자리 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-queue-stack | 일반 | 큐는 들어온 순서를 지키고 스택은 맨 위부터 꺼낸다. | 매표소 줄처럼 들어온 순서대로 나가면 큐, 책더미처럼 맨 위부터 꺼내면 스택이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-queue-stack | 보충 | 수업 밖 A,B,C 추적에서 큐 ABC, 스택 CBA로 나온다. | 수업 밖 예시: A,B,C를 넣으면 큐는 A,B,C, 스택은 C,B,A로 나와요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0907_Intro_DS_Algorithms.html#s3-dictionary | 일반 | 사전은 인덱스로 원하는 낱말을 찾는 탐색 구조다. | 인덱스가 붙은 영어사전처럼 찾기 좋게 정리한 구조가 사전(탐색 구조)이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s4-cheatsheet | 구조 | 기존 한눈에 보기 화면은 다른 토픽 요약을 링크로 모은 화면이다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s4-next | 구조 | 다음 시간 예고는 아직 배우지 않은 범위의 목록이다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0907_Intro_DS_Algorithms.html#s4-links | 구조 | 복습문제로 가는 링크 화면이다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
