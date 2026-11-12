# report-audit AI 작성 신호 검출 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `report-audit` 스킬의 `scripts/report_md.py`에 `signals` 서브커맨드를 더해, 과제2에서 밝혀낸 AI 작성 신호 10종을 Markdown 한 파일에서 검출·보고(수정 없음)한다.

**Architecture:** 기존 `report_md.py`의 `_walk`·`prose_lines`·`_IMAGE` 구조를 재사용하며 순수 함수 `style_signals(text, source=None) -> list[tuple[name, loc, evidence]]` 하나를 추가한다. 10개 검출기는 `_signal_<name>` 내부 함수로 분리되고 `style_signals`가 고정 순서로 호출한다. CLI는 `signals PATH [--source X.c]`로 노출되며 하나라도 발견되면 exit 1, 전부 음성이면 0, 파일 오류 2(기존과 동일).

**Tech Stack:** Python 3 표준 라이브러리(argparse, re, pathlib, unittest). 외부 의존성 없음. 기존 파일만 유지.

**Spec:** 이 세션(2026-11-12) grill-yourself 출력 "report-audit에 AI 작성 신호 보고 기능 추가". 모든 결정은 그 설계의 Confident·Needs you 표를 따른다. 사용자 확정: 10종만, 임계값은 trigram 0.6 / 접두 0.8 / parity 0.9, 1인칭은 한국어 어휘만.

## Global Constraints

- **표준 라이브러리만**: 기존 `report_md.py`는 외부 의존성이 없다. 유지한다.
- **수정 금지**: `signals`는 보고만 한다. 어떤 분기에서도 `text`나 `source`를 돌려쓰지 않는다. `SKILL.md`의 "Out of scope: style signals"는 본문을 바꾸지 않고 한 문장만 추가한다.
- **신호 이름 10종 고정** (이 순서로 출력, Task 간 공유):
  1. `run-script-trace`
  2. `output-block-smushed-prompts`
  3. `caption-duplication`
  4. `cell-prefix-repetition`
  5. `out-of-scope-vocabulary`
  6. `no-personal-voice`
  7. `evaluation-report-vocabulary`
  8. `third-person-rubric-echo`
  9. `provided-vs-implemented-parity`
  10. `source-out-of-scope-guards`
- **반환 튜플**: 각 신호 양성마다 `(signal_name: str, location: str, evidence: str)`. `location`은 `line 123` / `image 3` / `cell row 4` / `function dequeue` / `skipped`. `evidence`는 60자 이내 발췌 또는 수치(`6/6`, `count=37`).
- **CLI 출력**: 각 양성 한 줄에 `name<TAB>location<TAB>evidence`. `signals`는 양성 ≥1이면 exit 1, 0이면 exit 0, `source-out-of-scope-guards`의 `skipped`는 양성으로 치지 않는다.
- **임계값(코드 상수, argparse로 노출 안 함)**: trigram Jaccard 0.6 / 셀 접두 반복률 0.8 / parity 비율 0.9 / out-of-scope 어휘 ≥3회 / evaluation 어휘 ≥5회 / rubric echo ≥2회 / smushed-prompts 연속 안내문 ≥2회.
- **1인칭 어휘 (한국어만)**: `나는|내가|처음에|헷갈|시행착오|고쳤|수정했|생각했|이해했|보았다|느낀|어려|막혔|놓쳤|배운`. 영어는 포함하지 않는다.
- **커밋 템플릿** (모든 Task):
  ```
  <type>(report-audit): <subject>

  Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
  ```
- **읽기 범위**: `signals`는 대상 `.md`와 `--source`로 명시된 `.c`만 읽는다. 다른 파일·`git log`·캡처 PNG 금지. `SKILL.md:10~12`의 원칙을 그대로 따른다.
- **기존 테스트 유지**: `pytest .claude/skills/report-audit/tests/test_report_md.py`가 변경 후에도 모두 PASS.

## Review Focus

이 설계가 조용히 지나치면 사람이 쓸 때 다치는 입력 다섯 가지. 각각 명시된 Task의 테스트로 못 박는다.

