# 추적 데이터 → 그림 생성기 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 단계 추적을 상태 JSON 하나로 저작하면 정적 그림·재생기·글 목록이 같은 데이터에서 생성되게 하고, 두 스킬의 규칙·검사기가 이를 요구하게 하며, 1105 정리노트 3페이지를 첫 소비자로 옮긴다.

**Architecture:** `ds-review-pack/scripts/trace_figs.py`(표준 라이브러리)가 lint → 배치 → SVG → HTML 조각을 담당한다. 조각에는 `data-trace`·`data-trace-sha` 도장이 붙고, `check_html`과 문제설명 `mpe_cli build`가 저장된 JSON 으로 재렌더해 바이트 비교한다. 재생기는 미리 그린 단계 SVG 의 `hidden` 만 바꾼다.

**Tech Stack:** Python 3 표준 라이브러리, unittest/pytest(`python3 -m pytest`), 인라인 SVG, 바닐라 JS IIFE.

**Spec:** `docs/superpowers/specs/2026-11-12-trace-figures-design.md`

**Spec 조정(계획 단계):** 정리노트 대상에서 대표 단계 그림을 재생기 밖에 따로 두면 `.widget-static` 안의 같은 그림과 id·MD 그림이 중복된다. 그래서 정리노트는 "재생기(첫 단계가 보임) + `.widget-static` 대표 단계 + `ol.steps`", 문제설명은 "대표 단계 그림이 보임"으로 한다. 학생이 HTML 에서 보는 내용은 같다.

## Global Constraints
- Python 표준 라이브러리만. 외부 JS 라이브러리 금지.
- SVG 색은 클래스 `fig-ink`, `fig-accent`, `fig-dot`, `fig-text`, `fig-muted` 만. `style` 속성 0개. 글자는 `font-size="13"`. 화살표 머리는 `<path>`.
- 한도: 단계 ≤ 40, 트리 노드 ≤ 31, 배열 칸 ≤ 20, `key` 단계 2~4개.
- `text` 에 `$` 금지(노트 수식 검사와 충돌). `<`, `&` 는 HTML escape.
- id: 단계 SVG `trace-<id>-s<n>`(1부터), 대표 `trace-<id>-k<n>`, 정적 `widget-trace-<id>-static-<n>`, 재생기 `widget-trace-<id>`, 스크립트 `widget-trace-<id>-ui`.
- 도장: `data-trace-sha` = `sha256(json.dumps(trace, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())` 앞 12자.
- 강제 문턱: formal 레이어 `ol.steps` 의 `<li>` 5개 이상 → `data-trace` 필요. manifest `rules` 에 `"trace-v1"` 이 있을 때만.
- 재생기는 위젯 0~2개 한도에 세지 않는다.
- 문체: 사용자에게 보이는 글은 한국어 "~해요" 체.
- 작업은 git worktree `../자구알-trace-figs`(브랜치 `feat/trace-figs`)에서 한다. main 작업 트리에 다른 세션의 미추적 파일이 있다.

## Review Focus
1. 키가 숫자가 아닌 트리(수식 트리 `+`, `a`) — 배치는 키 값 정렬이 아니라 구조상 중위 순서여야 한다. → Task 2 `test_layout_uses_structure_not_key_order`.
2. 한 문서에 trace 두 개 — id·스크립트가 서로 간섭하지 않아야 한다. → Task 3 `test_two_players_do_not_collide`.
3. 큰 트리(31노드)를 375px 화면에서 볼 때 — 칸 너비를 줄여 viewBox 폭 ≤ 720 이어야 한다. → Task 2 `test_wide_tree_fits_width`.
4. 단계 글에 `<`, `&`, `$` — escape 되거나 lint 가 거부해야 한다. → Task 1 `test_lint_rejects_dollar`, Task 3 `test_text_is_escaped`.
5. JSON 은 고쳤는데 HTML 을 다시 만들지 않은 경우 — 검사기가 잡아야 한다. → Task 4 `test_stale_trace_fails`.

---

### Task 0: 작업 트리 준비

