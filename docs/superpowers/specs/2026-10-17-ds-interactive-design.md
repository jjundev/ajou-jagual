# ds-interactive 설계

상태: 2026-10-17 채팅에서 사용자가 설계와 결정 #8·#9를 확정하고 구현을 요청했다. 구현 전 writing-plans의 계획 검토와 실행 방식 선택 단계는 별도로 진행한다.

## 목적과 범위

자구알 코드를 한 단계씩 따라가며 변수, 포인터, 객체의 변화를 확인하는 인터랙티브 HTML을 만드는 프로젝트 스킬이다. 장기 범위는 자구알 전반이며 첫 구현은 C 함수 호출과 포인터 추적이다. 학생이 복사된 값과 실제로 변경된 저장 공간을 구별할 수 있어야 한다.

bio-interactive의 공통 화면, 테마, 단계 재생, 내용 검토, 정리노트 연결 방식을 계승한다. 구·막대 중심의 3D 장면 런타임은 가져오지 않고 HTML·SVG로 메모리를 표현한다. 다른 과목 저장소를 실행 의존성으로 사용하지 않는다.

## 확정된 결정

| 번호 | 결정 |
|---|---|
| 0 | 공통 실행 상태와 함수별 명시적 시나리오를 사용한다. |
| 1 | 변수 자신의 저장 공간, 저장된 주소 값, 주소가 가리키는 객체를 구별한다. |
| 2 | 함수 호출을 인자 값 확인 → 매개변수 복사 → 함수 진입으로 펼친다. |
| 3 | 코드와 2D 메모리 그림을 같은 단계 데이터에서 만든다. |
| 4 | 준비된 구조 사례와 범위가 정해진 값 입력을 제공한다. |
| 5 | 원본 C, 의사코드, 학습용 보충, 컴파일용 보정을 구별한다. |
| 6 | 독립 HTML과 .pack 근거를 저장하고 정리노트에 현재 탭 링크를 연결한다. |
| 7 | 중간 상태 독립 검산과 실제 브라우저 확인을 완료 조건으로 삼는다. |
| 8 | 자구알 전반으로 확장 가능한 구조로 만든다. 사용자 확정. |
| 9 | 첫 자료는 0928 포인터 기초로 만든다. 사용자 확정. |

## 사용자 동작

- 입력은 MMDD, 실제 날짜 범위 폴더명, 주제, 로컬 C 파일 경로, 대화에 전달한 코드다.
- 날짜 입력은 좋은 주제 최대 2–4개, 주제·함수 입력은 자료 1개다. 후보가 적으면 억지로 채우지 않는다.
- 함수만 제공되면 호출자·초기 조건을 보충하고 학습용 보충이라고 표시한다. 인자가 없으면 대화의 범위를 사용하고 없으면 사용법·후보를 알린다.
- 왼쪽에 코드, 가운데에 호출 프레임·변수·객체, 오른쪽에 현재 변화·변경 전후·핵심 구별을 보여 준다.
- 이전, 다음, 처음, 자동 재생, 일시정지, 속도, 단계 이동, 입력 변경, 사례 선택, 변수 선택을 제공한다.
- 변수 선택 시 이름, 타입, 기호 주소, 저장된 값, 대상, 수명을 표시한다. NULL과 초기화되지 않은 값은 구별한다.
- 기본 진행 단위는 C 문장이며 복잡한 대입은 주소 계산과 쓰기로 펼칠 수 있다. 실행 전과 실행 후를 명시한다.
- 모바일에서는 코드·메모리 보기를 전환하면서 같은 단계와 설명을 유지한다. 1024px 미만은 패널을 접는다.
- 초기값 변경과 사례 전환은 재생을 멈추고 새 실행 기록의 0단계로 돌아간다.
- 색만으로 의미를 전달하지 않는다. 키보드 조작, 44px 이상 조작 버튼, reduced-motion을 지원한다.

## 실행 의미와 공통 인터페이스

Node.js 20 이상, CommonJS 저작·CLI, 브라우저용 번들에는 네이티브 DOM·SVG를 사용한다. 설치가 필요한 실행 라이브러리는 추가하지 않는다. Python 3와 Playwright는 검증 전용이다.

세 층으로 분리한다. 공통 플레이어는 Trace를 읽고, c-memory 어댑터는 C 시나리오와 이벤트를 Trace로 만들며, 자료별 시나리오는 소스·초기 조건·이벤트를 명시한다. 향후 큐·트리·정렬 등은 Trace 계약과 플레이어를 재사용하고 새 어댑터를 추가할 수 있다. 첫 버전에서 다른 어댑터를 구현하지 않는다.

