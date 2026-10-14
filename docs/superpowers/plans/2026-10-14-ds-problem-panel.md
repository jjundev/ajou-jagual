# ds-problem-explain 문제 패널 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 생명과학 `bio-problem-explain` be26a42 의 문제 패널 HTML 형식과 `rerender` 명령을 `ds-problem-explain` 에 이식하고, 발행된 문제설명 9개를 새 형식으로 다시 발행한다.

**Architecture:** 템플릿은 3-way 병합(ds 현재 / bio 96c6d63 / bio be26a42)으로 만들고, 바뀐 추적 파일마다 `port-provenance.json` `local_overrides` 에 `replacements` override 를 기록 스크립트로 붙인다. render 는 문제·원문을 `.problem-pane` 으로 감싸고, CLI 의 `rerender` 는 발행 조각·검토를 이어받아 build 한다. 결과물 9개는 rerender → 실제 브라우저 검토 → publish 로 갱신하고, 팩별 migration 기록으로 해시 체인을 잇는다.

**Tech Stack:** Python 3.10+ 표준 라이브러리, pytest(`uv run -q --no-project --with pytest --with pymupdf python -m pytest`), Playwright(homebrew `python3`, `.venv` 에는 없음), git.

**Spec:** `docs/superpowers/specs/2026-10-14-ds-problem-panel-design.md`

## Global Constraints

- 작업 위치: worktree `../자구알-problem-panel`, 브랜치 `feat/problem-panel`(main e7b107e 기준). `.venv` 는 원 checkout 으로 심볼릭 링크. `git add` 는 경로를 지정한다. 병합·push 는 사용자 요청 시에만.
- 커밋 메시지 끝: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
- `S=.agents/skills/ds-problem-explain`. 생명과학 저장소는 `../생명과학`(커밋 96c6d63, be26a42).
- 템플릿 고정값: localStorage 탭 키 `'ds-problem-explain-tab'`, 기본 `data-prob-dock="left"`, SUBTITLE `왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.`, 원문 요약 `기출 원문 보기`, choice model 은 항상 `{}`.
- 템플릿에 `bio-` 문자열이 남지 않는다.
- `port-provenance.json` 의 `source_commit`(1e2d5f8…)과 기존 `files`·`local_overrides` 항목은 바꾸지 않는다. 덧붙이기만 한다.
- 이력 JSON(`docs/verify/*.json`, `복습노트/*/.pack/**` 의 기존 `.json`, `migration-2026-10-13-*.json`)은 수정하지 않는다. 결과물 쪽 새 파일은 팩마다 `.pack/migration-2026-10-14-problem-panel.json` 하나다.
- 원 복습문제·정리노트·PDF·은행은 수정하지 않는다. 설명 조각도 다시 쓰지 않는다.
- ds-review-pack 테스트는 Task 1 에서 잰 기준선 실패 목록(0914 delivery 6건 + test_pdf_cli 1건 예상) 밖의 새 실패가 0이어야 한다.

## Review Focus

- 원문이 없는 문항 → `details.original` 이 없고 원문 탭이 숨는다(Task 3 `test_problem_without_original_has_no_details`, Task 5 acceptance p2).
- 문제 지문과 원문에 같은 SVG id → 두 사본의 id 가 겹치지 않는다(Task 3 `test_statement_and_original_sharing_svg_ids_stay_unique`).
- `<pre>` 긴 코드가 있는 문제를 375px 패널에 띄움 → 문서 가로 넘침 0, 스크롤은 pre 안에서만(Task 5 acceptance 단언).
- 발행 manifest 의 `repo` 가 지금은 없는 다른 worktree 경로(실제 9개 모두 해당) → references 가 현재 checkout 으로 재기준되고 검토가 이어진다(Task 4 `test_rerender_rebases_reference_paths_to_current_checkout`).
- 같은 팩에 `migration-2026-10-14-problem-panel.json` 이 이미 있음 → 덮어쓰지 않고 실패한다(Task 6 스크립트 `test_record_refuses_existing`).