- [ ] **Step 1:** `git -C /Users/hyunjun_macbook_pro/Documents/Univ/자구알 worktree add ../자구알-trace-figs -b feat/trace-figs main`
- [ ] **Step 1b:** 이 계획과 Spec 은 main 작업 트리에 미추적 상태로 있다. 두 파일을 worktree 의 같은 경로로 복사하고 `git commit -m "docs(plans): add trace figures spec and plan"`.
- [ ] **Step 2:** 기준선. Run: `cd ../자구알-trace-figs && python3 -m pytest -q .agents/skills/ds-review-pack/tests/test_check_html.py .agents/skills/ds-review-pack/tests/test_manifest.py .agents/skills/ds-review-pack/tests/test_assemble.py .agents/skills/ds-review-pack/tests/test_html2md.py .agents/skills/ds-problem-explain/tests` — Expected: 모두 PASS(실패가 있으면 기록만 하고 이 계획 범위의 실패와 구분한다).

### Task 1: Trace 스키마와 lint

**Files:**
- Create: `.agents/skills/ds-review-pack/scripts/trace_figs.py`
- Create: `.agents/skills/ds-review-pack/tests/fixtures/trace/make_inorder_1105.py`, `.agents/skills/ds-review-pack/tests/fixtures/trace/inorder-1105.json`(앞 스크립트의 출력)
- Test: `.agents/skills/ds-review-pack/tests/test_trace_figs.py`

**Interfaces:**
- Produces: `class TraceError(ValueError)`(속성 `code: str`), `load(path: Path) -> dict`, `lint(trace: dict) -> list[str]`(오류 코드 목록, 빈 목록이면 통과), `trace_sha(trace: dict) -> str`.
- 오류 코드: `version`, `id`, `no-steps`, `too-many-steps`, `unknown-kind`, `unknown-structure`, `missing-node`(트리 l/r·cur·done·null_at·changed 가 없는 노드), `too-many-nodes`, `too-many-cells`, `key-count`, `dollar`.

- [ ] **Step 1: fixture 생성 스크립트.** `make_inorder_1105.py`(표준 라이브러리, 인자 = 출력 JSON 경로)는 19쪽 트리 — 구조 `t`(bintree, root `"18"`, nodes `18:{l:7,r:26}`, `7:{l:3,r:12}`, `26:{r:31}`, `31:{l:27}`, `3`·`12`·`27` 은 `{}`), `st`(stack, label `"미뤄 둔 노드"`), `out`(array, label `"출력"`, size 7) — 로 재귀 중위 순회를 실제로 실행하며 상태를 기록한다. 단계 경계는 노트 `s0-inorder` 의 `<li>` 14개와 같게 묶는다(`1105` 노트의 각 `<li>` 가 말하는 시점의 상태: `cur` = 그 단계에서 처리 중인 노드, `null_at` = 그 단계에서 확인한 빈 자식(3·4·6·7·9·11·12·13단계), `st` = 방문을 미룬 노드들, `out` = 지금까지 출력). `text` 는 그 `<li>` 문장을 그대로 넣고 key 는 1·5·8·14단계. 끝에서 `assert out == ["3","7","12","18","26","27","31"]`, 각 단계 `out` 이 다음 단계의 접두사인지 assert. 실행: `python3 .agents/skills/ds-review-pack/tests/fixtures/trace/make_inorder_1105.py .agents/skills/ds-review-pack/tests/fixtures/trace/inorder-1105.json`. 1단계는 `cur:"7", st:["18"], out:[]`, 14단계는 `cur:null, st:[], done` 7개여야 한다.
- [ ] **Step 2: 실패 테스트.**
```python
class TestLint(unittest.TestCase):
    def setUp(self): self.t = trace_figs.load(FIXTURES / "trace" / "inorder-1105.json")
    def test_fixture_is_clean(self): self.assertEqual(trace_figs.lint(self.t), [])
    def test_lint_codes(self):
        cases = {
            "missing-node": lambda t: t["structures"][0]["nodes"]["7"].update(l="99"),
            "key-count": lambda t: [s.pop("key", None) for s in t["steps"]],
            "too-many-steps": lambda t: t["steps"].extend([t["steps"][0]] * 27),
            "unknown-structure": lambda t: t["steps"][0]["state"].update(zz=[]),
            "dollar": lambda t: t["steps"][0].update(text="$x$"),
        }
        for code, mutate in cases.items():
            with self.subTest(code=code):
                t = copy.deepcopy(self.t); mutate(t)
                self.assertIn(code, trace_figs.lint(t))
    def test_lint_rejects_dollar(self):
        t = copy.deepcopy(self.t); t["steps"][3]["text"] = "비용은 $O(n)$"
        self.assertEqual(trace_figs.lint(t), ["dollar"])
        with self.assertRaises(trace_figs.TraceError): trace_figs.load(write_tmp(t))  # write_tmp: 임시 JSON 경로를 돌려주는 테스트 도우미
    def test_sha_is_stable_under_key_order(self):
        a = trace_figs.trace_sha(self.t); b = trace_figs.trace_sha(json.loads(json.dumps(self.t, sort_keys=False)))
        self.assertEqual(a, b); self.assertEqual(len(a), 12)
```
- [ ] **Step 3:** Run `python3 -m pytest -q .agents/skills/ds-review-pack/tests/test_trace_figs.py` → FAIL(`No module named trace_figs`).
- [ ] **Step 4:** `load`, `lint`, `trace_sha`, `TraceError` 구현. `load` 는 lint 오류가 있으면 첫 코드로 `TraceError` 를 던진다(`lint` 는 던지지 않는다).
- [ ] **Step 5:** 테스트 PASS 확인.
- [ ] **Step 6:** `git add` 세 파일 → `git commit -m "feat(ds-review-pack): add trace schema and lint"`

