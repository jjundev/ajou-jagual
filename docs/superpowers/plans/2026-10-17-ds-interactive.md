# ds-interactive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 자구알 전반으로 확장 가능한 ds-interactive 스킬과 0928 포인터 기초 자료 세 개를 구현하고 검산·브라우저·노트 연결까지 검증한다.

**Architecture:** 공통 Trace 플레이어, C 메모리 이벤트 엔진, 주제별 Scenario를 분리한다. bio-interactive의 디자인·검토·저장·문맥 링크 방식을 계승하되 DOM·SVG 메모리 렌더러를 사용하고 모든 표시를 같은 Snapshot에서 만든다. 날짜 선택·빌드·저장·연결 CLI는 새 스킬 안에서 독립 실행된다.

**Tech Stack:** Node.js 20 이상, CommonJS, node:test, HTML/CSS/DOM/SVG. Python 3·Playwright는 브라우저 검증 전용. 실행용 패키지 설치 없음.

**Spec:** `docs/superpowers/specs/2026-10-17-ds-interactive-design.md` — 채팅 설계를 저장했으며 결정 #8 자구알 전반 확장, #9 0928 시작은 사용자 확정이다.

## Global Constraints

- Node.js 20 이상, CommonJS 저작·CLI, 브라우저용 번들에는 네이티브 DOM·SVG를 사용한다.
- 설치가 필요한 실행 라이브러리는 추가하지 않는다. Python 3와 Playwright는 검증 전용이다.
- 기본 한도는 2,000단계, 호출 깊이 64, 객체 256개다.
- 입력 정수는 첫 자료에서 -99부터 99까지로 제한한다.
- HTML에는 CSS·JS·폰트를 포함한다. 런타임 외부 요청은 0이다.
- 공개 파일은 `복습노트/<날짜>/인터렉티브_NN_<이름>.html`, 저작·근거는 같은 폴더 `.pack/자료_인터렉티브_NN_<이름>/`이다. NN은 최소 두 자리다.
- 기존 번호와 자료 폴더는 덮어쓰지 않는다.
- 노트 연결은 관련 절 뒤 관찰 문장과 상대 경로 target=_self 링크만 추가한다. 본문·위젯·스타일·스크립트·MD·PDF는 보존한다.
- review.json은 schema/content/independent/browser의 실제 결과와 현재 소스·Trace·페이지 해시를 가진다. 미검토·실패·disputed·해시 변경은 save를 막는다.
- 브라우저는 1440×900, 1024×768, 375×812에서 light/dark로 실제 확인한다.
- 자동 커밋·푸시·외부 게시는 하지 않는다. 모델·서브에이전트 사용을 강제하지 않는다.
- 기존 관리 워크트리에서 진행한다. detached HEAD를 이유로 새 checkout을 만들지 않는다. 커밋 단계 대신 diff 체크포인트를 남긴다.

## Review Focus

1. 동일 객체를 두 인자로 전달: 매개변수 Cell은 분리되지만 두 주소는 같은 대상이어야 한다. Task 2·4가 고정한다.
2. free 또는 함수 반환 뒤 다른 별칭이 남음: 관련 포인터는 유효한 대상으로 접근할 수 없고 진단 이후 실행은 중단된다. Task 2가 고정한다.
3. 한글·공백·NFD 경로와 겹치는 날짜 팩: 실제 경로를 보존하고 애매한 후보는 임의 선택하지 않는다. Task 1·5가 고정한다.
4. 사례·입력 변경 중 재생 및 임의 단계 이동: 이전 타이머와 선택 상태를 정리하고 재생·코드·메모리를 일치시킨다. Task 3·6이 고정한다.
5. 검토 뒤 소스 변경·저장 충돌·노트 절 변경: 저장을 막거나 연결만 skipped하고 기존 파일은 보존한다. Task 5가 고정한다.

---

## 파일 구조와 책임

이하 S는 `.agents/skills/ds-interactive`다. 아래 경로는 모두 저장소 루트 기준이며 스킬 실행 시 다른 저장소를 찾지 않는다.

