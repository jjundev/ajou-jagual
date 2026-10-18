# 강의 코드 PDF 문제 영역 분해 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 강의 코드 카드의 PDF 문제 패널을 조건(문장별)과 구할 것(번호 목록)으로 나누고 `강의 예제 기반 자체 출제 …` 배지 문단을 삭제한 뒤, 10개 팩의 문제·답안 PDF를 다시 발행한다.

**Architecture:** 새 모듈 `scripts/pdf_lecture.py`가 카드의 prose Block들을 `(conditions_html, ask_html)`로 변환한다. `pdf_cards.to_payload`는 `c.kind=='강의 코드'`일 때만 이를 써서 템플릿에 이미 있는 `html.conditions`/`html.ask` 슬롯을 채운다. Block/PageSlice는 바꾸지 않으므로 `check_coverage`(`pdf_layout.py:30`)는 영향받지 않는다.

**Tech Stack:** Python 3.10+, pytest(`uv run -q --no-project --with pytest --with pymupdf python -m pytest`), Playwright + 설치된 Chrome(렌더 테스트·빌드), PyMuPDF.

**Spec:** `docs/superpowers/specs/2026-10-18-lecture-code-pdf-split-design.md`

## Global Constraints

- 대상: `data-source-kind="lecture-code"` 카드(`Card.kind=='강의 코드'`)만. 기출·교과서 payload는 바이트 단위로 현행 유지.
- 복습문제 HTML/MD, EC2 템플릿 원본(`assets/pdf/ec2/*`), 글꼴 크기는 수정 금지. CSS 추가는 `pdf_ds_layout.extend`의 확장 `<style>`에서만.
- 배지 문단 = `class="badge"`를 포함한 prose Block. PDF payload 어디에도(`conditions`, `ask`, 답안) 나오면 안 된다.
- `후속 수업 보충:`으로 시작하는 prose Block은 삭제하지 않고 `<p class="ds-source">…</p>` 캡션으로 조건 맨 위에 둔다.
- 문장 분리: `[.?!]` 직후 공백에서만, 열린 HTML 요소가 없고 `$…$` 밖일 때만.
- 질문 판별(태그 제거·trim한 문장 `t`): `t2 = re.sub(r'\s*\([^()]*\)(?=[.?!]?$)', '', t)` 후 `re.search(r'(?:세요|시오|하라|보라)[.)]?$|\?$', t2)`.
- 무손실: 배지 Block을 뺀 prose Block들의 공백 제거 텍스트 합 == 출력 HTML의 태그·공백 제거 텍스트. 다르면 `PdfError`.
- 발행은 `references/pdf-build.md` 절차 그대로. 모든 페이지 PNG 실화면 검토 없이 review.json에 pass를 쓰지 않는다.

## Review Focus

- 문장 경계가 `<strong>`/`<code>` 같은 열린 인라인 요소 안에 있는 경우 → 자르지 않고 HTML이 깨지지 않아야 한다 (Task 1 `test_no_split_inside_open_element`).
- 질문 문장 끝에 괄호 주석이 붙은 경우(`…설명하세요(그림의 링크 변경만 묻습니다).`, 1001 p5) → 질문으로 분류 (Task 1 `test_trailing_parenthetical_is_ask`).
- 문제에 그림/표 Block이 섞인 강의 카드(현재 0장이지만 향후 가능) → 그림은 기존처럼 가운데로 추출되고 글자는 보존 (Task 2 `test_lecture_figure_still_extracted`).
- 가장 긴 카드(1001 p5, 1005 p10)가 분해 후 길어져도 넘침 없이 계속 페이지로 렌더 (Task 2 `test_lecture_long_card_renders`).
- 답안 PDF도 같은 분해·배지 삭제 (Task 2 `test_lecture_answers_mode_split`).

---

### Task 1: 강의 문제 분해 함수

**Files:**
- Create: `.agents/skills/ds-review-pack/scripts/pdf_lecture.py`
- Test: `.agents/skills/ds-review-pack/tests/test_pdf_lecture.py`

