# 테마 스크롤바 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 자구알 화면용 HTML 템플릿 3개와 발행된 결과물 27개에 생명과학 `66939ad` 와 같은 테마 스크롤바를 넣되, 이력 해시 기록은 한 바이트도 바꾸지 않는다.

**Architecture:** CSS 조각 하나를 `.panel-inner` 규칙 줄 아래에 연속 삽입한다. ds-problem-explain 템플릿은 `port-provenance.json` 의 `local_overrides` 로 변경을 등록한다. 결과물은 팩마다 `migration-2026-10-13-scrollbar.json` 으로 옛 해시→새 해시를 잇고, `pack_layout.current_digest` 를 기록 순서와 무관하게 고친 뒤 해시를 직접 비교하던 검사 3곳을 그 함수 경유로 바꾼다.

**Tech Stack:** HTML/CSS, Python 3 표준 라이브러리, pytest·unittest(`uv run -q --no-project --with pytest --with pymupdf python -m pytest`)

**Spec:** `docs/superpowers/specs/2026-10-13-themed-scrollbar-design.md`

## Global Constraints

- 라이트 토큰 `--scroll: #c9d0db; --scroll-hover: #9aa3b2;`, 다크 토큰 `--scroll: #3f414b; --scroll-hover: #5b5e6a;`
- 세로 8px(`.content`, `.panel-inner`), 가로 8px(`pre`, `.table-wrap`, `.katex-display`, ds-problem-explain 만 `table` 추가). `math-pan` 은 건드리지 않는다.
- 막대 테두리 `2px solid var(--bg)`, `pre` 만 `var(--surface)`.
- `--scrollbar: 16px` 는 그대로.
- 이력 JSON(`docs/verify/*.json`, `복습노트/*/.pack/**` 의 기존 `.json`)은 수정 금지. 새 파일은 `.pack/migration-2026-10-13-scrollbar.json` 뿐.
- 인쇄용 `assignment-cover/assets/cover.html`, `ds-review-pack/assets/pdf/ec2/*.html`, `tests/fixtures/**` 는 수정 금지. PDF 재생성 금지.
- 작업은 worktree `../자구알-themed-scrollbar`, 브랜치 `feat/themed-scrollbar`. `git add` 는 경로를 지정한다. 병합·push 는 사용자 요청 시에만.
- 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

- 삽입을 두 번 돌림 → 두 번째 실행은 아무 파일도 바꾸지 않고 기록도 쓰지 않아야 한다(Task 1·3 의 `test_insert_is_idempotent`).
- ds-problem-explain 템플릿에 override 가 두 개가 됨 → `test_render.py:38` 이 모든 override 의 `current_sha256` 을 지금 파일 해시와 비교하므로 깨진다. 벗겨 가며 비교하도록 고친다(Task 1).
- 기록 두 개가 같은 파일을 연달아 고침(문제설명 HTML 은 `.pack` 이전과 이번 두 번) → 파일명 정렬 순서와 무관하게 끝까지 이어져야 한다(Task 2 `test_current_digest_chains_records_in_any_order`).
- `before == after` 인 항목이나 서로를 가리키는 기록 → `current_digest` 가 무한 반복하지 않아야 한다(Task 2 `test_current_digest_stops_on_cycle`).
- 같은 팩에 `migration-2026-10-13-scrollbar.json` 이 이미 있음 → 덮어쓰지 않고 실패해야 한다(Task 3 스크립트의 assert).

---

## 공용 도구: 삽입 스크립트

Task 1 과 Task 3 이 같은 스크립트를 쓴다. 저장소에 커밋하지 않는다.

경로: `/private/tmp/claude-501/-Users-hyunjun-macbook-pro-Documents-Univ----/d81c7425-25b6-4197-bcf9-cba7f96244ff/scratchpad/insert_scrollbar.py`

