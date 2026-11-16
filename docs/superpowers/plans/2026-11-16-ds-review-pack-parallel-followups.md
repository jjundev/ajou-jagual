# 자구알 복습팩의 문제설명·확인문제 병렬화 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 발행된 복습팩을 근거로 문제설명과 확인문제를 별도 컨텍스트에서 병렬로 생성·검증하고, 메인만 통과한 산출물을 각각 발행한다.

**Architecture:** 문제설명은 기존 `mpe_cli.py`의 작업본·발행 경계를 재사용한다. 확인문제는 고유 RUN 안에 실제 발행과 같은 상대 경로로 작업본을 만들고, 현재 입력·검토 기록·작업본이 일치할 때 기존 팩 잠금 아래 확인문제 소유 파일만 발행한다.

**Tech Stack:** Python 3.10+ 표준 라이브러리, pytest, 기존 Playwright·Chromium과 실제 화면 확인 도구, 기존 `publication_lock`과 `publish_update`.

**Spec:** 이 문서의 [설계 기준](#설계-기준). 직전 `grill-yourself`의 「문제설명·확인문제 병렬 생성 설계」를 실행자가 읽을 수 있도록 옮겼다.

## Global Constraints

- `복습노트/`에는 메인만 쓴다. 서브에이전트는 자기 RUN에만 쓴다. 서브에이전트의 Python 실행은 `PYTHONDONTWRITEBYTECODE=1`로 하고 명령 임시 파일과 화면 기록도 자기 RUN에서 관리한다.
- 기본 팩과 PDF의 기존 검증·발행을 먼저 마친다. 신규(`MMDD`·`MMDD-MMDD`, `lite` 포함)는 두 후속 작업을 병렬 시작한다. `update-existing`·`revise-existing`은 문제설명만, `bank`는 문제은행만 처리한다. 0문항 팩은 문제설명을 건너뛰고 신규 모드의 확인문제 조건은 그대로 적용한다.
- `lite`의 기존 6단계 내용 리뷰 생략 범위를 지킨다. 문제설명의 원자료 시각 대조·내용 검토·독립 검산·실화면, 확인문제의 규칙·블라인드 r1~r3·실화면·대상 팩 배치를 모두 적용한다. 기계 검사 통과와 실제 화면 판정은 별도 증거다.
- 확인문제 작성자·풀이자는 새 컨텍스트를 쓴다. 모델 선택은 현행 확인문제 스킬의 두 번째 등급 및 단일/순위 미확인 규칙을 따른다. 풀이자에게는 브리프·해당 회차 문제 사본·정리노트 MD만 읽기 입력으로 넘긴다.
- 각 후속 산출물은 독립적으로 `published`·`withheld`·`skipped`를 판정한다. 보류 시 기존 파일과 기본 팩·PDF를 보존하고, 작업본과 이유를 해당 RUN에 남긴다.
- 기존 단독 호출 및 공개 파일 형식과 호환한다. 정식 스킬 경로는 `.agents/skills`를 사용한다. 커밋은 사용자 승인 후, 푸시·PR은 별도 요청 시에만 한다.

## Review Focus

1. 실화면을 본 뒤 공용 CSS·글꼴 또는 정리노트의 로컬 자원이 바뀌면 발행을 거부한다. Task 2의 `test_publish_refuses_changes[shared-font]`, `[note-local-asset]`.
2. 같은 RUN에서 재검사한 뒤 이전 브라우저 결과를 제출하거나 4개 조합 중 하나를 중복 제출하면 발행을 거부한다. Task 2의 `test_publish_refuses_review[old-attempt]`, `[duplicate-case]`.
3. NFD 이름으로 저장된 팩 및 JSON 원고만 있는 팩에서도 실제 경로와 중복 검사 대상을 유지한다. Task 1의 `test_prepare_mirrors_pack[nfd-archive]`.
4. 기존 확인문제를 갱신하는 동안 다른 실행이 먼저 발행하거나, 여러 파일 중 두 번째 교체가 실패하면 기존 파일과 관련 없는 파일을 보존한다. Task 2의 `test_publish_refuses_changes[live-owned]`, `test_publish_rolls_back_second_replace`.
5. 중첩 호출을 지원하지 않는 환경에서도 풀이자에게 정답·이전 대화가 노출되지 않아야 한다. Task 3의 `test_blind_relay_contract`, Task 5의 브리프·회차별 컨텍스트 확인.

---

## 설계 기준

- 메인은 두 RUN의 절대 경로와 입력을 정하고, 신규에서는 두 담당 에이전트를 띄운 후 결과를 기다린다. 보고 형식은 `ready|withheld|skipped`, 미해결 항목 또는 이유, RUN과 기록 경로다. 메인은 자신이 지정한 RUN의 발행 명령을 호출하고 최종 상태와 발행·백업 경로를 보고한다.
- 확인문제는 `RUN/stage/복습노트/<range>/`를 실제 팩처럼 배치한다. 블라인드 자료와 화면 기록은 RUN에 둔다. 검토한 HTML을 그대로 발행하고, 공개 자료 폴더에는 현행 JSON 네 개를 둔다.
- 문제설명은 발행된 정확한 문제 원고를 `extract --repo REPO --target ABS_REVIEW --run EXPLAIN_RUN`으로 읽고 기존 네 검토를 완료한다. 문제설명 흐름의 마지막 쓰기는 RUN의 검토 기록이다. 메인은 기존 `publish --run EXPLAIN_RUN` 판정을 사용한다.
- 중첩 호출이 불가능하면 메인이 경로만 받아 확인문제 작성자와 회차별 풀이자를 새 컨텍스트에 띄우고 완료 경로만 돌려준다. 독립 컨텍스트나 실제 화면 검증을 확보할 수 없는 작업은 보류한다.

## 파일 지도

| 파일 | 책임 |
|---|---|
| `.agents/skills/ds-concept-check/scripts/concept_release.py` 및 `tests/test_release.py` | 대상 팩과 RUN 준비, 검토 요청, 발행 검증·복구와 회귀 시험 |
| `.agents/skills/ds-concept-check/scripts/build.py`, `browser_check.py`, `.agents/skills/ds-review-pack/scripts/assemble.py` | 작업용 자원·브라우저 루트 인자와 기존 인자 호환 |
| `.agents/skills/ds-concept-check/SKILL.md` | 단독 모드와 작업본 모드에서 기존 검증을 수행하고 근거를 남기는 방법 |
| `.agents/skills/ds-review-pack/SKILL.md`, `references/pack-followups.md` | 모드 선택, 병렬 시작, 풀이자 중계, 메인 발행·요약 |
| `.agents/skills/ds-review-pack/references/problem-explain.md`, `review-overhaul.md`, `textbook-update.md`, `tests/test_skill_files.py` | 정확한 문제 원고·검증 계약, 갱신 모드 연결과 문서 회귀 시험 |
| Rehearsal RUN의 `comparison.md` | 독립 리뷰·실행·해시·컨텍스트 측정과 보류 근거 |

### Task 1 — 저장소 밖에 검증 가능한 확인문제 작업본 준비

**Files** · Create `ds-concept-check/scripts/concept_release.py`, `ds-concept-check/tests/test_release.py`. Modify `ds-concept-check/scripts/build.py`, `ds-concept-check/scripts/browser_check.py`, `ds-review-pack/scripts/assemble.py`. 스킬 파일의 기준 디렉터리는 `.agents/skills/`이다.

**Interfaces**

- `concept_release.prepare(repo: Path, range_: str, run: Path) -> Path`. CLI `prepare --repo REPO --range RANGE --run RUN`은 작업용 SRC 절대 경로 한 줄을 출력한다. 고유한 비어 있는 외부 RUN에서 `prepare.json`은 `version: 1`, `repo`, `range`, `slug`, `inputs`, `owned_before`를 기록한다. `inputs`는 REPO 상대 경로 → SHA-256, `owned_before`는 같은 기준으로 발행 대상 경로 → SHA-256 또는 `null`이다. 나머지 경로는 이 값과 정해진 파일명으로 계산한다.
- `assemble.asset_root(out_dir: Path, *, assets_dir: Path | None = None) -> str`, `build.render_page(src: Path, *, assets_dir: Path | None = None) -> str`, `build.build(src: Path, *, assets_dir: Path | None = None) -> Path`. 새 CLI 옵션 `build.py SRC --assets-dir DIR`를 쓰면 `stage/복습노트/_assets/problem-explain/v1`에서 자원 경로를 계산한다. `browser_check.py`는 기존 `check(..., serve_root=...)`를 `--serve-root DIR`로 연결한다.

- [x] **0. 변경 전 시험 기준을 기록한다.** Task 3의 세 pytest 명령을 실행해 기준 커밋, 통과 수, 실패·건너뛴 테스트 ID를 저장소 밖 Rehearsal RUN에 보관한다.
- [x] **1. 작업본 테스트를 쓴다.** `test_prepare_mirrors_pack`을 `legacy-html`·`nfd-archive`·`zero-cards`로 매개변수화한다. 기존 Mini fixture에 작업용 정리노트 MD와 원고 형식별 입력을 둔다. `assert src.is_relative_to(run / "stage")`, `assert review_paths(stage_pack)`(0문항은 빈 목록), `assert owned_hashes(live_after) == owned_hashes(live_before)`. 기존 확인문제 네 JSON과 공개 HTML이 stage에 없는 상태를 단언한다. `test_prepare_requires_pack_evidence`의 `missing-stt`·`missing-note-md`·`missing-note-html`은 준비가 실패하고 기존 파일 해시가 같은지 확인한다.
- [x] **2. 경로 재현 테스트를 쓴다.** `test_staged_build_uses_final_relative_urls`에서 실제 stage와 팩의 깊이가 다른 경우에도 같은 입력으로 렌더한 HTML이 바이트 단위로 같은지, stage에서 정리노트 토픽 링크와 자원 파일을 찾는지 단언한다. `test_browser_cli_accepts_stage_root`는 실제 Playwright로 1280×900·375×812, light/dark 4개 조합을 통과시키고 `report["html"]`이 stage 기준 상대 경로인지 확인한다.
- [x] **3. 실패를 확인한다.** `python3 -m pytest .agents/skills/ds-concept-check/tests/test_release.py -k 'prepare or staged_build or browser_cli' -q`. 새 진입점과 CLI 옵션이 없어서 실패해야 한다.
- [x] **4. 작업본 경로 인자를 구현한다.** `assemble.py`, `build.py`, `browser_check.py`에 위 옵션을 전달하고 현재 기본값과 단독 호출을 보존한다.
- [x] **5. 준비를 구현한다.** 팩 잠금 아래 최종 manifest·STT·정리노트 HTML/MD와 `review_paths`가 읽는 실제 원고를 복사한다. 0문항 팩의 중복 검사 입력이 비어 있을 수 있다. 정리노트에서 참조하는 로컬 자원은 `browser_review.render_urls`·`local_asset`을 재사용해 CSS·SVG의 의존성까지 복제하고, 해당 공용 자원 폴더 전체를 같은 상대 경로로 복사한다. 대상 이름은 manifest의 range/slug와 기존 명명 형식으로 제한한다. 실경로·NFC/NFD를 확인하고 모호한 이름, 경로 이탈, 공개본으로 연결된 stage 링크를 거부한다. 기존 파일을 stage에 복사해 쓰기 대상으로 삼을 때는 독립된 사본을 사용한다. 준비 후 SRC에는 이번 실행의 작성 결과만 들어간다.
- [x] **6. 관련 테스트를 통과시킨다.** `python3 -m pytest .agents/skills/ds-concept-check/tests/test_release.py .agents/skills/ds-concept-check/tests/test_build.py .agents/skills/ds-concept-check/tests/test_browser.py -q`. legacy 빌드와 새 stage 조합이 통과해야 한다. Chromium을 실행할 수 없으면 환경 원인을 기록하고 Task 5에서 실제 브라우저 검증을 완료한다.

### Task 2 — 확인문제의 검토 기록을 대조해 메인에서 발행

**Files** · Modify `.agents/skills/ds-concept-check/scripts/concept_release.py`, `.agents/skills/ds-concept-check/tests/test_release.py`.

**Interfaces**

- `concept_release.write_review_request(repo: Path, range_: str, run: Path) -> Path`. CLI `review-request --repo REPO --range RANGE --run RUN`은 `RUN/review-request.json` 경로를 출력한다. 요청은 `version: 1`, `attempt`(새 UUID hex), `prepare_sha256`, `artifacts`(stage 상대 경로 → SHA-256. HTML·목표·문항·블라인드 장부), `cases`(필수 조합 ID 목록)를 담는다. 규칙 검사, r1~r3 블라인드 장부, 대상 stage 배치와 현재 입력 사본을 확인한 뒤 발급한다.
- 브라우저 실행은 `RUN/browser/<attempt>/browser.json`과 같은 폴더의 `shots/`에 기록한다. 수동 판정 `RUN/browser/<attempt>/visual-review.json`은 `version: 1`, `request_sha256`, `browser_report_sha256`, `reviewer`, `status: pass|fail|unavailable`, `cases`(필수 ID → `{status, observation, screenshots}`)를 담는다. ID는 `1280x900/light` 같은 형식이다. 각 조합에서 첫 문항·힌트·마지막 화면 캡처를 모두 열고 기록한다. 캡처 경로는 해당 attempt 폴더 상대 경로다.
- `concept_release.publish(repo: Path, range_: str, run: Path) -> Path`. CLI `publish --repo REPO --range RANGE --run RUN`은 성공 시 공개 HTML·백업 경로를 한 줄로 보고한다. 실패 시 이유와 비영 종료 코드를 반환한다. 공개 대상은 해당 확인문제 HTML, 해당 자료 폴더의 `objectives.json`, `items.json`, `blind-ledger.json`, 이번 attempt의 `browser.json`이다.

- [x] **1. 발행 회귀 테스트를 쓴다.** `test_publish_writes_only_owned_bytes`는 HTML의 발행 해시가 검토한 해시와 일치하고 기존 PDF·정리노트·문제설명·다른 팩 파일의 해시가 같다고 단언한다. `test_publish_refuses_review`에 `missing-record`, `machine-only`, `manual-fail`, `old-attempt`, `missing-case`, `duplicate-case`, `missing-shot`, `objection`, `round-4`, `bad-layout`을 둔다. 각 경우에서 `pytest.raises(ValueError)`와 공개 파일 해시 보존을 단언한다. 기계·수동 승인 픽스처는 이 자동 시험에서만 쓴다.
- [x] **2. 변경과 복구 회귀 테스트를 쓴다.** `test_publish_refuses_changes`에 `staged-html`, `items`, `ledger`, `browser-report`, `live-manifest`, `new-review-input`, `shared-font`, `note-local-asset`, `live-owned`를 둔다. 파일을 변경하거나 원고를 한 개 추가한 뒤 발행 직전 공개 해시가 유지돼야 한다. `test_review_request_rejects_unbuilt_items`는 빌드 후 차이가 HTML에 반영되는 문항 변경을 가하고 요청 생성을 거부하는지 확인한다. `test_publish_rolls_back_second_replace`는 대상 교체의 두 번째 `os.replace`에 실패를 주입하고 기존 파일과 파일이 없었던 경로 모두 원상복구됐는지 확인한다. `test_publish_rejects_stage_or_destination_symlink`는 연결된 경로에 쓰기 전에 실패해야 한다.
- [x] **3. 실패를 확인한다.** `python3 -m pytest .agents/skills/ds-concept-check/tests/test_release.py -k 'publish or review_request' -q`. 검토 요청과 발행 진입점이 아직 없어 실패해야 한다.
- [x] **4. 검토 요청을 구현한다.** 기존 `check.check`, `blind.status`, `pack_layout.check_layout`을 재사용한다. 장부 회차는 정수 1~3이어야 하고 미해결 문항은 0개여야 한다. 현재 목표·문항으로 메모리에서 렌더한 결과가 작업 HTML과 일치할 때 해시를 고정하고 새 attempt를 만든다. 재조립 또는 검토 대상 변경 시 규칙·블라인드 상태를 다시 확인하고 새 브라우저 요청으로 진행한다. 블라인드 장부가 무효로 표시한 문항만 기존 최대 r3 범위에서 다시 푼다.
- [x] **5. 발행을 구현한다.** `release_review.publication_lock`과 기존 잠금 함수를 쓴다. 잠금 안에서 실제 REPO/range, NFC/NFD 목적지, `owned_before`, 요청과 현 작업본, 대상 팩 배치를 다시 확인한다. live/stage의 현재 유효 근거를 다시 탐색해 경로 집합과 해시가 모두 준비 기록과 같은지 검사한다. 규칙 검사와 블라인드 상태를 재확인한다. 브라우저 보고서는 현재 HTML의 경로·해시, 정확한 4개 조합의 유일한 통과 행, 빈 실패 목록을 요구한다. 수동 기록은 현재 요청과 보고서 해시가 같아야 하고 전체 및 조합별 `pass`, 검사자, 각 조합의 관찰과 해당 attempt 캡처가 필요하다. 소유 파일 바이트만 모아 `update_review.publish_update(..., backup=RUN/"backups"/ATTEMPT)`로 교체한다. 검토하는 동안 공개 파일을 먼저 수정하지 않으므로 검토 실패는 RUN 기록만 보존한다. 교체 예외는 기존 복구 루틴으로 처리하고 후보·검증 기록·사유를 RUN에 남긴다.
- [x] **6. 발행·검증 관련 테스트를 통과시킨다.** `python3 -m pytest .agents/skills/ds-concept-check/tests -q`. 브라우저 실행 결과와 별도로 1~3회차 및 fail-closed 회귀 조건이 모두 통과해야 한다.

### Task 3 — 복습팩 모드와 서브에이전트 연결

**Files** · Create `.agents/skills/ds-review-pack/references/pack-followups.md`. Modify `.agents/skills/ds-review-pack/SKILL.md`, `references/problem-explain.md`, `references/textbook-update.md`, `references/review-overhaul.md`, `tests/test_skill_files.py`와 `.agents/skills/ds-concept-check/SKILL.md`. 갱신 레퍼런스 및 테스트 경로는 `ds-review-pack/` 기준이다.

**Interfaces** · Tasks 1~2의 `concept_release.py` 세 명령, 기존 `mpe_cli.py extract|build|check|preview|publish`. 문제설명과 확인문제 담당자는 각자의 예상 RUN에 `ready|withheld|skipped`, 사유, 검증 기록 경로를 반환한다. 메인은 RUN을 스스로 정하고 알려진 경로만 발행 명령에 넣는다.

- [x] **1. 문서 회귀 테스트를 쓴다.** `test_followups_start_after_base_publish`는 8단계의 기본 팩 발행 → 공통 후속 작업 → 전체 배치 순서를 확인한다. `test_followup_modes_and_publish_owner`는 공통 지침에 신규 병렬, 두 갱신 모드의 문제설명 전용, 0문항, 메인 발행, 독립 보류 규칙이 명시되고 두 갱신 레퍼런스 모두 같은 지침으로 연결되는지 확인한다. `test_blind_relay_contract`는 중계 조항에 브리프·현재 사본·정리노트 MD, 새 컨텍스트, r3 상한과 정답 자료의 열람 금지가 명시되는지 확인한다. 기존 `test_concept_check_*`는 옛 순차 문구 검사에서 같은 동작 계약을 검사하도록 갱신한다.
- [x] **2. 실패를 확인한다.** `python3 -m pytest .agents/skills/ds-review-pack/tests/test_skill_files.py -q`. 새 후속 연결·역할 규칙 테스트가 실패해야 한다.
- [x] **3. 공통 연결을 문서화한다.** `pack-followups.md`에 메인의 존재 확인과 RUN 지정, 신규 두 작업을 한 번에 시작하는 조건, 자식에 넘길 최소 입력, 각 작업의 발행 준비 신호와 메인의 발행 명령을 둔다. 문제설명은 원고·REPO가 이번 실행에 지정한 대상과 일치하는 단일 RUN인지 확인하고 기존 발행기를 실행한다. 8단계와 두 갱신 경로에서 이 공통 절로 연결한다. `references/problem-explain.md`의 실제 네 검토와 문제 원고 절차를 보존하고 발행을 메인 절로 옮긴다.
- [x] **4. 확인문제 작업본 모드를 문서화한다.** 현행 1~8단계에서 사용할 작업용 SRC와 자원 루트, 검토 요청 후 브라우저 네 조합과 수동 판정 기록을 지정한다. 블라인드 풀이 변경과 복사 방향을 그대로 적용한다. 중첩 호출이 불가하면 담당자가 요청 회차·세 읽기 경로·해당 회차 답안 출력 경로만 전달하고, 메인은 새 컨텍스트를 열어 답안 파일 경로만 담당자에게 돌려준다. 작성자 재호출에도 기존 모델·수정 한도를 적용한다. 본문에 남은 `opus` 표기는 현행 확인문제 모델 규칙 참조로 바꾼다.
- [x] **5. 세 스킬의 회귀 시험을 수행한다.** 아래 명령을 별도 프로세스에서 실행해 같은 이름의 테스트 모듈이 충돌하지 않게 한다. 실패 또는 건너뛰기가 있으면 변경 전 동일 명령 결과와 이름을 대조한다.

  ```bash
  python3 -m pytest .agents/skills/ds-review-pack/tests -q
  python3 -m pytest .agents/skills/ds-problem-explain/tests -q
  python3 -m pytest .agents/skills/ds-concept-check/tests -q
  git diff --check
  ```

### Task 4 — 구현과 분리된 독립 리뷰

**Inputs** · 변경 전 기준 커밋, 전체 작업 diff, 이 계획, 세 스킬의 시험 출력. **Output** · Rehearsal RUN의 리뷰 기록과 보완 후 재확인 결과.

- [x] **1. 새 컨텍스트의 리뷰어에게 읽기 전용으로 검토를 맡긴다.** 검토 기준은 메인만 공개 경로에 쓰는지, 새 풀이자 격리·r3·검증 기록을 보존하는지, stale·부분 실패·동시 실행에서 이전 파일을 보존하는지, 단독·갱신 경로가 유지되는지다. 리뷰어가 구현 과정의 요약 없이 diff와 근거 파일로 재현하도록 한다.
- [x] **2. 발견 사항을 검증하고 보완한다.** 재현 가능한 결함은 관련 테스트와 함께 수정하고 영향받은 시험을 다시 실행한다. 발행 경계나 검증 조건을 건드린 수정은 같은 리뷰어 또는 새 독립 리뷰어에게 재확인 받는다. 남은 판단이나 기존 시험 실패는 최종 보고에 식별 가능하게 적는다.

### Task 5 — 1116 복사본에서 실제 병렬 실행과 발행 확인

**Inputs** · 1116에 이미 발행된 정리노트·PDF·문제 원고·문제설명·확인문제, 현재 작업 스킬, 참조 자료와 브라우저 자원. **Output** · 저장소 밖 `REHEARSAL_RUN/comparison.md`와 각 검사·발행 기록.

- [x] **1. 복사본과 기준 해시를 준비한다.** 임시 저장소에 현재 스킬과 1116의 참조 자료·자원을 원래 상대 경로로 복제한다. 문제 원고는 실제 `복습노트/1116/.pack/자료_복습팩/복습문제_1116_Graph.json`의 복사본이다. NFC/NFD로 실파일을 찾고 원본·복사본 1116의 기준 파일 목록과 SHA-256을 각각 기록한다. 이미 발행된 팩을 신규 후속 단계의 입력으로 삼는다.
- [x] **2. 두 작업을 실제로 병렬 실행한다.** Task 3 경로로 설명과 확인문제를 한 번에 띄우고 시작·종료 시각을 기록해 실행 구간이 겹치는지 확인한다. 확인문제는 새 풀이자에 전달된 입력 범위와 실제 회차, 문제설명은 실제 네 검토를 기록한다. 각 작업의 화면 검증 기록을 확인하고, 발행 호출 직전까지 원본과 복사본의 공개 해시가 각 기준값과 같은지 확인한다. 갱신 모드 분기는 검증용으로 따로 실행해 기존 확인문제 해시가 유지되는지 확인한다.
- [x] **3. 양쪽 성공과 양방향 부분 실패를 확인한다.** 양쪽 성공에서는 메인이 각각 발행하고, 공개 링크와 검토본/발행본 해시를 비교한다. 별도 RUN에서 확인문제 작업본을 검토 직후 변경해 확인문제만 거부되고 설명은 발행되는지 확인한다. 반대 시험에서는 문제설명의 실제 검토 기록 하나를 `not_run`으로 바꿔 설명만 거부되고 확인문제는 발행되는지 확인한다. 각 시행은 알려진 기준 상태와 해당 시도의 실제 검토 기록에서 시작한다. 실패한 쪽의 기존 파일과 기본 팩·PDF가 그대로인지 파일 목록과 해시로 확인한다.
- [x] **4. 1116 자체 결함이 통과를 막으면 구분해 기록한다.** 원본과 복사본의 기존 공개 파일을 보존하고 어느 검증이 무엇을 발견했는지 남긴다. 성공 및 양방향 부분 실패 재현이 1116에서 막히면 별도 소형 팩에서 동일한 실제 검증과 발행 절차를 완료한다. 실제 리허설에서 합성 승인이나 기존 검토 기록의 재사용으로 통과를 만들지 않는다.
- [x] **5. 결과를 정리한다.** 시나리오별 발행·보류 상태, 미해결 조건, 백업·RUN·증거 경로, 원본 해시 대조, 독립 리뷰 결과를 기록한다. 후속 생성 구간의 메인 이미지 열람 수, 메인 도구 출력 문자 수, 측정 범위를 남긴다. 정상 위임에서 메인의 이미지 열람은 0회여야 한다. 동일 구간의 이전 로그가 있는 경우에만 비교하며, 전체 세션 절감률은 구간 측정과 구분한다. 마지막으로 `git diff --check`와 `git status --short`로 사용자 검토 범위를 확인한다.

## 실행 중 보완

- 복습팩 메인의 문제설명 발행에 `ds-review-pack/scripts/followup_explain.py`를 추가했다. 기본 팩과 같은 잠금에서 이번 원고와 이전 설명을 대조한 뒤 기존 문제설명 발행기를 호출한다.
- 확인문제 화면 기록은 브라우저 실행의 요청 ID와 해시, 검사 전후 작업본·자원 해시, 검사한 캡처의 해시에 연결했다. 실제 리허설에서 발견한 일시적인 채점·복사 알림은 자연히 사라진 뒤 캡처한다.
- 1116에서 확인문제는 복사본에 발행했고 문제설명은 P3·P5·P6의 원자료 충돌로 보류했다. 별도 소형 팩의 세 사본에서 두 작업 성공과 두 방향의 부분 실패를 모두 확인했다. 시험·공개본 해시와 시행별 증거는 외부 Rehearsal RUN의 `comparison.md`에 기록했다.