1. **빈 Markdown** — 신호 하나도 안 걸리고 exit 0, stderr 없음. (Task 1, `test_signals_on_empty_file_exits_zero`)
2. **이미지가 2장 이하**인 보고서 — `caption-duplication`은 ≥3장 요구. 2장짜리 입력에 false-positive 금지. (Task 4, `test_caption_duplication_needs_three_images`)
3. **`--source`가 없는 파일 경로** — `FileNotFoundError` → exit 2 (기존 `_read`와 같은 경로). (Task 10, `test_signals_missing_source_file_exits_two`)
4. **fenced block 언어가 `plain text`, `c`, `text`, 없음 모두** — `output-block-smushed-prompts`는 언어 무관으로 발동. (Task 2, `test_smushed_prompts_fires_regardless_of_fence_language`)
5. **노션 escape (`\<stdio.h\>`)와 BOM/전각 공백** — `cell-prefix-repetition`은 `_clean`이 벗긴 뒤 접두를 비교해야 한다. 원문자열의 `\#` 때문에 양성 놓치지 않기. (Task 5, `test_cell_prefix_matches_after_escape_strip`)

## 파일 구조

- **Modify** `.claude/skills/report-audit/scripts/report_md.py`
  — `style_signals()`, `_signal_*` 10개, CLI `signals` subparser. 기존 함수는 건드리지 않는다.
- **Modify** `.claude/skills/report-audit/tests/test_report_md.py`
  — `class SignalTests` 추가(10개 양성·음성 쌍), `class SignalIntegrationTests` 추가(fixture 두 쪽 대조), `class ReviewFocusTests` 추가(위 5개 명시 케이스).
- **Create** `.claude/skills/report-audit/tests/fixtures/hw1_excerpt.md` (≤2 KB)
  — 과제1 보고서에서 함수 셀 두 개 + 캡션 4개 + 실행 블록 1개만 발췌. 학번·이름·외부 S3 URL 제거.
- **Create** `.claude/skills/report-audit/tests/fixtures/hw2_excerpt.md` (≤2 KB)
  — 과제2 보고서에서 함수 셀 두 개 + 반복 캡션 3개 + 실행 블록 1개(안내문 짜붙임 + `EXIT_STATUS` 포함) + 제공/구현 라벨 둘 발췌.
- **Create** `.claude/skills/report-audit/tests/fixtures/hw2_source.c` (≤1 KB)
  — 과제2 HW2.c에서 `allocate_memory`·`find_first_fit` 두 함수만 발췌(NULL/≤0 방어 조건 포함).
- **Modify** `.claude/skills/report-audit/SKILL.md`
  — Workflow 2 뒤에 `signals` 한 줄, Findings 표 맨 아래 `AI 작성 신호 (보고만)` 범주 한 행, "Out of scope: style signals" 섹션 끝에 한 문장만 추가.
- **Modify** `.claude/skills/report-audit/agents/openai.yaml`
  — `short_description` 끝에 "AI 작성 신호 10종 보고" 꼬리 덧붙임.

---

### Task 1: `signals` 서브커맨드 스캐폴드 + 신호 1 `run-script-trace`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Consumes: 기존 `_walk`, `_IMAGE`, `_clean`, `_read`
- Produces:
  - `def style_signals(text: str, source: str | None = None) -> list[tuple[str, str, str]]`
  - CLI: `signals PATH [--source X.c]`, 양성 ≥1이면 exit 1, 0이면 exit 0
  - `_signal_run_script_trace(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

`tests/test_report_md.py` 하단에 `class SignalTests(unittest.TestCase)`를 열고 세 테스트를 추가:

```python
def test_signals_on_empty_file_exits_zero(self):
    self.assertEqual(report_md.style_signals(""), [])

def test_run_script_trace_fires_on_exit_status_and_run_command(self):
    text = "실행:\n```plain text\n$ ./run 01\nALLOC P1 20: SUCCESS\nEXIT_STATUS: 0\n```\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("run-script-trace", names)

def test_run_script_trace_quiet_on_plain_run(self):
    text = "실행:\n```plain text\n$ ./HW2\nALLOC P1 20: SUCCESS\n```\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("run-script-trace", names)
```

`class ReviewFocusTests(unittest.TestCase)`도 같은 단에 열고 한 테스트 추가:

```python
def test_signals_cli_on_empty_file_exits_zero(self):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(""); path = fh.name
    result = subprocess.run(
        [sys.executable, str(Path(report_md.__file__)), "signals", path],
        capture_output=True, text=True,
    )
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, "")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k Signal`
Expected: `AttributeError: module 'report_md' has no attribute 'style_signals'`.

- [ ] **Step 3: Implement scaffold + detector 1 in `scripts/report_md.py`**

파일 상단 상수 영역에 추가:
```python
_RUN_SCRIPT = re.compile(r"(?:^|\s)(\./run\s+\d+|EXIT_STATUS:\s*\d+|hw\d-(?:author-evidence|report-screenshots)[\w-]*|case-?\d+\.(?:txt|tty))")
```
모듈 하단 `_read` 아래에 다음을 추가:

```python
def _signal_run_script_trace(text: str) -> list[tuple[str, str, str]]:
    ...  # _RUN_SCRIPT.finditer(text), 줄 번호 계산, 매치마다 튜플 반환

