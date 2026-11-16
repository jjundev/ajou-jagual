# 전체 문항 개편과 공통 품질 게이트

`revise-existing [MMDD|all] [lite]`는 기존 문항을 유지·이동·통합·교체하는 모드다. `update-existing`는 기존 카드를 보존하며 교과서 원문을 추가하는 별도 모드다. 사용자가 전체 재검토를 요청했을 때만 개편 모드를 쓴다. `bank`는 이 절차를 실행하지 않는다.

신규·update-existing·revise-existing 모두 최종 manifest→출처→팩 HTML→전체 audit→MD→실화면→PDF·팩 발행→문제설명 순서의 검증을 따른다. lite도 출처·중복·설명·PDF 검증은 생략하지 않는다.

## 변경 전 전역 목록

메인은 작업 시작 전에 `collect_reviews(Path(REPO))` 결과를 stdout 대신 `RUN/baseline.json`에 UTF-8 JSON으로 저장한다. 기존 기출의 고유 source 목록도 별도 대조한다. 여러 팩을 갱신할 때도 변경 전 전체 목록 하나를 기준으로 사용한다. 과거 누락을 복구할 때는 복구 대상 기출 ID 배열을 `RUN/required-exams.json`에 둔다.

## 개편 준비

먼저 고유 RUN에 변경 전 팩 전체와 보호 대상 해시를 백업한다. 정리노트 HTML/MD·기존 그림, STT, 강의록, 기출·교과서 원본은 보존한다. 은행은 `python3 "$SKILL/scripts/bank.py" validate "$BANK" --out "$RUN/bank-validation.json"`로, 교과서는 `load_textbook(Path(TEXTBOOK), python=TEXTBOOK_PYTHON)`로 검증한다. 실패한 입력은 고친 뒤 다시 검사하고, 통과한 입력으로만 진행한다.

메인 읽기 — [변경 전 전역 목록](review-overhaul.md).

팩마다 `release_review.py prepare --repo REPO --range MMDD --run PACK_RUN --mode revise-existing`으로 작업 폴더를 만든다. 이 명령이 발행된 원고로 작업용 HTML을 조립한다. stage는 팩별 HTML과 `.pack/자료_복습팩/manifest.json`을 갖는다. `update_review.build_revision`으로 허용 영역만 교체한다. 기존 교과서 추가는 계속 `build_update`를 쓴다.

문제 번호 변경은 내용 버전별 `od-review-solved:<range>:<revision>` 상태 키로 구분한다. 옛 p1의 완료 상태를 새 p1에 이식하지 않는다. 테마·패널·노트 읽음 키는 보존한다. PDF 작성용 표는 pN이 아니라 source ID로 지정한다.

## 선별: 핵심 범위 충족 우선

수업별 핵심 개념·연산·경계 조건·실제 예제 코드의 coverage를 먼저 만든다. 보통 8~12개를 목표로 하되 적합한 문제가 적으면 적게, 핵심 범위가 넓으면 초과한다. 숫자만 바꾼 문제로 개수를 채우지 않는다. 후보 부족은 남은 목표와 이유를 기록하며 강의 예제를 근거로 직접 출제한다. 원문이 없는 예제를 만들고 강의 원문이라고 부르지 않는다.

coverage의 분모는 실제 강의·STT에서 먼저 추출한 핵심 목표다. 선택된 source ID나 문항의 objectives만 다시 나열한 목록은 완전성 검토가 아니다. 목표마다 당일 질문 ID와 자료 위치를 대응하고, 풀이에서만 언급한 내용이나 이후 날짜 문항만으로 당일 coverage를 충족했다고 세지 않는다. 기출이 없으면 코드뿐 아니라 ADT·표현·상태·경계 판단도 강의 개념·그림 기반 생성문제로 평가한다. 예고·과제 지시·보충은 핵심과 구분하고 제외 근거를 남긴다. 문항 없는 섹션과 그 목차 링크는 출력하지 않는다.

전체 날짜의 실제 질문·코드·보기·그림을 비교한다. 기출 `duplicate_of`는 원문 동일성을 확인한 재수록에만 사용하고 대표 출처로 정규화한다. 같은 기출의 반복 수록과 실제 동일 원문 재수록만 차단한다. 서로 다른 기출은 풀이 목표·코드 구조·상수 패턴이 같거나 비슷해도 전부 유지한다. 자체 제작 변형의 중복과 원래부터 다른 기출을 구분한다. 원문 보기·힌트·풀이만 같다는 이유로 중복 판정하지 않는다. 평가 능력이 다르면 같은 개념도 허용하며, 같은 강의 예제의 추적·빈칸·완성은 한 카드의 소문항으로 묶는다. 이 통합 규칙으로 서로 다른 기출을 합치지 않는다. 대표 날짜는 실제 학습 시점과 문제 품질로 고른다.