---

### Task 1: worktree, 기준선, override 기록 스크립트

**Files:**
- Create: `docs/verify/record-ds-explain-overrides.py`
- Create: `docs/verify/test_record_ds_explain_overrides.py`
- Modify: `$S/tests/test_render.py` (`test_template_bytes_match_pinned_ml` 이 `replacements` 도 벗기게)

**Interfaces:**
- Produces: CLI `python3 docs/verify/record-ds-explain-overrides.py --reason "<text>" <destination>...`. destination 은 `$S` 기준 상대 경로(예: `assets/note-template.html`)이고, 뒤 Task 들이 파일을 고친 뒤 모두 이 명령으로 기록한다.
- Produces: `undo_overrides(current: bytes, chain: list[dict]) -> bytes` 는 `$S/tests/test_skill_files.py` 의 기존 함수다. `test_render.py` 가 이것을 import 한다.

- [ ] **Step 1: worktree 를 만들고 기준선을 잰다**

```bash
git worktree add ../자구알-problem-panel -b feat/problem-panel main
cd ../자구알-problem-panel && ln -s ../자구알/.venv .venv
mv ../자구알/docs/superpowers/specs/2026-10-14-ds-problem-panel-design.md docs/superpowers/specs/
mv ../자구알/docs/superpowers/plans/2026-10-14-ds-problem-panel.md docs/superpowers/plans/
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-review-pack/tests -q -p no:cacheprovider 2>&1 | grep -E '^FAILED' | sort > /tmp/claude-501/ds-baseline.txt; wc -l /tmp/claude-501/ds-baseline.txt
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q
```
Expected: 기준선 7줄 안팎. ds-problem-explain 은 전부 PASS.

- [ ] **Step 2: 기록 스크립트의 실패 테스트를 쓴다**

`docs/verify/test_record_ds_explain_overrides.py` 는 임시 git 저장소를 만들고, 가짜 skill 디렉터리와 `assets/port-provenance.json`(files 항목 1개, override 없음)을 커밋한 뒤 파일을 고친다. 스크립트 함수 `record(skill: Path, reason: str, destinations: list[str]) -> list[dict]` 를 `importlib` 로 불러 테스트한다.
  - `test_record_appends_reversible_override`: 여러 군데(앞·중간·끝, 반복되는 줄 포함)를 고친 뒤 record. override 가 1개 추가되고, `current_sha256`== 지금 파일 hash, `base_sha256`== HEAD 바이트 hash 이며, `undo_overrides(지금 바이트,[새 override])`== HEAD 바이트.
  - `test_record_chains_on_existing_override`: 두 번 고치고 커밋 사이마다 record → 두 override 를 최신부터 벗기면 원본이 된다.
  - `test_record_refuses_unrecorded_head`: HEAD 바이트 hash 가 체인 마지막 `current_sha256`(체인이 없으면 `destination_sha256`)과 다르면 `SystemExit`.
  - `test_record_noop_when_unchanged`: 파일이 HEAD 와 같으면 override 를 추가하지 않는다.

- [ ] **Step 3: 실패 확인**

Run: `uv run -q --no-project --with pytest python -m pytest docs/verify/test_record_ds_explain_overrides.py -q`
Expected: FAIL(모듈 없음)

- [ ] **Step 4: `record()` 와 CLI 를 구현한다**

`old = git show HEAD:<skill 상대경로>`, `new = 현재 바이트`. 줄 단위 `difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False).get_opcodes()` 에서 equal 이 아닌 구간마다 앞뒤 context 를 k 줄 붙여 `{"old": …, "new": …}` 을 만든다. 넓힌 범위가 겹치는 구간은 하나로 합친다. 구간 순서는 파일 순서다. k=0 부터 늘려 가며 `undo_overrides(new,[candidate]) == old` 가 될 때(각 `new` 가 그 시점에 정확히 1회 등장) 확정하고, k>20 이면 `SystemExit`. 항목 형식은 `{"destination","base_sha256","current_sha256","replacements","reason"}` 이고, `json.dumps(…, ensure_ascii=False, indent=2)+"\n"` 로 저장한다. `undo_overrides` 는 `$S/tests/test_skill_files.py` 에서 import 한다.

