# 자구알 확인문제 (`ds-concept-check`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 복습팩 하나(1102)를 근거로 수업에서 처음 배운 개념을 확인하는 즉시 채점 HTML `확인문제_<range>_<slug>.html`을 만드는 새 스킬을 만들고, 1102로 시범 발행한다.

**Architecture:** 작성자는 `objectives.json`·`items.json`(데이터)만 쓴다. `build.py`가 카드 HTML을 렌더하고 자구알 `review-template.html` 외형에 생명과학에서 복사 이식한 즉시 채점 스크립트를 붙인다. `check.py`(규칙·파이썬 재계산), `blind.py`(블라인드 풀이 사본·대조 장부), `browser_check.py`(Playwright 조작)가 발행 전 관문이다.

**Tech Stack:** Python 3(홈브루 `python3`, pytest 9, playwright), 바닐라 JS/CSS(복사 자산), 자구알 `ds-review-pack` 템플릿·`html2md`·`pack_layout`.

**Spec:** `docs/superpowers/specs/2026-11-12-ds-concept-check-design.md`

## Global Constraints

- 스킬 실체는 `.agents/skills/ds-concept-check/`, `.claude/skills/ds-concept-check`는 `../../.agents/skills/ds-concept-check` 심볼릭 링크(기존 스킬과 같은 방식).
- 공개 파일: `복습노트/<range>/확인문제_<range>_<slug>.html`. 근거·원본: `복습노트/<range>/.pack/자료_확인문제_<range>_<slug>/`. 팩 루트에는 `.html`만 추가한다.
- 문항 수 1~16, 확인 목표마다 1~2문항, 모든 목표 최소 1문항.
- 객관식은 정확히 4지, 보기 id `A`~`D`. 정답 위치 개수의 최댓값−최솟값 ≤ 1.
- 부정형 발문(`않은`·`아닌`·`틀린`·`옳지`) 문항 수 × 4 ≤ 전체 문항 수.
- 오답 보기마다 `misconception`·`why`·`source`(접두 `stt:`·`note:`·`bank:`) 필수, 정답 보기도 `why` 필수.
- `절차 결과`·`규칙 적용` 목표의 문항은 `format: "short"`이고 `compute`가 필수다.
- SVG에 `style` 속성 금지(클래스 `fig-ink`·`fig-text`만).
- 새로고침하면 답안·진행 초기화(저장소 `null`로 마운트), 테마는 템플릿 기존 동작대로 유지.
- `ds-review-pack`·`bio-*` 파일은 수정하지 않는다. 생명과학 자산은 복사한다(출처를 `assets/SOURCE.md`에 기록).
- 사용자에게 보이는 글은 한국어, 해요체(기존 카드 문체).
- 테스트 실행: 저장소 루트에서 `python3 -m pytest .agents/skills/ds-concept-check/tests -q`.

## Review Focus

1. **macOS NFD 한글 폴더명** — `복습노트/1102/.pack/자료_복습팩`이 NFD로 저장돼도 `build.py`·`check.py`가 찾아야 한다. → Task 3에 `test_build_finds_nfd_pack_dir`.
2. **값 입력 표기 변형** — `A, B, D`·`A,B,D`·`A B D`·`ABD`·소문자 입력이 모두 정답이어야 한다. → Task 1 `test_accepted_variants`, Task 6 브라우저에서 소문자·공백 변형 입력.
3. **보기·발문 속 `<`·`&`** — `a<b`, `p && q` 같은 텍스트가 깨지지 않고, 채점 모델 생성이 실패하지 않아야 한다. → Task 2 `test_option_text_is_escaped`.
4. **근거 팩 누락** — `자료_복습팩/manifest.json`이나 `stt-summary.md`가 없으면 traceback 대신 "팩이 없어 근거가 없습니다"와 exit 1. → Task 3 `test_build_missing_pack_message`.
5. **문항 수정 뒤 블라인드 장부** — 문항을 고치면 그 문항의 이전 블라인드 판정은 무효가 되어 다시 풀어야 한다. → Task 5 `test_status_invalidates_changed_item`.

---

## File Structure