- `Value`: `{kind:'int',value:number}`, `{kind:'pointer',target:string|null}`, `{kind:'uninitialized'}`, `{kind:'indeterminate'}`의 합 타입.
- `Cell`: `{id,name,type,owner,address,value,lifetime}`. owner는 호출 프레임 또는 객체 ID, lifetime은 live/ended. 주소는 기호이며 실제 ABI나 물리 배치를 주장하지 않는다.
- `Object`: `{id,type,storage,cellIds,lifetime}`. storage는 automatic/allocated, lifetime은 live/ended. 구조체 멤버와 배열 원소도 별개 Cell로 식별한다.
- `Frame`: `{id,functionId,callSite,cellIds,lifetime}`. 동일 함수를 재호출해도 고유 ID를 사용한다.
- `MemoryState`: `{frames,objects,cells,activeFrame,stdout}`. 이름으로 객체를 식별하지 않는다.
- `Location`: `{sourceId,line}`. line은 표시할 소스의 1부터 시작하는 줄 번호다.
- `Event`: `{kind,at,explanation,...payload}`. kind는 observe/call/bind/enter/declare/read/write/allocate/free/return/diagnostic이며 명시적 Cell ID와 Value를 사용한다. call은 프레임 생성, bind는 호출 시 계산된 Value를 새 매개변수에 복사, enter는 함수 진입, declare는 지역 저장 공간 생성이다. return은 반환값 전달과 자동 객체 수명 종료를 처리한다.
- `Snapshot`: `{id,at,phase,title,explanation,state,reads,writes,diagnostic}`. phase는 before/after/diagnostic, reads는 Cell ID 목록, writes는 `{cellId,before,after}` 목록이다.
- `Trace`: `{version:1,id,title,kind,sources,inputs,presets,snapshots,metadata}`. kind는 c-memory이고 플레이어는 어댑터 레지스트리로 렌더러를 고른다. metadata에는 출처, 코드 해시, 입력 해시, 보충·단순화가 들어간다.
- `Scenario`: `{version:1,id,title,kind,sources,inputs,presets,initialState(input),generateEvents(input),expected}`. 검증된 저작 코드이며 브라우저 사용자가 C나 JS를 입력·실행하는 기능이 아니다.
- `compileScenario(scenario,input,limits?) -> Trace`: 입력을 검사하고 초기 상태에 이벤트를 적용하여 불변 스냅샷을 생성한다.
- `validateTrace(trace) -> Issue[]`: ID, 줄 매핑, 포인터 대상, 수명, writes 정합성을 검사한다.
- `registerRenderer(kind,renderer)`와 `renderer.render(snapshot,selection)`: 공통 플레이어와 메모리 표현의 경계다. 사용자 문서에는 이 구현 세부를 노출하지 않는다.

기본 한도는 2,000단계, 호출 깊이 64, 객체 256개다. 초과는 LIMIT_REACHED로 알리고 정상 완료로 표시하지 않는다. 입력 정수는 첫 자료에서 -99부터 99까지로 제한한다.

### 저작 데이터의 구체적인 형식

