# 복습팩 → 확인문제 연결 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/ds-review-pack MMDD` 신규 팩 생성이 8단계 PDF 다음에 `ds-concept-check`를 돌려 확인문제 HTML까지 내게 한다.

**Architecture:** 코드 변경은 `assemble.py` 하나 — 조립할 때마다 `RUN/manifest.json`과 `RUN/summaries/stt-*.md`(이어 붙임)를 팩의 `.pack/자료_복습팩/`에 써서 확인문제의 근거를 보장한다. 나머지는 두 SKILL.md의 절차 문서 변경이고, `test_skill_files.py`가 순서·문구를 고정한다.

**Tech Stack:** Python 3 표준 라이브러리, unittest(pytest로 실행).

**Spec:** `docs/superpowers/specs/2026-11-13-review-pack-concept-check-link-design.md`

## Global Constraints

- 확인문제는 신규 모드(`MMDD`·`MMDD-MMDD`, `lite` 포함)만. `bank`·`update-existing`·`revise-existing`은 만들지도 건드리지도 않는다.
- `lite`도 확인문제를 생략하지 않고 모델(opus)도 바꾸지 않는다.
- 8단계 순서: MD 변환 → 문제설명(`references/problem-explain.md`) → PDF(`references/pdf-build.md`) → 확인문제 → `pack_layout.py check`.
- 확인문제 실패는 "복습팩 생성됨 / 확인문제 보류"로 격리한다. 복습팩·문제설명·PDF는 되돌리지 않는다.
- 여러 날짜 요약은 `stt-*.md` 파일 이름순, 구분자 `\n\n---\n\n`.
- 저장소 문서·주석은 한국어. 커밋 메시지 끝에 `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- 테스트 실행: 저장소 루트에서 homebrew `python3 -m pytest .agents/skills/ds-review-pack/tests/<파일> -q`.
- 함정: `ds-review-pack/SKILL.md`의 `test_referenced_files_exist`는 `(references|scripts|assets)/<이름>.(md|py|html)` 꼴 문자열을 **이 스킬 폴더 기준**으로 존재 검사한다. 확인문제 스킬의 파일을 적을 때 `scripts/check.py`·`references/item-rules.md` 같은 꼴을 쓰지 않는다(`ds-concept-check/SKILL.md`와 "그 `scripts`의 `check.py`"처럼 쓴다).

## Review Focus

1. 같은 RUN으로 5~8단계에서 다시 조립 — `stt-summary.md`·`manifest.json`이 최신 RUN 내용으로 덮여야 한다(Task 1 `test_pack_sources_overwrite`).
2. `RUN/summaries/`가 없거나 비어 있음(요약 에이전트 실패) — 조립은 성공하고, 팩에 이미 있던 `stt-summary.md`는 지우지 않는다(Task 1 `test_no_summaries_keeps_existing`).
3. 날짜가 여러 개인 범위 — 이름순으로 이어지고 각 날짜 내용이 빠짐없이 들어간다(Task 1 `test_multi_date_summaries_joined`).
4. SKILL.md에 확인문제 스킬 파일 경로를 적다가 존재 검사 오탐 — Global Constraints의 함정. Task 2가 전체 `test_skill_files.py`를 돌려 잡는다.
5. 확인문제 단계가 8단계 안에서 PDF 앞이나 `pack_layout` 뒤로 놓임 — Task 2 `test_concept_check_after_pdf_before_layout`.

---

### Task 1: 조립이 확인문제 근거를 팩에 쓴다

**Files:**
- Modify: `.agents/skills/ds-review-pack/scripts/assemble.py:106-122`(`assemble()` 끝의 traces 복사 옆)
- Test: `.agents/skills/ds-review-pack/tests/test_assemble.py`

**Interfaces:**
- Produces: `copy_pack_sources(run_dir: Path, out_dir: Path) -> None` (assemble.py). `assemble()`이 두 HTML을 쓴 뒤 호출한다. 동작:
  - `out_dir/.pack/자료_복습팩/`을 만들고 `run_dir/manifest.json`을 바이트 그대로 `manifest.json`으로 복사(덮어씀).
  - `sorted(run_dir.glob("summaries/stt-*.md"))`가 비어 있지 않으면 각 파일 `read_text(encoding="utf-8").rstrip("\n")`를 `"\n\n---\n\n"`으로 이어 끝에 `"\n"`을 붙여 `stt-summary.md`로 쓴다(덮어씀). 비어 있으면 `stt-summary.md`를 쓰지도 지우지도 않는다.
- Consumes: 없음.

- [ ] **Step 1: 실패하는 테스트를 쓴다**

`test_assemble.py`에서:
- `test_no_traces_dir_creates_nothing`을 `test_no_traces_dir_creates_no_traces`로 바꾸고 단언을 `self.assertFalse((self.tmp / ".pack" / "자료_복습팩" / "traces").exists())`로 고친다(이제 manifest는 항상 복사되므로 `자료_복습팩` 폴더 자체는 생긴다).
- 새 테스트(각각 `shutil.copytree(MINI_RUN, self.tmp / "run")`으로 RUN 사본을 만들어 쓴다):

```python
    def _run_with(self, summaries: dict[str, str]) -> Path:
        run = self.tmp / "run"
        shutil.copytree(MINI_RUN, run)
        if summaries:
            (run / "summaries").mkdir()
            for name, text in summaries.items():
                (run / "summaries" / name).write_text(text, encoding="utf-8")
        return run

    def test_manifest_copied(self):
        dest = self.tmp / ".pack" / "자료_복습팩" / "manifest.json"
        self.assertEqual(dest.read_bytes(), (MINI_RUN / "manifest.json").read_bytes())

    def test_single_summary_copied(self):
        run = self._run_with({"stt-0101.md": "# 0101 요약\n\n본문\n"})
        out = self.tmp / "o1"
        assemble.assemble(run, out)
        got = (out / ".pack" / "자료_복습팩" / "stt-summary.md").read_text(encoding="utf-8")
        self.assertEqual(got, "# 0101 요약\n\n본문\n")

    def test_multi_date_summaries_joined(self):
        run = self._run_with({"stt-0102.md": "# 0102\nB\n\n", "stt-0101.md": "# 0101\nA\n"})
        out = self.tmp / "o2"
        assemble.assemble(run, out)
        got = (out / ".pack" / "자료_복습팩" / "stt-summary.md").read_text(encoding="utf-8")
        self.assertEqual(got, "# 0101\nA\n\n---\n\n# 0102\nB\n")

    def test_no_summaries_keeps_existing(self):
        run = self._run_with({})
        out = self.tmp / "o3"
        dest = out / ".pack" / "자료_복습팩"
        dest.mkdir(parents=True)
        (dest / "stt-summary.md").write_text("옛 요약\n", encoding="utf-8")
        assemble.assemble(run, out)
        self.assertEqual((dest / "stt-summary.md").read_text(encoding="utf-8"), "옛 요약\n")
        self.assertTrue((dest / "manifest.json").exists())

    def test_pack_sources_overwrite(self):
        run = self._run_with({"stt-0101.md": "새 요약\n"})
        out = self.tmp / "o4"
        dest = out / ".pack" / "자료_복습팩"
        dest.mkdir(parents=True)
        (dest / "stt-summary.md").write_text("옛 요약\n", encoding="utf-8")
        (dest / "manifest.json").write_text("{}", encoding="utf-8")
        assemble.assemble(run, out)
        self.assertEqual((dest / "stt-summary.md").read_text(encoding="utf-8"), "새 요약\n")
        self.assertEqual((dest / "manifest.json").read_bytes(), (run / "manifest.json").read_bytes())