- [ ] **Step 5: 통과 확인**

Run: `uv run -q --no-project --with pytest python -m pytest docs/verify/test_record_ds_explain_overrides.py -q`
Expected: PASS

- [ ] **Step 6: `test_render.py` 의 peel 루프를 `undo_overrides` 로 바꾼다**

`test_template_bytes_match_pinned_ml` 이 `from test_skill_files import undo_overrides` 를 쓰도록 바꾼다. 체인 마지막 `current_sha256` 과 지금 hash 가 같은지 확인한 뒤 `undo_overrides(...)` 결과가 `d0fe664a…ba50` 이어야 한다. 이어서 `python3 docs/verify/record-ds-explain-overrides.py --reason "2026-10-14 problem panel: peel replacement overrides too." tests/test_render.py` 를 실행한다.

- [ ] **Step 7: ds-problem-explain 전체 테스트가 통과하는지 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests docs/verify/test_record_ds_explain_overrides.py -q`
Expected: PASS

- [ ] **Step 8: 커밋**

```bash
git add docs/verify/record-ds-explain-overrides.py docs/verify/test_record_ds_explain_overrides.py .agents/skills/ds-problem-explain/tests/test_render.py .agents/skills/ds-problem-explain/assets/port-provenance.json docs/superpowers/specs/2026-10-14-ds-problem-panel-design.md docs/superpowers/plans/2026-10-14-ds-problem-panel.md
git commit -m "chore(ds-problem-explain): record replacement overrides by script"
```

### Task 2: 문제 패널 템플릿

**Files:**
- Modify: `$S/assets/note-template.html`
- Modify: `$S/tests/test_render.py` (템플릿 구조 테스트 3개 추가)
- Modify: `$S/assets/port-provenance.json` (기록 스크립트로)

**Interfaces:**
- Consumes: Task 1 기록 스크립트.
- Produces: 템플릿 마크업 `.layout[data-prob-dock]`, `#panel-prob`, `#tab-problem`/`#tab-original`, `.probs`, `.orig-tab`, `.prob-dock`, `.float-move`, `.float-resize`. 템플릿 JS 는 `.problem-pane[data-problem-for]` 와 `details.original` 을 읽어 패널을 채운다(Task 3 render 가 이 계약대로 출력한다).

- [ ] **Step 1: 실패 테스트를 쓴다(`test_render.py`)**

bio `tests/test_render.py`(be26a42)에서 `test_problem_panel_left_of_content` 와 `test_problem_panel_dock_controls` 를 그대로 가져온다. 그리고 다음을 추가한다.

```python
def test_template_is_ds_branded():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    assert 'bio-' not in t and "const TAB = 'ds-problem-explain-tab';" in t
    assert '.verdict-card {' in t  # 판정 카드 코드는 비활성 상태로 남는다
```

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests/test_render.py -q -k "panel or branded"`
Expected: FAIL

- [ ] **Step 3: 템플릿을 병합하고 이름을 바꾼다**

```bash
git -C ../생명과학 show 96c6d63:.agents/skills/bio-problem-explain/assets/note-template.html > /tmp/claude-501/bio-base.html
git -C ../생명과학 show be26a42:.agents/skills/bio-problem-explain/assets/note-template.html > /tmp/claude-501/bio-head.html
git merge-file .agents/skills/ds-problem-explain/assets/note-template.html /tmp/claude-501/bio-base.html /tmp/claude-501/bio-head.html
```
Expected: 종료 코드 0(충돌 없음). 이어서 `'bio-problem-explain-tab'` 을 `'ds-problem-explain-tab'` 으로 바꾼다. `bio-review-pack … 복사` 주석 4곳(CSS 3·JS 1)은 `생명과학 bio-problem-explain be26a42 에서 이식` 으로 바꾸고, `test_choice_feedback_copied_from_review_pack` 언급은 지운다.

- [ ] **Step 4: 템플릿 테스트와 기존 스크롤바·코드블록 테스트가 통과하는지 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests/test_render.py .agents/skills/ds-problem-explain/tests/test_scrollbar.py .agents/skills/ds-problem-explain/tests/test_code_blocks.py -q`
Expected: 새 테스트와 스크롤바·코드블록 테스트는 PASS. `test_template_bytes_match_pinned_ml` 은 아직 FAIL(기록 전).

