# 자구알 복습팩 화면 검증 위임 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습팩 화면 검증을 별도 컨텍스트에서 수행하고, 메인은 짧은 판정과 현재 산출물에 대응하는 검토 기록으로 발행한다.

**Architecture:** 기존 `release_review.py`에 작업용 HTML의 검토 기록과 입력 해시를 확인하는 단계를 추가한다. PDF는 기존 `PDF_RUN/review.json`과 발행기를 사용한다. 검사자는 RUN에 근거를 남기고 메인은 기존 발행 명령을 호출한다.

**Tech Stack:** Python 3.10+ 표준 라이브러리, pytest, 기존 브라우저 도구 또는 Playwright와 설치된 Chrome, 기존 PDF 빌드의 PyMuPDF.

**Spec:** 이 파일의 [설계 기준](#설계-기준). 앞선 `grill-yourself` 설계 중 화면 검증 위임을 옮겼다.

## Global Constraints

- 신규·`update-existing`·`revise-existing`은 각 모드의 실화면 검증 범위를 유지한다. `lite`가 생략하는 것은 기존 6단계 내용 리뷰다.
- 기록을 남기기 전에 정리노트·작업용 복습문제의 해당 화면과 문제지·답안지의 모든 PDF 페이지를 직접 확인한다. 기계 검사만 마친 상태는 미검토다.
- 서브에이전트에게 새 컨텍스트를 열고 지침과 입출력 경로만 넘긴다. 각 서브에이전트의 쓰기는 자기 RUN의 검사 기록과 증거에 한정한다. `복습노트/`에는 메인만 쓴다.
- 화면 도구를 서브에이전트에서 쓸 수 없으면 메인이 동일한 검사와 기록을 수행한다. 메인도 실화면 검사를 끝낼 수 없으면 보류한다.
- 기존 2회 수정 한도, 팩 잠금·백업·복구, 0문항 PDF `skipped`, 실패 시 `withheld`/`stale`을 적용한다. 독립된 다음 팩은 계속 처리한다.
- `bank`, 문제설명·확인문제 절차, PDF 템플릿과 발행 형식은 이번 범위 밖이다. 확인문제는 기존대로 신규에서만 만들고 블라인드 풀이를 r3까지 돌린다.
- 커밋은 사용자 승인 후, PR은 사용자 요청 시에만 한다. 테스트와 실제 브라우저 재현은 임시 저장소에서 수행한다.

## Review Focus

1. 같은 RUN에서 재검사를 시작했는데 이전 검토가 다시 들어옴 → 새 요청 해시와 일치하는 기록만 발행에 쓴다. Task 1 `test_publish_rejects_invalid_browser_review[old-attempt]`.
2. 두 갱신 모드에서 화면 하나 또는 테마 하나가 누락됨 → 기록이 `pass`여도 교체 전에 거부한다. Task 1 `test_publish_rejects_invalid_browser_review[missing-case]`와 `test_review_cases_by_mode`.
3. 검토 뒤 HTML 외 로컬 그림이나 공용 글꼴이 바뀜 → 이전 발행본을 보존한다. Task 1 `test_publish_rejects_invalid_browser_review[figure-changed]`, `[font-changed]`.
4. macOS에서 경로가 NFD로 저장된 팩 → 실제 파일로 읽어 검사하고 발행한다. Task 1 기존 발행 테스트의 `nfd` 케이스.
5. 문항이 0개인 팩 → 브라우저는 검사하고 PDF 검토·발행만 건너뛴다. Task 1 `test_zero_card_release_requires_browser_review_and_no_pdfs`, Task 2 `skipped` 확인.

---

## 설계 기준

- 메인은 브라우저 검사자의 통과 여부, 검사 횟수, 결함 위치와 기록 경로를 받는다. 브라우저 측정치, 화면 캡처, PDF의 쪽별 판정은 RUN에 보관한다. 일반적인 통과 흐름에서 메인이 화면 파일을 열 필요는 없다.
- 최종 작업용 HTML 두 개와 판단 기준인 manifest, 로컬 화면 자원을 검사 요청에 SHA-256으로 고정한다. 검사자가 실제 확인한 기록은 그 요청 해시에 대응한다. 팩 발행기는 작업 폴더 사본의 승인 여부를 확인하고 기존 링크 변환을 적용한다.
- PDF는 빌드와 기계 검사가 통과한 뒤 각 PNG와 원고·출력 PDF를 대조한다. 메인이 기존 `review_pdf.py publish` 게이트를 통과시킨 뒤 팩을 발행한다.
- 첫 실측은 1116 복사본으로 한다. 화면 검증 단계의 메인 텍스트 출력량과 이미지 수를 비교하고, 전체 복습팩 실행의 절감률은 별도 실측으로 확인한다.

## 파일 지도

| 파일 | 책임 |
|---|---|
| `.agents/skills/ds-review-pack/scripts/browser_review.py` | 브라우저 요청에 입력 파일과 필수 화면 조합을 기록하고 발행 직전에 검토 기록을 검사 |
| `.agents/skills/ds-review-pack/scripts/release_review.py` | 기존 `prepare`에 모드를 기록하고 요청 CLI 및 발행 게이트 연결 |
| `.agents/skills/ds-review-pack/SKILL.md`, `references/browser-check.md`, `references/textbook-update.md`, `references/review-overhaul.md` | 같은 게이트를 쓰는 세 모드의 실행 순서, 검사자 브리프와 오류 처리 |
| `.agents/skills/ds-review-pack/references/pdf-build.md` | 기존 PDF 발행 절차에 실제 검토 담당과 반환할 요약 명시 |
| `.agents/skills/ds-review-pack/tests/test_review_source.py` | 일반 발행 경로에서 승인·누락·변경·0문항·경로 정규화 검증 |

### Task 1: 브라우저 검사 결과를 팩 발행에 연결한다

**Files**

- Create: `.agents/skills/ds-review-pack/scripts/browser_review.py`
- Modify: `.agents/skills/ds-review-pack/scripts/release_review.py:55`, `.agents/skills/ds-review-pack/SKILL.md:135`, `.agents/skills/ds-review-pack/references/browser-check.md:1`, `.agents/skills/ds-review-pack/references/textbook-update.md:9`, `.agents/skills/ds-review-pack/references/review-overhaul.md:29`
- Test: `.agents/skills/ds-review-pack/tests/test_review_source.py`

**Interfaces**

- `release_review.prepare(repo: Path, range_: str, run: Path, *, mode: str = "new") -> Path`와 CLI `prepare --repo REPO --range RANGE --run RUN [--mode {new,update-existing,revise-existing}]`. `release-stage.json`에 `mode`를 저장한다. `release_paths`는 기존 stage/live 경로 검증을 재사용한다.
- `release_review.start_browser_review(repo: Path, run: Path) -> Path`와 CLI `browser-request --repo REPO --run RUN`. 한 줄로 `RUN/browser-request.json` 경로를 출력한다. 스냅샷 요청이 갱신될 때마다 `RUN/browser/<attempt>/`를 새로 만들고, 이 폴더만 검사자의 쓰기 대상으로 지정한다.
- `browser_review.required_cases(mode: str) -> tuple[str, ...]`. ID는 `<note|review>/<width>x<height>/<light|dark>`. `new`는 두 페이지, 갱신 모드는 작업용 `review`의 4개 조합이다. 갱신에서 확인하는 정리노트 링크의 목적지와 기존 레거시 검사는 지침대로 확인한다.
- `browser_review.write_request(repo: Path, stage: Path, run: Path, mode: str) -> Path`, `browser_review.require_pass(repo: Path, stage: Path, run: Path, mode: str) -> None`. 요청 JSON은 `version: 1`, `attempt`(UUID hex), `mode`, `stage`(절대 경로), `inputs`(저장소 상대 경로 → SHA-256), `cases`(필수 ID 목록)로 구성한다. 검사자의 `RUN/browser/<attempt>/browser-review.json`은 `version: 1`, `request_sha256`, `reviewer`, `status`, `cases`(ID → `{status, evidence}`), `issues`(결함의 `where`, `case`, `detail`)를 담는다. `evidence`는 해당 조합의 실제 관찰과 지침상 필요한 캡처의 검사 RUN 상대 경로다. 상태는 `pass`, `fail`, `unavailable`을 사용한다. `require_pass`는 실패 시 `ValueError`를 내며 메시지는 `브라우저 검토`와 원인을 포함한다.

- [ ] **1. 발행 회귀 테스트를 준비한다.** 기존 `test_release_keeps_pdfs_and_archives_legacy_without_public_html`의 준비 코드를 `release_fixture`로 꺼낸다. `MINI_RUN`을 복사해 `prepare`·`assemble`을 사용한다. 임시 저장소의 공용 자원에 실제 이름의 최소 테스트 파일 4개(`pretendard/pretendard.css`, `katex/katex.min.css`, `katex/katex.min.js`, `katex/contrib/auto-render.min.js`)와 `pretendard/test.woff2`를 두고 `assemble.SHARED_ASSETS`를 그곳으로 향하게 한다. `.pack/figures_<range>/test.svg`도 만들고 작업용 HTML에서 참조한다. 기존 가짜 PDF 승인 기록은 테스트에만 사용한다. `approve_browser(fixture)`는 `start_browser_review` 후 요청의 해시와 실제 `cases`를 사용해 테스트 검토 기록을 쓰며 그 경로를 반환한다. 기존 정상 발행 테스트의 원고·PDF 링크 단언을 유지하고, `nfd` 케이스에서는 임시 `복습노트` 디렉터리를 NFD 이름으로 만들어 그 아래에 발행되는지 확인한다.

- [ ] **2. 승인 누락과 변경의 회귀 사례를 추가한다.** `test_publish_rejects_invalid_browser_review`를 `missing`, `missing-case`, `old-attempt`, `note-changed`, `figure-changed`, `font-changed`로 매개변수화한다. 각각 기록 없음, `review/375x812/dark` 행 삭제, 새 요청의 폴더로 이전 승인 복사, 정리노트 내용 변경, `test.svg` 교체, `test.woff2` 교체를 만든다. `missing-case`는 두 갱신 모드로도 실행한다. 테스트 안에 `live_files_and_bytes(live: Path) -> dict[str, bytes]`를 두고 실제 날짜 폴더의 모든 파일을 상대 경로와 바이트로 읽는다. 교체 전에 그 값을 `before`로 저장한다. `test_review_cases_by_mode`에서 갱신 모드는 두 크기 × 두 테마의 `review` 4개, 신규는 여기에 `note` 4개가 추가되는지 확인한다. `test_zero_card_release_requires_browser_review_and_no_pdfs`는 `MINI_RUN`의 `problems`, `parts`, `links`를 비우고 HTML과 MD를 조립한다. 기록 없이 한 번 실패시킨 뒤 fixture 검토 기록으로 발행하며 `assert not list(live.glob('*.pdf'))`와 정리노트 보존을 확인한다.

  ```python
  with pytest.raises(ValueError, match="브라우저 검토"):
      publish(repo, run)
  assert live_files_and_bytes(live) == before
  assert stage.is_dir()
  ```

- [ ] **3. 실패를 확인한다.** 저장소 루트에서 `python3 -m pytest .agents/skills/ds-review-pack/tests/test_review_source.py -q`를 실행한다. 새 API가 없거나 미검토 발행을 거부하지 않아 새 사례가 실패하는지 확인한다.
- [ ] **4. `browser_review.py`의 요청과 검증을 구현한다.** `review_paths`와 `normalized_child`를 이용해 작업용 HTML 두 개와 `.pack/자료_복습팩/manifest.json`을 찾는다. 작업 폴더의 그림·CSS·JS·글꼴 및 `복습노트/_assets`의 공용 자원을 포함한다. 두 HTML의 로컬 이미지·스크립트·스타일시트 같은 렌더링 자원 참조도 실제 경로로 풀어 추가한다. 상대 URL의 percent encoding을 디코딩하고 query·fragment는 제거한다. 페이지 이동용 링크는 브라우저 검사 항목으로 처리하고 인라인 자원은 HTML 해시에 포함한다. 파일 집합과 해시는 정렬해서 저장하고, 발행 때 `repo`와 `stage`에서 다시 계산한다. `require_pass`는 필수 조합 전부의 실제 관찰 기록, `issues=[]`, 현재 요청 해시와 입력의 일치를 요구한다.
- [ ] **5. `release_review.py`에 발행 검사를 연결한다.** `browser-request`가 `release_paths`에서 검증한 stage와 모드로 요청을 만들게 한다. `publish`에서 기존 대상 잠금을 획득한 뒤 검토 기록을 확인한다. 같은 잠금 아래 archive·링크 변환·대상 바이트 읽기·교체를 수행한다. 발행 직전까지 작업본을 단일 메인이 소유하는 기존 규칙을 적용한다.
- [ ] **6. 세 모드의 실행 지침을 갱신한다.** 신규는 기존 두 HTML의 MD 변환을 7단계 검증 요청 전으로 옮긴다. 갱신은 기존 단일 복습문제 MD 변환을 마친 다음 요청한다. 두 갱신 지침의 `prepare`에 각각 `--mode update-existing`와 `--mode revise-existing`을 적는다. 공통 지침에는 실화면 검사 범위와 실행을 유지한다. 검사자는 자기 RUN에서 경로·모드·요청 해시를 확인하고 기록을 쓴다. 브라우저 도구가 없는 환경에선 설치된 Chrome과 기존 Playwright를 확인한다. 검사자가 화면을 열 수 없으면 메인이 같은 RUN에 같은 형식으로 기록한다. 결함은 `where` 기준으로 작성자에게 묶어서 전달한다. 재빌드 후 요청을 새로 생성하고, 기존 2회 한도 뒤 미해결이면 발행을 보류한다. 서버는 실행자가 자기 작업의 프로세스만 종료한다.
- [ ] **7. 관련 테스트를 실행한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_review_source.py .agents/skills/ds-review-pack/tests/test_skill_files.py -q`에서 모두 통과해야 한다. 이어 `python3 -m pytest .agents/skills/ds-review-pack/tests/test_panel_titles_browser.py -q`로 기존 4개 화면 조합의 패널 동작을 확인한다.
- [ ] **8. 사용자에게 검토 가능한 변경을 남긴다.** 승인받은 경우에만 이 작업의 파일을 지정하여 `feat(review-pack): require current browser review before publish`로 커밋한다.

### Task 2: PDF 실화면 검토를 위임하고 1116으로 재현한다

**Files**

- Modify: `.agents/skills/ds-review-pack/SKILL.md:165`, `.agents/skills/ds-review-pack/references/pdf-build.md:5`
- Test: 기존 `.agents/skills/ds-review-pack/tests/test_pdf_publish.py`, `.agents/skills/ds-review-pack/tests/test_pdf_cli.py` 및 임시 복사본의 1116 재현.

**Interfaces**

- Consumes: Task 1의 `browser-request` 및 팩 `publish`. PDF CLI는 기존 `review_pdf.py build --review REVIEW --run PDF_RUN`, `check --run PDF_RUN`, `publish --run PDF_RUN --repo REPO`를 쓴다. `PDF_RUN` 자체가 해당 PDF 검토자의 RUN이며 메인이 만든 `stage/`는 읽기 전용 입력으로 취급한다.
- Produces: 현행 PDF 발행기가 읽는 `PDF_RUN/review.json`. `status`, `reviewer`, `report_sha256`, `artifact_hashes`를 기존대로 사용한다. `evidence`에는 `{page, observation}` 행을 넣고 `page`는 `stage/pages/problems/001.png` 같은 RUN 상대 경로로 기록한다. 실패 시 `status: fail`과 결함 근거를 쓴다. 발행기는 기존 형식을 계속 읽는다.

- [ ] **1. 메인과 검토자의 일을 문서에 연결한다.** 메인은 `build`·`check` 후 `report.json`의 상태를 확인한다. `skipped`는 PDF 발행 없이 팩 발행 단계로 진행한다. `staged`이면서 machine check가 통과한 건만 검토자에게 `PDF_RUN`과 지침 경로를 전달한다. 검토자는 원고와 PDF를 대조하고 두 목록의 모든 PNG를 연다. 검사한 경로의 집합이 `stage/pages/{problems,answers}/*.png`와 정확히 일치할 때만 `pass`를 기록한다. 메인에게는 상태, 문제지·답안지 쪽 수, 실패 쪽과 기록 경로를 짧게 반환한다. `withheld`/`stale`과 재생성 조건은 현재 지침을 따른다. 독립 PDF backfill도 기존 `summary.json`의 각 RUN을 대상으로 같은 검토 계약을 쓴다.
- [ ] **2. 기존 PDF 발행 검사를 실행한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_pdf_publish.py .agents/skills/ds-review-pack/tests/test_pdf_cli.py -q`로 미검토 거부, 검토 후 변경 거부, 일부 파일 교체 실패 시 복구, 0문항 경로를 확인한다. 실제 브라우저를 요구하는 테스트가 환경 문제로 건너뛰어지면 이유를 남기고 다음 재현에서 해당 경로를 실제로 확인한다.
- [ ] **3. 1116 복사본에 정상 흐름을 적용한다.** 임시 저장소에 현재 작업본의 스킬·공용 자원·1116 팩·1116이 링크하는 로컬 자료를 같은 상대 경로로 복제하고, 그 안의 `.agents/skills/ds-review-pack` 명령을 쓴다. `prepare --range 1116 --mode new`로 기존 JSON 원고를 작업용 HTML로 복원한다. 이 재현에는 이미 발행된 MD와 그림을 입력으로 사용한다. `browser-request`로 요청하고 서브에이전트가 두 HTML의 8개 화면 조합을 검사한다. PDF를 새로 빌드·검토해 작업 폴더에 발행하고 팩 `publish`를 실행한다. 정리노트와 두 PDF가 있고, 정리노트에서 문제·답안 링크가 열리며, 복습문제 작업용 HTML은 원고 JSON으로 보존되었는지 확인한다. 신규 `new` 모드는 브라우저 검사 범위를 재현하는 데 사용하며 실제 1116 팩 제작은 이 재현 범위 밖이다.
- [ ] **4. 실패를 재현한다.** 별도 새 작업 폴더에서 브라우저 검사 후 정리노트 작업본의 바이트를 변경한다. 팩 `publish`가 실패하고 직전 발행본의 해시가 같아야 한다. PDF는 새 `PDF_RUN`에서 `review.json`을 초기 `not_run` 상태로 둔 채 `review_pdf.py publish`를 실행한다. 발행이 거부되고 기존 PDF가 그대로 있어야 한다.
- [ ] **5. 메인 컨텍스트를 측정한다.** 재현 RUN의 `comparison.md`에 브라우저/PDF 구간의 메인 이미지 수, 검사자 이미지 수, 메인 텍스트 도구 결과 문자 수와 측정 구간을 기록한다. 1116 원본 세션 JSONL을 확보할 수 있으면 같은 구간을 비교한다. 확보한 자료가 핸드오프의 전체 실행 집계뿐이면 새 재현 수치와 그 제한을 보고한다. 정상 위임 흐름의 합격 기준은 메인 이미지 읽기 0회, 검사 기록의 필수 화면 및 PDF 쪽 누락 0건, 메인에게 전달된 검토 내용이 상태·개수·결함·경로로 제한되는 것이다.
- [ ] **6. 사용자에게 검토 가능한 변경과 실제 검증 결과를 남긴다.** 승인받은 경우에만 이 작업의 파일을 지정하여 `docs(review-pack): delegate visual PDF review`로 커밋한다.
