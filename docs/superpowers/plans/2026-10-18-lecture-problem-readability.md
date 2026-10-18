# 강의노트 기반 문제 본문 구조화·경량화 및 문제설명 패널 서식 개선 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 10개 복습팩(`0907`–`1015`)의 강의노트 기반 문제(`lecture-code`, 47문항) 본문을 조건+코드 블록+핵심 소문항 `(a)`~`(c)` 목록으로 구조화·경량화하고, `문제설명_*.html`의 문제 패널(`.problem-pane`)과 PDF 생성기가 조건(`conditions`)과 질문(`ask`, `<h4>구할 것</h4>`)을 분리 렌더링하도록 개선한 뒤 전 산출물을 재발행한다.

**Architecture:** 먼저 `ds-problem-explain`의 `mpe_source.py`에 `split_lecture_statement`를 TDD로 추가해 `lecture-` 카드의 전제 조건과 마지막 `<ol>` 질문 목록을 `conditions_html`과 `ask_html`로 분리하고, `ds-review-pack`의 `pdf_lecture.py`가 `<p>` 조건 + `<ol>` 질문 구조를 무손실로 분리하도록 확장한다. 이어서 10개 팩의 47개 `lecture-code` 카드와 `문제설명` 프래그먼트(`fragments/pN.html`)를 개정해 `build_revision`·`mpe_cli.py`·`review_pdf.py` 파이프라인으로 HTML·MD·PDF를 일괄 재발행한다.

**Tech Stack:** Python 3.10+, pytest, PyMuPDF (`fitz`), Playwright + Chrome (`review_pdf.py`), `ds-review-pack` 및 `ds-problem-explain` 스킬 스크립트.

**Spec:** `docs/superpowers/specs/2026-10-18-lecture-problem-readability.md`

## Global Constraints

- `PE_SKILL=.agents/skills/ds-problem-explain`, `RP_SKILL=.agents/skills/ds-review-pack`, `REPO`=저장소 루트, `RUN=tmp/lecture-readability-2026-10-18`.
- 수정 대상 카드는 10개 복습팩의 `data-source-kind="lecture-code"` 47문항뿐이다. 기출(`past-exam`) 및 교과서(`textbook`) 카드는 `extract_cards`의 `raw`가 바이트 단위로 동일해야 한다.
- 각 `lecture-code` 카드의 `.problem` 구조:
  1. 첫 문단: `<p><span class="badge">강의 예제 기반 자체 출제</span> S<장> p<쪽></p>` (기존 `· 추가 근거 p…`는 `details.original`의 첫 문단 출처 표기로 이동·보존. 단 `0907 p4`의 `<p><strong>후속 수업 보충:</strong> …</p>`은 배지 앞/뒤 현행 위치 유지).
  2. 전제 조건: 1~2문장의 `<p>` 및 필요한 경우 초기 상태·구조체·함수 계약을 담은 `<pre><code class="language-c">…</code></pre>`.
  3. 질문 목록: 핵심 학습 목표 2~3개로 압축한 `<ol><li>(a) …</li><li>(b) …</li></ol>` (최대 `(c)`). 모든 C 식별자·포인터 식·수치 대입·복잡도에 인라인 `<code>`를 적용한다.
- 각 카드의 `id`, `data-source`, `data-source-kind="lecture-code"`는 변경하지 않으며, `.pack/자료_복습팩/manifest.json`의 필수 `terms`가 카드 텍스트 안에 100% 포함되어야 한다(`check_html.py:337`).
- `check_html.py`의 `LECTURE_REF_RE`(`강의|정리노트|슬라이드|S\d+ p\d+|…`)가 `.problem`(배지 제외)·`.hint`·`.solution`·`.answer`에서 0건이어야 한다.
- `ds-problem-explain` 스킬 파일(`scripts/mpe_source.py`, `assets/note-template.html`, `references/authoring.md`) 수정 시 반드시 `assets/port-provenance.json`의 `local_overrides` 체인에 역변환 가능한(reversible) `replacements` 항목과 SHA-256을 기록해 `test_claude_link_and_provenance`를 통과시켜야 한다.
- `fragments/pN.html`에서 `understand`는 1~2문장 핵심 요약으로 작성하고(문제 원문 통짜 복사 금지), `solve`와 `verify`는 `problem.subparts`(`('a', 'b')` 또는 `('a', 'b', 'c')`)와 정확히 일치하는 `<div data-subpart="a">…</div>` 블록들을 가져야 한다(`mpe_contract.py:58-61`).

## Review Focus

1. **비강의 카드(`past-exam`, `textbook`)의 `conditions_html`/`ask_html` 회귀 위험**: `split_lecture_statement`가 기출·교과서 문제의 `<ol>`(선지나 연산 나열)을 `ask_html`로 잘못 분리하면 기존 테스트와 원문 보존이 깨진다 → `source.startswith('lecture-')`일 때만 동작하도록 고정하고 Task 1 `test_non_lecture_ol_stays_in_conditions`로 검증한다.
2. **소문항 표지(`(a)`, `(b)`) 누락 시 `ExplainError` 발생**: `mpe_source.subparts`는 2개 이상의 질문 `<li>`에 `(a)`, `(b)` 접두사가 없으면 `ExplainError('소문항 질문 경계 모호함')`을 던진다 → 모든 `lecture-code` 질문 `<ol>`의 `<li>`를 `(a)`, `(b)`로 시작하게 하고 Task 1 `test_split_lecture_statement_with_subparts`로 검증한다.
3. **`pdf_lecture.split_lecture_problem`의 `<ol>` 폴백 충돌**: 기존 `pdf_lecture.py:56`은 `<ol>`이 있으면 조건 문단까지 통째로 `ask`로 반환해 PDF에서 `조건` 박스가 비어버린다 → Task 2에서 선행 `<p>` 블록은 `cond`로, 마지막 `<ol>` 블록은 `<ol class="ds-asks">`로 분리하고 `test_structured_lecture_ol_split`로 검증한다.
4. **소문항 경량화 후 `manifest.json`의 필수 `terms` 누락**: 질문을 2~3개로 줄이면서 `manifest.json`의 `terms` 토큰이 카드에서 빠지면 `check_html`이 `card-term` 오류를 낸다 → 각 팩 개정 단계(Task 4–7)에서 `check_review`가 `[]`인지 즉시 확인한다.
5. **`port-provenance.json` 역변환 체인 불일치**: `ds-problem-explain` 파일 수정 후 `local_overrides`에 정확한 `base_sha256`·`current_sha256`·`replacements`를 넣지 않으면 `test_skill_files.py`가 실패한다 → Task 1 Step 4에서 `pytest .agents/skills/ds-problem-explain/tests` 전체 통과로 고정한다.

---

### Task 1: `ds-problem-explain`의 `lecture-` 문항 `conditions`/`ask` 분리 및 템플릿 스타일 업데이트

**Files:**
- Modify: `.agents/skills/ds-problem-explain/scripts/mpe_source.py:170-185`
- Modify: `.agents/skills/ds-problem-explain/assets/note-template.html`
- Modify: `.agents/skills/ds-problem-explain/references/authoring.md`
- Modify: `.agents/skills/ds-problem-explain/assets/port-provenance.json`
- Test: `.agents/skills/ds-problem-explain/tests/test_source.py`

**Interfaces:**
- Consumes: `mpe_shared.parse(html_str) -> Node`, `mpe_shared.outer(node: Node) -> str`, `mpe_shared.Node`
- Produces:
  - `split_lecture_statement(statement_html: str, source: str) -> tuple[str, str]` in `mpe_source.py`
  - `load_source(path: Path, repo: Path) -> SourcePack` populating `Problem.conditions_html` and `Problem.ask_html` via `split_lecture_statement`

- [ ] **Step 1: Write the failing tests in `.agents/skills/ds-problem-explain/tests/test_source.py`**

