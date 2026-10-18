# 강의노트 기반 복습문제 standalone화 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 10개 복습팩의 lecture-code 문항 47개를 다른 문제·강의노트 참조 없이 카드 하나만으로 풀 수 있게 다시 쓰고, 같은 규칙을 검사기 lint로 강제한다.

**Architecture:** 먼저 `check_html.check_review`에 `lecture-standalone` 검사를 TDD로 추가해 위반을 기계적으로 찾는다. 이어서 팩별로 카드 fragment를 RUN 폴더에 꺼내 고치고, `update_review.build_revision`으로 stage HTML을 만든다. 전체 audit를 통과한 뒤 `publish_update`로 발행하고, 마지막으로 MD·문제설명·PDF를 다시 만든다.

**Tech Stack:** Python 3 (stdlib HTMLParser), pytest 9, gcc `-std=c11`, ds-review-pack·ds-problem-explain 스킬 스크립트.

**Spec:** `docs/superpowers/specs/2026-10-18-lecture-problem-standalone.md`

## Global Constraints

- `SKILL=.agents/skills/ds-review-pack`, `REPO`=저장소 루트, `RUN=tmp/lecture-standalone-2026-10-18` (팩별 하위 폴더 `$RUN/<range>/`).
- 작업 브랜치: `lecture-standalone` (main에서 분기).
- 수정 대상은 lecture-code 카드의 `div.problem`(배지 문단 제외)·`details.hint`·`details.solution`(`.answer` 포함)뿐이다.
- 배지 문단(`<p><span class="badge">강의 예제 기반 자체 출제</span> S… p…</p>`)과 `details.original`("강의 예제 보기")은 바이트 단위로 그대로 둔다.
- 기출·교과서 카드(`source_kind`≠`lecture-code`)는 `extract_cards`의 `raw`가 바이트 단위로 같아야 한다.
- 문제 번호·id·source·정답의 의미는 바꾸지 않는다. manifest의 `terms`는 카드 안에 그대로 남아야 한다(`check_html.py:306`).
- 문체는 기존 카드와 같은 "~해요"체를 쓴다.
- 정리노트 HTML/MD, STT, 강의록 PDF, 기출·교과서 원본은 수정하지 않는다.
- selection의 `policy_version`은 `review-questions-2026-10-17`을 유지한다. validation 기록은 덮어쓰지 않고 before/after 해시를 추가한다.
- 카드가 바뀐 팩은 `stamp_revision` 때문에 풀이 완료 표시가 초기화된다. 이는 계약상 정상 동작이므로 우회하지 않는다.

## Review Focus

1. **C 코드 식별자 오탐**: 코드 안의 `p1`, `*p2`, `P` 같은 이름이 lint에 걸리면 안 된다 → Task 1 `test_lecture_standalone_allows_code_identifiers`.
2. **본문에 넣은 정의가 원래 강의 코드와 다르게 동작**: 이렇게 되면 정답이 바뀐다. 1008 p2·p4의 remove_node·insert_node·get_node_at이 대표적이다 → 각 팩 Task의 R4(C11 harness)와 R3(본문만 보는 풀이자) 단계.
3. **새로 넣은 문장에 미리보기 금지어가 섞임**: `forbidden_outside_preview`나 후속 수업 용어가 들어갈 수 있다 → 각 팩 Task의 R6 `check_pack` 결과가 `[]`여야 한다.
4. **코드를 본문에 넣어 길어진 카드가 16:9 PDF 페이지를 넘침**: 배지 문단에 인용 외의 텍스트가 섞이면 `pdf_lecture.is_badge`가 예외를 던진다 → Task 13의 `review_pdf.py check` 결과 errors·overflow가 비어 있어야 한다.
5. **이후 생성되는 팩에서 재발** → Task 12의 저장소 회귀 테스트 `test_repo_lecture_cards_are_standalone`.

---

