# 자구알 복습팩 PDF Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 전자회로2 PDF 템플릿을 보존하여 신규·갱신 복습팩에 문제/답안 PDF를 자동 생성하고 기존 9팩에도 18개 PDF를 추가한다.

**Architecture:** 전자회로2 템플릿을 자구알에 고정 복사하고, 저장된 복습문제 HTML을 기존 workbook JSON 계약으로 변환한다. 렌더러는 기존 조판과 16:9 변환을 보존하면서 내용 분할·오프라인 자산·기계 검증을 담당한다. 발행기는 검토된 PDF 쌍과 별도 보고서만 백업 후 교체한다.

**Tech Stack:** Python 3.10+, 표준 unittest, Playwright sync API/Google Chrome, PyMuPDF, KaTeX 0.16.11, Pretendard 1.3.9.

**Spec:** `docs/superpowers/specs/2026-10-13-ds-review-pdf-design.md` (먼저 읽는다).

## Global Constraints

- 원본 템플릿 3개와 render.py 스냅샷의 정확한 SHA-256은 Spec 표와 일치해야 한다.
- 1920×1080px / 1440×810pt(±0.5pt), 하단 180px 예약, 원본 글꼴 배율·레이아웃·Hint 구성을 유지한다.
- 입력 HTML·MD·그림·은행·과거 validation.json을 바꾸지 않는다. PDF 보고서는 `자료_PDF/pdf-validation.json`에 별도로 쓴다.
- 해설지는 기존 `.solution` 전체와 정답을 포함한다. 별도 문제설명 일곱 구역은 포함하지 않는다.
- 코드 개행·들여쓰기·기호·선택지 순서·SVG·표·문항 순서를 보존한다. 템플릿 유지가 내용 삭제를 허용하지 않는다.
- 형제 전자회로2 저장소는 최초 포트의 읽기 전용 출처다. 완성 생성기의 런타임 의존성이 되어서는 안 된다.
- 자동 설치·웹 서비스·Git push·문항 추가·새 템플릿 디자인은 수행하지 않는다. 실행 시작 시 using-git-worktrees로 작업 위치를 결정한다.
- 아래 커밋은 구현 단계의 체크포인트다. 이번 계획 작성 턴은 문서만 저장하고 커밋·구현하지 않는다.

## Review Focus

1. `ol.steps` 밖 완성 C 코드가 있는 입력: 답안에 끝까지 보존한다(Task 1).
2. 긴 코드 줄·넓은 그림·큰 표: 잘림을 검출하고 분할 불가하면 발행을 보류한다(Task 3).
3. NFD 경로·같은 날짜의 여러 HTML: 실제 경로로 각각 처리하며 보고서 충돌을 거부한다(Task 4).
4. 렌더 중 입력 변경·PDF 쌍 중 두 번째 교체 실패: 이전 발행물을 보존하거나 rollback한다(Task 4).
5. 이전 PDF가 있는 팩의 실패·0문항·부분 backfill 실패: stale/skipped/withheld를 구분하고 전체 완료로 보고하지 않는다(Task 4, 6).

---

## 파일 구조와 실행 규약

이 문서의 상대 경로는 자구알 저장소 루트 기준이다. `S=.agents/skills/ds-review-pack`로 표기한다. 실제 호출에는 `--repo`, `--review`, `--run`에 검증한 절대 경로를 넘긴다. 테스트는 기존 `_util.py`를 통해 scripts를 import한다. `python3`에 Playwright와 PyMuPDF가 없다면 실행 가능한 Python 경로를 명시하며 테스트 skip으로 납품 성공을 주장하지 않는다.