```
.agents/skills/ds-concept-check/
  SKILL.md                      절차(1102 시범 포함), 경로 약속, 보고 형식
  references/item-rules.md      objectives.json·items.json 스키마와 문항 작성 규칙(작성자 브리프)
  references/blind-brief.md     블라인드 풀이 리뷰어 브리프
  scripts/_paths.py             SKILL·REPO·DS_REVIEW_PACK 경로, NFC 폴더 찾기, ds-review-pack 모듈 import
  scripts/tree.py               트리 연산(순회·높이·개수·계산·배열 인덱스)·compute·SVG
  scripts/render.py             item → 카드 HTML, 허용답 변형
  scripts/interaction.py        생명과학 review_interaction.py 복사본(경로·부트만 수정)
  scripts/build.py              src 폴더 → 확인문제 HTML
  scripts/check.py              발행 전 규칙 검사
  scripts/blind.py              블라인드 사본(make)·대조(record)·상태(status)
  scripts/browser_check.py      Playwright 조작 검사
  assets/review-interaction.js  복사
  assets/review-interaction.css 복사 + .short-input 규칙 추가
  assets/review-prompt.js       복사
  assets/SOURCE.md              복사 출처·커밋·수정 내역
  tests/_util.py                경로·픽스처 도우미
  tests/fixtures/mini/          가짜 팩(아래 Task 3 정의)
  tests/test_tree.py  test_render.py  test_build.py  test_check.py  test_blind.py  test_browser.py  test_skill_files.py
.claude/skills/ds-concept-check -> ../../.agents/skills/ds-concept-check
```

데이터 모양(전 Task 공통, `references/item-rules.md`에 그대로 적는다):

```json
// objectives.json
{"range": "1102", "slug": "Tree", "objectives": [
  {"id": "o1", "topic_id": "s0-array", "concept": "배열 표현의 인덱스 규칙",
   "can_do": "노드 번호로 부모·자식 칸을 계산한다", "kind": "규칙 적용",
   "source": {"slide": "S7 p8", "stt": "1절"}}]}
// items.json
{"items": [
  {"id": "q1", "objective": "o1", "format": "short", "title": "부모 칸 번호",
   "stem_html": "<p>…</p>", "tree": ["A","B","C",null,"D"],
   "compute": {"op": "parent_index", "arg": 5},
   "answer": {"canonical": "2", "accepted": []},
   "solution": ["i번의 부모는 i/2(정수 나눗셈)예요.", "5/2 = 2예요."]},
  {"id": "q2", "objective": "o2", "format": "mcq", "title": "…", "stem_html": "<p>…</p>",
   "options": [
     {"id": "A", "text": "…", "why": "…"},
     {"id": "B", "text": "…", "why": "…", "misconception": "레벨 순회를 표준 순회로 봄", "source": "stt:7절"}],
   "answer": "A", "compute": null}]}
```

`tree`는 레벨 순서 배열(0번 = 루트, 자식 `2k+1`·`2k+2`, 빈 자리 `null`)이다. 화면·정답에 쓰는 **강의 번호**는 1부터(루트 1, 자식 `2i`·`2i+1`)이며 `tree.py`가 변환한다.

---

### Task 1: 트리 연산과 compute

**Files:**
- Create: `.agents/skills/ds-concept-check/scripts/tree.py`, `scripts/_paths.py`, `tests/_util.py`, `tests/test_tree.py`

**Interfaces:**
- Produces:
  - `Tree = list[str | None]`
  - `preorder(t) -> list[str]`, `inorder(t)`, `postorder(t)`, `levelorder(t)`
  - `height(t) -> int` (빈 트리 0, 노드 하나 1 — 강의 `get_height`), `node_count(t) -> int`
  - `evaluate(t) -> int` (연산자 `+ - * /`, 피연산자 정수 문자열, `/`는 C처럼 0 쪽 버림)
  - `lecture_number(t, label) -> int`, `parent_index(i) -> int` (= `i // 2`), `left_index(i) -> int`, `right_index(i) -> int`
  - `compute(spec: dict, tree: Tree | None) -> str` — `op` ∈ {`preorder`,`inorder`,`postorder`,`levelorder`,`height`,`node_count`,`evaluate`,`lecture_number`,`parent_index`,`left_index`,`right_index`}. 순서열은 `", "`로 잇는다.
  - `tree_svg(t, svg_id: str, aria_label: str) -> str` — `<svg id=… viewBox=… role="img" aria-label=…>`, 선 `<line class="fig-ink">`, 노드 `<circle class="fig-ink">`·`<text class="fig-text">`, `style=` 없음
  - `_paths.SKILL`, `_paths.REPO`, `_paths.DS_REVIEW_PACK` (`REPO/.agents/skills/ds-review-pack`), `_paths.find_nfc(directory: Path, name: str) -> Path | None`

- [ ] **Step 1: 실패하는 테스트 작성** — `tests/test_tree.py`

