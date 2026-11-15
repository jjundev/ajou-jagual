# 리뷰어 지시문 (lite에서는 생략)

---
자료구조및알고리즘이해 복습팩 초안을 검토한다. 파일은 수정하지 않는다.

- 대상: `<RUN>/repo/복습노트/<range>/<정리노트 html>`, `<…/복습문제 html>`
- 근거: `<RUN>/summaries/stt-*.md`, `<RUN>/slides.txt`, `<RUN>/manifest.json`, `<RUN>/answers.py`, `<RUN>/problems.md`, 기출 원본 `<RUN>/repo/from_the_past/기출/`, 교과서 원문 JSON·PDF·검증된 자산, selection.json·validation.json
- 규칙: `<SKILL>/references/content-rules.md`, `card-rules.md`, `problem-selection.md`

확인할 것:
1. **사실 오류**: 정의, 코드, 추적 결과, 시간복잡도, 조건(예: "비어 있으면/가득 차면", "항상/보통")이 요약·슬라이드와 맞는가. 코드는 컴파일되는 C인가.
2. **누락**: 요약의 핵심 내용·강조 발언·시험 언급·미룬 설명 중 노트에 없는 것.
3. **범위**: "예고만/안 다룸" 내용이 본문에 설명되어 있는가.
4. **ELI5 품질**: 쉽게 말하면(eli5) 레이어가 전문용어·코드 없이 1~3문장인가, 그림이 개념을 실제로 보여 주는가.
5. **문제**: 카드가 `problems.md`의 원문과 숫자·코드·묻는 것까지 같은가(변형은 숫자만 다른가), 수업 범위로 풀 수 있는가, 정답이 `answers.py`와 같은가(직접 다시 계산·실행).
6. **교과서**: 원문 content/options/소문항·참조·SVG가 보존됐는가, verified를 정답 검증으로 오해하지 않았는가, 직접 검산 결과와 답이 같은가. 보기 전체와 선행 문항이 해당 수업 범위로 풀리는가. 기존 추가는 이전 raw 카드·pN·source·노트·문제설명이 그대로이며 재실행은 멱등인가.
7. **표현**: 표 첫 열이 한 글자씩 줄바꿈되거나 빈 칸이 있는 표, 잘린 문장, 가로로 너무 긴 코드 줄(80자 초과).

출력 형식(이것만):
```
## Critical
- [s2-call-stack] 문제 → 고칠 내용
## Important
- [p3] …
## Minor
- …
```
각 항목은 토픽/카드 id로 시작한다. 없으면 "없음".
---

## 강의 예제·전역 검토 연동

신규·update-existing·revise-existing은 [공통 개편·검증 계약](review-overhaul.md)을 함께 적용한다. lecture-code는 실제 강의 페이지·해시·학습 근거와 자체 질문을 구분한다. 전체 날짜 audit를 통과한 작업용 HTML로 PDF를 만들고, 발행한 JSON 원고에서 문제설명을 만든다. update-existing의 기존 카드 보존 계약은 유지한다.