```

- [ ] **Step 2: 실패를 확인한다**

Run: `python3 -m pytest .agents/skills/ds-review-pack/tests/test_assemble.py -q`
Expected: 새 테스트 5개와 바꾼 traces 테스트 중 manifest·summary 관련이 FAIL(파일 없음).

- [ ] **Step 3: `copy_pack_sources`를 구현하고 `assemble()`에서 호출한다**

traces 복사 블록 바로 뒤에서 호출한다. 주석 한 줄: 확인문제(`ds-concept-check`)가 이 두 파일을 근거로 읽는다.

- [ ] **Step 4: 통과를 확인한다**

Run: `python3 -m pytest .agents/skills/ds-review-pack/tests/test_assemble.py .agents/skills/ds-review-pack/tests/test_pack_layout.py -q`
Expected: 모두 PASS.

- [ ] **Step 5: 커밋**

```bash
git add .agents/skills/ds-review-pack/scripts/assemble.py .agents/skills/ds-review-pack/tests/test_assemble.py
git commit -m "feat(ds-review-pack): assemble writes manifest and STT summary into pack data"
```

---

### Task 2: 복습팩 8단계에 확인문제 절차를 넣는다

**Files:**
- Modify: `.agents/skills/ds-review-pack/SKILL.md`(산출물·`lite`·"해설 연결" 옆·8단계·9단계·오류 처리)
- Modify: `.agents/skills/ds-concept-check/SKILL.md`(도입부 한 줄)
- Test: `.agents/skills/ds-review-pack/tests/test_skill_files.py`

**Interfaces:**
- Consumes: Task 1 — 4단계 조립이 `.pack/자료_복습팩/manifest.json`·`stt-summary.md`를 쓴다(문서에서 이 사실을 근거로 든다).
- Produces: 없음(문서).

- [ ] **Step 1: 실패하는 테스트를 쓴다** (`TestSkillFiles`에 추가)

```python
    def _step8(self):
        return self.text.split("\n### 8. ", 1)[1].split("\n### 9. ", 1)[0]

    def test_concept_check_after_pdf_before_layout(self):
        s8 = self._step8()
        self.assertLess(s8.index("references/pdf-build.md"), s8.index("ds-concept-check/SKILL.md"))
        self.assertLess(s8.index("ds-concept-check/SKILL.md"), s8.index("pack_layout.py check"))

    def test_concept_check_scope_and_failure(self):
        self.assertTrue((SKILL.parent / "ds-concept-check" / "SKILL.md").exists())
        self.assertIn("**확인문제 연결**", self.text)
        self.assertIn("`update-existing`·`revise-existing`은 확인문제를 만들지 않고", self.text)
        self.assertIn("복습팩 생성됨 / 확인문제 보류", self.text)
        self.assertIn("| 확인문제 스킬 누락 |", self.text)
        self.assertIn("| 확인문제 검사 실패 |", self.text)
        self.assertIn("- 확인문제:", self.text.split("\n### 9. ", 1)[1])
        self.assertIn("stt-summary.md", self.text.split("\n### 9. ", 1)[1])
