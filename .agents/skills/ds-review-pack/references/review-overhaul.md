# 전체 문항 개편과 공통 품질 게이트

`revise-existing [MMDD|all] [lite]`는 기존 문항을 유지·이동·통합·교체하는 모드다. `update-existing`는 기존 카드를 보존하며 교과서 원문을 추가하는 별도 모드다. 사용자가 전체 재검토를 요청했을 때만 개편 모드를 쓴다. `bank`는 이 절차를 실행하지 않는다.

신규·update-existing·revise-existing 모두 최종 manifest→출처→팩 HTML→전체 audit→실화면→MD→문제설명/PDF 순서의 검증을 따른다. lite도 출처·중복·설명·PDF 검증은 생략하지 않는다.

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

`bank.py check-manifest BANK MANIFEST --repo REPO --textbook-dir TEXTBOOK`는 lecture-code의 현재 파일·페이지·해시·학습 날짜를 검사한다. 페이지 열람과 학습 근거의 의미 검토는 작성자가 별도로 수행한다.

## Stage와 전역 검사

먼저 고유 RUN에 변경 전 팩 전체와 보호 대상 해시를 백업한다. 정리노트 HTML/MD·기존 그림, STT, 강의록, 기출·교과서 원본은 보존한다. 변경 전에 `collect_reviews(REPO)` 결과 전체를 RUN/baseline.json으로 고정한다. 기존 기출의 고유 source 목록을 별도 대조하며 이번처럼 과거 누락을 복구할 때는 required-exams.json에 복구할 전체 기출 ID 배열을 둔다. stage는 팩별 HTML과 `.pack/자료_복습팩/manifest.json`을 갖는다. `update_review.build_revision`으로 허용 영역만 교체하고 `publish_update`로 백업·변경 감지·복구를 수행한다. 기존 교과서 추가는 계속 `build_update`를 쓴다.

문제 번호 변경은 내용 버전별 `od-review-solved:<range>:<revision>` 상태 키로 구분한다. 옛 p1의 완료 상태를 새 p1에 이식하지 않는다. 테마·패널·노트 읽음 키는 보존한다. PDF 작성용 표는 pN이 아니라 source ID로 지정한다.

```sh
python3 "$SKILL/scripts/review_audit.py" --repo "$REPO" --overlay "$RUN/overlay.json" --decisions "$RUN/decisions.json" --baseline "$RUN/baseline.json" --out "$RUN/audit.json"
```

overlay는 range→stage HTML 절대 경로 객체다. 바꾸지 않은 날짜도 실제 파일로 함께 검사한다. `decisions.json`은 처음에는 빈 목록이다. 서로 다른 은행 기출의 코드 구조·변수명·상수 차이는 `retained_similar_exams`에 보존 기록을 남기며 삭제·통합 후보로 다루지 않는다. 그 외 유사 문항은 검토 후보이며 자동 삭제하지 않는다. 후보 판정은 `left/right={range,id,content_sha256}`, `decision=duplicate|distinct`, `reason`, `evidence`를 기록한다. 내용이 바뀌면 과거 판정은 무효다. 동일 출처 재사용·동일 질문은 distinct 판정으로 우회하지 못한다. 기존 팩 변경은 반드시 `--baseline`을 전달한다. 복구 작업은 추가로 `--required-exams "$RUN/required-exams.json"`을 전달한다. baseline의 서로 다른 기출이 누락되면 실패하며, 동일 원문 재수록은 canonical source로 한 번 존재하면 된다. 최종 selection에는 전체 보존 기출 ID 배열 `required_exam_sources`를 기록한다. audit는 이 저장 목록도 자동으로 읽어 별도 옵션 없는 후속 검사에서도 누락을 검출한다. 최종 `blocking=[]`, 미판정 `candidates=[]`, `status=pass`가 필요하다.

## 발행·파생 산출물

selection은 `mode=revision`, `policy_version=review-questions-2026-10-17`, 최종 전 문항 `selected`, `excluded`, `coverage`, `replacements`, `duplicate_decisions`를 갖는다. 이전 모든 source/id/content hash와 새 대응을 기록한다. validation에는 before/after 해시, 실제 검사 결과, 보존 대상, unresolved를 적는다. 과거 기록을 덮어쓰거나 이전 pass에 현재 해시만 바꿔 붙이지 않는다.

정답은 문제만 보고 별도 추적·계산·정의된 C11 실행으로 검산한다. 실행 harness에 추가한 선언·헤더·main과 원문 차이를 기록하고 실제 스크립트·출력을 evidence로 보관한다. 검토하지 않은 문항은 pending이다.

모든 문항을 1280×900/375×812, light/dark에서 열고 원문·힌트·풀이·목차·pager·코드 내부 스크롤·링크·콘솔을 확인한다. MD는 최종 복습문제 HTML만 변환해 정리노트 MD를 보존한다. 정확한 최종 HTML 절대 경로로 [문제설명](problem-explain.md)과 [PDF](pdf-build.md)를 갱신한다. 설명 네 검토와 PDF 모든 페이지의 실제 검토를 마친 현재 입력만 발행한다.

팩마다 검증한 결과만 교체한다. 실패한 파생 산출물은 stale/withheld와 이유를 기록하고 이전 파일을 보존한다. 다른 독립 팩은 계속한다. 마지막 전체 audit와 `pack_layout.py check --repo REPO`를 실행하고 미완료 검사를 pass로 기록하지 않는다.
