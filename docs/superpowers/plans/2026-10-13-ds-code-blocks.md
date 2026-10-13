# 문제설명 코드 블록 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 모든 기존 문제설명 HTML의 독립 코드와 실행결과를 시각적으로 분리하고, 스킬·템플릿·검증을 함께 수정해 이후 생성에서도 유지한다.

**Architecture:** 기존 `<pre><code>` 구조에 공통 템플릿 스타일을 적용한다. 설명 조각의 코드 구조를 검사하고 기존 extract/build/check/publish 경로로 전체 팩을 갱신한다. 자동으로 일반 문장에서 코드를 추측해 분리하는 기능은 만들지 않는다.

**Tech Stack:** Python 3.10 이상, 표준 라이브러리 HTML 파서, pytest, HTML/CSS, 로컬 KaTeX/Pretendard.

**Spec:** 이 파일의 [확정 설계](#확정-설계). 대화에서 사용자가 전체 날짜 적용과 독립 코드·실행결과 블록화, 인라인 코드 유지를 확정했다.

## Global Constraints

- 모든 작업은 `/Users/hyunjun_macbook_pro/.codex/worktrees/ds-code-blocks/자구알`, 브랜치 `codex/ds-code-blocks`에서 수행한다. main에 다른 세션이 작업 중이다.
- 원 문제 HTML/MD, 정리노트, PDF, 그림 원본, 문제은행은 수정하지 않는다.
- 코드 내용·공백·들여쓰기·줄바꿈·연산 순서를 보존한다. `<`, `&`, `$`를 수식이나 HTML 태그로 재해석하지 않는다.
- 문장 속 짧은 코드는 인라인으로 유지한다. 실행결과는 코드와 같은 블록 스타일을 사용한다.
- 접기, 복사 버튼, 구문 강조, 외부 폰트/라이브러리는 추가하지 않는다.
- 실제 검토 없이 pass를 기록하지 않는다. 새 build의 not_run 검토를 기존 pass 기록으로 덮어쓰지 않는다.
- merge, push, main 이동은 이 계획의 실행 범위가 아니다. 작업별 커밋은 구현 실행이 승인되면 워크트리 브랜치에서 수행한다.

## Review Focus

1. 매우 긴 코드 줄: 문서 전체가 늘어나지 않고 pre 내부에서만 스크롤한다 — Task 1 브라우저 검사.
2. `<`, `&`, `$`, 탭과 빈 줄이 섞인 C 코드: HTML/MD에서 문자와 공백이 보존된다 — Task 1 회귀 테스트.
3. 문장 속 `head`와 한 줄 코드: 인라인 표기는 유지하고 한 줄 pre도 독립 블록이다 — Task 2 구조 테스트, Task 1 시각 검사.
4. 실행결과와 코드 없는 문항: 실행결과는 동일한 블록, 코드 없는 문항에는 빈 블록이 없다 — Task 1 렌더 테스트, Task 3 전체 검사.
5. 워크트리 재생성: 이전 checkout의 절대 경로와 과거 검토가 새 발행을 잘못 승인하지 않는다 — Task 3 경로·발행 검사.

---

## 확정 설계

기존 `복습노트/*/문제설명_*.html` 전체와 이후 생성에 적용한다. pre 자체를 블록으로 사용하며 배경은 `var(--surface)`, 글자색은 `var(--ink)`, 테두리는 `1px solid var(--line)`, 패딩은 `var(--s4)`(16px), 반경은 `var(--radius)`(8px), 위아래 여백은 `var(--s4)`로 한다. 고정폭 글꼴은 `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`, 크기는 14px, 줄간격은 1.6이다. `box-sizing:border-box; min-width:0; max-width:100%; overflow-x:auto; white-space:pre; tab-size:4`를 유지/추가한다. `pre > code`는 글꼴·크기·색상을 상속하고 자체 배경·테두리·여백·패딩을 두지 않는다. 설명과 코드가 한 pre에 섞였으면 설명 조각에서 설명만 밖으로 옮긴다. 원문은 내용과 구조를 보존하며 표시 규칙만 적용한다.

## 파일 역할

- `.agents/skills/ds-problem-explain/assets/note-template.html`: 공통 코드 블록 스타일.
- `.agents/skills/ds-problem-explain/assets/port-provenance.json`: 로컬 변경과 고정 원본의 관계. source/destination 고정 해시를 바꾸지 않고 local_overrides로 기록.
- `.agents/skills/ds-problem-explain/SKILL.md`, `references/authoring.md`, `references/verification.md`: 코드 저작·검토 규칙.
- `.agents/skills/ds-problem-explain/scripts/mpe_contract.py`: 설명 조각의 pre/code 구조 검사.
- `.agents/skills/ds-problem-explain/tests/test_code_blocks.py`(신규): 렌더링·구조·문자 보존 회귀 검사.
- `.agents/skills/ds-problem-explain/tests/test_skill_files.py`: 기존 provenance 검사 유지.
- `복습노트/*/자료_문제설명_*/fragments/*.html`: 독립 코드 구조에 문제가 확인된 설명 조각만 수정.
- `복습노트/*/문제설명_*.html/.md`, 해당 자료/그림 폴더: 기존 파이프라인으로 재생성한 설명 소유 산출물.
- `docs/verify/2026-10-13-ds-code-blocks.json`(신규): 보호 파일 해시, 대상 팩, 검토 근거, 백업/교체 기록.
- `.agents/skills/ds-review-pack/tests/test_problem_explain_delivery.py`: 새 발행을 기존 역사 기록과 연결하는 실제 산출물 검사.

### Task 1: 공통 코드 블록 표시와 보존 검사

**Files:** Modify `assets/note-template.html:112`, `assets/port-provenance.json:797` (이하 스킬 루트 기준). Create `tests/test_code_blocks.py`.

**Interfaces:** Consumes `build_explanation(pack, fragments, stage: Path, repo: Path) -> Artifacts`, `helpers.fragment(p)`, `helpers.source_file(repo)`, `mpe_shared.parse(markup)`. Produces 테마 변수를 사용하는 pre 스타일과 변경된 템플릿; 생성기 API는 유지한다.

- [x] Step 1: `test_code_block_style_uses_theme_tokens`를 작성한다. 생성 HTML의 pre 규칙에서 확정 설계의 배경/색/테두리/패딩/반경/글꼴/스크롤 선언을 확인하고 `pre > code`의 상속과 중복 패딩 제거를 확인한다. `test_code_and_output_whitespace_preserved`는 `code = 'if (a < b && p) {\n\tprintf("$%d", n);\n\n}\n'`, 실행결과 `'$1\n$2\n'`를 HTML escape 후 넣고 생성 HTML에서 각 pre의 `.text()`가 입력과 같으며 MD의 fenced block 내부도 같음을 확인한다. `test_pack_without_code_has_no_empty_pre`는 코드 없는 입력/설명에서 pre가 생성되지 않음을 확인한다.
- [x] Step 2: `uv run --with pytest python -m pytest .agents/skills/ds-problem-explain/tests/test_code_blocks.py -q` 실행. 스타일 검사는 현재 스타일에 배경/패딩이 없으므로 FAIL이어야 한다. 보존 검사의 기존 성공은 정상이다.
- [x] Step 3: 확정 설계대로 CSS를 변경한다. 템플릿의 기존 삽입 override를 전체 새 CSS 삽입문으로 교체하고 current_sha256을 계산한다. 고정 원본에서 새 삽입문을 제거하면 기존 base_sha256이 복원되도록 한다. 기타 수정된 이식 파일도 같은 provenance 규칙을 따른다.
- [x] Step 4: 스킬 전체 테스트 `uv run --with pytest python -m pytest .agents/skills/ds-problem-explain/tests -q` 실행. 모두 PASS, 원본 복원 해시 검사도 PASS여야 한다.
- [x] Step 5: 임시 fixture HTML을 실제 브라우저에서 1280×900/375×812, light/dark로 검사한다. 긴 줄 pre는 `scrollWidth > clientWidth`, 문서는 `scrollWidth <= clientWidth`; 계산 스타일의 패딩은 16px이고 테두리는 1px이며 각 테마에서 블록과 글자가 구분되어야 한다. 한 줄 코드, 출력, 인라인 코드도 확인하고 스크린샷/측정값을 evidence에 저장한다.
- [x] Step 6: 이 task 파일만 `git add`하고 `git diff --cached --check` 통과 후 `style: separate explanation code blocks`로 커밋한다.

### Task 2: 스킬 저작 규칙과 구조 검증으로 재발 방지

**Files:** Modify `SKILL.md`, `references/authoring.md:57`, `references/verification.md`, `scripts/mpe_contract.py:41`, `assets/port-provenance.json`. Extend `tests/test_code_blocks.py`.

**Interfaces:** Consumes Task 1 블록 스타일. Existing `validate_fragment(problem, fragment) -> list[str]` 내부에 `code_block_errors(fragment: str) -> list[str]`를 호출한다. 오류는 기존 build 검증 흐름으로 전달하며 원문 조건에는 이 신규 설명 저작 제약을 적용하지 않는다.

- [x] Step 1: `test_authored_pre_requires_one_direct_code_child`를 작성한다. `<pre>int n=0;</pre>`와 `<pre><p>설명</p><code>int n=0;</code></pre>`는 오류, `<pre><code class="language-c">int n=0;</code></pre>`는 오류 없음이어야 한다. pre 직계 공백 문자열은 허용하고 code 외 요소/비공백 텍스트는 거부한다. `test_inline_code_remains_valid`는 `<p><code>head</code>를 확인해요.</p>`가 기존 fragment에 포함되어도 `validate_fragment` 오류가 없음을 확인한다. `test_pre_inside_paragraph_is_rejected`는 `<p><pre><code>x</code></pre></p>`가 오류임을 확인한다.
- [x] Step 2: Task 1의 테스트 명령 실행. 새 구조 거부 검사 FAIL을 확인한다.
- [x] Step 3: `code_block_errors`를 기존 Node 파서로 구현하고 `validate_fragment`에 연결한다. 코드 구문을 추측하거나 일반 인라인 code를 블록으로 승격하지 않는다. 문서에는 독립 코드/실행결과는 pre/code, 설명은 밖, 짧은 인라인 표기는 유지, 빈 블록 금지, 문자 보존, 브라우저 검토 항목을 명시한다. 기존 코드 보존 예외/원문 보존 규칙은 유지한다.
- [x] Step 4: `test_skill_documents_code_block_contract`를 추가해 SKILL과 저작/검토 문서에 위 규칙이 존재함을 확인한다. 수정한 이식 파일의 local_overrides를 기존 원본 복원 방식에 맞게 갱신한다. 삽입 방식으로 기록할 수 있도록 고정 원본 내용은 유지하고 함수/문서 지침을 추가한다.
- [x] Step 5: 스킬 전체 테스트 명령 실행. 모두 PASS; 기존 SVG/수식/금지 속성 검사는 그대로 통과해야 한다.
- [x] Step 6: 이 task 변경만 stage, staged diff/check 검토 후 `fix: enforce explanation code block authoring`로 커밋한다.

### Task 3: 모든 날짜 재생성, 실제 검토, 발행 기록

**Files:** Modify 앞서 나열한 설명 소유 산출물과 delivery test. Create `docs/verify/2026-10-13-ds-code-blocks.json`. 원 문제·정리노트 파일은 보호 대상이다.

**Interfaces:** Consumes Task 1 템플릿, Task 2 구조 검사, 기존 CLI `extract --repo . --target <원문HTML> --run <고유RUN>`, `build/check/publish --run <RUN>`. Produces 전체 설명 산출물과 새 발행 증거. 기존 manifest/review 스키마를 유지한다.

- [x] Step 1: `복습노트/*/문제설명_*.html`을 열거해 현재 전체 목록을 잠근다. 기준은 0907/0914/0917/0921/0928/1001/1005/1008/1012의 9팩·64문항이며 실행 시 추가 팩이 있으면 전체 목록에 포함한다. 보호 파일의 상대경로/SHA-256, 기존 설명/검토 파일의 해시를 신규 보고서에 기록한다. 기존 docs/verify 보고서는 그대로 보존한다.
- [x] Step 2: `test_all_code_block_deliveries_current`를 delivery test에 추가한다. 신규 보고서가 전체 설명 HTML 집합과 일치하고 각 팩이 `check_pack(REPO, item) == []`, HTML/MD/원문 해시와 백업 교체 관계가 유효함을 확인한다. 기존 `test_real_delivery`는 역사 보고서의 경로/해시가 새 보고서의 유효한 교체 이력으로 이어질 때 승인하도록 기존 `check_preserved`를 사용한다. 이전 절대경로를 현재 repo로 해석하는 것은 보고된 상대경로와 원문 해시가 일치할 때만 허용하며, 잘못된 해시/누락 백업/가짜 pass fixture는 거부하는 테스트를 유지한다.
- [x] Step 3: `uv run --with pytest python -m pytest .agents/skills/ds-review-pack/tests/test_problem_explain_delivery.py -q` 실행. 신규 보고서 부재로 신규 검사 FAIL을 확인한다. 기존 경로 검사 실패는 worktree 경로 차이인지 근거를 분리한다.
- [x] Step 4: 팩별 고유 RUN으로 extract한다. 기존 `자료_문제설명_*/fragments/pN.html`을 RUN의 `explanations/`에 복사하고 관련 evidence를 보존한다. 구조 위반을 찾으면 해당 설명 조각만 최소 수정한다. 단순히 인라인 code라는 이유로 분리하지 않으며 원문/출력 텍스트를 바꾸지 않는다.
- [x] Step 5: 팩별 build/check를 수행한다. stage마다 원문 조건·설명 코드·출력·MD 문자/공백을 기존과 대조하고 보호 파일 해시를 확인한다. 새 artifact_hashes, 워크트리 안의 실제 references 경로와 해시를 사용한다.
- [x] Step 6: `references/verification.md`의 source_visual/content/independent/browser 검토를 실제 수행한다. 기존 독립 검산 스크립트는 재실행하고 내용 동등성을 확인한다. 모든 문항을 두 화면 크기·두 테마에서 검사하고 Task 1 측정과 목차/요약/수식/표/그림/링크 오류 0을 확인한다. 이번에 확인한 evidence만 review.json에 기록한다. 실패/disputed 팩은 교체하지 않고 원인을 해결하거나 미완료로 보고한다.
- [x] Step 7: 검토가 pass인 팩을 워크트리 내부에서 publish한다. publish 생성 백업의 실제 바이트 해시와 before/after를 신규 보고서에 기록한다. 보호 파일 전체 해시 불변과 전체 팩 적용을 확인한다. main checkout이나 다른 세션의 파일을 고치지 않는다.
- [x] Step 8: 스킬 전체 테스트와 delivery test 명령을 실행해 모두 PASS를 확인한다. `git diff --name-only`가 계획의 설명/스킬/검증 범위인지, `git diff --check`가 통과하는지 확인한다.
- [x] Step 9: 해당 산출물/보고서/test만 명시해 stage하고 `git diff --cached --check` 통과 후 `fix: regenerate review explanations with code blocks`로 커밋한다. merge/push 없이 브랜치와 최종 확인 결과를 보고한다.

## 계획 작성 시 확인 결과

- 시작점: main의 커밋 `d631a5a573a32c9406b139e319bc9c7c2d328098`.
- main의 다른 세션이 만든 미추적 PDF 계획/설계 파일은 복사하거나 수정하지 않았다.
- 워크트리 기본 Python에는 pytest가 없으므로 uv 임시 환경을 사용했다.
- baseline: `uv run --with pytest python -m pytest .agents/skills/ds-problem-explain/tests -q` → **72 passed in 3.09s**.
- self-review: 전체 날짜/코드·출력/인라인 유지/테마/공백 보존/재발 방지/워크트리 격리 요구사항이 Task 1–3에 포함되어 있다. 공개 생성/발행 API는 변경하지 않는다.

## 실행 인계

작은 변경이며 템플릿·이식 기록·재생성 작업이 서로 연결되므로 Native 실행을 권장한다. 계획 검토와 실행 방식 선택을 받은 뒤 구현한다. Native는 이 세션에서 직접 구현하고 마지막에 별도 리뷰어가 브랜치를 검토한다. Subagent-driven은 각 task 구현 및 리뷰를 별도 에이전트에 맡긴다.

## 실행 완료 기록

Native 방식으로 워크트리에서 Task 1–3을 실행했다. 문서 문구 고정 테스트는 테스트 지침에 따라 실제 구조/화면 검사와 수동 문서 검토로 대체했다. 별도 리뷰의 P2 재실행 결함을 추가 수정했으며, 기존 RUN 없이 64문항/256 브라우저 조합 재검증을 통과했다. 테스트는 78+159+60 passed, 4 skipped, 137 subtests passed. 자세한 판단·검토·재실행 명령은 `docs/verify/2026-10-13-ds-code-blocks-review.md`에 기록했다.
