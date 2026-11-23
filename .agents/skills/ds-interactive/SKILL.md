---
name: ds-interactive
description: Use when 자구알(자료구조및알고리즘이해)의 인터랙티브 학습 자료, 단계별 코드·메모리 시뮬레이션, C 포인터 디버깅형 HTML 또는 /ds-interactive를 요청할 때. 일반 코드 설명, 복습팩·문제해설·채팅 퀴즈 요청에는 사용하지 않는다.
---

# DS Interactive

자구알의 개념을 입력·사례·실행 단계로 탐색하는 **오프라인 HTML**을 만든다. 코드를 따라가며 매개변수의 값 복사, 포인터의 주소 값, 대상 객체의 변경을 같은 상태에서 보여 준다. 포인터 예제는 공통 좌우 패널과 중앙 메모리 장면을 쓴다. 이진 트리 재귀 순회는 넓은 화면에서 왼쪽에 코드·줄 기록·단계 설명, 가운데에 전체 트리·출력, 오른쪽에 호출 스택·예제 정보를 둔다. 재귀 트리는 출력 바로 아래의 [현재 변수 카드](references/design.md)에 현재 호출의 노드 매개변수를 기본으로 표시한다. 높이·개수처럼 더 추적할 변수는 `watch`에 추가한다. 넓은 화면에서는 패널을 각각 접고 경계를 끌어 너비를 조절할 수 있다. 조절한 너비는 브라우저에 저장하며 왼쪽 패널을 열면 줄 기록이 바로 표시된다. 좁은 화면에서는 트리와 출력을 먼저 보여 주고, 필요한 패널을 상단 버튼으로 열면 화면 가장자리의 서랍에 표시한다. 호출 스택의 행이나 트리 노드를 누르면 해당 단계의 저장 값과 주소를 확인할 수 있다.

그래프 자료는 [1102와 같은 학습 화면](references/design.md)을 사용한다. 상단은 제목과 사례·모드, 왼쪽은 실행 코드·줄 기록 3행·현재 단계 설명, 오른쪽은 실행 상태 상세·접힌 예제 정보다. 중앙은 그래프와 인접 행렬(해당하는 경우) → 결과 → 현재 값 카드 순서다. 왼쪽을 닫으면 설명을 카드 아래에 배치한다. 1280px 미만에서는 두 서랍을 닫고 시작하며 375×812 모바일 첫 화면에 결과와 현재 값 카드가 모두 들어와야 한다.

## 요청 해석

`/ds-interactive 0928`, 날짜 범위, 주제, C 파일 경로, 붙여 넣은 함수 코드를 받는다. 기존 자료 연결만 요청하면 생성하지 말고 `relink`를 쓴다. 먼저 저장된 자료와 근거를 확인해 같은 자료를 중복 생성하지 않는다.

- 날짜: 실제 노트·`.pack` MD·STT·강의 PDF를 읽고 유용한 주제 2–4개를 고른다. 개수를 채우기 위해 만들지 않는다.
- 주제/코드: 핵심 질문 하나와 필요한 호출자·입력 조건을 정한다. 붙여 넣은 코드는 고유 RUN의 `source.c`에 원문으로 보존한다. 함수만 있으면 호출자는 보충이라고 표시한다.
- 실제 소스가 의사코드이면 그렇게 표시한다. 원본의 오류·수명 문제를 임의 수정해 정상 코드로 제시하지 않는다.
- `ds-review-pack`은 복습팩, `ds-problem-explain`은 기존 문제 해설, `ds-review-coach`는 채팅 퀴즈다. 다른 스킬을 수정하거나 전체 팩을 재생성하지 않는다.

## 제작

아래 S는 **이 SKILL.md의 폴더 절대 경로**, REPO는 현재 자구알 저장소다. 다른 과목 경로에 실행 의존성이 없다. 모든 명령에서 공백 포함 경로를 인용한다. 런타임은 Node.js 20 이상, 추가 패키지 설치 없이 실행한다.

