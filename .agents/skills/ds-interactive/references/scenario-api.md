# Scenario와 Trace

저작 단위는 버전 1의 신뢰된 `.cjs` 파일이다. 외부 require/import 없이 Node에서는 `module.exports=scenario`, 브라우저에서는 `globalThis.DSInteractive.scenario=scenario`로 등록한다. [완전한 예제](../examples/0928/value-address.cjs)를 복사해 실제 근거·주제에 맞게 작성한다. C를 자동 파싱하지 않는다.

Scenario 필드: `version:1,id,title,kind:'c-memory',sources,inputs,presets,initialState(input),generateEvents(input),expected`. 선택 사항 intro/takeaway는 학습 안내다.

| 형식 | 필드 |
|---|---|
| Source | id,label,language c/pseudocode,text,provenance |
| provenance | path,sha256,section?,page?,supplement:boolean,adjustments |
| Input | key,label,type integer/enum,default,min/max 또는 options:[{value,label}] |
| Preset | id,label,input (모든 key 포함) |
| Value | {kind:'int',value:정수}, {kind:'pointer',target:Cell ID 또는 null}, {kind:'uninitialized'}, {kind:'indeterminate'} |
| Cell | id,name,type,owner:Frame/Object ID,address:기호,value,lifetime live/ended |
| Frame | id,functionId,callSite,cellIds,lifetime (caller는 엔진이 기록) |
| Object | id,type,storage automatic/allocated,cellIds,lifetime |
| MemoryState | frames/objects/cells: ID→객체 맵, activeFrame:ID/null, stdout:배열 |

Source.text의 `{{a}}`처럼 **정수 Input key**만 치환할 수 있다. Trace.sources에 현재 정수로 바뀐 코드가 들어간다. 줄 수는 변하지 않는다. 모드는 별도 Source로 작성한다. 초기 단계는 첫 이벤트의 소스와 줄을 가리킨다. 코드를 원문이라고 표시할 때 템플릿·호출자 보충을 구분한다.

공통 Event 필드: `kind,at:{sourceId,line:1부터},explanation,label?`. 이벤트는 배열 또는 유한 iterable이다. 처음부터 무한 배열을 만들지 않는다.

| kind | 추가 필드 / 의미 |
|---|---|
| observe | label / 상태 설명 |
| call | frame / 고유 호출 저장 공간 생성 |
| bind | cell,value,fromCellId? / 평가된 인자 값 복사. from이 있으면 실제 값 일치 검사 |
| enter | frameId / 활성 프레임 전환 |
| declare | cell / 선언, 미초기화도 허용 |
| read | cellId,through?:[포인터 Cell ID 사슬] |
| write | cellId,value,through? / 사슬이 실제 cellId를 가리켜야 함 |
| allocate | object,cells,resultCellId:null/ID / 객체 첫 Cell 주소를 결과 포인터에 씀 |
| free | pointerCellId / NULL 무동작, 할당 객체의 시작 주소만 허용 |
| return | frameId,result?:{cellId,value} / 활성 프레임 자동 저장 공간 종료 |
| diagnostic | code,message / 원인 단계에서 중단 |

`&a`는 a의 **값**을 읽지 않으므로 bind.fromCellId를 지정하지 않는다. `q`를 넘기면 q의 주소 값을 읽으므로 fromCellId='main.q'다. 함수 내부의 동적 read/write 값은 저작자가 계산한다. 엔진은 C 표현식 계산기가 아니다. 독립 검산이 저작 계산의 정확성을 보증한다.

자동 배열·구조체의 멤버는 owner=Object ID이며 해당 Frame.cellIds에도 등록한다. 같은 이름이어도 ID는 별개다. 반복 호출은 f1/f2처럼 새 ID를 사용한다. 구조체 값 복사는 각 필드 이벤트로, 배열 인자는 첫 원소 주소의 bind로 저작한다.

`compileScenario(scenario,input,limits?)` → 불변 Trace. 한도 steps 2000(초기·종료 진단 포함), depth 64, objects 256. `validateTrace(trace)` → `{code,path,message}[]`. `checkScenario(scenario)` → `{ok,issues,traces}` 기본과 모든 preset. expected는 `{presetId,checks:[{step:'last'|'step-N',cellId,value}],diagnosticCode?}`다. 의도한 진단도 expected에 적는다.

Snapshot: id initial/step-N,at,phase before/after/diagnostic,title,explanation,state,reads,writes:[{cellId,before,after}],diagnostic:null/{code,message}. Trace: version,id,title,kind,sources,inputs(선택값),presets,snapshots,metadata. UI의 코드/표/화살표/변화는 선택 Snapshot만 사용한다.

확장: `registerRenderer(kind,{render(snapshot,selection)})`로 DOM 노드를 반환한다. 현재 빌더는 c-memory만 승인한다. 새 어댑터는 상태 검증·빌더 승인·상호작용 검사를 함께 확장한다.