### Task 2: 배치와 단계 SVG

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/trace_figs.py`
- Test: `.agents/skills/ds-review-pack/tests/test_trace_figs.py`

**Interfaces:**
- Consumes: Task 1 의 `load`, `lint`.
- Produces: `tree_layout(structure: dict) -> dict[str, tuple[float, float]]`(노드 → (x, y)), `step_svg(trace: dict, index: int, svg_id: str, *, hidden: bool = False) -> str`, `shadow_svg(trace: dict, structure_id: str, svg_id: str) -> str`.

수치(이 값으로 고정): 노드 반지름 16, 층 높이 56, 칸 너비 `min(44, 680 / n)`(n = 트리 노드 수), 여백 20, 배열 칸 40×32, 스택 칸 52×28(트리 오른쪽 24px 띄움), 배열은 트리 아래 행마다 하나. 현재 노드: `fig-accent` 원 r=21 덧그림. 끝난 노드: 원 아래 `fig-dot` r=4. `null_at`: 해당 쪽 아래로 길이 24 의 `fig-ink` 선 `stroke-dasharray="4 3"` + `fig-muted` 글자 `NULL`. `changed`: `fig-accent` 원. 배열 `hi`: `fig-accent` 칸, `ptr`: 칸 아래 `fig-muted` 이름. list: 칸 + `<path>` 화살표, `edge_changed` 는 `fig-accent`. 모든 `<svg>` 에 `viewBox`, `role="img"`, `aria-label`=그 단계 `text`. `shadow_svg`: 트리 + 각 노드에서 아래 수직선까지 `fig-ink` 점선, 수직선 위 값 `fig-text`, 왼→오 `<path>` 화살표, aria-label `"나무의 숫자를 아래로 내리면 왼쪽부터 3, 7, …이 차례로 놓여요"`(값은 실제 중위 순서로 채움).

- [ ] **Step 1: 실패 테스트.**
```python
def test_layout_x_follows_inorder(self):
    pos = trace_figs.tree_layout(self.t["structures"][0])
    self.assertEqual(sorted(pos, key=lambda k: pos[k][0]), ["3","7","12","18","26","27","31"])
    self.assertEqual(pos["27"][1], pos["18"][1] + 3 * 56)
def test_layout_uses_structure_not_key_order(self):
    s = {"id":"t","kind":"bintree","root":"+","nodes":{"+":{"l":"*","r":"/"},"*":{"l":"a","r":"b"},"/":{"l":"c","r":"d"},"a":{},"b":{},"c":{},"d":{}}}
    pos = trace_figs.tree_layout(s)
    self.assertEqual(sorted(pos, key=lambda k: pos[k][0]), ["a","*","b","+","c","/","d"])
def test_wide_tree_fits_width(self):
    s = full_tree(31)  # 테스트 도우미: 완전 이진 트리, 키 "1".."31"
    svg = trace_figs.step_svg(single_step_trace(s), 0, "x")
    self.assertLessEqual(viewbox_width(svg), 720)