| 파일 | 책임 |
|---|---|
| S/SKILL.md, S/agents/openai.yaml | 사용·제작 절차와 발견 메타데이터 |
| S/references/{scenario-api,c-semantics,design,verification,topic-selection,note-links}.md | 저작 계약·근거·검토 규칙 |
| S/assets/{shell.html,player.css,player.js,memory-svg.js} | 화면, 공통 제어, c-memory 렌더러 |
| S/assets/engine/{contract,memory,trace}.js | 공유 타입 검사, C 상태 전이, Trace 생성 |
| S/assets/vendor/pretendard/, S/assets/vendor/provenance.json | 로컬 폰트·라이선스·해시 |
| S/examples/0928/{value-address,pointer-target,double-pointer}.cjs | 실제 제작에도 사용하는 검증된 시나리오 |
| S/scripts/resolve.cjs | 날짜·주제·C 파일 대상 탐색 |
| S/scripts/{check,steps,build}.cjs | 구조·상태 검사, Trace 추출, 단일 HTML 빌드 |
| S/scripts/{review,save,link-notes,relink}.cjs | 검토 해시 검증, 번호 예약 저장, 문맥 링크와 복원 |
| S/tests/{resolve,engine,trace,build,examples,delivery,skill}.test.cjs | 의미·CLI·발행·스킬 검증 |
| S/tests/browser_acceptance.py | 실제 브라우저 상호작용·휴대성 검증 |
| S/tests/fixtures/ | 작은 synthetic 팩·시나리오·명세 |
| .claude/skills/ds-interactive | 기존 프로젝트 관례에 따른 상대 심볼릭 링크 |
| 복습노트/0928/인터렉티브_NN_*.html, .pack/자료_인터렉티브_NN_*/ | 최종 세 자료와 저작·검토·독립 검산 근거 |
| 복습노트/0928/정리노트_0928_ArrayStructureList.html | 문맥 링크만 추가 |
| docs/verify/2026-10-17-ds-interactive.md | 최종 검증 기록 |

원본 bio-interactive는 읽기 전용 참고다. 필요한 디자인 수치와 링크 파서만 이식하며 이식 파일·원본 해시를 provenance에 기록한다. .dc 런타임·캔버스 메타데이터·생명과학 문구는 복사하지 않는다.

## 공통 타입과 API

Spec의 Value/Cell/Object/Frame/MemoryState/Event/Location/Snapshot/Trace/Scenario 및 「저작 데이터의 구체적인 형식」의 Source/Input/Preset/expected·이벤트 payload를 그대로 사용하고 JSDoc으로 정의한다. 후속 Task는 여기와 Spec의 이름을 바꾸지 않는다.

- `resolveTarget({repo,arg,source?}) -> Target`: Target={kind,folder,date,notes,noteHtml,stt,source,existing,next}. kind=date/topic/code. notes는 실제 절대 경로 목록이다.
- `initialMemory() -> MemoryState`, `applyEvent(state,event,limits) -> {state,reads,writes,diagnostic}`: 입력을 변경하지 않는다.
- `compileScenario(scenario,input,limits?) -> Trace`, `validateTrace(trace) -> Issue[]`: Issue={code,path,message}.
- `buildPage({scenario,inputs?,title?}) -> {html,traces,hashes}`: inputs 생략 시 기본값·모든 preset을 포함한다. 브라우저 값 변경은 같은 compileScenario를 실행한다.
- `checkScenario(scenario) -> {ok,issues,traces}`: 기본·모든 preset을 검사한다.
- `readReview(dir) -> Review`, `verifyReview(dir) -> Issue[]`: Review={version:1,hashes,checks:{schema,content,independent,browser}}. 각 check={status,evidence,notes}; status=not_run/pass/fail/disputed. evidence는 자료 폴더 내부 상대 경로다.
- `save({run,dest,name}) -> {nn,html,dir}`: 검토·소스 해시 검사 후 exclusive 파일 예약을 사용한다.
- `linkNotes({note,links,dryRun,backupDir}) -> {note,changed,results}`: 링크는 {sectionId,html,label,before,after,anchorId?}, result.status=added/updated/unchanged/skipped.
- `relink({repo,target,dryRun,backupDir}) -> LinkReport`: 저장된 상대 note-links.json을 해석해 linkNotes를 호출한다.

## Task 1: 독립 스킬의 대상 선택과 계약