def style_signals(text: str, source: str | None = None) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    out.extend(_signal_run_script_trace(text))
    return out
```

`main()`의 `sub` 블록에 추가:
```python
signals = sub.add_parser("signals")
signals.add_argument("path")
signals.add_argument("--source", default=None)
```
`main()`의 커맨드 분기 맨 아래(warnings 바로 앞)에 추가:
```python
if args.command == "signals":
    found = style_signals(text, args.source)
    for name, loc, evidence in found:
        print(f"{name}\t{loc}\t{evidence}")
    graded = [row for row in found if row[1] != "skipped"]
    return 1 if graded else 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 신규 테스트 모두 PASS, 기존 테스트도 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): add signals subcommand scaffold with run-script-trace

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 2: 신호 2 `output-block-smushed-prompts`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Consumes: `_walk`, `style_signals`에 디스패치 추가
- Produces: `_signal_output_block_smushed_prompts(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

`SignalTests`에 세 테스트 추가(모두 fenced 안 **연속 두 번 이상** 등장하는 "입력하세요:" 안내문이 입력값 없이 붙어 있으면 양성):

```python
def test_smushed_prompts_fires_on_run_from_captured_output(self):
    text = (
        "```plain text\n"
        "프로세스의 수를 입력하세요. (1~8): 자원의 종류의 개수를 입력하세요. (0~5):\n"
        "Need matrix:\n"
        "```\n"
    )
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("output-block-smushed-prompts", names)

def test_smushed_prompts_fires_regardless_of_fence_language(self):
    for lang in ("", "text", "c", "plain text"):
        text = f"```{lang}\nX를 입력하세요: Y를 입력하세요:\n```\n"
        names = [n for n, _, _ in report_md.style_signals(text)]
        self.assertIn("output-block-smushed-prompts", names, lang)

def test_smushed_prompts_quiet_with_interleaved_input(self):
    text = "```plain text\n프로세스의 수를 입력하세요. (1~8): 2\n자원의 종류를 입력하세요. (0~5): 2\n```\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("output-block-smushed-prompts", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k smushed`
Expected: 처음 두 테스트 FAIL(검출기 없음), 세 번째는 음성 보장으로 PASS.

- [ ] **Step 3: Implement detector 2**

상수:
```python
_PROMPT = re.compile(r"[ㄱ-힝\w\s().~\-]{1,40}입력하세요[^:\n]{0,40}:")
```
알고리즘: fence 안 각 줄에 대해 `_PROMPT.findall(line)` 결과 수 ≥2 이면서, 매치들 사이 구간에 숫자/`[0-9]` 입력값이 없으면 양성 1건. 줄 번호 보고. `style_signals`에 `out.extend(_signal_output_block_smushed_prompts(text))` 추가.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect smushed prompts in output blocks

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 3: 신호 3 `caption-duplication`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Consumes: `_IMAGE`, `style_signals`에 디스패치 추가
- Produces: `_signal_caption_duplication(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_caption_duplication_fires_when_all_three_captions_equal(self):
    text = (
        "![동일 캡션]({u1})\n![동일 캡션]({u1})\n![동일 캡션]({u1})\n"
    ).format(u1="https://example.com/a.png")
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("caption-duplication", names)

def test_caption_duplication_needs_three_images(self):
    text = "![동일]({u})\n![동일]({u})\n".format(u="https://example.com/a.png")
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("caption-duplication", names)

def test_caption_duplication_quiet_when_captions_differ(self):
    text = "\n".join(f"![사례 {i} 설명 {w}]({{u}})" for i, w in enumerate(["push", "pop", "idle"], 1)).format(u="https://example.com/a.png") + "\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("caption-duplication", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k caption_duplication`
Expected: 첫 테스트 FAIL, 둘·셋은 PASS(음성).

- [ ] **Step 3: Implement detector 3**