**Interfaces:**
- Consumes: `pdf_types.Block`, `pdf_types.PdfError`, `pdf_cards.read_pack`(테스트 전용).
- Produces: `split_lecture_problem(blocks: tuple[Block, ...]) -> tuple[str, str]` — `(conditions_html, ask_html)`. 입력은 `kind=='prose'` Block만(호출자가 거름). `conditions_html`은 `[<p class="ds-source">보충</p>] + <p>조건문장</p>*`, `ask_html`은 `<ol class="ds-asks"><li>질문</li>…</ol>` 또는 폴백 시 원래 prose HTML 연결.

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_pdf_lecture.py` (`from _util import REPO` 로 경로 설정, 헬퍼 `lecture(range_, pid)`는 `read_pack`으로 해당 카드의 prose Block 튜플 반환, `P(html)`은 `Block('prose', html, 태그제거텍스트)`):

```python
def test_1015_p5_split():
    cond, ask = split_lecture_problem(lecture('1015', 'p5'))
    assert cond.count('<p>') == 4 and ask.count('<li>') == 2
    assert strip(ask).startswith('clock=1,2,3에서')
    assert '강의 예제 기반' not in cond + ask and 'S6 p22' not in cond + ask

def test_trailing_parenthetical_is_ask():
    cond, ask = split_lecture_problem(lecture('1001', 'p5'))
    assert cond.count('<p>') == 1 and ask.count('<li>') == 5

def test_supplement_kept_as_caption():
    cond, ask = split_lecture_problem(lecture('0907', 'p4'))
    assert cond.startswith('<p class="ds-source">') and '후속 수업 보충' in cond
    assert '강의 예제 기반' not in cond + ask

def test_no_split_inside_open_element():
    cond, ask = split_lecture_problem((P('<p>A는 <code>x. y</code>예요. <strong>a. b</strong>를 쓰세요.</p>'),))
    assert cond == '<p>A는 <code>x. y</code>예요.</p>'
    assert ask == '<ol class="ds-asks"><li><strong>a. b</strong>를 쓰세요.</li></ol>'

def test_fallback_existing_list_and_no_question():
    badge = P('<p><span class="badge">강의 예제 기반 자체 출제</span> S1 p2</p>')
    lst = P('<ol><li>(a) 쓰세요.</li></ol>')
    assert split_lecture_problem((badge, lst)) == ('', lst.html)
    plain = P('<p>상황만 있어요. 끝이에요.</p>')
    assert split_lecture_problem((badge, plain)) == ('', plain.html)

def test_all_lecture_cards_lossless_and_badge_free():
    n = 0
    for src in sorted((REPO / '복습노트').glob('*/복습문제_*.html')):
        for c in read_pack(src).cards:
            if c.kind != '강의 코드': continue
            prose = tuple(b for b in c.problem if b.kind == 'prose')
            cond, ask = split_lecture_problem(prose)
            assert '<li>' in ask, c.id
            assert squash(cond + ask) == squash(''.join(b.text for b in prose if 'class="badge"' not in b.html))
            assert '강의 예제 기반' not in cond + ask
            n += 1
    assert n == 47
```

(`strip` = 태그 제거, `squash` = 태그·모든 공백 제거; 테스트 파일 안에 정의. HTML 엔티티는 `html.unescape` 후 비교.)

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-review-pack/tests/test_pdf_lecture.py -q`
Expected: FAIL — `ModuleNotFoundError: pdf_lecture`

- [ ] **Step 3: `split_lecture_problem` 구현**

처리 순서: 배지 Block 제거 → 보충 Block은 캡션으로 → 나머지 중 html이 `<ol`/`<ul`로 시작하는 Block이 있으면 폴백 → 각 `<p>` 내부 HTML을 문장 분리 → 분류 → 질문 0개면 폴백 → 무손실 검사(실패 시 `PdfError(card 텍스트 앞 40자)`).

문장 분리는 정규식 하나로 결정되지 않으므로 이 알고리즘을 쓴다:

```python
def sentences(inner: str) -> list[str]:
    out, start, depth, math, i = [], 0, 0, False, 0
    while i < len(inner):
        ch = inner[i]
        if ch == '<':
            j = inner.index('>', i)
            tag = inner[i:j + 1]
            if not tag.endswith('/>') and not re.match(r'<(br|img|hr)\b', tag):
                depth += -1 if tag.startswith('</') else 1
            i = j + 1; continue
        if ch == '$': math = not math
        if ch in '.?!' and depth == 0 and not math and i + 1 < len(inner) and inner[i + 1].isspace():
            out.append(inner[start:i + 1].strip()); start = i + 1
        i += 1
    tail = inner[start:].strip()
    return out + ([tail] if tail else [])
```