```

- [ ] **Step 2: 실패를 확인한다**

Run: `python3 -m pytest .agents/skills/ds-review-pack/tests/test_skill_files.py -q`
Expected: 새 테스트 2개 FAIL.

- [ ] **Step 3: `ds-review-pack/SKILL.md`를 고친다**

고정 문구(그대로 쓴다):

1. **산출물** 루트 줄에 `확인문제_<range>_<slug>.html`(신규 모드만)을, `.pack/` 줄에 `자료_확인문제_<range>_<slug>/`를 더한다.
2. **인자**의 `lite` 줄 "생략하지 않는다" 목록에 `확인문제(작성자·블라인드 풀이자 opus, 검사 전부)`를 더한다.
3. "해설 연결" 문단 바로 뒤에 새 문단:
   > **확인문제 연결**: 신규 모드(`MMDD`·`MMDD-MMDD`, `lite` 포함)만 확인문제를 만든다. `bank`·`update-existing`·`revise-existing`은 확인문제를 만들지 않고 기존 확인문제도 건드리지 않는다. 신규 모드는 생성 시작 전에 형제 `ds-concept-check/SKILL.md`와 그 `scripts` 폴더의 `check.py`·`build.py`·`blind.py`·`browser_check.py`가 있는지 확인하고, 하나라도 없으면 경로를 보고하고 시작하지 않는다.
4. 8단계에서 PDF 문단 뒤, "마지막으로 폴더 배치를 검사한다" 앞에 새 문단:
   > - 신규 모드면 이어서 확인문제를 만든다. 진행 표시는 `8/9 확인문제 중: <확인문제 단계>`. 형제 `ds-concept-check/SKILL.md`를 읽고 그 1~8단계를 이 팩의 `range`로 실제로 따른다. 근거인 `.pack/자료_복습팩/manifest.json`·`stt-summary.md`는 4단계 조립이 이미 써 두었다. 확인문제의 `RUN`(`<scratchpad>/ds-concept-check/<range>/`)은 이 스킬의 `RUN`과 따로 둔다. 그 스킬의 규칙 검사·블라인드 풀이(r3까지)·브라우저 검사·배치 검사 중 하나라도 끝내 통과하지 못하면 새 확인문제 HTML과 `자료_확인문제_*` 폴더를 확인문제 `RUN/withheld-<시각>/`으로 옮기고, 그 스킬 1단계 백업(있으면)을 제자리로 되돌린 뒤 "복습팩 생성됨 / 확인문제 보류"로 보고한다. 복습팩·문제설명·PDF는 되돌리지 않는다.
5. 9단계 보고 제목 괄호에 `확인문제 보류 시: 복습팩 생성됨 / 확인문제 보류`를 더하고, `- PDF:` 줄 다음에:
   > `- 확인문제: 발행/보류, 목표 n·문항 n(객관식 n·입력 n), 블라인드 회차별 일치, 브라우저 pass/fail, HTML·SRC·확인문제 RUN·백업 경로, 보류 이유`

   저장 목록 문장에 `stt-summary.md(4단계 조립이 쓴다)`를 더한다.
6. 오류 처리 표에 두 행:
   > `| 확인문제 스킬 누락 | 신규 모드 생성 시작 전에 경로를 보고하고 중단 |`
   > `| 확인문제 검사 실패 | 새 확인문제를 확인문제 RUN의 withheld-<시각>/으로 옮기고 이전 확인문제를 되돌린 뒤 “복습팩 생성됨 / 확인문제 보류”와 이유 보고; 복습팩·문제설명·PDF는 유지 |`

- [ ] **Step 4: `ds-concept-check/SKILL.md` 도입부 첫 문단 뒤 목록 첫 줄에 더한다**

> - `ds-review-pack` 신규 모드가 8단계에서 이 절차(1~8단계)를 팩마다 부른다. 단독 실행(`/ds-concept-check <range>`)도 그대로 쓴다.

- [ ] **Step 5: 통과를 확인한다**

Run: `python3 -m pytest .agents/skills/ds-review-pack/tests/test_skill_files.py .agents/skills/ds-concept-check/tests -q`
Expected: 모두 PASS(특히 `test_referenced_files_exist` — 함정 문구가 없어야 한다).

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/ds-review-pack/SKILL.md .agents/skills/ds-review-pack/tests/test_skill_files.py .agents/skills/ds-concept-check/SKILL.md
git commit -m "docs(ds-review-pack): run concept check after PDF in new packs"
```

---

### 마무리 검증

- [ ] Run: `python3 -m pytest .agents/skills/ds-review-pack/tests/test_assemble.py .agents/skills/ds-review-pack/tests/test_skill_files.py .agents/skills/ds-review-pack/tests/test_pack_layout.py .agents/skills/ds-concept-check/tests -q`
  Expected: 모두 PASS. 실제 신규 팩 실행(다음 수업 STT가 생긴 뒤 `/ds-review-pack <MMDD>`)은 이 계획 범위 밖이며, 그때 확인문제 줄이 보고에 나오는지 본다.
