# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_0917_Recursion.html#p1 | 일반 | j=0반환i,아니면gcd(j,i%j)이다. | j=0 종료, 아니면 gcd(j,i%j) | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p1 | 주의 | j검사전나머지는%0오류,양의입력과 변환성공전제다. | 양의 int와 입력 변환 성공을 가정하고 j==0을 나머지 계산보다 먼저 검사해 %0을 막아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p1 | 일반 | 공약수보존과 두번째인자감소가 정확성과 종료근거다. | (48,18)→(18,12)→(12,6)→(6,0)에서 6이며, 공약수 집합을 보존하고 두 번째 인자가 줄어 종료해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p2 | 일반 | 재귀먼저 n/2를 출력하고 n%2를 나중에 찍어10→1010,0→0이다. | n>=2이면 dec_to_bin(n/2) 호출 후 printf("%d",n%2). 10→1010, 0→0. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p2 | 주의 | 범위0이상int이며0에서조기리턴하면빈출력이다. | 입력은 0 이상의 int이며 음수는 범위 밖이에요. n==0에서 바로 리턴하면 0 한 자리가 사라져요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p3 | 일반 | 출력열10,7,4,1,-2 최종반환3이다. | 출력 10,7,4,1,−2 / 반환 3 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p3 | 조건 | printf는검사전,+1은복귀후이므로 -2도출력 n1도한번더호출한다. | printf가 검사 전이라 -2도 출력하고, n=1은 n<1이 아니어서 더 호출해요. 반환은 바닥 -1에 복귀 때마다 1을 더해 3이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p4 | 일반 | 0부터1..n을누적해자기호출제거한다. | 0에서 1..n 누적, 호출 제거 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p4 | 조건 | 원래정의양의n,합과i++범위유지전제다. | 양의 n에서 i=1..n을 한 번씩 더하며, 합과 i++가 int 범위를 넘지 않는 입력을 가정해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p4 | 일반 | 불변식과n4=10이원래와같음을보인다. | 매 i 뒤 total=1+…+i이고 n=4에서 10으로 원래 순환과 같아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p5 | 일반 | 홀수식/호출열/반환/Ologn대On모두있다. | (a) x * power(x * x, (n - 1) / 2), 호출 (2, 5) → (4, 2) → (16, 1) → (256, 0), 반환 1 → 16 → 16 → 32 (b) power: $O(\log n)$, slow_power: $O(n)$. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p5 | 주의 | n>=0,double범위전제,n0종료,짝수밑제곱필수다. | n≥0·중간 계산은 double 범위 안을 가정하고 n==0에서 1로 종료해요. 짝수 분기도 반드시 밑 x*x를 넘겨요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p6 | 일반 | 중복미저장원인,8결과,3호출,세대입순서있다. | (a) fib(6) = 8, fib(3) 호출 3회 (하위 호출 중복·미저장) (b) tmp = current; current += last; last = tmp; | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p6 | 주의 | F3값2와호출수3 구별,갱신전lastF(i-2),currentF(i-1)이다. | 갱신 전 last=F(i-2)·current=F(i-1)이며 옛 current를 보존해 다음 두 항으로 옮겨요. F(3)의 값 2와 fib(3) 호출 3회를 구별해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p7 | 일반 | 나머지로줄이는유클리드법이다. | 나머지로 줄이는 유클리드 호제법 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0917_Recursion.html#p7 | 조건 | 양의x,y만유효,y0은%0,공약수보존과r<y로종료다. | 양의 x,y에서 공약수 집합을 보존하는 (y,x%y)로 바꾸고 0≤나머지<y라 종료하며, 나머지 0이면 y를 반환해요. y=0 입력은 %0이므로 유효하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0917_Recursion.html#p7 | 일반 | 실제결과GCD6이다. | foo(48,18)은 (18,12)→(12,6)에서 6을 반환하므로 최대공약수 GCD 함수예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 복습문제_0917_Recursion.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_0917_Recursion.html#s0-factorial | 일반 | 순환은 중간 곱셈을 스택에 보존하고 복귀하며 계산한다. | 순환 호출은 곱할 값을 내부 스택에 쌓았다가 종결 조건에서 되돌아오며 곱을 완성해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s0-factorial | 조건 | n<=1 기저1,n-1 호출로 감소한다. | n<=1이면 1을 반환하고 그 외 n*factorial(n-1)로 줄이며, factorial(5)는 돌아오며 120을 만들어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s0-structure | 일반 | 종료와 그 조건으로의 수렴이 둘 다 필요하다. | 순환 알고리즘에는 순환을 멈추는 부분이 있어야 하고, 순환 호출을 하는 부분은 그쪽으로 수렴해야 해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s0-structure | 주의 | 항상 수 감소가 본질인 것은 아니며 종료가 큰 쪽이면 증가도 가능하다. | n-1·n-2·n/2처럼 줄여도 되고, 종료 조건이 큰 쪽에 있으면 증가해도 돼요. 핵심은 종료 조건 도달 보장이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s1-vs-iter | 일반 | 자기 호출과 for/while 반복을 구별하고 대부분 변환 가능하다. | 되풀이는 순환과 반복 두 가지이고, 대부분의 순환은 반복으로 바꿀 수 있어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s1-vs-iter | 일반 | 재귀는 스택 오버헤드가 있다. | 내부 스택에 호출을 쌓았다 꺼내는 데 드는 부담이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s1-vs-iter | 구분 | 반복은 호출 부담이 없으나 하노이 같은 문제는 작성이 어려워진다. | 반복은 호출 오버헤드가 없지만, 하노이처럼 순환적인 문제는 반복으로 작성하기 어려울 수 있어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s1-fact-iter | 일반 | n번 상수 비용 반복이 O(n),빅오는 저차항과 계수 생략이다. | 반복문이 $n$번 돌면 $O(n)$이고, 꼬랑지와 계수를 떼 최고차항의 차수만 빅오로 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s1-fact-iter | 일반 | v1,k n..1 감소 누적 곱이 구현 원리다. | v=1에서 시작해 k=n부터 k>0 동안 v=v*k, k--를 반복하고 v를 반환해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s2-power | 일반 | 짝수/홀수 항등식으로 지수를 절반으로 줄이고 반복은 n곱셈이다. | slow_power는 곱셈을 n번 하고, power는 짝수·홀수로 나눠 n을 반씩 줄여요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s2-power | 조건 | n=0이면1이고 홀수는 x를 곱해 재귀 반환을 완성한다. | n==0이면 1, 짝수는 power(x*x,n/2), 홀수는 x*power(x*x,(n-1)/2)를 반환해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s2-power | 보충 | 2,10 추적은 수업에서 하지 않은 예시다. | 수업 밖 추적: power(2,10)은 호출 5번으로 1024를 구하고 slow_power는 10번 곱해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s2-power-analysis | 일반 | 한 호출씩 지수를 절반 감소시켜 깊이가 logn이다. | power는 n을 반씩 줄여 호출 깊이가 log n이라 O(log n)이고, 코드 줄 수는 복잡도와 상관없어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s2-power-analysis | 주의 | 루프가 보이지 않아도 재귀 깊이를 세야 한다. | for가 없다고 O(1)이라 하지 말고 재귀 호출 횟수와 제어 구조를 확인해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s2-power-analysis | 주의 | 수업 구술 수치와 슬라이드 실측 수치가 다르다. | 슬라이드의 실측 비교는 slow_power 7.17초·power 0.47초이며 수업에서 읽은 수치와 구별해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s3-fib-rec | 일반 | 기저는0→0,1→1이다. | n이 0이면 0, 1이면 1을 바로 돌려주고 순환 호출을 멈추는 부분 | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s3-fib-rec | 주의 | 두 자식 n-1,n-2로 감소해 더하나 중복 탓 비효율 가능하다. | n≥2에서는 fib(n-1)+fib(n-2)로 두 인자를 줄여 더하지만, 같은 항의 중복 호출로 더 느려질 수 있어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s3-fib-waste | 일반 | 메모 없이 중복 계산하며 테이블에서 찾으면 가지가 중단된다. | 순환 피보나치는 같은 항을 여러 번 다시 계산하고, 다이내믹 프로그래밍은 테이블에서 먼저 찾아 가지를 끊어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s3-fib-waste | 보충 | 보이는 부분 트리와 전체 호출 횟수를 구별한다. | 슬라이드 부분 트리와 전체 트리를 구별해요. 슬라이드 밖 전체 추적의 fib(6)은 호출 25회이고 fib(3)은 3회예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s3-fib-iter | 일반 | 이전 두 항만 보존해 단일 n회 루프로 O(n)이다. | 지금 값과 바로 전 값만 들고 for 루프를 한 번 돌아서 피보나치를 구해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s3-fib-iter | 조건 | n<2반환,이전 current저장후 합,last갱신 순서다. | n<2이면 n을 반환하고, 그 외 last=0·current=1에서 tmp=current; current+=last; last=tmp; 순으로 갱신해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s4-hanoi-rule | 일반 | A의 n원판을 C로 옮기는 문제다. | 하노이 탑은 규칙을 지키며 막대 A의 원판 n개를 막대 C로 옮기는 문제예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s4-hanoi-rule | 조건 | 한번에 맨위한개,작은위큰금지,B임시 사용에도 제약을 지킨다. | 한 번에 맨 위 원판 한 개만 옮기고 작은 원판 위에 큰 원판을 놓지 않으며, 임시 막대 B에서도 이 규칙을 지켜요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s4-hanoi-3 | 일반 | 3개7이동,가장큰것 이동뒤2개문제로 감소한다. | 원판 3개는 7번에 옮겨지고, 가장 큰 원판이 C에 놓이면 원판 2개 문제로 줄어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s4-hanoi-3 | 일반 | 작은2개 A→B,큰 A→C,작은 B→C로 역할 변화한다. | 작은 2개 A→B, 큰 원판 A→C, 작은 2개 B→C로 나누며 소스·타깃·임시 막대 역할이 바뀌어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s4-hanoi-general | 일반 | 크기n-1 순환을 두번 사용한다. | 가장 큰 원판을 뺀 n-1개를 옮기는 일을 같은 함수의 순환 호출로 두 번 맡겨요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0917_Recursion.html#s4-hanoi-general | 조건 | 기저1 직접이동,재귀인자 역할 순서다. | n==1은 from→to 직접 이동하고, 그 외 (n-1,from,to,tmp) 호출 → 큰 원판 from→to → (n-1,tmp,from,to) 호출 순서예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s4-hanoi-general | 보충 | 자리순서 설명과 점화식은 수업에서 유도하지 않은 보충이다. | 보충(수업에서 유도하지 않음): 인자 자리는 출발·임시·도착이며, 이동 횟수 T(1)=1, T(n)=2T(n-1)+1에서 T(n)=2ⁿ-1이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0917_Recursion.html#s5-cheatsheet | 구조 | 기존 요약·예고·링크 화면은 별도 요약을 만들지 않는다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0917_Recursion.html#s5-next | 구조 | 기존 요약·예고·링크 화면은 별도 요약을 만들지 않는다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0917_Recursion.html#s5-links | 구조 | 기존 요약·예고·링크 화면은 별도 요약을 만들지 않는다. | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
