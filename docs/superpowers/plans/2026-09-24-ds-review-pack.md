# 자구알 복습팩 스킬 (`ds-review-pack`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 머신러닝기초 `ml-review-pack`을 자구알 저장소로 포크해, STT·강의록으로 정리노트를 만들고 기출 문제은행에서 복습문제를 고르는 `ds-review-pack` 스킬을 만든다.

**Architecture:** ML 스킬(커밋 `80307b8`)의 스크립트·템플릿·테스트를 그대로 복사한 뒤 과목 의존 부분만 바꾼다(과목명, `<pre>` 코드 블록, 문구). 기출은 `bank` 모드가 한 번 전사해 `from_the_past/기출/문제은행.json`에 두고, 새 스크립트 `bank.py`가 스키마 검사·후보 선별·manifest 대조를 맡는다. 복습팩 절차 0~9단계는 ML과 같다.

**Tech Stack:** Python 3.14 표준 라이브러리(unittest, json, argparse), PyMuPDF(`fitz`, 스킬 실행 시), `cc`(정답 검증), KaTeX CDN(템플릿).

**Spec:** `/Users/hyunjun_macbook_pro/Documents/Univ/자구알/docs/superpowers/specs/2026-09-24-ds-review-pack-design.md`

## Global Constraints

- 스킬 이름 `ds-review-pack`, 위치 `<저장소>/.claude/skills/ds-review-pack/`.
- 과목명(manifest `course`, 문서): `자료구조및알고리즘이해`. 교수: `이정원 교수님`.
- 원본: `/Users/hyunjun_macbook_pro/Documents/Univ/머신러닝기초` 저장소 커밋 `80307b8`의 `.claude/skills/ml-review-pack`. 원본 저장소에는 아무것도 쓰지 않는다.
- 작업은 worktree `/Users/hyunjun_macbook_pro/Documents/Univ/자구알-ds-review-pack`(브랜치 `feat/ds-review-pack`)에서 한다. 아래 명령의 `$WT`는 이 경로, `$SK`는 `$WT/.claude/skills/ds-review-pack`이다. 셸 상태는 호출 사이에 이어지지 않으므로 실행할 때마다 절대 경로로 바꿔 쓰거나 같은 명령 앞에 `WT=… SK=…`를 붙인다.
- 테스트 실행: `python3 -m unittest discover -s "$SK/tests"` (표준 라이브러리만, 저장소 데이터 불필요).
- 템플릿 변경은 N2 범위만: `pre`/`code` CSS, 스와이프 제외 목록에 `pre`, 복습문제 패널 문구 "교과서 원문" → "기출 원문". 그 밖의 디자인은 건드리지 않는다.
- 기출 선별 규칙: 출제자 `이정원` > `미상` > 그 밖, 유형 `trace`·`code-read` > `blank`·`short`·`code-write` > `essay` > `ox`, OX 최대 2개, 목표 8~12문항, 원본이 8개 미만이면 변형(`partC`)으로 8개까지, 최소 4문항.
- 은행 `reviewed`: `text`·`hwp`·`txt` 원본은 `true`, `scan`·`photo` 원본은 사용자 검수 전 `false`. `reviewed: false` 원본의 문항은 선별하지 않는다.
- 문서·주석은 한국어. 코드 식별자·경로는 원문.
- 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

---

## 파일 구조

| 파일 | 책임 | 만드는 Task |
|---|---|---|
| `SKILL.md` | 두 모드(`bank`, 복습팩)의 절차 | 1(프론트매터), 6(본문) |
| `assets/note-template.html`, `assets/review-template.html` | 페이지 틀(ML 복사 + N2 변경) | 1, 3 |
| `assets/SOURCE.md` | 복사 출처 기록 | 1 |
| `scripts/assemble.py` | 조각 → 페이지 조립(과목명은 manifest에서) | 1 |
| `scripts/manifest.py`, `scripts/check_html.py` | manifest 검사, 기계 검사(변경 없음) | 1 |
| `scripts/html2md.py` | HTML → MD(`<pre>` → 펜스) | 2 |
| `scripts/bank.py` | 문제은행 검사·선별·manifest 대조 | 4 |
| `references/content-rules.md`, `card-rules.md`, `manifest-guide.md`, `problem-selection.md`, `stt-summary-prompt.md`, `review-prompt.md`, `widget-rules.md`, `browser-check.md` | 작성자·리뷰어 브리프와 규칙 | 5 |
| `references/bank-build.md` | 문제은행 구축 규칙·전사 브리프 | 6 |
| `tests/*` | 회귀 테스트 | 1~6 |

---

### Task 0: 작업 공간 준비

**Files:** 없음 (git worktree만)

- [ ] **Step 1: 동료 세션 확인**

`ListAgents`로 같은 저장소(`자구알`)에서 도는 다른 세션이 있는지 본다. 있으면 그 세션이 main에 커밋할 수 있으므로 반드시 worktree에서 작업한다(아래 그대로).

- [ ] **Step 2: worktree 만들기**

```bash
git -C /Users/hyunjun_macbook_pro/Documents/Univ/자구알 worktree add ../자구알-ds-review-pack -b feat/ds-review-pack
```
Expected: `Preparing worktree (new branch 'feat/ds-review-pack')`.

worktree에는 추적 파일만 있다. `STT/`, `자료구조_강의록_2026/`, `from_the_past/기출/`, `docs/`는 원 트리에만 있고, 이 계획과 스펙도 원 트리 절대 경로로 읽는다. 테스트는 이 데이터가 필요 없다.

---

### Task 1: 스킬 복사와 과목명 일반화

**Files:**
- Create: `$SK/**` (ML 스킬 복사), `$SK/assets/SOURCE.md`
- Delete: `$SK/assets/backup-20260924-165016/`, `$SK/tests/test_regression_0909_0916.py`, `$SK/tests/fixtures/manifest-0909-0916.json`
- Modify: `$SK/scripts/assemble.py:64,86`, `$SK/SKILL.md:1-4`, `$SK/tests/test_manifest.py:22-23`, `$SK/tests/test_assemble.py:30,42`, `$SK/tests/test_check_html.py:106`, `$SK/tests/test_skill_files.py:22-28`, `$SK/tests/_util.py:15`, `$SK/tests/fixtures/mini-run/manifest.json`, `$SK/tests/fixtures/mini-run/cards/p1.html`, `$WT/.gitignore`

**Interfaces:**
- Produces: `assemble.assemble(run_dir, out_dir) -> (note_path, review_path)` — 페이지 `<title>`이 `f"{m['course']} 정리노트 {m['range']}"`, `f"{m['course']} 복습문제 {m['range']}"`가 된다. 픽스처 `mini-run`의 `course`는 `"자료구조및알고리즘이해"`, 문제 `p1`의 `source`는 `"2016-final-ljw-q1"`.

- [ ] **Step 1: ML 스킬을 커밋 기준으로 복사**

```bash
ML=/Users/hyunjun_macbook_pro/Documents/Univ/머신러닝기초
WT=/Users/hyunjun_macbook_pro/Documents/Univ/자구알-ds-review-pack
mkdir -p "$WT/.claude/skills"
git -C "$ML" archive 80307b8 .claude/skills/ml-review-pack | tar -x -C "$WT/.claude/skills" --strip-components=2
mv "$WT/.claude/skills/ml-review-pack" "$WT/.claude/skills/ds-review-pack"
ls "$WT/.claude/skills/ds-review-pack"
```
Expected: `SKILL.md  assets  references  scripts  tests`

- [ ] **Step 2: ML 전용 파일 삭제와 `.gitignore`**

```bash
SK=/Users/hyunjun_macbook_pro/Documents/Univ/자구알-ds-review-pack/.claude/skills/ds-review-pack
rm -r "$SK/assets/backup-20260924-165016" "$SK/tests/test_regression_0909_0916.py" "$SK/tests/fixtures/manifest-0909-0916.json"
printf '\n# Python\n__pycache__/\n' >> /Users/hyunjun_macbook_pro/Documents/Univ/자구알-ds-review-pack/.gitignore
```

`$SK/tests/test_manifest.py`에서 지운 픽스처를 쓰는 테스트를 뺀다. 아래 네 줄(빈 줄 포함)을 지운다:
```python
    def test_regression_manifest_is_valid(self):
        manifest.load(FIXTURES / "manifest-0909-0916.json")

```
`FIXTURES`는 이 테스트에서만 쓰였으므로 9행 `from _util import FIXTURES, MINI_RUN`을 `from _util import MINI_RUN`으로 바꾼다.

`$SK/tests/_util.py`의 `REPO = SKILL.parents[2]  # <repo>/.claude/skills/ml-review-pack` 주석을 `# <repo>/.claude/skills/ds-review-pack`으로 바꾼다.

`$SK/assets/SOURCE.md`를 만든다:
```markdown
# 복사 출처

- 원본: `머신러닝기초/.claude/skills/ml-review-pack`, 커밋 `80307b8` (2026-09-24 복사)
- 원본의 이후 변경은 자동으로 따라오지 않는다. 가져오려면 이 커밋 이후 원본 diff를 보고 손으로 옮긴다.
- 자구알에서 바꾼 내용은 이 폴더의 git 이력(`git log -- .claude/skills/ds-review-pack`)에 있다.
```

- [ ] **Step 3: 복사본 기준선 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 69 tests` … `OK`

- [ ] **Step 4: 과목명·픽스처 테스트를 자구알 값으로 바꾼다 (실패 테스트)**

`$SK/tests/fixtures/mini-run/manifest.json`에서 세 곳을 바꾼다:
- `"course": "머신러닝기초",` → `"course": "자료구조및알고리즘이해",`
- `"parts": [{"id": "partA", "title": "A. 교과서 예제", "short": "A 교과서 예제"}],` → `"parts": [{"id": "partA", "title": "A. 이정원 교수님 기출", "short": "A 이정원 기출"}],`
- `"source": "MML Example 6.1"` → `"source": "2016-final-ljw-q1"`

`$SK/tests/fixtures/mini-run/cards/p1.html`에서 두 줄을 바꾼다:
- `      <article class="card" id="p1" data-source="MML Example 6.1">` → `      <article class="card" id="p1" data-source="2016-final-ljw-q1">`
- `        <details class="original"><summary>교과서 원문 보기</summary>"Compute the mean." — Example 6.1</details>` → `        <details class="original"><summary>기출 원문 보기</summary><p>2016 기말 1번 · 4점 · 이정원 교수님</p>"1과 2의 평균을 구하시오."</details>`

`$SK/tests/test_check_html.py:106`:
```python
        self.edit("cards/p1.html", 'data-source="2016-final-ljw-q1"', 'data-source="2016-final-ljw-q2"')
```

`$SK/tests/test_assemble.py`에서:
- 30행 `        self.assertIn("<title>머신러닝기초 정리노트 0101-0102</title>", self.note_html)`을 아래 두 줄로 바꾼다.
```python
        self.assertIn("<title>자료구조및알고리즘이해 정리노트 0101-0102</title>", self.note_html)
        self.assertIn("<title>자료구조및알고리즘이해 복습문제 0101-0102</title>", self.review_html)
```
- 42행 → `        self.assertIn('<section id="partA"><h2>A. 이정원 교수님 기출</h2>', self.review_html)`

- [ ] **Step 5: 실패 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: FAIL 1건 — `test_sections_toc_and_titles` (`'<title>자료구조및알고리즘이해 정리노트 0101-0102</title>' not found`). 나머지는 통과.

- [ ] **Step 6: `assemble.py`가 manifest `course`를 쓰게 한다**

`$SK/scripts/assemble.py`:
- 64행 `        "PAGE_TITLE": esc(f"머신러닝기초 정리노트 {m['range']}"),` → `        "PAGE_TITLE": esc(f"{m['course']} 정리노트 {m['range']}"),`
- 86행 `        "PAGE_TITLE": esc(f"머신러닝기초 복습문제 {m['range']}"),` → `        "PAGE_TITLE": esc(f"{m['course']} 복습문제 {m['range']}"),`

- [ ] **Step 7: SKILL.md 프론트매터와 그 테스트**

`$SK/SKILL.md`의 1~4행(프론트매터)을 아래로 바꾼다. 본문은 Task 6에서 새로 쓴다.
```markdown
---
name: ds-review-pack
description: 자료구조및알고리즘이해(자구알) 수업의 STT·강의록으로 ELI5 정리노트 HTML과 기출 기반 복습문제 HTML(+MD, 그림)을 만들어 복습노트/<날짜>/ 폴더에 저장하고, 기출 원본으로 문제은행을 만든다. "자구알 정리노트", "자구알 복습문제", "복습팩", "기출 문제은행 만들어줘"처럼 자구알 수업 정리나 기출 정리를 요청하거나 /ds-review-pack [bank | MMDD | MMDD-MMDD] [lite]로 부를 때 사용한다.
---
```

`$SK/tests/test_skill_files.py`의 `test_frontmatter`를 바꾼다:
```python
    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "ds-review-pack")
        self.assertIn("정리노트", m.group(2))
        self.assertIn("복습문제", m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)
```

- [ ] **Step 8: 통과 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 69 tests` … `OK`

- [ ] **Step 9: Commit**

```bash
git -C "$WT" add .gitignore .claude/skills/ds-review-pack
git -C "$WT" commit -m "feat(skill): fork ml-review-pack as ds-review-pack; course name from manifest

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: `html2md.py`가 `<pre>` 코드 블록을 펜스로 옮긴다

**Files:**
- Modify: `$SK/scripts/html2md.py` (docstring, `BLOCK`, `SKIP_CHECK`, `block()`, 새 함수 `render_code`)
- Test: `$SK/tests/test_html2md.py`

**Interfaces:**
- Consumes: `html2md.convert_pack(note, review) -> ((note_md, review_md), figs)`, `html2md.check_md(html, md) -> list[str]`, 테스트 도우미 `small_pack(directory, note_body, review_body)` (기존)
- Produces: `<pre><code class="language-c">…</code></pre>` → ```` ```c ```` 펜스. `<pre>` 안 글자는 수식 검사에서 뺀다.

- [ ] **Step 1: 실패 테스트 작성**