### Task 1: `lecture-standalone` lint와 규칙 문서

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/check_html.py:51-60` (Container), `:76-172` (_Parser), `:285-309` (check_review)
- Modify: `.agents/skills/ds-review-pack/references/review-overhaul.md` ("강의 예제 근거" 절 끝), `references/card-rules.md`
- Test: `.agents/skills/ds-review-pack/tests/test_lecture_html.py`

**Interfaces:**
- Produces:
  - `Container.part_text: dict[str, str]`: CARD_PARTS 클래스(`problem`, `original`, `hint`, `solution`, `answer`)별 텍스트. 가장 안쪽 part가 텍스트를 받는다(`answer`는 `solution` 안에 있으므로 `answer`로 들어감).
  - `LECTURE_REF_RE: re.Pattern`, `BADGE_LEAD_RE: re.Pattern`
  - `lecture_ref_hits(card: Container) -> list[str]`: 일치한 부분 문자열 목록
  - `Problem("lecture-standalone", <card id>, <hit들을 ", "로 연결>)`: `source_kind == "lecture-code"`인 카드에 대해서만 `check_review`가 내보낸다.

- [ ] **Step 1: 실패하는 테스트 작성** (`tests/test_lecture_html.py`, 기존 테스트의 card·manifest 형식 재사용)

```python
M={'forbidden_outside_preview':[],'problems':[{'id':'p1','source':'lecture-x','source_kind':'lecture-code','terms':[]}]}
def card(problem, hint='H', sol='S', kind='lecture-code'):
    return (f'<article id="p1" class="card" data-source="lecture-x" data-source-kind="{kind}">'
            f'<div class="problem"><p><span class="badge">강의 예제 기반 자체 출제</span> S4 p48 · 추가 근거 p28,47</p>{problem}</div>'
            '<details class="original"><summary>강의 예제 보기</summary><p>S4 p48 · Software_4_List.pdf</p></details>'
            f'<details class="hint">{hint}</details><details class="solution"><p class="answer">{sol}</p></details></article>')
def codes(html, m=M): return [(e.code, e.detail) for e in check_review(parse_html(html), m)]

def test_lecture_standalone_ignores_badge_and_original():
    assert codes(card('<p>길이 1인 리스트에서 값을 쓰세요.</p>')) == []

def test_lecture_standalone_flags_lecture_reference():
    out = codes(card('<p>강의 p47에서 get_node_at은 NULL을 반환해요.</p>'))
    assert [c for c,_ in out] == ['lecture-standalone'] and '강의' in out[0][1]

def test_lecture_standalone_flags_slide_citation_and_other_problem():
    assert [c for c,_ in codes(card('<p>S3 p8에서 높은 차수만 읽어요.</p>'))] == ['lecture-standalone']
    assert [c for c,_ in codes(card('<p>값을 쓰세요.</p>', hint='P3의 결과를 써요.'))] == ['lecture-standalone']
    assert [c for c,_ in codes(card('<p>앞 문제의 리스트를 써요.</p>'))] == ['lecture-standalone']

def test_lecture_standalone_flags_solution_answer():
    assert [c for c,_ in codes(card('<p>값을 쓰세요.</p>', sol='이 예제는 강의 원문의 결함이에요.'))] == ['lecture-standalone']

def test_lecture_standalone_allows_code_identifiers():
    assert codes(card('<pre><code>ListNode *p1, *p2; p1=p2-&gt;link;</code></pre><p>위 코드의 p1을 쓰세요.</p>')) == []

def test_past_exam_cards_not_linted():
    m={**M,'problems':[{**M['problems'][0],'source_kind':'past-exam'}]}
    assert codes(card('<p>강의 p3 참고</p>', kind='past-exam').replace('강의 예제 보기','기출 원문 보기'), m) == []
```

- [ ] **Step 2: 실패 확인**

Run: `cd .agents/skills/ds-review-pack && python -m pytest tests/test_lecture_html.py -v`
Expected: 새 테스트 중 flag 계열 4개가 FAIL (`lecture-standalone` 미존재). ignore·identifier·past-exam 테스트는 이미 PASS여도 된다.

- [ ] **Step 3: 구현** (`check_html.py`)

- `_Parser.stack` 튜플에 5번째 원소 `part`를 추가한다. 컨테이너 안에서 `classes & CARD_PARTS`가 있으면 그 클래스(가장 안쪽)를 part로 쓰고, `_emit`에서 `containers[con].part_text[part] += data`를 수행한다.
- 고정값:

```python
BADGE_LEAD_RE = re.compile(r'^\s*강의 예제 기반 자체 출제\s*(?:S\d+ p\d+(?: · 추가 근거 p\d+(?:,\d+)*)?)?')
LECTURE_REF_RE = re.compile(
    r'강의|정리노트|슬라이드|S\d+ p\d+'
    r'|(?<![A-Za-z0-9_>*&])p\d+(?=의|에서)'
    r'|(?<![A-Za-z0-9_])P\d+(?!\d)'
    r'|(?:앞|위|이전|다른) 문제')
