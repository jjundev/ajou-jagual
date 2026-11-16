# 자구알 복습팩의 단계별 참조 읽기와 RUN 보고서 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 복습팩 메인이 현재 단계에 필요한 참조 절과 한 줄 요약을 읽고, 상세는 RUN에서 필요한 만큼 조회하게 한다.

**Architecture:** 메인의 참조 범위는 각 단계 옆에 적고, 작성자·검사자에게 전달하는 문서 경로와 기존 역할을 유지한다. `bank.py`는 복습팩이 선택하는 `--out` 모드에서만 상세를 파일에 쓴다. `review_audit.py`는 현행 보고서를 그대로 저장하고 요약에 경로를 추가한다.

**Tech Stack:** 기존 Python 3.10+ 표준 라이브러리, pytest, Markdown, `rg`와 범위 지정 읽기.

**Spec:** 이 문서의 [인터페이스와 동작](#인터페이스와-동작). 직전 `grill-yourself`의 「복습팩 메인 컨텍스트 축소 설계」를 옮겼다.

## Global Constraints

- 기출·교과서의 후보 순서·필터, 원문 대조와 검산, manifest 출처 검사, 전체 날짜 audit의 기준·JSON·종료 코드를 유지한다. 감사의 `blocking=[]`, 미판정 `candidates=[]`, `status=pass` 기준을 그대로 적용한다.
- `lite`의 현행 6단계 내용 리뷰 생략 범위, 실제 브라우저·PDF 화면과 해시 검증, 독립 검산, 확인문제 블라인드 r1~r3, 보류와 기존 파일 보존을 유지한다.
- 기본 팩 발행 후 신규는 문제설명과 확인문제를 병렬로 맡긴다. 두 갱신 모드는 문제설명만 처리한다. `bank`는 두 후속 작업을 건너뛴다. 메인만 `복습노트/`에 쓰고 서브에이전트는 자기 RUN에만 쓴다.
- `bank.py`의 옵션 없는 기존 CLI 출력과 종료 코드, Python 호출부, 공개 제작자료 형식을 유지한다. 정상 경로는 `.agents/skills`를 사용한다. `answers.py` 작성 역할과 내용도 유지한다.
- 1116 검증은 저장소 밖 복사본을 사용한다. 커밋은 결과 확인 후 사용자 승인으로 진행하며 푸시·PR은 사용자 요청에 따른다.

## Review Focus

1. 교과서와 기출이 섞인 후보의 전체 순서와 다섯 필드가 기존 TSV와 일치한다. Task 1의 `test_select_report_matches_legacy_rows`, Task 5의 1116 비교.
2. 여러 오류가 나열되는 재검사에서는 실패 보고서가 앞선 성공을 대체한다. Task 1의 `test_validation_report_replaces_prior_success`.
3. 목적지가 디렉터리거나 부모가 없어 보고서를 쓸 수 없으면 성공 요약 없이 한 줄 오류와 종료 코드 1을 반환한다. Task 1의 `test_bank_report_write_failure`.
4. 전역 검사에서 `blocking`이 0이어도 미판정 후보가 있으면 실패하고, 같은 해시의 유효한 판정을 추가한 실행만 통과한다. Task 2의 `test_audit_cli_report_and_status`.
5. 참조 제목 아래에 하위 절이나 제목처럼 보이는 코드 예시가 있더라도 본문 제목 경계를 사용한다. 두 갱신 모드와 검사자 실패 시 메인의 대체 경로까지 문서 연결이 유효하다. Task 3의 `test_main_reference_sections_resolve`와 모드별 검토.

---

## 인터페이스와 동작

- `bank.py validate BANK [--out PATH]`, `bank.py select BANK <기존 인자> [--out PATH]`, `bank.py check-manifest BANK MANIFEST <기존 인자> [--out PATH]`. 스킬은 절대 경로로 `--out`을 넘긴다. `--out` 사용 시 성공은 stdout 한 줄 `OK: <건수 또는 검사 결과>; report=<경로>`, 실패는 stderr 한 줄 `FAIL: <오류 건수 또는 저장 실패>; report=<경로>`. 성공은 0, 실행 결과 실패는 1이다. 저장 실패 메시지에는 파일을 쓰지 못했다는 사실을 명시한다.
- 보고서는 UTF-8 JSON 객체다. 모든 보고서에 `status: "pass" | "fail"`, `errors: list[str]`를 둔다. `select`에는 `candidates: list[dict]`를 추가한다. 후보 필드는 `id`, `professor`, `type`, `chapters`(정수 배열), `answer_origin`이고 값과 순서는 기존 TSV와 대응한다. 실패한 선별의 배열은 비어 있다. `validate` 성공에는 `source_count`, `problem_count`를 둔다. 보고서 쓰기 성공 뒤에 실행 결과 요약을 낸다.
- RUN 내 파일명은 `bank-validation.json`, `candidates-preview.json`, `candidates.json`, `bank-manifest-check.json`, `audit.json`이다. 단계별로 성공 요약을 받은 뒤 파일을 사용하며, 실패 진단은 현재 실행이 작성한 파일만 읽는다.
- `review_audit.py`는 기존 인자·키·판정을 유지한다. 보고서를 저장한 실행의 요약은 `<status> <N> blocking <M> candidates report=<경로>`다. 메인은 실패한 감사의 `blocking`과 미판정 `candidates`에서 조치할 행만 읽는다. 전체 인벤토리와 승인 기록은 RUN에서 기존 검증 입력과 증거로 사용한다.

## 파일 지도

| 경로 | 책임 |
|---|---|
| `.agents/skills/ds-review-pack/scripts/bank.py`, `.agents/skills/ds-review-pack/tests/test_bank.py` | 기존 CLI와 RUN 보고서 모드를 같은 검증·후보 추출 경로에 연결 |
| `.agents/skills/ds-review-pack/scripts/review_audit.py`, `.agents/skills/ds-review-pack/tests/test_review_audit.py` | 감사 요약의 경로 표시와 성공·실패 비교 |
| `.agents/skills/ds-review-pack/SKILL.md`, `.agents/skills/ds-review-pack/tests/test_skill_files.py` | 모드·단계별 읽기, RUN 출력 및 검증 연결 |
| `.agents/skills/ds-review-pack/references/{problem-selection,manifest-guide,review-overhaul,textbook-update,pdf-build}.md` | 실제 명령과 절 경계, 실패 시 상세 조회 지침 |

실행을 시작하면 Task 5의 첫 단계로 변경 전 기준을 고정하고, Task 1~4를 완료한 뒤 Task 5의 비교를 진행한다.

### Task 1 — `bank.py` RUN 보고서

**Files** · `.agents/skills/ds-review-pack/scripts/bank.py`의 `main`, 필요시 기존 CLI 데이터 투영. `.agents/skills/ds-review-pack/tests/test_bank.py`의 `TestCli`.

**Interfaces** · 기존 `main(argv: list[str] | None = None) -> int`, `load`, `select`, `check_manifest`를 사용한다. 위의 세 `--out` 명령과 JSON 형식을 제공한다.

- [x] **회귀 테스트를 추가한다.** `test_select_report_matches_legacy_rows`는 기존 TSV를 구조화한 값과 새 JSON의 `candidates`가 같고 stdout 한 줄·stderr 빈 문자열인지 확인한다. 빈 후보도 `pass`, `[]`, 0이어야 한다. `test_validation_report_replaces_prior_success`는 `validate`의 `source_count == 6`, `problem_count == 11`을 확인한 후 같은 파일을 오류 두 개 이상이 있는 입력으로 재실행해 `status == "fail"`, 오류 전체, 종료 코드 1, stderr 한 줄을 확인한다. `test_manifest_report`는 정상·은행에 없는 출처·잘못된 JSON을 확인한다. `test_bank_report_write_failure`는 저장 불가 경로에서 종료 코드 1, 오류 한 줄, 성공 요약 없음, 입력 파일 해시 불변을 확인한다.
- [x] **새 모드의 실패를 확인한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_bank.py -q`. 기존 테스트는 통과하고 새 테스트는 `--out` 미지원으로 실패해야 한다.
- [x] **CLI를 구현한다.** 세 하위 명령에 옵션을 붙이고, 현재 후보 행의 메타데이터를 한 번 계산해 TSV와 JSON에서 같이 쓴다. 결과와 검증 오류를 보고서에 기록한다. 출력 파일은 같은 디렉터리의 임시 파일에 완성한 뒤 교체해 중간 JSON을 노출하지 않는다. 저장 예외는 입력 오류와 분리해서 요약한다. `--out`이 없는 경로의 기존 stdout·stderr 및 종료 코드를 유지한다.
- [x] **기출과 교과서 테스트를 실행한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_bank.py .agents/skills/ds-review-pack/tests/test_textbook.py -q`. 새 테스트와 기존 호출 테스트가 모두 통과해야 한다.

### Task 2 — 전역 감사 요약

**Files** · `.agents/skills/ds-review-pack/scripts/review_audit.py`, `.agents/skills/ds-review-pack/tests/test_review_audit.py`.

**Interfaces** · 기존 `audit_reviews(repo: Path, *, overlays=None, decisions=None, baseline=None, required_exams=None)` 및 필수 `--out PATH`를 사용한다. 위에 정의한 경로 포함 한 줄을 제공한다.

- [x] **`test_audit_cli_report_and_status`를 추가한다.** 기존 후보 fixture를 재사용해 미판정 상태와 유효한 `distinct` 판정 상태를 각각 subprocess로 호출한다. 첫 실행에서 `blocking == []`, `len(candidates) == 1`, 종료 코드 1을, 둘째에서 `candidates == []`, 종료 코드 0을 확인한다. 각 파일을 같은 인자로 호출한 `audit_reviews` 반환값과 비교한다. stdout은 경로를 포함한 정확한 한 줄, stderr는 비어 있어야 한다.
- [x] **새 테스트가 경로 차이로 실패하는지 확인한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_review_audit.py -q`.
- [x] **요약 끝에 `report=<경로>`를 붙인다.** 기존 검사·JSON 쓰기·종료 코드 계산을 사용한다.
- [x] **같은 명령을 다시 실행한다.** 기존 차단·후보·기출 보존 테스트와 새 CLI 테스트가 통과해야 한다.

### Task 3 — 모드별 참조 절과 RUN 조회 연결

**Files** · 파일 지도의 `SKILL.md`, 참조 문서 다섯 개, `tests/test_skill_files.py`.

**Interfaces** · Task 1~2의 CLI와 보고서, 기존 작성자·실화면 검사·후속 작업의 경로 입력을 사용한다. 메인용 참조의 경계는 문서 안에 실제로 존재하는 제목으로 지정한다.

- [x] **문서 회귀 테스트를 추가한다.** `test_main_reference_sections_resolve`는 단계별 명시 링크가 실제 제목으로 이어지고 코드 펜스 속 제목이 범위를 끊지 않는지 확인한다. `test_run_report_commands_by_mode`는 은행 모드의 검증, 신규의 준비·예비/최종 후보·manifest 검증, 두 갱신 모드의 적용되는 명령과 실패 기록을 확인한다. `python3 -m pytest .agents/skills/ds-review-pack/tests/test_skill_files.py -q`를 실행해 새 계약이 없는 상태의 실패를 확인한다.
- [x] **메인용 읽기 규칙을 적는다.** 제목은 `rg -n`으로 찾고 해당 제목에서 다음 동급 또는 상위 본문 제목 직전까지만 읽는다. 현재 단계에서 읽은 절은 같은 실행에서 재사용한다. B1~B4는 `bank-build.md`의 원본 표, 정규화, 전사 브리프, 챕터 표·중복 문항·정답 검증을 각각 지정한다. 신규 1단계는 후보 추출 절, 2단계는 선별·parts·level·원문·정답·교과서와 manifest에 적용되는 절을 지정한다. 불필요한 절을 통째로 읽게 하는 참조는 작성자·검사자에게 전달할 경로와 구별한다.
- [x] **검증과 발행 경로의 읽기 범위를 지정한다.** 브라우저는 정상 위임 시 요청·결과 계약을 확인하며 대체 수행 시 해당 검사 절을 적용한다. PDF에는 생성·검사 요청·발행을 찾을 제목을 두고, backfill이나 생성기 진단용 절은 해당 작업에서만 읽게 한다. 후속 작업은 기존 준비·병렬 시작·발행 절을 필요한 단계에서 연결하고, 블라인드 중계 절은 중계 요청 시 연다. `textbook-update.md`의 번호 절차에는 준비·선별, 작성·검증, 발행·보고 제목을 붙인다. 두 갱신 모드는 `review-overhaul.md`의 공통 선별·근거·전역 검사 절을 각각 적용할 때 읽는다. 기존 검토 지침과 실패 조건을 유지한다.
- [x] **활성 명령을 RUN 출력에 연결한다.** 신규 준비에서는 저장소·필수 입력 존재 확인 뒤 범위와 RUN을 확정하고 은행·교과서 검증이 끝난 뒤 다음 단계로 진행한다. `problem-selection.md`에는 후보 추출 명령을 별도 절로 두고 예비·최종 출력 이름을 단계에서 선택한다. `manifest-guide.md`, `review-overhaul.md`, `textbook-update.md`에서 적용되는 은행 검사에 `--out`을 넘긴다. audit 판정·재실행·발행 순서와 기존 영속 증거 파일을 보존한다.
- [x] **문서와 관련 CLI 테스트를 실행한다.** 위 문서 테스트와 Task 1~2의 테스트를 실행하고 `git diff --check`를 확인한다. 신규·기간·lite·두 갱신·bank에서 메인 읽기와 담당자에게 전달하는 내용이 각각 올바른지 문서를 순서대로 대조한다.

### Task 4 — 독립 리뷰

**Inputs** · 기준 커밋, 미커밋 구현 diff, 이 계획, Task 1~3 테스트 결과. **Output** · 발견 사항, 재현, 수정과 재검토 기록.

- [x] **구현자와 별도의 서브에이전트에게 리뷰를 맡긴다.** 첫 단계와 갱신 분기를 따라가며 참조 경계와 문서 명령을 대조한다. 기존 CLI 호출자의 의존성, 오류가 통과로 보일 경로, 감사 대상 범위, 메인만 쓰는 발행 경계와 실화면·블라인드 검증 유지 여부를 확인하도록 요청한다.
- [x] **발견 사항을 재현하고 확인된 결함을 수정한다.** 지적한 조건을 재현하는 테스트와 관련 테스트를 실행한 뒤 변경분을 독립 리뷰어에게 다시 보낸다. 남은 사항과 판정을 보고한다.

### Task 5 — 1116 복사본에서 전후 비교

**Inputs** · 실행 시작 시 고정한 기준 SHA, 수정 스킬, 실제 1116 자료와 전체 날짜 감사 입력. **Output** · 저장소 밖 `RUN/comparison.md` 및 원시 로그·JSON·해시 목록.

- [x] **비교 기반을 고정한다.** 구현 시작 전에 `git rev-parse HEAD`와 `python3 -m pytest .agents/skills/ds-review-pack/tests -q`의 출력을 RUN에 기록한다. 기준 스킬은 해당 SHA에서 별도 디렉터리로 내보낸다. 1116의 숨김 제작자료와 로컬 자원, 나머지 날짜의 감사 입력, 기출 은행·교과서·STT·강의록을 저장소 밖에 복사한다. 상대 경로를 유지하고 비교 전에 원본 1116의 상대 경로와 SHA-256 목록을 기록한다. 기준·변경 스크립트는 동일한 복사본 경로와 Python을 사용한다.
- [x] **CLI의 성공·실패 결과를 비교한다.** 복사본의 1116 `selection.json`의 근거인 `--range-ch 8,10 --taught 1-8,10`과 `--used-dir <복사본>/복습노트 --this-range 1116 --textbook-dir <복사본>/교과서 --textbook-python <동일 Python>`을 두 선별에 적용한다. 기존 TSV를 구조화해 새 후보 JSON의 다섯 필드와 순서가 정확히 같은지 확인한다. 같은 1116 manifest와 출처 하나를 잘못 지정한 사본으로 `check-manifest`를 두 번씩 실행해 통과·실패 종료 코드와 오류를 대조한다. 은행 스키마 검사도 정상 은행과 오류를 넣은 별도 복사본으로 비교한다.
- [x] **전체 감사 결과를 비교한다.** 복사본에서 `collect_reviews`로 한 번 생성한 `baseline.json`과 1116의 `selection.json`에서 가져온 `duplicate_decisions`를 두 CLI에 똑같이 넘긴다. overlay의 `1116` 값은 1116 원고의 논리적 HTML 경로 `<복사본>/복습노트/1116/복습문제_1116_Graph.html`이다. 실제 HTML이 없어도 기존 원고 리더가 `.pack`의 JSON을 사용한다. 나머지 날짜도 포함됐는지 `inputs`를 확인한다. 공유 입력에서 생성한 `audit.json` 값과 종료 코드가 일치해야 한다. 별도 실패 시행에서는 은행에 없는 ID 하나를 `--required-exams`로 전달하고 `blocking`의 사유 `required exam not in bank`를 RUN에서 확인한다. 기존 1116 보관 감사의 판정을 이번 실행의 증거로 사용하지 않는다.
- [x] **메인 읽기 수치를 잰다.** 같은 1116 입력과 같은 단계 범위로 기준·변경 지침을 따라 메인 읽기와 명령 호출을 각각 재현한다. 기준 실행의 실제 읽기 범위도 그대로 기록한다. 메인에게 반환된 참조 텍스트, CLI stdout·stderr, 실패 진단용 상세 조회의 문자 수를 항목별로 기록한다. 같은 절의 재열람도 합산한다. RUN에 저장한 본문과 담당자가 읽은 양은 메인 수치와 구분한다. 각 결과에 파일·절·실행 명령을 남기고, 확인된 범위의 절감량을 보고한다.
- [x] **최종 결과를 확인한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests -q`와 `git diff --check`를 실행한다. 기준과 실패·건너뛰기 이름을 대조한다. 원본 1116의 전체 파일 목록과 해시, 복사본의 원본 자료 해시, Git 변경 경로를 확인한다. `comparison.md`에 독립 리뷰, 판정 일치 여부, 실제 측정 범위와 수치, 남은 검증을 적는다. 1116 비교는 읽기·선별·감사 재현 범위로 보고하고, 실화면 검사를 수행했다는 판정은 해당 실행의 실제 증거가 있을 때만 기록한다.