**Files:** Create S/scripts/resolve.cjs, S/assets/engine/contract.js, S/references/scenario-api.md, S/tests/resolve.test.cjs, S/tests/fixtures/mini-repo/.

**Interfaces:** Consumes Spec의 Target·Trace 계약. Produces resolveTarget, Value/Trace/Scenario JSDoc과 입력 검사 함수 `validateInput(definitions,input) -> Issue[]`.

- [x] **Step 1: 실패 테스트 작성.** 실제 0928, .pack 우선, 주제별 fallback, 직접 C 경로, 없는 파일, 범위 중복, NFC/NFD와 공백 경로를 임시 팩으로 고정한다. `assert.equal(resolveTarget({repo,arg:'0928'}).date,'0928')`, 중복은 `assert.throws(...,{code:'AMBIGUOUS_TARGET'})`, 없는 명시 C는 SOURCE_MISSING. 정수 -99·99 통과, -100·100·NaN·빈 값은 입력 오류다.
- [x] **Step 2: 실패 확인.** `node --test .agents/skills/ds-interactive/tests/resolve.test.cjs` → 모듈 없음 또는 구현 전 assertion 실패.
- [x] **Step 3: 구현.** resolveTarget과 validateInput을 위 파일에 만든다. 검색 결과 경로를 유지하고 .pack/루트의 같은 이름 MD는 .pack 하나를 선택한다. 명시 파일을 주제 문자열로 오인하지 않는다. repo 밖 C도 읽되 출력은 repo 안에 둔다. CLI `node resolve.cjs REPO ARG`는 Target JSON, 오류는 코드와 종료 1을 출력한다.
- [x] **Step 4: 통과 확인.** 같은 테스트 명령이 exit 0. 실제 `node .agents/skills/ds-interactive/scripts/resolve.cjs . 0928`의 noteHtml과 source를 읽어 맞는지 확인한다.
- [x] **Step 5: 체크포인트.** diff에서 생성 경로·이름·공통 타입을 확인하고 이 Task 체크박스만 갱신한다. 커밋하지 않는다.

## Task 2: C 메모리 전이와 불변 실행 기록

**Files:** Create S/assets/engine/memory.js, S/assets/engine/trace.js, S/tests/engine.test.cjs, S/tests/trace.test.cjs, S/references/c-semantics.md, S/scripts/check.cjs, S/scripts/steps.cjs.

**Interfaces:** Consumes contract.js의 타입·validateInput. Produces initialMemory, applyEvent, compileScenario, validateTrace, checkScenario. 브라우저와 Node에서 같은 순수 코드를 사용하도록 CommonJS export와 전역 이름공간 DSInteractive를 함께 제공한다.

- [x] **Step 1: 실패 테스트 작성.** 값 매개변수 변경 후 caller.a=10 유지, 포인터 write 뒤 caller.a=20, 지역 p=NULL 뒤 caller.q.target='main.a' 유지, 이중 포인터 뒤 caller.q.target='main.b', 같은 객체를 인자로 두 번 넘겨도 callee Cell ID는 서로 다름을 assert한다. 구조체 포인터 필드 복사, 배열 매개변수 조정, 링크 필드 변경도 검사한다.
- [x] **Step 2: 수명·복원 실패 테스트 추가.** free(NULL)은 무동작, free 뒤 모든 별칭은 indeterminate, 반환 뒤 자동 객체 참조는 접근 불가, 반복 호출 프레임 ID는 고유, NULL·초기화 전 읽기·범위 밖·잘못된 free는 diagnostic 뒤 정상 Snapshot 0개임을 assert한다. `assert.deepEqual(trace.snapshots[k], rebuilt.snapshots[k])`, 원본 initialState 불변, 모든 at.line이 유효함을 검사한다. 한도 2000·64·256의 경계·초과를 검사한다.
- [x] **Step 3: 실패 확인.** `node --test .agents/skills/ds-interactive/tests/engine.test.cjs .agents/skills/ds-interactive/tests/trace.test.cjs` → 구현 전 실패.
- [x] **Step 4: 구현.** Spec 이벤트를 명시적 Cell ID로 적용한다. call/bind/enter는 별도 단계이고 bind는 평가된 값을 복사한다. 진단 시 그 Snapshot으로 종료한다. 유효했던 대상의 수명 종료는 별칭을 indeterminate로 바꾸며 참조용 과거 관계는 metadata에만 남긴다. 배열 경계·저장 공간 정보를 갖는 진단을 사용한다. steps.cjs SCENARIO는 기본·preset의 Snapshot JSON, check.cjs SCENARIO는 검사를 출력한다. Source C를 자동 파싱·실행하지 않는다.
- [x] **Step 5: 통과 확인.** 같은 테스트가 exit 0이며 check가 ok다. 서로 다른 입력에서 중간값이 변하고 이전 Trace가 변경되지 않음을 확인한다.
- [x] **Step 6: 체크포인트.** C 문서와 전이 코드의 정의·수명 규칙을 대조하고 diff를 확인한다.

