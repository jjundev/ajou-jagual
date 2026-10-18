# Content review — 1012 연결 스택 pop

대조 자료: Software_5_Stack.pdf p16(타입)·p18(pop) 렌더링 이미지, 정리노트 `s0-node`·`s0-linkedpop`, STT 1012 Part 02–03(줄 153–161 "얘를 return 받고 얘도 free시켜", "s의 top을 s의 top이 가리키는 곳의 link가 가리키는 곳을 가리키게").

## 코드 보존
- `correct` 소스 16–29줄은 p18 pop 본문과 같다("스택이 비어있음\n", `int item`, `s->top = s->top->link;`, `free(temp);`, `return item;`).
- `is_empty`(11–14줄)는 p18이 호출만 하고 싣지 않으므로 노트 설명(top == NULL)대로 보충. 타입 오타 수정·main·시작 노드는 보충으로 표시.
- `late-read`, `free-first`는 순서만 바꾼 비교용 보충(supplement=true).

## 단계별 C 의미 (기본 n=3, 맨 위 30)
1. call 34, bind 16: `&s` 주소 값 복사.
2. 18줄 is_empty 호출: 새 프레임, bind 11은 pop의 s 값을 읽어 복사(fromCellId=f.s로 실제 값 일치 검사). 13줄 through=[e.s]로 s.top 읽기 → 0 반환. 반환 후 e.s 수명 종료.
3. 23줄: s.top 읽기(&C) → temp 선언·초기화. temp와 s.top이 같은 노드를 공유하는 별칭.
4. 24줄: `temp->item`(첫 멤버) through=[f.temp] 읽기 → item에 30 복사.
5. 25줄: s.top 읽기 → C.link 읽기(첫 멤버가 아니라 별도 이벤트) → s.top=&B.
6. 26줄 free(temp): C 객체 수명 종료, 살아 있는 별칭 temp만 사용 불가(s.top은 이미 B). 
7. 27줄: 보관한 item 읽기 → x=30 반환, pop 지역 수명 종료. 해제 노드를 읽지 않는다.

## 오류 예
- 해제 후 읽기: top 이동·free 후 `temp->item` → temp가 indeterminate이므로 그 읽기에서 INDETERMINATE_READ 중단. UB를 실행하지 않는다.
- 먼저 해제: free 시 temp와 s.top이 모두 같은 C를 가리키므로 둘 다 indeterminate. 26줄 s->top 읽기에서 중단. x는 초기화되지 않은 채.

## 경계
- n=0: is_empty=1 → exit(1)은 프로그램 종료(수업 중 "루프를 빠져나오는" 표현은 노트처럼 바로잡음). pop은 반환하지 않으므로 x 미초기화로 끝난다. 진단이 아니라 관찰 단계.
- n=1: s.top=NULL로 빈 스택. 맨 위 값 -99/99 경계, n=2에서 top 노드는 B.

판정: pass. 독립 Python 표 79건(전 preset + 값 6개 × n 4개 × 모드 3개)과 bind/선언/쓰기 순서·진단 지점·최종 Cell이 일치.