CLI: `python3 insert_scrollbar.py [--record] FILE...`
- 앵커: `    .panel-inner { flex: 1 1 auto; min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding: var(--s4) var(--s4) var(--s6); }\n` — 파일마다 `assert count == 1`.
- `--scroll:` 이 이미 있으면 건너뛴다(출력 없음).
- 조각 선택: 경로에 `ds-problem-explain` 이 있거나 파일명이 `문제설명_` 으로 시작하면 EXPLAIN, 아니면 BASE.
- 바꾼 파일마다 `<path>\t<before sha256>\t<after sha256>` 를 stdout 에 쓴다.
- `--record`: 바꾼 파일을 팩 루트(`복습노트/<MMDD>`)별로 묶어 `<팩>/.pack/migration-2026-10-13-scrollbar.json` 을 쓴다. 파일이 이미 있으면 `assert` 로 멈춘다. 형식(들여쓰기 2, `ensure_ascii=False`, 끝 개행):
  ```json
  {"date": "2026-10-13", "reason": "themed scrollbar (bio-interactive 66939ad)", "moved": [],
   "rewritten": {"정리노트_1012_Queue.html": {"before": "…", "after": "…"}}}
  ```
  키는 팩 루트 기준 파일명(NFC).

BASE 조각(앵커 바로 뒤에 그대로 붙음, 각 줄 4칸 들여쓰기):

```css
    :root { --scroll: #c9d0db; --scroll-hover: #9aa3b2; }
    @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --scroll: #3f414b; --scroll-hover: #5b5e6a; } }
    :root[data-theme="dark"] { --scroll: #3f414b; --scroll-hover: #5b5e6a; }
    .content::-webkit-scrollbar, .panel-inner::-webkit-scrollbar { width: 8px; }
    :is(pre, .table-wrap, .katex-display)::-webkit-scrollbar { height: 8px; }
    :is(.content, .panel-inner, pre, .table-wrap, .katex-display)::-webkit-scrollbar-track { background: transparent; }
    :is(.content, .panel-inner, .table-wrap, .katex-display)::-webkit-scrollbar-thumb { background: var(--scroll); border-radius: 8px; border: 2px solid var(--bg); }
    pre::-webkit-scrollbar-thumb { background: var(--scroll); border-radius: 8px; border: 2px solid var(--surface); }
    :is(.content, .panel-inner, pre, .table-wrap, .katex-display)::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }
    @supports (scrollbar-color: auto) { :is(.content, .panel-inner, pre, .table-wrap, .katex-display) { scrollbar-width: thin; scrollbar-color: var(--scroll) transparent; } }
```

EXPLAIN 조각 = BASE 에서 `.katex-display)` 를 모두 `.katex-display, table)` 로 바꾼 것(5곳).

---

### Task 1: 템플릿 3개 + provenance

**Files:**
- Modify: `.agents/skills/ds-review-pack/assets/note-template.html`, `.agents/skills/ds-review-pack/assets/review-template.html`, `.agents/skills/ds-problem-explain/assets/note-template.html` (`.panel-inner` 줄 아래)
- Modify: `.agents/skills/ds-problem-explain/assets/port-provenance.json` (`local_overrides` 에 2개 추가)
- Modify: `.agents/skills/ds-problem-explain/tests/test_render.py:36-41`
- Modify: `.agents/skills/ds-review-pack/tests/test_skill_files.py` (클래스 추가)
- Create: `.agents/skills/ds-problem-explain/tests/test_scrollbar.py`
- Move in: `docs/superpowers/specs/2026-10-13-themed-scrollbar-design.md`, `docs/superpowers/plans/2026-10-13-themed-scrollbar.md`

**Interfaces:**
- Produces: 공용 삽입 스크립트(위 절), 기준선 실패 목록 `<scratchpad>/baseline-review-pack.txt`

- [ ] **Step 0: worktree 와 기준선**