## 강의 예제 근거

`source_kind: lecture-code`, `source: lecture-s02-p10-power` 같은 ID를 사용한다. `lecture_ref={path,pdf_page,sha256,example,taught_on}`는 저장소 상대 경로, 1부터 세는 PDF 페이지, 현재 파일 해시, 예제 이름, 실제 학습 날짜다. `objectives`는 비어 있지 않은 평가 목표 문자열 목록, `task_family`는 풀이 절차 식별자다. 추가 근거 페이지가 있으면 `extra_pages`를 기록한다.

PDF의 실제 페이지를 열고 STT와 대조한다. 다룸·일부·예고·미학습을 구분하며 모든 소문항이 해당 날짜까지의 범위여야 한다. 강의 PDF가 없거나 아직 배우지 않은 예제는 강의 코드 문제로 승인하지 않는다. 예제 코드가 없는 날짜에 코드 수를 강제하지 않는다.

기존 범위 밖 문항을 보존해야 할 때만 `scope=retained-supplement`, `scope_evidence`에 당일 제외·후속 학습 근거를 기록하고 실제 확인된 `lecture_ref.taught_on`을 사용한다. 화면에도 후속 보충임을 밝히고 당일 핵심 coverage에서 제외한다. 이 보존 예외로 새 범위 밖 문제를 추가하거나 핵심 누락을 채우지 않는다.

카드에는 `강의 예제 기반 자체 출제`, 원문 영역에는 `강의 예제 보기`를 쓴다. 원 코드 발췌, 자체 번역·유사코드, 그림에서 유도한 자체 코드, 실행 harness를 구별한다. 원문에 없는 코드를 원 코드라고 제시하지 않는다. 오류·오래된 main·헤더 생략·주변 함수 가정도 밝힌다. UB·비종료·해제 후 접근·누수는 정상 출력으로 승인하지 않고 결함을 묻는 명시적 문제로 다룬다.

lecture-code 카드의 문제·힌트·풀이·정답은 standalone이다. 강의 페이지·슬라이드·정리노트·다른 문제(Pn, 앞 문제)를 가리키지 않고, 필요한 함수 계약·코드·규칙·값을 본문에 직접 쓴다. 출처는 배지 인용과 `강의 예제 보기`에만 둔다. `check_html`의 `lecture-standalone`이 이를 검사한다.

출처 검사는 lecture-code의 현재 파일·페이지·해시·학습 날짜를 검사한다. 페이지 열람과 학습 근거의 의미 검토는 작성자가 별도로 수행한다.

## 개편 기계 검사

개편 모드는 `MANIFEST`를 최종 작업 폴더의 `.pack/자료_복습팩/manifest.json` 절대 경로로 지정한다. `NOTE`와 `REVIEW`는 같은 작업 폴더의 보존된 정리노트와 최종 복습문제 HTML 절대 경로다. 아래 세 검사가 모두 통과해야 한다. 은행 검사 실패 상세는 현재 `PACK_RUN/bank-manifest-check.json`에서 확인한다. 신규·교과서 추가의 manifest·HTML 검사 명령은 각 모드 단계에 있다.

```sh
python3 "$SKILL/scripts/manifest.py" "$MANIFEST"
python3 "$SKILL/scripts/bank.py" check-manifest "$BANK" "$MANIFEST" --repo "$REPO" --textbook-dir "$TEXTBOOK" --textbook-python "$TEXTBOOK_PYTHON" --out "$PACK_RUN/bank-manifest-check.json"
python3 "$SKILL/scripts/check_html.py" --manifest "$MANIFEST" --note "$NOTE" --review "$REVIEW"
```

## 새 날짜의 감사 입력

아직 발행되지 않은 신규 날짜는 기존 CLI에서 overlay 키로 허용되지 않는다. `RUN/audit-repo`에 읽기 전용 입력을 가리키는 감사용 폴더를 만들고 이를 `AUDIT_REPO`로 쓴다. 감사용 `복습노트/` 아래 기존 날짜 폴더는 실제 날짜 폴더로 링크하고 신규 날짜는 현재 `STAGE`로 링크한다. `from_the_past`는 실제 폴더로 링크한다. 신규 날짜의 작업용 HTML과 stage의 최종 manifest가 함께 발견되어야 한다. `overlay.json`은 `{}`로 둔다. 공개 날짜 폴더는 메인 발행 절차에서 만든다.

## Stage와 전역 검사

발행된 날짜를 바꿀 때는 `AUDIT_REPO="$REPO"`로 지정하고 `overlay.json`에 이번에 바꾸는 날짜의 range→stage HTML 절대 경로를 둔다. 다른 날짜도 함께 검사한다.