| 파일 | 책임 |
|---|---|
| S/assets/pdf/ec2/{problem.html,answer.html,video-16x9.css,render.py} | 변경하지 않는 참조 스냅샷 |
| S/assets/pdf/template-provenance.json | 출처·원본/목적지 해시·포트 허용 범위 |
| S/assets/pdf/vendor/{katex,pretendard}/, provenance.json | 같은 버전 로컬 자산·라이선스·해시 |
| S/scripts/pdf_types.py | 카드·블록·페이지·보고서 자료형과 PdfError |
| S/scripts/pdf_cards.py | 원본 HTML 추출·블록 보존·JSON adapter |
| S/scripts/pdf_render.py | 고정 템플릿 로딩·자산 라우팅·A4 측정·PDF/DOM 검사 |
| S/scripts/pdf_layout.py | 실측 기반 공통 페이지 분할 |
| S/scripts/pdf_publish.py | 검토/해시 게이트·잠금·백업·rollback |
| S/scripts/review_pdf.py | build/check/publish/backfill CLI와 발견 |
| S/references/pdf-build.md | 신규·갱신·backfill 실행과 실제 검토 절차 |
| S/tests/test_pdf_{cards,template,layout,publish,cli,delivery}.py | 책임별 회귀 테스트 |
| S/tests/fixtures/pdf/ | 최소 카드·긴 코드·SVG·오류 입력 |
| S/SKILL.md, references/textbook-update.md | PDF 단계 연결 |
| 복습노트/<range>/*-{문제,답안}.pdf, 자료_PDF/pdf-validation.json | 납품물과 별도 검증 증거 |

### Task 1: 손실 없는 카드 추출과 workbook adapter

**Files:** Create `S/scripts/pdf_types.py`, `S/scripts/pdf_cards.py`, `S/tests/test_pdf_cards.py`, `S/tests/fixtures/pdf/cards.html`.

**Interfaces:**
- `PdfError(ValueError)`.
- frozen `Block(kind: str, html: str, text: str)`; kind는 prose/code/table/figure다. code.text는 HTML entity를 복원한 원본 코드다.
- frozen `Card(id: str, source: str, kind: str, title: str, problem: tuple[Block,...], solution: tuple[Block,...], answer_html: str, hint_html: str)`.
- frozen `Pack(source: Path, source_sha256: str, range: str, slug: str, cards: tuple[Card,...])`.
- `read_pack(review: Path) -> Pack`; `to_payload(pack: Pack, mode: Literal['problems','answers'], pages: tuple[PageSlice,...], assets: Path) -> dict`.
- frozen `PageSlice(logical_id: str, physical_id: str, continuation: int, problem: tuple[Block,...], solution: tuple[Block,...], show_answer: bool, show_hint: bool)`. continuation는 1부터다.

- [ ] **Step 1: failing tests 작성.** `test_solution_extra_code_preserved`: 실제 1005 P4에서 추출한 code.text가 `.solution > pre`의 entity 복원 문자열과 같다. `test_problem_payload_has_no_solution`: JSON 모든 entry에 solution 키가 없다. `test_escaped_c_and_svg`: `p->link`, `<`, `&&`, `printf("\\n")`, SVG 참조·선택지 순서가 유지된다. `test_invalid_card_rejected`: 중복 p1 또는 비어 있는 답은 PdfError, 0카드는 빈 Pack이다.
- [ ] **Step 2: red 확인.** `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p test_pdf_cards.py -v`; 아직 모듈 없음으로 FAIL.
- [ ] **Step 3: 자료형·read_pack 구현.** 기존 `html2md.Builder/Node/serialize`를 사용하되 ds-problem-explain vendor 파서에 런타임 의존하거나 그 파일을 수정하지 않는다. solution은 steps 밖 직접 자식까지 원래 순서로 수집한다. 제목의 P번호는 중복되지 않게 제거해 header 번호 필드로 전달한다.
- [ ] **Step 4: to_payload 구현.** 전체 질문은 ask, conditions/original은 빈 문자열. 교과서는 연습문제, 기출은 기출, 나머지는 장말문제다. section은 source ID, book_page=null, difficulty=0, sol=false, original_lang='ko'다. 그림은 독립 SVG/img 자산과 w_mm/h_mm로 연결한다. 풀이 각 블록은 steps의 label=''와 html로 전달하고 answer는 마지막 조각만 표시한다. hint는 기존 내용을 label='풀이 방향', html=hint_html로 연결한다. JSON 주입에는 원본 inject와 같은 `<` escape를 사용한다.
- [ ] **Step 5: green 확인.** Step 2 명령 PASS; 추가로 실팩 9개의 카드 개수 `[4,12,12,8,4,4,4,4,12]`와 합계 64를 검사한다.
- [ ] **Step 6: checkpoint commit.** 위 네 파일만 stage하고 `git diff --cached --check`; `feat: preserve ds review cards for pdf export`.

### Task 2: 전자회로2 템플릿 고정 포트와 오프라인 렌더

**Files:** Create `S/assets/pdf/`의 위 스냅샷·vendor·provenance, `S/scripts/pdf_render.py`, `S/tests/test_pdf_template.py`, `S/tests/fixtures/pdf/workbook.json`.

**Interfaces:**
- 소비: Task 1 payload와 PdfError.
- frozen `Probe(page_ids: tuple[str,...], overflow: tuple[str,...], errors: tuple[str,...], geometry: dict, typography: dict)` (pdf_types.py에 추가).
- `load_template(mode: str, layout: str) -> str`, `inject(template: str, data: dict) -> str`.
- `probe(data: dict, mode: str, layout: str, run: Path) -> Probe`.
- `render(data: dict, mode: str, run: Path, pdf: Path) -> Probe`: A4 probe의 typography를 주입해 16:9 render한다.

- [ ] **Step 1: failing tests 작성.** `test_pinned_template_hashes`: Spec의 네 해시 그대로 assert. `test_injected_layout_matches_ec2`: 로컬 frozen render.py의 load_template/inject 출력과 새 모듈 출력 문자열이 같다(참조 import 시 paths.TEMPLATES를 임시 모듈로 공급). `test_offline_ready_and_geometry`: 외부 fetch 차단 상태 ready=true, MediaBox=(1440,810)±0.5pt, caption 영역에 본문 없음. `test_missing_font_or_math_fails`: route 누락은 Probe.errors에 기록되어 성공으로 간주되지 않는다.
- [ ] **Step 2: red 확인.** `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p test_pdf_template.py -v`; 미구현으로 FAIL.
- [ ] **Step 3: 스냅샷·vendor를 복사.** 원본 네 파일의 해시를 다시 확인한 뒤 bytes 그대로 복사한다. 기존 ds-problem-explain/assets/vendor에서 같은 버전의 폰트·KaTeX·라이선스를 독립 복사한다. provenance에 원본 위치와 해시, 복사 해시를 기록한다.
- [ ] **Step 4: 렌더 모듈 구현.** Chrome channel='chrome', viewport=1400×1000, ready timeout=120000ms, prefer_css_page_size=true, print_background=true. CDN root 및 상대 폰트 요청을 로컬 자산으로 route.fulfill하고 그 밖의 네트워크는 오류로 기록한다. .katex-error, console/pageerror, 실패 자원, 이미지 naturalWidth=0, panel/work/pre/table/figure의 실제 경계를 검사한다. 원본 템플릿이 수식 렌더 함수를 못 찾고도 ready=true가 될 수 있으므로 ready만 검사하지 않는다.
- [ ] **Step 5: green/시각 동등성 확인.** Step 2 PASS. 같은 최소 workbook JSON으로 frozen 참조 경로와 새 경로를 렌더하고 첫 문제·답안 페이지를 비교한다. geometry, 글꼴 배율, 격자, Hint, footer가 일치한다. browser build 차이로 픽셀 차이가 있으면 이유를 기록하고 실제 검토한다.
- [ ] **Step 6: checkpoint commit.** 이 Task의 자산·모듈·테스트만 stage, cached diff check, `feat: reuse frozen ec2 pdf templates`.

### Task 3: 긴 질문·코드·해설을 공통 페이지로 분할

**Files:** Create `S/scripts/pdf_layout.py`, `S/tests/test_pdf_layout.py`, `S/tests/fixtures/pdf/long-code.html`, `wide-figure.html`; modify `S/scripts/pdf_types.py` 자료형만.

**Interfaces:**
- 소비: Pack/Block/PageSlice, to_payload, probe.
- `plan_pages(pack: Pack, run: Path) -> tuple[PageSlice,...]`.
- `check_coverage(pack: Pack, pages: tuple[PageSlice,...]) -> list[str]`.
- 반환 pages는 문제/답안에 공통 사용, show_answer는 마지막 조각만, show_hint는 첫 조각만이다.

- [ ] **Step 1: failing tests 작성.** `test_long_code_reconstructed_exactly`: 분할 후 code.text를 이어 붙이면 원본과 같다(최종 개행 포함). `test_paired_page_plan`: 문제/답안의 logical_id·physical_id·질문 내용은 동일하며 마지막만 정답. `test_wide_svg_or_unbreakable_line_withheld`: 원본 fitting 후에도 넘치는 입력은 PdfError에 pN과 영역을 포함한다. `test_no_progress_guard`: probe가 계속 overflow를 반환하면 반복이 종료되고 원본 내용은 그대로다.
- [ ] **Step 2: red 확인.** `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p test_pdf_layout.py -v`; 모듈 없음으로 FAIL.
- [ ] **Step 3: plan_pages 구현.** 템플릿 fitting을 먼저 실행하고 문제·답안 중 하나라도 overflow면 양쪽 공통 페이지 계획을 조정한다. 질문은 블록/목록 항목, 해설은 블록/코드 개행 경계로 나누며 source block 인덱스와 코드 줄 구간을 추적한다. 최소 한 블록/줄을 소비하는 greedy prefix를 실제 probe로 확인한다. 문항당 128조각 초과·소비량 0·단일 불가 블록은 PdfError다. 글꼴/CSS는 덮어쓰지 않는다.
- [ ] **Step 4: check_coverage 구현.** 모든 논리 문항이 순서대로 있고, 각 source block/코드 줄은 1회씩 포함하며 답·힌트 표시는 지정한 조각에만 존재해야 한다. 그림 자산 해시와 연결을 검사한다. 자연어 공백 정규화로 코드 검증을 대체하지 않는다.
- [ ] **Step 5: green 확인.** Step 2 PASS. 실제 0917·0921·1005의 완성 코드와 1012 긴 해설을 stage로 렌더하고 잘림을 직접 확인한다.
- [ ] **Step 6: checkpoint commit.** 이 Task 파일만 stage/cached diff check, `feat: paginate ds pdf content without truncation`.

### Task 4: CLI·팩 발견·검토 게이트·안전한 발행

**Files:** Create `S/scripts/pdf_publish.py`, `S/scripts/review_pdf.py`, `S/tests/test_pdf_publish.py`, `S/tests/test_pdf_cli.py`.

**Interfaces:**
- `discover_reviews(repo: Path, target: str) -> tuple[Path,...]`: target은 all 또는 MMDD/MMDD-MMDD, 날짜와 이름을 NFC로 비교하고 실제 경로를 반환한다.
- `build_pack(review: Path, run: Path) -> Path`: run 아래 stage와 report.json을 생성하고 그 report 경로를 반환한다.
- `check_stage(run: Path) -> list[str]`: 내용 coverage, 자산, PDF 페이지 크기/개수/텍스트, Probe.errors/overflow 검사.
- `publish_stage(run: Path, repo: Path) -> Path`: backup 경로 반환. run/review.json의 실제 browser 승인과 stage artifact SHA-256이 일치해야 한다.
- CLI: `build --review ABS --run ABS`; `check --run ABS`; `publish --run ABS --repo ABS`; `backfill --repo ABS --target all --run ABS`.
- backfill은 팩별 build/check만 수행해 summary.json을 출력한다. 실제 화면 검토 후 각 팩 publish를 실행한다. 결과 상태는 staged/skipped/withheld/published/stale, withheld/stale 존재 시 exit=1이다.

- [ ] **Step 1: failing tests 작성.** `test_nfd_discovery_and_report_collision`: NFC/NFD와 기간을 발견하며 같은 폴더에 리뷰 2개면 공유 report 충돌을 PdfError로 거부한다. `test_source_change_blocks_publish`: source bytes 변경 후 최종 대상 그대로. `test_second_replace_rolls_back`: 두 번째 os.replace 실패 시 첫 PDF와 report도 원래 bytes. `test_unreviewed_stage_rejected`: browser 승인 없음/해시 변경이면 발행 안 됨. `test_zero_cards_and_partial_failure`: 0문항 skipped, 다른 팩 staged, 실패 팩 withheld와 exit=1. `test_lock_contention`: 두 발행기가 같은 팩을 동시에 교체할 수 없다. `test_failed_rebuild_marks_previous_stale`: 보고서는 새 staged 실패를 명시하며 이전 PDF 성공으로 대체하지 않는다.
- [ ] **Step 2: red 확인.** `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p 'test_pdf_p*.py' -v`와 `-p test_pdf_cli.py`; 미구현으로 FAIL.
- [ ] **Step 3: build/check/discovery 구현.** stage에 PDF 두 개·report·자산·페이지 PNG를 둔다. report는 Spec의 hashes/ids/coverage/page_mapping/checks를 기록한다. build마다 review를 not_run으로 초기화하며 테스트 fixture의 pass 기록을 실제 보고서로 복사하지 않는다. JSON 입력이 문제지에서 풀이·정답을 제외하는지 다시 검사한다.
- [ ] **Step 4: 발행기 구현.** 팩 단위 fcntl 잠금, 입력 재해시, 승인된 stage 해시 검증, 임시 파일 fsync/os.replace, 고유 backup, 실패 시 역순 복구. 새 파일은 rollback에서 제거한다. lock 파일 inode를 실행 중 삭제하지 않는다. 이전 해설 vendor 파일은 수정하지 않고 필요한 발행 알고리즘만 독립 구현한다.
- [ ] **Step 5: green 확인.** Step 2 PASS; 임시 repo에서 build→check→실제 렌더 검토→publish 후 PDF 두 개와 report가 함께 존재하며 원본 HTML hash는 같다.
- [ ] **Step 6: checkpoint commit.** 이 Task 파일만 stage/cached diff check, `feat: add staged ds pdf build and publication`.

### Task 5: 신규·lite·기존 갱신 흐름에 PDF 연결

**Files:** Modify `S/SKILL.md` 산출물·8/9단계·오류 처리, `S/references/textbook-update.md` 8/9단계; create `S/references/pdf-build.md`; modify `S/tests/test_skill_files.py`.

**Interfaces:** 소비: Task 4의 정확한 build/check/publish CLI. 외부 입력은 최종 검증된 리뷰의 절대 경로이며 날짜/최신 팩으로 추측하지 않는다.

- [ ] **Step 1: failing tests 작성.** `test_pdf_flow_contract`: SKILL에 pdf-build 참조와 pdf 두 개가 있고 신규/lite/update-existing 모두 연결한다. pdf-build는 정확한 build/check/publish 인자를 안내하며 backfill은 update-existing를 호출하지 않는다. `test_pdf_failure_independent_of_explanation`: PDF/문제설명 각각의 발행·보류를 보고하고 이전 자료는 보존한다.
- [ ] **Step 2: red 확인.** `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p test_skill_files.py -v`; 새 계약 assert FAIL.
- [ ] **Step 3: 지침 수정.** 기존 0~9/B1~B4 구조를 보존한다. 최종 리뷰 검증 후 pdf-build 절차를 호출하고 전체 페이지를 실제 검토해 review.json에 artifact_hashes와 pass를 기록한 뒤 publish한다. 0문항 skip, 실패/stale 보고, lite에서 PDF 검증 생략 금지를 명시한다. 기존 backup.py는 복습문제 prefix의 pdf도 이미 백업하므로 불필요하게 수정하지 않는다.
- [ ] **Step 4: green 확인.** Step 2 PASS 및 `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -v` PASS. 환경 의존 검사에 필요한 Python을 명시하고 skip 목록/이유를 보고한다. 새 코드가 기존 설명을 바꾸지 않았음을 ds-problem-explain의 기존 테스트로 확인한다.
- [ ] **Step 5: checkpoint commit.** 이 Task 네 파일만 stage/cached diff check, `docs: include pdf export in ds review pack workflows`.

### Task 6: 기존 9개 팩 실제 PDF 납품과 전체 검증

**Files:** Create 발견한 각 `복습노트/<range>/복습문제_<range>_<slug>-문제.pdf`, `-답안.pdf`, `자료_PDF/pdf-validation.json`; create `S/tests/test_pdf_delivery.py`. 임시 render/PNG/백업은 외부 RUN에만 둔다.

**Interfaces:** 소비: discover_reviews/backfill/check/publish 및 report schema. 이 Task의 산출물은 실제 승인된 PDF 18개와 별도 보고서 9개다.

- [ ] **Step 1: failing delivery test 작성.** `test_existing_pack_pdf_coverage`: 현재 9팩 `[0907,0914,0917,0921,0928,1001,1005,1008,1012]`, 개수 `[4,12,12,8,4,4,4,4,12]`, source/template/artifact 해시·실제 page mapping 일치. PDF는 각 MediaBox=1440×810±0.5pt, logical IDs 전체 포함, checks/browser 모두 pass. `test_inputs_unchanged`: RUN에 기록한 before 해시와 HTML·MD·그림의 after 해시 일치. 납품 전 PDF 없음으로 FAIL해야 한다.
- [ ] **Step 2: red 확인.** `python3 -m unittest discover -s .agents/skills/ds-review-pack/tests -p test_pdf_delivery.py -v`; 아직 납품 PDF 없음으로 FAIL.
- [ ] **Step 3: 재발견·보존 snapshot.** 실제 9팩/64문항인지 확인하고 입력 HTML·MD·그림·기존 제작자료와 전자회로2 참조 파일의 SHA-256을 RUN/before.json에 기록한다. 목록이 달라지면 실제 대상과 이유를 보고하고 test 기대값을 검증된 목록으로 갱신한다.
- [ ] **Step 4: backfill 실행.** `python3 .agents/skills/ds-review-pack/scripts/review_pdf.py backfill --repo "$REPO" --target all --run "$RUN"`; 9팩 staged, withheld=0, exit=0. 실패 팩이 있으면 원본을 바꾸지 않고 생성기·adapter·분할을 수정해 재생성한다. 템플릿 변경이 필요하다면 사용자에게 구체적 변경안을 별도로 확인한다.
- [ ] **Step 5: 모든 페이지 실화면 검토.** RUN 아래 PNG를 view_image로 확인하고 문제/답안/힌트/연속 페이지·코드·SVG·하단 자막 영역을 검사한다. 오류 수정 후 build부터 다시 실행한다. 검토한 현재 stage의 SHA-256에만 실제 승인 기록을 남긴다.
- [ ] **Step 6: 팩별 publish.** Task 4 CLI로 승인된 9팩을 발행한다. PDF 18개·보고서 9개를 확인하고 입력 및 전자회로2 파일의 before/after 해시가 같은지 증명한다.
- [ ] **Step 7: green/전체 검사.** Step 2 PASS, 전체 ds-review-pack tests PASS, `git diff --check` PASS. 원본 HTML 소스가 아니라 최종 PDF에서 MediaBox·텍스트 코드·폰트와 렌더 이미지를 검사한다. 반복 backfill의 논리 page mapping·내용 해시가 동일한지 확인한다(PDF 생성 시간 metadata 때문에 bytes 동일성을 요구하지 않는다).
- [ ] **Step 8: 최종 checkpoint commit.** 새 PDF 18개·새 report 9개·delivery test만 정확히 stage하고 cached diff/stat/check 검토 후 `docs: add pdf worksheets to existing ds review packs`. push는 하지 않는다. 최종 보고에 실제 납품 경로, 팩/문항/페이지 수, 보존 해시, 검증 결과, 미해결과 backup/RUN 경로를 적는다.

## 자체 검토 결과

- Spec coverage: 템플릿/Hint 유지(Task 2), 내용 보존(Task 1/3), 신규·갱신 연결(Task 5), 9팩 납품(Task 6), 잠금·rollback·stale(Task 4)를 모두 배정했다.
- Step scan: 각 단계에 파일·함수/명령·판정 기준을 지정했다. renderer를 구현 코드 전체로 미리 작성하지 않았다.
- Type consistency: Pack→PageSlice→payload→Probe→stage report를 같은 함수명/자료형으로 연결했다.
- Review Focus: 다섯 위험을 위 Task의 구체적 테스트에 배정했다.
- Proportion: 6개 작업으로 나눴으며 자산 설정은 renderer 작업, 지침은 흐름 연결 작업에 포함했다. 구현은 별도 승인 후 시작한다.