```python
T = ["A", "B", "C", "D", "E", None, "F"]          # A(B(D,E), C(-,F))
EXPR = ["+", "*", "/", "a", "b", "c", "d"]
NUM = ["-", "*", "/", "3", "4", "7", "2"]

def test_traversals():
    assert tree.preorder(T) == list("ABDECF")
    assert tree.inorder(T) == list("DBEACF")
    assert tree.postorder(T) == list("DEBFCA")
    assert tree.levelorder(T) == list("ABCDEF")
    assert tree.inorder(EXPR) == list("a*b+c/d")

def test_height_count():
    assert tree.height([]) == 0 and tree.height(["A"]) == 1 and tree.height(T) == 3
    assert tree.node_count(T) == 6

def test_evaluate_c_division():
    assert tree.evaluate(NUM) == 3 * 4 - 7 // 2          # 9
    assert tree.evaluate(["/", "-7", "2"]) == -3          # C 버림

def test_lecture_numbers():
    assert tree.lecture_number(T, "F") == 7
    assert (tree.parent_index(5), tree.left_index(3), tree.right_index(3)) == (2, 6, 7)

def test_compute_joins_sequences():
    assert tree.compute({"op": "postorder"}, T) == "D, E, B, F, C, A"
    assert tree.compute({"op": "parent_index", "arg": 5}, None) == "2"
    assert tree.compute({"op": "lecture_number", "arg": "F"}, T) == "7"

def test_svg_has_no_style_and_labels():
    svg = tree.tree_svg(T, "fig-q1", "트리 A")
    assert 'style=' not in svg and svg.count("<circle") == 6 and 'aria-label="트리 A"' in svg
```

- [ ] **Step 2: 실패 확인** — `python3 -m pytest .agents/skills/ds-concept-check/tests/test_tree.py -q` → `ModuleNotFoundError: tree`
- [ ] **Step 3: `tree.py`·`_paths.py`·`tests/_util.py` 구현** — `_util.py`는 `sys.path`에 `scripts/`를 넣고 `FIXTURES = TESTS / "fixtures"`를 둔다. SVG 배치는 깊이별 균등 분할(1102 복습문제 P1 그림과 같은 원 반지름 17, 글자 14).
- [ ] **Step 4: 통과 확인** — 같은 명령 → `6 passed`
- [ ] **Step 5: 커밋** — `git add .agents/skills/ds-concept-check && git commit -m "feat(ds-concept-check): add tree ops and compute"`

### Task 2: 카드 렌더와 채점 스크립트 이식

**Files:**
- Create: `scripts/render.py`, `scripts/interaction.py`, `assets/review-interaction.js`, `assets/review-interaction.css`, `assets/review-prompt.js`, `assets/SOURCE.md`, `tests/test_render.py`
- 복사 원본: `../생명과학/.claude/skills/bio-review-pack/scripts/review_interaction.py`, `.../assets/review-interaction.{js,css}`, `.../assets/review-prompt.js`

**Interfaces:**
- Consumes: `tree.tree_svg`, `_paths.DS_REVIEW_PACK`
- Produces:
  - `render.accepted_variants(canonical: str) -> list[str]` — `", "`로 나뉘는 순서열이면 `","`·`" "`·`""`·`"→"` 결합 변형(정답 자신 제외, 중복 제거), 아니면 `[]`
  - `render.card_html(item: dict, objective: dict, number: int) -> str`
  - `interaction.install(source: str, document_id: str) -> str` — 생명과학 `install`과 같고, 부트에서 `storage = null`(새로고침 초기화), 모델 오류가 있으면 `ValueError`
  - `interaction.build_model(source, document_id) -> dict`

카드 마크업(생명과학 `build_model`이 읽는 구조와 같아야 한다):
- 공통: `<article class="card" id="{id}" data-objective="{objective}">`, `<h3>Q{number}. {title}</h3>`, `<div class="problem">` 안에 `stem_html`, `tree`가 있으면 `<figure class="figure">{tree_svg}</figure>`, 그 아래 `<p class="source">{slide} · 확인: {concept}</p>`.
- mcq: `<ol class="choices">`에 `<li data-choice="A">` …; `<details class="solution"><summary>풀이 보기</summary><ol class="steps">`에 보기마다 `<li data-explains="A">` (오답은 `"{misconception}" — {why}`), `<p class="answer">정답: A</p></details>`.
- short: 속성 `data-format="short" data-short-answer="{json(canonical, accepted + accepted_variants, case_sensitive=false), html-escaped}"`, 문제 아래 `<div class="short-input"><label for="answer-{id}">답</label><input type="text" id="answer-{id}" autocomplete="off"><button class="btn check-answer" type="button">답 확인</button></div>`, 풀이는 `solution` 줄들을 `<ol class="steps">`로, `<p class="answer">정답: {canonical}</p>`.
- 보기 `text`·`why`·`title`·`concept`는 `html.escape`. `stem_html`은 HTML 그대로.

- [ ] **Step 1: 실패하는 테스트** — `tests/test_render.py`