알고리즘(trigram Jaccard):
```python
def _trigrams(s: str) -> set[str]:
    s = re.sub(r"\s+", " ", s).strip()
    return {s[i:i+3] for i in range(max(0, len(s)-2))}

def _signal_caption_duplication(text):
    caps = [(i+1, m.group(0)[2:m.group(0).index(']')]) for i, m in enumerate(_IMAGE.finditer(text))]
    if len(caps) < 3:
        return []
    grams = [(i, t, _trigrams(t)) for i, t in caps]
    out = []
    for (i1, t1, g1), (i2, t2, g2) in itertools.combinations(grams, 2):
        if not g1 or not g2: continue
        j = len(g1 & g2) / min(len(g1), len(g2))
        if j >= 0.6:
            out.append(("caption-duplication", f"image {i1},{i2}", f"jaccard={j:.2f}"))
    return out
```
`import itertools` 는 파일 상단 import 블록에 추가.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect caption duplication across images

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 4: 신호 4 `cell-prefix-repetition`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Consumes: `_walk` (`prose_cell` 분류), `_clean`, `style_signals`에 디스패치 추가
- Produces: `_signal_cell_prefix_repetition(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_cell_prefix_repetition_fires_on_uniform_intro(self):
    body = "\n".join(
        f"<tr>\n<td>void f{i}(void);</td>\n<td>인자: 없음. 반환값: 없음. 변경 상태: 없음.</td>\n</tr>"
        for i in range(5)
    )
    text = f"<table>\n<tr><td>소스코드</td><td>기능 명세와 분석</td></tr>\n{body}\n</table>\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("cell-prefix-repetition", names)

def test_cell_prefix_matches_after_escape_strip(self):
    body = "\n".join(
        f"<tr>\n<td>#define X{i} 1</td>\n<td>\\#기능 명세 X{i} 상한이다.</td>\n</tr>"
        for i in range(4)
    )
    text = f"<table>\n<tr><td>소스코드</td><td>기능 명세와 분석</td></tr>\n{body}\n</table>\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("cell-prefix-repetition", names)

def test_cell_prefix_quiet_when_intros_vary(self):
    bodies = [
        "인자: 없음. 반환값: 없음.",
        "인자: 큐. 반환값: 1.",
        "front == rear 이면 비었다고 본다.",
        "top == -1 이면 1을 반환한다.",
    ]
    rows = "\n".join(f"<tr>\n<td>f{i}();</td>\n<td>{b}</td>\n</tr>" for i, b in enumerate(bodies))
    text = f"<table>\n<tr><td>소스코드</td><td>기능 명세와 분석</td></tr>\n{rows}\n</table>\n"
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("cell-prefix-repetition", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k cell_prefix`
Expected: 처음 두 테스트 FAIL.

- [ ] **Step 3: Implement detector 4**

