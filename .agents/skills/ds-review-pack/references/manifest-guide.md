# manifest.json 작성 규칙 (메인 에이전트)

manifest는 이번 팩의 계약이다. 작성자, 검사기, 조립기가 모두 이 파일을 기준으로 삼는다.
필드 모양 예시: `tests/fixtures/mini-run/manifest.json`(테스트용 축약본이라 요약·예고 섹션의 토픽 일부가 없다. 섹션 구성은 아래 규칙을 따른다).
작성 후 반드시 두 검사가 모두 `OK`여야 한다:
`python3 <SKILL>/scripts/manifest.py <RUN>/manifest.json`, `python3 <SKILL>/scripts/bank.py check-manifest <BANK> <RUN>/manifest.json --textbook-dir <TEXTBOOK> --textbook-python <TEXTBOOK_PYTHON>`

## 최상위
| 키 | 값 |
|---|---|
| `course` | `"자료구조및알고리즘이해"` |
| `range` | `"0921"` 또는 `"0917-0921"` (첫 STT–마지막 STT 날짜) |
| `slug` | 이번 범위 대표 강의록 파일명의 영문 부분. `Software_2_Recursion.pdf` → `"Recursion"`, `Software_3_ArrayStructureList.pdf` → `"ArrayStructureList"`. 두 강의록에 걸치면 뒤쪽 것. 1장(`Software_1_자료구조및알고리즘.pdf`)은 `"Intro_DS_Algorithms"` |
| `note_title` | `"<주제> — 5살도 이해하는 정리노트"` |
| `note_subtitle` | `"이정원 교수님 자료구조및알고리즘이해 · 0917 · 0921 수업 (Software_2 Recursion)"` 형식 |
| `review_title` | `"복습문제 N선 — <range 물결표기> 수업 범위"` |
| `review_intro` | 인라인 HTML만(`<b>`, `<i>`, `<code>`, `<a>`). 템플릿이 `<p>`로 감싸므로 `<p>`·`<ul>`·`<div>` 같은 블록 태그는 쓰지 않는다. 문제 구성(이정원 교수님 기출 몇 개, 다른 기출 몇 개, 변형 몇 개, 교과서 몇 개)과 "먼저 풀어 보고, 막히면 힌트를 열어 보세요"처럼 "~해요" 체 한 문장 안내(이모지 없이) |
| `footer_note` | HTML 허용. `출처: 이정원 교수님 강의록(Software_N–M) · 수업 녹음 전사(MMDD…).` |
| `footer_review` | HTML 허용. `출처: 자료구조및알고리즘(이해) 기출 — <이번 팩에 쓴 원본을 "2016 기말(이정원), 2019 중간(출제자 미상)"처럼>. 풀이는 자체 작성이며 답은 <실제로 수행한 Python/C11 실행/강의 근거 대조>로 검증했습니다. 교과서 장·문항 출처도 명시합니다.` |
| `rules` | 선택. 문자열 목록. `["trace-v1"]` 이면 formal 레이어의 5단계 이상 `ol.steps` 에 trace 생성 조각(`data-trace`)을 요구한다. 신규 팩은 넣는다 |
| `sessions` | 날짜별 `{date, stt, summary, slides}`. `stt`는 `"STT/0921 자구알.md"`, `slides`는 `"S2 p1–20"` 형식 |

## sections / topics
- 섹션 id는 `s0`, `s1`, … 순서. 마지막 섹션은 항상 "요약 · 예고"이며 토픽 `s<N>-cheatsheet`, `s<N>-next`, `s<N>-links`를 둔다.
- 섹션은 **개념 순서(강의록 순서)** 로 묶는다. 날짜는 토픽 태그로만 드러낸다.
- 토픽 id는 `s<n>-<kebab>`(영문 소문자). 토픽 하나 = 강의록 1~3쪽 또는 칠판 설명·추적 하나.
- `short`는 상단 목차 글자(예: `"2 재귀 호출"`), `title`은 `"2. 재귀 호출의 구조"`.
- `layers`: 개념 토픽은 `["eli5", "formal", "prof"]`. 교수님 발언이 없으면 `prof` 대신 빼되 이유를 보고서 "스킬이 정한 사항"에 적는다. 요약·예고 섹션 토픽은 `[]`.
- `supp`: 요약의 `🕳️ 미룬 유도`를 보충으로 싣는 토픽만 `true`.
- `required_terms`: 토픽당 3~9개. 요약의 **용어·코드 목록과 강조 발언**에서 고른다.
  - 식은 작성자가 **공백까지 그대로** 쓸 TeX 문자열이다(예: `"T(n) = T(n-1) + 1"`).
  - 코드 조각은 코드 블록에 들어갈 글자 그대로다(예: `"return n * factorial(n - 1);"`). `<`는 그대로 `<`로 적는다(검사기는 HTML 엔티티를 푼 글자와 비교한다).
  - 교수님 비유의 핵심 단어(예: `"러시아 인형"`)를 최소 하나 넣어 교수님 말씀(prof) 레이어 누락을 잡는다.