## Task 3: 오프라인 플레이어와 2D 메모리 화면

**Files:** Create S/assets/shell.html, S/assets/player.css, S/assets/player.js, S/assets/memory-svg.js, S/scripts/build.cjs, S/assets/vendor/pretendard/, S/assets/vendor/provenance.json, S/references/design.md, S/tests/build.test.cjs.

**Interfaces:** Consumes compileScenario와 Trace/Snapshot. Produces buildPage, `mountPlayer(root,scenario) -> {destroy()}`, registerRenderer, `memoryRenderer.render(snapshot,selection)`. root 내 `[data-action]`, `[data-cell-id]`, `[data-line]`, `[data-step]`, `[data-view]`를 공개 검증 선택자로 사용한다.

- [x] **Step 1: 실패 테스트 작성.** 빌드 HTML에 외부 script/link/font/import/fetch가 없고 Node와 브라우저에 동일 엔진이 들어가는지 검사한다. 코드에 `</script>`, `<img>`, `&`가 있어도 텍스트로 보존하고 실행되지 않게 직렬화한다. Trace 계약 위반과 미등록 renderer는 분명한 오류로 처리한다.
- [x] **Step 2: 실패 확인.** `node --test .agents/skills/ds-interactive/tests/build.test.cjs` → build.cjs 없음으로 실패.
- [x] **Step 3: 빌더 구현.** buildPage는 셸·CSS·엔진·렌더러·시나리오·동봉 폰트를 인라인한다. 폰트는 현재 저장소 동봉 Pretendard에서 필요한 woff2·LICENSE를 복사해 provenance를 고정한다. 원본·코드·안내는 textContent 또는 동등한 escape를 사용한다. 시나리오 함수는 신뢰된 저작 코드이며 임의 C 입력 실행 기능을 만들지 않는다. buildPage의 scenario는 `{definition:Scenario,sourceText:string}`이며 definition.id와 저작 소스의 등록 ID가 같음을 확인한다. 인라인 JS의 closing-script 문자를 안전하게 처리하며 외부 require/import를 거부한다. CLI `node build.cjs SCENARIO PREVIEW.html`를 제공한다.
- [x] **Step 4: 플레이어 구현.** mountPlayer는 기본 입력으로 Trace를 만들고 선택 단계에 대해 코드·메모리·설명을 함께 갱신한다. 타이머는 하나만 유지하고 입력·preset 변경 시 정지·0단계·선택 해제를 적용한다. destroy는 타이머·이벤트를 제거한다. 속도는 0.5/1/2, 마지막 단계는 자동 정지한다. 이전·다음은 경계를 넘지 않는다.
- [x] **Step 5: 메모리·접근성 구현.** frame/object/cell ID로 HTML·SVG를 배치하고 null·미초기화·수명 종료의 텍스트 표지를 제공한다. 변경된 Cell을 before/after와 함께 표시한다. 1024px 미만은 코드·메모리 전환, 44px 버튼, 키보드·aria 상태·동작 줄이기를 구현한다. 문서 가로 스크롤은 만들지 않는다.
- [x] **Step 6: 통과 확인.** build.test.cjs exit 0, synthetic 자료를 파일로 열어 단계·선택·테마를 확인한다. 본격 UI 수용 검사는 Task 6에서 모든 자료에 수행한다.
- [x] **Step 7: 체크포인트.** 외부 의존성과 폰트 라이선스·원본 해시, 공통 셸과 c-memory 렌더러의 경계를 diff로 확인한다.

## Task 4: 0928 세 시나리오와 독립 검산