```python
def test_accepted_variants():
    v = render.accepted_variants("A, B, D")
    assert {"A,B,D", "A B D", "ABD", "A→B→D"} <= set(v) and "A, B, D" not in v
    assert render.accepted_variants("2") == []

def test_mcq_card_builds_model():
    page = "<html><body><main>" + render.card_html(MCQ, OBJ, 1) + "</main></body></html>"
    m = interaction.build_model(page, "t")
    assert m["errors"] == [] and m["cards"]["q2"]["answer"] == "A"
    assert len(m["cards"]["q2"]["options"]) == 4

def test_short_card_builds_model():
    m = interaction.build_model("<body>" + render.card_html(SHORT, OBJ, 2) + "</body>", "t")
    assert m["cards"]["q1"]["format"] == "short" and "ABD" in m["cards"]["q1"]["answer"]["accepted"]

def test_option_text_is_escaped():
    item = {**MCQ, "options": [{**MCQ["options"][0], "text": "a<b && c"}] + MCQ["options"][1:]}
    html_ = render.card_html(item, OBJ, 1)
    assert "a&lt;b &amp;&amp; c" in html_
    assert interaction.build_model("<body>" + html_ + "</body>", "t")["errors"] == []

def test_install_boots_without_storage():
    out = interaction.install(TEMPLATE_WITH_CARD, "확인문제_t")
    assert "storage = null" in out and "review-interaction-model" in out
```

`MCQ`·`SHORT`·`OBJ`는 테스트 파일 상단 상수(데이터 모양 절의 예와 같은 형태, SHORT는 `canonical "A, B, D"`). `TEMPLATE_WITH_CARD`는 `DS_REVIEW_PACK/assets/review-template.html`을 `assemble.fill`로 채운 문자열(`PARTS`에 MCQ 카드 하나).

- [ ] **Step 2: 실패 확인** — `python3 -m pytest .agents/skills/ds-concept-check/tests/test_render.py -q` → `ModuleNotFoundError`
- [ ] **Step 3: 자산 복사와 구현** — 네 파일을 복사한다. `interaction.py`는 `from html2md import Builder, Node`를 `_paths`로 `DS_REVIEW_PACK/scripts`를 `sys.path`에 넣은 뒤 import하도록, `SKILL`은 이 스킬 폴더, `load_overrides`는 `{}` 반환, 부트의 `let storage = null; try { storage = window.sessionStorage; } catch {}`를 `const storage = null;`로 바꾼다(테스트는 `storage = null` 문자열로 확인). CSS 끝에 생명과학 `exam_practice.py:63`의 `.short-input` 규칙을 붙인다. `SOURCE.md`에 원본 경로·복사 날짜(2026-11-12)·바꾼 세 곳을 적는다.
- [ ] **Step 4: 통과 확인** — `5 passed`
- [ ] **Step 5: 커밋** — `git commit -m "feat(ds-concept-check): render cards and port review interaction"`

### Task 3: build.py — 확인문제 HTML 조립

**Files:**
- Create: `scripts/build.py`, `tests/test_build.py`, `tests/fixtures/mini/` (아래)

픽스처 `tests/fixtures/mini/9999/`:
- `복습문제_9999_Mini.html` — 카드 하나(`<article class="card" id="p1">`, 발문 `"다음 트리를 후위 순회한 결과를 쓰시오. 루트는 A이다."`)
- `.pack/자료_복습팩/manifest.json` — `course "자료구조및알고리즘이해"`, `range "9999"`, `slug "Mini"`, sections 하나에 topics `s0-a`·`s0-b`·`s0-c`, `preview_topic "s0-c"`, `forbidden_outside_preview ["이진 탐색 트리"]`
- `.pack/자료_복습팩/stt-summary.md` — 한 줄
- `.pack/자료_확인문제_9999_Mini/objectives.json` — 목표 o1(규칙 적용, s0-a), o2(이유, s0-b)
- `.pack/자료_확인문제_9999_Mini/items.json` — q1 short(parent_index 5 → "2"), q2 mcq(정답 A), q3 short(postorder, 3노드 트리 → "B, C, A", 목표 o1)

**Interfaces:**
- Consumes: `render.card_html`, `interaction.install`, `assemble.fill` (ds-review-pack), `_paths.find_nfc`
- Produces:
  - `class BuildError(RuntimeError)`
  - `load_source(src: Path) -> dict` — `{range, slug, objectives, items, manifest, pack_root}`. `src`는 `.../<range>/.pack/자료_확인문제_<range>_<slug>`. 형제 `자료_복습팩/manifest.json`·`stt-summary.md`를 NFC로 찾고, 없으면 `BuildError("팩이 없어 근거가 없습니다: <경로>")`
  - `output_name(range_: str, slug: str) -> str` = `f"확인문제_{range_}_{slug}.html"`
  - `render_page(src: Path) -> str`, `build(src: Path) -> Path` (팩 루트에 쓰고 경로 반환)
  - CLI `python3 build.py <src>` → 성공 시 경로 출력·exit 0, `BuildError`면 메시지·exit 1

