# 본문–요약 의미 감사

일반·강조·주의·보충의 핵심을 분리해 직접 대조했다. 예시 전체·반복 비유는 압축하며 요약표·예고·링크는 기존 구조를 유지한다.

| 자료·토픽 | 구분 | 본문 핵심 주장 | 실제 대응 요약 문장 | 보완 전 | 판정 / 생략 이유 |
|---|---|---|---|---|---|
| 문제설명_0928_ArrayStructureList.html#p1 | 일반 | 원소수타입크기곱해double80최대다. | 개수×타입 크기 → double[10] 80 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p1 | 조건 | 환경조건에서40,80,40,40이며모든C일반화안된다. | 이 팩의 int4·double8·char1·float4바이트 조건에서 40,80,40,40바이트로 정답 (2)예요. 다른 C 구현의 타입 크기는 다시 확인해야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p2 | 일반 | 같은복소성분합해구조체값반환한다. | 같은 성분끼리 합, 구조체 값 반환 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p2 | 주의 | 실수허수각합,호출자불변,지역주소반환금지다. | result.real=a.real+b.real, result.imag=a.imag+b.imag를 값으로 반환해 (1,2)+(3,4)=(4,6)이 돼요. 복사본이므로 호출자 a,b는 그대로이고 지역 result의 주소를 반환하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p3 | 일반 | malloc대상크기NULL저장free수명주기다. | malloc(sizeof *p) → NULL 검사 → 저장 → free | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p3 | 주의 | 100문자열저장값,문자20+널21,sizep포인터,해제후금지다. | number=100·text="just testing"을 저장해요. 20문자와 종료 널을 위해 21칸을 고르고, sizeof p가 아닌 sizeof *p를 할당하며 free 뒤 접근하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p4 | 일반 | 접근1최소합n최선최악같다. | 접근 O(1), 최소·합 O(n), 최선=최악 | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p4 | 조건 | 정렬정보없는임의배열/유효인덱스출력상수전제,미독원소결과변경가능이다. | 유효 인덱스 접근·정수 출력을 상수로 세고 정렬 정보가 없는 임의 배열을 가정해요. 읽지 않은 값이 최소나 합을 바꿀 수 있어 두 연산은 전부 방문해야 해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p5 | 일반 | 주소전달순서추적과값복사호출자유지있다. | (a) swap(&a,&b);, (1,2,1) → (2,2,1) → (2,1,1) (b) 값 전달은 지역 변수 x,y만 바꾸므로 a,b는 1,2 그대로다. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p5 | 구분 | px=py와*px=*py구분,C주소도값복사이다. | C는 포인터 주소도 값으로 복사하지만 역참조로 원본에 접근해요. px=py는 주소 변수만 바꾸므로 *px=*py와 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p6 | 일반 | 두객체값,원소간격,sizeof,헤더수명규칙있다. | (a) p[0]={1,"Park"}, p[1]={2,"Kim"}, sizeof(struct Example)바이트 뒤 (b) stdlib.h, stdio.h, string.h, free(p) 후 역참조 금지. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p6 | 주의 | free최초주소만,패딩크기단정금지,자동NULL아니다. | free에는 최초 할당 주소 p만 넘기고 p+1을 넘기지 않아요. 패딩 때문에 크기를 14로 단정하지 않고 free 뒤 p가 자동 NULL이 된다고 생각하지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p7 | 일반 | 두++대상및x10y20최종배열,pp대상구분있다. | *p++는 포인터를 이동시키고 (*p)++는 가리키는 원소 값을 증가시켜요. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p7 | 일반 | pp주소,*pp포인터값,**pp배열원소,간격4다. | (b) pp는 p의 주소, *pp는 p의 값, **pp는 a[1], 간격 4바이트. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p8 | 일반 | 유효저장소연결,NULL미초기화역참조불가와동적수명이다. | (a) 미초기화·NULL 역참조 불가, char c; char *pc=&c; *pc='E';, char *q=(char *)v; (b) 고정 배열은 용량 부족·낭비 가능, 동적 할당은 실행 중 크기 결정 및 NULL 확인·free 후 접근 금지. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p8 | 주의 | void*는NULL뜻아니며캐스트유효주소보장안된다. | void * 선언은 NULL 초기화가 아니며, 캐스트만으로 잘못된 주소가 유효해지지는 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 문제설명_0928_ArrayStructureList.html#p9 | 일반 | 패딩과배열비,환경크기구분이다. | (a) 오프셋 1~3에 3바이트 패딩이 있어 전체 8바이트 (b) 전체 20바이트, 원소 4바이트, 비 20/4=5개, sizeof(char)만 항상 1 보장. | pass | pass / 기존 충족, 수정 없음 |
| 문제설명_0928_ArrayStructureList.html#p9 | 주의 | 배열매개변수포인터에는sizeof비로길이못구하고패딩누수아니다. | 배열이 포인터로 전달된 매개변수에서는 이 sizeof 비로 배열 길이를 구할 수 없으며, 정렬 패딩은 메모리 누수와 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 복습문제_0928_ArrayStructureList.html | 구조 | 문제·보기·힌트·풀이·정답을 보존하고 기존 요약 없음 확인 | — | pass | pass / .sum 없는 복습문제는 S 추가 대상 아님 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-concept | 일반 | 포인터는주소로원본공유하고수정이원본에반영된다. | 포인터는 다른 변수의 주소를 담아서, 값을 복사하지 않고 공유하게 해 줘요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-concept | 구분 | 대상수정은포인터주소저장값자체변경아니다. | p=&a 뒤 *p를 바꾸면 a의 내용이 바뀌지만 p에 저장된 주소는 그대로예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-ops | 일반 | &주소,*대상내용,객체단위증가이다. | &는 주소를 꺼내고 *는 가리키는 곳의 내용을 꺼내며, 포인터를 하나 올리면 다음 칸으로 가요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-ops | 구분 | 선언별표와역참조구분,p값주소,&p자기주소이다. | 선언 char *p의 *는 포인터 표시이고, 문장의 *p는 대상 내용이에요. p는 담긴 주소, &p는 포인터 자신의 주소예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-ops | 구분 | *p++는포인터이동,(*p)++는내용증가이다. | *p++·*p--는 현재 내용을 쓰고 p를 다음·이전 칸으로 옮기며, (*p)++는 p를 두고 대상 값만 1 늘려요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-ops | 일반 | 이중포인터로p주소뒤a값접근이다. | p=&a, pp=&p이면 *pp는 p에 든 주소이고 **pp는 a의 값이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-risk | 일반 | 가독성과잘못된메모리변경위험이다. | 포인터는 가독성을 떨어뜨리고, 가리키면 안 되는 곳을 바꿀 수 있어 위험해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-risk | 주의 | 수업은모든것포인터화의세부설명보류했다. | Java·Python의 “모든 것을 포인터화했다”는 수업 표현의 세부 원리는 이번 수업에서 설명하지 않았어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-types | 일반 | 타입은대상타입,void*형변환이다. | 포인터 선언의 타입은 가리킬 대상의 타입이고, void *는 캐스트로 필요한 타입으로 바꿔 써요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s0-pointer-types | 주의 | 포인터는int가아니고일반64환경8바이트다. | 주소가 정수처럼 보여도 C 포인터는 int 타입이 아니며, 보통 64비트 환경에서 포인터 8바이트·int 4바이트로 크기도 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s1-swap | 일반 | 주소로원본변경하고상수시간이다. | 주소를 넘기고 포인터로 받으면 함수 안에서 바깥 변수를 직접 바꿀 수 있어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s1-swap | 일반 | tmp보존후양쪽역참조대입과주소호출이다. | swap(&a,&b)로 부르고 tmp=*px; *px=*py; *py=tmp; 순으로 바꿔요. py=tmp처럼 주소와 값을 섞지 않아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s1-call-by-value | 일반 | 값복사원본유지,목적따라전달방식선택이다. | 값을 복사해서 넘기면 원본은 안전하지만 결과가 main에 돌아오지 않아요. 전달 방식은 목적에 맞게 골라요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s1-call-by-value | 구분 | 반영/여러결과는주소,훼손금지는값복사;크기비용이다. | 원본에 결과를 반영하거나 여러 결과를 공유하려면 주소를, 원본을 지켜야 하면 값을 복사해요. 복사 비용은 넘기는 크기에 따라 들어요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s1-array-pointer | 일반 | 배열이름첫주소,Ai값,연속배치주소4i다. | 배열 이름만 쓰면 첫 번째 주소가 되고, 인덱스를 붙인 A[i]는 값이에요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s1-struct-pointer | 일반 | 일반구조체점,포인터arrow이다. | 구조체 변수는 점으로, 구조체를 가리키는 포인터는 ->로 멤버에 접근해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s1-struct-pointer | 구분 | 포인터만선언해대상구조체생성안되고ps연결후접근이다. | s와 *ps를 선언해도 구조체 객체는 s 하나예요. ps=&s로 연결하면 ps->i는 (*ps).i, 곧 s.i와 같아요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s2-double-pointer | 일반 | 포인터주소를담아두번역참조한다. | 이중 포인터는 포인터의 주소를 담아서, 두 번 따라가면 끝의 값에 닿아요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s2-double-pointer | 구분 | pp와*p와**대상구분이다. | p=&a, pp=&p이면 pp는 p의 주소, *pp는 a의 주소, **pp는 a의 내용이에요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s2-pointer-arith | 일반 | 객체크기단위로포인터증감이다. | 포인터에 1을 더하면 1바이트가 아니라 가리키는 객체 한 칸만큼 움직여요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s2-pointer-arith | 보충 | 일반주소공식은수업에서쓴식아니다. | 보충(수업에서 쓴 식 아님): addr(p+k)=addr(p)+k·sizeof(*p)로 객체 단위 이동을 나타내요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s2-null-init | 일반 | 미연결NULL,우변읽기전초기화이다. | 가리킬 곳이 없는 포인터는 NULL로 두고, 우변에 쓰이는 변수는 꼭 초기화해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s2-null-init | 주의 | 미초기화포인터쓰기는위험하며명시적변환권고이다. | 초기화되지 않은 pc에 *pc=값을 쓰지 말고, 포인터 타입 간 변환에는 바꿀 타입을 명시해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s3-static-vs-dynamic | 일반 | 선언고정크기대실행중필요량할당반납이다. | 정적 할당은 시작 전에 크기가 굳고, 동적 할당은 실행 중에 필요한 만큼 받고 반납해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s3-static-vs-dynamic | 구분 | 고정크기는부족/낭비,포인터사용동기는공유/다중결과/동적할당이다. | 고정 용량은 큰 입력에서 부족하고 작은 입력에서는 낭비예요. 포인터는 공유·여러 결과 반환·동적 할당에 써요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s3-malloc-free | 일반 | malloc요청크기시작주소,free반납이다. | malloc은 필요한 크기만큼 받아 시작 주소를 돌려주고, free는 그 블록을 반납해요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s3-malloc-free | 주의 | 해제전같은포인터재대입은옛주소잃어누수다. | 해제 전 pi에 새 malloc 결과를 덮어쓰면 옛 블록의 주소를 잃어 free할 수 없으므로 별도 포인터로 보관해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s3-sizeof-align | 일반 | sizeof바이트,패딩으로charint8,배열비로원소개수다. | sizeof는 크기를 바이트로 돌려주고, 메모리 정렬 때문에 struct AlignDepends는 5가 아니라 8바이트예요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s3-sizeof-align | 주의 | 예제오프셋0,패딩1..3,int4..7이며패딩누수아니다. | 예제는 c가 0, 패딩이 1–3, i가 4–7에 놓여 8바이트예요. 정렬 패딩은 할당 뒤 해제하지 않은 메모리 누수와 달라요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s3-sizeof-align | 보충 | char항상sizeof1,CHAR_BIT변경가능은수업외보충이다. | 보충(수업에서 유도하지 않음): sizeof(char)는 C에서 항상 1이고, 시스템마다 달라질 수 있는 것은 한 바이트의 비트 수 CHAR_BIT예요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s3-malloc-example | 일반 | 두구조체할당,실패NULL검사,각값설정이다. | 구조체 두 개를 한 번에 받고, NULL 검사로 할당 실패를 거른 뒤 p와 p+1에 차례로 값을 넣어요. | pass | pass / 기존 충족, 수정 없음 |
| 정리노트_0928_ArrayStructureList.html#s3-malloc-example | 일반 | 할당크기2sizeof,첫1Park둘2Kim,전체free이다. | 2*sizeof(struct Example)을 받아 p[0]={1,"Park"}, p[1]={2,"Kim"}을 저장하고 free(p)로 블록 전체를 반납해요. | unresolved | pass / 보완 후 실제 문장 재확인 |
| 정리노트_0928_ArrayStructureList.html#s4-cheatsheet | 구조 | 기존요약·예고·링크화면유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0928_ArrayStructureList.html#s4-next | 구조 | 기존요약·예고·링크화면유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
| 정리노트_0928_ArrayStructureList.html#s4-links | 구조 | 기존요약·예고·링크화면유지 | — | pass | pass / 요약표·예고·링크 화면: 별도 .sum을 새로 만들지 않음 |