**Files:** Create S/examples/0928/value-address.cjs, pointer-target.cjs, double-pointer.cjs, S/tests/fixtures/c-evidence/, S/tests/examples.test.cjs, S/references/topic-selection.md. 작업 근거는 고유 RUN/0928/<topic>/evidence/에 저장한다.

**Interfaces:** Consumes Scenario·Event·checkScenario. Produces 계약을 만족하는 세 시나리오, 기본 입력·모든 preset, expected와 독립 중간 상태 증거. examples.test는 각 파일을 require해 compileScenario를 사용한다.

- [x] **Step 1: 근거 확정.** 0928 HTML·.pack MD·STT, Software_3_ArrayStructureList.pdf p20·22·25와 연결 문맥을 실제 대조한다. 원본/보충/컴파일 보정 구분을 source.json·brief.md에 기록한다. PDF 확인에는 pdf 스킬을 사용한다.
- [x] **Step 2: 실패 테스트 작성.** value-address 기본 a=1,b=2: 값 복사 모드 caller=(1,2), 주소 swap 모드 caller=(2,1); 별칭 preset swap(&a,&a)는 a=1 유지. pointer-target 기본 a=10: 역참조 뒤 a=20, p=NULL 뒤 q는 a를 가리킴. double-pointer 기본 a=10,b=20,q=&a: 단일 포인터 모드는 q=&a, 이중 포인터 모드는 q=&b, a/b 값은 유지. 각 입력 -99·99와 동일값, NULL 진단 preset을 포함한다.
- [x] **Step 3: 실패 확인.** `node --test .agents/skills/ds-interactive/tests/examples.test.cjs` → 예제 모듈 없음 또는 기대 상태 실패.
- [x] **Step 4: 저작.** 세 Scenario를 위 파일에 구현한다. 입력은 -99..99 정수, 그림·문구는 Snapshot에서 나온다. UI 모드는 별도 preset의 mode 필드로 선택하고 sourceId/Location은 해당 코드에 연결한다. 원본 swap은 보존하고 호출자·추가 예제는 보충이라고 표시한다. 함수 호출 인자에 부수 효과를 넣지 않는다.
- [x] **Step 5: 독립 검산.** 현재 설치된 C 컴파일러를 확인하고 정의된 검산용 C를 컴파일·실행해 정규화된 JSON 중간값·최종값을 대조한다. gcc/clang/cl 중 실제 있는 실행기를 사용한다. 없으면 별도 Python 표 계산으로 중간값을 검산하고 compiler_unavailable을 기록한다. 주소 문자열은 비교하지 않는다. UB 사례는 실행 결과를 정답 근거로 사용하지 않는다. 구조 검사와 독립 검산 증거를 구분한다.
- [x] **Step 6: 통과 확인.** examples.test.cjs exit 0, 세 파일 각각 check.cjs가 ok, steps 출력과 independent 증거의 모든 쓰기·bind가 일치한다.
- [x] **Step 7: 체크포인트.** 원본 HTML·MD·STT 해시 불변과 보충 표시, 호출 시 복사와 대상 변경의 구별을 확인한다.

## Task 5: 검토를 통과한 자료 저장과 문맥 링크

**Files:** Create S/scripts/review.cjs, save.cjs, link-notes.cjs, relink.cjs, S/tests/delivery.test.cjs, S/references/verification.md, S/references/note-links.md.

**Interfaces:** Consumes Target·buildPage·Trace·Review. Produces readReview, verifyReview, save, linkNotes, relink. RUN/주제는 scenario.cjs, brief.md, source.json, trace.json, preview.html, review.json, evidence/, note-links.json을 가진다.