`render_page` 값: 템플릿 `DS_REVIEW_PACK/assets/review-template.html`, `PAGE_TITLE = "{course} 확인문제 {range}"`, `DESCRIPTION`·`TITLE = "{range} 확인문제 — 이번 수업 개념 확인"`, `TOC`는 파트 하나 `<a href="#check">확인</a>`, `NOTE_HREF = 정리노트_{range}_{slug}.html`, `INTRO = "<p>이번 수업에서 처음 배운 개념을 {n}문항으로 확인해요. 고르면 바로 채점돼요.</p>"`, `PARTS = <section id="check"><h2>확인문제</h2>…카드(items 순서)…</section>`, `FOOTER = "<p>Claude가 강의 근거로 만든 문항이에요. 근거: 강의록·수업 녹음 요약.</p>"`, `SCRIPTS = ""`, `RANGE = "{range}-확인"`(복습문제의 푼 문제 기록과 키 분리). 이어서 `interaction.install(page, output_name without .html)`.

- [ ] **Step 1: 실패하는 테스트**

```python
def test_build_writes_root_html(tmp_path):
    root = copy_fixture(tmp_path)                      # tmp/9999
    out = build.build(root / ".pack/자료_확인문제_9999_Mini")
    assert out == root / "확인문제_9999_Mini.html"
    page = out.read_text(encoding="utf-8")
    assert "확인문제 9999" in page and page.count('class="card"') == 3
    assert interaction.build_model(page, "x")["errors"] == []

def test_build_finds_nfd_pack_dir(tmp_path):
    root = copy_fixture(tmp_path, nfd=True)            # 자료_복습팩·자료_확인문제_* 를 NFD 이름으로
    assert build.build(nfd_path(root, ".pack/자료_확인문제_9999_Mini")).exists()

def test_build_missing_pack_message(tmp_path):
    root = copy_fixture(tmp_path)
    shutil.rmtree(root / ".pack/자료_복습팩")
    with pytest.raises(build.BuildError, match="팩이 없어 근거가 없습니다"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")
```

`copy_fixture`·`nfd_path`는 `tests/_util.py`에 둔다.
- [ ] **Step 2: 실패 확인** → `ModuleNotFoundError: build`
- [ ] **Step 3: `build.py` 구현**
- [ ] **Step 4: 통과 확인** → `3 passed`, 그리고 `python3 .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo <tmp 아님>`는 Task 7에서 실제 팩으로 확인
- [ ] **Step 5: 커밋** — `git commit -m "feat(ds-concept-check): build concept-check html"`

### Task 4: check.py — 발행 전 규칙 검사

**Files:**
- Create: `scripts/check.py`, `tests/test_check.py`

**Interfaces:**
- Consumes: `build.load_source`, `tree.compute`, `_paths.find_nfc`
- Produces: `check(src: Path) -> list[str]` — 문제마다 `"[코드] <id>: <설명>"`, 없으면 `[]`. CLI는 `OK` 또는 문제 줄들, 문제가 있으면 exit 1.

코드와 판정(값은 Global Constraints 그대로):
- `[count]` 문항 0개 또는 16개 초과, 목표에 문항 0개, 목표에 문항 3개 이상
- `[topic]` `topic_id`가 manifest topics에 없음, 또는 `preview_topic`과 같음
- `[source]` `source.slide`가 `^S\d+ p\d+(–\d+)?$`가 아님
- `[format]` `kind`가 `절차 결과`·`규칙 적용`인데 문항이 `short`가 아님
- `[mcq-shape]` 보기 수 ≠ 4 또는 id가 `A B C D`가 아님, `answer`가 보기에 없음
- `[explain]` 보기 `why` 빈 값, 오답에 `misconception` 빈 값, 오답 `source`가 `stt:`·`note:`·`bank:`로 시작하지 않음
- `[balance]` 객관식 정답 위치 개수의 최댓값−최솟값 > 1 (객관식 4개 이상일 때만)
- `[negative]` 부정형 문항 수 × 4 > 전체 문항 수
- `[forbidden]` 제목·발문·보기·풀이에 manifest `forbidden_outside_preview` 낱말
- `[title-leak]` 객관식 정답 보기 `text`(공백 제거, 2자 이상)가 제목(공백 제거)에 포함
- `[compute]` short인데 `compute` 없음, 또는 `tree.compute(...) != answer.canonical`; mcq에 `compute`가 있으면 정답 보기의 `value`와 비교
- `[duplicate]` 발문 텍스트(태그 제거·공백 정규화) 중 20자 이상 구간이 같은 팩 `복습문제_*.html` 카드 발문 텍스트에 그대로 있음
- `[style]` `stem_html`에 `style=` 속성