```

- `lecture_ref_hits`: `BADGE_LEAD_RE`로 앞부분을 제거한 problem 텍스트와 hint·solution·answer 텍스트를 검사한다. `original`은 검사하지 않는다.
- `check_review`의 `lecture-label` 검사 바로 뒤에 `if kind=='lecture-code' and (hits:=lecture_ref_hits(card)): out.append(Problem('lecture-standalone', q['id'], ', '.join(hits)))`를 넣는다.

- [ ] **Step 4: 통과 확인**

Run: `cd .agents/skills/ds-review-pack && python -m pytest tests -q`
Expected: 전체 PASS. 기존 테스트 회귀가 없어야 한다.

- [ ] **Step 5: 현재 저장소 위반 목록 확인**

Run (저장소 루트):
```bash
python - <<'EOF'
import json,sys; from pathlib import Path
sys.path.insert(0,'.agents/skills/ds-review-pack/scripts'); from check_html import check_review,parse_html
for m in sorted(Path('복습노트').glob('*/.pack/자료_복습팩/manifest.json')):
    rng=m.parents[2]; html=next(rng.glob('복습문제_*.html')).read_text(encoding='utf-8')
    print(rng.name,[(e.where,e.detail) for e in check_review(parse_html(html),json.loads(m.read_text(encoding='utf-8'))) if e.code=='lecture-standalone'])