```bash
cd /Users/hyunjun_macbook_pro/Documents/Univ/자구알
git worktree add ../자구알-themed-scrollbar -b feat/themed-scrollbar
mkdir -p ../자구알-themed-scrollbar/docs/superpowers/specs ../자구알-themed-scrollbar/docs/superpowers/plans
mv docs/superpowers/specs/2026-10-13-themed-scrollbar-design.md ../자구알-themed-scrollbar/docs/superpowers/specs/
mv docs/superpowers/plans/2026-10-13-themed-scrollbar.md ../자구알-themed-scrollbar/docs/superpowers/plans/
```
이후 모든 명령은 `../자구알-themed-scrollbar` 에서 실행한다. 기준선:
```bash
uv run -q --no-project --with pytest --with pymupdf python -m pytest -q -p no:cacheprovider .agents/skills/ds-review-pack/tests 2>&1 | grep FAILED | sort > <scratchpad>/baseline-review-pack.txt
```
Expected: 20줄(전부 `test_pdf_code`·`test_pdf_layout`·`test_pdf_template`·`test_pdf_ds_layout`·`test_pdf_cards` 의 브라우저 의존 실패). ds-problem-explain 은 `79 passed`.

- [ ] **Step 1: 실패하는 테스트 작성**

`ds-review-pack/tests/test_skill_files.py` 에 `class TestScrollbar(unittest.TestCase)` 를, `ds-problem-explain/tests/test_scrollbar.py` 에 pytest 함수를 만든다. 공통 단언(템플릿 `t` 하나당):
```python
assert len(re.findall(r'--scroll: #[0-9a-f]{6}; --scroll-hover: #[0-9a-f]{6};', t)) == 3
assert t.count('--scroll: #c9d0db; --scroll-hover: #9aa3b2;') == 1
assert t.count('--scroll: #3f414b; --scroll-hover: #5b5e6a;') == 2
assert '::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }' in t
assert 'pre::-webkit-scrollbar-thumb { background: var(--scroll); border-radius: 8px; border: 2px solid var(--surface); }' in t
assert 'scrollbar-color: var(--scroll) transparent;' in t
assert '--scrollbar: 16px;' in t
```
테스트 이름: `test_note_template_scrollbar`, `test_review_template_scrollbar`(ds-review-pack, 둘 다 `'katex-display, table)' not in t`), `test_explain_template_scrollbar`(ds-problem-explain, `t.count('.katex-display, table)') == 5`).

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest python -m pytest -q -p no:cacheprovider .agents/skills/ds-review-pack/tests/test_skill_files.py .agents/skills/ds-problem-explain/tests/test_scrollbar.py`
Expected: 3 failed (`assert 0 == 3`)

- [ ] **Step 3: 삽입 스크립트 작성 후 템플릿 3개에 적용**

`python3 <scratchpad>/insert_scrollbar.py <템플릿 3개>` — 3줄 출력. ds-problem-explain 줄의 before 는 `ce1ae742d818b1145a1364bfcb2c0284ae29c5dcd4ac43f3e17ec4c3a5cd4f1e` 여야 한다.

- [ ] **Step 4: 멱등성 확인**

같은 명령을 다시 실행. Expected: 출력 없음, `git diff --stat` 변화 없음.

- [ ] **Step 5: `test_render.py` 의 override 루프 수정**

36-41행을, 같은 destination 의 override 를 **최신부터** 순회하며 매번 `hashlib.sha256(original).hexdigest()==override['current_sha256']` 를 단언하고 `inserted_text` 를 1회 제거하는 형태로 바꾼다(42행 원본 해시 단언은 그대로). 바꾸기 전 파일 해시를 기록해 둔다(`f57d4bcb8413766d79422027c14892a916fb477221970f843d7c023fc07fc907` 이어야 함 — `tests/test_render.py` 의 기존 override 체인 마지막 `current_sha256`).

- [ ] **Step 6: `port-provenance.json` 에 override 2개 추가 (기존 항목 뒤)**

```json
{"destination": "assets/note-template.html",
 "base_sha256": "ce1ae742d818b1145a1364bfcb2c0284ae29c5dcd4ac43f3e17ec4c3a5cd4f1e",
 "current_sha256": "<Step 3 after>",
 "inserted_text": "<EXPLAIN 조각 그대로, 각 줄 끝 \n 포함>",
 "reason": "User approved 2026-10-13: themed scrollbar matching bio-interactive 66939ad; preserve original template bytes."},
{"destination": "tests/test_render.py",
 "base_sha256": "f57d4bcb8413766d79422027c14892a916fb477221970f843d7c023fc07fc907",
 "current_sha256": "<Step 5 후 해시>",
 "replacements": [{"old": "<36-41행 원문>", "new": "<Step 5 의 새 블록>"}],
 "reason": "2026-10-13 themed scrollbar: peel stacked template overrides newest-first."}
