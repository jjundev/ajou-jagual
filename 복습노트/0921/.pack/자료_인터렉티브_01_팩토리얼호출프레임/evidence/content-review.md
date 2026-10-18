# Content review — 0921 factorial 호출 프레임

대조 자료: Software_2_Recursion.pdf p6 렌더링(evidence/pdf-s2-p6.png), 정리노트 `s0-recursion-rules`(HTML·.pack MD: "호출할 때마다 문제가 줄어들어 바닥을 칠 수 있어야", "멈추는 부분이 없으면 시스템 오류가 날 때까지 끝없이 호출"), STT 0921 00:14("그 바닥이 답이 뭐다라고 제시할 수 있는 조건").

## 코드 보존
- lecture 소스 2–6줄은 p6 factorial과 같다. 슬라이드의 `if( n <= 1 )  return 1` 뒤 세미콜론 누락은 그대로 컴파일되지 않으므로 보충했고, 코드 아래 안내·provenance·brief·source.c에 밝혔다(정상 코드로 몰래 고치지 않음).
- #include, int main(void), printf는 보충(provenance.supplement=false이지만 note에 보충 범위 명시). nobase는 p6 질문을 확인하는 보충(supplement=true), if 줄을 주석으로 바꿔 줄 번호를 맞췄다.

## 단계별 C 의미 (기본 n=4, trace-walkthrough.txt)
1. main 9줄: factorial(4) 호출 → 새 프레임 f1, 상수 인자 4를 매개변수 n에 bind(fromCellId 없음: 리터럴은 변수 값을 읽지 않음).
2. 4줄: n 읽기, 4 <= 1 거짓 → 5줄. 반환값을 받을 화면용 칸 `factorial(3)`을 f1에 선언(이름 없는 값 · 주소 없음으로 표시해 실제 변수처럼 주장하지 않음).
3. 5줄: n-1 계산을 위해 f1.n 읽기 → 새 프레임 f2 call → bind 3. 호출 n은 서로 다른 Cell(&f1.n, &f2.n)이며 앞 호출은 "대기" 상태로 남는다.
4. f4(n=1): 4줄 참 → return 1이 f3의 반환 칸에 쓰이고 f4의 n 수명 종료.
5. 올라가며 각 호출: 돌아온 값 읽기, 자기 n 읽기(곱셈 피연산자 순서는 C가 정하지 않음을 설명), n×값을 호출자 칸에 return. 2→6→24, main의 r=24, printf에서 r 읽기.
- 반환 순서는 호출의 역순(f4→f3→f2→f1)이며 반환 시 해당 프레임의 Cell만 종료된다(엔진 return).

## 경계·오류
- n=1, 0, -3: 첫 호출에서 바로 바닥, r=1. 음수는 수학적 팩토리얼이 정의되지 않지만 코드가 1을 돌려준다는 설명을 추가.
- n=12: 479001600(int 안). n=13: f1에서 13 × 479001600 = 6227020800 > 2147483647 → 곱셈 단계에서 SIGNED_OVERFLOW 진단으로 중단. int 32비트는 강의 기준(정리노트 s1-array-why)이라고 명시, 실제 ABI 크기를 일반 사실로 주장하지 않음.
- n 범위 -99..99: 14..63은 바닥까지 내려간 뒤 n=13 호출의 곱셈에서 SIGNED_OVERFLOW. 64 이상은 64번째 factorial 호출(main 포함 65개째)에서 엔진 깊이 한도로 멈추며, 설명에 "화면은 깊이 64까지만, 실제 C는 모두 쌓였다가 13!부터 UB"라고 구분해 엔진 한도를 C 의미로 주장하지 않는다.
- nobase: 바닥 검사 없이 매번 declare→read→call. 64번째 호출(main+63 factorial 프레임)에서 엔진 깊이 한도 LIMIT_REACHED. 설명은 실제 프로그램은 스택 공간이 바닥날 때까지 부르다 비정상 종료된다고 구분.

## 문구
- 숫자 뒤 조사(을/를, 이/가, 과/와)를 값에 맞춰 계산. "n은 4이고" 등 표기 확인.
- 판정: pass. 각 줄의 복사(bind)·읽기·쓰기(return 결과)가 C 의미와 맞고, 보충·단순화는 화면 안내와 brief에 구분되어 있다.
