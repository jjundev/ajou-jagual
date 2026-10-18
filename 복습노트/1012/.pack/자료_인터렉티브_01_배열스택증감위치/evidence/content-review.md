# Content review — 1012 배열 스택 ++top / top--

대조 자료: Software_5_Stack.pdf p13(StackType·init·is_empty·is_full)·p14(push·pop·peek) 렌더링 이미지, 정리노트 `s0-array`·`s0-pushpop`(예: top=1, [7, 9]에 push(4) → pop), STT 1012 Part 02(줄 63–81 "증가부터 하고 써라", "s top 값을 먼저 써").

## 코드 보존
- `correct` 소스 5–34줄은 p13 타입·is_empty·is_full, p14 push·pop 본문과 같다("스택 포화 에러\n", "스택 공백 에러\n"). init·peek는 화면 범위 밖으로 생략하고 source.c에 보존.
- MAX_STACK_SIZE 5, main, 시작 원소 가정은 보충. `wrong`은 24줄 전위 ++만 후위 ++로 바꾼 비교용 보충.

## 단계별 C 의미 (기본 n=2, item=4)
1. push 호출: `&s` 주소 값 복사(배열·top 복제 아님), 4 복사.
2. is_full 호출: pop/push의 s 값을 읽어 새 s에 복사(fromCellId) → s 읽기, s.top=1 읽기 → 0 반환.
3. 24줄: s 읽기, top 1 읽기, ++ → top=2, item 읽기, s.stack[2]=4. 증가 후 값이 인덱스. 같은 식 안의 top 저장과 배열 저장의 상대 순서는 C가 정하지 않는다는 점을 설명에 명시하고, 화면 순서는 수업의 "증가부터 하고 써라" 설명 순서를 따랐다.
4. pop: is_empty → 0. 33줄: top 2 읽기(감소 전 값 = 인덱스) → s.stack[2] 읽기 4 → top=1 → x=4 반환. 감소는 반환 전에 완료. 배열 칸 값은 지우지 않고 유효 범위 밖이 된다(노트와 일치).
5. `s->top`은 첫 멤버(stack[0])가 아니어서 포인터 s 읽기와 s.top Cell 접근을 분리했다. 포인터 s의 값은 &s(= &s.stack[0])로 표시.

## 오류 예·경계
- 후위 ++, n=2: s.stack[1]의 9를 4로 덮어쓰고 top=2 → pop이 미초기화 s.stack[2]를 읽는 지점에서 UNINITIALIZED_READ 중단.
- 후위 ++, n=0: 인덱스 -1 쓰기 → OUT_OF_BOUNDS 중단(UB 미실행).
- n=5(포화): is_full=1 → 포화 에러 출력 후 저장 없이 반환, pop은 기존 6을 꺼냄. 두 모드 동일(정상).
- n=4 + item -99: 마지막 칸 s.stack[4]에 저장 후 바로 꺼냄. 빈 스택 n=0 정상 모드: s.stack[0]에 저장 후 top -1 복귀.

판정: pass. 독립 Python 표 79건(전 preset + item 6개 × n 6개 × 모드 2개)과 일치. 숫자 조사 J()는 -99..99 전 범위의 설명 출력으로 확인.
