# 교과서 연습문제 통합 검증 — 2026-10-12

ds-review-pack은 검증된 교과서 JSON catalog를 기출과 함께 조회한다. 신규 팩은 8~12개 중 적합한 교과서 원문 최소 2개, 기존 추가는 기존 문항 전부 + 교과서 4~8개를 사용한다. update-existing은 카드·노트 재생성 없이 partD를 추가한다.

## 결과

| 날짜 | 기존 | 추가 | 총합 | 교과서 원문 ID |
|---|---:|---:|---:|---|
| 0907 | 0 | 4 | 4 | ch01-q01, ch01-q02, ch01-q03, ch05-q01 |
| 0914 | 8 | 4 | 12 | ch01-q12, ch01-q09, ch02-q01, ch02-q05 |
| 0917 | 8 | 4 | 12 | ch02-q06, ch02-q09, ch02-q13, ch02-q16 |
| 0921 | 4 | 4 | 8 | ch03-q01, ch03-q04, ch03-q05, ch03-q06 |
| 0928 | 0 | 4 | 4 | ch03-q03, ch03-q07, ch03-q12, ch01-q17 |
| 1001 | 0 | 4 | 4 | ch03-q08, ch03-q09, ch03-q10, ch03-q11 |
| 1005 | 0 | 4 | 4 | ch06-q03, ch06-q04, ch06-q07, ch06-q10 |
| 1008 | 0 | 4 | 4 | ch04-q01, ch04-q04, ch04-q05, ch04-q08 |
| 1012 | 8 | 4 | 12 | ch05-q03, ch04-q07, ch04-q11, ch04-q14 |

기존 28개 + 추가 36개 = 총 64개. 9/9 팩에 각각 4개를 추가했다. 부족·미해결은 없다. HTML/MD와 날짜별 `자료_복습팩/{manifest.json,selection.json,answers.py,validation.json}`을 함께 갱신한다.

## 검증

- 교과서 현재 원본/자산/검수 payload 검사: 14장, 14원본, 44쪽, 213문항, 46자산 PASS. 교과서 answer=null은 그대로다. 원문·기출은행은 수정하지 않았다.
- 원문 renderer는 content/options/소문항/검수 SVG를 보존하고 필기·인쇄 정답을 풀이로 넣지 않는다. SVG의 ID와 참조는 카드별로 분리한다.
- 36개 추가 답안은 Python 추적·계산, C11 컴파일·실행, 강의 개념 근거로 각각 검증했다. 완성 C 프로그램은 화면에 보이는 코드 그대로 컴파일 검사했다. 검산 스크립트는 임시 폴더에만 실행 파일을 만들고 저장소를 변경하지 않는다.
- manifest, 양쪽 출처 대조, HTML, 단일 리뷰 MD 변환, 기존 카드 보존, 재실행 동일성, 발행 실패 rollback 테스트를 통과했다.
- Google Chrome/Playwright: 1280×900·375×812, light/dark 36조건에서 신규 카드 144상태 검사. 원문·힌트·풀이·선택지·그림·코드·KaTeX·누락 자원·문서 가로 넘침 검사 PASS. 브라우저의 별도 favicon 요청은 콘텐츠 자원 검사에서 제외한다. 넓은 코드·그림은 내부 스크롤한다.
- 9개 팩에서 목차 이동·이전/다음·기존 p1 진행 저장 키를 실제 브라우저로 확인했다. 모바일 SVG 글자는 축소하지 않고 원래 폭으로 내부 스크롤하며, 연결 리스트 그림의 18px 글자와 문서 가로 넘침 0을 확인했다.
- 기존 카드 28개의 raw HTML/id/source, 정리노트 HTML/MD, 이전 SVG, 문제설명 HTML/MD/자료는 해시가 같다. 1012 문제설명은 기존 p1~p8만 설명하며 신규 p9~p12는 리뷰 내부 풀이에서 본다.

## 선별과 검토에서 반영한 사항

- 0907은 의사코드 기초 3개와 이미 배운 매표소 FIFO 개념 1개를 사용한다. 교과서 큐 장 전체를 학습한 것으로 처리하지 않는다.
- 1001은 교과서 배열 삽입/삭제 문항을 S4의 실제 배열 리스트 근거로 개별 대응한다. ch03-q09와 q11의 선행 문항 q08/q10을 함께 싣는다.
- 1008은 S5 p1~12까지의 스택 기초만, 1012는 큐 FIFO와 배운 스택 응용만 사용한다. 미학습 원형 큐/덱 등은 제외했다.
- 비유일 Big-O 객관식 ch01-q08은 제외하고 성장률 정렬 ch01-q12로 교체했다. ch03-q02는 주소 계산과 보기가 맞지 않아 제외했다. 외부 본문/의미를 불확실하게 하는 원문 오류도 제외했다.
- ch03-q03은 타입 크기가 환경에 의존하므로 화면에 검산 환경(int 4, double 8, char 1, float 4바이트)을 밝혔다. 원문은 그대로다.
- 독립 리뷰에서 지적한 근거 PDF 쪽번호·빈 연결 제목·완성 C 헤더를 수정했다. 기본 source_kind/기출 CLI 호환성과 카탈로그 실패 오류 처리도 확인했다.
- 사용자 지시에 따라 이후 origin 이미지를 재독하지 않았다. 검수된 JSON/SVG와 원본·자산·payload 해시를 사용한다.

## 재검증 명령

```sh
DS_TEXTBOOK_PYTHON=/tmp/ds-review-textbook-venv/bin/python python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -v
python3 복습노트/1012/자료_복습팩/answers.py
python3 .agents/skills/ds-review-pack/scripts/bank.py check-manifest from_the_past/기출/문제은행.json 복습노트/1012/자료_복습팩/manifest.json --textbook-dir 교과서 --textbook-python /tmp/ds-review-textbook-venv/bin/python
```

카탈로그 검증용 Python에는 PyMuPDF와 jsonschema가 필요하다. 기본 Python에 없으면 명시한 실행 파일을 사용한다. 임시 venv가 없어졌으면 해당 의존성이 있는 Python으로 경로를 바꾼다.

## 백업과 Git

백업: /Users/hyunjun_macbook_pro/Documents/Univ/자구알/.superpowers/sdd/2026-10-12-ds-review-pack-textbook/backups

커밋·푸시는 실행하지 않았다. 변경은 원래 작업 폴더에 반영하며 관리 워크트리는 검증 후 정리한다.

최종 작업 폴더 검증: 146 tests PASS, 9개 answers.py·manifest·출처·HTML·MD·보존 검사 PASS, git diff --check PASS.
