# 문제 카드 규칙

## 작성자 브리프 (메인 에이전트가 1명, 모델은 SKILL.md "에이전트 모델")

---
자료구조및알고리즘이해 기출·교과서 복습문제 카드를 쓴다.

- 읽기: `<SKILL>/references/card-rules.md`(이 파일 전체), `<SKILL>/references/problem-selection.md`의 원칙, `<SKILL>/references/content-rules.md`의 "수식", "C 코드", "SVG 그림"
- 계약: `<RUN>/manifest.json`의 `problems` — id, `source`, `variant`, `anchor`, `level`, `date`, `terms`, `answer`를 그대로 따른다.
- 금지어: `<forbidden 목록>` — 카드 어디에도(문제, 원문, 힌트, 풀이, 풀이의 "수업과의 연결" 줄 포함) 쓰지 않는다. 검사기가 복습문제 페이지 전체를 훑는다. "다음 시간에 배울 …" 같은 예고도 쓰지 않는다.
- 기출 근거: 문항 원문 `<RUN>/problems.md`(문항 id마다 은행의 문제 글·그림 설명·정답과 전사 기록), 정답 계산 `<RUN>/answers.py`, 정리노트 토픽 제목은 manifest. 원본을 봐야 하면 먼저 `<RUN>/repo/from_the_past/기출/_전사/<source-id>.md`를 보고, 원본 파일은 jpg·PDF일 때만 `<RUN>/repo/from_the_past/기출/`의 해당 파일을 Read로 연다(hwp는 Read로 열 수 없다).
- 출력: `<RUN>/cards/<pid>.html` 문제마다 한 파일. 다른 곳에 쓰지 않는다(임시 파일은 아래 규칙).
- 임시·보조 파일(스크립트, 초안, 그림 생성 폴더)은 `<RUN>/work/` 아래에만 둔다. 저장소(`STT/`, `자료구조_강의록_2026/`, `from_the_past/`, `복습노트/`)와 scratchpad 루트, `/tmp`에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 복사하거나 이름을 바꾸지 말고 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 그 경로로 연다.
- 자기 검사: 카드별 `terms`가 문자 그대로 있는지, 정답이 `answer`와 같은지, `$` 짝, 코드 블록 안에 `$`가 없는지, 금지어 `<forbidden 목록>`이 하나도 없는지. 원본 문항(`variant: false`)은 숫자·코드·연산 순서·묻는 것이 원문과 같은지. 변형은 숫자·데이터 값만 바뀌고 구조(자료구조 종류와 크기, 연산 순서의 꼴, 코드 모양, 묻는 것)는 그대로인지. 어긋나면 고치지 말고 보고에 적는다.
- 보고: 카드별 한 줄(출처, 정답), 풀이 중 수업 밖 개념이 필요했던 곳, 원문을 읽기 어려웠던 곳.
---

## 마크업
```html
<article class="card" id="pN" data-source="2016-final-ljw-q3">
  <h3>PN. 제목</h3>
  <div class="problem">…한국어 문제… 코드는 <pre><code class="language-c">…</code></pre> 여러 문항이면 <ol><li>(a) …</li><li>(b) …</li></ol></div>
  <details class="original"><summary>기출 원문 보기</summary><p>2016 기말 3번 · 4점 · 이정원 교수님</p>"…원문…"</details>
  <details class="hint"><summary>힌트 보기</summary>…한두 문장…</details>
  <details class="solution"><summary>풀이 보기</summary><ol class="steps"><li>…</li></ol><p class="answer">정답: …</p></details>
</article>
```
- `data-source`는 manifest `source`(은행 문항 id)와 글자까지 같다. 출처는 이 속성과 기출 원문 보기 안에만 두고, 화면에 출처 배지는 달지 않는다.
- `.problem`은 원문의 뜻을 살려 "~해요" 체로 다듬는다. 숫자, 코드, 연산 순서, 묻는 것은 원문과 한 글자도 다르게 쓰지 않는다(변형은 manifest가 정한 새 값).
- 기출 원문 보기: 첫 줄 `<p>`에 `<연도> <시험> <번호>번 · <배점>점 · <출제자>`(모르는 값은 뺀다, 출제자가 미상이면 "출제자 미상"), 이어서 전사 원문을 따옴표로. 원문이 코드 포함 15줄을 넘으면 앞부분과 묻는 문장만 남기고 "(중략)". 변형이면 원래 숫자가 보이게 원문을 싣는다.
- 원문 그림(트리, 배열, 표)은 인라인 SVG나 표로 다시 그린다. 사진·스캔 이미지를 붙이지 않는다.
- 난이도(`level`)와 수업 날짜(`date`)는 문제 구성에만 쓰고, 카드 위에 배지·태그 줄(`card-head`)을 두지 않는다.
- 풀이 보기 밖에 "수업에서 다시 보기", "수업과 연결" 같은 연결 안내 줄을 따로 두지 않는다(풀이 보기 안 마지막 단계의 "수업과의 연결" 한 줄은 둔다). manifest `anchor`는 풀이가 기대는 토픽을 고르는 데만 쓴다.
- 이모지와 장식 기호(★, ↗ 등)는 쓰지 않는다. 문제·힌트·풀이 문장은 토스처럼 짧고 다정한 "~해요" 체로 쓴다(예: "front와 rear를 구해 보세요.", "넣을 때마다 rear를 한 칸 옮겨요.").
- 템플릿이 카드 하나를 한 화면에 보여 준다. 카드는 다른 카드 없이도 풀 수 있게 쓴다.
- 추적 문제의 풀이는 단계마다 자료구조 상태를 한 줄로 쓴다(예: `push(5) → [5]`, `front=2, rear=5`). 단계가 8개를 넘으면 상태 표(`<div class="table-wrap"><table>`)로 쓴다.
- 풀이 보기 안 마지막 단계(`ol.steps`의 마지막 `li`)에 "수업과의 연결"을 한 줄로(어느 수업의 어떤 말·코드와 이어지는지).

## 교과서 카드
교과서 근거는 problems.md의 교과서 브리프·검증된 JSON/catalog·선택 근거·answers.py이며 기출 전사 경로·연도·시험을 요구하지 않는다.
`data-source="textbook-chNN-qNN" data-source-kind="textbook"`를 manifest와 같게 쓴다. `original` summary는 `교과서 원문 보기`, 첫 줄은 장 제목·문항 번호·책 쪽번호(없으면 PDF 쪽번호)이다. 배지는 추가하지 않는다. `textbook_blocks.render_question`으로 선택지 label/순서·코드·재귀 소문항·검수된 SVG를 보존한다. 기존 기출에 적용되는 원문 중략 규칙은 교과서에는 적용하지 않는다. 문제와 원문에 동일 그림을 넣으면 서로 다른 prefix로 SVG id/href/url 참조를 모두 바꾼다. 흰 배경·대체 설명을 유지하고 observations나 정답 그림을 원문에 넣지 않는다. 의존하는 이전 문항은 같은 팩에 포함하거나 제외한다. 풀이 마지막 단계는 해당 날짜 수업과의 연결이다.
그림 글자가 모바일에서 작아지면 원래 SVG의 폭을 유지하고 `.figure-scroll` 내부에서 가로로 스크롤하게 한다. 바깥 문서의 가로 넘침은 허용하지 않는다. 원문 그림의 값·좌표·연결을 수정해 해결하지 않는다.