def test_step_svg_contract(self):
    svg = trace_figs.step_svg(self.t, 0, "trace-inorder-1105-s1")
    self.assertNotIn("style=", svg)
    self.assertEqual(set(re.findall(r'class="([^"]+)"', svg)) - {"fig-ink","fig-accent","fig-dot","fig-text","fig-muted"}, set())
    self.assertIn('aria-label="18에서는 왼쪽을 먼저 처리해요.', svg)
    self.assertIn(">18<", svg)  # 스택 칸
def test_null_marker(self):
    i = next(n for n, s in enumerate(self.t["steps"]) if s["state"]["t"].get("null_at"))
    self.assertIn(">NULL<", trace_figs.step_svg(self.t, i, "x"))
def test_shadow_order(self):
    svg = trace_figs.shadow_svg(self.t, "t", "fig-inorder-shadow")
    self.assertIn("3, 7, 12, 18, 26, 27, 31", svg)
```
- [ ] **Step 2:** FAIL 확인.
- [ ] **Step 3:** 구현. 중위 순위는 재귀 없이 명시 스택으로 계산(31노드 한도라 깊이 문제는 없지만 Task 7 스크립트와 구분).
- [ ] **Step 4:** PASS 확인.
- [ ] **Step 5:** `git commit -am "feat(ds-review-pack): render trace steps as svg"`

### Task 3: HTML 조각과 CLI

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/trace_figs.py`
- Test: `.agents/skills/ds-review-pack/tests/test_trace_figs.py`, `.agents/skills/ds-problem-explain/tests/test_trace_fragment.py`

**Interfaces:**
- Consumes: Task 2 `step_svg`, `shadow_svg`; Task 1 `load`, `trace_sha`.
- Produces: `render(trace: dict, target: str) -> str`(`target` ∈ `{"note","explain"}`), `main(argv) -> int` 서브커맨드 `lint PATH`, `render PATH --target note|explain`, `shadow PATH --structure ID --id SVG_ID`, `verify HTML --traces DIR`(Task 4 에서 채움).

조각 형태(바깥 래퍼 고정):
- note: `<div class="trace-block" data-trace="<id>" data-trace-sha="<sha>" data-trace-target="note">` + `.widget#widget-trace-<id>`(h4 `직접 해 보기: <title>`, `p.widget-help` = `"이전·다음을 누르면 한 단계씩 그림과 설명이 바뀌어요."`, `.controls` 인라인 버튼 3개 — [widget-rules.md](../../../.agents/skills/ds-review-pack/references/widget-rules.md) 의 버튼 스타일 그대로, id `trace-<id>-reset|prev|next`, 단계 SVG 전부(첫 장만 보이고 나머지 `hidden`), `p.readout` `<b id="trace-<id>-n">1/N</b> <span id="trace-<id>-text" aria-live="polite">첫 문장</span>`, `.widget-static hidden` 안에 key 단계 `figure.figure` + 표 `단계/설명`) + `<ol class="steps" data-trace="<id>">` 전 단계 `text` + `</div>` + `<script id="widget-trace-<id>-ui">(function(){…})();</script>`.
- explain: 같은 래퍼(`data-trace-target="explain"`) 안에 key 단계마다 `<figure class="figure"><svg id="trace-<id>-k<n>">…</svg><figcaption>단계 n. text</figcaption></figure>`. script·hidden·style·details 없음. `ol` 없음(설명 본문이 상태 표를 따로 쓴다).
- 래퍼 닫는 `</div>` 바로 뒤에 `<!-- /trace <id> -->` 표지(검증용 경계).