`$SK/tests/test_html2md.py`의 `TestHtml2Md` 클래스 안, `def test_check_md_detects_deleted_short_math(self):` 바로 앞에 넣는다(필요한 import는 이미 있다).
```python
    def test_pre_becomes_fenced_code(self):
        d = self.tmp / "pre"
        d.mkdir()
        code = ('<pre><code class="language-c">int fib(int n) {\n'
                '    if (n &lt; 2) return n;\n'
                '    return fib(n - 1) + fib(n - 2);\n'
                '}</code></pre>')
        note, review = small_pack(d, f'<section id="s"><h2>A</h2><p>재귀 코드예요.</p>{code}</section>',
                                  '<section id="q"><h2>Q</h2><p>q</p></section>')
        (note_md, _), _ = html2md.convert_pack(note, review)
        md = Path(note_md).read_text(encoding="utf-8")
        self.assertIn("```c\nint fib(int n) {\n    if (n < 2) return n;\n    return fib(n - 1) + fib(n - 2);\n}\n```", md)
        self.assertEqual(html2md.check_md(note, note_md), [])

    def test_pre_with_dollar_is_not_math(self):
        d = self.tmp / "pre-dollar"
        d.mkdir()
        note, review = small_pack(d, '<section id="s"><h2>A</h2><pre><code>printf("$%d$", x);</code></pre></section>',
                                  '<section id="q"><h2>Q</h2><p>q</p></section>')
        (note_md, _), _ = html2md.convert_pack(note, review)
        md = Path(note_md).read_text(encoding="utf-8")
        self.assertIn('```\nprintf("$%d$", x);\n```', md)
        self.assertEqual(html2md.check_md(note, note_md), [])
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s "$SK/tests" -p test_html2md.py`
Expected: FAIL 2건(`test_pre_becomes_fenced_code`, `test_pre_with_dollar_is_not_math`) — 둘 다 `assertIn`에서 펜스를 못 찾음.

- [ ] **Step 3: 구현**

`$SK/scripts/html2md.py`에 다섯 군데를 고친다.

(a) 모듈 docstring — `- 표 안 수식의 \| 는 \Vert, | 는 \vert 로 바꾼다(GFM 표 구분자 충돌 방지).` 줄 바로 아래에 한 줄 추가:
```
- <pre> 코드는 펜스 코드 블록으로 옮기고, 수식 누락 검사에서 뺀다.
```

(b) `BLOCK` 끝줄 `         "nav", "hr", "dl"}` → `         "nav", "hr", "dl", "pre"}`

(c) `SKIP_CHECK = {"script", "style", "svg", "nav"}` → `SKIP_CHECK = {"script", "style", "svg", "nav", "pre"}`

(d) `def _fig_name(svg, ctx, name):` 바로 앞(`render_table` 함수 뒤)에 새 함수:
```python
def render_code(node):
    """<pre><code class="language-c"> → 펜스 코드 블록. 공백·줄바꿈은 그대로 둔다."""
    code = next((c for c in node.children if isinstance(c, Node) and c.tag == "code"), None)
    lang = next((c[len("language-"):] for c in sorted(code.classes) if c.startswith("language-")), "") if code else ""
    body = node.text().strip("\n")
    fence = "````" if "```" in body else "```"
    return [fence + lang, *body.split("\n"), fence]


```

(e) `block()` 안 `    if t == "table":` 바로 앞에:
```python
    if t == "pre":
        return render_code(node)
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 71 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .claude/skills/ds-review-pack/scripts/html2md.py .claude/skills/ds-review-pack/tests/test_html2md.py
git -C "$WT" commit -m "feat(skill): html2md renders <pre> code as fenced blocks

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: 템플릿에 코드 블록 스타일과 "기출 원문" 문구

**Files:**
- Modify: `$SK/assets/note-template.html:94,759`, `$SK/assets/review-template.html:89,379,778`
- Test: `$SK/tests/test_assemble.py`

**Interfaces:**
- Consumes: Task 1의 `assemble.assemble`
- Produces: 두 페이지에 `pre`/`code` CSS. 가로 스와이프가 `pre` 안에서는 화면을 넘기지 않음. 복습문제 패널 안내가 "기출 원문".

- [ ] **Step 1: 실패 테스트 작성**

`$SK/tests/test_assemble.py`의 `TestAssemble` 클래스 안, `def test_missing_fragment_raises(self):` 바로 앞에 넣는다:
```python
    def test_code_blocks_styled_and_swipe_safe(self):
        for html in (self.note_html, self.review_html):
            self.assertIn("    pre { margin: var(--s3) 0;", html)
            self.assertIn("closest('.widget, .katex-display, .table-wrap, pre, svg, input, details')", html)
        self.assertIn("그 문제의 기출 원문, 힌트, 풀이가 여기에 나옵니다.", self.review_html)
        self.assertNotIn("교과서", self.review_html)
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s "$SK/tests" -p test_assemble.py`
Expected: FAIL 1건 `test_code_blocks_styled_and_swipe_safe`

- [ ] **Step 3: 템플릿 수정**

`$SK/assets/note-template.html`:
- 94행 `    blockquote { margin: var(--s3) 0; padding: 0 0 0 var(--s3); border-left: 2px solid var(--line); color: var(--ink-2); }` 바로 아래에 넣는다:
```css
    pre { margin: var(--s3) 0; padding: var(--s3) var(--s4); overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius);
      font: var(--fs-small)/1.6 ui-monospace, 'SF Mono', Menlo, Consolas, monospace; white-space: pre; word-break: normal; overflow-wrap: normal; tab-size: 4; }
    code { font-family: ui-monospace, 'SF Mono', Menlo, Consolas, monospace; font-size: .92em; }
    pre code { font-size: inherit; }
```
- 스와이프 줄(원래 759행) `closest('.widget, .katex-display, .table-wrap, svg, input, details')` → `closest('.widget, .katex-display, .table-wrap, pre, svg, input, details')`

`$SK/assets/review-template.html`:
- 89행 `    blockquote { margin: var(--s2) 0; padding: 0 0 0 var(--s3); border-left: 2px solid var(--line); color: var(--ink-2); }` 바로 아래에 위와 같은 CSS 네 줄
- 패널 안내(원래 379행) `문제로 넘어가면 그 문제의 교과서 원문, 힌트, 풀이가 여기에 나옵니다.` → `문제로 넘어가면 그 문제의 기출 원문, 힌트, 풀이가 여기에 나옵니다.`
- 스와이프 줄(원래 778행) 위와 같은 치환

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 72 tests` … `OK`

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .claude/skills/ds-review-pack/assets .claude/skills/ds-review-pack/tests/test_assemble.py
git -C "$WT" commit -m "feat(skill): code block styles and past-exam wording in templates

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `bank.py` — 문제은행 검사·선별·manifest 대조

**Files:**
- Create: `$SK/scripts/bank.py`
- Test: `$SK/tests/test_bank.py`

**Interfaces:**
- Produces (Task 5·6 문서가 이 이름을 그대로 쓴다):
  - `bank.validate(bank: dict) -> list[str]`
  - `bank.load(path) -> dict` (오류면 `bank.BankError`)
  - `bank.parse_chapters(spec: str) -> set[int]` — `"1-3,5"` → `{1, 2, 3, 5}`
  - `bank.used_sources(notes_dir) -> set[str]` — `복습문제_*.html`의 `data-source` 값
  - `bank.select(bank, range_ch: set[int], taught: set[int], used=frozenset()) -> list[dict]`
  - `bank.check_manifest(bank, manifest) -> list[str]`
  - CLI: `bank.py validate BANK` → `OK: 원본 N개, 문항 M개` / `bank.py select BANK --range-ch 2 --taught 1-2 [--used-dir DIR]` → 머리줄 `id\t출제자\t유형\t챕터\t정답출처` + 후보 줄 / `bank.py check-manifest BANK MANIFEST` → `OK`. 오류는 종료 코드 1.

- [ ] **Step 1: 실패 테스트 작성**

`$SK/tests/test_bank.py`:
```python
"""bank.py: 문제은행 스키마 검사, 후보 선별, manifest 출처 대조."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from _util import SCRIPTS

import bank


def P(pid, chapters, type_, duplicate_of=None):
    source, number = pid.rsplit("-q", 1)
    return {"id": pid, "source": source, "number": number, "chapters": chapters, "type": type_,
            "points": 4, "text": f"{pid} 문제", "figure": None, "answer": "1", "answer_origin": "key",
            "duplicate_of": duplicate_of}


def S(sid, year, professor, transcribed_from, reviewed=True):
    return {"id": sid, "file": f"{sid}.pdf", "year": year, "exam": "기말", "professor": professor,
            "has_key": True, "transcribed_from": transcribed_from, "reviewed": reviewed}


def mini_bank():
    return {"version": 1,
            "sources": [S("2016-final-ljw", 2016, "이정원", "photo"),
                        S("2019-mid", 2019, "미상", "txt"),
                        S("2017-final-kdh", 2017, "김도희", "text"),
                        S("2015-ljw", 2015, "이정원", "scan", reviewed=False),
                        S("2021-mock1", 2021, "미상", "text"),
                        S("unk-final-ltk", None, "이태권", "text")],
            "problems": [P("2016-final-ljw-q1", [2], "trace"),
                         P("2016-final-ljw-q2", [2, 5], "trace"),  # 5장을 아직 안 배움
                         P("2019-mid-q8", [2], "code-read"),
                         P("2019-mid-q1", [2], "ox"),
                         P("2019-mid-q2", [2], "ox"),
                         P("2019-mid-q3", [2], "ox"),  # OX 셋째라 잘림
                         P("2017-final-kdh-q4", [1, 2], "short"),
                         P("2019-mid-q9", [1], "short"),  # 이번 범위(2장)와 안 겹침
                         P("2015-ljw-q1", [2], "trace"),  # 검수 전 원본
                         P("2021-mock1-q1", [2], "trace", duplicate_of="2016-final-ljw-q1"),
                         P("unk-final-ltk-q2", [2], "trace")]}


EXPECTED = ["2016-final-ljw-q1", "2019-mid-q8", "2019-mid-q1", "2019-mid-q2", "unk-final-ltk-q2",
            "2017-final-kdh-q4"]


class TestValidate(unittest.TestCase):
    def test_mini_bank_is_valid(self):
        self.assertEqual(bank.validate(mini_bank()), [])

    def test_bad_chapter(self):
        b = mini_bank()
        b["problems"][0]["chapters"] = [13]
        self.assertTrue(any(e.startswith("problems[0].chapters") for e in bank.validate(b)))

    def test_bool_is_not_a_chapter(self):
        b = mini_bank()
        b["problems"][0]["chapters"] = [True]
        self.assertTrue(any(e.startswith("problems[0].chapters") for e in bank.validate(b)))

    def test_id_must_match_source_and_number(self):
        b = mini_bank()
        b["problems"][0]["id"] = "2016-final-ljw-q9"
        self.assertTrue(any(e.startswith("problems[0].id") for e in bank.validate(b)))

    def test_duplicate_problem_id(self):
        b = mini_bank()
        b["problems"].append(dict(b["problems"][0]))
        self.assertIn("problems[11].id: 중복: 2016-final-ljw-q1", bank.validate(b))

    def test_unknown_type_and_origin(self):
        b = mini_bank()
        b["problems"][0]["type"] = "tree"
        b["sources"][0]["transcribed_from"] = "fax"
        errors = bank.validate(b)
        self.assertTrue(any(e.startswith("problems[0].type") for e in errors))
        self.assertTrue(any(e.startswith("sources[0].transcribed_from") for e in errors))

    def test_missing_field(self):
        b = mini_bank()
        del b["sources"][0]["reviewed"]
        self.assertIn("sources[0].reviewed: 없음", bank.validate(b))

    def test_duplicate_of_must_point_to_an_original(self):
        b = mini_bank()
        b["problems"][0]["duplicate_of"] = "2021-mock1-q1"  # 2021-mock1-q1도 중복 문항
        self.assertTrue(any(e.startswith("problems[0].duplicate_of") for e in bank.validate(b)))

    def test_unknown_duplicate_target(self):
        b = mini_bank()
        b["problems"][1]["duplicate_of"] = "nope-q1"
        self.assertIn("problems[1].duplicate_of: 없는 문항: nope-q1", bank.validate(b))

    def test_load_reports_json_error(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "bank.json"
            p.write_text("{", encoding="utf-8")
            with self.assertRaises(bank.BankError) as cm:
                bank.load(p)
            self.assertIn("JSON 형식 오류", str(cm.exception))


class TestSelect(unittest.TestCase):
    def ids(self, b=None, used=frozenset()):
        return [q["id"] for q in bank.select(b or mini_bank(), {2}, {1, 2}, used)]

    def test_order_and_filters(self):
        self.assertEqual(self.ids(), EXPECTED)

    def test_used_are_skipped(self):
        self.assertEqual(self.ids(used={"2016-final-ljw-q1"}), EXPECTED[1:])

    def test_reviewed_source_becomes_eligible(self):
        b = mini_bank()
        b["sources"][3]["reviewed"] = True
        self.assertEqual(self.ids(b)[:2], ["2016-final-ljw-q1", "2015-ljw-q1"])

    def test_parse_chapters(self):
        self.assertEqual(bank.parse_chapters("1-3,5"), {1, 2, 3, 5})
        for bad in ("0", "3-1", "a", "", "13"):
            with self.subTest(bad=bad), self.assertRaises(bank.BankError):
                bank.parse_chapters(bad)

    def test_used_sources_reads_review_pages_only(self):
        with tempfile.TemporaryDirectory() as d:
            notes = Path(d) / "복습노트"
            (notes / "0921").mkdir(parents=True)
            (notes / "0923").mkdir()
            (notes / "0921" / "복습문제_0921_Recursion.html").write_text(
                '<article class="card" data-source="2016-final-ljw-q1">', encoding="utf-8")
            (notes / "0923" / unicodedata.normalize("NFD", "복습문제_0923_Stack.html")).write_text(
                '<article class="card" data-source="2019-mid-q8">', encoding="utf-8")
            (notes / "0921" / "정리노트_0921_Recursion.html").write_text(
                '<div data-source="2019-mid-q1">', encoding="utf-8")
            self.assertEqual(bank.used_sources(notes), {"2016-final-ljw-q1", "2019-mid-q8"})
            self.assertEqual(bank.used_sources(Path(d) / "없음"), set())


class TestCheckManifest(unittest.TestCase):
    def errors(self, *items):
        m = {"problems": [{"id": f"p{i + 1}", "source": s, "variant": v} for i, (s, v) in enumerate(items)]}
        return bank.check_manifest(mini_bank(), m)

    def test_ok_with_variant_of_same_problem(self):
        self.assertEqual(self.errors(("2016-final-ljw-q1", False), ("2016-final-ljw-q1", True),
                                     ("2019-mid-q8", False)), [])

    def test_unknown_source(self):
        self.assertEqual(self.errors(("nope-q1", False)), ["problems[0].source: 은행에 없는 문항: 'nope-q1'"])

    def test_duplicate_problem_must_use_original(self):
        self.assertIn("원 문항 2016-final-ljw-q1", self.errors(("2021-mock1-q1", False))[0])

    def test_unreviewed_source(self):
        self.assertIn("검수 전 원본", self.errors(("2015-ljw-q1", False))[0])

    def test_same_problem_twice(self):
        self.assertIn("같은 문항이 두 번", self.errors(("2019-mid-q8", False), ("2019-mid-q8", False))[0])


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.bank = self.tmp / "bank.json"
        self.bank.write_text(json.dumps(mini_bank(), ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "bank.py"), *map(str, args)],
                              capture_output=True, text=True)

    def test_validate(self):
        r = self.run_cli("validate", self.bank)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "OK: 원본 6개, 문항 11개")

    def test_validate_broken_bank(self):
        self.bank.write_text(json.dumps({"version": 2, "sources": [], "problems": []}), encoding="utf-8")
        r = self.run_cli("validate", self.bank)
        self.assertEqual(r.returncode, 1)
        self.assertIn("version", r.stderr)

    def test_select(self):
        r = self.run_cli("select", self.bank, "--range-ch", "2", "--taught", "1-2")
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(lines[0], "id\t출제자\t유형\t챕터\t정답출처")
        self.assertEqual(lines[1], "2016-final-ljw-q1\t이정원\ttrace\t2\tkey")
        self.assertEqual(len(lines), 1 + len(EXPECTED))

    def test_check_manifest(self):
        m = self.tmp / "manifest.json"
        m.write_text(json.dumps({"problems": [{"id": "p1", "source": "nope-q1", "variant": False}]}), encoding="utf-8")
        r = self.run_cli("check-manifest", self.bank, m)
        self.assertEqual(r.returncode, 1)
        self.assertIn("은행에 없는 문항", r.stdout)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s "$SK/tests" -p test_bank.py`