EOF
```
Expected: 스펙의 "확인된 위반" 표에 있는 16개 카드가 모두 나와야 한다(0907 p4, 0914 p7, 0921 p5·p7·p10·p11, 0928 p7·p9, 1001 p3, 1005 p7, 1008 p2·p4·p5, 1012 p9, 1015 p4·p5). 표에 없는 카드가 추가로 잡히면 해당 팩 Task의 대상에 넣는다. 결과는 `$RUN/violations-before.txt`에 저장한다.

- [ ] **Step 6: 규칙 문서**

`review-overhaul.md` "강의 예제 근거" 절 끝과 `card-rules.md`에 다음 한 문단을 추가한다. "lecture-code 카드의 문제·힌트·풀이·정답은 standalone이다. 강의 페이지·슬라이드·정리노트·다른 문제(Pn, 앞 문제)를 가리키지 않고, 필요한 함수 계약·코드·규칙·값을 본문에 직접 쓴다. 출처는 배지 인용과 `강의 예제 보기`에만 둔다. `check_html`의 `lecture-standalone`이 이를 검사한다." 그 뒤 `python -m pytest tests/test_skill_files.py -q` PASS를 확인한다.

- [ ] **Step 7: Commit**

```bash
git add .agents/skills/ds-review-pack/scripts/check_html.py .agents/skills/ds-review-pack/tests/test_lecture_html.py .agents/skills/ds-review-pack/references/review-overhaul.md .agents/skills/ds-review-pack/references/card-rules.md
git commit -m "feat(ds-review-pack): lint lecture-code cards for external references"
```

---

### Task 2: RUN 준비 (백업·baseline)

**Files:**
- Create: `$RUN/backup/`, `$RUN/baseline.json`, `$RUN/<range>/cards/`

**Interfaces:**
- Produces: `$RUN/<range>/cards/<id>.html`(각 카드의 `raw`), `$RUN/<range>/manifest.json`(원본 복사본), `$RUN/baseline.json`

- [ ] **Step 1:** `tmp/`가 git에서 무시되는지 확인한다(`git check-ignore tmp/x`). 무시되지 않으면 RUN을 스크래치 경로로 옮기고 Global Constraints의 RUN 값을 갱신한다.
- [ ] **Step 2:** 10개 팩의 `복습문제_*.html`, `.pack/복습문제_*.md`, `.pack/문제설명_*.md`, `문제설명_*.html`, PDF 두 개, `.pack/자료_복습팩/*`를 `$RUN/backup/<range>/`에 복사하고 sha256 목록을 `$RUN/backup/hashes.txt`에 남긴다.
- [ ] **Step 3:** `python -c "import sys,json;sys.path.insert(0,'$SKILL/scripts');from review_inventory import collect_reviews;..."`로 `collect_reviews(REPO)` 결과를 `$RUN/baseline.json`에 쓴다. 함수 위치가 다르면 `grep -n "def collect_reviews" $SKILL/scripts/*.py`로 찾는다.
- [ ] **Step 4:** 팩마다 `extract_cards(html)`의 각 카드 `raw`를 `$RUN/<range>/cards/<id>.html`로 저장하고 manifest를 복사한다. 검증 기준: 47개 lecture-code 파일이 존재해야 한다.

---

### 팩 개정 절차 R (Task 3–11 공통)

각 팩 Task는 아래 R1–R7을 그 팩의 대상 카드에 적용한다. `<range>`, 대상 id, 필수 반영 내용은 각 Task에 적혀 있다.

- **R1 수정**: `$RUN/<range>/cards/<id>.html`에서 problem(배지 문단 뒤)·hint·solution·answer만 고친다. 참조 표현은 그 표현이 뜻하던 내용으로 바꾼다. 본문 밖에서 정의된 함수·규칙·상수는 계약 문장이나 코드 블록(`<pre><code class="language-c">`)으로 본문에 넣는다. 코드는 해당 `lecture_ref`의 PDF 페이지에서 그대로 옮긴다.
- **R2 manifest**: 정답 문구를 바꿨으면 `$RUN/<range>/manifest.json`의 해당 `answer`를 카드 `.answer`와 같은 문장으로 맞춘다. `terms`는 바꾸지 않는다.
- **R3 본문만 보는 풀이자**: 대상 카드마다 새 서브에이전트에 `div.problem` 텍스트만 주고 풀게 한다(힌트·풀이·original은 주지 않음). 결과를 `answer`와 비교해 `$RUN/<range>/solver.json`에 `{id: {"match": bool, "missing": "<풀이자가 추측해야 했던 정보>"}}`로 기록한다. 기준: 모든 대상이 `match: true`이고 `missing`이 빈 문자열이어야 한다. 아니면 R1로 돌아간다.
- **R4 C11 검산**: 코드를 새로 넣었거나 코드 실행 결과를 묻는 카드는 `$RUN/<range>/harness/<id>.c`를 만든다. `gcc -std=c11 -Wall -Wextra -fsanitize=address,undefined`로 실행한 출력이 정답과 일치해야 한다. 누수를 묻는 문항은 ASan 누수 보고 자체를 증거로 쓴다. 출력은 `harness/<id>.out`에 저장한다.
- **R5 stage 생성**: `build_revision(원본 HTML, manifest=$RUN/<range>/manifest.json, cards={id: 파일 내용})` → `$RUN/<range>/stage/<원본 파일명>`.
- **R6 검사**: `check_pack(manifest, 정리노트 HTML, stage HTML)` 결과가 `[]`여야 한다(lecture-standalone 포함). 같은 팩에서 비대상 카드의 `raw`가 원본과 같아야 하고, 대상 카드의 배지 문단과 `details.original` 바이트도 원본과 같아야 한다.
- **R7 기록**: `$RUN/<range>/changes.md`에 카드별로 "제거한 참조 → 넣은 내용"을 한 줄씩 남긴다.

---

### Task 3: 0907 (p4, p5, p6, p7)
- p4(보충, `scope=retained-supplement`): "강의 코드에서" → "전역 배열 score의 앞 n개가 입력이에요". `score`의 선언(`int score[MAX];`)이 본문 코드에 없으면 추가한다. 후속 보충임을 밝히는 기존 표시는 유지한다.
- p5–p7: lint 위반은 없다. R3만 수행하며, 실패한 경우에만 수정한다.
- R1–R7을 적용한다.

### Task 4: 0914 (p6, p7, p8) · 0917 (p5, p6)
- 0914 p7: "강의 규칙처럼 루프 제어는 제외하고" → "for 문의 초기화·비교·증가는 세지 않고"로 바꾸고, 세는 연산(대입·덧셈·곱셈 각 1회) 정의를 본문에 그대로 둔다.
- 나머지 카드: R3만 수행한다.
- 두 팩에 각각 R1–R7을 적용한다.

### Task 5: 0921 (p5–p11)
- p5: "코드는 강의 그림의 행렬 A를 C로 옮긴 것" → "아래 코드는 행렬 A를 C 배열로 쓴 것이에요".
- p7: 내림차순 계수 저장 규칙을 본문에 정의한다. 기준은 `S3` 해당 페이지의 polynomial 구조체(`degree`, `coef[MAX_DEGREE]`)이며, "coef[i]는 x^(degree−i)의 계수"를 명시한다.
- p10: 두 방식을 이름으로 정의한다((a) 모든 차수 계수 배열 내림차순, (b) (계수,차수) 쌍 배열). "S3 p8에서…"는 해당 페이지의 덧셈 함수 코드(`poly_add1`) 중 차수 비교 분기를 본문 코드로 넣은 뒤 그 분기를 가리키는 문장으로 바꾼다. R4 harness 대상이다.
- p11: "강의의 person" → `struct person { char name[10]; int age; float height; };` 선언을 본문에 넣는다.
- p6, p8, p9: R3만 수행한다.

### Task 6: 0928 (p5–p9)
- p7: "다음은 강의 개념을 확인하는 자체 코드예요" → "다음 코드를 보세요".
- p9: "강의의 struct AlignDepends" → 선언을 본문 코드로 제시한다(환경 가정 문장은 유지).
- p5, p6, p8: R3만 수행한다. p5의 "위 함수"는 같은 카드 안의 코드를 가리키므로 허용된다.

### Task 7: 1001 (p1–p5)
- p3: "강의 사용 예의" 삭제. 연산 의미를 본문에 정의한다. `add_tail(x)`: 끝에 추가. `add(pos,x)`: pos 위치에 넣고 뒤 원소를 한 칸씩 민다. `delete(pos)`: 삭제하고 뒤 원소를 당긴다. `replace(pos,x)`: 교체. `get_entry(pos)`·`get_length()`: 조회. 위치는 0부터 센다.
- 나머지: R3만 수행한다.

### Task 8: 1005 (p3–p11)
- p7: "강의의 head는 마지막 노드를 가리켜요" → "이 원형 리스트 구현에서 head는 마지막 노드를 가리켜요". 끝 삽입 함수(`insert_last`) 코드가 본문에 없으면 강의 해당 페이지에서 옮겨 넣는다. R4 harness 대상이다.
- p10: 세 구현이 본문만으로 정의되는지 R3로 확인한다.
- 나머지: R3만 수행한다.

### Task 9: 1008 (p2–p5)
- p2: "강의 p47…p28의…" 문장을 지우고 다음 둘을 본문에 넣는다. ① `get_node_at(list,pos)` 계약: pos<0이면 NULL, 그 외에는 head에서 pos번 link를 따라간 노드. ② `remove_node(ListNode **phead, ListNode *p, ListNode *removed)` 코드(Software_4_List.pdf p28). 풀이의 "강의 원문의 결함" → "이 래퍼 코드의 결함". R4 harness(ASan 누수 보고) 대상이다.
- p4: "기존 insert_node" → `insert_node(ListNode **phead, ListNode *p, ListNode *new_node)` 코드(Software_4_List.pdf의 해당 페이지)와 `get_node_at` 계약을 본문에 넣는다. R4 대상이다.
- p5: "강의 예처럼" 삭제(상황은 이미 본문에 정의되어 있음).
- p3: R3만 수행한다.

### Task 10: 1012 (p7, p8, p9)
- p9: "강의 eval의 일부예요" → "후위식 계산 함수 eval의 일부예요". 스택 연산(`push`, `pop`)의 의미를 한 문장으로 명시한다.
- p7, p8: R3만 수행한다.

### Task 11: 1015 (p4–p8)
- p4: "강의 그림을 바탕으로 직접 코드를 작성하는 문제예요" 문장을 삭제한다.
- p5: "강의 루프의 일부예요" → "은행 대기열 시뮬레이션 루프의 일부예요". 루프에서 쓰는 변수(`clock`, `service_time` 등)가 모두 본문에 정의되어 있는지 R3로 확인한다.
- p6–p8: R3만 수행한다.

각 팩 Task(3–11)의 완료 기준: R3 전부 match, R6 `[]`, `changes.md` 작성. 이 단계에서는 커밋하지 않는다(stage가 RUN에만 있음).

---

### Task 12: 전체 audit, 발행, 회귀 테스트

**Files:**
- Modify: `복습노트/<range>/복습문제_*.html` ×10, `복습노트/<range>/.pack/자료_복습팩/{manifest,selection,validation}.json`
- Test: `.agents/skills/ds-review-pack/tests/test_lecture_html.py`

**Interfaces:**
- Consumes: Task 3–11의 `$RUN/<range>/stage/*.html`, `$RUN/<range>/manifest.json`, `solver.json`, `harness/*.out`

- [ ] **Step 1: 저장소 회귀 테스트 작성**

```python
def test_repo_lecture_cards_are_standalone():
    from _util import REPO
    import json
    bad = []
    for m in sorted((REPO/'복습노트').glob('*/.pack/자료_복습팩/manifest.json')):
        rng = m.parents[2]
        html = next(rng.glob('복습문제_*.html')).read_text(encoding='utf-8')
        bad += [(rng.name, e.where, e.detail) for e in check_review(parse_html(html), json.loads(m.read_text(encoding='utf-8'))) if e.code == 'lecture-standalone']
    assert bad == []