- [ ] **Step 1: 실패 테스트(ds-review-pack).**
```python
def test_note_fragment_parts(self):
    h = trace_figs.render(self.t, "note")
    self.assertEqual(h.count("<svg id=\"trace-inorder-1105-s"), 14)
    self.assertEqual(h.count(" hidden"), 13 + 1)  # 숨긴 단계 13 + widget-static
    self.assertEqual(re.findall(r"<li>(.*?)</li>", h), [s["text"] for s in self.t["steps"]])
    self.assertIn('data-trace-sha="' + trace_figs.trace_sha(self.t) + '"', h)
    self.assertEqual(h.count('id="widget-trace-inorder-1105-static-'), 4)
def test_two_players_do_not_collide(self):
    t2 = copy.deepcopy(self.t); t2["id"] = "inorder-b"
    doc = trace_figs.render(self.t, "note") + trace_figs.render(t2, "note")
    ids = re.findall(r' id="([^"]+)"', doc); self.assertEqual(len(ids), len(set(ids)))
def test_text_is_escaped(self):
    t = copy.deepcopy(self.t); t["steps"][0]["text"] = "a<b & c"
    self.assertIn("a&lt;b &amp; c", trace_figs.render(t, "note"))
def test_cli_render_matches_function(self):
    out = subprocess.run([sys.executable, str(SCRIPTS / "trace_figs.py"), "render", str(FIXTURES / "trace" / "inorder-1105.json"), "--target", "note"],
                         capture_output=True, text=True, check=True).stdout
    self.assertEqual(out, trace_figs.render(self.t, "note"))
```
- [ ] **Step 2: 실패 테스트(ds-problem-explain).** `test_trace_fragment.py`: `sys.path` 에 `../../ds-review-pack/scripts` 추가 후 `render(t, "explain")` 을 `mpe_shared.parse` 로 파싱해 `markup_errors(root)` == `[]`, `<script` 없음, `<figure` 4개.
- [ ] **Step 3:** 두 테스트 FAIL 확인.
- [ ] **Step 4:** `render`, CLI `lint|render|shadow` 구현. 재생기 JS: 상태 `i`, `show(i)` 가 단계 SVG 의 `hidden` 토글·`n/N`·문장 갱신·이전/다음 `disabled` 처리. 전역 변수 없음.
- [ ] **Step 5:** PASS 확인.
- [ ] **Step 6:** `git add` → `git commit -m "feat(ds-review-pack): emit trace fragments for notes and explanations"`

### Task 4: 검증과 check_html 통합

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/trace_figs.py`
- Modify: `.agents/skills/ds-review-pack/scripts/check_html.py:260-278`(check_common), `:371-377`(check_pack), `:380-`(main)
- Modify: `.agents/skills/ds-review-pack/scripts/manifest.py:17-22`
- Test: `.agents/skills/ds-review-pack/tests/test_trace_figs.py`, `test_check_html.py`, `test_manifest.py`

**Interfaces:**
- Produces: `trace_figs.verify(html: str, traces_dir: Path) -> list[tuple[str, str]]`(`(code, trace id)` 목록; code ∈ `trace-missing`, `trace-stale`). `check_common(doc, source, path, *, rules: frozenset[str] = frozenset(), traces_dir: Path | None = None)`. 기본 `traces_dir` = `Path(path).parent / ".pack" / "자료_복습팩" / "traces"`. CLI `check_html.py --traces DIR`.
- 새 Problem 코드: `trace-missing`, `trace-stale`, `trace-required`.
- manifest: 선택 최상위 키 `rules: list[str]`(필수 아님, 원소는 문자열).

`verify`: `<div class="trace-block" data-trace="X" … data-trace-target="T">` 부터 `<!-- /trace X -->` 까지를 잘라 `render(load(traces_dir/f"{X}.json"), T)` 의 같은 구간과 비교. 스크립트가 조립 시 `</body>` 앞으로 옮겨지므로 비교 구간은 표지까지(스크립트 제외)이고, 스크립트는 `<script id="widget-trace-X-ui">` 를 문서 어디서든 찾아 따로 비교한다.

`trace-required`: `rules` 에 `"trace-v1"` 이 있을 때, `<div class="layer formal">` 안의 `<ol class="steps"` 중 `data-trace` 없고 `<li>` 5개 이상인 것마다 Problem(where=토픽 id).

- [ ] **Step 1: 실패 테스트.**
```python
def test_stale_trace_fails(self):  # test_trace_figs
    d = tmpdir(); json.dump(self.t, open(d/"inorder-1105.json","w"), ensure_ascii=False)
    h = trace_figs.render(self.t, "note")
    self.assertEqual(trace_figs.verify(h, d), [])
    self.t["steps"][2]["text"] += "!"; json.dump(self.t, open(d/"inorder-1105.json","w"), ensure_ascii=False)
    self.assertEqual(trace_figs.verify(h, d), [("trace-stale", "inorder-1105")])
def test_missing_json(self):
    self.assertEqual(trace_figs.verify(trace_figs.render(self.t, "note"), tmpdir()), [("trace-missing", "inorder-1105")])