Expected: `ModuleNotFoundError: No module named 'bank'`

- [ ] **Step 3: 구현**

`$SK/scripts/bank.py`:
```python
#!/usr/bin/env python3
"""자구알 기출 문제은행(문제은행.json) 검사·선별 도구 (표준 라이브러리만 사용).

CLI:
  bank.py validate BANK                                              # 스키마 검사 → OK
  bank.py select BANK --range-ch 2,3 --taught 1-3 [--used-dir DIR]   # 후보를 우선순위 순으로 출력
  bank.py check-manifest BANK MANIFEST                               # manifest 문항 출처가 쓸 수 있는 은행 문항인지
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NUMBER_RE = re.compile(r"\d+")
EXAMS = {"중간", "기말", "모의", "미상"}
TRANSCRIBED_FROM = {"text", "scan", "photo", "hwp", "txt"}
TYPES = {"ox", "blank", "trace", "code-read", "code-write", "short", "essay"}
ANSWER_ORIGINS = {"key", "verified", "unverified"}
PROFESSOR_RANK = {"이정원": 0, "미상": 1}  # 그 밖의 교수는 2
TYPE_RANK = {"trace": 0, "code-read": 0, "blank": 1, "short": 1, "code-write": 1, "essay": 2, "ox": 3}
MAX_OX = 2
SOURCE_ATTR_RE = re.compile(r'data-source="([^"]+)"')
REVIEW_NAME_RE = re.compile(r"복습문제_\d{4}(?:-\d{4})?_[A-Za-z0-9_]+\.html")


class BankError(Exception):
    pass


def _is(value, typ) -> bool:
    if typ is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, typ)


def _need(obj: dict, key: str, typ: type, where: str, errors: list[str], nullable: bool = False) -> bool:
    if key not in obj:
        errors.append(f"{where}.{key}: 없음")
        return False
    if nullable and obj[key] is None:
        return True
    if not _is(obj[key], typ):
        errors.append(f"{where}.{key}: {typ.__name__}{' 또는 null' if nullable else ''}이어야 함")
        return False
    return True


def _check_source(s: dict, where: str, ids: set[str], errors: list[str]) -> None:
    fields = (("id", str, False), ("file", str, False), ("year", int, True), ("exam", str, False),
              ("professor", str, False), ("has_key", bool, False), ("transcribed_from", str, False),
              ("reviewed", bool, False))
    if not all([_need(s, key, typ, where, errors, nullable) for key, typ, nullable in fields]):
        return
    if not ID_RE.fullmatch(s["id"]):
        errors.append(f"{where}.id: 소문자·숫자·하이픈만: {s['id']!r}")
    elif s["id"] in ids:
        errors.append(f"{where}.id: 중복: {s['id']}")
    ids.add(s["id"])
    if s["exam"] not in EXAMS:
        errors.append(f"{where}.exam: {sorted(EXAMS)} 중 하나여야 함: {s['exam']!r}")
    if s["transcribed_from"] not in TRANSCRIBED_FROM:
        errors.append(f"{where}.transcribed_from: {sorted(TRANSCRIBED_FROM)} 중 하나여야 함: {s['transcribed_from']!r}")
    if not s["professor"].strip():
        errors.append(f"{where}.professor: 비어 있음")


def _check_problem(q: dict, where: str, source_ids: set[str], ids: set[str], errors: list[str]) -> None:
    fields = (("id", str, False), ("source", str, False), ("number", str, False), ("chapters", list, False),
              ("type", str, False), ("points", int, True), ("text", str, False), ("figure", str, True),
              ("answer", str, False), ("answer_origin", str, False), ("duplicate_of", str, True))
    if not all([_need(q, key, typ, where, errors, nullable) for key, typ, nullable in fields]):
        return
    if q["source"] not in source_ids:
        errors.append(f"{where}.source: 없는 원본: {q['source']}")
    if not NUMBER_RE.fullmatch(q["number"]):
        errors.append(f"{where}.number: 숫자 문자열이어야 함: {q['number']!r}")
    elif q["id"] != f"{q['source']}-q{q['number']}":
        errors.append(f"{where}.id: '<source>-q<number>' 꼴이어야 함: {q['id']!r}")
    if q["id"] in ids:
        errors.append(f"{where}.id: 중복: {q['id']}")
    ids.add(q["id"])
    ch = q["chapters"]
    if not (ch and all(_is(c, int) and 1 <= c <= 12 for c in ch) and len(set(ch)) == len(ch)):
        errors.append(f"{where}.chapters: 1~12 정수, 중복 없이 하나 이상이어야 함: {ch!r}")
    if q["type"] not in TYPES:
        errors.append(f"{where}.type: {sorted(TYPES)} 중 하나여야 함: {q['type']!r}")
    if q["answer_origin"] not in ANSWER_ORIGINS:
        errors.append(f"{where}.answer_origin: {sorted(ANSWER_ORIGINS)} 중 하나여야 함: {q['answer_origin']!r}")
    for key in ("text", "answer"):
        if not q[key].strip():
            errors.append(f"{where}.{key}: 비어 있음")


def _check_duplicates(problems: list, errors: list[str]) -> None:
    by_id = {q["id"]: q for q in problems if isinstance(q, dict) and isinstance(q.get("id"), str)}
    for i, q in enumerate(problems):
        dup = q.get("duplicate_of") if isinstance(q, dict) else None
        if not isinstance(dup, str):
            continue
        where = f"problems[{i}].duplicate_of"
        target = by_id.get(dup)
        if target is None:
            errors.append(f"{where}: 없는 문항: {dup}")
        elif dup == q.get("id"):
            errors.append(f"{where}: 자기 자신을 가리킴")
        elif target.get("duplicate_of") is not None:
            errors.append(f"{where}: 원 문항 {dup}도 중복 문항임")


def validate(bank: dict) -> list[str]:
    if not isinstance(bank, dict):
        return ["최상위: 객체여야 함"]
    errors: list[str] = []
    if bank.get("version") != 1:
        errors.append("version: 1이어야 함")
    sources, problems = bank.get("sources"), bank.get("problems")
    if not isinstance(sources, list) or not isinstance(problems, list):
        return errors + ["sources, problems: 목록이어야 함"]
    source_ids: set[str] = set()
    problem_ids: set[str] = set()
    for i, s in enumerate(sources):
        if isinstance(s, dict):
            _check_source(s, f"sources[{i}]", source_ids, errors)
        else:
            errors.append(f"sources[{i}]: 객체여야 함")
    for i, q in enumerate(problems):
        if isinstance(q, dict):
            _check_problem(q, f"problems[{i}]", source_ids, problem_ids, errors)
        else:
            errors.append(f"problems[{i}]: 객체여야 함")
    _check_duplicates(problems, errors)
    return errors


def load(path: Path | str) -> dict:
    try:
        bank = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BankError(f"{path}: JSON 형식 오류: {e}") from e
    except (OSError, UnicodeDecodeError) as e:
        raise BankError(f"{path}: 파일을 읽을 수 없음: {e}") from e
    errors = validate(bank)
    if errors:
        raise BankError("\n".join(errors))
    return bank


def parse_chapters(spec: str) -> set[int]:
    """'1-3,5' → {1, 2, 3, 5}. 챕터는 강의록 Software_<N> 번호(1~12)."""
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not m:
            raise BankError(f"챕터 표기 오류: {part!r}")
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if not 1 <= a <= b <= 12:
            raise BankError(f"챕터는 1~12, 앞이 작아야 함: {part!r}")
        out.update(range(a, b + 1))
    return out


def used_sources(notes_dir: Path | str) -> set[str]:
    """이전 복습팩 복습문제 페이지(NFC·NFD 이름 모두)의 data-source 값."""
    used: set[str] = set()
    for dirpath, _, files in os.walk(notes_dir):
        for name in files:
            if REVIEW_NAME_RE.fullmatch(unicodedata.normalize("NFC", name)):
                used.update(SOURCE_ATTR_RE.findall(Path(dirpath, name).read_text(encoding="utf-8")))
    return used


def select(bank: dict, range_ch: set[int], taught: set[int], used=frozenset()) -> list[dict]:
    """쓸 수 있는 문항을 우선순위 순으로. OX는 MAX_OX개까지."""
    sources = {s["id"]: s for s in bank["sources"]}

    def eligible(q: dict) -> bool:
        ch = set(q["chapters"])
        return (sources[q["source"]]["reviewed"] and q["duplicate_of"] is None
                and ch <= taught and bool(ch & range_ch) and q["id"] not in used)

    def rank(q: dict) -> tuple:
        s = sources[q["source"]]
        return (PROFESSOR_RANK.get(s["professor"], 2), TYPE_RANK[q["type"]], -(s["year"] or 0), q["id"])

    out, ox = [], 0
    for q in sorted(filter(eligible, bank["problems"]), key=rank):
        if q["type"] == "ox":
            if ox >= MAX_OX:
                continue
            ox += 1
        out.append(q)
    return out


def check_manifest(bank: dict, manifest: dict) -> list[str]:
    """manifest problems의 source가 쓸 수 있는 은행 문항인지. 변형(variant)은 같은 문항을 다시 써도 된다."""
    items = manifest.get("problems") if isinstance(manifest, dict) else None
    if not isinstance(items, list):
        return ["manifest.problems: 목록이어야 함"]
    problems = {q["id"]: q for q in bank["problems"]}
    sources = {s["id"]: s for s in bank["sources"]}
    errors: list[str] = []
    originals: set[str] = set()
    for i, p in enumerate(items):
        where = f"problems[{i}].source"
        src = p.get("source") if isinstance(p, dict) else None
        q = problems.get(src)
        if q is None:
            errors.append(f"{where}: 은행에 없는 문항: {src!r}")
            continue
        if q["duplicate_of"] is not None:
            errors.append(f"{where}: 중복 문항이므로 원 문항 {q['duplicate_of']}을 써야 함")
        if not sources[q["source"]]["reviewed"]:
            errors.append(f"{where}: 검수 전 원본의 문항: {src}")
        if not p.get("variant"):
            if src in originals:
                errors.append(f"{where}: 같은 문항이 두 번: {src}")
            originals.add(src)
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="자구알 기출 문제은행 검사·선별")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate").add_argument("bank")
    sp = sub.add_parser("select")
    sp.add_argument("bank")
    sp.add_argument("--range-ch", required=True, help="이번 범위 챕터, 예: 2,3")
    sp.add_argument("--taught", required=True, help="지금까지 배운 챕터, 예: 1-3")
    sp.add_argument("--used-dir", help="이전 팩 폴더(복습노트). 주면 이미 쓴 문항을 뺀다")
    cp = sub.add_parser("check-manifest")
    cp.add_argument("bank")
    cp.add_argument("manifest")
    a = ap.parse_args(argv)
    try:
        bank = load(a.bank)
        if a.cmd == "validate":
            print(f"OK: 원본 {len(bank['sources'])}개, 문항 {len(bank['problems'])}개")
            return 0
        if a.cmd == "select":
            used = used_sources(a.used_dir) if a.used_dir else set()
            rows = select(bank, parse_chapters(a.range_ch), parse_chapters(a.taught), used)
            sources = {s["id"]: s for s in bank["sources"]}
            print("id\t출제자\t유형\t챕터\t정답출처")
            for q in rows:
                print("\t".join([q["id"], sources[q["source"]]["professor"], q["type"],
                                 ",".join(map(str, q["chapters"])), q["answer_origin"]]))
            print(f"후보 {len(rows)}개", file=sys.stderr)
            return 0
        manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        errors = check_manifest(bank, manifest)
    except (BankError, OSError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: 통과 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 96 tests` … `OK` (test_bank 24개 추가)

- [ ] **Step 5: Commit**

