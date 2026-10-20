# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_0921_ArrayStructureList.html#p1 | 일반 | 행열원소수곱하기int크기800이다. | 행×열×int 크기 = 800 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p1 | 주의 | 4바이트문제전제,행포인터추가없다. | 문제의 int=4바이트 가정에서 10×20×4=800바이트, 정답 (4)예요. 실제 2차원 배열은 int**처럼 행 포인터가 추가되지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p2 | 일반 | 첫1,이전원소두배로생성한다. | two[0]=1, 이전 원소×2 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p2 | 주의 | 유효범위0..9,생성1..9,출력1..512,^XOR다. | two[0]=1 뒤 i=1..9에서 two[i]=2*two[i-1]로 채워 1,2,4,8,16,32,64,128,256,512를 출력해요. i=0의 이전 칸은 범위 밖이고 ^는 거듭제곱이 아닌 XOR예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p3 | 일반 | name문자배열 age정수 salaryfloat멤버이다. | char name[], int age, float salary | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p3 | 주의 | 크기100은선택,널포함99바이트문자,선언세미콜론필요다. | name[100]은 길이가 지정되지 않은 문제의 설계 선택으로 최대 99바이트와 종료 널을 담아요. 구조체 선언 끝에는 세미콜론이 필요해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p4 | 일반 | typedef후c1,c2별도선언한다. | typedef 별명 뒤 변수 c1,c2 선언 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p4 | 일반 | 두필드float이며typedef만으로객체생성안된다. | typedef struct { float real; float imaginary; } complex;로 별명을 붙인 뒤 complex c1,c2;로 객체를 따로 만들어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p5 | 일반 | 비영행우선7개삼중항,3t공간조건이다. | 삼중항 t개는 3t개 정수를 쓰므로 3t < 행수 × 열수일 때만 전체 배열보다 작아요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p5 | 조건 | 공간조건은행렬크기부가정보제외이다. | 3t<행수×열수는 행렬 크기 부가정보를 제외한 비교이며, 이 예는 9개 정수와 21개 정수라 전체 배열이 더 작아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p6 | 일반 | 하노이7이동과역할교환점화식기저있다. | (a) 1:A→C, 2:A→B, 1:C→B, 3:A→C, 1:B→A, 2:B→C, 1:A→C (b) T(1)=1, T(n)=2T(n-1)+1, T(3)=7. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p6 | 주의 | n>=1,막대는고정이름아닌현재역할이다. | n≥1에서 from·tmp·to는 고정된 막대 이름이 아니라 현재 호출의 출발·임시·도착 역할이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p7 | 일반 | degree-i공식과1001계수대2항공간비교이다. | (a) 10x^5+6x+3, coef[4]는 1차 항 (b) 모든 차수 배열 1001개 계수 vs 쌍 방식 2개 항. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p7 | 주의 | 쌍2개는계수차수각2개이고예제MAX_DEGREE6이상이다. | 예제 MAX_DEGREE는 6 이상이며, 쌍 방식의 2개 항은 계수 2개와 차수 2개를 함께 저장한다는 뜻이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p8 | 일반 | 자체참조태그포인터,arrow멤버접근,값멤버무한크기이다. | (a) struct ListNode *link;, p->data, p->link (b) 값 포함 시 무한 중첩으로 크기 결정 불가. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p8 | 주의 | 유효p전제,포인터선언은다음노드할당아니다. | p는 유효한 노드를 가리킨다고 가정해요. link 포인터 멤버를 선언해도 다음 노드가 자동으로 할당되지는 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p9 | 일반 | 객체연산계약과주소1036범위확인있다. | (a) 객체는 인덱스와 요소 쌍의 집합, create(6)은 6개 요소 생성, store는 2번에 7 저장, retrieve는 7 반환 (b) 주소 1000 + 9×4 = 1036, 0<=2<3·0<=1<4로 유효. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p10 | 일반 | 큰쪽소비같으면둘소비,정확답과차수별복잡도이다. | 차수가 큰 쪽만 소비하고 같을 때만 양쪽을 합산·소비하는 병합(merge) 구조로 선형 시간에 덧셈해요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0921_ArrayStructureList.html#p10 | 주의 | 같은차수합0도양쪽전진하고D와m,n다른입력척도다. | 합 0을 저장하지 않아도 양쪽 인덱스는 전진해요. O(D+1)의 D는 최고차수, O(m+n)의 m,n은 입력 항 수라 서로 다른 척도예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0921_ArrayStructureList.html#p11 | 일반 | 배열포함값복사와독립객체,전체비교금지필드비교이다. | (a) b=a 가능, name 배열도 복사되며 b.age 수정 시 a.age는 유지됨 (b) a>b 불가, a.age>b.age로 비교. | pass | pass / 기존 충족, 수정 없음 |
| 복습문제_0921_ArrayStructureList.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_0921_ArrayStructureList.html#s0-recursion-rules | 일반 | 축소와 즉답하는 기저 조건이 필요하다. | 순환은 호출마다 문제가 줄어들어야 하고, 바로 답을 내는 바닥 조건이 있어야 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s0-recursion-rules | 주의 | 피보나치 재귀의 반복계산이 DP 동기다. | fib(6)에서 fib(3)을 3번 계산하듯 중복 호출이 생기면, 계산 결과를 기억해 재사용하는 다이내믹 프로그래밍을 생각해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s0-hanoi-logic | 일반 | 작은문제로 로직 세워 n으로 일반화한다. | 원반 세 개로 로직을 세운 뒤, 위의 n−1개를 옮겼다고 가정해 n개로 일반화해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s0-hanoi-logic | 조건 | 한번맨위하나,작은위큰금지;기저1과두번n-1인자역할이다. | 한 번에 맨 위 한 개만 옮기고 작은 원판 위에 큰 원판은 놓지 않아요. n==1은 from→to로 옮기고, 그 외 (n-1,from,to,tmp) → 큰 원판 from→to → (n-1,tmp,from,to) 순서예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s0-hanoi-trace | 일반 | 가장왼말단첫출력,바닥에서복귀하며스택보존이다. | hanoi_tower(4, A, B, C)는 가장 왼쪽 말단부터 출력하며, 바닥을 치면 돌아서 위로 올라가요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s0-hanoi-trace | 일반 | n4총15회,큰4는8번째,첫이동1A→B이다. | n=4는 총 15회 이동하며 처음은 원판1 A→B, 8번째는 가장 큰 원판4 A→C예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s0-hanoi-trace | 보충 | 출력순서 이유는 수업유도않은보충이다. | 보충(수업에서 유도하지 않음): 각 호출은 첫 호출의 모든 출력 → 자기 출력 → 두 번째 호출의 모든 출력 순서라 가장 왼쪽 말단부터 나와요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s1-array-why | 일반 | 동형변수묶음과인덱스직접접근이다. | 배열은 같은 형의 변수를 함께 다니게 묶은 것이고, 가장 큰 장점은 인덱스로 곧장 가는 빠른 액세스예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s1-array-why | 일반 | C0기반,최대탐색은첫원소시작이후갱신이다. | C 인덱스는 0부터라 다섯 번째는 A[4]예요. 최댓값은 score[0]으로 시작해 i=1..n-1에서 더 큰 값으로 갱신해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s1-array-adt | 일반 | 객체와연산의ADT,배열객체는인덱스요소쌍이다. | ADT는 객체와 연산으로 정의하고, 배열 ADT의 객체는 <인덱스, 요소> 쌍의 집합이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s1-array-adt | 일반 | create생성 retrieve반환 store저장 계약이다. | create(n)은 n개 요소 배열 생성, retrieve(A,i)는 i 위치 값 반환, store(A,i,item)은 그 위치에 저장하는 연산이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s1-array-adt | 구분 | 내부구현과필요연산선택은설계자몫이다. | 연산의 기능을 정하되 몸체 구현과 필요한 추가 연산은 프로그래머가 정해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s1-array-memory | 일반 | 연속배치로base+i*sizeof 직접주소,2D는rowmajor다. | 배열 요소는 base address부터 빈틈없이 붙어 있어서, 곱하고 더하는 계산만으로 주소를 바로 찾아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s1-array-memory | 일반 | 2D행순서배치이다. | 2차원 배열을 0행, 1행, … 순서로 한 줄로 놓는 방식 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s1-array-memory | 조건 | 유효0..n-1이며필요크기연속공간과sizeof바이트단위다. | 인덱스는 0..n-1이고 sizeof는 바이트 크기예요. int가 4바이트이면 A[6]은 연속 24바이트, A[3][4]는 연속 48바이트예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-method1 | 일반 | 0계수포함배열이며차수degree-i이다. | 방법 #1은 0인 항까지 모든 차수의 계수를 배열 하나에 저장하고, 차수는 인덱스로 계산해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-method1 | 구분 | degree와coef를구조체로묶고0저장공간과연산단순성교환이다. | degree와 coef를 polynomial 구조체로 묶어요. 모든 차수를 저장하면 연산은 단순하지만 0이 많을수록 공간을 낭비해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-add1 | 일반 | 큰차수복사,같으면합;실제dense는상수항에서함께끝난다. | 방법 #1 덧셈은 두 차수를 비교해 큰 쪽을 복사하거나 같으면 더해요. 교수님은 후처리가 필요하다고 했지만, 이 루프는 두 다항식이 상수항에서 함께 끝나서 후처리는 안전장치예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-add1 | 조건 | 큰쪽만전진,같으면둘다전진,AND조건한쪽끝정지다. | AND 조건에서 두 입력이 범위 안일 때 비교하며, 큰 차수 쪽만 복사·전진하고 같을 때 두 계수를 더해 양쪽을 전진해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-add1 | 보충 | 수업외후처리와결과차수이다. | 보충(수업에서 유도하지 않음): 남은 A·B 항을 C 끝으로 옮기는 후처리를 두고 C.degree는 두 입력 degree의 큰 값으로 정해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-method2 | 일반 | 비영계수차수쌍공유배열avail다음빈칸이다. | 방법 #2는 0이 아닌 항만 (계수, 차수) 쌍으로 배열 하나에 이어 저장하고, 결과는 avail 자리부터 붙여요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-method2 | 구분 | 0이많으면메모리절약연산복잡해진다. | 0이 많으면 메모리를 아끼지만 지수도 저장해야 하고 연산 구현은 복잡해지는 트레이드오프예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-add2 | 일반 | 순차루프는합산하여O(n),줄수아닌시간공간기준이다. | 프로그램 3.3은 코드가 길어도 루프가 차례로 놓여 있어서 방법 #1과 같은 오더로 돌아가요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-add2 | 일반 | 큰항붙임같으면합0제외,입력진전남은항복사와CsCe설정이다. | 큰 차수 항을 붙이고 같으면 계수를 합하되 합 0은 저장하지 않아요. 한쪽 종료 뒤 남은 항을 복사하며 Cs=시작 avail, Ce=완료 avail-1이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s2-poly-add2 | 구분 | 고차희소#2,낮은밀집#1이선택조건이다. | 고차이고 0이 많으면 방법 #2, 0이 거의 없는 낮은 차수면 방법 #1이 알맞을 수 있어요. 줄 수가 아닌 시간·공간으로 판단해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s3-sparse-full | 일반 | 전체배열은간단하지만대부분0인희소행렬공간낭비다. | 행렬을 2차원 배열에 전부 저장하면 연산은 간단하지만, 희소 행렬에서는 메모리 낭비가 커요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s3-sparse-triple | 일반 | 비영삼중항이희소일때메모리절감,연산복잡증가다. | 0이 아닌 요소만 (행, 열, 값)으로 저장하면 희소 행렬의 메모리를 아끼지만, 행렬 연산 구현은 복잡해져요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s3-sparse-triple | 주의 | 항7개는정수21개로A는오히려9→21 증가다. | 항 7개는 삼중항 21칸이에요. B는 36→21칸으로 줄지만 0이 적은 A는 9→21칸으로 늘어 희소 조건을 확인해야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s4-struct | 일반 | 이형필드묶고typedef별명으로struct생략이다. | 구조체는 타입이 다른 필드를 한 덩어리로 묶고, typedef로 별명을 붙이면 struct 없이 쓸 수 있어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s4-struct | 구분 | 배열동형과구조체이형,태그별명구분이다. | 배열은 같은 타입끼리 묶어요. 태그만 있으면 struct person a;, typedef 별명 person이 있으면 person a;로 선언해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s4-struct-assign | 일반 | 동형구조체대입가능전체비교불가필드선택이다. | 같은 타입의 구조체는 b = a;로 통째로 대입할 수 있지만, 비교는 a.age > b.age처럼 필드를 골라야 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s4-self-ref | 일반 | 동형구조체가리키는포인터필드이다. | 자체 참조 구조체는 자기와 같은 모양의 구조체를 가리키는 포인터 필드를 가진 구조체예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0921_ArrayStructureList.html#s4-self-ref | 구분 | 자체참조구조체는순환호출과다른개념이다. | struct ListNode *link는 같은 타입 노드의 주소를 담는 필드이며, 함수가 자신을 부르는 순환 호출과는 다른 개념이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0921_ArrayStructureList.html#s5-cheatsheet | 구조 | 기존요약표·예고·링크 구조를유지한다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0921_ArrayStructureList.html#s5-next | 구조 | 기존요약표·예고·링크 구조를유지한다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0921_ArrayStructureList.html#s5-links | 구조 | 기존요약표·예고·링크 구조를유지한다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