- [ ] **Step 5: provenance 를 기록하고 전체 테스트를 돌린다**

```bash
python3 docs/verify/record-ds-explain-overrides.py --reason "User approved 2026-10-14: problem panel layout from bio-problem-explain be26a42 (3-way merge over ds code blocks and scrollbar); ds tab key." assets/note-template.html
python3 docs/verify/record-ds-explain-overrides.py --reason "2026-10-14 problem panel: template structure tests." tests/test_render.py
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q
```
Expected: PASS(render 는 아직 예전 마크업을 내므로 `test_legacy_statement_rendered_once` 등 기존 render 테스트도 그대로 통과).

- [ ] **Step 6: 커밋**

```bash
git add .agents/skills/ds-problem-explain/assets/note-template.html .agents/skills/ds-problem-explain/assets/port-provenance.json .agents/skills/ds-problem-explain/tests/test_render.py
git commit -m "feat(ds-problem-explain): dockable problem panel template from bio-problem-explain"
```

### Task 3: render 가 문제를 패널용으로 출력

**Files:**
- Modify: `$S/scripts/mpe_render.py` (`resources` style 허용 scope, `build_explanation` 147–168행)
- Modify: `$S/tests/test_render.py`, `$S/tests/helpers.py` (`acceptance_pack` p2 에 그림·marker SVG 추가)
- Modify: `$S/assets/port-provenance.json` (기록)

**Interfaces:**
- Consumes: Task 2 템플릿 계약.
- Produces: 문항마다 `<div class="problem-pane" data-problem-for="pN"><div class="layer formal" data-source-problem="pN">…</div>[<details class="original" data-original-problem="pN"><summary>기출 원문 보기</summary>…</details>]</div>`, `SCRIPTS = '<script type="application/json" id="explain-choice-model">{}</script>'`.

- [ ] **Step 1: 실패 테스트를 쓴다**

`test_legacy_statement_rendered_once` 에서 `assert not list(...details...)` 를 bio 처럼 바꾼다. details 가 1개이고 `'original' in classes` 이며, SUBTITLE 문구가 있고, `md.index('printf') < md.index('이 문제를 봤을 때')` 여야 한다. bio 에서 `test_problem_pane_wraps_statement_and_original`, `test_statement_and_original_sharing_svg_ids_stay_unique` 를 가져온다. `test_problem_without_choice_absent_from_model` 은 이름을 `test_choice_model_is_empty` 로 바꿔 가져온다. 다음을 추가한다.