```
`files[]` 는 바꾸지 않는다. JSON 은 기존 파일의 들여쓰기·키 순서를 따른다.

- [ ] **Step 7: 테스트 통과 확인**

Run: `uv run -q --no-project --with pytest python -m pytest -q -p no:cacheprovider .agents/skills/ds-problem-explain/tests` → `80 passed` (기존 79 + `test_explain_template_scrollbar`).
Run: ds-review-pack 전체 → `grep FAILED | sort | diff <scratchpad>/baseline-review-pack.txt -` 출력 없음.

- [ ] **Step 8: Commit**

```bash
git add .agents/skills/ds-review-pack/assets/note-template.html .agents/skills/ds-review-pack/assets/review-template.html .agents/skills/ds-problem-explain/assets/note-template.html .agents/skills/ds-problem-explain/assets/port-provenance.json .agents/skills/ds-problem-explain/tests/test_render.py .agents/skills/ds-problem-explain/tests/test_scrollbar.py .agents/skills/ds-review-pack/tests/test_skill_files.py docs/superpowers/specs/2026-10-13-themed-scrollbar-design.md docs/superpowers/plans/2026-10-13-themed-scrollbar.md
git commit -m "feat(skills): themed panel scrollbar in note templates"
```

---

### Task 2: 기록 순서와 무관한 해시 연결

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/pack_layout.py:99-112`
- Modify: `.agents/skills/ds-review-pack/tests/test_pdf_delivery.py:13`, `.agents/skills/ds-review-pack/tests/explanation_delivery_checks.py:27`, `.agents/skills/ds-review-pack/tests/test_textbook_delivery.py:26`
- Test: `.agents/skills/ds-review-pack/tests/test_pack_layout.py`

**Interfaces:**
- Produces: `current_digest(path, digest: str) -> str` — 시그니처 그대로, 모든 `migration-*.json` 을 변화가 없을 때까지 반복 적용(최대 기록 수만큼).

- [ ] **Step 1: 실패하는 테스트 작성** (`PackLayoutTests` 안)

