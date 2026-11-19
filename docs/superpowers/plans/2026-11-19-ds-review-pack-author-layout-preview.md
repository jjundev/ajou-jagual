# `ds-review-pack` 작성 단계 레이아웃 검증 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 신규 복습팩 작성자가 실제 템플릿에서 수식 넘침, 좁은 풀이 패널의 작은 그림 글자, 강의 예제의 PDF 쪽 분할을 조립 전에 발견하게 한다.

**Architecture:** 선택한 조각을 기존 조립기로 렌더링하고 동일한 브라우저 측정 함수를 작성 단계와 최종 검사에서 호출한다. 강의 예제는 기존 PDF 배치기를 시험 실행한다. 신규 모드의 최종 발행은 실제 화면 승인에 더해 현재 요청에 대한 조합별·영역별 측정 기록을 요구한다.

**Tech Stack:** Python 3.10+, JavaScript DOM 측정, Playwright와 설치된 Google Chrome, pytest, 기존 브라우저·PDF 템플릿.

**Spec:** 직전 `grill-yourself` 설계의 `#1=작성 단계 검증`. 실행자용 사본은 이 문서의 [설계 기준](#설계-기준)에 포함한다.

## Global Constraints

- 적용 대상은 신규 `new` 복습팩이다. 작성 검사는 `375×812`와 `1280×900` 라이트 모드, 최종 검사는 두 크기 × 두 테마 × 정리노트·복습문제의 8개 조합이다.
- 실제 SVG 글자 높이 9 CSS px 미만은 결함, 9 이상 12 미만은 실화면 판독성 확인 대상, 12px은 주요 라벨 작성 목표다. 수식은 렌더링된 바깥 가로 넘침으로 판단한다.
- 작성자의 산출물은 자기 `RUN/work/preview/` 아래에 둔다. 최종 검사자는 현재 `RUN/browser/<attempt>/`에만 검사 기록을 쓴다. 팩 교체는 기존 메인 발행 경로를 사용한다.
- 신규 검사 명령에 사용할 Python과 설치된 Chrome을 확인한다. 자동 설치나 외부 자원 요청 없이 기존 번들 자원을 사용한다. 작성 단계의 `unavailable`은 조립본 검사를 통해 확인한다.
- 최종 수동 실화면 승인, 입력 해시, 기존 팩 잠금·백업, 브라우저 수정 2회 한도, 0문항 PDF `skipped`를 유지한다. `bank`, 갱신 모드, PDF 공통 출력 수정 및 분류기 수정, 제작자료 재현성, 후속 작업 선행 실행은 별도 범위다.
- 새 테스트는 임시 RUN 또는 임시 저장소에서 재현한다. 실제 날짜별 발행본에 쓰지 않는다. 작업별 커밋은 승인된 실행 범위의 파일만 포함한다.

## Review Focus

1. 활성 카드의 풀이가 오른쪽 패널로 이동했고 이전 카드 풀이가 DOM에 남아 있음 → 현재 카드의 열린 영역만 잰다. Task 1 `test_measures_active_solution_in_both_widths`.
2. 큰 그림의 내부 스크롤과 패널 자체의 잘림이 동시에 존재함 → 내부 스크롤은 허용하고 바깥 넘침은 검출한다. Task 1 `test_local_scroll_is_allowed_but_panel_overflow_fails`.
3. 다른 작성자의 조각이 아직 없거나 현재 조각의 상대 경로 자원이 깨짐 → 요청한 조각의 파일로 렌더링하고 자원 누락을 정확히 보고한다. Task 2 `test_preview_uses_only_selected_fragments`와 `test_preview_reports_missing_local_asset`.
4. 답안만 다음 쪽으로 이어짐 → 문제지 한 쪽인 강의 예제로 판정한다. Task 3 `test_solution_continuation_does_not_count_as_question_page`.
5. 새 요청의 조합별 통과 표시는 모두 있으나 풀이 영역 한 줄이 빠지거나 측정 파일이 교체됨 → 발행 전에 거부한다. Task 4 `test_v2_publish_rejects_incomplete_layout[missing-solution]`, `[changed-measurements]`.

---

## 설계 기준

- 작성자는 담당 섹션 하나 또는 선택한 카드 묶음의 실제 레이아웃을 확인한다. 정리노트는 본문·요약과 위젯을, 카드는 문제·원문·힌트·풀이를 검사한다. 최종 검사자는 동일한 측정값과 실제 화면을 근거로 승인한다.
- 자료에 딸린 내부 스크롤은 허용한다. 바깥 본문이나 패널에서 내용이 잘리는 경우를 검출한다. 글자가 포함된 이미지 등 DOM에서 크기를 얻을 수 없는 그림은 수동으로 확인한다. 최소 높이 9–12px 구간은 측정값과 판독 근거를 남긴다.
- 작성 단계의 `lecture-code` 시험은 기존 배치기로 문제지 쪽 수, 조건과 질문의 출력 위치를 알려준다. 여러 쪽이 필요한 예제는 작성자가 사유와 보고서를 메인에 넘긴다. PDF 출력이나 원본 요약을 수정하는 절차에는 영향이 없다.
- 신규 최종 요청과 검사 기록에 영역별 증거를 추가한다. 기존 요청·산출물 해시 검사 및 실화면 승인 요건을 적용한 뒤 발행한다. 브라우저 승인이 끝난 조립본을 전체 PDF 쪽별 검토에 사용한다.

## 파일 지도

| 파일 | 책임 |
|---|---|
| `.agents/skills/ds-review-pack/scripts/measure_layout.js` | 활성 영역의 그림·글자와 가로 넘침의 DOM 측정 |
| `.agents/skills/ds-review-pack/scripts/browser_layout.py` | 기대 영역 계산, Chrome에서의 화면 전환과 측정, 결과 판정 규칙 |
| `.agents/skills/ds-review-pack/scripts/preview_layout.py` | 작성용 조각 조립, PDF 시험 배치, 조립본 측정 명령과 기록 경로 |
| `.agents/skills/ds-review-pack/scripts/browser_review.py` | 신규 요청 v2의 필수 영역과 현재 측정 기록 검증 |
| `.agents/skills/ds-review-pack/SKILL.md`, `references/content-rules.md`, `references/card-rules.md`, `references/browser-check.md` | 0·3·7·8단계 연결과 작성자·검사자 입출력 |
| `.agents/skills/ds-review-pack/tests/test_browser_layout.py`, `test_preview_layout.py`, `test_review_source.py`, `test_skill_files.py` | 브라우저 재현, CLI·PDF 배치, 발행·절차 회귀 |

이하 작업의 파일 경로는 `.agents/skills/ds-review-pack/` 기준이다. 저장소 루트에서 테스트할 때 `SKILL=.agents/skills/ds-review-pack`을 지정하고, `TEST_PYTHON`은 pytest와 Playwright가 설치된 Python의 절대 경로를 지정한다. 실제 배치 테스트에서는 `chromium.launch(channel="chrome")`가 성공해야 한다.

### Task 1. 브라우저가 현재 화면의 각 영역을 측정한다

**Files**

- Create `scripts/browser_layout.py`, `scripts/measure_layout.js`, `tests/test_browser_layout.py`.
- Reuse `assets/note-template.html`, `assets/review-template.html`, `tests/_util.py`.

**Interfaces**

- `browser_layout.expected_scopes(manifest: dict, kind: str) -> tuple[tuple[str, str], ...]`. `kind`는 `note|review`. 두 종류 모두 `("hero", "body")`를 포함한다. 노트는 모든 토픽의 `body`와 `layers`가 비어 있지 않은 토픽의 `summary`를 포함한다. 카드는 `problem`, `original`, `hint`, `solution`을 포함한다.
- `browser_layout.measure_case(browser: Browser, page_path: Path, case: str, scopes: Sequence[tuple[str, str]]) -> CaseLayout`. 예시 `case`는 `review/375x812/light`. `CaseLayout`은 `{rows: list[ScopeRow], errors: list[str]}`다. `ScopeRow`는 `{id: str, area: str, state: str, overflow_px: float, svg_text_count: int, min_svg_text_height_px: float | None, widget_min_svg_text_height_px: dict[str, float | None]}`다. `state`는 `measured|no-figure|visual-only`. `visual-only`는 이미지나 DOM 높이를 얻을 수 없는 그림을 하나라도 포함한 영역이며, 같은 영역의 측정 가능한 SVG 높이도 보존한다. 글자가 없는 인라인 SVG는 `measured`, `svg_text_count=0`, 최솟값 `null`이다.
- `browser_layout.has_layout_defect(row: ScopeRow) -> bool`은 `overflow_px > 1` 또는 글자 최솟값 `< 9`일 때 참이다. `browser_layout.needs_visual_check(row: ScopeRow) -> bool`은 `visual-only` 또는 `9 <= min_svg_text_height_px < 12`일 때 참이다. 기준값 비교 전 반올림은 하지 않는다.
- `scripts/measure_layout.js`는 `(root, scroller) => { ... }` 형식의 함수 식으로 저장한다. Playwright와 수동 도구가 같은 함수 식을 평가할 수 있다. `id`와 `area`는 호출자가 붙인다.

- [ ] **1. 재현 테스트를 쓴다.** `MINI_RUN`에서 실제 조립한 HTML과 Chrome을 사용한다. 픽스처 안 SVG에서 `viewBox`와 배치 방향만 바꿀 수 있게 한다. 새 테스트의 핵심 단언은 아래와 같다.

  ```python
  # test_measures_active_solution_in_both_widths
  assert bad["id"] == "p9" and bad["area"] == "solution"
  assert 0 < bad["min_svg_text_height_px"] < 9
  assert fixed["min_svg_text_height_px"] >= 12
  assert not has_layout_defect(fixed)
  # test_local_scroll_is_allowed_but_panel_overflow_fails
  assert internal_scroll["overflow_px"] <= 1
  assert overflowing_panel["overflow_px"] > 1
  # test_inline_math_overflow_and_split_formula
  assert original["overflow_px"] > 1 and split["overflow_px"] <= 1
  # test_height_thresholds_and_external_image
  assert [has_layout_defect(row(h)) for h in (8.99, 9.0, 12.0)] == [True, False, False]
  assert [needs_visual_check(row(h)) for h in (9.0, 11.99, 12.0)] == [True, True, False]
  assert image_row["state"] == "visual-only"
  assert textless_svg["state"] == "measured" and textless_svg["svg_text_count"] == 0
  assert textless_svg["min_svg_text_height_px"] is None
  ```

  P9는 네 신장 트리를 한 줄에 그린 버전과 2×2 버전을 두 폭에서 비교한다. 그 앞 카드에 더 작은 풀이 그림을 넣어 활성 풀이 선택의 정확성을 확인한다. 수식은 s3의 간선 일곱 개를 KaTeX 인라인 하나에 넣은 버전과 분리한 버전을 사용한다. 위젯 픽스처에서는 `widget_min_svg_text_height_px`에 실제 위젯 ID가 들어가는지 확인한다. `test_missing_required_panel_is_error`에서 필요한 풀이가 없는 카드는 `errors`에 `p9/solution`이 있고 성공 행이 없는지 확인한다.
- [ ] **2. 실패를 확인한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_browser_layout.py" -q`에서 새 측정 모듈이나 함수가 없어 실패하는지 확인한다.
- [ ] **3. DOM 함수 식을 구현한다.** `getBoundingClientRect().height`로 활성 영역의 텍스트를 잰다. 숨겨진 요소, 접근성용 `.katex-mathml`, 아이콘을 제외한다. 현재 콘텐츠의 스크롤 컨테이너 경계와 넘친 요소를 대조한다. `.figure-scroll`, `.table-wrap`, `pre`, `.katex-display`의 내부는 독립 영역으로 보고 래퍼 자체의 경계를 검사한다. `img`, 외부 SVG 참조 및 측정할 수 없는 글자가 든 그림은 수동 확인 대상으로 기록한다.
- [ ] **4. Python 측정기를 구현한다.** 각 조합에 별도 브라우저 컨텍스트를 쓰고 로컬 파일 또는 실화면 도구의 루프백 서버만 이용한다. `document.fonts.load()`와 KaTeX 로드, 화면의 양수 폭을 확인한다. `location.hash`로 이동한 뒤 현재 화면과 활성 `.aid`/`.sum`이 갱신되기를 기다린다. `.aid`에 카드 ID 속성이 없으므로 `od:screen` 이후 유일하게 보이는 그룹에서 현재 카드의 세 `details`를 찾는다. 오른쪽 패널은 실제 토글로 열고 세부 영역의 `summary`를 펼친다. 자원 오류·페이지 오류·필수 영역 누락은 `errors`에 기록한다. 검사 컨텍스트의 저장 상태는 그 컨텍스트 닫을 때 폐기한다.
- [ ] **5. 브라우저 회귀를 확인한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_browser_layout.py" "$SKILL/tests/test_panel_titles_browser.py" -q`에서 관련 테스트가 모두 통과하고 Chrome 테스트가 실제 실행되는지 확인한다.
- [ ] **6. 승인된 경우 작업 파일을 커밋한다.** `feat(review-pack): measure rendered topic and card layout`.

### Task 2. 작성자가 전체 팩 조립 전에 담당 조각을 시험한다

**Files**

- Create `scripts/preview_layout.py`, `tests/test_preview_layout.py`.
- Reuse `scripts/assemble.py:77`, `scripts/manifest.py`, `scripts/pdf_render.py:34`.

**Interfaces**

- `preview_layout.build_author_page(run: Path, output: Path, *, section: str | None, cards: Sequence[str]) -> tuple[Path, dict]`. 두 번째 값은 기대 영역을 계산할 manifest 사본이다. `output`은 호출마다 새 디렉터리다.
- `preview_layout.main(argv: list[str] | None = None) -> int`. 명령은 `preview_layout.py preflight` 및 `preview_layout.py author --run RUN (--section SID | --card PID [--card PID ...])`다. `preflight`는 선택된 Python에서 기존 `render_session()`으로 Chrome을 한 번 열고 종료한다. `author`는 한 줄 요약과 `RUN/work/preview/<대상>-<고유번호>/layout.json` 경로를 출력한다.
- 작성 결과는 `{version: 1, status: "pass" | "fail" | "unavailable", cases: dict[str, CaseLayout], issues: list[str]}`다. `pass=0`, `fail=1`, `unavailable=2`로 반환한다. 수동 확인 대상은 작성 보고서에서 진단으로 남기고 최종 검사에서 확인한다. 명령 형식 오류는 `argparse`가 처리한다.

- [ ] **1. 작성 진입점 테스트를 쓴다.** `MINI_RUN`의 한 섹션을 남기고 다른 섹션 파일을 제거한 사본과, manifest에 파일이 아직 없는 두 번째 카드를 추가한 사본을 이용한다. `test_preview_uses_only_selected_fragments`, `test_preview_reports_missing_local_asset`, `test_preview_can_report_unavailable`, `test_author_cli_returns_both_light_cases`에 아래 핵심 단언을 넣는다.

  ```python
  assert [section["id"] for section in partial_note["sections"]] == ["s1"]
  assert [card["id"] for card in partial_review["problems"]] == ["p1"]
  assert original_manifest.read_bytes() == before
  assert any("missing.svg" in error for error in report["issues"])
  assert unavailable_report["status"] == "unavailable" and unavailable_rc == 2
  assert set(card_report["cases"]) == {"review/375x812/light", "review/1280x900/light"}
  ```

  `test_author_rejects_unknown_id`는 존재하지 않는 `p99`를 넘겨 `fail`과 ID가 찍히는지 확인한다. 정상 자원 사례에는 `RUN/.pack/figures_1119/` 아래의 SVG를 상대 경로로 참조하는 조각을 써서 미리보기에서도 로드되는지 확인한다.
- [ ] **2. 실패를 확인한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_preview_layout.py" -q`에서 작성 명령 또는 입력 조각 렌더링이 구현되지 않아 실패하는지 확인한다.
- [ ] **3. `build_author_page()`를 구현한다.** 원본 manifest를 `manifest.load()`로 검증한 뒤 복제해서 지정한 섹션 또는 카드와 해당 파트만 유지한다. 이 부분 집합을 전체 팩용 manifest 검사에 다시 넣지 않는다. `build_note()` 또는 `build_review()`와 기존 파일명 함수를 호출한다. 공용 자원 URL은 기존 조립기로 해석한다. 조각의 팩 상대 자원은 `RUN`을 기준으로 찾아 미리보기의 동일 상대 경로에 복사한다. 원격 자원과 `RUN` 밖으로 탈출하는 조각 자원은 오류로 돌려준다. 페이지 이동 링크의 목적지는 최종 팩 검사에서 확인한다.
- [ ] **4. 작성 CLI를 연결한다.** `build_author_page()`로 조립한 HTML을 한 Chrome 세션에서 두 라이트 조합으로 측정하고 `layout.json`으로 저장한다. 입력이나 레이아웃 문제는 `fail`, Playwright 또는 Chrome을 열 수 없는 환경은 `unavailable`로 남긴다. 현재 작업에 사용한 Python으로 `preflight`를 호출할 수 있게 한다. 작성 명령과 사전 점검은 저장소에 쓰지 않는다.
- [ ] **5. 작성 진입점을 확인한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_preview_layout.py" "$SKILL/tests/test_browser_layout.py" -q`에서 모두 통과하고 브라우저 케이스가 실행됐는지 확인한다.
- [ ] **6. 승인된 경우 작업 파일을 커밋한다.** `feat(review-pack): preview selected author fragments`.

### Task 3. 강의 예제의 문제지 쪽 분할을 시험한다

**Files**

- Modify `scripts/preview_layout.py`, `tests/test_preview_layout.py`.
- Reuse `scripts/pdf_cards.py:77`, `scripts/pdf_layout.py:50`, `scripts/review_pdf.py:38`.

**Interfaces**

- `preview_layout.probe_lecture_pages(review: Path, work: Path) -> list[LectureLayout]`. `LectureLayout`은 `{id: str, question_pages: list[str], conditions_pages: list[str], ask_pages: list[str], split_ok: bool}`다. 각 쪽 목록에서 실제 `PageSlice.physical_id`를 사용한다.
- 카드 `author` 보고서에 `lecture_pdf: list[LectureLayout]`을 추가한다. 대상이 없으면 `[]`다. `question_pages`가 두 쪽 이상이거나 `split_ok`가 거짓이면 `issues`에 카드 ID·쪽 수·분리 상태를 남기고 `status=fail`로 반환한다. 이는 작성 단계 판정이다. 필요한 자료 때문에 여러 쪽이 생기면 메인이 사유를 보고 판단한다.

- [ ] **1. 쪽 배치 회귀 테스트를 쓴다.** P10 유형으로 조건 문단, C 코드, `(a)`–`(c)` 질문 목록을 가진 미리보기 원고를 만든다. 짧은 원고는 조건과 질문이 모두 한 쪽에 들어가게 하고 긴 버전에는 의미를 바꾸지 않는 코드 주석 줄을 추가한다. `test_lecture_preview_detects_question_split`, `test_solution_continuation_does_not_count_as_question_page`, `test_nonlecture_preview_skips_pdf_probe`를 넣는다.

  ```python
  assert short["question_pages"] == short["conditions_pages"] == short["ask_pages"] == ["p10"]
  assert short["split_ok"] is True
  assert len(long["question_pages"]) >= 2 and "p10-c2" in long["question_pages"]
  assert long["split_ok"] is False
  assert long_answer_only["question_pages"] == ["p10"]
  assert long_answer_only["split_ok"] is True
  assert probe_lecture_pages(exam_only_review, work) == []
  assert not list(work.rglob("*.pdf")) and not list(work.rglob("*.png"))
  ```

  답안 계속 쪽 사례는 별도로 실제 `plan_pages()`에 넘겨 `p10-c2`가 존재하는지 확인한 뒤 시험 배치 결과를 비교한다.
- [ ] **2. 실패를 확인한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_preview_layout.py" -k 'lecture or continuation' -q`에서 PDF 시험 API가 없어 실패하는지 확인한다.
- [ ] **3. 기존 배치기와 연결한다.** `read_pack()` 결과에서 `kind == '강의 코드'`만 골라 `dataclasses.replace()`로 카드 목록을 제한한다. `plan_pages()`와 `pages_for_mode(..., 'problems')`를 거쳐 `to_payload(..., 'problems', ...)`의 각 쪽을 확인한다. `conditions_pages`는 `html.conditions`가 비어 있지 않은 쪽이고 `ask_pages`는 `html.ask`가 비어 있지 않은 쪽이다. `split_ok`는 조건이 있고 질문이 분류된 `ds-asks` 목록으로 출력될 때 참이다. 쪽 수 진단과 분류 진단을 독립적으로 기록한다. 배치 중간 파일은 작성자 미리보기 아래에 보관한다.
- [ ] **4. 실제 배치 테스트를 실행한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_preview_layout.py" "$SKILL/tests/test_pdf_layout.py" "$SKILL/tests/test_pdf_lecture.py" -q`에서 통과 및 Chrome 사용을 확인한다.
- [ ] **5. 승인된 경우 작업 파일을 커밋한다.** `feat(review-pack): preview lecture question pagination`.

### Task 4. 신규 팩의 최종 승인에 전체 측정 범위를 연결한다

**Files**

- Modify `scripts/browser_review.py:139`, `scripts/preview_layout.py`, `tests/test_review_source.py`, `tests/test_preview_layout.py`, `tests/test_skill_files.py`.
- Modify `SKILL.md:96`, `references/content-rules.md:6`, `references/card-rules.md:6`, `references/browser-check.md:3`.
- Reuse `scripts/release_review.py:88`의 경로 확인과 `require_pass()` 호출 위치.

**Interfaces**

- `browser_review.snapshot(repo: Path, stage: Path, mode: str, attempt: str, *, version: int | None = None) -> dict`. 신규 요청 발급은 v2, 두 갱신 모드는 v1이다. v2는 기존 필드에 `expected_scopes`를 추가한다. 값은 조합 ID → `[[id, area], ...]`다. 발행 시 저장된 요청 버전으로 같은 스냅샷을 재계산한다. 업데이트 전에 이미 발급된 신규 v1 요청은 기존 형식으로 검증한다.
- `preview_layout.py stage --repo REPO --run RUN`은 `release_paths()`로 stage를 찾고 최신 v2 요청을 읽는다. 조합 8개의 측정 결과를 `RUN/browser/<attempt>/layout-measurements.json`에 쓴다. 결과는 `{version: 1, request_sha256: str, cases: dict[str, CaseLayout]}`. 종료 코드는 작성 명령과 같으며 문제가 있는 실행도 가능한 진단을 저장한다.
- v2 `browser-review.json`은 기존 승인 필드와 `measurements_sha256`(측정 파일 바이트의 SHA-256)을 포함하고 `version: 2`를 쓴다. 승인 `cases[case]`의 `visual_notes`는 `[{id, area, observation}, ...]`다. 내용이 있는 관찰 한 줄이 각 수동 확인 대상에 있어야 한다. 기존 `evidence`는 해당 실제 화면과 지침상 필요한 캡처를 기록한다.

- [ ] **1. 발행·CLI 회귀 테스트를 쓴다.** `test_review_source.py`의 `approve_browser()`는 요청 버전별로 테스트용 측정·승인을 구성한다. v2의 고의 실패는 `test_v2_publish_rejects_incomplete_layout`에서 매개변수화한다. `changed-measurements`를 제외한 측정 내용 변경 사례는 승인 해시도 다시 계산해 각 검증 조건을 직접 시험한다.

  ```python
  # missing-solution, duplicate-scope, changed-measurements,
  # old-request-hash, missing-visual-note, 8.99px, bad-measurements
  with pytest.raises(ValueError, match="브라우저 검토"):
      publish(repo, run)
  assert live_files_and_bytes(live) == before
  assert stage.is_dir()
  ```

  `test_new_request_contains_all_scopes`는 요청의 `review/375x812/light`에 `p1`의 네 영역이 정확히 한 번씩 들어가는지 확인한다. 기존 0문항 테스트가 `review`의 `hero/body`만 요구하도록 단언을 추가한다. `test_legacy_new_request_still_accepts_v1`과 기존 갱신 모드 테스트에서 측정 파일 없이 기존 승인 형식으로 성공하는지 확인한다. `test_stage_cli_writes_current_attempt_only`는 실제 `MINI_RUN` 조립본을 대상으로 8개 조합, 현재 요청 해시, 쓰기 경로를 확인한다. `test_new_workflow_documents_layout_checks`에서 3단계에 `preview_layout.py`가 있고, 7단계의 최종 브라우저 승인 뒤에 8단계 전체 PDF 검토가 이어지는지 확인한다.
- [ ] **2. 실패를 확인한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_review_source.py" "$SKILL/tests/test_preview_layout.py" "$SKILL/tests/test_skill_files.py" -q`에서 v2 요청과 최종 측정 명령의 신규 사례가 실패하는지 확인한다.
- [ ] **3. v2 발행 게이트를 구현한다.** `expected_scopes()`를 stage manifest에 적용해 조합별 범위를 계산한다. 현재 요청 해시를 검사하고 `layout-measurements.json`의 SHA-256을 승인 기록의 `measurements_sha256`과 대조한다. 필수 조합·영역 목록의 정확한 일치, 중복 없음, `errors=[]`, 필드 타입·유한 수치의 유효성, 결함 없음, 필요한 수동 확인 관찰을 검증한다. `svg_text_count`가 0이면 최솟값은 `null`, 양수이면 최솟값은 유한한 양수여야 한다. `no-figure`는 글자 수 0을 요구한다. 수동 관찰은 그 조합의 대상 영역에만 연결한다. 손상된 JSON, 지원하지 않는 버전, 잘못된 영역은 `ValueError`로 발행을 거부한다. 현재 입력 해시 재계산까지 기존 `publish` 잠금 안에서 처리한다.
- [ ] **4. 조립본 측정 명령을 구현한다.** 현재 v2 요청의 조합과 필수 영역을 Task 1의 `measure_case()`에 넘긴다. 요청과 stage의 경로가 일치해야 하며, 검사 파일은 32자리 소문자 16진수로 확인한 요청의 `attempt` 하위에만 쓴다. 요청이 바뀌면 새 시도의 폴더에 이전 측정을 쓰지 않는다. 기록을 임시 파일로 저장한 뒤 교체한다. 이 명령은 측정 기록을 생성하며 실화면 판정은 검사자가 작성한다.
- [ ] **5. 기본 팩 절차를 갱신한다.** 0단계에서 확인한 Python 절대 경로를 브리프에 넘긴다. 3단계는 미리보기와 보고서 경로, `fail`일 때 수정할 항목, `unavailable`이면 조립본에서 확인할 항목을 명시한다. 7단계는 요청→측정→실화면 승인 순서와 v2 기록 예시를 추가한다. Playwright를 사용할 수 없지만 실화면 도구가 있다면 동일한 JS 함수 식으로 같은 영역 기록을 수집한다. 둘 다 없으면 기존 브라우저 보류 절차를 적용한다. 8단계는 통과한 조립본의 전체 PDF를 사용한다.
- [ ] **6. 통합 검사를 실행한다.** `"$TEST_PYTHON" -m pytest "$SKILL/tests/test_browser_layout.py" "$SKILL/tests/test_preview_layout.py" "$SKILL/tests/test_review_source.py" "$SKILL/tests/test_panel_titles_browser.py" "$SKILL/tests/test_pdf_layout.py" "$SKILL/tests/test_pdf_lecture.py" "$SKILL/tests/test_skill_files.py" -q`에서 모두 통과하고 실제 브라우저 조합이 실행됐는지 확인한다. 이어 `"$TEST_PYTHON" -m pytest "$SKILL/tests" -q`로 전체 스킬을 검사한다. 전체 스킬에 실패가 있으면 같은 환경의 작업 전 결과와 대조해 이번 변경에 따른 회귀를 확인한다.
- [ ] **7. 실제 그림과 시험 배치를 확인한다.** 임시 RUN에서 P9 두 버전의 `375×812` 풀이를 각각 열어 실제 판독성과 측정값을 대조한다. P10 두 버전을 시험 배치해 문제지 `2쪽 이상 → 1쪽`을 확인한다. 최종 조립본의 `review/375x812/light`에서 P9의 `solution` 행을 제거하고 승인·측정 해시를 맞춰도 임시 팩 발행이 거부되는지 확인한다. 정확한 기록을 복원하고 기존 승인 경로로 통과하는지 확인한다. 보고는 판정, 관련 수치, 근거 경로로 남긴다.
- [ ] **8. 승인된 경우 작업 파일을 커밋한다.** `feat(review-pack): require complete layout evidence for new packs`.