```python
def test_problem_without_original_has_no_details(tmp_path):
    pack,fragments=make(tmp_path)
    pack=replace(pack,problems=(replace(pack.problems[0],original_html=''),))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    assert not list(parse(result.html.read_text()).find_all(lambda n:n.tag=='details'))
```

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests/test_render.py -q`
Expected: FAIL(problem-pane·details 없음)

- [ ] **Step 3: `build_explanation` 과 `resources` 를 고친다**

bio be26a42 `mpe_render.py` 의 같은 구간을 따른다. `.assets`·forecast·`context_hashes`·choices 수집은 넣지 않는다. 바뀌는 점은 다음과 같다.
  - `resources()` 의 정적 그림 style 허용 조건을 `scope in ('source','original')` 로 넓힌다.
  - 원문을 `resources(p.original_html, …, 'original')` 로 따로 검증한 뒤 details 로 감싼다.
  - 위 Interfaces 의 마크업으로 감싼다.
  - `SUBTITLE` 과 `SCRIPTS` 는 Global Constraints 의 값을 쓴다.

  `helpers.acceptance_pack` 의 p2 에는 bio 처럼 `<ol><li>(a)` 앞에 `<img src="그림.png" alt="문제 그림">` 과 marker SVG 그림을 넣는다.

- [ ] **Step 4: 통과 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q`
Expected: PASS(provenance 테스트 제외)

- [ ] **Step 5: 기록, 전체 테스트, 커밋**

```bash
python3 docs/verify/record-ds-explain-overrides.py --reason "2026-10-14 problem panel: wrap problem and original for the panel; empty choice model." scripts/mpe_render.py tests/test_render.py tests/helpers.py
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q
git add .agents/skills/ds-problem-explain/scripts/mpe_render.py .agents/skills/ds-problem-explain/tests/test_render.py .agents/skills/ds-problem-explain/tests/helpers.py .agents/skills/ds-problem-explain/assets/port-provenance.json
git commit -m "feat(ds-problem-explain): render problem and original into the problem panel"
```
Expected: PASS

### Task 4: `rerender` 명령

**Files:**
- Modify: `$S/scripts/mpe_cli.py`
- Modify: `$S/tests/test_cli.py`
- Modify: `$S/assets/port-provenance.json` (기록)

**Interfaces:**
- Consumes: 기존 `extract(repo,target,run)`, `load_run`, `load_fragments`, `build(item,fragments)`, `names(pack)`, `PACK_DIR`(mpe_render), `payload_hash`, `load_source`.
- Produces: `rerender(repo, target, run) -> int`, `git_blob(path: Path, digest: str) -> bytes | None`, `published_source(pack, digest) -> SourcePack | None`, `same_problems(old, new) -> bool`, `carried_references(references, old_repo: Path, repo: Path) -> tuple[list, list[str]]`, `CODE_RE`. 하위 명령 `rerender --repo --target --run`(모두 필수).

- [ ] **Step 1: 실패 테스트를 쓴다**

bio `tests/test_cli.py` 의 `published_pack`(`reference=` 인자 포함), `git_commit_all`, `rerendered_review` 와 테스트 8개를 가져온다: `test_rerender_reuses_content_reviews`, `…changed_source_keeps_reviews_unrun`, `…without_published_fragments_fails`, `…style_only_source_change_reuses_reviews`, `…content_change_with_history_keeps_reviews_unrun`, `…rebases_reference_paths_to_current_checkout`, `…reference_style_only_change_updates_hash`, `…reference_content_change_keeps_old_hash`. 경로의 `.assets/자료_*` 는 `.pack/자료_*` 로 바꾸고 bio 전용 PNG/figure 준비는 뺀다. 다음을 추가한다.