```
`test_check_html.py`:
```python
def test_trace_required_only_with_rule(self):
    ol = "<ol class=\"steps\">" + "<li>x</li>" * 5 + "</ol>"
    src = f'<html lang="ko"><body><article class="topic" id="t"><div class="layer formal">{ol}</div></article></body></html>'
    doc = check_html.parse_html(src)
    codes = lambda r: [p.code for p in check_html.check_common(doc, src, Path("정리노트_9999_X.html"), rules=r)]
    self.assertNotIn("trace-required", codes(frozenset()))
    self.assertIn("trace-required", codes(frozenset({"trace-v1"})))
def test_four_steps_allowed(self): ...  # <li> 4개 + trace-v1 → trace-required 없음
def test_existing_notes_unchanged(self):  # 복습노트/*/정리노트_*.html 전부 check_common(rules 없음) 결과에 trace-* 코드 0
```
`test_manifest.py`: `rules` 없음·`["trace-v1"]` 통과, `"trace-v1"`(문자열)·`[1]` 거부.
- [ ] **Step 2:** FAIL 확인.
- [ ] **Step 3:** 구현. `check_pack` 은 `rules=frozenset(m.get("rules", []))` 를 노트에만 넘긴다.
- [ ] **Step 4:** Run `python3 -m pytest -q .agents/skills/ds-review-pack/tests/test_trace_figs.py .agents/skills/ds-review-pack/tests/test_check_html.py .agents/skills/ds-review-pack/tests/test_manifest.py` → PASS.
- [ ] **Step 5:** `git commit -am "feat(ds-review-pack): verify trace fragments in check_html"`

### Task 5: 조립·MD 변환 경로

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/assemble.py:105-117`(assemble)
- Test: `.agents/skills/ds-review-pack/tests/test_assemble.py`, `test_html2md.py`

**Interfaces:**
- Consumes: Task 3 `render`.
- Produces: `assemble()` 가 `RUN/traces/*.json` 이 있으면 `<out>/.pack/자료_복습팩/traces/` 로 복사(같은 이름 덮어씀, 없으면 아무것도 안 함).

- [ ] **Step 1: 실패 테스트.** `test_assemble.py`: mini-run 복사본에 `traces/inorder-1105.json` 과, 섹션 조각에 `render(t,"note")` 를 넣고 조립 → 출력 `.pack/자료_복습팩/traces/inorder-1105.json` 존재, `check_html.check_pack` 에 `trace-*` 코드 없음, 스크립트 `widget-trace-inorder-1105-ui` 가 `</body>` 앞에 있음. `test_html2md.py`: 같은 노트를 `html2md` 로 변환 → `figures_<range>/widget-trace-inorder-1105-static-1.svg`~`-4.svg` 생성, MD 에 `trace-inorder-1105-s2` 그림 없음(숨긴 단계는 MD 로 안 나감), MD 에 단계 문장 14줄.
- [ ] **Step 2:** FAIL 확인.
- [ ] **Step 3:** `assemble` 복사 구현. html2md 가 위젯을 `.widget-static` 로 바꾸므로 html2md 는 수정이 필요 없을 것으로 예상한다. 테스트가 실패하면 원인(예: `ol` 이 `.trace-block` 안에 있어 누락)을 고치는 최소 수정을 `html2md.py` 에 한다.
- [ ] **Step 4:** PASS 확인.
- [ ] **Step 5:** `git commit -am "feat(ds-review-pack): carry traces through assemble and md export"`

### Task 6: 문제설명 통합

**Files:**
- Modify: `.agents/skills/ds-problem-explain/scripts/mpe_cli.py:98-`(build), `mpe_render.py:155`(build_explanation 시그니처)
- Test: `.agents/skills/ds-problem-explain/tests/test_trace_fragment.py`

**Interfaces:**
- Consumes: `trace_figs.verify`(경로: `Path(__file__).resolve().parents[2] / "ds-review-pack" / "scripts"` 를 `sys.path` 에 넣어 import. 없으면 `ExplainError("trace 생성기(ds-review-pack/scripts/trace_figs.py)가 없어요")`).
- Produces: `build_explanation(pack, fragments, stage, repo, traces: Path | None = None)` — `traces` 가 있으면 `data_dir/"traces"` 로 복사(manifest `files` 목록 계산 전에). `mpe_cli.build` 는 `folder/"traces"` 가 있으면 조각마다 `verify` 하고 오류 시 `ExplainError("<pN>: trace-stale <id>")`, 그다음 `traces=folder/"traces"` 로 호출.