- [ ] **Step 1: 실패하는 테스트** — 픽스처를 복사한 뒤 `items.json`을 한 곳씩 망가뜨리는 매개변수화 테스트

```python
@pytest.mark.parametrize("mutate, code", [
    (lambda d: d["items"][1]["options"].pop(), "[mcq-shape]"),
    (lambda d: d["items"][1]["options"][1].update(misconception=""), "[explain]"),
    (lambda d: d["items"][0]["answer"].update(canonical="3"), "[compute]"),
    (lambda d: d["items"][1].update(title=d["items"][1]["options"][0]["text"]), "[title-leak]"),
    (lambda d: d["items"][1].update(stem_html="<p>이진 탐색 트리에서</p>"), "[forbidden]"),
    (lambda d: d["items"][1].update(stem_html="<p>다음 트리를 후위 순회한 결과를 쓰시오. 루트는 A이다.</p>"), "[duplicate]"),
    (lambda d: d["items"][1].update(stem_html='<p style="color:red">x</p>'), "[style]"),
    (lambda d: d["items"].extend(dict(d["items"][0], id=f"x{i}") for i in range(14)), "[count]"),
])
def test_rule_fires(tmp_path, mutate, code):
    src = mutated_fixture(tmp_path, mutate)
    assert any(p.startswith(code) for p in check.check(src))

def test_fixture_is_clean(tmp_path):
    assert check.check(fixture_src(tmp_path)) == []

def test_negative_ratio(tmp_path):
    src = mutated_fixture(tmp_path, lambda d: d["items"][1].update(stem_html="<p>옳지 않은 것은?</p>"))
    assert any(p.startswith("[negative]") for p in check.check(src))   # 1×4 > 3
```

- [ ] **Step 2: 실패 확인** → `ModuleNotFoundError: check`
- [ ] **Step 3: `check.py` 구현**
- [ ] **Step 4: 통과 확인** → `10 passed`
- [ ] **Step 5: 커밋** — `git commit -m "feat(ds-concept-check): add pre-publish checks"`

### Task 5: blind.py — 블라인드 사본과 대조 장부

**Files:**
- Create: `scripts/blind.py`, `references/blind-brief.md`, `tests/test_blind.py`

**Interfaces:**
- Consumes: `build.load_source`
- Produces:
  - `item_hash(item: dict) -> str` — `json.dumps(item, sort_keys=True, ensure_ascii=False)`의 SHA-256
  - `make(src: Path, out: Path, only: set[str] | None = None) -> None` — 문항마다 `## q1. 제목`, 발문(태그 제거 텍스트, 그림은 `[그림: aria-label]`), 객관식이면 `A. …`~`D. …`, short면 `(값을 쓰시오)`. 정답·`why`·`misconception`·`solution`·`compute`는 넣지 않는다.
  - `parse_answers(text: str) -> dict[str, dict]` — `| 문항 | 고른 답 | 근거 | 이의 |` 표, 문항 id 중복이면 `ValueError`
  - `record(src, answers_md: Path, ledger: Path, round_no: int) -> dict` — 문항별 `{answer, objection, hash, round}`를 장부(JSON)에 병합
  - `status(src, ledger: Path) -> list[str]` — 장부에 없음 / 해시 불일치(수정됨) / 답 불일치(short는 `canonical`·허용답을 `NFC·trim·소문자`로 비교) / 이의 있음 을 `"<id>: <사유>"`로. 빈 리스트면 합격
  - CLI: `blind.py make <src> <out> [--only q1,q3]`, `blind.py record <src> <answers> <ledger> --round N`, `blind.py status <src> <ledger>`(OK 또는 줄들, 실패 exit 1)

`references/blind-brief.md`: 생명과학 `bio-webquiz-forecast/references/blind-brief.md`를 본떠 자구알용으로 쓴다 — 읽을 것은 사본과 `.pack/정리노트_<range>_<slug>.md`뿐, 정답 파일 금지, 문항마다 답 하나와 근거 토픽, 이의(다른 보기도 답 / 발문에 없는 조건 / 노트 밖 사실 / 제목·그림 라벨에 답 노출), 출력 표 형식.

- [ ] **Step 1: 실패하는 테스트**