알고리즘: `_walk(text)`로 `prose_cell` 셀만 모으고 각 셀의 `_clean(payload)` 결과 앞 10글자를 접두로 삼는다. 전체 셀 수 ≥4이고 같은 접두를 공유하는 셀 비율 ≥0.8이면 양성 1건. `location="prose cells"`, `evidence=f"{shared}/{total} start with {prefix!r}"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect uniform cell prefix across function blocks

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 5: 신호 5 `out-of-scope-vocabulary`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Produces: `_signal_out_of_scope_vocabulary(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_out_of_scope_vocabulary_fires_with_three_hits(self):
    text = "최악은 O(n)이다. 정의되지 않은 동작이다. Best-Fit과 다르다. MSVC 경고."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("out-of-scope-vocabulary", names)

def test_out_of_scope_vocabulary_quiet_below_threshold(self):
    text = "최악은 O(n)이다. 다른 내용은 평범하다."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("out-of-scope-vocabulary", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k out_of_scope_vocabulary`
Expected: 첫 FAIL, 둘 PASS.

- [ ] **Step 3: Implement detector 5**

상수:
```python
_OUT_OF_SCOPE = (
    (r"O\(\s*[nN1]\s*\)", "O(n)"),
    (r"정의되지\s*않은\s*동작", "정의되지 않은 동작"),
    (r"(?i)undefined\s+behavior", "undefined behavior"),
    (r"Best-?Fit|Worst-?Fit", "Best/Worst-Fit"),
    (r"MSVC", "MSVC"),
    (r"ISO\s*C", "ISO C"),
    (r"외부\s*단편화", "외부 단편화"),
)
```
알고리즘: 각 패턴별 `re.findall` 합을 구해 총합 ≥3이면 양성 1건. `evidence=f"count={total}; "+"/".join(labels_with_hits)`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect out-of-scope vocabulary

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 6: 신호 6 `no-personal-voice`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Produces: `_signal_no_personal_voice(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_no_personal_voice_fires_on_prose_without_markers(self):
    text = "함수는 1을 반환한다. 성공하면 상태가 바뀐다. 실패하면 유지한다." * 8
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("no-personal-voice", names)

def test_no_personal_voice_quiet_when_any_marker_present(self):
    text = "함수는 1을 반환한다. 처음에 헷갈렸다. 이후 수정했다."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("no-personal-voice", names)

def test_no_personal_voice_quiet_on_short_text(self):
    text = "짧다."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("no-personal-voice", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k personal_voice`
Expected: 첫 FAIL, 둘·셋 PASS.

- [ ] **Step 3: Implement detector 6**

상수:
```python
_VOICE = re.compile(r"나는|내가|처음에|헷갈|시행착오|고쳤|수정했|생각했|이해했|보았다|느낀|어려|막혔|놓쳤|배운")
```
알고리즘: `prose_lines(text)` 결과를 이어붙여 산문 길이가 400자 미만이면 신호를 내지 않는다(음성). 그 이상이면서 `_VOICE.search`가 None이면 양성 1건. `location="whole prose"`, `evidence=f"prose_chars={n}, markers=0"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect absence of personal voice in prose

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 7: 신호 7 `evaluation-report-vocabulary`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Produces: `_signal_evaluation_report_vocabulary(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_evaluation_vocabulary_fires_with_five_hits(self):
    text = (
        "표준 출력 원문. 관찰한 메모리 지도. 실제 결과는. 검증했다. 하네스."
    )
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("evaluation-report-vocabulary", names)

def test_evaluation_vocabulary_quiet_below_threshold(self):
    text = "실제 출력은 정상이었다."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("evaluation-report-vocabulary", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k evaluation`
Expected: 첫 FAIL, 둘 PASS.

- [ ] **Step 3: Implement detector 7**

상수 `_EVAL = (r"표준\s*출력\s*원문", r"관찰한", r"실제\s*결과", r"검증했", r"하네스", r"(?i)sanitizer", r"링크\s*검사")`. 총 매치 ≥5이면 양성 1건. `evidence=f"count={total}"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect evaluation-report vocabulary

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 8: 신호 8 `third-person-rubric-echo`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Produces: `_signal_third_person_rubric_echo(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_rubric_echo_fires_with_two_hits(self):
    text = "추가 함수는 만들지 않았다. 주어진 함수 형식을 유지한다."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("third-person-rubric-echo", names)

def test_rubric_echo_quiet_with_one_hit(self):
    text = "추가 함수는 만들지 않았다. 다음은 다른 이야기다."
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertNotIn("third-person-rubric-echo", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k rubric_echo`
Expected: 첫 FAIL, 둘 PASS.

- [ ] **Step 3: Implement detector 8**

상수:
```python
_RUBRIC = (
    r"추가\s*함수는\s*만들지\s*않",
    r"주어진\s*함수\s*형식.{0,8}유지",
    r"요구사항.{0,4}(?:충족|확인)",
    r"제공.{0,4}함수.{0,12}(?:유지|변경하지)",
)
```
총 매치 ≥2이면 양성 1건. `evidence=f"count={total}"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect third-person rubric echo

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 9: 신호 9 `provided-vs-implemented-parity`

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Consumes: `_walk`, `_clean`
- Produces: `_signal_provided_vs_implemented_parity(text: str) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_parity_fires_when_both_groups_long_and_similar(self):
    long_body = "설명. " * 100  # ~400 chars per cell
    rows = []
    for label in ("제공 함수", "제공 함수", "구현 대상 함수", "구현 대상 함수"):
        rows.append(f"## {label}\n<table>\n<tr><td>소스코드</td><td>기능 명세와 분석</td></tr>\n<tr><td>code</td><td>{long_body}</td></tr>\n</table>\n")
    text = "\n".join(rows)
    names = [n for n, _, _ in report_md.style_signals(text)]
    self.assertIn("provided-vs-implemented-parity", names)

def test_parity_quiet_when_provided_is_terse(self):
    long_body = "설명. " * 100
    rows = [
        "## 제공 함수\n<table>\n<tr><td>소스코드</td><td>기능 명세와 분석</td></tr>\n<tr><td>code</td><td>짧다.</td></tr>\n</table>\n",
        f"## 구현 대상 함수\n<table>\n<tr><td>소스코드</td><td>기능 명세와 분석</td></tr>\n<tr><td>code</td><td>{long_body}</td></tr>\n</table>\n",
    ]
    names = [n for n, _, _ in report_md.style_signals("\n".join(rows))]
    self.assertNotIn("provided-vs-implemented-parity", names)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k parity`
Expected: 첫 FAIL, 둘 PASS.

- [ ] **Step 3: Implement detector 9**

알고리즘: `text`를 줄 기준으로 훑으며 가장 가까운 상위 Markdown 소제목(`##`, `###`)을 기록해 두고, 각 `prose_cell`을 그 소제목 레이블로 묶는다. 레이블에 "제공"이 있으면 그룹 `P`, "구현" 또는 "학생"이 있으면 그룹 `I`. `_clean`한 셀 길이의 중앙값을 두 그룹에서 구해 둘 다 ≥400이고 `min/max ≥ 0.9`면 양성 1건. `evidence=f"P_median={pm}, I_median={im}, ratio={r:.2f}"`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect provided/implemented parity in cell length

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 10: 신호 10 `source-out-of-scope-guards` (opt-in `--source`)

**Files:**
- Modify: `.claude/skills/report-audit/scripts/report_md.py`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`

**Interfaces:**
- Consumes: `_read`, `style_signals`에 `source` 전달
- Produces: `_signal_source_out_of_scope_guards(source: str | None) -> list[tuple[str, str, str]]`

- [ ] **Step 1: Write the failing tests**

```python
def test_guards_skipped_when_no_source(self):
    rows = report_md.style_signals("")
    self.assertIn(("source-out-of-scope-guards", "skipped", "--source not given"), rows)

def test_guards_fire_on_defensive_conditions(self):
    source = (
        "int allocate(List *l, int pid, int size)\n"
        "{\n"
        "    if (l == NULL || pid <= 0 || size <= 0) { return 0; }\n"
        "    return 1;\n"
        "}\n"
    )
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".c", delete=False) as fh:
        fh.write(source); src = fh.name
    text = ""
    names_locs = [(n, l) for n, l, _ in report_md.style_signals(text, src)]
    self.assertIn(("source-out-of-scope-guards", "function allocate"), names_locs)

def test_signals_missing_source_file_exits_two(self):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(""); report = fh.name
    result = subprocess.run(
        [sys.executable, str(Path(report_md.__file__)), "signals", report, "--source", "/no/such/file.c"],
        capture_output=True, text=True,
    )
    self.assertEqual(result.returncode, 2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k guards`
Expected: 첫·둘 FAIL (검출기 없음), 셋은 `_read`가 던지므로 지금 PASS지만 포함.

- [ ] **Step 3: Implement detector 10**

알고리즘: `source is None`이면 `[("source-out-of-scope-guards", "skipped", "--source not given")]` 반환. 아니면 `re.finditer(r"^\s*\w[\w\s*]*\s+(\w+)\s*\([^)]*\)\s*\n\s*\{", source, re.M)`로 함수 정의를 찾고, 그 함수 본문 첫 15줄 안에서 `re.findall(r"(\w+)\s*(?:==\s*NULL|<=\s*0|<\s*0)", block)`의 수 ≥2 이면 양성 1건, `location=f"function {name}"`, `evidence=f"guards={hits}"`.

`style_signals`에 디스패치 추가:
```python
if source is None:
    guard_rows = [("source-out-of-scope-guards", "skipped", "--source not given")]
else:
    try:
        guard_rows = _signal_source_out_of_scope_guards(_read(source))
    except FileNotFoundError:
        raise
out.extend(guard_rows)
```
`main()`의 `signals` 분기는 `style_signals(text, args.source)`로 호출. `FileNotFoundError`는 기존 `except (FileNotFoundError, ValueError)`가 받아 exit 2.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: 모두 PASS.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/report-audit/scripts/report_md.py .claude/skills/report-audit/tests/test_report_md.py
git commit -m "$(cat <<'MSG'
feat(report-audit): detect out-of-scope defensive guards in source

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

### Task 11: Fixture 발췌 + 통합 테스트 + SKILL.md·agents yaml 갱신

**Files:**
- Create: `.claude/skills/report-audit/tests/fixtures/hw1_excerpt.md`
- Create: `.claude/skills/report-audit/tests/fixtures/hw2_excerpt.md`
- Create: `.claude/skills/report-audit/tests/fixtures/hw2_source.c`
- Modify: `.claude/skills/report-audit/tests/test_report_md.py`
- Modify: `.claude/skills/report-audit/SKILL.md`
- Modify: `.claude/skills/report-audit/agents/openai.yaml`

**Interfaces:**
- Consumes: Task 1~10의 `style_signals`
- Produces: 눈금 회귀(`class SignalIntegrationTests`)로 과제1 ≤2, 과제2 ≥8 양성 보장

- [ ] **Step 1: 과제1·과제2 보고서에서 발췌 fixture를 작성한다**

각 fixture는 2 KB 이내. 학번·이름·외부 S3 URL은 제거하고 placeholder(`학번 000000000`, `https://example.com/img.png`)로 치환한다.

`hw2_excerpt.md`에 반드시 포함할 것:
- 함수 셀 4개(모두 `인자: ... 반환값: ... 변경 상태: ...` 접두) — 신호 4
- 반복 캡션 3장(`![터미널의 실제 실행 화면. 명령별 처리 결과와 메모리 지도를 보여 준다.](https://example.com/img.png)`) — 신호 3
- `./run 03`과 `EXIT_STATUS: 0`을 포함한 fenced block 1개 — 신호 1
- 안내문이 입력값 없이 한 줄에 붙은 fenced block 1개 — 신호 2
- 산문 400자 이상, 1인칭 어휘 0 — 신호 6
- "표준 출력 원문" ·"관찰한 메모리 지도"·"실제 결과"·"검증했다"·"하네스" 각 1회 이상 — 신호 7
- "추가 함수는 만들지 않았다"·"주어진 함수 형식을 유지한다" 각 1회 — 신호 8
- `## 제공 함수`·`## 구현 대상 함수` 소제목 각 2개, 각 셀 400자 이상이고 길이 비슷 — 신호 9
- "O(n)"·"정의되지 않은 동작"·"Best-Fit"·"MSVC" 포함 — 신호 5

`hw1_excerpt.md`에 반드시 포함할 것:
- 글머리표 산문, 영어 괄호는 몇 개 있으나 "O(n)"/"정의되지 않은 동작"은 없음
- 서로 다른 캡션 4개(Jaccard < 0.4)
- 실행 블록에 `./HW1`만, `EXIT_STATUS` 없음
- 안내문과 입력값이 번갈아 있는 블록 1개
- 1인칭 어휘 ≥2 포함("처음에"·"수정했")
- "추가 함수"·"주어진 함수 형식" 같은 rubric echo 없음

`hw2_source.c`에 `find_first_fit`, `allocate_memory` 두 함수 발췌(NULL·<=0 조건 포함).

- [ ] **Step 2: 실패하는 통합·리뷰 포커스 테스트를 쓴다**

`class SignalIntegrationTests(unittest.TestCase)`와 `class ReviewFocusTests` 확장:

```python
FIXTURES = Path(__file__).resolve().parent / "fixtures"

class SignalIntegrationTests(unittest.TestCase):
    def test_hw2_triggers_at_least_eight(self):
        text = (FIXTURES / "hw2_excerpt.md").read_text(encoding="utf-8")
        source = str(FIXTURES / "hw2_source.c")
        names = {n for n, loc, _ in report_md.style_signals(text, source) if loc != "skipped"}
        self.assertGreaterEqual(len(names), 8, sorted(names))

    def test_hw1_triggers_at_most_two(self):
        text = (FIXTURES / "hw1_excerpt.md").read_text(encoding="utf-8")
        names = {n for n, loc, _ in report_md.style_signals(text) if loc != "skipped"}
        self.assertLessEqual(len(names), 2, sorted(names))

    def test_signals_cli_tab_separated_lines(self):
        import tempfile
        text = (FIXTURES / "hw2_excerpt.md").read_text(encoding="utf-8")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
            fh.write(text); report = fh.name
        result = subprocess.run(
            [sys.executable, str(Path(report_md.__file__)), "signals", report],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        for line in result.stdout.splitlines():
            self.assertEqual(line.count("\t"), 2)
```

- [ ] **Step 3: 테스트 실행해 FAIL 확인**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v -k Integration`
Expected: FAIL (fixture가 없거나 임계값 못 맞춤).

- [ ] **Step 4: Fixture 내용 조정해 PASS 보장**

`style_signals(text)`를 직접 돌려가며 각 신호가 의도대로 발동/침묵하는지 확인한 뒤 fixture를 다듬는다. 실제 과제 원문의 문구를 **옮겨 쓰되** 다섯 줄 이내로 압축. 원문에 없는 내용을 지어내지 않는다.

Run: `python3 -c "import sys; sys.path.insert(0, '.claude/skills/report-audit/scripts'); import report_md; print([r for r in report_md.style_signals(open('.claude/skills/report-audit/tests/fixtures/hw2_excerpt.md').read(), '.claude/skills/report-audit/tests/fixtures/hw2_source.c')])"`
Expected: 10개 신호 중 양성(skipped 제외) 이름 종류 ≥8.

- [ ] **Step 5: SKILL.md와 agents yaml을 갱신한다**

`SKILL.md`:

- Workflow 2 바로 뒤에 새 bullet 하나:
  > `python3 .claude/skills/report-audit/scripts/report_md.py signals FILE [--source X.c]` — 과제2에서 밝혀낸 AI 작성 신호 10종을 보고한다. 자동 수정하지 않는다.
- "## Findings table (all categories required)" 표 맨 아래 한 행 추가:

  | 범주 | What to check | Example from this course |
  |---|---|---|
  | AI 작성 신호 (보고만) | `signals` 10종. 양성 이름·위치·수치를 그대로 옮기고, 수정 제안은 쓰지 않는다. `source-out-of-scope-guards`는 `--source` 지정 시에만. | 과제2: `run-script-trace` 24건, `output-block-smushed-prompts` 6건, `caption-duplication` 6/6, `no-personal-voice` whole prose |
- "## Out of scope: style signals" 섹션 **본문은 그대로 유지**, 맨 끝에 한 문장만 추가:
  > 다만 검출(`signals`)은 저자가 제출 전 공개·수정할 수 있도록 허용한다. 스킬 자체가 재작성하거나 신호 문구를 "자연스럽게" 바꾸지 않는다.

`agents/openai.yaml`의 `short_description` 뒤에 `+ AI 작성 신호 10종 보고` 꼬리 덧붙임.

- [ ] **Step 6: 전체 테스트 실행해 PASS 확인**

Run: `python3 -m unittest .claude/skills/report-audit/tests/test_report_md.py -v`
Expected: `Ran N tests ... OK` (N ≥ 25).

- [ ] **Step 7: Commit**

```bash
git add .claude/skills/report-audit/tests/fixtures .claude/skills/report-audit/tests/test_report_md.py .claude/skills/report-audit/SKILL.md .claude/skills/report-audit/agents/openai.yaml
git commit -m "$(cat <<'MSG'
test(report-audit): pin signals on hw1/hw2 fixtures and update skill docs

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
MSG
)"
```

---

## Self-Review

- **Spec coverage**: 설계의 Confident 1·2·3·7·8·9·10과 Needs you 4·5·6을 Global Constraints로 흡수했다. 설계 "신호 10종"은 Task 1~10에 1:1로 대응한다. SKILL.md 문구 변경, 결과 포맷(탭 구분), exit 코드, `--source` opt-in도 각 Task에 들어 있다. 설계 "신호 재작성 금지" 정책은 SKILL.md Task 11 Step 5의 한 문장 추가와 Global Constraints "수정 금지"로 두 번 못 박았다. 빠진 항목 없음.
- **Step scan**: 각 단계는 테스트 하나의 이름/본문, 실행 커맨드/기대 출력, 함수 시그니처 하나, 커밋 하나로 끝난다. 알고리즘이 모호한 세 신호(caption-duplication·cell-prefix-repetition·parity·source-guards)에만 코드 블록을 붙였고 나머지는 상수 + 임계값 + 한 줄 설명이다. "여기 추가" 같은 모호한 지시 없음.
- **Type consistency**: `style_signals(text, source=None)`이 Task 1~10 전부에서 같은 시그니처로 호출된다. 반환은 `list[tuple[str, str, str]]`로 고정, 신호 이름 10개는 Global Constraints 표가 결정한다. `_signal_*` 내부 함수들은 모두 `text`(또는 `source`) 한 인자를 받는다.
- **Review Focus**: 5개 모두 명시된 Task의 테스트 이름까지 못 박았다. Task 1의 `test_signals_on_empty_file_exits_zero`·`test_signals_cli_on_empty_file_exits_zero`, Task 4의 `test_caption_duplication_needs_three_images`, Task 10의 `test_signals_missing_source_file_exits_two`, Task 2의 `test_smushed_prompts_fires_regardless_of_fence_language`, Task 4의 `test_cell_prefix_matches_after_escape_strip`.
- **Proportion**: 설계 ~4 KB, 계획 ~14 KB. 신호 10개에 각각 테스트·시그니처·커밋이 들어가므로 3.5배는 과하지 않다. 코드 블록은 알고리즘이 안 보이는 네 곳에만.

Plan complete and saved to `docs/superpowers/plans/2026-11-12-report-audit-signals.md`. Please review the plan. Which execution approach would you prefer?

- **Subagent-driven** — A fresh subagent implements each task and a fresh reviewer checks it before the next one starts, then a whole-branch review at the end. Most thorough; costs a fresh context per task and per review.
- **Native** — I implement every task myself in this session, the way this harness runs work, then one fresh reviewer on the most capable model checks the whole branch. Cheapest and fastest; no independent review until the end. Runs well with a mid-tier session model, since the plan carries the design.

**For this plan I recommend Native**, because the 11 tasks share a single file and a single contract (`style_signals`), each task is ≤25 lines of regex-and-threshold code gated by a tight unit test, and a slip would just be a flaky detector a later fixture catches — not something a reviewer per task would meaningfully gate. Does the plan capture what you want, and which approach should we use?