- [ ] **Step 1: 실패 테스트.** 합성 pack(`helpers.pack`)의 조각 하나에 `render(t,"explain")` 를 넣고 traces 폴더와 함께 build → 성공, 산출 `data_dir/traces/inorder-1105.json` 존재. JSON 을 바꾼 뒤 build → `ExplainError` 메시지에 `trace-stale`.
- [ ] **Step 2:** FAIL 확인.
- [ ] **Step 3:** 구현.
- [ ] **Step 4:** Run `python3 -m pytest -q .agents/skills/ds-problem-explain/tests` → PASS(기준선 대비 새 실패 0).
- [ ] **Step 5:** `git commit -am "feat(ds-problem-explain): verify and keep trace data"`

### Task 7: 규칙 문서

**Files:**
- Create: `.agents/skills/ds-review-pack/references/trace-figures.md`
- Modify: `.agents/skills/ds-review-pack/references/content-rules.md:61,76-83`, `references/widget-rules.md:3-6`, `SKILL.md`(3단계 작성, 8단계 저장 목록, 2단계 manifest), `references/manifest-guide.md`, `.agents/skills/ds-problem-explain/references/authoring.md:45`
- Test: `.agents/skills/ds-review-pack/tests/test_skill_files.py`

내용(정확한 문장):
- `trace-figures.md`: 스키마 표(Spec 의 Trace JSON 절), 한도, 작성 순서 4줄(① `RUN/work/trace_<id>.py` 가 실제 알고리즘을 돌려 `RUN/traces/<id>.json` 을 쓴다 ② `python3 "$SKILL/scripts/trace_figs.py" lint` ③ `render --target note` 출력을 formal 레이어에 그대로 붙인다(손으로 고치지 않는다) ④ 고칠 때는 JSON 을 고치고 다시 render), fixture `tests/fixtures/trace/inorder-1105.json` 을 예제로 가리킴.
- content-rules formal 문체 줄(61행) 뒤에 추가: "- 5단계 이상 상태 추적은 [trace 생성기](trace-figures.md)로 만든다. 손으로 쓴 `ol.steps` 는 4단계까지만 쓴다. 생성 조각은 손으로 고치지 않는다."
- content-rules SVG 절 첫 줄 뒤에 추가: "- 실제 예제(트리·배열·스택·리스트)의 상태는 formal 레이어에서 trace 생성기 그림으로 보여 준다. eli5 그림은 비유여도 된다."
- widget-rules "언제" 첫 줄 뒤: "- trace 생성기 재생기(`widget-trace-*`)는 이 한도에 세지 않는다."
- SKILL.md 2단계 manifest 절: "- 신규 팩 manifest 에 `\"rules\": [\"trace-v1\"]` 을 넣는다." / 3단계 브리프 줄: "- 추적 토픽 작성자에게 `<RUN>/traces/` 와 [trace 생성기](references/trace-figures.md)를 알려 준다." / 9단계 저장 문장의 목록에 `traces/` 추가.
- manifest-guide: `rules` 선택 키 한 줄.
- authoring.md 45행 "자료구조 추적은 연산별 상태 표와 불변식을 보여 줘요." → "자료구조 추적은 연산별 상태 표와 불변식을 보여 주고, 5단계 이상이면 `RUN/<대상>/traces/<id>.json` 을 만들어 `trace_figs.py render --target explain` 그림을 붙여요."

- [ ] **Step 1:** `test_skill_files.py` 에 실패 테스트: `trace-figures.md` 존재, SKILL.md·content-rules·widget-rules 에서 `trace-figures.md` 링크가 실제 파일로 풀림, content-rules 에 "4단계까지만" 문자열.
- [ ] **Step 2:** FAIL 확인 → 문서 작성 → PASS 확인.
- [ ] **Step 3:** `git commit -am "docs(ds-review-pack): require trace figures for long traces"`

### Task 8: 첫 소비자 — 1105 정리노트 3페이지

**Files:**
- Create: `복습노트/1105/.pack/자료_복습팩/traces/trace_inorder_1105.py`, `…/traces/inorder-1105.json`
- Modify: `복습노트/1105/정리노트_1105_Tree.html`(`article#s0-inorder`, `</body>` 앞 스크립트)
- Regenerate: `복습노트/1105/.pack/정리노트_1105_Tree.md`, `.pack/figures_1105/`(새 `fig-inorder-shadow.svg`, `fig-inorder-blocks.svg`, `widget-trace-inorder-1105-static-1~4.svg`; `fig-inorder-desk.svg` 삭제)