- [x] **Step 1: 실패 테스트 작성.** not_run/fail/disputed/근거 누락/검토 뒤 시나리오·trace·preview 변경은 save 실패 및 기존 파일 해시 불변. 같은 NN의 공개 HTML 또는 .pack 디렉터리만 존재하는 경우 다음 번호 사용. exclusive 예약 충돌은 재시도하고 복사 실패 시 자신이 만든 파일만 복구. 99 다음 번호는 100. 이름에 경로 구분자·Windows 예약 이름은 거부한다.
- [x] **Step 2: 링크 실패 테스트 작성.** 한글 공백 경로를 URL encode한 상대 _self 링크, dry-run 불변, 실제 추가 후 재실행 changed=false, 기존 target만 보정하고 rel·문구 보존, 모호·누락 절 skipped, 백업 바이트 동일. 상대 명세를 팩 이동 후 relink해 링크를 복원한다. 중복 id와 script/comment 속 가짜 id는 실제 절로 오인하지 않는다.
- [x] **Step 3: 실패 확인.** `node --test .agents/skills/ds-interactive/tests/delivery.test.cjs` → 구현 전 실패.
- [x] **Step 4: 검토·저장 구현.** review.cjs는 review 초기화·현재 해시·근거 존재 검사만 하며 content/independent/browser를 자동 pass 처리하지 않는다. save는 모든 check pass와 현재 해시 일치 후 번호를 exclusive 예약하고 검토한 preview.html 바이트와 자료 디렉터리를 함께 복사한다. 공개 HTML을 다시 빌드하거나 경로 주석을 바꾸지 않는다. 실패 시 생성 소유 경로만 복구하고 기존 자료를 삭제하지 않는다. review의 아티팩트 해시는 최종 복사 후 재확인한다.
- [x] **Step 5: 문맥 링크 구현.** bio-interactive의 offset 기반 파서를 검토·이식하고 data-ds-interactive를 사용한다. 매니페스트 상대 경로를 실제 절대 경로로 해석해 linkNotes에 넘긴다. 수정 전 백업하고 연결 외 바이트를 보존한다. CLI는 `node link-notes.cjs MANIFEST [--dry-run]`, `node relink.cjs REPO TARGET [--dry-run]`. 명세가 없으면 내용을 읽어 저작하는 절차를 문서화하며 임의 절에 붙이지 않는다.
- [x] **Step 6: 통과 확인.** delivery.test.cjs exit 0. synthetic 팩에서 save→link→relink가 동작하고 두 번째 연결은 unchanged다. source HTML/MD·다른 스킬의 비허용 변경은 없다.
- [x] **Step 7: 체크포인트.** 최종 저장된 review의 해시 의미, 백업·복구·번호 예약의 소유권 범위를 diff로 검토한다.

## Task 6: 스킬 등록과 실제 세 자료의 최종 수용 검증

**Files:** Create S/SKILL.md, S/agents/openai.yaml, S/tests/skill.test.cjs, S/tests/browser_acceptance.py, .claude/skills/ds-interactive, docs/verify/2026-10-17-ds-interactive.md. Publish 세 자료와 .pack 근거. Modify 복습노트/0928/정리노트_0928_ArrayStructureList.html의 관련 절 링크만.

**Interfaces:** Consumes Tasks 1–5의 모든 CLI·계약. Produces 사용 가능한 스킬, 검토를 통과한 standalone 세 파일, 관련 절 링크, 재현 가능한 검증 기록.