- Source는 `{id,label,language:'c'|'pseudocode',text,provenance}`이며 provenance는 `{path,sha256,section?,page?,supplement,adjustments}`다. 붙여 넣은 코드는 RUN/source.c로 보존해 해시를 고정한다.
- Input은 `{key,label,type:'integer'|'enum',default,min?,max?,options?}`다. enum options는 `{value,label}` 목록이다. Preset은 `{id,label,input}`이고 input은 모든 Input key를 가진 객체다.
- Scenario.expected는 `{presetId,checks:[{step,cellId,value}],diagnosticCode?}` 목록이다. step은 Snapshot의 id 또는 'last'다. expected는 검증 보조이며 독립 검산을 대체하지 않는다.
- 이벤트 공통 필드는 kind, at, explanation이다. observe는 `{label}`을, call은 `{frame:Frame}`을, enter는 `{frameId}`를 가진다.
- bind는 `{cell:Cell,value:Value,fromCellId?}`, declare는 `{cell:Cell}`이다. bind는 새로운 callee 저장 공간에 복사하고 fromCellId는 호출자 읽기 표시다. `&a`처럼 주소를 계산하는 경우 value.target이 'main.a'여도 a의 값 읽기로 표시하지 않는다.
- read는 `{cellId,through?:string[]}`, write는 `{cellId,value:Value,through?:string[]}`다. through는 접근에 사용한 포인터 Cell ID 순서이며 엔진은 단계별 유효성 및 실제 target 연결이 목적지와 맞는지 검사한다. 직접 변수 접근은 through를 생략한다. 잘못된 target을 무시하고 임의 cellId에 쓰지 않는다.
- allocate는 `{object:Object,cells:Cell[],resultCellId:string|null}`이고 resultCellId가 있으면 해당 포인터에 객체 첫 Cell의 주소를 쓴다. 할당 실패는 해당 포인터에 NULL을 쓰는 write 이벤트로 명시한다.
- free는 `{pointerCellId}`이고 포인터가 객체 첫 Cell을 가리키는지 확인한다. return은 `{frameId,result?:{cellId,value:Value}}`이며 활성 프레임만 종료할 수 있다.
- diagnostic은 `{code,message}`다. 런타임이 발견한 진단도 같은 Snapshot 형식으로 제공한다. validateTrace는 구조 문제와 상태 전이 불일치를 반환하며 의도한 진단 preset 자체를 구조 실패로 취급하지 않는다.
- 자동 객체의 지역 Cell은 프레임의 cellIds에도 등록하고 owner는 Object ID를 사용한다. 객체에 속하지 않는 매개변수·지역 Cell의 owner는 Frame ID다. 객체 첫 Cell은 object.cellIds[0]이다.
- 초기 Snapshot id는 'initial'이고 phase=before다. 이후 각 이벤트에 'step-1'부터 순서 ID를 부여한다. read와 write를 별도 이벤트로 저작하면 같은 source line이 여러 단계에 나타날 수 있다.
- 생성된 시나리오는 엔진의 고정 전역 API만 사용하고 외부 require/import를 사용하지 않는다. Node에서는 module.exports, 브라우저에서는 고정 전역 등록 방식으로 같은 저작 소스를 로드한다.

### C 의미 규칙

- C의 인자는 값으로 전달된다. 포인터 전달도 주소 값의 복사이며 대상 객체를 복제하지 않는다. 수업의 call by reference 표현은 주소를 사용해 원본을 변경한다는 설명과 함께 구별한다.
- p, &p, *p와 포인터 변수의 재대입, 대상 필드의 쓰기를 구별한다. 이중 포인터는 호출자의 포인터 Cell까지 연결한다.
- 구조체 값 복사는 필드를 복사하되 포인터 필드의 대상 객체를 복제하지 않는다. 배열 매개변수는 포인터로 조정되는 별도 사례로 검증한다.
- 초기화되지 않은 값 읽기, NULL 접근, 범위 밖 접근, 종료된 저장 공간 접근, 잘못된 해제는 원인 단계에서 진단하고 이후 정상 실행 기록을 만들지 않는다. free(NULL)은 정상 무동작이다.
- free 뒤 기존 포인터는 유효한 주소 값처럼 읽지 않고 indeterminate로 표시한다. 종료 객체는 과거 관계를 확인하는 참조용 흔적으로만 남긴다. pi=NULL 대입은 가능하다.
- 반환 시 자동 객체의 수명을 끝내고 해당 객체를 가리키던 포인터의 유효성도 갱신한다. 반환값은 프레임 종료 전 계산된 값을 전달한다.
- 인자 사이의 평가 순서가 정해지지 않은 코드를 한 가지 필수 순서처럼 설명하지 않는다. 순서에 따라 결과가 달라지면 진단·보류하거나 명시한 조건의 별도 학습 예제로 분리한다.
- 실행 기록은 임의 단계에서도 같은 상태를 재현한다. 애니메이션은 표시 효과이며 계산과 무관하다.

## 첫 산출물

0928에 자료 세 개를 만든다. 신규 파일의 번호는 저장 시 계산한다.

1. 값과 주소의 전달: 값 매개변수와 포인터 매개변수를 비교하고 swap을 추적한다. 기본 a=1, b=2, 같은 객체를 두 인자로 넘기는 사례를 포함한다. 연결 절은 s1-call-by-value와 s1-swap이다.
2. 포인터 변수와 대상 값: `*p = 20; p = NULL;`의 차이와 p / &p / *p를 보여 준다. 기본 a=10, q=&a. 코드가 추가 예제임을 표시한다. 연결 절은 s0-pointer-ops다.
3. 이중 포인터로 호출자의 포인터 바꾸기: `p=&b`와 `*pp=&b`를 비교한다. 기본 a=10, b=20, q=&a. 연결 절은 s2-double-pointer다. 함수 호출 예제는 학습용 보충이라고 표시한다.