```python
def test_rerender_keeps_published_evidence(tmp_path):
    repo, source = published_pack(tmp_path)
    data = next((repo / '복습노트/0917/.pack').glob('자료_*'))
    (data / 'evidence' / 'code-block-history').mkdir(parents=True)
    (data / 'evidence' / 'code-block-history' / 'old.html').write_text('옛 화면')
    result = call('rerender', '--repo', repo, '--target', source, '--run', tmp_path / 'run2')
    assert result.returncode == 0, result.stderr
    folder = next(p for p in (tmp_path / 'run2').iterdir() if p.is_dir())
    assert (folder / 'evidence' / 'code-block-history' / 'old.html').read_text() == '옛 화면'
```
`test_skill_files.test_install_has_no_ml_runtime_dependency` 의 `--help` 단언에 `'rerender' in result.stdout` 을 추가한다.

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests/test_cli.py .agents/skills/ds-problem-explain/tests/test_skill_files.py -q -k "rerender or install"`
Expected: FAIL(`invalid choice: 'rerender'`)

- [ ] **Step 3: `mpe_cli.py` 에 이식한다**

bio be26a42 `mpe_cli.py` 의 해당 함수와 하위 명령을 옮긴다. 차이는 다음과 같다.
  - 자료 폴더는 `pack.path.parent / PACK_DIR / names(pack)[2]` 다.
  - `SIDE_URL_RE`·`unside`·`migrate_md`·`moves` 와 `carried_references` 의 `.assets` 이동 분기는 뺀다.
  - `same_problems` 는 `tuple(old)==tuple(new)` 다.
  - `carried_references` 의 style-only 비교는 `CODE_RE.sub('', text)` 만 쓴다. 알림 문구는 `참조 자료는 스타일·스크립트만 바뀌었어요: <name>` 이다(가져온 테스트 문구도 맞춘다).
  - 출력 문구 `content·independent 재사용, source_visual·browser 재검토 필요`, `원본 파일은 바뀌었지만 문항 내용은 같아요: `, `입력 변경: 네 검토 모두 다시 필요`, `발행된 조각 없음/불일치: 정상 저작 절차를 쓰세요` 는 bio 와 같다.

- [ ] **Step 4: 통과 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q`
Expected: PASS(provenance 테스트 제외)

- [ ] **Step 5: 실제 9개 팩 dry run(발행 안 함)**

```bash
for d in 1012 1008 1005 1001 0928 0921 0917 0914 0907; do python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py rerender --repo "$PWD" --target $d --run tmp/ds-problem-explain/20261014-dry/$d | grep -E '재사용|입력 변경|참조'; done
```
Expected: 9줄 모두 `원본 파일은 바뀌었지만 문항 내용은 같아요: content·independent 재사용, source_visual·browser 재검토 필요`, `입력 변경` 0줄. 하나라도 다르면 여기서 멈추고 보고한다.

- [ ] **Step 6: 기록, 전체 테스트, 커밋**

```bash
python3 docs/verify/record-ds-explain-overrides.py --reason "2026-10-14 problem panel: rerender for layout-only republish (from bio-problem-explain be26a42, .pack layout)." scripts/mpe_cli.py tests/test_cli.py tests/test_skill_files.py
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q
git add .agents/skills/ds-problem-explain/scripts/mpe_cli.py .agents/skills/ds-problem-explain/tests/test_cli.py .agents/skills/ds-problem-explain/tests/test_skill_files.py .agents/skills/ds-problem-explain/assets/port-provenance.json
git commit -m "feat(ds-problem-explain): add rerender for layout-only republish"
```

### Task 5: 브라우저 수용 검사와 문서

**Files:**
- Modify: `$S/tests/browser_acceptance.py`
- Modify: `$S/SKILL.md`, `$S/references/verification.md`, `$S/references/authoring.md`
- Modify: `$S/tests/test_skill_files.py` (문서 단언)
- Modify: `$S/assets/port-provenance.json` (기록)

**Interfaces:**
- Consumes: Task 3 `acceptance_pack`(p1·p2), Task 2 템플릿 셀렉터.
- Produces: `python3 $S/tests/browser_acceptance.py <빈 scratch>` 는 실패 시 0이 아닌 코드로 끝나고 결과 JSON 을 출력한다. Task 6 이 실제 팩에 같은 단언을 재사용한다.

- [ ] **Step 1: 문서 단언(실패)을 쓴다**

```python
def test_skill_documents_rerender_and_panel():
    skill=(S/'SKILL.md').read_text();verification=(S/'references/verification.md').read_text()
    assert '### 레이아웃만 바뀐 기존 발행분 재발행' in skill and 'mpe_cli.py rerender' in skill
    assert 'od-panels:explain:v2:prob' in skill and '원문 탭' in verification and '띄우기' in verification
```