`<p>` 내부 추출은 바깥 `<p…>`/`</p>`만 벗긴다(문단 하나 = Block 하나, `pdf_cards.blocks`가 보장).

- [ ] **Step 4: 통과 확인**

Run: 위와 같은 명령
Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add .agents/skills/ds-review-pack/scripts/pdf_lecture.py .agents/skills/ds-review-pack/tests/test_pdf_lecture.py
git commit -m "feat(review-pdf): split lecture-code problems into conditions and asks"
```

---

### Task 2: payload 연결·CSS·문서

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/pdf_cards.py:166-180` (`to_payload`)
- Modify: `.agents/skills/ds-review-pack/scripts/pdf_ds_layout.py:48` (확장 `<style>` 문자열)
- Modify: `.agents/skills/ds-review-pack/references/pdf-build.md` (절 추가)
- Test: `.agents/skills/ds-review-pack/tests/test_pdf_lecture.py` (추가)

**Interfaces:**
- Consumes: Task 1의 `split_lecture_problem(blocks) -> (conditions_html, ask_html)`.
- Produces: 강의 코드 페이지의 payload `p['html'] == {'original':'','conditions':cond,'ask':ask_with_figures_removed,'code':code}`. 다른 kind는 현행과 동일.

- [ ] **Step 1: 실패하는 테스트 추가**

```python
def payload(range_, mode='problems'):
    pack = read_pack(next((REPO / '복습노트' / range_).glob('복습문제_*.html')))
    pages = tuple(PageSlice(c.id, c.id, 1, c.problem, c.solution, True, True) for c in pack.cards)
    return pack, to_payload(pack, mode, pages, Path(tempfile.mkdtemp()) / 'assets')

def test_lecture_payload_uses_conditions():
    pack, data = payload('1015')
    p5 = next(p for p in data['problems'] if p['id'] == 'p5')
    assert p5['html']['conditions'].count('<p>') == 4 and '<ol class="ds-asks">' in p5['html']['ask']
    assert 'service_time--' in p5['html']['code']

def test_lecture_answers_mode_split():
    _, data = payload('1015', 'answers')
    assert all('강의 예제 기반' not in json.dumps(p['html'], ensure_ascii=False) for p in data['problems'])

def test_non_lecture_payload_unchanged():
    _, data = payload('1015')
    p1 = next(p for p in data['problems'] if p['id'] == 'p1')
    assert p1['html']['conditions'] == '' and 'ds-asks' not in p1['html']['ask']

def test_lecture_figure_still_extracted():
    # 임시 폴더에 lecture-code 카드 1장: 배지 <p>, "<p>상황이에요. 값을 쓰세요.</p>", <svg viewBox="0 0 80 40">…</svg>
    ...
    assert len(p['figures']) == 1 and '<svg' not in p['html']['ask'] and '<li>' in p['html']['ask']

def test_lecture_long_card_renders():
    from pdf_layout import plan_pages  # 실제 측정 분할 사용
    pack = read_pack(next((REPO / '복습노트/1001').glob('복습문제_*.html')))
    # plan_pages(pack, tmp) 후 problems/answers 각각 render → errors == () and overflow == ()
```