```python
from mpe_source import split_lecture_statement

def test_split_lecture_statement_with_subparts():
    stmt = (
        '<p><span class="badge">강의 예제 기반 자체 출제</span> S4 p18</p>'
        '<p>단순 연결 리스트에서 <code>head = 300</code>이에요.</p>'
        '<pre><code class="language-c">300: [10 | 100] -&gt; 100: [20 | NULL]</code></pre>'
        '<ol><li>(a) 순회 순서를 쓰세요.</li><li>(b) 삽입 후 링크를 쓰세요.</li></ol>'
    )
    cond, ask = split_lecture_statement(stmt, 'lecture-s04-p18-linked-representation')
    assert cond == (
        '<p><span class="badge">강의 예제 기반 자체 출제</span> S4 p18</p>'
        '<p>단순 연결 리스트에서 <code>head = 300</code>이에요.</p>'
        '<pre><code class="language-c">300: [10 | 100] -&gt; 100: [20 | NULL]</code></pre>'
    )
    assert ask == '<ol><li>(a) 순회 순서를 쓰세요.</li><li>(b) 삽입 후 링크를 쓰세요.</li></ol>'
    assert subparts(ask, '') == ('a', 'b')

def test_non_lecture_ol_stays_in_conditions():
    stmt = '<p>다음 연산을 수행한다.</p><ol><li>(a) 첫째</li><li>(b) 둘째</li></ol>'
    cond, ask = split_lecture_statement(stmt, '2022-mid-q1')
    assert cond == stmt and ask == ''
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest .agents/skills/ds-problem-explain/tests/test_source.py -k "test_split_lecture_statement_with_subparts or test_non_lecture_ol_stays_in_conditions" -v`
Expected: FAIL with `ImportError: cannot import name 'split_lecture_statement' from 'mpe_source'`

- [ ] **Step 3: Implement `split_lecture_statement` in `.agents/skills/ds-problem-explain/scripts/mpe_source.py` and update `note-template.html`, `authoring.md`, and `port-provenance.json`**

In `mpe_source.py`:
- Import `outer` from `mpe_shared` (`from mpe_shared import HOMEWORK, REVIEW, Node, ReviewPdfError, read_cards, normalize_cards, outer, parse`).
- Define `split_lecture_statement(statement_html: str, source: str) -> tuple[str, str]`:
  ```python
  def split_lecture_statement(statement_html: str, source: str) -> tuple[str, str]:
      if not source.startswith('lecture-'):
          return statement_html, ''
      root = parse(statement_html)
      blocks = [c for c in root.children if isinstance(c, Node)]
      if len(blocks) >= 2 and blocks[-1].tag in ('ol', 'ul') and not choice_container(blocks[-1], root):
          return ''.join(outer(b) for b in blocks[:-1]), outer(blocks[-1])
      return statement_html, ''
  ```
- In `load_source`, replace lines 176–178 with:
  ```python
        problems = tuple(
            Problem(c.id, int(c.id[1:]), c.title, c.source, c.original_html,
                    *split_lecture_statement(c.statement_html, c.source), (), c.steps, c.answer_html,
                    subparts(c.statement_html, c.original_html))
            for c in pack.cards
        )
  ```
- In `.agents/skills/ds-problem-explain/assets/note-template.html`, add CSS rules inside the `.problem-pane` style block for `[data-source-field="conditions"]` and `[data-source-field="ask"]` spacing (`p + p`, `p + pre`, `pre + p`, `ol`, `li + li`).
- In `.agents/skills/ds-problem-explain/references/authoring.md`, document that `lecture-code` cards render conditions in `[data-source-field="conditions"]` and `(a)`/`(b)` sub-questions in `<h4>구할 것</h4><div data-source-field="ask">`, and that `understand` must be a concise 1–2 sentence summary rather than repeating the full problem text.
- Record the exact before/after SHA-256 and `replacements` for `scripts/mpe_source.py`, `assets/note-template.html`, `references/authoring.md`, and `tests/test_source.py` in `.agents/skills/ds-problem-explain/assets/port-provenance.json` (`local_overrides`).

- [ ] **Step 4: Run all `ds-problem-explain` tests to verify they pass**

Run: `python -m pytest .agents/skills/ds-problem-explain/tests -v`
Expected: All tests in `test_source.py`, `test_render.py`, `test_skill_files.py`, `test_sync.py` PASS.

- [ ] **Step 5: Commit**

```powershell
git add .agents/skills/ds-problem-explain/scripts/mpe_source.py .agents/skills/ds-problem-explain/assets/note-template.html .agents/skills/ds-problem-explain/references/authoring.md .agents/skills/ds-problem-explain/assets/port-provenance.json .agents/skills/ds-problem-explain/tests/test_source.py
git commit -m "feat(ds-problem-explain): split lecture-code conditions and asks in problem pane"
```

---

### Task 2: `ds-review-pack` PDF 분리기(`pdf_lecture.py`)의 구조화된 `<ol>` 질문 목록 지원 및 카드 규칙 문서화

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/pdf_lecture.py:50-65`
- Modify: `.agents/skills/ds-review-pack/references/card-rules.md`
- Test: `.agents/skills/ds-review-pack/tests/test_pdf_lecture.py`

**Interfaces:**
- Consumes: `pdf_types.Block`, `pdf_types.PdfError`
- Produces: `split_lecture_problem(blocks: tuple[Block, ...]) -> tuple[str, str]` in `pdf_lecture.py` supporting `[<p>조건...</p>, <ol><li>(a) 질문...</li></ol>]` by placing preceding `<p>` blocks into `cond` and the trailing `<ol>` block(s) into `ask` (with `<ol class="ds-asks">`), while preserving the single-list fallback `split_lecture_problem((badge, lst)) == ('', lst.html)`.

- [ ] **Step 1: Write the failing test in `.agents/skills/ds-review-pack/tests/test_pdf_lecture.py`**

```python
def test_structured_lecture_ol_split():
    badge = P('<p><span class="badge">강의 예제 기반 자체 출제</span> S4 p18</p>')
    cond_p = P('<p>단순 연결 리스트에서 <code>head = 300</code>이에요.</p>')
    asks_ol = P('<ol><li>(a) 방문 순서를 쓰세요.</li><li>(b) 삽입 후 링크를 쓰세요.</li></ol>')
    cond, ask = split_lecture_problem((badge, cond_p, asks_ol))
    assert cond == '<p>단순 연결 리스트에서 <code>head = 300</code>이에요.</p>'
    assert ask == '<ol class="ds-asks"><li>(a) 방문 순서를 쓰세요.</li><li>(b) 삽입 후 링크를 쓰세요.</li></ol>'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest .agents/skills/ds-review-pack/tests/test_pdf_lecture.py -k test_structured_lecture_ol_split -v`
Expected: FAIL because `split_lecture_problem` currently returns `('', '<p>단순 연결 리스트에서...</p><ol>...</ol>')` when any `<ol>` block is present.

- [ ] **Step 3: Implement structured `<ol>` splitting in `.agents/skills/ds-review-pack/scripts/pdf_lecture.py` and update `references/card-rules.md`**

In `pdf_lecture.py:56-57`, replace:
```python
    if any(re.match(r'\s*<[ou]l\b', b.html) for b in body):
        return caption, original
```
with:
```python
    if any(re.match(r'\s*<[ou]l\b', b.html) for b in body):
        pre = [b for b in body if not re.match(r'\s*<[ou]l\b', b.html)]
        lists = [b for b in body if re.match(r'\s*<[ou]l\b', b.html)]
        if not pre:
            return caption, original
        cond = caption + ''.join(b.html for b in pre)
        ask = ''.join(re.sub(r'^\s*<[ou]l\b[^>]*>', '<ol class="ds-asks">', re.sub(r'</[ou]l>\s*$', '</ol>', b.html)) for b in lists)
        assert_lossless(''.join(b.html for b in kept), cond + ask)
        return cond, ask
