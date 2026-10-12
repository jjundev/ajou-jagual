# 자구알 문제설명 스킬 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 기존 자구알 복습문제 HTML에서 입문 설명 HTML·MD를 만드는 독립 스킬을 설치한다.

**Architecture:** ML의 검증된 설명 엔진을 고정 커밋에서 이식하고 자구알 카드 어댑터를 추가한다. 템플릿은 그대로 유지하며 필요한 공용 모듈을 스킬 안에 포함한다. 원자료와 설명 발행은 분리한다.

**Tech Stack:** Python 3.10+, standard library runtime, pytest development tests, HTML/CSS/JavaScript, bundled KaTeX/Pretendard, local browser verification.

**Spec:** `docs/superpowers/specs/2026-10-12-ds-problem-explain-design.md`

## Global Constraints

- 원본 커밋: `1e2d5f81813a5481c78341545a13ab300f2d82c5`.
- `assets/note-template.html`과 vendor 자원은 바이트 그대로 복사한다.
- Python 3.10 이상, 실행기는 표준 라이브러리만 사용한다.
- 기존 복습문제 HTML 우선. 과제·실습 PDF 직접 추출과 과제 카드 지원은 이번 구현에서 제외한다.
- 최신 팩이 0문항이면 알리고 중단하며 이전 날짜로 자동 이동하지 않는다.
- 일곱 직계 구역 `understand → recall → start → solve → verify → pitfall → retry`를 유지한다.
- 기존 HTML/MD/그림·은행·정리노트는 변경하지 않는다.
- 브라우저는 1280×900/375×812, light/dark. 콘솔·KaTeX 오류, 누락 자원, 외부 요청, 문서 가로 넘침은 0.
- 읽음 상태 키: `ds-problem-explain-review-<range>-<slug>`.
- 설치 중 실제 수업 문제설명을 발행하지 않는다. 커밋·푸시는 별도 사용자 요청 없이 실행하지 않는다.

## Review Focus

1. 최신/명시 날짜의 0문항 팩: 자동 fallback·빈 완성본 없이 문항 없음과 후보를 보고한다 — Task 1.
2. 질문 목록과 연산 목록이 섞인 코드 문항: 질문 소문항을 잘못 늘리거나 합치지 않는다 — Task 1.
3. C 코드의 `<`, `&`, `$`와 원문 오타/UB: 텍스트를 보존하고 수식 오검사·정답 자동 승인을 막는다 — Tasks 1–2.
4. NFD 경로·반복 SVG ID·그림/anchor 이동: 발행 후에도 자원과 링크를 유지한다 — Task 3.
5. 검토 후 참조 변경·두 번째 파일 교체 실패: 승인 재사용을 거부하고 기존 파일을 복구한다 — Task 4.

---

## 파일 구조와 경계

모든 신규 코드의 기준 폴더 S는 `.agents/skills/ds-problem-explain`이다. 기존 ds-review-pack은 수정하지 않는다.

