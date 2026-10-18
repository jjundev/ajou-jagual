# Content review — 1012 연결 스택 push

대조 자료: Software_5_Stack.pdf p16(타입)·p17(push) 렌더링 이미지(`pdf-p16.png`, `pdf-p17.png`), 정리노트 HTML/.pack MD `s0-node`·`s0-linkedpush`, STT 1012 Part 02(줄 119–151 "top부터 바꾸면 낙동강 오리알", "101호를 가리키는 거").

## 코드 보존
- `correct` 소스 12–24줄은 p17 push 본문과 같다(문자열 "메모리 할당에러\n" 포함). p16의 `} StackeNode;` 오타는 노트와 같이 `StackNode`로 고쳤고 provenance·brief·화면 안내문에 적었다.
- `wrong` 소스는 21·22줄 순서만 바꾼 비교용 보충(supplement=true)이다. main(25–31줄)과 시작 노드 가정은 보충이며 화면 코드 주석으로 표시한다.

## 단계별 C 의미 (기본 n=3, item=40)
1. call 29 → 새 push 프레임. bind 12: `&s`는 s의 값을 읽지 않는 주소 값이므로 fromCellId 없음. 정수 상수 40 복사.
2. 14줄: temp 저장 공간 → malloc 결과 &D 대입. D.item/D.link는 미초기화. 할당 성공 가정(brief 명시).
3. 15줄: temp 읽기만 하고 NULL 아님.
4. 20줄: item 읽기 → `temp->item`은 첫 멤버이므로 through=[f.temp]로 D(item)에 정확히 쓰기.
5. 21줄: `s->top`은 through=[f.s]로 main s.top 읽기(&C). `temp->link`는 첫 멤버가 아니라서 temp 읽기 + D.link 쓰기 두 이벤트로 분리. 값 &C.
6. 22줄: temp 읽기 → through=[f.s]로 s.top에 &D. 이 시점에 C는 D.link가 보유.
7. return 24: push의 s·item·temp 수명 종료. 할당 노드 D는 살아 있음(정확).
8. 결과 top → D → C → B → A → NULL.

## 오류 예
- top 먼저: s.top=&D가 &C의 유일한 보관처를 덮어씀 → 22줄 s->top 읽기는 &D → D.link=&D 자기 순환. C, B, A는 할당된 채 도달 불가(누수). UB가 아니므로 진단 없이 끝까지 실행하는 것이 맞다.
- 빈 스택 + top 먼저: 잃는 노드는 없고 D.link=&D로 NULL 종료가 깨진다. 22줄 설명은 n=0일 때 "원래 값 NULL이 아니라 &D"로 분기한다.

## 경계·같은 값
- n=0(빈 스택): D.link=NULL. n=1: D.link=&A. item -99/99 경계, item 30(C와 같은 값)은 값이 같아도 노드(주소)는 다름을 보여 준다.

## 표기
- 포인터 값 &C는 노드 객체 시작(구조체 전체)이라는 수업 설명("101호")과 일치하도록 첫 Cell ID를 노드 이름으로 두었다. A~D는 그림 이름표이고 실제 번지가 아님을 intro와 brief에 명시.
- 숫자 조사는 J() 함수로 처리하고 -99..99·0..3 전 조합의 설명에서 조사·null/undefined 출력을 확인했다.

판정: pass. 독립 Python 표 63건(전 preset + item 7개 × n 4개 × 모드 2개)과 일치.