- [ ] **Step 1: 생성 스크립트 보관.** Task 1 의 `make_inorder_1105.py` 를 `복습노트/1105/.pack/자료_복습팩/traces/trace_inorder_1105.py` 로 복사(같은 내용, 출력 경로만 인자로 받음).
- [ ] **Step 2:** Run `python3 복습노트/1105/.pack/자료_복습팩/traces/trace_inorder_1105.py 복습노트/1105/.pack/자료_복습팩/traces/inorder-1105.json && python3 .agents/skills/ds-review-pack/scripts/trace_figs.py lint 복습노트/1105/.pack/자료_복습팩/traces/inorder-1105.json` → 출력 없음, 종료 0. `cmp` 로 fixture JSON 과 바이트가 같은지 확인.
- [ ] **Step 3: 노트 수정(백업 먼저: `cp` 원본 → scratchpad).**
  - eli5: `p.lead` = "나무에 달린 숫자를 바닥으로 똑바로 내리면 작은 수부터 차례로 줄을 서요.", 두 번째 `<p>` 삭제, 그림 = `trace_figs.py shadow … --structure t --id fig-inorder-shadow`, figcaption = "왼쪽부터 읽으면 크기순이에요." (eli5 3문장)
  - formal: LVR 정의 문단 다음에 `fig-inorder-blocks` 손 SVG — `[3 7 12] | 18 | [26 27 31]` 큰 테두리 세 칸(가운데 18 은 `fig-accent`), 왼쪽 칸 안에 `[3] | 7 | [12]`, 오른쪽 칸 안에 `[] | 26 | [27 31]` 작은 칸, 그 안에 `[27] | 31 | []`; aria-label 은 이 구조를 글로 적는다(테두리·선 용어 규칙 준수); figcaption "왼쪽 칸·가운데·오른쪽 칸 순서가 칸 안에서도 똑같이 반복돼요."
  - 연결 목록 문단 다음의 기존 `<ol class="steps">` 를 `render --target note` 조각으로 교체, 스크립트는 `</body>` 앞 기존 스크립트들 뒤로.
  - `.sum` 용어에 `<dt>그림자로 읽기</dt><dd>나무의 키를 아래로 내려 왼쪽부터 읽으면 중위 순회 출력과 같아요. 이진 탐색 트리에서 이 순서는 오름차순이에요.</dd>` 추가.
- [ ] **Step 4: 기계 검사.** Run:
  - `python3 .agents/skills/ds-review-pack/scripts/check_html.py --manifest 복습노트/1105/.pack/자료_복습팩/manifest.json --note 복습노트/1105/정리노트_1105_Tree.html --review 복습노트/1105/복습문제_1105_Tree.html` → `OK`
  - `python3 .agents/skills/ds-review-pack/scripts/html2md.py 복습노트/1105/정리노트_1105_Tree.html 복습노트/1105/복습문제_1105_Tree.html --check` → `OK`
  - `git status --short 복습노트/1105` → 복습문제 MD·문제설명 파일 변화 0
  - `python3 .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo .` → `OK`
- [ ] **Step 5: 브라우저 검사.** `python3 -m http.server` 빈 포트 → 내장 브라우저로 1280×900·375×812 × light/dark: 3페이지에서 [다음] 13번·[이전]·[처음부터] 동작, `1/14`→`14/14`, NULL 표시가 3단계에서 보임, 375px 가로 스크롤 없음, 다크모드에서 선·점 보임, 요약 패널에 "그림자로 읽기", 콘솔 오류 0. 서버 종료.
- [ ] **Step 6:** `git add 복습노트/1105` → `git commit -m "docs(notes): visualize inorder trace in 1105"`

### Task 9: 마무리

- [ ] **Step 1:** Run `python3 -m pytest -q .agents/skills/ds-review-pack/tests .agents/skills/ds-problem-explain/tests` → Task 0 기준선 대비 새 실패 0(브라우저 테스트가 환경 때문에 건너뛰어지면 그대로 기록).
- [ ] **Step 2:** 사용자에게 보고: 브랜치 `feat/trace-figs` 커밋 목록, 바뀐 3페이지 스크린샷, 남은 이주 대상 41토픽·111문항. 병합·push 는 사용자 확인 후.
