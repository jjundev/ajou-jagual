> 후속 UI·글꼴 갱신 결과는 [생명과학 UI 일치 검증](2026-10-17-ds-interactive-ui.md)을 따른다. 아래는 최초 구현 당시 기록이다.

# ds-interactive 구현·검증 기록

2026-10-17 · Native · 관리 워크트리 HEAD 6b170af. 커밋·푸시·외부 게시 없음.

## 구현 범위

`.agents/skills/ds-interactive`에 공통 Trace/플레이어, C 메모리 이벤트 엔진, DOM/SVG 렌더러, 저작 예제, resolve/check/steps/build/review/save/link/relink CLI와 지침을 구현했다. `.claude/skills/ds-interactive`는 `.agents` 원본을 가리키는 상대 심볼릭 링크다. 모델·서브에이전트 사용을 새 스킬에 강제하지 않는다.

새 어댑터를 등록할 경계는 마련했으며 첫 구현은 c-memory다. 큐·트리·정렬 시뮬레이터와 임의 C 실행기는 포함하지 않는다.

## 실제 검사

| 명령/검사 | 결과 |
|---|---|
| `node --test .agents/skills/ds-interactive/tests/*.test.cjs` | 26/26 통과 |
| skill-creator `quick_validate.py .agents/skills/ds-interactive` | Skill is valid |
| `python .agents/skills/ds-interactive/tests/independent.py EVIDENCE` | 38개 조건, bind/declaration/write 144건 일치 |
| `python .agents/skills/ds-interactive/tests/browser_discovery.py` | 1/2/4 자료·직접 HTML·0928 외 날짜 탐색 통과 |
| `python .agents/skills/ds-interactive/tests/browser_regressions.py PREVIEW` | 숫자 입력 도중 즉시 정지, 초기화, 단계 숫자, 키보드 셀 포커스 통과 |
| `browser_acceptance.py RUN_PARENT SCRATCH` | 3자료 × 3화면 × 2테마 = 18조합, 기본/모든 preset의 852 Snapshot 검사 |
| 실제 브라우저 | Chromium · file:// · offline=True · 1440×900,1024×768,375×812 · light/dark |
| 외부 HTTP 요청 / 콘솔 오류 / 문서 가로 넘침 | 0 / 0 / 0 |
| 수동 시각 확인 | 세 자료의 데스크톱·태블릿·모바일 캡처, 읽기/쓰기·화살표·소스 줄·단계 숫자 확인 |
| 원문 확인 | 0928 HTML/.pack MD/STT와 PDF p20/22/25를 실제 대조, PDF 렌더링 확인 |
| 독립 검산 한계 | PATH에 gcc/clang/cl 없음. C 컴파일 실행을 주장하지 않으며 별도 Python 표 사용 |

기본 호출 깊이 64·객체 256 경계와 초과, 단계 제한, 불변 상태, 별칭·해제·반환 수명, 구조체의 포인터 필드 얕은 복사·배열 인자 조정·오류 중단을 검사했다. save 검토 미완료/실패/논쟁·변경 해시·근거 누락을 차단한다. 동시 다른 이름 저장도 번호 단위 lock으로 구분한다. 링크 파서는 주석·script 속 가짜 ID와 중복 절을 배제하며, 백업·이동·재연결을 검사했다.

## 원본과 보충

값/주소 자료의 포인터 swap 본문은 강의 p22와 같다. 헤더·int main(void)·입력 템플릿·호출자와 비교/별칭 모드는 보충이다. 포인터/대상과 이중 포인터의 함수 예제는 p20/p25 개념을 확장한 보충이다. 원문 main()은 동봉 PDF 페이지 추출 근거에 그대로 보존했다. NULL은 실제 UB 실행 없이 원인 단계에서 진단한다.

폰트는 기존 저장소의 Pretendard Regular를 복사했으며 원본·SHA-256·OFL을 기록했다. OFL은 독립 HTML에도 포함한다. bio-interactive의 링크 offset 파서를 이식했고 원본 해시와 변경 범위를 assets/vendor/provenance.json에 남겼다. 다른 과목 저장소에는 쓰지 않았다.

## 검토와 수정

Native 구현자는 전체를 직접 구현했다. writing-skills의 독립 대조 평가에서 기존 판단의 C 의미는 이미 정확했으나 번호·검토 해시·relink 계약이 없음을 확인했다. SKILL은 이 지역 규약과 재현 가능한 CLI를 제공한다. 이후 새 컨텍스트의 최종 리뷰어가 실제 스킬/근거만 읽어 올바른 0928 작업 절차를 구성했다.

최종 별도 리뷰는 Critical 없음, Important 4개와 Minor 1개였다. 숫자 편집 시 change/blur 대기, NFD 한글 노트 누락, 다른 이름의 동시 번호 예약, 검증기 3개/0928 고정은 각각 재현 테스트 실패 후 수정·통과했다. 키보드 선택 뒤 포커스 손실은 키보드 조작 수용 조건에 영향을 주므로 Important로 재분류해 같은 수정 패스에서 해결했다. 재리뷰로 합격을 추정하지 않고 회귀 테스트·전체 새 스킬 검사를 실행했다. 미해결 리뷰 항목은 없다.