```

- [ ] **Step 2: 실패 확인** — `python -m pytest tests/test_lecture_html.py::test_repo_lecture_cards_are_standalone -v` → FAIL. 실패 목록이 `violations-before.txt`와 같아야 한다.
- [ ] **Step 3: audit** — `$RUN/overlay.json`(range→stage 절대 경로 10개), `$RUN/decisions.json`=`[]`을 만들고 다음을 실행한다.
  `python $SKILL/scripts/review_audit.py --repo . --overlay $RUN/overlay.json --decisions $RUN/decisions.json --baseline $RUN/baseline.json --out $RUN/audit.json`
  기대 결과: `status=pass`, `blocking=[]`, `candidates=[]`. 후보가 나오면 판정을 decisions.json에 기록하고 다시 실행한다.
- [ ] **Step 4: 발행** — 팩마다 `publish_update({review_html: stage bytes, manifest_path: bytes, selection_path: bytes, validation_path: bytes}, backup=$RUN/publish-backup/<range>)`를 실행한다.
  - selection에는 `replacements`에 대상 id별 이전/새 content hash를 추가한다.
  - validation에는 before/after 해시, `solver.json`·`harness/*.out` 경로, `lecture-standalone: pass`를 추가한다. 기존 기록은 덮어쓰지 않는다.
- [ ] **Step 5: 통과 확인** — `python -m pytest tests -q` 전체 PASS, `python $SKILL/scripts/pack_layout.py check --repo .` PASS.
- [ ] **Step 6: Commit**

```bash
git add 복습노트/*/복습문제_*.html 복습노트/*/.pack/자료_복습팩 .agents/skills/ds-review-pack/tests/test_lecture_html.py
git commit -m "fix(review): make lecture-code problems standalone across 10 packs"
```

---

### Task 13: MD·문제설명·PDF 재생성

**Files:**
- Modify: `복습노트/<range>/.pack/복습문제_*.md`, `복습노트/<range>/문제설명_*.html`, `.pack/문제설명_*.md`, `복습문제_*-문제.pdf`, `복습문제_*-답안.pdf`

- [ ] **Step 1: MD** — 팩마다 `python $SKILL/scripts/html2md.py <정리노트.html> <복습문제.html> --check` → 오류가 없어야 한다. 정리노트 MD의 해시가 바뀌지 않았는지 확인한다.
- [ ] **Step 2: 문제설명** — `references/problem-explain.md` 절차를 최종 복습문제 HTML 절대 경로로 팩마다 실행한다(ds-problem-explain `scripts/mpe_cli.py`). 기준: 대상 카드 설명에 `lecture-standalone` 패턴(`LECTURE_REF_RE`)이 없어야 한다.
- [ ] **Step 3: PDF** — 팩마다 `review_pdf.py build --review <abs> --run $RUN/pdf/<range>` → `check --run …` → errors·overflow가 없을 때만 `publish --run … --repo .`. 문제지와 답안지의 모든 페이지를 육안으로 검토한다(Review Focus 4).
- [ ] **Step 4: 실화면** — 대상 팩 HTML을 1280×900·375×812, light·dark로 열어 대상 카드의 원문·힌트·풀이·코드 스크롤과 콘솔 오류 0을 확인한다.
- [ ] **Step 5:** `python -m pytest tests -q`, `pack_layout.py check --repo .` 재실행 → PASS.
- [ ] **Step 6: Commit**

```bash
git add 복습노트
git commit -m "chore(review): regenerate MD, explanations and PDFs for standalone lecture problems"
```