```bash
git -C "$WT" add .claude/skills/ds-review-pack/scripts/bank.py .claude/skills/ds-review-pack/tests/test_bank.py
git -C "$WT" commit -m "feat(skill): bank.py validates, selects and cross-checks past-exam bank

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: 작성자·리뷰어 문서를 자구알용으로

**Files:**
- Rewrite: `$SK/references/content-rules.md`, `card-rules.md`, `manifest-guide.md`, `problem-selection.md`, `stt-summary-prompt.md`, `review-prompt.md`
- Modify: `$SK/references/widget-rules.md:4`, `$SK/references/browser-check.md:20`
- Test: `$SK/tests/test_skill_files.py`

**Interfaces:**
- Consumes: Task 4 CLI(`bank.py select … --used-dir`, `bank.py check-manifest`), Task 2의 `<pre><code class="language-c">` 마크업, Task 1의 은행 id 형식(`<source>-q<number>`)
- Produces: SKILL.md(Task 6)가 가리키는 브리프들. 브리프 자리표시자: `<SKILL>`, `<RUN>`, `<sid>`, `<섹션 title>`, `<위젯>`, `<이 섹션의 links 목록>`, `<forbidden 목록>`, `<preview_topic>`, `<pid>`, `<MMDD>`, `<MMDD 자구알.md>`, `<Software_N_*.pdf>`, `<YYYY-MM-DD>`, `<range>`

- [ ] **Step 1: 실패 테스트 작성 — ML 흔적 그물**

`$SK/tests/test_skill_files.py`에서 `SKILL_MD = SKILL / "SKILL.md"` 줄 바로 아래에 넣는다:
```python
ML_WORDS = ("MML", "머신러닝", "정방철", "교과서", "머러기", "Lecture", "강의노트/")
```
`TestSkillFiles` 클래스의 `test_steps_present` 메서드 바로 아래에 넣는다:
```python
    def test_no_ml_leftovers_in_references(self):
        for path in sorted((SKILL / "references").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for word in ML_WORDS:
                with self.subTest(file=path.name, word=word):
                    self.assertNotIn(word, text)
```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s "$SK/tests" -p test_skill_files.py`
Expected: FAIL — `content-rules.md`, `card-rules.md`, `manifest-guide.md`, `problem-selection.md`, `stt-summary-prompt.md`, `review-prompt.md`의 하위 테스트가 실패.

- [ ] **Step 3: `references/content-rules.md` 전체를 아래로 바꾼다**

````markdown
# 섹션 작성 규칙

## 작성자 브리프 (메인 에이전트가 섹션마다 1명, 병렬, model: opus / lite: sonnet)

---
자료구조및알고리즘이해 정리노트의 섹션 `<sid>`(`<섹션 title>`)를 쓴다.

- 읽기: `<SKILL>/references/content-rules.md`(이 파일 전체), 위젯이 있으면 `<SKILL>/references/widget-rules.md`
- 위젯: <위젯> (메인 에이전트가 정한 것만 만든다. "위젯 없음"이면 이 섹션에는 위젯을 넣지 않는다)
- 계약: `<RUN>/manifest.json`의 섹션 `<sid>` — 토픽 id·제목·`required_terms`·`layers`·`supp`가 정확히 여기 적힌 대로여야 한다.
- 링크: manifest `links` 중 `topic`이 이 섹션에 있는 항목 `<이 섹션의 links 목록>`을 모두 그 토픽 안에 `<a href="…">`로 넣는다. `href`는 글자 그대로 복사(`%20` 포함). 복습문제 링크만은 `{{REVIEW_HREF}}`로 써도 된다(조립 뒤 실제 파일명이 되어 검사를 통과한다).
- 근거: `<RUN>/summaries/stt-*.md`(해당 날짜), `<RUN>/slides.txt`(강의록 텍스트, 쪽 표시 `=== S<N> p<k> ===`). 슬라이드 그림·코드가 텍스트로 깨졌으면 `<RUN>/repo/자료구조_강의록_2026/`의 해당 PDF 쪽을 직접 본다.
- 출력: `<RUN>/sections/<sid>.html` **한 파일만**. `<section>`/`<h2>`는 쓰지 않는다(조립기가 감싼다). 임시 파일은 아래 규칙.
- 임시·보조 파일(스크립트, 초안, 그림 생성 폴더)은 `<RUN>/work/` 아래에만 둔다. 저장소(`STT/`, `자료구조_강의록_2026/`, `from_the_past/`, `복습노트/`)와 scratchpad 루트, `/tmp`에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 복사하거나 이름을 바꾸지 말고 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 그 경로로 연다.
- 자기 검사(끝내기 전): 토픽별로 `required_terms`가 모두 문자 그대로 들어갔는지(코드 조각은 `&lt;`가 `<`로 풀린 글자 기준), `$` 짝, `links` 항목이 해당 토픽 안에 있는지, 금지어 `<forbidden 목록>`이 없는지. 금지어는 예고 토픽 `<preview_topic>` 안에서만 허용된다 — 이 토픽에는 예고 제목을 빠뜨리지 말고 쓴다. eli5 레이어마다 문장 수(figcaption 포함)가 3 이하이고 전문용어·기호(식, 코드, 영어 용어)가 없는지 — 있으면 formal 레이어로 옮긴다. 조각 어디에도 이모지를 쓰지 않았는지. 코드 블록 안에 `$`가 없는지. `layers`가 빈 목록이 아닌 토픽마다 마지막에 `<div class="sum" hidden>`이 있고, 그 식·용어가 본문과 같은 표기인지. 그림 설명(글, `aria-label`)이 SVG 클래스의 실제 모양(채움/윤곽)과 맞는지.
- 보고: 파일 경로, 토픽별 한 줄, 요약에 있었지만 넣지 않은 것과 이유.
---

## 범위
- 요약의 슬라이드 대조표에서 "다룸/일부"인 내용만 쓴다. "예고만/안 다룸"은 `s<N>-next`에 제목만.
- 수업에서 말한 모든 개념, 코드 설명, 동작 추적(칠판에 그린 스택·큐·트리 상태 변화 포함), 교수님 비유와 강조 발언을 빠짐없이 싣는다(잡담 제외).
- STT 오인식과 말실수는 올바른 형태로 쓴다. 코드나 추적 결과가 틀렸던 경우만 각주 한 줄로 "(수업 중 X로 적었다가 정정)".

## 토픽 마크업 (이 순서)
```html
<article class="topic" id="…"><h3>…</h3><div class="tags"><span class="tag date">MMDD 수업</span><span class="tag slide">S2 p7</span></div>
  <div class="layer eli5"><span class="layer-title">쉽게 말하면</span><p class="lead">한 문장 비유</p> …그림… </div>
  <div class="layer formal"><span class="layer-title">정확히 말하면</span> …정의·C 코드(pre)·동작 추적(ol.steps)·시간복잡도… </div>
  <div class="layer prof"><span class="layer-title">교수님 말씀</span> …비유·일화, 원문은 blockquote… </div>
  <div class="layer warn"><span class="layer-title">꼭 기억해요</span> …원문 인용 + (MMDD MM:SS)… </div>   ← 강조 발언이 있을 때만
  <div class="layer supp"><span class="badge supp">보충 · 수업에서 유도하진 않았어요</span> … </div>             ← manifest supp=true만
  <div class="sum" hidden>…페이지 요약(아래)…</div>                                                    ← layers가 빈 목록이 아닌 토픽만, 맨 끝
</article>
```
- 슬라이드 태그는 `S<강의록 번호> p<쪽>`(예: `S2 p7`, 여러 쪽이면 `S2 p7–9`). 다음 팩이 이 태그로 이전 범위를 찾는다.
- 레이어 제목과 배지 글자는 위와 글자 그대로 쓴다. 이모지, 장식 기호(★, ↗, → 같은 화살표 아이콘), "아래를 보세요" 같은 안내 문장은 쓰지 않는다.
- 템플릿이 토픽 하나를 한 화면에 보여 준다. 토픽은 그것만 읽어도 이해되게 쓰고, "위에서 본 것처럼"처럼 앞 토픽의 위치에 기대는 말 대신 `<a href="#토픽id">토픽 제목</a>`으로 잇는다.
- 요약·예고 섹션: 치트시트는 표(`<div class="table-wrap"><table>`), 예고는 `<ul>`, 링크는 `<ul><li><a>`.
- 복습문제 링크는 `href="{{REVIEW_HREF}}"`로 쓴다(조립기가 실제 파일명으로 바꾼다. manifest의 파일명을 그대로 써도 된다). 다른 링크는 manifest `href`를 글자 그대로.

## 페이지 요약 (`.sum`)
화면 오른쪽 "페이지 요약" 패널에 그 토픽의 핵심만 보여 준다. 템플릿이 토픽의 **직계 자식** `.sum`을 패널로 옮기므로 토픽 안 맨 끝에, 레이어 밖에 둔다. `hidden`은 꼭 붙인다(본문에 두 번 보이지 않게).
```html
<div class="sum" hidden>
  <p class="sum-lead">토픽 핵심 한 문장("~해요" 체)</p>
  <p class="panel-label">핵심 식</p>
  <ul class="eq-list"><li><span class="eq-name">식 이름</span>$$…$$</li></ul>
  <p class="panel-label">용어</p>
  <dl class="terms"><dt>용어(영어)</dt><dd>한 줄 뜻</dd></dl>
</div>
```
- 새 내용을 쓰지 않는다. 본문(formal 레이어)에 이미 나온 식·용어를 **같은 표기로** 1~3개씩 고른다. 요약에만 있는 식이나 설명은 두지 않는다.
- 핵심 식에는 점화식·시간복잡도처럼 식으로 쓸 수 있는 것만 둔다. 코드 블록은 요약에 넣지 않는다.
- 식이 없는 토픽은 "핵심 식" 줄과 `eq-list`를 빼고, 용어가 없으면 "용어" 줄과 `dl`을 뺀다. `sum-lead`는 항상 쓴다.
- 요약·예고 섹션처럼 `layers`가 `[]`인 토픽에는 두지 않는다.

## 문체
- 쉽게 말하면(eli5): 초등학생이 이해할 1~3문장(figcaption 포함) + 그림. 전문용어·기호·코드 없이(필요하면 정확히 말하면에 쓴다). 토스처럼 짧고 다정한 "~해요" 체.
- 정확히 말하면(formal): 빠짐없이, 정확하게. 추적은 한 줄에 한 단계. 문장은 "~해요" 체, 추적 단계는 상태 위주로 짧게(예: `push(3) → [1, 3]`).
- 교수님 말씀(prof)/꼭 기억해요(warn): 원문 인용은 15단어 안팎으로 줄이고 `(0914 26:00)`처럼 출처.
- UI 글은 한국어, 전문용어는 영어 병기(예: 재귀(recursion)). 한 문장에 한 가지만 말하고, 군더더기 수식어("아주", "정말", "한번")는 뺀다.

## 수식
- `$…$`(인라인), `$$…$$`(디스플레이)만. 본문에 리터럴 `$` 금지.
- TeX 안에 `<`, `>`, `&` 금지 → `\lt`, `\gt`. 정렬 환경 대신 `$$` 줄을 나눈다.
- 시간복잡도는 `$O(n^2)$`, 점화식은 `$T(n) = T(n-1) + 1$`처럼 쓴다. manifest `required_terms`와 같은 표기.

## C 코드
- `<pre><code class="language-c">…</code></pre>`만 쓴다. 한 줄 조각은 `<code>`.
- 수업 코드는 슬라이드 그대로 옮기고(변수명·들여쓰기 포함), 설명용으로 줄일 때는 `/* … */`로 생략을 표시한다. 30줄을 넘기지 않는다.
- 들여쓰기는 공백 4칸. HTML이므로 `<`, `>`, `&`는 `&lt;`, `&gt;`, `&amp;`로 쓴다.
- 코드 안에 `$`를 쓰지 않는다(KaTeX와 검사기가 수식으로 오인한다).
- 코드 조각이 `required_terms`에 있으면 글자 그대로(공백 포함) 코드 블록이나 `<code>` 안에 둔다.

## SVG 그림
- 개념 토픽마다 eli5 레이어에 그림 1개 이상(노드와 화살표로 된 리스트, 칸으로 된 배열·스택·큐, 트리, 재귀 호출 상자 쌓기 등).
- `<figure class="figure"><svg id="fig-<kebab>" viewBox="…" role="img" aria-label="한국어 설명">…</svg><figcaption>…</figcaption></figure>`
- 색은 클래스로만: `fig-ink`, `fig-accent`, `fig-danger`, `fig-dot`, `fig-text`, `fig-muted`. 하드코딩 색 금지(다크모드).
- 채움과 윤곽: `fig-ink`, `fig-accent`, `fig-danger`는 선만 그린다(`fill:none`). 속이 칠해진 점·도형은 `fig-dot`(강조색 채움)뿐이다(`fig-text`, `fig-muted`는 글자용). 글·figcaption·`aria-label`에서 "색칠된", "채워진"은 `fig-dot` 도형에만 쓰고, 선만 있는 도형은 "테두리", "선"으로 부른다.
- 화살표 머리는 `<path>`로 직접 그린다(`marker`는 MD 변환에서 색이 사라질 수 있다).
- 글자 12~14px, SVG `<text>`에 `$` 금지(₁, → 같은 유니코드).
- id는 페이지 전체에서 유일해야 한다(`fig-` + 토픽 고유 단어).
````

- [ ] **Step 4: `references/card-rules.md` 전체를 아래로 바꾼다**

````markdown
# 문제 카드 규칙

## 작성자 브리프 (메인 에이전트가 1명, model: opus / lite: sonnet)

---
자료구조및알고리즘이해 기출 복습문제 카드를 쓴다.

- 읽기: `<SKILL>/references/card-rules.md`(이 파일 전체), `<SKILL>/references/problem-selection.md`의 원칙, `<SKILL>/references/content-rules.md`의 "수식", "C 코드", "SVG 그림"
- 계약: `<RUN>/manifest.json`의 `problems` — id, `source`, `variant`, `anchor`, `level`, `date`, `terms`, `answer`를 그대로 따른다.
- 금지어: `<forbidden 목록>` — 카드 어디에도(문제, 원문, 힌트, 풀이, "수업과 연결" 줄 포함) 쓰지 않는다. 검사기가 복습문제 페이지 전체를 훑는다. "다음 시간에 배울 …" 같은 예고도 쓰지 않는다.
- 근거: 문항 원문 `<RUN>/problems.md`(문항 id마다 은행의 문제 글·그림 설명·정답과 전사 기록), 정답 계산 `<RUN>/answers.py`, 정리노트 토픽 제목은 manifest. 원본 사진·PDF를 봐야 하면 `<RUN>/repo/from_the_past/기출/`의 해당 파일을 Read로 연다.
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
- 카드에 "수업에서 다시 보기", "수업과 연결" 같은 연결 안내 줄을 두지 않는다. manifest `anchor`는 풀이가 기대는 토픽을 고르는 데만 쓴다.
- 이모지와 장식 기호(★, ↗ 등)는 쓰지 않는다. 문제·힌트·풀이 문장은 토스처럼 짧고 다정한 "~해요" 체로 쓴다(예: "front와 rear를 구해 보세요.", "넣을 때마다 rear를 한 칸 옮겨요.").
- 템플릿이 카드 하나를 한 화면에 보여 준다. 카드는 다른 카드 없이도 풀 수 있게 쓴다.
- 추적 문제의 풀이는 단계마다 자료구조 상태를 한 줄로 쓴다(예: `push(5) → [5]`, `front=2, rear=5`). 단계가 8개를 넘으면 상태 표(`<div class="table-wrap"><table>`)로 쓴다.
- 풀이 마지막 단계에 "수업과의 연결"을 한 줄로(어느 수업의 어떤 말·코드와 이어지는지).
````

- [ ] **Step 5: `references/manifest-guide.md` 전체를 아래로 바꾼다**

````markdown
# manifest.json 작성 규칙 (메인 에이전트)

manifest는 이번 팩의 계약이다. 작성자, 검사기, 조립기가 모두 이 파일을 기준으로 삼는다.
정본 예시: `tests/fixtures/mini-run/manifest.json`.
작성 후 반드시 두 검사가 모두 `OK`여야 한다:
`python3 <SKILL>/scripts/manifest.py <RUN>/manifest.json`, `python3 <SKILL>/scripts/bank.py check-manifest <BANK> <RUN>/manifest.json`

## 최상위
| 키 | 값 |
|---|---|
| `course` | `"자료구조및알고리즘이해"` |
| `range` | `"0921"` 또는 `"0917-0921"` (첫 STT–마지막 STT 날짜) |
| `slug` | 이번 범위 대표 강의록 파일명의 영문 부분. `Software_2_Recursion.pdf` → `"Recursion"`, `Software_3_ArrayStructureList.pdf` → `"ArrayStructureList"`. 두 강의록에 걸치면 뒤쪽 것. 1장(`Software_1_자료구조및알고리즘.pdf`)은 `"Intro_DS_Algorithms"` |
| `note_title` | `"<주제> — 5살도 이해하는 정리노트"` |
| `note_subtitle` | `"이정원 교수님 자료구조및알고리즘이해 · 0917 · 0921 수업 (Software_2 Recursion)"` 형식 |
| `review_title` | `"기출 복습문제 N선 — <range 물결표기> 수업 범위"` |
| `review_intro` | 인라인 HTML만(`<b>`, `<i>`, `<code>`, `<a>`). 템플릿이 `<p>`로 감싸므로 `<p>`·`<ul>`·`<div>` 같은 블록 태그는 쓰지 않는다. 문제 구성(이정원 교수님 기출 몇 개, 다른 기출 몇 개, 변형 몇 개)과 "먼저 풀어 보고, 막히면 힌트를 열어 보세요"처럼 "~해요" 체 한 문장 안내(이모지 없이) |
| `footer_note` | HTML 허용. `출처: 이정원 교수님 강의록(Software_N–M) · 수업 녹음 전사(MMDD…).` |
| `footer_review` | HTML 허용. `출처: 자료구조및알고리즘(이해) 기출 — <이번 팩에 쓴 원본을 "2016 기말(이정원), 2019 중간(출제자 미상)"처럼>. 풀이는 자체 작성이며 답은 Python·C 실행으로 검증했습니다.` |
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
- 문제 선별은 `references/problem-selection.md`. 개수 8~12(부족하면 그 파일의 규칙).
- 문제 `id`: `p1`, `p2`, … 빈 번호 없이 순서대로(카드 파일명 `cards/<id>.html`이 된다). `part`: 위 `parts`의 id 중 하나.
- `source`: 은행 문항 id(예: `"2016-final-ljw-q3"`). 변형도 원래 문항 id를 쓰고 `variant: true`.
- `anchor`: 풀이가 기대는 정리노트 토픽 id(카드에 링크로 쓰지는 않는다). `level`: `problem-selection.md`의 level 표. `date`: 관련 수업 날짜.
- `terms`: 카드에 반드시 나올 글자(정답 포함). **모두 빈 문자열이 아닌 문자열**이다. 예: `"front=4"`, `"rear=2"`, `"60 40 30 15 12 6 10 5"`. `required_terms`, `forbidden_outside_preview`도 같다(`manifest.py`가 검사).
- `answer`: `<RUN>/answers.py`로 계산한 정답 문자열. 계산 스크립트 경로를 보고서에 적는다.

## links
- `href`는 작성자가 `<a href="…">`에 **글자 그대로** 넣을 값이다(검사기가 해당 `topic` 안의 링크와 정확히 비교한다). `%20` 같은 인코딩도 그대로.
- `{"topic": "s<N>-links", "href": "복습문제_<range>_<slug>.html"}`는 항상. 파일명은 `manifest.py`의 `review_name`이 만드는 것과 정확히 같아야 한다.
- 이번 범위 강의록 중 파일명이 영문인 것(2~12장)은 `s<N>-links`에 `../../자료구조_강의록_2026/Software_<N>_<이름>.pdf`를 건다. 1장 PDF는 파일명이 한글이라 걸지 않는다.
- 이전 복습팩과 이어지는 개념이면 `../<이전 range>/정리노트_<이전 range>_<slug>.html#<토픽>` 링크를 건다(팩마다 `복습노트/<range>/` 폴더라 한 단계 위로 올라간다). 토픽은 기본 `s<N>-links`, 특정 토픽에 거는 편이 분명하면 그 토픽 id.
````

- [ ] **Step 6: `references/problem-selection.md` 전체를 아래로 바꾼다**

````markdown
# 문제 선별 규칙 (기출 문제은행 전용)

## 원칙
- 문제는 **기출 문제은행(`from_the_past/기출/문제은행.json`)에서만** 가져온다. 자작 문제 금지.
- 변형은 원본 문항이 8개보다 적을 때만 만든다. 숫자·데이터 값만 바꾸고, 구조(자료구조 종류와 크기, 연산 순서의 꼴, 코드 모양, 묻는 것)는 그대로 둔다. 구조를 바꾸면 자작 문제다.
- 수업에서 배운 내용만으로 풀 수 있어야 한다. `bank.py select`의 챕터 조건이 먼저 거르고, 메인 에이전트가 문항 글을 읽어 수업에서 안 다룬 개념(같은 챕터라도 슬라이드 대조표에서 "안 다룸"인 연산 등)이 한 단계라도 필요하면 뺀다. 뺀 문항과 이유는 보고서 "스킬이 정한 사항"에 적는다.
- 개수: 8~12문항.

## 순서
1. 후보를 뽑는다(이미 쓴 문항은 빠진다):
   ```bash
   python3 "$SKILL/scripts/bank.py" select "$BANK" --range-ch <range_ch> --taught <taught> --used-dir "$REPO/복습노트"
   ```
   출력은 이미 우선순위 순이다(출제자 이정원 > 미상 > 그 밖, 유형 trace·code-read > blank·short·code-write > essay > ox, 최근 연도, OX 최대 2개).
2. 위에서부터 읽으며 12개까지 고른다. 같은 개념(예: 원형 큐 front/rear 계산)이 셋 이상 겹치면 뒤의 것을 건너뛴다.
3. 고른 원본 문항이 8개 미만이면 변형을 더해 8개로 맞춘다.
   - 변형 후보: `--used-dir` 없이 다시 `select`한 목록(이전 팩에서 쓴 문항 포함) 중 `trace`, `code-read`, `blank`.
   - 변형 문항의 manifest `source`는 원래 문항 id, `variant: true`, `part: "partC"`.
4. 변형까지 더해도 4개가 안 되면 있는 만큼 쓰고 보고서 "미해결"에 "문항 부족(N개)"을 적는다.

## parts
| id | title | short | 들어가는 문항 |
|---|---|---|---|
| `partA` | `A. 이정원 교수님 기출` | `A 이정원 기출` | 출제자 이정원, 원본 그대로 |
| `partB` | `B. 다른 기출` | `B 다른 기출` | 출제자 미상·그 밖, 원본 그대로 |
| `partC` | `C. 기출 변형` | `C 변형` | `variant: true` |

문항이 0개인 part는 뺀다.

## level
| level | 유형 |
|---|---|
| 1 | `ox`, `blank` |
| 2 | `trace`, `code-read`, `short` |
| 3 | `code-write`, `essay`, 또는 배점 10점 이상 |

## 문항 원문 모으기
카드 작성자가 볼 `<RUN>/problems.md`를 메인 에이전트가 만든다. 고른 문항마다:
```
## <은행 문항 id>  (manifest id pN, variant true/false)
- 원본: <연도> <시험> <번호>번 · <배점>점 · <출제자> — <sources.file>
- 문제 글: <은행 text 그대로>
- 그림: <은행 figure 또는 "없음">
- 은행 정답: <answer> (<answer_origin>)
- 변형 값: <변형이면 바꾼 숫자, 아니면 "없음">
- 전사 기록: <from_the_past/기출/_전사/<source-id>.md 에서 그 번호 절 그대로>
```

## 정답
- 모든 정답을 `<RUN>/answers.py`에서 다시 계산한다. 자료구조 연산은 Python으로 그대로 시뮬레이션하고(리스트로 만든 스택·큐·힙, 딕셔너리로 만든 트리), C 코드를 읽는 문제는 `<RUN>/work/`에서 `cc -std=c11 -Wall -o <이름> <이름>.c`로 컴파일해 실행한다.
- 은행 `answer`와 다르면 실행값을 쓰고 보고서 "은행과 다른 답"에 적는다. 은행 파일은 고치지 않는다(다음 `bank` 실행 때 반영).
- 그림으로 답하는 문제(트리 그리기 등)는 결과를 순회 순서나 배열 표현 같은 글자로도 적어 manifest `terms`에 넣는다(예: 레벨 순서 `60 40 30 15 12 6 10 5`).
````

- [ ] **Step 7: `references/stt-summary-prompt.md` 전체를 아래로 바꾼다**

````markdown
# STT 요약 에이전트 지시문

메인 에이전트는 날짜마다 아래 브리프로 에이전트 1명을 띄운다(병렬, model: opus / lite: sonnet).

---
자료구조및알고리즘이해(이정원 교수님) <MMDD> 수업 녹음 전사를 정밀 요약한다.

- 입력(읽기 전용): `<RUN>/repo/STT/<MMDD 자구알.md>` — **처음부터 끝까지 전부** 읽는다. 건너뛰지 않는다.
- 대조 자료: `<RUN>/repo/자료구조_강의록_2026/<Software_N_*.pdf>` 슬라이드 텍스트(메인이 추출해 `<RUN>/slides.txt`에 둠, 쪽 표시 `=== S<N> p<k> ===`)
- 출력: `<RUN>/summaries/stt-<MMDD>.md` 한 파일만 쓴다. 다른 곳에는 쓰지 않는다(임시 파일은 아래 규칙).
- 임시·보조 파일(스크립트, 초안, 그림 생성 폴더)은 `<RUN>/work/` 아래에만 둔다. 저장소(`STT/`, `자료구조_강의록_2026/`, `from_the_past/`, `복습노트/`)와 scratchpad 루트, `/tmp`에는 아무것도 쓰지 않는다. 한글(NFD) 파일명은 복사하거나 이름을 바꾸지 말고 Python `os.listdir` + `unicodedata.normalize('NFC', …)`로 찾아 그 경로로 연다.

출력 형식:
1. `# <MMDD> 자료구조및알고리즘이해 강의 개요 (이정원 교수, <YYYY-MM-DD>)`
2. **총평**: 녹음 길이, 이번 수업이 다룬 강의록과 쪽 범위(예: "S2 p1–14"), **시작하지 않은** 쪽, 흐름 한 줄.
3. 흐름 순서대로 `## N. 제목 (Part PP MM:SS–MM:SS)` 절. 각 절에:
   - **핵심 내용**: 정의, C 코드(슬라이드 코드는 `c` 펜스로 글자 그대로), 동작 추적(스택·큐 상태 변화, 재귀 호출 순서), 시간복잡도(TeX `$O(n)$`). 슬라이드에 없는 설명은 `[슬라이드 외]` 표시.
   - **비유와 일화**: 개념을 싣는 비유만. 순수 잡담(출석, 자리, 이메일 등)은 쓰지 않는다.
   - **학생과의 대화**: 학생 이름은 "한 학생".
   - 강조 발언: 원문 인용 + `(MM:SS)`. "중요", "시험", "꼭", "중간고사", "기말", "과제", "실습" 같은 표현이 붙은 발언은 모두.
   - "나중에 할게요/설명은 생략" 처럼 **미룬 설명**은 `🕳️ 미룬 유도:`로 표시.
4. `## 슬라이드 대조표`: | 쪽 | 다룸/일부/예고만/안 다룸 | 근거 타임스탬프 | — 쪽은 `S2 p7`처럼.
5. `## 용어·코드 목록`: 수업에서 실제로 쓴 용어(한국어·영어), 식(TeX), 한 줄 코드 조각(슬라이드 표기 그대로) — 정리노트 required_terms 후보.
6. `## 시험·과제 언급`: 시험 범위·출제 방식·과제에 대한 교수님 발언 원문과 `(MM:SS)`. 없으면 "없음".
7. `## 말실수 정정`: STT 오인식 또는 교수님 말실수와 올바른 형태.

보고: 파일 경로와 총평 3줄만 돌려준다.
---
````

- [ ] **Step 8: `references/review-prompt.md` 전체를 아래로 바꾼다**

````markdown
# 리뷰어 지시문 (lite에서는 생략)

---
자료구조및알고리즘이해 복습팩 초안을 검토한다. 파일은 수정하지 않는다.

- 대상: `<RUN>/repo/복습노트/<range>/<정리노트 html>`, `<…/복습문제 html>`
- 근거: `<RUN>/summaries/stt-*.md`, `<RUN>/slides.txt`, `<RUN>/manifest.json`, `<RUN>/answers.py`, `<RUN>/problems.md`, 기출 원본 `<RUN>/repo/from_the_past/기출/`
- 규칙: `<SKILL>/references/content-rules.md`, `card-rules.md`, `problem-selection.md`

확인할 것:
1. **사실 오류**: 정의, 코드, 추적 결과, 시간복잡도, 조건(예: "비어 있으면/가득 차면", "항상/보통")이 요약·슬라이드와 맞는가. 코드는 컴파일되는 C인가.
2. **누락**: 요약의 핵심 내용·강조 발언·시험 언급·미룬 설명 중 노트에 없는 것.
3. **범위**: "예고만/안 다룸" 내용이 본문에 설명되어 있는가.
4. **ELI5 품질**: 쉽게 말하면(eli5) 레이어가 전문용어·코드 없이 1~3문장인가, 그림이 개념을 실제로 보여 주는가.
5. **문제**: 카드가 `problems.md`의 원문과 숫자·코드·묻는 것까지 같은가(변형은 숫자만 다른가), 수업 범위로 풀 수 있는가, 정답이 `answers.py`와 같은가(직접 다시 계산·실행).
6. **표현**: 표 첫 열이 한 글자씩 줄바꿈되거나 빈 칸이 있는 표, 잘린 문장, 가로로 너무 긴 코드 줄(80자 초과).

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
````

- [ ] **Step 9: `widget-rules.md`와 `browser-check.md`의 한 줄씩**

`$SK/references/widget-rules.md` 4행:
- 기존: `- 팩 전체에 0~2개. "슬라이더를 움직이면 개념이 보이는" 경우만(예: λ와 과적합, prior 강도와 MAP).`
- 새: `- 팩 전체에 0~2개. "버튼·슬라이더를 움직이면 동작이 보이는" 경우만(예: 재귀 호출 상자를 한 단계씩 쌓고 풀기, 원형 큐에 넣고 빼며 front·rear 보기).`

`$SK/references/browser-check.md` 20행 끝의 괄호 부분을 바꾼다. 기존:
```
(`.katex-display`·`.table-wrap` 안의 자체 가로 스크롤은 넘침이 아니다)
```
새:
```
(`.katex-display`·`.table-wrap`·`pre` 안의 자체 가로 스크롤은 넘침이 아니다)
```

- [ ] **Step 10: 통과 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 97 tests` … `OK`

그리고 문서 안 ML 흔적이 그물 밖에서도 없는지 눈으로 한 번 본다:
Run: `grep -rn -E "λ|prior|MAP|likelihood|최소제곱" "$SK/references"`
Expected: `widget-rules.md`의 CSS 클래스 이름 줄(`plot-prior`, `mark-map` 등 템플릿 클래스 목록)만 나온다. 다른 줄이 나오면 자구알 예시로 바꾼다.

- [ ] **Step 11: Commit**

```bash
git -C "$WT" add .claude/skills/ds-review-pack/references .claude/skills/ds-review-pack/tests/test_skill_files.py
git -C "$WT" commit -m "docs(skill): writer and reviewer briefs for data structures course

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: SKILL.md 본문과 문제은행 구축 규칙

**Files:**
- Rewrite: `$SK/SKILL.md`
- Create: `$SK/references/bank-build.md`
- Test: `$SK/tests/test_skill_files.py` (`TestSkillFiles` 클래스와 그 위 상수)

**Interfaces:**
- Consumes: Task 4 CLI 세 가지, Task 5 브리프 파일과 자리표시자, ML 백업 스니펫(글자 그대로 — `TestBackupSnippet`이 정규식으로 뽑아 실행한다)
- Produces: `/ds-review-pack bank`, `/ds-review-pack [MMDD|MMDD-MMDD] [lite]` 절차. 은행 경로 `from_the_past/기출/문제은행.json`, 전사 기록 `from_the_past/기출/_전사/<source-id>.md`, 검증 스크립트 `from_the_past/기출/_정답검증/<source-id>.py`

- [ ] **Step 1: 실패 테스트 작성**

`$SK/tests/test_skill_files.py`에서 `SKILL_MD = SKILL / "SKILL.md"` 줄부터 `class TestBackupSnippet` 바로 앞까지를 아래로 바꾼다(`TestBackupSnippet` 이하와 파일 맨 위 import는 그대로 둔다).
```python
SKILL_MD = SKILL / "SKILL.md"
ML_WORDS = ("MML", "머신러닝", "정방철", "교과서", "머러기", "Lecture", "강의노트/")


class TestSkillFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SKILL_MD.read_text(encoding="utf-8")

    def test_frontmatter(self):
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n---\n", self.text)
        self.assertIsNotNone(m, "frontmatter는 name, description 두 줄")
        self.assertEqual(m.group(1), "ds-review-pack")
        for word in ("정리노트", "복습문제", "문제은행"):
            self.assertIn(word, m.group(2))
        self.assertLessEqual(len(m.group(2)), 1024)

    def test_referenced_files_exist(self):
        refs = set(re.findall(r"(?:references|scripts|assets)/[\w.-]+\.(?:md|py|html)", self.text))
        self.assertGreaterEqual(len(refs), 14)
        for rel in sorted(refs):
            with self.subTest(rel=rel):
                self.assertTrue((SKILL / rel).exists(), rel)

    def test_every_reference_is_used(self):
        for path in sorted((SKILL / "references").glob("*.md")):
            with self.subTest(ref=path.name):
                self.assertIn(f"references/{path.name}", self.text)

    def test_steps_present(self):
        for n in range(10):
            with self.subTest(step=n):
                self.assertRegex(self.text, rf"\n### {n}\. ")

    def test_bank_steps_present(self):
        for n in range(1, 5):
            with self.subTest(step=n):
                self.assertRegex(self.text, rf"\n### B{n}\. ")

    def test_no_ml_leftovers(self):
        for path in [SKILL_MD, *sorted((SKILL / "references").glob("*.md"))]:
            text = path.read_text(encoding="utf-8")
            for word in ML_WORDS:
                with self.subTest(file=path.name, word=word):
                    self.assertNotIn(word, text)


```

- [ ] **Step 2: 실패 확인**

Run: `python3 -m unittest discover -s "$SK/tests" -p test_skill_files.py`
Expected: FAIL 3건 — `test_referenced_files_exist`(참조 14개 미만), `test_bank_steps_present`(`### B1.` 없음), `test_no_ml_leftovers`(SKILL.md에 "MML" 등). `test_frontmatter`는 Task 1의 description에 "문제은행"이 이미 있어 통과한다.

- [ ] **Step 3: `references/bank-build.md` 작성**

````markdown
# 문제은행 구축 규칙 (`bank` 모드)

문제은행은 `from_the_past/기출/문제은행.json` 한 파일이다. 스키마 검사는 `scripts/bank.py validate`가 한다.

## 원본 표
id와 메타데이터는 이 표로 고정한다(전사 에이전트가 정하지 않는다). `file`은 `from_the_past/기출/` 기준 상대 경로다. 파일명이 NFD일 수 있으니 `os.listdir` + NFC 비교로 찾는다.

| id | file | year | exam | professor | transcribed_from |
|---|---|---|---|---|---|
| `2015-ljw` | `자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 2015기출(이정원).pdf` | 2015 | 미상 | 이정원 | scan |
| `2016-final-ljw` | `자료구조및알고리즘이해 기출 소스/자료구조및알고리즘 기말 (2016이정원)/` (jpg 9장, 파일명 순) | 2016 | 기말 | 이정원 | photo |
| `2017-mid-c050` | `자구알 기출/자료구조및알고리즘_중간고사+(모범답안+공지용).pdf` | 2017 | 중간 | 미상 | text |
| `2017-final-kdh` | `자료구조및알고리즘이해 기출 소스/자료구조및알고리즘_기말고사 (모범답안), 2017 김도희.pdf` | 2017 | 기말 | 김도희 | text |
| `2017-final2` | `자구알 기출/자료구조및알고리즘_기말고사_(공지용_모범답안).pdf` | 2017 | 기말 | 미상 | text |
| `2018-mid-c024` | `자구알 기출/2018_2_자료구조및알고리즘_중간고사_C024_화B목A (공지용).hwp` | 2018 | 중간 | 미상 | hwp |
| `2018-mid-c102` | `자구알 기출/2018_2_자료구조및알고리즘_중간고사_C102_화B목A (공지용).hwp` | 2018 | 중간 | 미상 | hwp |
| `2019-mid` | `자구알 기출/19-1 중간 복원.txt` | 2019 | 중간 | 미상 | txt |
| `2019-final` | `자구알 기출/19-1 기말 복원.hwp` | 2019 | 기말 | 미상 | hwp |
| `2021-mock1` | `자료구조및알고리즘이해 기출 소스/2021학년도 2학기 자료구조및알고리즘이해 기말고사 모의 1회.pdf` | 2021 | 모의 | 미상 | text |
| `unk-final-ltk` | `자료구조및알고리즘이해 기출 소스/자료구조 기말(이태권).pdf` | null | 기말 | 이태권 | text |

- 출제자는 파일명이나 원본 글에 이름이 있을 때만 적는다. 분반 코드 같은 간접 근거로 추측하지 않는다.
- `reviewed`: `text`·`hwp`·`txt`는 `true`, `scan`·`photo`는 `false`. 이전 은행(`RUN/previous-bank.json`)에 같은 id가 `reviewed: true`로 있으면 `true`를 그대로 둔다.
- `has_key`: 전사 에이전트가 원본에 답(모범답안, 괄호 속 답)이 있는지 보고 적는다.

## 정규화 (메인 에이전트, 결과는 `RUN/work/`)
| transcribed_from | 할 일 |
|---|---|
| `txt` | `iconv -f CP949 -t UTF-8 "<원본>" > "$RUN/work/<id>.txt"` |
| `hwp` | `hwp-to-pdf` 스킬로 PDF를 만들어 `$RUN/work/<id>.pdf`에 둔다(스킬이 원본 옆에 쓰면 그 PDF를 `$RUN/work/`로 옮긴다). 그다음 `text`와 같이 한다. 변환에 실패하면 그 원본을 빼고 보고서에 적는다 |
| `text` | 텍스트를 `$RUN/work/<id>.txt`로 뽑고, 쪽 이미지도 만든다(표·그림은 텍스트 추출에서 깨진다) |
| `scan` | 쪽 이미지만 만든다 |
| `photo` | 할 일 없음. jpg 경로 목록을 파일명 순으로 브리프에 넘긴다 |

쪽 이미지·텍스트 추출:
```bash
SRC="<원본 또는 변환된 PDF>" OUT="$RUN/work/<id>" python3 - <<'EOF'
import fitz, os
out = os.environ["OUT"]
os.makedirs(out, exist_ok=True)
doc = fitz.open(os.environ["SRC"])
with open(out + ".txt", "w", encoding="utf-8") as f:
    for i, page in enumerate(doc, 1):
        f.write(f"=== p{i} ===\n{page.get_text()}\n")
        page.get_pixmap(dpi=150).save(os.path.join(out, f"p{i}.png"))
print("쪽", doc.page_count, "→", out)
EOF
```

## 전사 브리프 (원본마다 1명, 병렬, model: opus / lite: sonnet)

---
자구알 기출 원본 `<source-id>`를 전사한다.

- 원본(읽기 전용): `<원본 경로들>` — 쪽 이미지 `<RUN>/work/<source-id>/p*.png`, 텍스트 `<RUN>/work/<source-id>.txt`(있으면), 사진이면 jpg 경로 목록. 이미지는 Read로 직접 본다. 텍스트가 있어도 표·그림·코드 들여쓰기는 이미지로 확인한다.
- 읽기: `<SKILL>/references/bank-build.md`(이 파일 전체)
- 출력: `<RUN>/parts/<source-id>.md`(전사 기록), `<RUN>/parts/<source-id>.json`(문항 조각). 다른 곳에 쓰지 않는다. 임시 파일은 `<RUN>/work/<source-id>/` 아래에만. 저장소(`from_the_past/` 포함)에는 아무것도 쓰지 않는다.
- 전사 기록(.md): 원본 순서대로 `## <번호>번`마다 문제 글을 **원문 그대로**(맞춤법·띄어쓰기도 원문대로, 읽을 수 없는 글자는 `[?]`). 코드는 `c` 펜스, 그림은 `[그림: …]`으로 모양을 글로(트리는 레벨 순서와 부모-자식, 표는 마크다운 표). 원본에 답이 있으면 `**원본 답:**` 줄. 맨 위에 `# <source-id>`와 원본 파일 경로.
- 문항 조각(.json):
  ```json
  {"source": "<source-id>", "has_key": true,
   "problems": [{"id": "<source-id>-q3", "source": "<source-id>", "number": "3", "chapters": [6],
                 "type": "trace", "points": 4, "text": "…", "figure": null,
                 "answer": "…", "answer_origin": "key", "duplicate_of": null}]}
  ```
  - 문항 하나 = 원본의 큰 번호 하나. (a)(b) 같은 하위 문항은 한 문항으로 묶고 `text`에 모두 적는다.
  - `chapters`: 아래 챕터 표로, 풀이에 꼭 필요한 챕터 전부.
  - `type`: `ox`(참/거짓), `blank`(빈칸), `trace`(연산 결과·상태를 구함), `code-read`(코드를 읽고 결과·기능을 답함), `code-write`(코드를 씀), `short`(짧은 서술·정의), `essay`(긴 서술).
  - `points`: 배점 정수, 없으면 `null`. `figure`: 그림이 있으면 한 줄 설명, 없으면 `null`.
  - `text`: 전사 기록의 그 번호 문제 글과 같게(코드는 펜스 포함).
  - `answer`: 원본 답이 있으면 그 답(`answer_origin: "key"`), 없으면 직접 푼 답(`"unverified"` — 메인 에이전트가 검증한다). 그림 답은 글로(레벨 순서, 배열 표현).
  - `duplicate_of`: 항상 `null`(메인 에이전트가 채운다).
- 자기 검사: 원본의 문항 수와 조각 문항 수가 같은지, `python3 -m json.tool <RUN>/parts/<source-id>.json` 통과, `[?]` 개수.
- 보고: 문항 수, `[?]` 개수와 위치, 원본에 답이 있었는지, 챕터를 정하기 어려웠던 문항.
---

## 챕터 표 (강의록 `자료구조_강의록_2026/Software_<N>_*.pdf`)
| N | 강의록 | 다루는 것 |
|---|---|---|
| 1 | `Software_1_자료구조및알고리즘.pdf` | 프로그래밍 언어 분류, 자료구조·알고리즘 개념, 시간복잡도 |
| 2 | `Software_2_Recursion.pdf` | 재귀 |
| 3 | `Software_3_ArrayStructureList.pdf` | 배열, 구조체, 포인터 |
| 4 | `Software_4_List.pdf` | 연결 리스트 |
| 5 | `Software_5_Stack.pdf` | 스택, 수식 표기(후위 표기) |
| 6 | `Software_6_Queue.pdf` | 큐, 원형 큐, 덱 |
| 7 | `Software_7_Tree.pdf` | 트리, 순회, 이진 탐색 트리 |
| 8 | `Software_8_Heap.pdf` | 힙 |
| 9 | `Software_9_Sorting.pdf` | 정렬 |
| 10 | `Software_10_Graph.pdf` | 그래프 |
| 11 | `Software_11_Hash.pdf` | 해싱 |
| 12 | `Software_12_Search.pdf` | 탐색 |

- 이진 탐색 트리는 7, 배열 이진 탐색은 12. 코드의 시간복잡도를 묻는 문제는 1과 그 코드의 자료구조 챕터.
- 표만으로 애매하면 해당 강의록 PDF를 열어 그 개념이 있는 챕터를 고른다.

## 정답 검증 (메인 에이전트)
- 원본마다 `RUN/work/verify_<source-id>.py`를 쓴다. 문항마다 함수 `q<번호>()`가 답 문자열을 돌려주고, 실행하면 `<문항 id>\t<답>`을 한 줄씩 출력한다. 자료구조 연산은 Python으로 그대로 시뮬레이션한다.
- C 코드 문제는 코드를 스크립트 안 문자열로 넣고 `tempfile` 폴더에서 `cc -std=c11 -Wall`로 컴파일·실행한다(저장소로 옮겨도 혼자 돌아가게).
- 판정:
  | 조각의 answer_origin | 실행 결과 | 은행에 쓸 값 |
  |---|---|---|
  | `key` | 같음 | `key` 그대로 |
  | `key` | 다름 | answer = 실행값, `verified`, 보고서 "모범답안과 다른 답" |
  | `unverified` | 같음 | `verified` |
  | `unverified` | 다름 | answer = 실행값, `verified`, 보고서 "에이전트 답과 다른 답" |
  | 실행으로 확인할 수 없음(`essay`, 정의형 `short`·`ox`) | — | `key`면 그대로, 아니면 `unverified` |

## 중복 문항
- 문항 글에 "[2015-1 기출]"처럼 다른 시험을 가리키는 표시가 있거나, 다른 원본 문항과 숫자·코드까지 같으면 `duplicate_of`에 원래 시험 쪽 문항 id를 적는다(원래 시험이 은행에 없으면 `null`로 두고 보고서에 적는다).
- 원 문항 쪽의 `duplicate_of`는 `null`이어야 한다(`bank.py validate`가 검사).
````

- [ ] **Step 4: `SKILL.md` 전체를 아래로 바꾼다**

`### 4. 조립`의 백업 스니펫은 글자 하나 바꾸지 않는다(`TestBackupSnippet`이 ```` ```bash\nRANGE=<range> REPO=… RUN=… python3 - <<'EOF'\n ```` 부터 `EOF` 까지를 정규식으로 뽑아 실행한다).

`````markdown
---
name: ds-review-pack
description: 자료구조및알고리즘이해(자구알) 수업의 STT·강의록으로 ELI5 정리노트 HTML과 기출 기반 복습문제 HTML(+MD, 그림)을 만들어 복습노트/<날짜>/ 폴더에 저장하고, 기출 원본으로 문제은행을 만든다. "자구알 정리노트", "자구알 복습문제", "복습팩", "기출 문제은행 만들어줘"처럼 자구알 수업 정리나 기출 정리를 요청하거나 /ds-review-pack [bank | MMDD | MMDD-MMDD] [lite]로 부를 때 사용한다.
---

# 자구알 복습팩

수업 녹음 전사(STT)와 강의록(`자료구조_강의록_2026/`), 기출 문제은행으로 한 기간의 복습팩을 만든다. 문제은행은 `bank` 모드로 먼저 한 번 만들어 둔다. 중간에 사용자에게 묻지 않고 끝에 한 번 보고한다. 커밋은 제안만 한다.

**모드**
- `bank`: 기출 원본을 전사해 문제은행을 만들거나 다시 만든다. 절차는 "문제은행 모드" B1~B4.
- 그 밖(`[MMDD | MMDD-MMDD] [lite]`): 복습팩을 만든다. 절차는 "복습팩 절차" 0~9.

**산출물** (복습팩, `복습노트/<range>/`, 수업 날짜마다 폴더 하나):
`정리노트_<range>_<slug>.html`, `복습문제_<range>_<slug>.html`, 같은 이름의 `.md` 두 개, `figures_<range>/`

**인자**: `[bank | MMDD | MMDD-MMDD] [lite]`
- `lite`: 작성자·요약·전사 에이전트를 sonnet으로, 6단계 리뷰를 생략한다. 기계 검사와 브라우저 검사는 그대로 한다.

**진행 표시**: 단계마다 한 줄만 쓴다. 예: `3/9 작성 중: 섹션 4개 + 카드 9개 (병렬)`, `B3 전사 중: 원본 11개 (병렬)`

**경로 약속**
- `SKILL` = 이 파일이 있는 폴더(`.claude/skills/ds-review-pack`)의 절대 경로
- `REPO` = 저장소 루트
- `BANK` = `REPO/from_the_past/기출/문제은행.json`
- `RUN` = 복습팩은 `<scratchpad>/ds-review-pack/<range>/`, 문제은행은 `<scratchpad>/ds-bank/<YYYYMMDD-HHMMSS>/`
- 셸 상태는 Bash 호출 사이에 이어지지 않는다. 아래 명령의 `$SKILL`, `$RUN`, `$REPO`, `$BANK`는 실행할 때마다 실제 절대 경로로 바꿔 쓰거나, 같은 명령 앞에 `SKILL=… RUN=… REPO=… BANK=…`를 붙여 설정한다. `cd`는 쓰지 않고 파일도 절대 경로로 넘긴다.

## 문제은행 모드 (`bank`)

### B1. 준비
1. `REPO/from_the_past/기출/`이 있는지 확인한다. 없으면 "자구알 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. 실행 폴더를 만든다: `mkdir -p "$RUN"/{parts,work} && ln -sfn "$REPO" "$RUN/repo"`
3. `BANK`가 이미 있으면 `RUN/previous-bank.json`으로 복사한다(`reviewed` 값을 이어받는 데 쓴다).
4. 원본 목록과 id는 `references/bank-build.md`의 원본 표를 따른다. 표에 없는 파일이 `from_the_past/기출/` 아래에 있으면 보고서 "새 원본"에 적고 이번에는 넣지 않는다.

### B2. 정규화
`references/bank-build.md`의 "정규화"대로 원본을 `RUN/work/`에 읽을 수 있는 형태로 만든다(cp949 → UTF-8, hwp → PDF, PDF → 텍스트·쪽 이미지).

### B3. 전사 (병렬)
원본마다 전사 에이전트 1명을 **한 메시지에서 병렬로** 띄운다(opus, `lite`이면 sonnet). 브리프는 `references/bank-build.md`의 "전사 브리프"이며 `<source-id>`, `<원본 경로들>`, `<RUN>`, `<SKILL>`을 채워 넘긴다. 각자 `RUN/parts/<source-id>.json`과 `RUN/parts/<source-id>.md`를 쓴다.

### B4. 합치기·검증·저장
1. 조각을 합쳐 `RUN/bank.json`(`{"version": 1, "sources": [...], "problems": [...]}`)을 만든다. `sources`는 원본 표 값에 조각의 `has_key`와 `reviewed` 규칙(`references/bank-build.md`)을 더한다.
2. 챕터 태그를 `references/bank-build.md`의 챕터 표로 다시 본다.
3. 중복 문항(`duplicate_of`)을 `references/bank-build.md`의 "중복 문항"대로 채운다.
4. 정답을 `references/bank-build.md`의 "정답 검증"대로 확인해 `answer`, `answer_origin`을 정한다.
5. `python3 "$SKILL/scripts/bank.py" validate "$RUN/bank.json"` 결과가 `OK`여야 한다. 아니면 고치고 다시 검사한다.
6. 저장소에 쓴다(메인 에이전트만): `RUN/bank.json` → `BANK`, `RUN/parts/<id>.md` → `REPO/from_the_past/기출/_전사/<id>.md`, `RUN/work/verify_<id>.py` → `REPO/from_the_past/기출/_정답검증/<id>.py`.
7. 보고한다:
```
## 문제은행 완료
- 파일: from_the_past/기출/문제은행.json (원본 N개, 문항 M개), _전사/ N개, _정답검증/ N개
- 챕터별 문항 수: 1장 a · 2장 b · …
- 검수 대기(reviewed: false): 2015-ljw(스캔), 2016-final-ljw(사진) — _전사/<id>.md를 원본과 대조한 뒤 문제은행.json의 그 원본 reviewed를 true로 바꿔 주세요
- unverified 문항: … (없으면 "없음")
- 모범답안과 다른 답: … (실행값 채택, 없으면 "없음")
- 빠진 원본·새 원본: … (없으면 "없음")
- 커밋 제안: git add from_the_past/기출/문제은행.json from_the_past/기출/_전사 from_the_past/기출/_정답검증 && git commit -m "data(bank): build past-exam bank"
```

## 복습팩 절차

### 0. 준비
1. `REPO`에 `STT/`, `자료구조_강의록_2026/`이 모두 있는지 확인한다. 없으면 "자구알 저장소에서만 동작합니다"라고 알리고 멈춘다.
2. `BANK`가 없으면 "먼저 `/ds-review-pack bank`로 문제은행을 만들어 주세요"라고 알리고 멈춘다. 있으면 `python3 "$SKILL/scripts/bank.py" validate "$BANK"`가 `OK`여야 한다. 아니면 오류를 보여 주고 멈춘다.
3. STT 목록은 NFC로 읽는다. macOS에는 NFD 파일명이 섞여 있다.
   ```bash
   python3 -c "import os,unicodedata as u,re;n=[u.normalize('NFC',f) for f in os.listdir('$REPO/STT')];print(sorted(m.group(1) for f in n if f.endswith(' 자구알.md') and (m:=re.match(r'(\d{4})',f))))"
   ```
4. 기간을 정한다.
   - 인자가 있으면 그 기간을 쓴다.
   - 인자가 없으면 `복습노트/*/정리노트_<range>_*.html` 중 가장 늦은 끝 날짜를 찾고, 그 뒤의 STT를 모두 쓴다. `정리노트_*`가 하나도 없으면 STT 전부를 쓴다.
   - 해당 STT가 하나도 없으면 사용 가능한 날짜를 보여 주고 멈춘다.
   - `range`는 첫 STT 날짜 하나이거나 `첫-끝` 형식이다.
5. 실행 폴더를 만든다. 서브에이전트에게는 `RUN`, `RUN/repo`, `SKILL` 경로만 넘긴다.
   ```bash
   mkdir -p "$RUN"/{summaries,sections,cards,work} && ln -sfn "$REPO" "$RUN/repo"
   ```
   에이전트는 `RUN` 밖에 쓰지 않는다. 임시·보조 파일(그림 생성 스크립트, 초안, 복사본)은 `RUN/work/`에만 둔다. 저장소(`STT/`, `자료구조_강의록_2026/`, `from_the_past/`)에는 아무도 쓰지 않고, `복습노트/`에는 메인 에이전트만 쓴다.

### 1. 범위 파악
1. **먼저** 관련 강의록 텍스트를 쪽 번호와 함께 `RUN/slides.txt`에 추출한다(몇 초면 끝난다). 요약 에이전트는 이 파일이 있다고 보고 시작하므로 추출이 끝난 뒤에 띄운다.
   - 관련 챕터: 이전 팩 정리노트(`복습노트/*/정리노트_*.html`)의 `<span class="tag slide">S<N> p<k>` 중 가장 큰 챕터(그 챕터 마지막 쪽까지 다뤘으면 그다음 챕터)부터 두 챕터. 이전 팩이 없으면 1~3장. 확실하지 않으면 넉넉히 넣는다.
   ```bash
   CH="<관련 챕터 번호, 공백 구분>" REPO=… RUN=… python3 - <<'EOF'
   import fitz, os, re
   want = {int(x) for x in os.environ["CH"].split()}
   d = os.path.join(os.environ["REPO"], "자료구조_강의록_2026")
   with open(os.path.join(os.environ["RUN"], "slides.txt"), "w", encoding="utf-8") as f:
       for name in sorted(os.listdir(d)):
           m = re.match(r"Software_(\d+)_", name)
           if not m or int(m.group(1)) not in want:
               continue
           for i, page in enumerate(fitz.open(os.path.join(d, name)), 1):
               f.write(f"=== S{m.group(1)} p{i} ===\n{page.get_text()}\n")
   print("slides.txt:", sorted(want))
   EOF
   ```
   - 추출에 실패하면 STT만으로 진행하고 보고서에 적는다(브리프의 `slides.txt` 줄은 "없음"으로 바꿔 넘긴다).
2. 그다음 STT 날짜마다 요약 에이전트 1명을 **병렬로** 띄운다. 브리프는 `references/stt-summary-prompt.md`에 있다.
   - `<Software_N_*.pdf>`: 그 날짜가 다룬 쪽이 들어 있는 강의록(확실하지 않으면 관련 챕터의 강의록을 모두 적는다).
   - `<MMDD 자구알.md>`: NFC 목록에서 찾은 실제 파일명. `<YYYY-MM-DD>`: 연도는 이번 학기 연도(오늘 날짜 기준), 월·일은 `<MMDD>`.
3. 에이전트가 도는 동안 메인 에이전트는 관련 챕터로 후보 문항을 미리 본다(`references/problem-selection.md`의 `select` 명령, `--range-ch`와 `--taught`는 관련 챕터로 임시로).

### 2. manifest
- 요약들의 슬라이드 대조표로 `range_ch`(이번 범위에서 "다룸/일부"인 쪽이 있는 챕터)와 `taught`(1장부터 이번 범위의 마지막 챕터까지)를 정한다.
- 문제 선별은 `references/problem-selection.md`를 따른다.
  - 정답은 `RUN/answers.py`로 다시 계산한다.
  - 카드 작성자용 문항 원문은 `RUN/problems.md`에 모은다(형식은 `references/problem-selection.md`).
- manifest는 `references/manifest-guide.md`대로 `RUN/manifest.json`에 쓴다.
- 검증: 둘 다 `OK`여야 한다.
  ```bash
  python3 "$SKILL/scripts/manifest.py" "$RUN/manifest.json"
  python3 "$SKILL/scripts/bank.py" check-manifest "$BANK" "$RUN/manifest.json"
  ```

### 3. 작성
- 섹션마다 작성자 1명을 띄운다. 브리프는 `references/content-rules.md`, 위젯 규칙은 `references/widget-rules.md`에 있다.
- 문제 작성자 1명이 모든 카드를 쓴다. 브리프는 `references/card-rules.md`에 있다.
- 모두 **한 메시지에서 병렬로** 띄운다. 모델은 opus, `lite`이면 sonnet이다.
- 브리프의 `<…>` 자리는 실제 경로, id, 금지어 목록(`<forbidden 목록>`), 예고 토픽 id(`<preview_topic>`), 그리고 섹션 작성자에게는 manifest `links` 중 그 섹션 토픽에 속한 것만(`<이 섹션의 links 목록>`) 채워 넣는다.
- 위젯은 팩 전체에 0~2개다. 병렬 작성자끼리는 서로를 모르므로 **메인 에이전트가 띄우기 전에** 위젯을 둘 토픽(0~2개)을 정하고, 그 토픽의 섹션 작성자 브리프에만 `<위젯>` 자리에 "토픽 `<토픽 id>`에 위젯 1개: <무엇을 누르거나 움직이면 무엇이 보이는지>"를 적는다. 나머지 작성자의 `<위젯>` 자리에는 "위젯 없음"이라고 적는다. 정한 토픽과 이유는 보고서 "스킬이 정한 사항"에 적는다.

### 4. 조립
- **처음 조립할 때만**: `복습노트/<range>/`(또는 예전 형식인 `복습노트/` 바로 아래)에 이번 `range`의 산출물(`정리노트_<range>_*`, `복습문제_<range>_*`의 `.html`·`.md`, `figures_<range>/`)이 하나라도 있으면 먼저 백업한다. 다시 조립할 때(5~8단계에서 돌아온 경우)는 백업하지 않는다. 이미 스킬이 만든 초안이 백업에 섞이기 때문이다.
  - `RANGE`, `REPO`, `RUN`을 모두 실제 값으로 바꿔 한 명령으로 실행한다. 파일명은 NFC로 비교하므로 NFD 파일명도 잡힌다.
  - 백업은 매번 새 폴더 `RUN/previous-<시각>-<임의>/`에 만든다(이전 백업을 덮어쓰지 않음). `RANGE`가 형식에 안 맞거나, 대상이 있는데 복사된 파일 수가 다르면 종료 코드 1로 멈춘다. 이때는 조립하지 말고 원인을 고친다.
```bash
RANGE=<range> REPO=… RUN=… python3 - <<'EOF'
import os, re, shutil, sys, tempfile, time, unicodedata as u
r, run = os.environ["RANGE"], os.environ["RUN"]
notes = os.path.join(os.environ["REPO"], "복습노트")
if not re.fullmatch(r"\d{4}(-\d{4})?", r) or not os.path.isdir(run):
    sys.exit(f"백업 중단: RANGE={r!r} 또는 RUN={run!r} 잘못됨")
def want(n):
    n = u.normalize("NFC", n)
    return n.startswith((f"정리노트_{r}_", f"복습문제_{r}_")) or n == f"figures_{r}"
def listdir_nfc(d):  # NFD 폴더명도 찾는다
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}
srcs = [listdir_nfc(notes).get(r), notes]  # 날짜 폴더, 예전 형식(바로 아래)
hits = sorted({n: p for d in srcs if d and os.path.isdir(d) for n, p in listdir_nfc(d).items() if want(n)}.items())
if not hits:
    print("백업할 기존 팩 없음"); sys.exit(0)
def count(p):
    return sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 1
dst = tempfile.mkdtemp(prefix=time.strftime("previous-%Y%m%d-%H%M%S-"), dir=run)  # 항상 새 폴더
for n, a in hits:
    b = os.path.join(dst, n)
    shutil.copytree(a, b) if os.path.isdir(a) else shutil.copy2(a, b)
want_n, got_n = sum(count(a) for _, a in hits), count(dst)
if got_n != want_n:
    sys.exit(f"백업 실패: 파일 {want_n}개 중 {got_n}개만 복사됨 → {dst}")
print(f"백업 {len(hits)}항목(파일 {got_n}개): {dst}", *(a for _, a in hits), sep="\n")
EOF
```
```bash
python3 "$SKILL/scripts/assemble.py" --run "$RUN" --out "$REPO/복습노트/<range>"
```

### 5. 기계 검사
```bash
python3 "$SKILL/scripts/check_html.py" --manifest "$RUN/manifest.json" --note "$REPO/복습노트/<range>/<정리노트>.html" --review "$REPO/복습노트/<range>/<복습문제>.html"
```
- `FAIL`이면 Problem의 `where`(토픽 id, 카드 id, 섹션 id)로 담당 작성자를 찾는다.
- 그 작성자에게 문제 목록을 보내 조각을 고치게 한다(SendMessage, 안 되면 같은 브리프로 새 에이전트).
- 고친 뒤 4단계부터 다시 한다. 최대 2회까지이며, 그래도 남으면 "미해결"로 보고한다.

### 6. 리뷰 (`lite`면 생략)
- 리뷰어 1명을 띄운다. 브리프는 `references/review-prompt.md`에 있다.
- Critical과 Important는 모두, Minor는 쉬운 것만 고친다.
- 담당 작성자별로 **한 번에 모아서** 수정을 요청한다. 수정은 한 번만 한다.
- 수정 후 4~5단계를 다시 한다. 반영하지 않은 항목은 보고서에 적는다.

### 7. 브라우저 검증
- `references/browser-check.md`대로 한다.
  - http.server를 빈 포트에 띄운다.
  - 확인: KaTeX 오류 0, 남은 `$` 없음, 375px에서 가로 스크롤 없음(코드 블록은 자체 스크롤), 다크모드, 위젯, 링크, 콘솔 오류
- 결함은 5단계와 같은 방식으로 작성자에게 되돌린다. 이것도 최대 2회 규칙에 포함된다.
- 끝나면 서버를 종료한다.

### 8. MD 변환
```bash
python3 "$SKILL/scripts/html2md.py" "$REPO/복습노트/<range>/<정리노트>.html" "$REPO/복습노트/<range>/<복습문제>.html" --check
```
- `OK`가 나와야 한다.
- 누락이 나오면 대부분 HTML 조각의 마크업 문제다(수식이 `svg`나 `.controls` 안에 있는 경우 등). 조각을 고치고 4단계부터 다시 한다.

### 9. 보고
다음 형식으로 끝낸다.
```
## 복습팩 <range> 완료
- 파일: 복습노트/<range>/… (html 2, md 2, figures_<range>/ N개)
- 범위: 배운 쪽 S2 p1–20 … / 예고만: …
- 문제: P1 2016-final-ljw-q3 (2016 기말 3번, 이정원, trace) … / 변형 K개 (정답은 RUN/answers.py로 검증)
- 은행과 다른 답: … (없으면 "없음")
- 스킬이 정한 사항: slug, 섹션 구성, 위젯, 뺀 내용과 이유, 뺀 후보 문항과 이유
- 미해결: … (없으면 "없음")
- 커밋 제안: git add 복습노트/<range> && git commit -m "docs(notes): add ds review pack <range>"
```
실행 폴더 경로(`RUN`)도 적는다. 수정이 필요하면 조각을 고쳐 4단계부터 다시 돌리면 된다.

## 오류 처리
| 상황 | 동작 |
|---|---|
| 저장소가 아님 | 알리고 멈춤 |
| 문제은행 없음 | "먼저 `/ds-review-pack bank`" 안내 후 멈춤 |
| 문제은행 검사 실패 | `bank.py validate` 오류를 보여 주고 멈춤 |
| 기간에 해당하는 STT 없음 | 사용 가능한 날짜를 보여 주고 멈춤 |
| PDF 텍스트 추출 실패 | STT만으로 진행하고 보고서에 표시 |
| 후보 문항 8개 미만 | `references/problem-selection.md`의 변형 규칙. 4개 미만이면 "미해결"에 문항 부족 |
| hwp 변환 실패(`bank`) | 그 원본을 빼고 진행, 보고서 "빠진 원본"에 적음 |
| 원본 판독 불가(`bank`) | `[?]`로 표시하고 보고서에 적음 |
| 포트 사용 중 | 다른 빈 포트 사용 |
| 같은 range의 팩이 이미 있음 | 4단계 첫 조립 전에 기존 html·md·`figures_<range>/`를 새 폴더 `RUN/previous-<시각>-<임의>/`에 복사하고(다시 조립할 때는 복사하지 않음) 백업 경로를 보고서에 적음. 백업 명령이 실패하면 조립하지 않고 원인을 고친다 |
| 검사 2회 실패 | 멈추지 않고 나머지 단계를 끝낸 뒤 "미해결"로 보고 |
`````

- [ ] **Step 5: 통과 확인**

Run: `python3 -m unittest discover -s "$SK/tests"`
Expected: `Ran 98 tests` … `OK`

- [ ] **Step 6: Commit**

```bash
git -C "$WT" add .claude/skills/ds-review-pack/SKILL.md .claude/skills/ds-review-pack/references/bank-build.md .claude/skills/ds-review-pack/tests/test_skill_files.py
git -C "$WT" commit -m "docs(skill): ds-review-pack procedures for bank build and review packs

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: 병합과 실사용 검증 (원 트리, 사용자와 함께)

**Files:** 원 트리의 `from_the_past/기출/문제은행.json`, `_전사/`, `_정답검증/`, `복습노트/<range>/` (스킬이 만든다)

**Interfaces:**
- Consumes: Task 1~6의 스킬 전체
- Produces: 실제 문제은행과 첫 복습팩. 스킬 문서의 빈 곳이 드러나면 새 Task로 고친다.

- [ ] **Step 1: 병합**

원 트리는 `from_the_past/` 재배치가 커밋되지 않은 상태지만, 브랜치는 `.claude/skills/ds-review-pack/`과 `.gitignore`만 건드리므로 겹치지 않는다.
```bash
git -C /Users/hyunjun_macbook_pro/Documents/Univ/자구알 merge --ff-only feat/ds-review-pack
python3 -m unittest discover -s /Users/hyunjun_macbook_pro/Documents/Univ/자구알/.claude/skills/ds-review-pack/tests
git -C /Users/hyunjun_macbook_pro/Documents/Univ/자구알 worktree remove ../자구알-ds-review-pack
git -C /Users/hyunjun_macbook_pro/Documents/Univ/자구알 branch -d feat/ds-review-pack
```
Expected: fast-forward, `Ran 98 tests` … `OK`. `--ff-only`가 실패하면(그 사이 main에 커밋이 생김) 멈추고 사용자에게 알린다. `.gitignore`가 원 트리에서도 수정돼 있으면 병합 전에 사용자에게 알린다.

- [ ] **Step 2: 문제은행 구축 (새 세션)**

스킬은 세션을 시작할 때 읽히므로, 사용자가 원 트리에서 **새 세션**을 열고 `/ds-review-pack bank`를 실행한다. 새 세션에는 이 계획의 맥락이 없어서, 스킬 문서만으로 도는지가 곧 격리 검사가 된다. 실행한 에이전트에게 "문서만으로 막힘 없이 진행했는지, 막혔다면 어느 단계였는지"를 보고서 끝에 적게 한다.
확인할 것: `bank.py validate` OK, 원본 11개(빠진 원본이 있으면 이유), 검수 대기 2개(`2015-ljw`, `2016-final-ljw`).

- [ ] **Step 3: 사용자 검수 (N4)**

사용자가 `from_the_past/기출/_전사/2015-ljw.md`, `_전사/2016-final-ljw.md`를 원본 스캔·사진과 대조하고, 맞으면 `문제은행.json`에서 두 원본의 `reviewed`를 `true`로 바꾼다. 바꾼 뒤:
```bash
python3 /Users/hyunjun_macbook_pro/Documents/Univ/자구알/.claude/skills/ds-review-pack/scripts/bank.py validate /Users/hyunjun_macbook_pro/Documents/Univ/자구알/from_the_past/기출/문제은행.json
```
Expected: `OK: 원본 11개, 문항 N개`

- [ ] **Step 4: 첫 복습팩**

같은 새 세션(또는 또 다른 새 세션)에서 `/ds-review-pack 0921`을 실행한다.
확인할 것: `복습노트/0921/`에 html 2·md 2·`figures_0921/`, 5단계 검사 OK, 8단계 `--check` OK, 카드 `data-source`가 모두 은행 id, 코드 블록이 375px에서 가로 스크롤로 보이고 페이지는 넘치지 않음.
막힌 단계가 있으면 그 원인을 스킬 문서의 빈 곳으로 보고, 새 Task로 규칙이나 검사를 더한다(검사만 더하면 매번 사후 교정이 되므로 규칙도 함께 쓴다).

- [ ] **Step 5: 커밋 제안**

스킬 보고서의 커밋 제안을 사용자에게 보여 주고, 사용자가 원하면 커밋한다(은행·전사·검증 스크립트, `복습노트/0921`). 이 계획과 스펙(`docs/superpowers/`)도 함께 커밋할지 묻는다.