```python
def test_make_hides_answers(tmp_path):
    src = fixture_src(tmp_path); out = tmp_path / "b.md"
    blind.make(src, out)
    text = out.read_text(encoding="utf-8")
    assert "## q2." in text and "A. " in text
    for leak in ("why", "정답", "misconception", "B, C, A"):
        assert leak not in text

def test_record_and_status_ok(tmp_path):
    src = fixture_src(tmp_path)
    write(tmp_path / "a.md", "| 문항 | 고른 답 | 근거 | 이의 |\n|---|---|---|---|\n| q1 | 2 | s0-a | |\n| q2 | A | s0-b | |\n| q3 | b c a | s0-a | |")
    blind.record(src, tmp_path / "a.md", tmp_path / "l.json", 1)
    assert blind.status(src, tmp_path / "l.json") == []

def test_status_flags_mismatch_and_objection(tmp_path): ...   # q2 → B, q1 이의 "부모 정의 모호" → 두 줄
def test_status_invalidates_changed_item(tmp_path):            # 합격 장부 뒤 q2 title 수정 → "q2: 수정됨"
    ...
```

- [ ] **Step 2: 실패 확인** → `ModuleNotFoundError: blind`
- [ ] **Step 3: `blind.py`·`blind-brief.md` 구현**
- [ ] **Step 4: 통과 확인** → `4 passed`
- [ ] **Step 5: 커밋** — `git commit -m "feat(ds-concept-check): add blind solve ledger"`

### Task 6: browser_check.py — 실제 조작 검사

**Files:**
- Create: `scripts/browser_check.py`, `tests/test_browser.py`

**Interfaces:**
- Consumes: `build.load_source` (문항·정답), 빌드된 HTML
- Produces: `check(html: Path, out: Path, shots: Path | None, *, src: Path, serve_root: Path | None = None) -> dict` — `serve_root` 기본은 `REPO`. `{"html", "sha256", "runs": [...], "failures": [...]}`를 `out`에 쓰고 반환. CLI `browser_check.py <html> --src <src> --out <json> [--shots <dir>]`, `failures`가 있으면 exit 1.

동작: 저장소 루트를 빈 포트 `http.server`로 띄우고 1280×900·375×812 × `emulate_media(color_scheme=light|dark)` 4회. 매 회:
- 콘솔 error 0, `.katex-error` 0, `document.documentElement.scrollWidth <= innerWidth`
- 객관식마다: 문항으로 이동 → 오답 보기 `.review-choice` 클릭 → `.review-status` 글자 있음·`.review-diagnostic:visible` ≥ 1 → `.review-reset` → `data-selected='true'` 0 → 정답 보기 클릭
- short마다: 허용답 중 소문자·공백 변형 하나(없으면 `canonical.lower()`)를 입력 → `.check-answer` → 상태 글자에 `정답` 포함
- 새로고침 → `.review-choice[data-selected='true']` 0, 입력값 빈칸
- 복기 버튼(`button:has-text("복기")`) ≥ 1
- `shots`가 있으면 회마다 첫 문항·마지막 화면 스크린샷

- [ ] **Step 1: 실패하는 테스트** (`@pytest.mark.skipif(not playwright_available())`)

```python
def test_browser_passes_on_fixture(tmp_path):
    root = copy_fixture(tmp_path)
    src = root / ".pack/자료_확인문제_9999_Mini"
    html = build.build(src)
    result = browser_check.check(html, tmp_path / "b.json", None, src=src, serve_root=tmp_path)
    assert result["failures"] == [] and len(result["runs"]) == 4
```
- [ ] **Step 2: 실패 확인** → `ModuleNotFoundError: browser_check`
- [ ] **Step 3: 구현** — 생명과학 `bio-webquiz-forecast/scripts/browser_check.py`의 `Run`·`route_external`(CDN KaTeX·Pretendard 로컬 대체가 필요하면 그대로) 구조를 참고해 새로 쓴다.
- [ ] **Step 4: 통과 확인** → `1 passed` (약 30초)
- [ ] **Step 5: 커밋** — `git commit -m "feat(ds-concept-check): add browser check"`

### Task 7: SKILL.md·작성 규칙·링크

**Files:**
- Create: `.agents/skills/ds-concept-check/SKILL.md`, `references/item-rules.md`, `tests/test_skill_files.py`, 링크 `.claude/skills/ds-concept-check`