- `preview_topic`: `s<N>-next`.
- `forbidden_outside_preview`: 슬라이드 대조표에서 "예고만/안 다룸"인 쪽의 핵심 용어 3~8개. 본문에 나오면 검사 실패.

## parts / problems
- `parts`: `references/problem-selection.md`의 parts 표를 따른다(`id`·`title`·`short` 모두). 문항이 0개인 part는 뺀다.
- 문제 선별은 `references/problem-selection.md`. 새 팩은 8~12(적합한 교과서 최소 2개), 기존 추가는 기존 전부 + 교과서 4~8개(부족하면 보고).
- 문제 `id`: `p1`, `p2`, … 빈 번호 없이 순서대로(카드 파일명 `cards/<id>.html`이 된다). `part`: 위 `parts`의 id 중 하나.
- `source_kind`: `past-exam`, `textbook`, `lecture-code`; 기존 생략 필드는 past-exam. 교과서는 `source: textbook-chNN-qNN`, `variant: false`, `part: partD`. 종류와 ID 불일치는 실패한다.
- `source`: 기출이면 은행 문항 id(예: `"2016-final-ljw-q3"`). 변형도 원래 문항 id를 쓰고 `variant: true`.
- `anchor`: 풀이가 기대는 정리노트 토픽 id(카드에 링크로 쓰지는 않는다). `level`: `problem-selection.md`의 level 표. `date`: 관련 수업 날짜.
- `terms`: 카드에 반드시 나올 글자(정답 포함). **모두 빈 문자열이 아닌 문자열**이다. 예: `"front=4"`, `"rear=2"`, `"60 40 30 15 12 6 10 5"`. `required_terms`, `forbidden_outside_preview`도 같다(`manifest.py`가 검사).
- `answer`: `<RUN>/answers.py`로 계산한 정답 문자열. 계산 스크립트 경로를 보고서에 적는다.

## links
- `href`는 작성자가 `<a href="…">`에 **글자 그대로** 넣을 값이다(검사기가 해당 `topic` 안의 링크와 정확히 비교한다). `%20` 같은 인코딩도 그대로.
- `{"topic": "s<N>-links", "href": "복습문제_<range>_<slug>.html"}`는 항상. 파일명은 `manifest.py`의 `review_name`이 만드는 것과 정확히 같아야 한다.
- 이번 범위 강의록 중 파일명이 영문인 것(2~12장)은 `s<N>-links`에 `../../자료구조_강의록_2026/Software_<N>_<이름>.pdf`를 건다. 1장 PDF는 파일명이 한글이라 걸지 않는다.
- 이전 복습팩과 이어지는 개념이면 `../<이전 range>/정리노트_<이전 range>_<slug>.html#<토픽>` 링크를 건다(팩마다 `복습노트/<range>/` 폴더라 한 단계 위로 올라간다). 토픽은 기본 `s<N>-links`, 특정 토픽에 거는 편이 분명하면 그 토픽 id.

## 영속 제작자료
`.pack/자료_복습팩/selection.json`(팩 폴더 기준): range, mode(new|retrofit), taught_evidence, concept_overrides, selected, excluded. selected는 id/source/source_kind/original_id/prerequisites, evidence(path/locator/sha256), answer, verification(method/reference/result)를 갖는다. methods는 python/c-run/lecture-reference; result는 pass|blocked. validation.json은 checks, counts(existing/added/total), preserved(원문 카드·노트·문제설명 해시), unresolved를 저장한다. 실패·미실행을 pass로 기록하지 않는다. answers.py는 저장소를 변경하지 않는 재현 검산이다.

## 강의 예제·전역 검토 연동

신규·update-existing·revise-existing은 [공통 개편·검증 계약](review-overhaul.md)을 함께 적용한다. lecture-code는 실제 강의 페이지·해시·학습 근거와 자체 질문을 구분한다. 최종 전체 날짜 audit를 통과한 정확한 최종 HTML 경로만 설명·PDF 입력으로 사용한다. update-existing의 기존 카드 보존 계약은 유지한다.

lecture-code는 source=lecture-sNN-pN-example, lecture_ref(path,pdf_page,sha256,example,taught_on), objectives, task_family를 필수로 기록한다. 경로는 저장소 상대 경로이며 --repo로 실제 PDF를 검사한다.