1. `node "S/scripts/resolve.cjs" "REPO" 0928`로 실제 경로를 찾는다. `.pack` MD를 우선한다. `AMBIGUOUS_TARGET`이면 후보를 보고하고 임의 선택하지 않는다. 명시 C 파일 누락은 `SOURCE_MISSING`이다. 대응 노트 없는 주제·코드는 `복습노트/주제별`을 사용한다. 주제와 강의 대응은 [topic-selection](references/topic-selection.md)을 읽는다.
2. 새 고유 RUN을 만들고 `brief.md`, `source.json`에 질문·입력·출처·페이지·해시·보충·단순화를 적는다. 원본 C는 그대로 보존하고 검산용 헤더·main 보정을 구분한다. PDF가 근거이면 실제 해당 페이지도 읽는다.
3. [scenario-api](references/scenario-api.md)와 [c-semantics](references/c-semantics.md)를 읽고 `scenario.cjs`를 저작한다. 포인터 자료는 [값과 주소 전달](examples/0928/value-address.cjs)의 `c-memory`를 쓴다. 이진 트리 재귀 순회는 [1105 중위 순회](examples/1105/inorder.cjs)의 `c-tree`를 쓴다. 트리 자료에는 정상 트리와 빈 트리를 넣고, 왼쪽 NULL과 오른쪽 NULL이 각각 어느 줄로 복귀하는지 확인한다. 초기 상태·이벤트로 Trace를 만들며, 화면과 설명이 별도 수동 상태를 갖지 않게 한다. 브라우저에 임의 코드 편집·컴파일·실행기를 만들지 않는다.
4. `node "S/scripts/check.cjs" "RUN/scenario.cjs"`, `node "S/scripts/steps.cjs" "RUN/scenario.cjs"`로 기본값과 모든 preset을 확인하고 후자 JSON을 `trace.json`으로 저장한다. 정수 경계·같은 값·별칭·NULL·수명 종료 중 해당 사례를 포함한다. 예상 최종값만으로 중간값 검산을 대신하지 않는다.
5. 실제 C 컴파일러로 정의된 코드의 bind/write와 결과를 독립 검산한다. 없으면 별도 Python 표를 사용하고 `compiler_unavailable`을 기록한다. UB를 실행해 정답을 정하지 않는다. 포인터 예제는 `python3 "S/tests/independent.py" "EVIDENCE"`, 중위 순회는 `python3 "S/tests/inorder_oracle.py" "RUN/trace.json"`으로 재검산할 수 있다.
6. `node "S/scripts/build.cjs" "RUN/scenario.cjs" "RUN/preview.html"`. CSS와 JS를 HTML에 포함하고, Pretendard는 복습노트 공용 자원을 상대 경로로 참조한다. [design](references/design.md)의 배치·접근성 기준과 [verification](references/verification.md)의 브라우저 검사를 적용한다. 시나리오 내용 변경 후 다시 build/check/검산한다.
7. `node "S/scripts/review.cjs" init "RUN"`은 `not_run` 검토를 만든다. 이미 있으면 검토 파일을 보존하고 새 현재 해시로 재검토한다. schema/content/independent/browser 각각 실제 증거와 사람이 읽을 판정 이유를 남긴다. `createReview`는 합격을 판정하지 않는다. 내용 검토는 각 줄의 복사·읽기·쓰기가 C 의미와 맞는지 검토한다. 자동 구조 검사로 대체하지 않는다.
8. 모든 검토를 마치면 `node "S/scripts/verify-build.cjs" "RUN"`을 통과시키고 `node "S/scripts/save.cjs" "RUN" "대상폴더" "자료이름"`으로 저장한다. 재귀 트리는 브라우저 검사 결과인 `browser.json`을 RUN의 evidence에 저장하고 browser 판정에 연결한다. 그래프도 `browser.json`을 browser 판정에 지정하며, 같은 빌드에서 그래프 해상도 4종·테마 2종의 패널·장면 배치, 모바일 초기·중간·종료 단계에서의 결과와 현재 값 카드 노출, 모든 사례의 실행 단계를 확인해야 한다. 저장은 검토 해시와 재빌드 결과를 확인한다. [검토·저장 계약](references/verification.md)을 따른다.
9. 관련 절에 [note-links](references/note-links.md)의 관찰 문맥 링크만 dry-run 후 추가한다. `target="_self"`, URL 인코딩한 상대 경로이며 기존 노트는 백업한다. 노트 재생성 후 `node "S/scripts/relink.cjs" "REPO" 0928`로 복원한다. 누락·모호한 절은 해당 연결만 skipped로 보고한다.

## 저장과 확인

공개 파일은 `복습노트/<날짜>/인터렉티브_NN_<이름>.html`, 근거는 `.pack/자료_인터렉티브_NN_<이름>/`이다. 번호는 최소 두 자리이며 100도 허용한다. 신규 생성은 기존 HTML 또는 자료 폴더를 덮어쓰지 않는다. 사용자가 기존 자료 수정을 명시하면 [verification](references/verification.md)의 백업·재검증·동일 경로 갱신 절차를 따른다. 자료 폴더에는 scenario/brief/source/trace/review, evidence, 상대 `note-links.json`을 보존한다. 저장소 안에서는 인터넷 없이 열 수 있다. 다른 PC에 HTML 하나만 옮기려면 `export-standalone-note`에 공개 HTML 경로를 지정한다.

저장 후 `node "S/scripts/verify-build.cjs" "보관 자료 폴더" "공개 HTML"`로 재빌드 결과와 공개 HTML의 일치를 확인한다. 최종 경로에서 입력·모드·단계와 노트의 현재 탭 이동·뒤로가기를 확인한다. 1105는 [최종 경로 자동 검사](references/verification.md)로 정리노트 링크 왕복을 확인할 수 있다. 재연결 결과는 unchanged여야 한다. 모든 최종 경로와 검산 방식·확인하지 못한 범위를 보고한다. 커밋·푸시·외부 게시를 자동 수행하지 않는다.

## 주의할 판단

- C 포인터 인자도 **주소 값의 복사**다. 매개변수 Cell과 대상 객체를 합치지 않는다. 수업의 call by reference 표현에는 이 차이를 덧붙인다.
- `p`, `&p`, `*p`, `p=NULL`, `*p=값`을 따로 표시한다. 실제 물리 주소·ABI 크기를 주장하지 않는다.
- 역참조 오류는 해당 단계에서 중단한다. `free(NULL)`은 무동작이고, 해제·반환 뒤 별칭은 사용 불가다.
- 재귀 호출마다 새 매개변수 Cell을 만들고, 호출이 끝나면 그 Cell의 수명을 끝낸다. 출력 순번은 실제 출력한 키의 Cell ID를 따르므로 같은 키를 가진 노드도 구별한다. 새 자료구조는 Trace 계약과 렌더러 경계를 먼저 설계한다.