```
Also in `.agents/skills/ds-review-pack/references/card-rules.md`, add the formatting rule for `lecture-code` cards:
- 첫 문단은 `<p><span class="badge">강의 예제 기반 자체 출제</span> S<장> p<쪽></p>`로 쓰고 `추가 근거`는 `details.original` 안에만 적는다.
- 전제 조건(`<p>` 및 `<pre><code class="language-c">`)과 구할 것(`<ol><li>(a) …</li><li>(b) …</li></ol>`, 핵심 2~3문항)을 분리하고 모든 C 식별자·포인터 식·수치에 `<code>`를 쓴다.

- [ ] **Step 4: Run `test_pdf_lecture.py` and `test_skill_files.py` to verify they pass**

Run: `python -m pytest .agents/skills/ds-review-pack/tests/test_pdf_lecture.py .agents/skills/ds-review-pack/tests/test_skill_files.py -k "not long_card and not show_number_only" -v`
Expected: PASS

- [ ] **Step 5: Commit**

```powershell
git add .agents/skills/ds-review-pack/scripts/pdf_lecture.py .agents/skills/ds-review-pack/references/card-rules.md .agents/skills/ds-review-pack/tests/test_pdf_lecture.py
git commit -m "feat(review-pdf): preserve condition paragraphs when lecture-code cards use ol asks"
```

---

### Task 3: RUN 작업 공간 초기화 및 백업·baseline 생성

**Files:**
- Create: `tmp/lecture-readability-2026-10-18/backup/`, `tmp/lecture-readability-2026-10-18/baseline.json`, `tmp/lecture-readability-2026-10-18/<range>/cards/`

**Interfaces:**
- Consumes: `review_inventory.collect_reviews`, `update_review.extract_cards`
- Produces:
  - `tmp/lecture-readability-2026-10-18/baseline.json`
  - `tmp/lecture-readability-2026-10-18/<range>/cards/<id>.html` (all cards across 10 packs)
  - `tmp/lecture-readability-2026-10-18/<range>/manifest.json`
  - `tmp/lecture-readability-2026-10-18/<range>/fragments/<id>.html` (existing explanation fragments)

- [ ] **Step 1: Verify `tmp/` is git-ignored and initialize `$RUN` backup and extracted card workspaces**

Run:
```powershell
git check-ignore tmp/lecture-readability-2026-10-18
python -c "import sys, json, shutil; from pathlib import Path; sys.path.insert(0, '.agents/skills/ds-review-pack/scripts'); from review_inventory import collect_reviews; from update_review import extract_cards; repo = Path('.'); run = repo / 'tmp/lecture-readability-2026-10-18'; run.mkdir(parents=True, exist_ok=True); (run / 'baseline.json').write_text(json.dumps(collect_reviews(repo), ensure_ascii=False, indent=2), encoding='utf-8');
for mpath in sorted((repo / '복습노트').glob('*/.pack/자료_복습팩/manifest.json')):
    rng = mpath.parents[2].name
    rdir = run / rng
    (rdir / 'cards').mkdir(parents=True, exist_ok=True)
    (rdir / 'fragments').mkdir(parents=True, exist_ok=True)
    shutil.copy2(mpath, rdir / 'manifest.json')
    html_path = next(mpath.parents[2].glob('복습문제_*.html'))
    for c in extract_cards(html_path.read_text(encoding='utf-8')):
        (rdir / 'cards' / f\"{c['id']}.html\").write_text(c['raw'], encoding='utf-8')
    for fpath in sorted(mpath.parents[2].glob('.pack/자료_문제설명_*/fragments/*.html')):
        shutil.copy2(fpath, rdir / 'fragments' / fpath.name)
print('Initialized packs:', [p.name for p in sorted(run.iterdir()) if p.is_dir()])"
```
Expected: `tmp/lecture-readability-2026-10-18` printed by `git check-ignore`, and 10 pack directories (`0907`..`1015`) initialized with `cards/`, `fragments/`, and `manifest.json`.

---

### 공통 팩 개정 절차 R (Task 4–7 공통)

각 팩 Task는 대상 `lecture-code` 카드들에 대해 아래 **R1–R5**를 수행하고 검증한다:

- **R1 (`cards/<id>.html` 구조화·경량화)**:
  1. `.problem` 첫 문단은 `<p><span class="badge">강의 예제 기반 자체 출제</span> S<장> p<쪽></p>`로 대표 슬라이드만 표기하고, 기존 `· 추가 근거 p…`가 있으면 `details.original`의 첫 `<p>` 출처 문단 끝에 보존한다(단, `0907 p4`의 `<p><strong>후속 수업 보충:</strong> …</p>`는 그대로 유지).
  2. 전제 조건은 1~2문장의 `<p>`와 필요한 경우 `<pre><code class="language-c">…</code></pre>`(초기 노드 상태, 구조체 선언, 보조 함수 계약 등)로 분리한다.
  3. 질문은 핵심 학습 목표 2~3개의 `<ol><li>(a) …</li><li>(b) …</li></ol>`(최대 `(c)`)로 정돈한다. 모든 C 변수·필드·포인터 식·상수·복잡도에 `<code>`를 적용하고 붙여 쓴 한영/숫자(`주소300` → `주소 <code>300</code>`)를 교정한다.
  4. `.solution`의 `<ol>` 풀이 단계와 `<p class="answer">`도 소문항 `(a)`, `(b)`, `(c)`에 맞춰 `<code>` 서식으로 깔끔히 정리한다.
- **R2 (`manifest.json` 동기화)**:
  - `$RUN/<range>/manifest.json`에서 해당 문항의 `answer`를 수정된 `.answer`의 평문 텍스트와 일치시키고, 통합·축약된 질문에 맞춰 `objectives`를 갱신한다.
  - `terms` 배열의 모든 문자열이 수정된 카드 텍스트 안에 그대로 존재하는지 확인한다.
- **R3 (`fragments/<id>.html` 재작성)**:
  - `understand` (`문제를 내 말로 읽어요`): 문제 원문 복붙을 제거하고 1~2문장으로 핵심 상황과 목표만 요약한다.
  - `solve` (`단계별로 풀어요`) 및 `verify` (`답을 검산해요`): 새 소문항 표지(`('a', 'b')` 또는 `('a', 'b', 'c')`)에 맞춰 `<div data-subpart="a">…</div>`, `<div data-subpart="b">…</div>`를 각각 1회씩 작성한다. `solve` 끝에 `.answer` 줄글 전체를 중복 복사해 넣지 않는다.
  - `retry` 및 `sum[hidden]`에 이중 이스케이프(`&amp;lt;`)가 없도록 하고 코드 식에 `<code>`를 적용한다.
- **R4 (Stage 빌드 및 `check_pack` + `validate_fragment` 검증)**:
  - `update_review.build_revision`으로 `$RUN/<range>/stage/복습문제_<range>_<slug>.html`을 생성한다.
  - `check_html.check_pack` 결과가 `[]`인지 확인한다(`lecture-standalone`, `card-term`, `card-parts` 등 오류 0건).
  - 비대상 카드(`past-exam`, `textbook`)의 `extract_cards` `raw`가 원본 HTML과 바이트 단위로 동일한지 확인한다.
  - `mpe_source.load_source` + `mpe_contract.validate_fragment`로 해당 팩의 모든 `fragments/<id>.html`이 오류 `[]`이고, 모든 `lecture-code` 문항의 `p.ask_html`이 비어 있지 않으며 `p.subparts`가 `('a', 'b')` 또는 `('a', 'b', 'c')`인지 확인한다.

---

### Task 4: `0907` (`p4`–`p7`), `0914` (`p6`–`p8`), `0917` (`p5`–`p6`) 개정 (9문항)

**Files:**
- Modify: `tmp/lecture-readability-2026-10-18/{0907,0914,0917}/cards/p*.html`
- Modify: `tmp/lecture-readability-2026-10-18/{0907,0914,0917}/manifest.json`
- Modify: `tmp/lecture-readability-2026-10-18/{0907,0914,0917}/fragments/p*.html`

**Interfaces:**
- Consumes: Task 1–3 outputs
- Produces: Verified stage HTML, `manifest.json`, and explanation `fragments/*.html` for `0907`, `0914`, `0917`

- [ ] **Step 1: Apply R1–R3 to `0907` (`p4`, `p5`, `p6`, `p7`)**
  - `0907 p4` (`lecture-s01-p21-find-max`): `<p><strong>후속 수업 보충:</strong> …</p>` 유지. 조건 `<p>`에 입력 `score = {-8, -3, -10, -1}`, `n = 4` 제시. `<ol>` 소문항: `(a)` `tmp` 변화와 반환값, `(b)` `tmp = 0` 초기화 시 오류와 `n >= 1` 조건 및 유한 종료 이유.
  - `0907 p5` (`lecture-s01-p24-seq-search`): 조건 `<p>`에 `list = {3, 9, 5, 8, 2}`, `n = 5` 제시. `<ol>` 소문항: `(a)` `key = 8`과 `key = 7`일 때 비교 횟수 및 반환값, `(b)` 최선·최악 비교 횟수와 빅오 표기.
  - `0907 p6` (`lecture-s01-p30-cal-time`): 조건 `<p>`에 `start = 1500`, `stop = 4200`, `CLOCKS_PER_SEC = 1000` 제시. `<ol>` 소문항: `(a)` `duration` 값과 `(double)` 형변환을 생략할 때의 결과 차이, `(b)` `time()` 대신 `clock()`을 쓰는 이유.
  - `0907 p7` (`lecture-s01-p38-39-bitmatrix-steps`): 조건 `<p>`에 `n = 8`, 최고값 행이 `5`행(`0`부터 시작)임을 제시. `<ol>` 소문항: `(a)` 알고리즘 1과 알고리즘 2의 `1` 진입·유지·탈출 이동 횟수 비교, `(b)` 전체 최악 실행시간을 $O(n)$으로 판단하는 근거.

- [ ] **Step 2: Apply R1–R3 to `0914` (`p6`, `p7`, `p8`) and `0917` (`p5`, `p6`)**
  - `0914 p6` (`lecture-s01-p34-37-type-ab-ops`): 조건 `<p>`에 `n = 5`와 연산 규칙 제시. `<ol>` 소문항: `(a)` Type A와 Type B의 대입·덧셈·곱셈 횟수 및 총 연산 횟수 $T(n)$, `(b)` 두 알고리즘의 빅오 복잡도와 증가율 비교.
  - `0914 p7` (`lecture-s01-p41-big-o`): 조건 `<p>`에 $T(n) = 2n^2 + 3n + 1$ 제시. `<ol>` 소문항: `(a)` $c = 6, n_0 = 1$로 $T(n) \le c n^2$ 성립 확인 및 $O(n^2)$ 판정, `(b)` $T(n) \in O(n)$이 성립하지 않는 이유와 최소 상한 차수 선택 원칙.
  - `0914 p8` (`lecture-s02-p06-factorial-print`): 조건 `<p>`에 `factorial(3)` 호출 제시. `<ol>` 소문항: `(a)` 호출 순서대로 출력되는 줄과 반환값 추적, `(b)` `if (n <= 1)` 기저 조건이 없을 때 발생하는 현상.
  - `0917 p5` (`lecture-s02-p15-power`): 조건 `<p>`에 `slow_power(2, 6)`과 `power(2, 6)` 제시. `<ol>` 소문항: `(a)` `power(2, 6)`의 재귀 호출 사슬과 각 단계 반환값, `(b)` 두 함수의 곱셈 횟수 및 시간 복잡도($O(n)$ vs $O(\log_2 n)$) 비교.
  - `0917 p6` (`lecture-s02-p19-20-fib`): 조건 `<p>`에 `fib(5)`와 `fib_iter(5)` 제시. `<ol>` 소문항: `(a)` `fib(5)`에서 `fib(2)`·`fib(1)`·`fib(0)` 호출 횟수와 중복 계산 원인, `(b)` `fib_iter(5)`의 단계별 `(pp, p, result)` 변화와 시간 복잡도 비교.

- [ ] **Step 3: Run R4 verification on `0907`, `0914`, `0917`**

Run:
```powershell
python -c "import sys, json; from pathlib import Path; sys.path.insert(0, '.agents/skills/ds-review-pack/scripts'); sys.path.insert(0, '.agents/skills/ds-problem-explain/scripts'); from update_review import build_revision, extract_cards; from check_html import check_pack; from mpe_source import load_source; from mpe_contract import validate_fragment
repo = Path('.'); run = repo / 'tmp/lecture-readability-2026-10-18'
for rng in ('0907', '0914', '0917'):
    rdir = run / rng; m = json.loads((rdir / 'manifest.json').read_text(encoding='utf-8'))
    orig_html = next((repo / '복습노트' / rng).glob('복습문제_*.html'))
    note_html = next((repo / '복습노트' / rng).glob('정리노트_*.html'))
    cards = {p.stem: p.read_text(encoding='utf-8') for p in (rdir / 'cards').glob('*.html')}
    staged = build_revision(orig_html.read_text(encoding='utf-8'), manifest=m, cards=cards)
    sdir = rdir / 'stage'; sdir.mkdir(exist_ok=True); spath = sdir / orig_html.name; spath.write_text(staged, encoding='utf-8')
    errs = check_pack(m, note_html, spath)
    assert errs == [], (rng, errs)
    pack = load_source(spath, repo)
    for p in pack.problems:
        frag = (rdir / 'fragments' / f'{p.id}.html').read_text(encoding='utf-8')
        ferrs = validate_fragment(p, frag)
        assert ferrs == [], (rng, p.id, ferrs)
        if p.source.startswith('lecture-'):
            assert p.ask_html and p.subparts != ('main',), (rng, p.id, p.subparts)
print('0907, 0914, 0917 verified OK')"
```
Expected: `0907, 0914, 0917 verified OK`

---

### Task 5: `0921` (`p5`–`p11`), `0928` (`p5`–`p9`) 개정 (12문항)

**Files:**
- Modify: `tmp/lecture-readability-2026-10-18/{0921,0928}/cards/p*.html`
- Modify: `tmp/lecture-readability-2026-10-18/{0921,0928}/manifest.json`
- Modify: `tmp/lecture-readability-2026-10-18/{0921,0928}/fragments/p*.html`

**Interfaces:**
- Consumes: Task 1–3 outputs
- Produces: Verified stage HTML, `manifest.json`, and explanation `fragments/*.html` for `0921`, `0928`

- [ ] **Step 1: Apply R1–R3 to `0921` (`p5`–`p11`)**
  - `0921 p5` (`lecture-s03-p16-18-matrix-transpose1`): `(a)` `B[c][r] = A[r][c]` 복사로 만들어지는 전치행렬 `B`의 3행 및 대각 원소, `(b)` 이중 루프 대입 횟수와 시간 복잡도.
  - `0921 p6` (`lecture-s03-p19-22-sparse-transpose2`): `(a)` `bindex`가 증가하는 `(c, i)` 순서에 따른 전치 결과 `b.data[0..3]`의 `(row, col, value)` 표, `(b)` `a.data`가 열 기준 정렬이 아닐 때 `c` 바깥 루프가 열 오름차순(행 주순서)을 보장하는 원리와 시간 복잡도 $O(\text{cols} \times \text{terms})$.
  - `0921 p7` (`lecture-s03-p08-11-poly-add1`): 조건에 `degree`와 `coef[i]`($x^{\text{degree}-i}$의 계수) 규칙 명시. `(a)` 초기 `C.degree`, `Cpos`와 차수 비교 분기에 따른 단계별 `C.coef` 채움 결과, `(b)` 최고차항이 상쇄되는 두 다항식 덧셈에서 `C.degree`가 실제 최고차항과 달라지는 이유.
  - `0921 p8` (`lecture-s02-p23-26-hanoi`): `(a)` `hanoi_tower(3, 'A', 'B', 'C')`의 7줄 출력 순서, `(b)` 총 이동 횟수 일반식 $2^n - 1$과 기저 조건(`n == 1`)의 역할.
  - `0921 p9` (`lecture-s03-p04-array-adt`): `(a)` `create(5)` 직후 `set(A, 5, 10)`과 `get(A, -1)`이 범위 오류인 이유, `(b)` 1차원 배열 시작 주소 `base`와 `sizeof(Element)`로 인덱스 `i`의 주소를 $O(1)$에 계산하는 식.
  - `0921 p10` (`lecture-s03-p07-15-poly-representations`): 1,374자 줄글을 대폭 경량화. 조건 문단 + `poly_add1`/`poly_add2` 핵심 비교 루프 `<pre><code>` 제시. `(a)` $P(x) = 10x^{1000} + 2$에서 두 표현 방식(방식 1: 전 차수 계수 배열, 방식 2: `(coef, expon)` 항 배열)의 저장 공간 효율 비교, `(b)` $A(x) = 2x^3 + 4x$, $B(x) = 3x^3 + 5$일 때 방식 2의 `switch (compare(...))` 비교 단계별 `(coef, expon)` 결과와 최고차항 상쇄(`3x^3`과 `-3x^3`) 처리 차이.
  - `0921 p11` (`lecture-s03-p24-27-struct-typedef`): `struct person` 선언을 `<pre><code class="language-c">`로 분리. `(a)` `struct person a;`와 `typedef` 별칭 `person b;` 선언 차이 및 점 연산자(`a.age = 20`) 멤버 접근, `(b)` 구조체 대입 `b = a;`와 비교 연산 `if (a == b)`의 C 문법 허용 여부와 동등 비교 방법.

- [ ] **Step 2: Apply R1–R3 to `0928` (`p5`–`p9`)**
  - `0928 p5` (`lecture-s03-p32-swap-pointers`): `(a)` 호출 전후 `a`, `b`, `*px`, `*py` 값과 `main`의 `a`, `b`가 바뀌는 이유, `(b)` 값에 의한 호출 `swap_val(int x, int y)`로 작성했을 때 `main`의 `a`, `b`가 바뀌지 않는 이유.
  - `0928 p6` (`lecture-s03-p33-34-array-param-malloc`): `(a)` `get_integers(list)` 호출 후 `list[0..5]` 값과 `cal_sum(list)` 반환값(배열 매개변수가 첫 원소 포인터 `int *`로 전달되는 원리), `(b)` `int *p = (int *)malloc(sizeof(int) * 6);` 동적 할당 시 반환값(`NULL`) 확인과 `free(p)` 시점.
  - `0928 p7` (`lecture-s03-p29-31-pointer-null`): `(a)` `p = &a; *p = 200;` 실행 후 `a`의 값과 역참조 연산자 `*p`의 의미, `(b)` `p = NULL;` 후 `if (p != NULL)` 검사를 거치는 이유와 널 포인터 역참조 시 발생하는 문제.
  - `0928 p8` (`lecture-s03-p35-struct-pointer-malloc`): `(a)` `sizeof(student)`의 하한 크기(`10 + 4 + 8 = 22`바이트 이상)와 패딩을 가정하지 않고 `sizeof(student)`를 쓰는 이유, `(b)` `s->age = 20`과 동치인 역참조 표기 `(*s).age` 및 `strcpy(s->name, "Park")` 실행 후 멤버 값과 `free(s)` 필요성.
  - `0928 p9` (`lecture-s03-p26-35-struct-layout-offset`): `struct AlignDepends` 선언을 `<pre><code class="language-c">`로 제시. `(a)` 4바이트 정렬 환경에서 `c`, `i`, `d`의 오프셋(`0`, `4`, `8`)과 전체 크기(`16`바이트) 및 패딩 위치, `(b)` 멤버를 `(double d, int i, char c)` 순으로 재배치했을 때 오프셋과 전체 크기가 `16`바이트가 되는 이유.

- [ ] **Step 3: Run R4 verification on `0921` and `0928`**

Run:
```powershell
python -c "import sys, json; from pathlib import Path; sys.path.insert(0, '.agents/skills/ds-review-pack/scripts'); sys.path.insert(0, '.agents/skills/ds-problem-explain/scripts'); from update_review import build_revision; from check_html import check_pack; from mpe_source import load_source; from mpe_contract import validate_fragment
repo = Path('.'); run = repo / 'tmp/lecture-readability-2026-10-18'
for rng in ('0921', '0928'):
    rdir = run / rng; m = json.loads((rdir / 'manifest.json').read_text(encoding='utf-8'))
    orig_html = next((repo / '복습노트' / rng).glob('복습문제_*.html'))
    note_html = next((repo / '복습노트' / rng).glob('정리노트_*.html'))
    cards = {p.stem: p.read_text(encoding='utf-8') for p in (rdir / 'cards').glob('*.html')}
    staged = build_revision(orig_html.read_text(encoding='utf-8'), manifest=m, cards=cards)
    sdir = rdir / 'stage'; sdir.mkdir(exist_ok=True); spath = sdir / orig_html.name; spath.write_text(staged, encoding='utf-8')
    errs = check_pack(m, note_html, spath)
    assert errs == [], (rng, errs)
    pack = load_source(spath, repo)
    for p in pack.problems:
        frag = (rdir / 'fragments' / f'{p.id}.html').read_text(encoding='utf-8')
        ferrs = validate_fragment(p, frag)
        assert ferrs == [], (rng, p.id, ferrs)
        if p.source.startswith('lecture-'):
            assert p.ask_html and p.subparts != ('main',), (rng, p.id, p.subparts)
print('0921, 0928 verified OK')"
```
Expected: `0921, 0928 verified OK`

---

### Task 6: `1001` (`p1`–`p5`), `1005` (`p3`–`p11`) 개정 (14문항)

**Files:**
- Modify: `tmp/lecture-readability-2026-10-18/{1001,1005}/cards/p*.html`
- Modify: `tmp/lecture-readability-2026-10-18/{1001,1005}/manifest.json`
- Modify: `tmp/lecture-readability-2026-10-18/{1001,1005}/fragments/p*.html`

**Interfaces:**
- Consumes: Task 1–3 outputs
- Produces: Verified stage HTML, `manifest.json`, and explanation `fragments/*.html` for `1001`, `1005`

- [ ] **Step 1: Apply R1–R3 to `1001` (`p1`–`p5`)**
  - `1001 p1` (`lecture-s04-p11-array-list-add`): `(a)` `add(&L, 1, 25)` 실행 시 `i`의 변화 순서와 원소 이동 대입식 및 최종 `list[0..4]`·`length`, `(b)` 최선(끝 삽입)과 최악(맨 앞 삽입)의 원소 이동 횟수 및 시간 복잡도.
  - `1001 p2` (`lecture-s04-p12-array-list-delete`): `(a)` `delete(&L, 1)` 실행 시 반환값 `item`, `i`의 이동 대입식, 최종 `list[0..2]`·`length`, `(b)` `add`는 뒤에서 앞으로(`i--`), `delete`는 앞에서 뒤로(`i++`) 복사 방향이 반대인 이유.
  - `1001 p3` (`lecture-s04-p05-06-list-adt-trace`): 연산 계약(`add_tail`, `add`, `delete`, `replace`, `get_entry`, `get_length`)을 조건 `<pre><code>`로 간결히 제시. `(a)` 5단계 연산을 순서대로 실행했을 때 단계별 리스트 상태와 `length`, `(b)` 최종 상태에서 `get_entry(1)`, `get_length()` 반환값 및 `delete(0)` 추가 실행 시 앞으로 당겨지는 원소 개수.
  - `1001 p4` (`lecture-s04-p08-10-arraylist-init-predicates`): `(a)` `init(&L)` 직후 `length`, `is_empty(&L)`, `is_full(&L)` 값과 `length == 3`일 때의 반환값 및 `get_entry(&L, 2)`·`get_entry(&L, 3)` 결과, `(b)` `main`에서 구조체 값(`ArrayListType L`)이 아닌 주소(`&L`)를 넘기는 이유.
  - `1001 p5` (`lecture-s04-p18-linked-representation`): 사용자가 제보한 대표 문항. 초기 메모리 상태를 조건 `<pre><code>`(`head = 300`, `300:[data=10|link=100] -> 100:[data=20|link=400] -> 400:[data=30|link=200] -> 200:[data=40|link=NULL]`, `p = 100`)로 깔끔히 제시. `<ol>` 소문항: `(a)` `head`부터 `NULL`까지 방문하는 `(주소, data)` 순서와 배열 리스트 대비 연결 표현의 장단점, `(b)` 주소 `500`(`data = 25`)인 새 노드 `new_node`를 `p`(`100`) 뒤에 삽입할 때 바꿀 링크와, 초기 상태에서 노드 `400`을 삭제할 때 바꿀 링크.

- [ ] **Step 2: Apply R1–R3 to `1005` (`p3`–`p11`)**
  - `1005 p3` (`lecture-s04-p27-insert-node`): `(a)` `[10] -> [20] -> [30]`에서 `p`가 `10`을 가리킬 때 `insert_node`의 두 링크 대입 후 체인 상태, `(b)` 두 대입 순서를 바꾸면 뒷부분 노드를 잃어버리는 이유와 `ListNode **phead` 이중 포인터를 쓰는 이유.
  - `1005 p4` (`lecture-s04-p28-remove-node`): `(a)` `[10] -> [20] -> [30]`에서 `p`가 `10`, `removed`가 `20`일 때 `remove_node` 실행 후 체인과 해제 대상 노드, `(b)` `p == NULL`(맨 앞 삭제) 분기가 따로 필요한 이유와 단일 포인터로 삭제할 수 없는 이유.
  - `1005 p5` (`lecture-s04-p29-32-display-search-concat`): `(a)` `A = [10 -> 20]`, `B = [30 -> 40]`에서 `display(A)`, `search(A, 20)` 결과와 `concat(A, B)`의 `p` 이동 과정 및 결과 체인, `(b)` `A == NULL`일 때 `concat(A, B)`의 처리와 시간 복잡도 $O(|A|)$.
  - `1005 p6` (`lecture-s04-p33-reverse`): `(a)` `[10] -> [20] -> [30]`에서 루프 1~3회차 종료 시점마다 `(r, q, p)`가 가리키는 노드와 `q->link` 방향 표, `(b)` 루프 안에서 `q = p; p = p->link;` 전에 `q->link = r;`를 먼저 실행하면 안 되는 이유.
  - `1005 p7` (`lecture-s04-p37-circular-insert-last`): `(a)` 원형 리스트에서 `head`가 마지막 노드(`20`, `20->link == 10`)를 가리킬 때 `insert_last(&head, node(30))` 실행 후 각 노드의 `link`와 `head`, `(b)` `head`가 첫 노드가 아닌 마지막 노드를 가리키게 설계할 때 맨 앞(`insert_first`)·맨 뒤(`insert_last`) 삽입이 모두 $O(1)$이 되는 이유.
  - `1005 p8` (`lecture-s04-p41-42-dinsert-node`): `(a)` 헤드 노드 `H`와 `A`(`H <-> A <-> H`) 사이(`before = H`)에 새 노드 `N`을 넣는 `dinsert_node` 4개 대입 단계별 포인터 값과 결과 체인, `(b)` `before->rlink = new_node;`를 첫 줄에 먼저 실행하면 원래 첫 노드 `A`의 `llink`를 갱신하지 못하는 이유.
  - `1005 p9` (`lecture-s04-p20-25-node-alloc-chain`): `(a)` `p1`(`10`), `p2`(`20`) 동적 생성 및 연결 후 표현식 `p1->data`, `p1->link->data`, `p1->link->link`의 값, `(b)` `p1`과 `p2`를 해제할 때 `free(p1)`을 먼저 호출하면 생기는 문제와 올바른 `free` 순서.
  - `1005 p10` (`lecture-s04-p26-44-list-Pointer-cases`): 조건 문단과 보조 계약을 간결히 정리. `(a)` 단순 연결 리스트 `[10] -> [20]`에서 `p == NULL`로 `5`를 맨 앞에 삽입한 뒤, `p`가 `10`을 가리킬 때 `20`을 삭제하는 과정의 `head` 및 `link` 변화, `(b)` 원형 연결 리스트에서 `insert_first(&head, node(10))` 후 `insert_first(&head, node(5))` 실행 시 `head`·`link` 상태와, 이중 연결 리스트 `[H <-> 10 <-> 20 <-> H]`에서 `removed = node(10)` 삭제 후 링크 상태.
  - `1005 p11` (`lecture-s04-p45-53-list-adt-wrappers`): `(a)` 공백 리스트에서 `add_first(10)`, `add_last(30)`, `add(1, 20)` 순서로 호출할 때 내부 `get_node_at` 반환 포인터와 `insert_node`에 전달되는 `p` 및 리스트 변화, `(b)` `delete(1)` 실행 후 `get_entry(1)` 값과 `clear(&list)`에서 `p->link`를 먼저 읽지 않고 `free(p)`를 하면 안 되는 이유.

- [ ] **Step 3: Run R4 verification on `1001` and `1005`**

Run:
```powershell
python -c "import sys, json; from pathlib import Path; sys.path.insert(0, '.agents/skills/ds-review-pack/scripts'); sys.path.insert(0, '.agents/skills/ds-problem-explain/scripts'); from update_review import build_revision; from check_html import check_pack; from mpe_source import load_source; from mpe_contract import validate_fragment
repo = Path('.'); run = repo / 'tmp/lecture-readability-2026-10-18'
for rng in ('1001', '1005'):
    rdir = run / rng; m = json.loads((rdir / 'manifest.json').read_text(encoding='utf-8'))
    orig_html = next((repo / '복습노트' / rng).glob('복습문제_*.html'))
    note_html = next((repo / '복습노트' / rng).glob('정리노트_*.html'))
    cards = {p.stem: p.read_text(encoding='utf-8') for p in (rdir / 'cards').glob('*.html')}
    staged = build_revision(orig_html.read_text(encoding='utf-8'), manifest=m, cards=cards)
    sdir = rdir / 'stage'; sdir.mkdir(exist_ok=True); spath = sdir / orig_html.name; spath.write_text(staged, encoding='utf-8')
    errs = check_pack(m, note_html, spath)
    assert errs == [], (rng, errs)
    pack = load_source(spath, repo)
    for p in pack.problems:
        frag = (rdir / 'fragments' / f'{p.id}.html').read_text(encoding='utf-8')
        ferrs = validate_fragment(p, frag)
        assert ferrs == [], (rng, p.id, ferrs)
        if p.source.startswith('lecture-'):
            assert p.ask_html and p.subparts != ('main',), (rng, p.id, p.subparts)
print('1001, 1005 verified OK')"
```
Expected: `1001, 1005 verified OK`

---

### Task 7: `1008` (`p2`–`p5`), `1012` (`p7`–`p9`), `1015` (`p4`–`p8`) 개정 (12문항)

**Files:**
- Modify: `tmp/lecture-readability-2026-10-18/{1008,1012,1015}/cards/p*.html`
- Modify: `tmp/lecture-readability-2026-10-18/{1008,1012,1015}/manifest.json`
- Modify: `tmp/lecture-readability-2026-10-18/{1008,1012,1015}/fragments/p*.html`

**Interfaces:**
- Consumes: Task 1–3 outputs
- Produces: Verified stage HTML, `manifest.json`, and explanation `fragments/*.html` for `1008`, `1012`, `1015`

- [ ] **Step 1: Apply R1–R3 to `1008` (`p2`–`p5`), `1012` (`p7`–`p9`), `1015` (`p4`–`p8`)**
  - `1008 p2` (`lecture-s04-p48-list-delete-pos0-bug`): `remove_node` 코드와 `get_node_at` 계약을 조건에 유지. `(a)` `pos == 0`과 `pos == 2`일 때 `tmp_node` 값과 `remove_node`의 실제 삭제 대상 노드 비교(`pos == 0`에서 두 번째 노드 `20`이 잘못 삭제되는 결함), `(b)` `pos == 0`일 때 `remove_node(&(list->head), NULL, list->head)`가 호출되도록 고치는 방법.
  - `1008 p3` (`lecture-s05-p08-10-array-stack-ops`): `(a)` `MAX_STACK_SIZE = 3`, `top = -1`에서 `push(10)`, `push(20)`, `peek()`, `pop()`, `push(30)`, `push(40)` 실행 시 단계별 `top`과 `stack[]` 상태, `(b)` 이어서 `push(50)` 호출 시 `is_full()` 판정과 `pop()`에서 배열 원소를 지우지 않고 `top--`만 해도 되는 이유.
  - `1008 p4` (`lecture-s04-p49-50-list-add-get-pos0`): `insert_node` 코드와 `get_node_at` 계약을 조건에 유지. `(a)` `[10] -> [20] -> [30]`(`length = 3`)에서 `add(&list, 0, 5)` 호출 시 `p = get_node_at(list, -1)` 반환값(`NULL`)과 `insert_node`의 맨 앞 삽입 동작, `(b)` 같은 리스트에서 `get_entry(&list, 0)`과 `get_entry(&list, 2)`가 반환하는 값.
  - `1008 p5` (`lecture-s05-p03-07-stack-adt-lifo`): `(a)` 빈 스택에 `A`, `B`, `C`를 차례로 `push`한 뒤 `pop` 3회 실행 시 반환 순서와 함수 호출 스택 프레임(`main -> B -> A`) 복귀 순서, `(b)` 공백 스택(`top == -1`)에서 `pop`/`peek`을 호출하거나 포화 스택에서 `push`할 때 발생하는 오류 조건.
  - `1012 p7` (`lecture-s05-p12-14-struct-stack`): `(a)` `init(&s)` 후 `push(&s, {1, "Kim"})`, `push(&s, {2, "Lee"})`, `pop(&s)` 실행 시 단계별 `s.top`과 반환 구조체, `(b)` 전역 배열 대신 `StackType s` 구조체 포인터(`&s`)를 전달할 때 다중 스택 운용상의 장점.
  - `1012 p8` (`lecture-s05-p16-19-linked-stack`): `(a)` `s->top = NULL`에서 `push(&s, 10)`, `push(&s, 20)` 후 `pop(&s)` 실행 시 `temp->link`, `s->top` 변화와 `free(temp)` 전에 `item`과 `s->top`을 먼저 갱신해야 하는 이유, `(b)` 연결된 스택에서 `is_empty` 조건(`s->top == NULL`)과 `is_full`이 동적 메모리 고갈 외에는 `0`인 이유.
  - `1012 p9` (`lecture-s05-p28-31-postfix-eval`): `(a)` 후위 표기식 `"82/3-32*+"`를 `eval`로 계산할 때 문자별 스택 변화와 최종 반환값 `7` (`op2 = pop()`, `op1 = pop()` 순서가 나눗셈·뺄셈에서 중요한 이유 포함), `(b)` 중위 표기식 `(8 / 2 - 3) + 3 * 2`를 후위 표기식으로 변환할 때 연산자 스택의 변화.
  - `1015 p4` (`lecture-s06-p05-08-linear-queue`): `(a)` `MAX_QUEUE_SIZE = 5`, `front = -1, rear = -1`인 선형 큐에서 `enqueue(10)`, `enqueue(20)`, `dequeue()`, `enqueue(30)` 실행 후 `(front, rear)`와 배열 상태, `(b)` `front = 2, rear = 4`에서 앞 칸(`0..2`)이 비어 있는데도 `is_full()`이 참이 되는 가짜 포화(false full) 문제와 해결책.
  - `1015 p5` (`lecture-s06-p22-25-bank-simulation`): `(a)` `duration = 3`, `clock = 1, 2, 3`에서 도착 고객(`id=0, t=1, s=2` / `id=1, t=2, s=1`)에 대한 시각별 큐 상태, 서비스 시작 시각, 대기 시간 및 누적 `waited_time`, `(b)` 서비스 중인 고객이 있는 동안(`service_time > 0`) 도착한 고객을 큐에 대기시키는 조건 분기.
  - `1015 p6` (`lecture-s06-p09-13-circular-queue-array`): `(a)` `MAX_QUEUE_SIZE = 4`, `front = 0, rear = 0`인 원형 큐에서 `enqueue(10)`, `enqueue(20)`, `enqueue(30)` 후 `is_full` 판정과 `dequeue()`, `enqueue(40)` 실행 시 `(front, rear)` 변화, `(b)` 원형 큐에서 한 칸을 비워 두어 공백(`front == rear`)과 포화(`front == (rear + 1) % MAX_QUEUE_SIZE`)를 구별하는 이유.
  - `1015 p7` (`lecture-s06-p16-19-linked-queue`): `(a)` `front = NULL, rear = NULL`인 연결 큐에서 `enqueue(10)`, `enqueue(20)` 실행 시 공백 삽입과 비공백 삽입의 포인터 갱신 차이, `(b)` 이어서 `dequeue()`를 두 번 호출해 마지막 노드를 꺼낼 때 `q->front == NULL`이면 `q->rear = NULL`까지 함께 갱신해야 하는 이유.
  - `1015 p8` (`lecture-s06-p20-21-deque-adt`): `(a)` 공백 덱에서 `add_front(10)`, `add_rear(20)`, `add_front(5)`, `delete_rear()`, `delete_front()`를 순서대로 실행했을 때 단계별 덱 상태와 반환값, `(b)` 덱 연산만으로 스택(LIFO)과 큐(FIFO)를 각각 구현하는 연산 대응 관계, 그리고 원형 배열 덱에서 `delete_rear`/`add_front` 시 반시계 방향 인덱스 식 `(idx - 1 + MAX) % MAX`를 쓰는 이유.

- [ ] **Step 2: Run R4 verification on `1008`, `1012`, `1015`**

Run:
```powershell
python -c "import sys, json; from pathlib import Path; sys.path.insert(0, '.agents/skills/ds-review-pack/scripts'); sys.path.insert(0, '.agents/skills/ds-problem-explain/scripts'); from update_review import build_revision; from check_html import check_pack; from mpe_source import load_source; from mpe_contract import validate_fragment
repo = Path('.'); run = repo / 'tmp/lecture-readability-2026-10-18'
for rng in ('1008', '1012', '1015'):
    rdir = run / rng; m = json.loads((rdir / 'manifest.json').read_text(encoding='utf-8'))
    orig_html = next((repo / '복습노트' / rng).glob('복습문제_*.html'))
    note_html = next((repo / '복습노트' / rng).glob('정리노트_*.html'))
    cards = {p.stem: p.read_text(encoding='utf-8') for p in (rdir / 'cards').glob('*.html')}
    staged = build_revision(orig_html.read_text(encoding='utf-8'), manifest=m, cards=cards)
    sdir = rdir / 'stage'; sdir.mkdir(exist_ok=True); spath = sdir / orig_html.name; spath.write_text(staged, encoding='utf-8')
    errs = check_pack(m, note_html, spath)
    assert errs == [], (rng, errs)
    pack = load_source(spath, repo)
    for p in pack.problems:
        frag = (rdir / 'fragments' / f'{p.id}.html').read_text(encoding='utf-8')
        ferrs = validate_fragment(p, frag)
        assert ferrs == [], (rng, p.id, ferrs)
        if p.source.startswith('lecture-'):
            assert p.ask_html and p.subparts != ('main',), (rng, p.id, p.subparts)
print('1008, 1012, 1015 verified OK')"
```
Expected: `1008, 1012, 1015 verified OK`

---

### Task 8: 10개 팩 전체 `review_audit` 검증, `복습문제_*.html`·`.md` 발행 및 `test_pdf_lecture.py` 동기화

**Files:**
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/복습문제_*.html`
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/.pack/복습문제_*.md`
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/.pack/자료_복습팩/{manifest,validation}.json`
- Modify: `.agents/skills/ds-review-pack/tests/test_pdf_lecture.py`

**Interfaces:**
- Consumes: Task 4–7 stage outputs in `tmp/lecture-readability-2026-10-18/<range>/stage/`
- Produces: Published `복습문제_*.html`, `.pack/복습문제_*.md`, `.pack/자료_복습팩/manifest.json`, `.pack/자료_복습팩/validation.json`, and passing `test_lecture_html.py`, `test_pdf_lecture.py`, `test_review_delivery.py`

- [ ] **Step 1: Run `review_audit.py` across all 10 staged packs**

Run:
```powershell
python -c "import json; from pathlib import Path; run = Path('tmp/lecture-readability-2026-10-18'); overlay = {p.name: {'review_path': str(next((p / 'stage').glob('복습문제_*.html')).resolve()), 'manifest_path': str((p / 'manifest.json').resolve())} for p in sorted(run.iterdir()) if p.is_dir() and (p / 'stage').is_dir()}; (run / 'overlay.json').write_text(json.dumps(overlay, ensure_ascii=False, indent=2), encoding='utf-8')"
python .agents/skills/ds-review-pack/scripts/review_audit.py --repo . --overlay tmp/lecture-readability-2026-10-18/overlay.json --baseline tmp/lecture-readability-2026-10-18/baseline.json --out tmp/lecture-readability-2026-10-18/audit.json
```
Expected: `pass 0 blocking 0 candidates`

- [ ] **Step 2: Publish `복습문제_*.html`, `manifest.json`, `validation.json` via `publish_update` and regenerate `.pack/복습문제_*.md` via `html2md.py`**

Run:
```powershell
python -c "import sys, json, hashlib; from pathlib import Path; sys.path.insert(0, '.agents/skills/ds-review-pack/scripts'); from update_review import publish_update; repo = Path('.'); run = repo / 'tmp/lecture-readability-2026-10-18'
for rng in ('0907','0914','0917','0921','0928','1001','1005','1008','1012','1015'):
    rdir = run / rng
    pack_dir = repo / '복습노트' / rng
    rev_path = next(pack_dir.glob('복습문제_*.html'))
    man_path = pack_dir / '.pack/자료_복습팩/manifest.json'
    val_path = pack_dir / '.pack/자료_복습팩/validation.json'
    staged_bytes = (rdir / 'stage' / rev_path.name).read_bytes()
    man_bytes = (rdir / 'manifest.json').read_bytes()
    val = json.loads(val_path.read_text(encoding='utf-8'))
    val['lecture_readability_2026_10_18'] = {
        'before_review_sha256': hashlib.sha256(rev_path.read_bytes()).hexdigest(),
        'after_review_sha256': hashlib.sha256(staged_bytes).hexdigest(),
        'before_manifest_sha256': hashlib.sha256(man_path.read_bytes()).hexdigest(),
        'after_manifest_sha256': hashlib.sha256(man_bytes).hexdigest(),
        'status': 'pass'
    }
    val_bytes = (json.dumps(val, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    publish_update({rev_path: staged_bytes, man_path: man_bytes, val_path: val_bytes}, backup=run / 'publish-backup' / rng)
print('Published all 10 review packs')"
```
Then regenerate `.pack/복습문제_*.md` for all 10 packs using `html2md.py` and verify that `정리노트_*.md` hashes are untouched.

- [ ] **Step 3: Update `test_pdf_lecture.py` assertions for `1015 p5` and `1001 p5` paragraph/subpart counts and run tests**

In `.agents/skills/ds-review-pack/tests/test_pdf_lecture.py`, update `test_1015_p5_split`, `test_trailing_parenthetical_is_ask`, and `test_lecture_payload_uses_conditions` so the expected `<p>` count in `cond` and `<li>` count in `ask` match the newly structured `1015 p5` and `1001 p5` cards (while keeping an inline unit test `P('<p>상황이에요. 결과를 설명하세요(링크 변경만 묻습니다).</p>')` in `test_trailing_parenthetical_is_ask` so the trailing parenthetical regex remains directly tested).

Run: `python -m pytest .agents/skills/ds-review-pack/tests/test_lecture_html.py .agents/skills/ds-review-pack/tests/test_pdf_lecture.py .agents/skills/ds-review-pack/tests/test_review_delivery.py -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```powershell
git add 복습노트/*/복습문제_*.html 복습노트/*/.pack/복습문제_*.md 복습노트/*/.pack/자료_복습팩/manifest.json 복습노트/*/.pack/자료_복습팩/validation.json .agents/skills/ds-review-pack/tests/test_pdf_lecture.py
git commit -m "fix(review): structure and condense lecture-code problems across 10 packs"
```

---

### Task 9: 10개 복습팩 `문제설명_*.html`·`.md` 및 `복습문제_*-{문제,답안}.pdf` 재생성·검증·발행

**Files:**
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/문제설명_*.html`
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/.pack/문제설명_*.md`
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/.pack/자료_문제설명_*/{manifest.json,validation.json,fragments/*.html}`
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/복습문제_*-{문제,답안}.pdf`
- Modify: `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/.pack/자료_PDF/pdf-validation.json`

**Interfaces:**
- Consumes: Task 1–8 outputs, `mpe_cli.py`, `review_pdf.py`, `pack_layout.py`
- Produces: Republished `문제설명_*.html`, `.pack/문제설명_*.md`, `복습문제_*-문제.pdf`, `복습문제_*-답안.pdf` across all 10 packs

- [ ] **Step 1: Rebuild, validate, and publish `문제설명_*.html` and `.pack/문제설명_*.md` for all 10 packs via `mpe_cli.py`**

For each pack (`0907`..`1015`):
1. Run `python .agents/skills/ds-problem-explain/scripts/mpe_cli.py extract --repo . --target <range> --run tmp/lecture-readability-2026-10-18/mpe-run/<range>`
2. Copy the updated `tmp/lecture-readability-2026-10-18/<range>/fragments/*.html` into the run's `explanations/` directory.
3. Run `mpe_cli.py build --run ...`, update `review.json` with verified `source_visual`, `content`, `independent`, and `browser` entries for all subparts (`p.id:s`), run `mpe_cli.py validate --run ...`, and run `mpe_cli.py publish --run ... --repo .`.
4. Verify that in every published `문제설명_<range>_<slug>.html`, all 47 `lecture-code` problem panes contain both `<div data-source-field="conditions">` and `<h4>구할 것</h4><div data-source-field="ask"><ol><li>(a)`.

- [ ] **Step 2: Rebuild, check, inspect, and publish `복습문제_*-{문제,답안}.pdf` for all 10 packs via `review_pdf.py`**

1. Run `python .agents/skills/ds-review-pack/scripts/review_pdf.py backfill --repo . --target all --run tmp/lecture-readability-2026-10-18/pdf-run`
2. For each pack run directory in `pdf-run`, run `review_pdf.py check --run <pack_run>` (expect 0 errors and 0 overflow), inspect generated page PNGs, write `review.json` with `report_sha256` and `artifact_hashes`, and run `review_pdf.py publish --run <pack_run> --repo .`.

- [ ] **Step 3: Run full verification suite**

Run:
```powershell
python -m pytest .agents/skills/ds-problem-explain/tests .agents/skills/ds-review-pack/tests/test_lecture_html.py .agents/skills/ds-review-pack/tests/test_pdf_lecture.py .agents/skills/ds-review-pack/tests/test_review_delivery.py .agents/skills/ds-review-pack/tests/test_pdf_delivery.py -k "not test_original_reviews_notes_and_figures_unchanged" -v
python .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo .
```
Expected: All tests PASS and `pack_layout.py check` exits 0 (`OK`).

- [ ] **Step 4: Commit**

```powershell
git add 복습노트 docs/superpowers/specs/2026-10-18-lecture-problem-readability.md docs/superpowers/plans/2026-10-18-lecture-problem-readability.md
git commit -m "chore(review): regenerate explanations, MD, and PDFs for structured lecture problems"
```