- `S/scripts/mpe_types.py`: 원본 Problem/SourcePack/Artifacts와 ExplainError 계약.
- `S/scripts/mpe_source.py`: 날짜/경로 선택, 자구알 카드 추출, Unicode 경로.
- `S/scripts/mpe_shared.py`: 동봉된 공용 도구의 좁은 import 어댑터.
- `S/scripts/mpe_contract.py`: 설명 구역·소문항·검토 계약.
- `S/scripts/mpe_render.py`: 템플릿 슬롯·그림/링크·MD·stage 검증.
- `S/scripts/mpe_publish.py`: 현재 검토·참조·산출물 검사와 발행.
- `S/scripts/mpe_cli.py`: extract/build/check/publish와 팩별 성공/실패.
- `S/scripts/vendor/html2md.py`, `review_pdf_types.py`, `review_pdf_cards.py`, `review_pdf_publish.py`: ML 공용 모듈의 동봉 사본. `normalize_cards`와 과제 profile은 신규 흐름에서 사용하지 않는다.
- `S/scripts/vendor/math_checks.py`: ML check_html의 math_delimiter_errors를 출처와 함께 분리하여 manifest 모듈 의존성을 제거한다. cards 모듈의 import만 이 파일로 바꾼다.
- `S/assets/note-template.html`, `S/assets/vendor/**`: 원본과 바이트 동일한 화면/자원.
- `S/assets/port-provenance.json`: source repo/commit/path/hash, destination/hash, 변경 이유 및 동봉 dependency 목록.
- `S/references/authoring.md`, `verification.md`, `S/SKILL.md`: 자구알 저작·검증·호출 규칙.
- `S/tests/conftest.py`, `helpers.py`, `test_source.py`, `test_contract.py`, `test_render.py`, `test_publish.py`, `test_cli.py`, `test_layout.py`, `test_skill_files.py`: 원본 테스트를 재사용/조정하고 아래 회귀 사례를 추가한다.
- `.claude/skills/ds-problem-explain`: S를 가리키는 상대 symlink.

원본 이식은 Git show 또는 archive로 수행한다. 머신러닝기초 현재 checkout이나 branch를 바꾸지 않는다. 함수명을 mpe_*로 유지해 불필요한 전면 rename을 피한다. 이하 Run 명령의 S는 위 경로의 실제 값으로 치환한다.

### Task 1: 자구알 입력 추출과 독립 실행 기반