(`test_lecture_figure_still_extracted`의 카드는 `test_pdf_cards.test_images_frozen_in_solution_answer_hint`의 임시 파일 패턴을 따르고 `data-source-kind="lecture-code"`를 붙인다. 렌더 테스트는 Chrome이 필요하므로 기존 렌더 테스트와 같은 방식으로 실행.)

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-review-pack/tests/test_pdf_lecture.py -q`
Expected: 새 테스트 5개 FAIL (`conditions == ''`, `강의 예제 기반` 포함)

- [ ] **Step 3: `to_payload` 수정**

`c.kind == '강의 코드'`이면 `cond, text = split_lecture_problem(tuple(b for b in page.problem if b.kind == 'prose'))`, `body = text + ''.join(figure/table Block html)`; 그 외에는 현행 `body`. `figures_from(body, …)`는 그대로 적용하고 `'conditions': cond`(비강의 카드는 `''`).

- [ ] **Step 4: 확장 CSS 추가**

`pdf_ds_layout.py`의 마지막 `<style>` 문자열 끝에 정확히 추가:
`.ds-source { font-size: .8em; color: #777; margin: 0 0 2mm; } .conditions p { margin: 0; } .conditions p + p, .ds-asks li + li { margin-top: 1.5mm; } .ds-asks { padding-left: 1.4em; margin: 0; }`

- [ ] **Step 5: 통과 확인 + 회귀**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-review-pack/tests -q -p no:cacheprovider`
Expected: test_pdf_lecture 전부 PASS, 기존 실패 목록이 작업 전 기준선과 동일(작업 시작 전에 같은 명령으로 `FAILED` 줄을 scratchpad에 저장해 두고 비교).

- [ ] **Step 6: 문서**

`references/pdf-build.md`의 "자구알 배치 확장" 절 뒤에 `## 강의 코드 문제 분해` 절을 추가: 배지 문단 PDF 삭제, 보충 캡션, 문장 분리·질문 판별 규칙, 폴백, 무손실 실패 조건을 Global Constraints 문구 그대로 5줄 이내로.

- [ ] **Step 7: Commit**

```bash
git add .agents/skills/ds-review-pack/scripts/pdf_cards.py .agents/skills/ds-review-pack/scripts/pdf_ds_layout.py .agents/skills/ds-review-pack/references/pdf-build.md .agents/skills/ds-review-pack/tests/test_pdf_lecture.py
git commit -m "feat(review-pdf): render lecture-code conditions and numbered asks"
```

---

### Task 3: 10개 팩 PDF 재생성·검토·발행

**Files:**
- Modify(발행 결과): `복습노트/{0907,0914,0917,0921,0928,1001,1005,1008,1012,1015}/복습문제_*-{문제,답안}.pdf`, 각 `.pack/자료_PDF/pdf-validation.json`

**Interfaces:**
- Consumes: Task 2까지 커밋된 생성기. `review_pdf.py backfill|check|publish` CLI(`references/pdf-build.md`).

- [ ] **Step 1: backfill**

Run (RUN은 scratchpad 아래 새 빈 디렉터리): `python .agents/skills/ds-review-pack/scripts/review_pdf.py backfill --repo "$REPO" --target all --run "$PDF_RUN"`
Expected: `summary.json`에 10개 run, 각 `report.json` status=staged, checks.status=pass. withheld/stale가 있으면 생성기를 고치고 새 RUN에서 반복(템플릿·코드 생략으로 통과시키지 않음).

- [ ] **Step 2: run별 check**

Run: 각 run에 `review_pdf.py check --run <run>`
Expected: 오류 0.

- [ ] **Step 3: 전 페이지 실화면 검토**

각 run의 `stage/pages/problems/*.png`, `stage/pages/answers/*.png` 모든 페이지를 Read로 연다. 강의 코드 페이지마다 확인: 배지 문구 없음 / 조건 문장 줄바꿈 / 구할 것 번호 개수가 원문 질문 수와 일치 / 코드 블록 온전 / 계속 페이지 순서 / 하단 여백. 비강의 페이지는 이전 PDF와 동일 배치인지 확인.

- [ ] **Step 4: review.json 기록**

각 run에 `status=pass`, `reviewer`, 페이지별 구체 evidence, `report_sha256`(현재 report.json SHA-256), `artifact_hashes`(report.json 값 그대로).

- [ ] **Step 5: publish**

Run: 각 run에 `review_pdf.py publish --run <run> --repo "$REPO"`
Expected: 10팩 모두 교체, 백업은 `$PDF_RUN/backups`. 실패 팩은 이전 PDF 유지 + 사유 보고.

- [ ] **Step 6: 최종 검사·Commit**

Run: `python .agents/skills/ds-review-pack/scripts/pack_layout.py check --repo "$REPO"` → pass.

```bash
git add 복습노트/*/복습문제_*-문제.pdf 복습노트/*/복습문제_*-답안.pdf 복습노트/*/.pack/자료_PDF/pdf-validation.json
git commit -m "chore(review-pdf): regenerate PDFs with split lecture-code problems"
```