원본 정리노트 HTML·MD, STT, Software_3_ArrayStructureList.pdf의 관련 페이지를 대조한다. 원본의 구형 main() 등은 보존하며 검산용 C 파일에는 헤더·int main(void) 등 보정을 기록한다. 독립 검산에는 정의된 코드의 정상·동일 대상·경계 입력을 사용한다.

## 제작·저장·연결

- 새 스킬은 `.agents/skills/ds-interactive/`, 호환 링크는 `.claude/skills/ds-interactive`다.
- 제작 순서는 resolve → 근거·조건 확정 → 시나리오 저작 → check/steps → 독립 검산 → build → 브라우저 검토 → save → link-notes다.
- 날짜 검색은 실제 경로를 반환하며 .pack MD를 우선한다. 날짜 범위가 여러 폴더에 겹치면 AMBIGUOUS_TARGET, 명시 파일 누락은 SOURCE_MISSING이다. 날짜 없는 주제·코드는 대응 노트가 없으면 복습노트/주제별/을 사용한다.
- 공개 파일은 `복습노트/<날짜>/인터렉티브_NN_<이름>.html`, 저작·근거는 같은 폴더 `.pack/자료_인터렉티브_NN_<이름>/`이다. NN은 최소 두 자리다.
- 자료 폴더에 scenario.cjs, brief.md, source.json, trace.json, review.json, evidence/, note-links.json을 보존한다. 실행 경로는 RUN이며 매번 고유 디렉터리를 사용한다.
- HTML에는 CSS·JS·폰트를 포함한다. 로컬 Pretendard 자원과 라이선스·출처·SHA-256을 스킬에 동봉하고 런타임 외부 요청은 0이다.
- review.json은 schema/content/independent/browser의 실제 결과와 현재 소스·Trace·페이지 해시를 가진다. 미검토·실패·disputed·해시 변경은 save를 막는다. 구조 검사를 내용 검토로 기록하지 않는다.
- 기존 번호와 자료 폴더는 덮어쓰지 않는다. 충돌 시 다음 번호를 예약하며 새로 만든 파일만 실패 시 복구한다. 저장 직전 검토 해시를 재확인한다.
- 노트 연결은 관련 절 뒤 관찰 문장과 상대 경로 target=_self 링크만 추가한다. 본문·위젯·스타일·스크립트·MD·PDF는 보존한다. 절이 모호하면 해당 연결만 skipped다.
- 링크 명세는 자료 폴더 기준 상대 경로로 보존하고 노트 재생성 후 `relink`로 복원할 수 있게 한다. 재실행은 unchanged여야 한다. 변경 전 노트를 RUN에 백업한다.
- 기존 자료 연결만 요청하면 새 자료를 생성하지 않는다. 실제 같은 자료가 있으면 중복 생성하지 않고 이유를 보고한다.
- 자동 커밋·푸시·외부 게시는 하지 않는다. 모델·서브에이전트 사용을 강제하지 않는다.

## 검증과 완료 기준

값 복사, 포인터 복사와 별칭, 역참조, 포인터 재대입, 이중 포인터, 구조체 포인터 필드 복사, 배열 매개변수 조정, 연결 필드 변경, malloc/free, 호출별 고유 프레임, 자동 객체 수명, 오류 중단, 한도, 임의 이동을 의미 단위로 검증한다.

브라우저는 1440×900, 1024×768, 375×812에서 light/dark로 실제 확인한다. file://와 네트워크 차단을 우선하며 도구 제한 시 로컬 HTTP 대체와 미확인 범위를 기록한다. 모든 자료·모드·사례·단계·입력 경계를 확인하고 캡처를 눈으로 검토한다. 코드 내부 스크롤은 허용하되 문서 가로 넘침, 글자·화살표 겹침, 콘솔 오류, 외부 요청은 없어야 한다.

스킬 검증, 공통 엔진·CLI 테스트, 첫 자료 독립 검산, 브라우저 확인, 최종 경로에서 노트 링크 이동·뒤로가기·재연결 검증을 통과하고 파일·근거·한계를 보고해야 구현 완료다. 미검토 상태를 완료로 표시하지 않는다.

## 제외

임의 C 편집·실행, 전체 C 인터프리터, 실제 주소·ABI 재현, 3D 메모리, 다른 자료구조 어댑터의 즉시 구현, 복습팩 재생성, 다른 과목 저장소 수정, standalone 내보내기 스킬의 범위 확장은 제외한다.