```python
def test_current_digest_chains_records_in_any_order(self):
    data = self.notes / "0103" / ".pack"; data.mkdir(parents=True)
    rec = lambda name, b, a: (data / name).write_text(json.dumps({"date": "2026-10-13", "moved": [], "rewritten": {"a.html": {"before": b, "after": a}}}), encoding="utf-8")
    rec("migration-2026-10-13.json", "h0", "h1")
    rec("migration-2026-10-13-scrollbar.json", "h1", "h2")
    self.assertEqual(pl.current_digest(self.notes / "0103" / "a.html", "h0"), "h2")

def test_current_digest_stops_on_cycle(self):
    # 같은 방식으로 h0→h1, h1→h0 두 기록. 반환값은 "h0" 또는 "h1" 이면 되고, 끝나야 한다.
```

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest python -m pytest -q -p no:cacheprovider .agents/skills/ds-review-pack/tests/test_pack_layout.py -k current_digest`
Expected: chains 테스트 FAIL (`'h1' != 'h2'`), cycle 테스트 PASS(지금은 한 번만 훑으므로)

- [ ] **Step 3: `current_digest` 구현**

기록을 한 번 읽어 `(rel 후보 키들, rewritten)` 목록으로 두고, 한 바퀴에 바뀐 것이 없거나 바퀴 수가 기록 수에 이르면 멈춘다. docstring 은 "기록 파일 순서와 무관" 을 한 줄 덧붙인다.

- [ ] **Step 4: 통과 확인**

같은 명령. Expected: 2 passed.

- [ ] **Step 5: 직접 비교 3곳을 `current_digest` 경유로**

- `test_pdf_delivery.py:13`: `self.assertEqual(current_digest(source,r['source_sha256']),digest(source))` (이미 import 됨)
- `explanation_delivery_checks.py:27`: `digest!=current_digest(src,item['source_sha256']) or digest!=current_digest(src,m['source_sha256'])`
- `test_textbook_delivery.py:26`: `self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),current_digest(file,ev['sha256']))`, 상단에 `from pack_layout import current_digest`

- [ ] **Step 6: 회귀 없음 확인**

Run: ds-review-pack 전체 → `grep FAILED | sort | diff <scratchpad>/baseline-review-pack.txt -` 출력 없음. (결과물이 아직 그대로라 세 곳은 동작이 같아야 한다.)

- [ ] **Step 7: Commit**

```bash
git add .agents/skills/ds-review-pack/scripts/pack_layout.py .agents/skills/ds-review-pack/tests/test_pack_layout.py .agents/skills/ds-review-pack/tests/test_pdf_delivery.py .agents/skills/ds-review-pack/tests/explanation_delivery_checks.py .agents/skills/ds-review-pack/tests/test_textbook_delivery.py
git commit -m "fix(ds-review): chain pack migrations regardless of file order"
```

---

### Task 3: 발행 결과물 27개 + 마이그레이션 기록

**Files:**
- Modify: `복습노트/*/{정리노트,복습문제,문제설명}_*.html` (27개)
- Create: `복습노트/*/.pack/migration-2026-10-13-scrollbar.json` (9개)

**Interfaces:**
- Consumes: 삽입 스크립트 `--record`(공용 도구), Task 2 의 `current_digest`

> 배경: 스크래치 사본에서 기록 없이 삽입하면 delivery 테스트 9개가 새로 실패했다(`test_pdf_delivery` 2, `test_problem_explain_delivery` 3, `test_textbook_delivery` 4). Step 3 에서 이 9개가 0 이 되어야 한다.

- [ ] **Step 1: 삽입 + 기록**

```bash
python3 <scratchpad>/insert_scrollbar.py --record 복습노트/*/*.html
```
Expected: 27줄 출력, `.pack/migration-2026-10-13-scrollbar.json` 9개 생성, 각 `rewritten` 키 3개.

- [ ] **Step 2: 멱등성·diff 확인**

- 같은 명령 재실행 → 출력 없음, 새 파일 없음. 스크립트는 팩에서 바꾼 파일이 0개면 그 팩의 기록을 쓰지 않으므로 이미 있는 기록의 assert 에 걸리지 않는다.
- `git diff --numstat -- 복습노트` → 27줄 모두 `10	0`.
- `git status --porcelain -- docs/verify '복습노트/*/.pack'` → `?? …/migration-2026-10-13-scrollbar.json` 9줄만.

- [ ] **Step 3: 테스트**

Run: ds-review-pack 전체 → 기준선과 diff 없음(새 실패 0). ds-problem-explain 전체 → 전부 통과.

- [ ] **Step 4: 브라우저 확인**

내장 브라우저로 `file:///<worktree 절대경로>/복습노트/1012/복습문제_1012_Queue.html` 을 열고:
```js
const s=()=>[getComputedStyle(document.querySelector('.content')).scrollbarColor,getComputedStyle(document.querySelector('pre')).scrollbarColor];
document.documentElement.dataset.theme='light'; const a=s();
document.documentElement.dataset.theme='dark'; const b=s(); [a,b]
```
Expected: 라이트 두 값 모두 `rgb(201, 208, 219) rgba(0, 0, 0, 0)`, 다크 두 값 모두 `rgb(63, 65, 75) rgba(0, 0, 0, 0)`. `문제설명_1012_Queue.html` 에서 `.content` 로 한 번 더.

- [ ] **Step 5: Commit**

```bash
git add -- '복습노트/*/정리노트_*.html' '복습노트/*/복습문제_*.html' '복습노트/*/문제설명_*.html' '복습노트/*/.pack/migration-2026-10-13-scrollbar.json'
git commit -m "docs(notes): themed scrollbar in existing note HTML"
```