`SKILL.md` 내용(frontmatter `name: ds-concept-check`, description: "자구알 수업 하나에서 새로 배운 개념을 확인하는 즉시 채점 HTML(확인문제)을 기존 복습팩 근거로 만들 때 사용한다. /ds-concept-check MMDD. 복습팩·문제설명·인터랙티브·채팅 퀴즈에는 사용하지 않는다."):
1. 준비: `복습노트/<MMDD>/.pack/자료_복습팩/{manifest.json,stt-summary.md}`와 `.pack/정리노트_*.md` 확인, 없으면 멈춤. `range`·`slug`는 manifest에서. `SRC = .pack/자료_확인문제_<range>_<slug>/`. 이미 있으면 `RUN/previous-<시각>/`에 백업.
2. 확인 목표: 메인 에이전트가 `objectives.json`을 쓴다(item-rules 1절). 6개 미만이면 보고서에 사유.
3. 문항: 작성자 1명(opus)에게 `item-rules.md` 브리프로 `items.json`을 쓰게 한다. 오답 오개념 출처는 STT 절·정리노트 토픽·`from_the_past/기출/문제은행.json` 같은 장 문항.
4. `check.py <SRC>` → OK까지(작성자에게 묶어 되돌림, 최대 2회).
5. `build.py <SRC>`.
6. 블라인드: `blind.py make` → `blind-brief.md`로 opus 1명 → `record` → `status`. 실패 문항만 고쳐 4단계부터, `--only`로 재풀이, 최대 2회.
7. `browser_check.py` → `SRC/browser.json`, 스크린샷은 RUN에. 스크린샷을 직접 열어 겹침·잘림 확인.
8. `python3 .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo <REPO>` → OK.
9. 보고: 경로, 목표 수, 문항 수(객관식 n · 입력 n), 정답 분포, 부정형 수, 블라인드 결과(고친 문항), 브라우저 결과, 미해결, 커밋 제안 `git add 복습노트/<MMDD> && git commit -m "docs(notes): add concept check <MMDD>"`.

`references/item-rules.md`: 위 데이터 모양 절, 목표 종류 5개와 형식 매핑, 제외 대상(이전 강의 복습·예고·금지어·일화·정리 토픽), 오답 출처 3종과 `source` 표기, 부정형 상한, 정답 위치 균등, `compute` op 목록과 `tree` 표기(레벨 배열 vs 강의 번호), 발문·보기 문체(해요체, 기존 카드 예: `복습노트/1102/복습문제_1102_Tree.html` P1), 수식은 `$…$`.

- [ ] **Step 1: 실패하는 테스트** — `tests/test_skill_files.py`

```python
def test_skill_mentions_every_script():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    for name in ("check.py", "build.py", "blind.py", "browser_check.py", "item-rules.md", "blind-brief.md"):
        assert name in text and any(SKILL.rglob(name))

def test_claude_link():
    link = REPO / ".claude/skills/ds-concept-check"
    assert link.is_symlink() and link.resolve() == SKILL.resolve()

def test_item_rules_lists_compute_ops():
    import tree
    rules = (SKILL / "references/item-rules.md").read_text(encoding="utf-8")
    for op in tree.OPS:            # Task 1의 compute가 받는 op 이름 튜플(이 Task에서 tree.py에 OPS 상수로 노출)
        assert f"`{op}`" in rules
```

- [ ] **Step 2: 실패 확인**
- [ ] **Step 3: 문서 작성, `tree.OPS` 노출, `ln -s ../../.agents/skills/ds-concept-check .claude/skills/ds-concept-check`**
- [ ] **Step 4: 전체 테스트** — `python3 -m pytest .agents/skills/ds-concept-check/tests -q` → 전부 통과
- [ ] **Step 5: 커밋** — `git commit -m "feat(ds-concept-check): add skill docs and link"`

### Task 8: 1102 시범 발행

**Files:**
- Create: `복습노트/1102/확인문제_1102_Tree.html`, `복습노트/1102/.pack/자료_확인문제_1102_Tree/{objectives.json,items.json,blind-ledger.json,browser.json}`

- [ ] **Step 1: 확인 목표** — SKILL.md 2단계. 예상 목표(설계 문서): 배열 인덱스 계산, 0번 칸을 쓰지 않는 이유, 편향 트리 배열 낭비, 링크 노드 구조, VLR·LVR·LRV 대응, 재귀와 내부 스택, 전위 출력, 수식 트리 중위, 디렉토리 용량 = 후위인 이유, 레벨 순회·큐·비표준, 수식 트리 후위 표기, evaluate 값, get_node_count 재귀식, get_height 기저·결과. S7 p7 복습과 `s3-*`는 넣지 않는다.
- [ ] **Step 2: 문항 작성 → `check.py`** → `OK`
- [ ] **Step 3: `build.py`** → `복습노트/1102/확인문제_1102_Tree.html`
- [ ] **Step 4: 블라인드** → `blind.py status` → `OK`
- [ ] **Step 5: 브라우저** → `failures: []`, 스크린샷 직접 확인
- [ ] **Step 6: `pack_layout.py check`** → `OK`, 그리고 `git status`로 1102 기존 파일(정리노트·복습문제·문제설명·PDF)이 바뀌지 않았는지 확인
- [ ] **Step 7: 보고서 작성 후 커밋** — `git add 복습노트/1102/확인문제_1102_Tree.html "복습노트/1102/.pack/자료_확인문제_1102_Tree" && git commit -m "docs(notes): add concept check 1102"` (push는 사용자 확인 뒤)
