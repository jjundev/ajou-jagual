# 추적 데이터 → 그림 생성기 설계

2026-11-12 · 대화에서 확정(#1~#12). 근거 조사: 정리노트 189토픽 중 156개가 formal 그림 0, 42개가 5단계 이상 글 추적, 문제설명 141문항 중 111개 풀이 그림 0.

## Intent
정리노트·문제설명의 단계 추적을 작성자가 손그림이나 글로만 쓰지 않게 한다. 작성자는 실제 알고리즘을 돌려 상태 데이터(trace JSON)를 만들고, 생성기 `trace_figs.py` 하나가 같은 데이터에서 대표 단계 정적 그림·단계별 재생기(정리노트만)·`ol.steps` 글 목록을 만든다. 첫 소비자는 1105 정리노트 3페이지(`s0-inorder`). 기존 다른 페이지 이주는 별도 작업.
분류: architectural.

## Behavior when done
- 작성 에이전트: `RUN/work/trace_<id>.py`로 JSON 생성 → `trace_figs.py render` 조각을 섹션에 붙인다.
- 정리노트: formal 레이어에 재생기([처음부터]/[이전]/[다음], 현재 위치 강조·끝난 노드 점·스택 칸·출력 칸) + 같은 문장의 `ol.steps`. MD 에는 대표 단계 정적 SVG.
- 문제설명: 대표 단계 정적 그림만(스크립트·style·hidden 금지 계약).
- 실패: 데이터 형식 오류는 `lint` 오류 코드, JSON 변경 후 미재생성은 `trace-stale`, 새 팩의 5단계 이상 손 추적은 `trace-required`.

## Not in this round
- 기존 41개 추적 토픽·문제설명 111문항 이주.
- 그래프·해시·2차원 미로 모양.
- ds-interactive C 메모리 엔진 통합.
- 추적 값 누락 휴리스틱 검사.

## Approach
A: Python 표준 라이브러리 CLI가 작성 시점에 JSON → 완성 HTML 조각을 만들고 조각에 데이터 해시를 박는다. (B: 조립 시 자리표시자 펼치기 — 기존 노트에 RUN 이 없어 불가. C: ds-interactive 확장 — 렌더러가 둘로 갈림.)

## Trace JSON (version 1)
- `{version:1, id, title, structures:[…], steps:[{text, state:{<structure id>: …}, key?:bool}]}`
- 구조 kind: `bintree`(nodes:{key:{l?,r?}}, root), `array`(label, size), `stack`(label), `list`(label).
- 단계 상태(전체 상태): bintree `{cur, done[], null_at:{node,side}|null, changed[]}`, array `{values[], hi[], ptr:{name:index}}`, stack `[값…]`(아래→위), list `{order[], ptr:{name:node}, edge_changed:[[a,b]…]}`.
- 한도: 단계 40, 트리 노드 31, 배열 칸 20, key 단계 2~4.

## Rendering
- 트리 x = 구조상 중위 순위, y = 깊이. 클래스 `fig-ink`/`fig-accent`/`fig-dot`/`fig-text`/`fig-muted`만, `style` 속성 0, 글자 `font-size="13"`.
- 재생기는 모든 단계 SVG를 미리 그려 넣고 JS 는 보이기만 바꾼다. 그리는 코드는 Python 하나.
- 조각은 `data-trace`, `data-trace-sha`(정규 JSON sha256 앞 12자)로 도장을 찍는다.

## Decisions
| # | 결정 | 답 |
|---|---|---|
| 1 | 언어·위치 | Python 표준 라이브러리, `ds-review-pack/scripts/trace_figs.py` |
| 2 | 통합 | 작성 시점 CLI |
| 3 | 상태 | 단계별 전체 상태 |
| 4 | 계산 주체 | `trace_<id>.py` 실제 알고리즘 |
| 5 | 재생기 | 미리 그린 SVG 전환 |
| 6 | 트리 배치 | x=중위 순위, y=깊이 |
| 7 | 문제설명 | 정적 SVG 만, style 없음 |
| 8 | 신선도 | sha + 재렌더 바이트 비교 |
| 9 | 기존 팩 보호 | `trace-required` 는 manifest `rules` 에 `trace-v1` 있는 팩만 |
| 10 | 위젯 한도 | 재생기는 팩당 0~2개 한도에서 제외 [confirmed] |
| 11 | 첫 소비자 | 1105 p3 만 [confirmed] |
| 12 | 강제 문턱 | `ol.steps` 5단계 이상 [confirmed] |