```sh
python3 "$SKILL/scripts/review_audit.py" --repo "$AUDIT_REPO" --overlay "$RUN/overlay.json" --decisions "$RUN/decisions.json" --baseline "$RUN/baseline.json" --out "$RUN/audit.json"
```

한 줄 요약과 종료 코드를 본다. 실패 보고서가 저장됐으면 현재 `audit.json`의 `blocking`과 미판정 `candidates`에서 해결할 항목만 읽는다. 명령 오류로 보고서를 쓰지 못했으면 오류를 고쳐 다시 실행한다. 전체 보고서는 RUN에 보존하고, 조치와 재검사 뒤 최종 `blocking=[]`, 미판정 `candidates=[]`, `status=pass`와 종료 코드 0을 확인한다. 검사 범위를 확인할 때는 `inputs`의 날짜와 경로만 조회한다. 성공한 감사 증거는 기존과 같이 작업본의 `.pack/자료_복습팩/audit.json`으로 보존한다.

`decisions.json`은 처음에는 빈 목록이다. 서로 다른 은행 기출의 코드 구조·변수명·상수 차이는 `retained_similar_exams`에 보존 기록을 남기며 삭제·통합 후보로 다루지 않는다. 그 외 유사 문항은 검토 후보이며 자동 삭제하지 않는다. 후보 판정은 `left/right={range,id,content_sha256}`, `decision=duplicate|distinct`, `reason`, `evidence`를 기록한다. 내용이 바뀌면 과거 판정은 무효다. 동일 출처 재사용·동일 질문은 distinct 판정으로 우회하지 못한다. 기존 팩 변경은 반드시 `--baseline`을 전달한다. 복구 작업은 추가로 `--required-exams "$RUN/required-exams.json"`을 전달한다. baseline의 서로 다른 기출이 누락되면 실패하며, 동일 원문 재수록은 canonical source로 한 번 존재하면 된다. 최종 selection에는 전체 보존 기출 ID 배열 `required_exam_sources`를 기록한다. audit는 이 저장 목록도 자동으로 읽어 별도 옵션 없는 후속 검사에서도 누락을 검출한다.

## 발행·파생 산출물

selection은 `mode=revision`, `policy_version=review-questions-2026-10-17`, 최종 전 문항 `selected`, `excluded`, `coverage`, `replacements`, `duplicate_decisions`를 갖는다. 이전 모든 source/id/content hash와 새 대응을 기록한다. validation에는 before/after 해시, 실제 검사 결과, 보존 대상, unresolved를 적는다. 과거 기록을 덮어쓰거나 이전 pass에 현재 해시만 바꿔 붙이지 않는다.

정답은 문제만 보고 별도 추적·계산·정의된 C11 실행으로 검산한다. 실행 harness에 추가한 선언·헤더·main과 원문 차이를 기록하고 실제 스크립트·출력을 evidence로 보관한다. 검토하지 않은 문항은 pending이다.

메인 읽기 — [검사 요청과 결과](browser-check.md). 메인이 대체 검사할 때는 [서버](browser-check.md)부터 [패널 제목과 요약 계약](browser-check.md)까지 적용한다. 검사자에게는 브라우저 지침 경로를 넘긴다.

MD는 최종 복습문제 HTML만 변환해 정리노트 MD를 보존한다. 최종 manifest와 자원이 준비되면 브라우저 요청을 발급한다. 검사자는 모든 문항을 1280×900/375×812, light/dark에서 열고 원문·힌트·풀이·목차·pager·코드 내부 스크롤·링크·콘솔을 확인한다. 실패 시 `where`별로 고치고 기계 검사·감사·변환 후 요청을 갱신한다. 2회 수정 뒤 미해결이면 해당 팩 발행을 보류하고 기존 팩을 보존한다.

메인 읽기 — [생성과 기계 검사](pdf-build.md), [쪽별 실화면 검토](pdf-build.md), [발행](pdf-build.md). 검증한 작업용 HTML로 PDF를 만들어 작업 폴더에 발행한다.

메인이 `release_review.py publish --repo REPO --run PACK_RUN`으로 팩을 교체한다(백업·변경 감지·복구 포함). 메인 읽기 — 발행 직후 [병렬 시작](pack-followups.md), 판정을 받은 뒤 [발행](pack-followups.md). 발행한 JSON 원고의 정확한 경로로 `revise-existing`의 문제설명 분기를 실행한다.

팩마다 검증한 결과만 교체한다. 실패한 파생 산출물은 stale/withheld와 이유를 기록하고 이전 파일을 보존한다. 다른 독립 팩은 계속한다. 마지막 전체 audit와 `pack_layout.py check --repo REPO`를 실행하고 미완료 검사를 pass로 기록하지 않는다.