캡처에서 발견한 단계 숫자 갱신과 무효 입력 초기화 문제, 생성기 조기 소비, 하위 증거 해시 누락, 독립 HTML의 OFL 동봉도 RED→GREEN으로 고쳤다.

## 실행 중 결정과 비용

1. Windows에 Bash 래퍼 실행기가 없어 작업 brief/ledger와 실제 명령 결과를 직접 기록했다. 테스트 기능은 유지하며 비용은 수동 진행기록이다.
2. `Source.text`의 정수 `{{key}}` 치환과 첫 이벤트 기준 초기 위치를 추가했다. 입력과 표시 코드가 일치하며 비용은 문서화한 작은 저작 형식 확장이다.
3. 이미 승인된 bio 참조·화면 설계 안에서 UI 지침을 적용했다. 새 시각 방향 인터뷰와 저장소 루트 PRODUCT/DESIGN 생성은 하지 않았으며 비용은 대안 시각안이 없다는 점이다.
4. 키보드 포커스 문제는 필수 조작에 영향을 주므로 수정 대상으로 올렸다. 비용은 Cell ID 기반 포커스 복원 코드다.
5. 기존 전체 Python 검사 실패는 이번 작업 범위 밖이므로 원본을 보존했다. 비용은 아래의 저장소 전체 실패가 남는 점이다.
6. 승인된 계획의 커밋·푸시 없음 결정을 유지하고 관리 워크트리를 보존한다. 미커밋 근거를 잃지 않도록 작업 workspace도 보존하며 비용은 임시 검토 파일의 로컬 디스크 사용이다.

## 기존 저장소 전체 검사

`python -m pytest -q`: **62 passed, 7 failed**. 실패 파일은 이번 작업에서 변경하지 않았다(`git diff HEAD`로 확인). core.autocrlf=true 환경에서 기존 HEAD/개행 해시와 교과서 SVG 바이트·리뷰 해시 문제로 실패했다. 새 스킬의 Node 검사 결과와 구분한다.

- docs/verify/test_record_ds_explain_overrides.py::test_record_chains_on_existing_override
- docs/verify/test_record_ds_explain_overrides.py::test_record_noop_when_unchanged
- 교과서/제작자료/tests/test_delivery.py::test_rollback_preserves_foreign_replacement
- 교과서/제작자료/tests/test_delivery.py::test_success_json_last_and_no_overwrite
- 교과서/제작자료/tests/test_delivery.py::test_final_chapter_package_verifies
- 교과서/제작자료/tests/test_delivery.py::test_publish_chapter_files_last
- 교과서/제작자료/tests/test_validation.py::test_complete_inventory

개별 결과는 [repo-suite-summary.json](ds-interactive-2026-10-17/repo-suite-summary.json)에 보존한다. 전체 저장소가 통과했다고 주장하지 않는다.

## 최종 저장·연결

최종 경로 검사까지 통과했다. 각 자료 `.pack`에는 현재 해시를 가진 review.json과 schema/content/independent/browser 실제 근거·캡처를 동봉했다.

- [인터렉티브_01_값과주소전달.html](../../복습노트/0928/인터렉티브_01_값과주소전달.html)
- [인터렉티브_02_포인터와대상값.html](../../복습노트/0928/인터렉티브_02_포인터와대상값.html)
- [인터렉티브_03_이중포인터.html](../../복습노트/0928/인터렉티브_03_이중포인터.html)

`final_paths.py`는 세 공개 HTML과 검토 preview의 바이트 일치, 최종 file:// 폰트·단계 이동, 네 노트 링크의 현재 탭 이동·뒤로가기를 확인했다. 기존 노트의 페이지 방식에 맞춰 실제 절의 hash 경로에서 링크를 클릭했다. 모든 왕복은 같은 탭에서 이루어졌다. [final-paths.json](ds-interactive-2026-10-17/final-paths.json), [delivery.json](ds-interactive-2026-10-17/delivery.json).

재연결 dry-run은 네 링크 모두 unchanged다. 원본 182개 파일 해시 중 변경은 노트 HTML 하나이며, 추가 문맥 링크 네 문장을 제거한 나머지 바이트는 최초 원본과 같다. MD·STT·PDF·기존 assets는 불변이다. [preservation.json](ds-interactive-2026-10-17/preservation.json). 수정 전 노트 bytes는 backups/에 보존했다.

최종 판정: 요청한 새 스킬과 0928 세 자료·노트 연결·오프라인 검증 완료. 기존 전체 Python 실패 7개와 C 컴파일러 부재는 위에 구분해 기록했다. 남긴 미해결 새 스킬 리뷰 항목은 없다.