- [ ] **Step 2: 실패 확인**

Run: `uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests/test_skill_files.py -q -k documents`
Expected: FAIL

- [ ] **Step 3: 문서를 고친다**

  - SKILL.md 6단계 브라우저 문장 뒤에 bio 의 문제 패널 문장을 붙인다. 판정 카드 관련 구절은 뺀다.
  - SKILL.md 7단계 뒤에 bio 의 "레이아웃만 바뀐 기존 발행분 재발행" 절을 옮긴다. `.assets` 이동 문장은 빼고, 예시 경로는 `복습노트/1012/복습문제_1012_Queue.html`, 순서는 "최신 → 0907" 로 쓴다.
  - verification.md 의 `browser` 항목에 bio 의 패널 확인 문장을 붙인다. 보기 판정·알림·재풀이 구절은 뺀다.
  - authoring.md 의 원문 보존 문장은 "기출 원문은 조립기가 문제 안에 '기출 원문 보기'로 접어 보존해요." 로 바꾼다.

- [ ] **Step 4: 브라우저 수용 검사를 이식한다**

bio be26a42 `browser_acceptance.py` 를 기준으로 옮긴다.
  - 서버 기동·뷰포트(1280×900, 1024×768, 375×812)×테마 루프, 콘솔·실패 요청·외부 요청 0, 문서 가로 넘침 0, 문제 패널 기본 열림, 원문 탭, 도킹 세 방식, 띄운 창 이동·크기 조절·clamp, `drag`·`headgap`·`touchdrag`, 375 의 '문제 보기' 토글, 문제 그림 확대 단언은 그대로 가져온다.
  - choice model·보기 판정·알림·p3/p4 부분은 뺀다.
  - 원문 없는 문항은 p2 의 `details.original` 을 지워서 만든다(bio 의 p4 자리).
  - ds 의 기존 단언(코드 블록 내부 스크롤, KaTeX)은 유지한다.
  - 375 에서 p1 의 긴 `<pre>` 가 패널 안에서만 스크롤하고 `document.scrollingElement.scrollWidth <= innerWidth` 인지 단언한다.

- [ ] **Step 5: 수용 검사와 전체 테스트를 실행한다**

```bash
python3 .agents/skills/ds-problem-explain/tests/browser_acceptance.py "$(mktemp -d)/acc"
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests -q
```
Expected: 수용 검사 종료 코드 0, pytest 는 provenance 테스트 제외 PASS.

- [ ] **Step 6: 기록, 테스트, 커밋**

```bash
python3 docs/verify/record-ds-explain-overrides.py --reason "2026-10-14 problem panel: document rerender and panel checks; browser acceptance for the panel." SKILL.md references/verification.md references/authoring.md tests/browser_acceptance.py tests/test_skill_files.py
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests docs/verify/test_record_ds_explain_overrides.py -q
git add .agents/skills/ds-problem-explain docs/verify/record-ds-explain-overrides.py
git commit -m "feat(ds-problem-explain): browser acceptance and docs for the problem panel"
```
Expected: PASS

### Task 6: 기존 문제설명 9개 재발행

**Files:**
- Create: `docs/verify/record-problem-panel-migration.py`, `docs/verify/test_record_problem_panel_migration.py`
- Create: `docs/verify/problem-panel-browser.py` (실제 팩 하나의 stage HTML 에 Task 5 단언을 적용하는 래퍼)
- Modify(publish 로): `복습노트/<D>/문제설명_<D>_<slug>.html`, `복습노트/<D>/.pack/문제설명_<D>_<slug>.md`, `복습노트/<D>/.pack/자료_문제설명_<D>_<slug>/**`
- Create: `복습노트/<D>/.pack/migration-2026-10-14-problem-panel.json` × 9