- [x] **Step 1: 실패 수용 테스트 작성.** skill.test는 frontmatter 이름·description·상대 참조 파일·CLI 존재와 다른 과목 절대 경로 실행 의존성 부재를 검사한다. browser_acceptance.py는 REPO와 빈 SCRATCH를 인자로 받고 네트워크 차단 file://에서 세 자료의 모든 preset·단계를 순회한다. 선택자로 코드/메모리 단계 일치, 이전·다음·처음·마지막, 입력 -99/99/빈 값, 재생 중 입력 변경, 속도, 테마, 셀 선택, 키보드, 모바일 보기, reduced-motion, 타이머 정지를 assert한다.
- [x] **Step 2: 실패 확인.** `node --test .agents/skills/ds-interactive/tests/skill.test.cjs`와 `python .agents/skills/ds-interactive/tests/browser_acceptance.py . <빈-SCRATCH>`가 미등록 스킬·없는 페이지 또는 미구현 동작으로 실패함을 확인한다.
- [x] **Step 3: 스킬 문서·등록.** skill-creator와 writing-skills를 읽고 SKILL.md에 입력 탐색, 주제 선택, 저작, 중간 상태 검산, 브라우저, 검토·저장, 연결·복원, 오류 보고를 작성한다. 기존 ds-review-pack/ds-review-coach/ds-problem-explain과 호출 경계를 명확히 한다. 인터랙티브 자료 요청을 받아야만 실행하고 일반 코드 설명을 가로채지 않는다. metadata와 기존 관례의 상대 링크를 만든다. 링크 생성 불가 시 일반 복사본으로 중복 관리하지 말고 원인과 발견 가능한 .agents 원본을 보고한다.
- [x] **Step 4: 전체 테스트·미리보기.** `node --test .agents/skills/ds-interactive/tests/*.test.cjs`를 실행한다. 셸 wildcard가 확장되지 않으면 Node가 지원하는 디렉터리 테스트 실행이나 파일 목록 배열을 사용한다. 세 시나리오를 고유 RUN에 복사하고 build/check/steps를 실행하여 review를 not_run으로 시작한다. skill-creator의 실제 quick_validate 경로를 확인해 스킬 검사한다.
- [x] **Step 5: 브라우저·시각 검토.** 1440×900·1024×768·375×812와 light/dark의 6조합에서 모든 자료를 확인한다. 캡처를 눈으로 읽어 글자·화살표 충돌을 고치고 코드 블록 내부만 스크롤을 허용한다. console/pageerror/외부 요청/문서 가로 넘침=0을 기록한다. file://가 거절되면 로컬 HTTP로 대체하고 미확인 범위를 명시한다. 변경 시 관련 검토를 not_run으로 되돌리고 다시 확인한다.
- [x] **Step 6: 실제 저장·연결.** 실제 source/content/independent/browser 결과와 증거·현재 해시를 review.json에 기록한 뒤 save.cjs로 0928 자료 세 개를 저장한다. s1-swap/s1-call-by-value, s0-pointer-ops, s2-double-pointer에 관찰 문맥 링크를 dry-run 후 적용한다. 전체 노트를 덮어쓰지 않는다. 첫 자료의 두 절 연결은 동일 HTML 목적지라도 각 절별로 수행한다.
- [x] **Step 7: 최종 경로 확인.** 공개 HTML에서 세 자료의 단계와 폰트를 다시 확인한다. 관련 노트 링크를 클릭해 현재 탭 이동·뒤로가기를 확인하고 재연결 결과 changed=false를 기록한다. synthetic 노트 재생성 후 relink 복원도 확인한다. 빌드와 최종 파일 해시가 같고 비대상 노트·MD·PDF 해시 불변임을 검증한다.
- [x] **Step 8: 완료 검증·보고.** verification-before-completion과 requesting-code-review 절차를 적용한다. 선택한 실행 방식에 맞춰 검토하고 허용된 범위 밖 위임은 하지 않는다. 리뷰로 변경된 파일의 관련 검사만 재실행한다. docs/verify에 명령·관측 결과·증거 경로·확인하지 못한 항목을 적고 파일·모드·입력·링크·검산 결과를 보고한다. 커밋·푸시하지 않는다.

## 자체 검토

- 설계 대응: 대상·경로(Task 1), 값·별칭·수명·한도(Task 2), 표시·오프라인·접근성(Task 3), 첫 세 자료·보충·독립 검산(Task 4), 검토·번호·문맥 링크·복원(Task 5), 스킬 발견·브라우저·실제 산출물(Task 6).
- 타입 일치: 모든 후속 Task는 공통 타입·API의 이름을 사용한다. Task 4 모드도 Trace가 바뀌는 preset의 mode 입력이며 별도 상태 시스템을 만들지 않는다.
- Review Focus 다섯 항목은 지정 Task의 실패 테스트·수용 테스트에 포함했다.
- 계획은 새 런타임·브라우저 제어·저장을 서로 독립 검토할 수 있는 여섯 Task로 나눈다. 별도 과목 어댑터와 임의 C 실행기는 만들지 않는다.
- 현재 단계에서는 이 문서와 Spec만 저장했다. 구현·설치·자료 생성·원본 노트 수정은 시작하지 않았다.

## 실행 인계

추천: Native. 여섯 Task가 같은 MemoryState/Trace 계약을 이어 쓰므로 같은 세션에서 직접 구현하고 마지막에 별도 검토하는 편이 적합하다. Subagent-driven도 선택할 수 있다. 계획 검토와 실행 방식 선택 뒤 선택한 방식의 실행 스킬을 적용한다.
