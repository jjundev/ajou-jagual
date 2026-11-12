# trace 생성기

5단계 이상 상태 추적(트리 순회, 배열·스택·리스트 변화)은 손으로 그리지 않고 데이터에서 만든다. 단계 글과 그림이 같은 JSON 에서 나오므로 서로 어긋나지 않는다. 예제는 `tests/fixtures/trace/inorder-1105.json`(생성 스크립트 `make_inorder_1105.py`)이다.

## 작성 순서
1. `RUN/work/trace_<id>.py` 가 실제 알고리즘을 돌려 `RUN/traces/<id>.json` 을 쓴다.
2. `python3 "$SKILL/scripts/trace_figs.py" lint RUN/traces/<id>.json` 이 통과해야 한다.
3. `python3 "$SKILL/scripts/trace_figs.py" render RUN/traces/<id>.json --target note` 출력을 formal 레이어에 그대로 붙인다(손으로 고치지 않는다).
4. 고칠 때는 JSON 을 고치고 다시 render 한다.

정적 트리 그림만 필요하면 `shadow PATH --structure ID --id SVG_ID`, 완성된 HTML 이 JSON 과 맞는지는 `verify HTML --traces DIR` 로 본다. 문제설명은 `render --target explain`(정적 SVG 만, `style` 없음)이다.

## Trace JSON (version 1)
`{version:1, id, title, structures:[…], steps:[{text, state:{<구조 id>: …}, key?:bool}]}`

| 구조 kind | 정의 | 단계 상태(매 단계 전체 상태) |
|---|---|---|
| `bintree` | `nodes:{키:{l?,r?}}`, `root` | `{cur, done[], null_at:{node,side}\|null, changed[]}` |
| `array` | `label`, `size` | `{values[], hi[], ptr:{이름:인덱스}}` |
| `stack` | `label` | `[값…]`(아래→위) |
| `list` | `label` | `{order[], ptr:{이름:노드}, edge_changed:[[a,b]…]}` |

- 트리 x 는 키 크기가 아니라 구조상 중위 순위, y 는 깊이다. 수식 트리처럼 키가 숫자가 아니어도 된다.
- `text` 는 일반 글자다. HTML 태그와 `$` 를 쓰지 않는다(`<`, `&` 는 렌더러가 escape 한다).
- `key: true` 는 대표 단계다.

## 한도
단계 40개 이하, 트리 노드 31개 이하, 배열 칸 20개 이하, `key` 단계 2~4개. lint 오류 코드: `version`, `id`, `no-steps`, `too-many-steps`, `unknown-kind`, `unknown-structure`, `missing-node`, `too-many-nodes`, `too-many-cells`, `key-count`, `dollar`, `not-object`(최상위가 객체 아님), `text`(단계 `text` 없음·문자열 아님), `structure-id`(구조 `id` 가 유일한 문자열 아님), `bad-ref`(노드 참조·`done`·`changed` 가 문자열 아님), `not-a-tree`(루트에서 걸을 때 같은 노드를 다시 만남: 순환·공유 자식). lint 는 어떤 JSON 값에도 예외를 던지지 않는다.

## 조각과 검사
- 조각은 `data-trace`, `data-trace-sha`(정규 JSON 해시 앞 12자)로 도장이 찍힌다. id 는 `trace-<id>-s<n>`, `trace-<id>-k<n>`, `widget-trace-<id>`(재생기), `widget-trace-<id>-static-<n>`, `widget-trace-<id>-ui` 다.
- 재생기(`widget-trace-*`)는 팩의 위젯 0~2개 한도에 세지 않는다.
- JSON 은 조립 때 `.pack/자료_복습팩/traces/` 로 복사된다. `check_html.py` 코드: `trace-missing`(JSON 없음), `trace-stale`(조각이 JSON 을 다시 render 한 결과와 다름. JSON 을 읽을 수 없거나 lint 에 실패해도 같다), `trace-required`(manifest `rules` 에 `trace-v1` 이 있는데 formal 의 5단계 이상 `ol.steps` 가 생성된 `div.trace-block` 안에 있지 않음. 손으로 쓴 `data-trace` 속성은 면제되지 않는다).