**Interfaces:**
- Consumes: Task 4 `rerender`, Task 5 수용 단언.
- Produces: `record(date_dir: Path, before: dict[str,str]) -> Path`. before 는 `{"문제설명_….html": sha, ".pack/문제설명_….md": sha}` 이고, 결과 파일은 `{"date":"2026-10-14","reason":"problem panel (bio-problem-explain be26a42)","moved":[],"rewritten":{rel:{"before","after"}}}` 이다. before==after 인 항목은 기록하지 않는다.

- [ ] **Step 1: migration 기록 테스트(실패)를 쓴다**

`test_record_writes_before_after`(after 는 지금 파일 hash), `test_record_refuses_existing`(같은 파일이 있으면 `SystemExit` 하고 파일 내용이 바뀌지 않음), `test_record_skips_unchanged`.

- [ ] **Step 2: 실패 확인 → 구현 → 통과 확인**

Run: `uv run -q --no-project --with pytest python -m pytest docs/verify/test_record_problem_panel_migration.py -q`
Expected: 먼저 FAIL, 구현 후 PASS

- [ ] **Step 3: 팩마다(1012 → 0907 순서) rerender·check 를 실행한다**

```bash
D=1012; RUN=tmp/ds-problem-explain/20261014-panel/$D
python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py rerender --repo "$PWD" --target $D --run $RUN
python3 .agents/skills/ds-problem-explain/scripts/mpe_cli.py check --run $RUN
```
Expected: `content·independent 재사용` 과 `check: machine PASS`. `입력 변경` 이나 `참조 자료 변경/없음` 이 나오면 그 팩은 멈추고 보고한다.

- [ ] **Step 4: 실제 브라우저 검토와 review 기록**

`python3 docs/verify/problem-panel-browser.py <RUN 의 stage html> <RUN>/<bucket>/evidence/browser-rerender-<D>.json` 은 4조합(1280/375 × light/dark)과 1024 light 에서 모든 문항을 돌며 Task 5 단언을 적용하고 스크린샷을 같은 폴더에 둔다. 스크린샷과 원 `복습문제_<D>_<slug>.html` 을 열어 패널의 문제·원문이 원본과 같은지(코드·수치·그림) 직접 대조한다. 그 결과를 `review.json` 의 `source_visual`·`browser` 에 `{"status":"pass","reviewer":…,"evidence":"evidence/browser-rerender-<D>.json …"}` 로 적는다. 결함이 있으면 publish 하지 않고 보고한다.

- [ ] **Step 5: publish 와 migration 기록**

publish 전에 HTML·MD 의 HEAD hash 를 잰다. `mpe_cli.py publish --run $RUN` 을 실행하고, `record-problem-panel-migration.py` 로 `.pack/migration-2026-10-14-problem-panel.json` 을 쓴다. Steps 3–5 를 9개 팩 모두에 반복한다.

- [ ] **Step 6: 회귀 확인**

```bash
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-problem-explain/tests docs/verify -q
uv run -q --no-project --with pytest --with pymupdf python -m pytest .agents/skills/ds-review-pack/tests -q -p no:cacheprovider 2>&1 | grep -E '^FAILED' | sort | diff /tmp/claude-501/ds-baseline.txt -
git status --short | grep -v '^??' ; git status --short 복습노트 | grep -v 'migration-2026-10-14\|문제설명' || true
```
Expected: 첫 줄 PASS, diff 출력 없음(새 실패 0), 문제설명 소유 파일과 migration 기록 외에 바뀐 파일 없음.

- [ ] **Step 7: 커밋**

```bash
git add docs/verify/record-problem-panel-migration.py docs/verify/test_record_problem_panel_migration.py docs/verify/problem-panel-browser.py 복습노트/*/문제설명_*.html 복습노트/*/.pack/문제설명_*.md 복습노트/*/.pack/자료_문제설명_* 복습노트/*/.pack/migration-2026-10-14-problem-panel.json
git commit -m "docs(notes): republish problem explanations with dockable problem panel"
```