**Files:** Create S/scripts/mpe_types.py, mpe_source.py, mpe_shared.py, vendor/*.py; S/tests/conftest.py, helpers.py, test_source.py.

**Interfaces:**
- Consumes: 저장된 `.card`, `.problem`, `.original`, `.solution`, `.steps`, `.answer` HTML.
- Produces: `resolve_sources(repo: Path, target: str | None) -> tuple[Path, ...]`, `load_source(path: Path, repo: Path) -> SourcePack`, `subparts(ask: str, original: str) -> tuple[str, ...]`, `sha256(path: Path) -> str`, `inside(path: Path, repo: Path) -> Path`, `existing_path(path: Path) -> Path`.
- SourcePack/Problem/Artifacts 필드는 원본 mpe_types.py 그대로. profile은 review이며 전체 problem은 conditions_html, ask_html은 빈 문자열이다. 원본 helper parse/inner/outer/compact와 MD·발행 exports는 mpe_shared에서 동봉 모듈로 제공한다.

- [ ] **Step 1: 실패 테스트 작성.** `test_legacy_problem_preserves_code`는 `conditions_html`을 parse하여 pre/code의 text가 입력과 같고 ask_html == '' 및 subparts == ('main',)인지 검증한다. `test_empty_latest_does_not_fallback`은 최신 1008 빈 팩과 이전 유효 팩에서 ExplainError('문항 없음') 및 입력 무변경을 검증한다. `test_question_vs_operation_lists`는 질문 (a)/(b)와 내부 연산 목록에서 ('a','b')만 추출한다. `test_ambiguous_subparts_block`, `test_duplicate_card_ids`, `test_nfd_target`, `test_multiple_slugs_require_path`, `test_range_conflict`, `test_source_outside_repo`도 기대 오류/선택 경로를 고정한다. 실제 비어 있지 않은 자료는 0917을 read-only 비교 대상으로 쓰고 fixture는 test scratch에 둔다.
최소 테스트 assertions 예시(legacy_file/repo fixture는 helpers.py에서 생성):

```python
def test_legacy_problem_preserves_code(legacy_file, repo):
    pack = load_source(legacy_file, repo)
    problem = pack.problems[0]
    assert problem.ask_html == ''
    assert problem.subparts == ('main',)
    code = next(parse(problem.conditions_html).find_all(lambda n: n.tag == 'code'))
    assert code.text() == 'printf("$%d", n);'
```

- [ ] **Step 2: 실패 확인.** Run `python3 -m pytest S/tests/test_source.py -q`; 신규 API import 또는 구현 미존재로 FAIL이어야 한다.
- [ ] **Step 3: 추출 구현.** 고정 원본의 types와 공용 모듈을 동봉하고 source/shared를 구현한다. 기존 read_cards를 사용하되 normalize_cards/workbook 의존성은 제거한다. `.original`은 summary만 제거하고 펼친 내용으로 보존한다. 동일 카드에서 중복된 media를 전체 problem 보존과 별도 figures_html에 이중 삽입하지 않는다. 모호한 소문항은 추측하지 않는다. 비어 있지 않은 후보 목록은 안내만 한다.
- [ ] **Step 4: 통과 확인.** Run `python3 -m pytest S/tests/test_source.py -q`; 모두 PASS. S만 별도 임시 디렉터리로 복사하고 source/shared import가 ML·ds-review-pack 없이 성공하는지 확인한다.
- [ ] **Step 5: 변경 검토.** `git diff --check`, `git status --short`로 신규 S 파일만 확인한다. 커밋이 별도 승인되었다면 이 작업 파일만 stage하고 `feat(ds-problem-explain): extract existing review cards`로 커밋한다.

### Task 2: 설명·검토 계약과 자구알 저작 규칙

**Files:** Create S/scripts/mpe_contract.py; S/references/authoring.md, verification.md; S/tests/test_contract.py.

**Interfaces:**
- Consumes: Task 1 Problem/SourcePack 및 `dict[str, str]` 문항별 설명 조각.
- Produces: `validate_fragment(problem: Problem, fragment: str) -> list[str]`, `initial_reviews(pack: SourcePack, fragments: dict[str,str]) -> dict`, `validate_reviews(pack: SourcePack, fragments: dict[str,str], reviews: dict) -> list[str]`, `payload_hash(pack: SourcePack, fragments: dict[str,str]) -> str`, `markup_errors(root: Node, allow_summary: bool = False) -> list[str]`.

- [ ] **Step 1: 실패 테스트 작성.** `test_nested_heading_only_recall_rejected`, `test_every_subpart_requires_solve_verify`, `test_reordered_sections_rejected`, `test_retry_limits`, `test_hidden_body_rejected`, `test_pending_or_disputed_reviews_rejected`, `test_code_dollar_is_not_math`를 작성한다. 마지막 테스트는 설명 pre/code에 `printf("$%d", n);`가 있어도 구분자 오류가 없고 본문 홀수 `$`는 오류인 것을 assert한다.
```python
def test_nested_heading_only_recall_rejected(problem, valid_fragment):
    fragment = replace_recall_body(valid_fragment, '<div><h4>떠올릴 개념</h4></div>')
    assert any('recall' in error for error in validate_fragment(problem, fragment))
```

helpers.py의 `replace_recall_body(fragment: str, body: str) -> str`는 recall wrapper를 유지하고 그 내용만 교체한다.

- [ ] **Step 2: 실패 확인.** Run `python3 -m pytest S/tests/test_contract.py -q`; 신규 계약 미존재 또는 코드 구분자 회귀에서 FAIL.
- [ ] **Step 3: 계약 구현.** 원본 최신 recall 검사를 유지하여 제목만 있는 구역을 거부한다. 수식 검사는 pre/code를 제외한 텍스트로 수행한다. references 지침은 ML/MML 예시를 자구알 자료·C·상태 추적으로 바꾸고 원문 오타·UB/비종료·은행 충돌의 disputed 처리 및 독립 검산을 명시한다. 검토 형식과 허용 method=`exact|symbolic|numerical|proof|qualitative`는 원본 그대로 유지한다. CLI가 의미적 진실을 자동 판정한다고 쓰지 않는다.
- [ ] **Step 4: 통과 확인.** Run `python3 -m pytest S/tests/test_contract.py -q`; 모두 PASS.
- [ ] **Step 5: 변경 검토.** `git diff --check`; 별도 승인된 커밋은 해당 작업 파일만 `feat(ds-problem-explain): enforce explanation review contract`.

### Task 3: 동일 템플릿의 HTML·MD 조립

**Files:** Create S/assets/**, S/scripts/mpe_render.py; S/tests/test_render.py, test_layout.py.

**Interfaces:**
- Consumes: Task 1 SourcePack, Task 2 validate_fragment와 설명 dict.
- Produces: `build_explanation(pack: SourcePack, fragments: dict[str,str], stage: Path, repo: Path) -> Artifacts`, `check_artifacts(pack: SourcePack, artifacts: Artifacts) -> list[str]`, `artifact_hashes(artifacts: Artifacts) -> dict[str,str]`, `names(pack: SourcePack) -> tuple[str,str,str]`, `dump(path: Path, value: object) -> None`.

- [ ] **Step 1: 실패 테스트 작성.** `test_template_bytes_match_pinned_ml`은 고정 Git blob과 동봉 템플릿의 SHA-256 일치를 assert한다. `test_legacy_statement_rendered_once`는 전체 problem/code text가 유지되고 빈 ask 제목과 별도 중복 그림이 없음을 assert한다. `test_ds_namespace_and_names`, `test_local_assets_only`, `test_markdown_code_and_media_preserved`, `test_repeated_svg_ids_scoped`, `test_nfd_image_link_and_missing_anchor`를 추가한다. namespace는 `ds-problem-explain-review-0917-Recursion`, 산출 stem은 `문제설명_0917_Recursion`이다.
```python
def test_template_bytes_match_pinned_ml(skill_dir, pinned_template_sha):
    assert sha256(skill_dir / 'assets/note-template.html') == pinned_template_sha
```

pinned_template_sha는 최초 이식 시 고정 Git blob에서 계산해 fixture/provenance에 리터럴로 저장한다. 실행 중 네트워크나 ML checkout에서 읽지 않는다.

- [ ] **Step 2: 실패 확인.** Run `python3 -m pytest S/tests/test_render.py S/tests/test_layout.py -q`; 파일 미존재/ML 슬롯값에서 FAIL.
- [ ] **Step 3: 렌더러 구현.** template/vendor를 고정 커밋에서 바이트 복사한다. 렌더러 title/course와 RANGE 슬롯만 자구알용으로 바꾼다. ask_html이 빈 문자열이면 제목/본문 래퍼를 생략하며 보존 검사는 이 표현을 지원한다. 원본 링크 검증, scoped SVG ID, 로컬 이미지 복사, Markdown 코드·수식·이미지 보존 검사를 유지한다. 코드 가로 넘침은 템플릿 기존 pre 규칙으로 처리한다.
- [ ] **Step 4: 통과 확인.** Run `python3 -m pytest S/tests/test_render.py S/tests/test_layout.py -q`; 모두 PASS. 템플릿 SHA와 vendor provenance를 독립 재계산한다.
- [ ] **Step 5: 변경 검토.** `git diff --check`; 별도 승인된 커밋은 이 작업 파일만 `feat(ds-problem-explain): render notes with unchanged ML template`.

### Task 4: 검증된 설명만 백업·발행

**Files:** Create S/scripts/mpe_publish.py; S/tests/test_publish.py.

**Interfaces:**
- Consumes: Tasks 1–3 pack, fragments, Artifacts, review dict, 동봉 `publish_files(staged, backup_dir)`.
- Produces: `publish_explanation(pack: SourcePack, artifacts: Artifacts, fragments: dict[str,str], reviews: dict, destination: Path, backup_dir: Path) -> tuple[Path, ...]` (발행된 destination 파일 경로 목록).

- [ ] **Step 1: 실패 테스트 작성.** `test_pending_review_cannot_publish`, `test_changed_fragment_source_reference_artifact_blocks`에서 각 변경별 발행 거부 및 기존 파일 byte 동일을 assert한다. `test_second_replace_failure_restores_existing`는 두 번째 copy/replace에 오류를 주입해 HTML·MD·그림 복구를 assert한다. `test_unrelated_notes_and_bank_unchanged`는 설명 소유 파일 밖 hash 동일을 assert한다. `test_evidence_copied_with_current_hash`를 추가한다.
```python
def test_pending_review_cannot_publish(pack, artifacts, fragments, destination, backups):
    reviews = initial_reviews(pack, fragments)
    before = snapshot_files(destination)
    with pytest.raises(ExplainError, match='발행 보류'):
        publish_explanation(pack, artifacts, fragments, reviews, destination, backups)
    assert snapshot_files(destination) == before
```

helpers.py의 `snapshot_files(root: Path) -> dict[str, bytes]`는 상대경로별 파일 bytes를 반환한다.

- [ ] **Step 2: 실패 확인.** Run `python3 -m pytest S/tests/test_publish.py -q`; 신규 API 미존재로 FAIL.
- [ ] **Step 3: 발행 구현.** ML의 hash/review/references/manifest 검사와 백업 롤백을 이식한다. 동봉 publisher lock namespace를 `ds-problem-explain-locks`로 바꾼다. 과목 checkout이나 기존 복습팩 API를 참조하지 않는다. 다중 파일 발행을 OS 원자적 transaction이라고 표현하지 않는다.
- [ ] **Step 4: 통과 확인.** Run `python3 -m pytest S/tests/test_publish.py -q`; 모두 PASS.
- [ ] **Step 5: 변경 검토.** `git diff --check`; 별도 승인된 커밋은 이 작업 파일만 `feat(ds-problem-explain): gate publication and restore failed replacement`.

### Task 5: CLI·스킬 등록과 전체 흐름

**Files:** Create S/scripts/mpe_cli.py, S/SKILL.md, S/assets/port-provenance.json; .claude/skills/ds-problem-explain symlink; S/tests/test_cli.py, test_skill_files.py.

**Interfaces:**
- Consumes: Tasks 1–4 APIs.
- Produces: `main(argv: list[str] | None = None) -> int`; commands extract(--repo,--target?,--run), build/check/publish(--run). 종료 코드 0=모든 대상 성공, 1=실패/보류 존재. `source.json`, `run.json`, 문항 explanations/, evidence/, stage.json, review.json, machine.json은 ML 계약을 유지한다.

- [ ] **Step 1: 실패 테스트 작성.** `test_extract_build_check_publish_scratch`, `test_rebuild_resets_reviews`, `test_mixed_packs_continue_after_failure`, `test_modified_source_json_rejected`, `test_unsupported_homework_target`, `test_install_has_no_ml_runtime_dependency`, `test_claude_link_and_provenance`를 작성한다. synthetic fixture의 scratch 발행만 허용하고 실제 수업 폴더 hash가 변하지 않았음을 assert한다.
```python
def test_rebuild_resets_reviews(authored_run):
    assert main(['build', '--run', str(authored_run)]) == 0
    review = json.loads((only_pack_folder(authored_run) / 'review.json').read_text())
    assert review['browser']['status'] == 'not_run'
    assert all(item['status'] == 'not_run' for item in review['independent']['items'].values())
```

helpers.py의 `only_pack_folder(run: Path) -> Path`는 run.json의 유일한 target을 읽는다. authored_run fixture는 scratch의 추출·조각·이전 pass 검토를 제공한다.

- [ ] **Step 2: 실패 확인.** Run `python3 -m pytest S/tests/test_cli.py S/tests/test_skill_files.py -q`; CLI·등록 미존재로 FAIL.
- [ ] **Step 3: CLI·지침 구현.** 원본 흐름을 그대로 연결하며 source.json 수동 수정은 기존처럼 거부한다. 지침에 명시 날짜가 비어 있으면 후보를 안내하는 동작, 실제 읽기/검산/브라우저 검토, C 주의사항, 설치 시 산출물 미생성, 추가 확인 없이 검증된 사용자 호출 범위를 발행하는 규칙을 기록한다. CLI 테스트의 검토 pass 주입은 synthetic이며 live 검증을 주장하지 않는다. provenance의 모든 파일 및 동봉 모듈 해시와 변경 이유를 채운다.
- [ ] **Step 4: 전체 통과 확인.** Run `python3 -m pytest S/tests -q` 및 `python3 S/scripts/mpe_cli.py --help`; 모두 PASS/exit 0. 승인된 실행 환경에서 기존 ds-review-pack tests도 한 번 실행해 독립 이식이 기존 도구를 변경하지 않았음을 확인한다.
- [ ] **Step 5: 변경 검토.** `git diff --check`, `git status --short`; 별도 승인된 커밋은 해당 파일만 `feat(ds-problem-explain): register independent review explanation skill`.

### Task 6: 브라우저 수용 검증과 인계

**Files:** Create `docs/verify/2026-10-12-ds-problem-explain.md`; fixture 수정이 필요한 경우 S/tests/helpers.py, test_layout.py만 수정한다.

**Interfaces:**
- Consumes: CLI가 생성한 scratch Artifacts와 원본 template provenance.
- Produces: 실제 확인한 viewport/theme, 자원·오류·스크롤 결과, source/template hashes와 재현 명령이 있는 검증 기록.

- [ ] **Step 1: 검증 fixture 확정.** scratch fixture에 긴 C 코드(`<`, `&`, `$` 포함), 연산 상태 표, 수식, SVG/래스터 그림, (a)/(b) 질문, 요약을 포함한다. 실제 강의 문항을 새로 출제하거나 발행하지 않는다. test_layout에 fixture 요소가 유지되는 assertions를 작성한다.
- [ ] **Step 2: fixture 검사.** Run `python3 -m pytest S/tests/test_layout.py -q`; fixture 추가 전의 누락을 확인한 뒤 fixture를 완성하여 PASS를 확인한다.
- [ ] **Step 3: 실제 브라우저 확인.** scratch stage를 로컬 서버로 열고 1280×900/375×812, light/dark에서 목차·이전/다음·패널 열기/닫기/요약·resize·수식·코드·표·그림을 확인한다. 최종 발행 기준 링크는 실제 원파일/anchor와 별도로 대조한다. 콘솔/KaTeX/누락/외부 요청/문서 가로 넘침 각각 0을 기록한다. 오류면 owning task 코드/fixture를 수정하고 영향 테스트만 재실행한다. 템플릿 자체 수정은 하지 않고 결함을 보고한다.
- [ ] **Step 4: 기록·최종 확인.** 검증 기록에 synthetic UI 검증과 미수행 실제 수업 저작/발행을 구분한다. `git diff --check`와 원자료 hash 보존, template byte 일치, 현재 변경 범위를 확인하고 서버를 종료한다.
- [ ] **Step 5: 인계.** 스킬 경로·호출 예시·검증 결과·제한(최신 0문항, 과제 미지원)을 보고한다. 커밋 승인 시 필요한 검증 기록/수정 파일만 `docs(ds-problem-explain): record browser acceptance`로 커밋한다.

## 자체 검토

- 설계 요구를 Tasks 1–6에 대응: 입력/빈 팩/모호함(1), 저작/의미 검토(2), 템플릿/자원/MD(3), hash·발행·복구(4), 등록/독립성/CLI(5), 실제 화면(6).
- 이후 태스크의 타입은 원본 mpe_types의 동일 계약을 사용하며 새로운 정의되지 않은 데이터 타입을 도입하지 않는다.
- Review Focus 5개를 해당 태스크의 구체적인 회귀 테스트에 연결했다.
- 계획은 구현 함수 본문을 복제하지 않고 이식 경계와 테스트 기대값을 고정한다.
- 실행 방식 선택·계획 확인을 기다리며 이 문서 작성에서는 구현 코드·템플릿·수업 산출물을 변경하지 않는다.
