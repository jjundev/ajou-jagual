# Scenario와 Trace

저작 단위는 버전 1의 신뢰된 `.cjs` 파일이다. 외부 require/import 없이 Node에서는 `module.exports=scenario`, 브라우저에서는 `globalThis.DSInteractive.scenario=scenario`로 등록한다. [포인터 예제](../examples/0928/value-address.cjs) 또는 [중위 순회 예제](../examples/1105/inorder.cjs)를 복사해 실제 근거·주제에 맞게 작성한다. C를 자동 파싱하지 않는다.

Scenario 필드: `version:1,id,title,kind:'c-memory'|'c-tree',sources,inputs,presets,initialState(input),generateEvents(input),expected`. 선택 사항 intro/takeaway는 학습 안내다.

| 형식 | 필드 |
|---|---|
| Source | id,label,language c/pseudocode,text,provenance |
| provenance | path,sha256,section?,page?,supplement:boolean,adjustments,note?(포인터 화면의 코드 아래 한 줄 안내. 생략하면 기본 문구를 표시한다. 트리 화면은 출처를 저작·검토 데이터에 두며 이 안내를 숨긴다.) |
| Input | key,label,type integer/enum,default,min/max 또는 options:[{value,label}] |
| Preset | id,label,input (모든 key 포함) |
| Value | {kind:'int',value:정수}, {kind:'pointer',target:Cell ID 또는 null}, {kind:'uninitialized'}, {kind:'indeterminate'} |
| Cell | id,name,type,owner:Frame/Object ID,address:기호,value,lifetime live/ended |
| Frame | id,functionId,callSite,cellIds,lifetime (caller는 엔진이 기록) |
| Object | id,type,storage automatic/allocated/static,cellIds,lifetime |
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
| read | cellId, through?:[포인터 Cell ID 사슬] 또는 memberOf?:객체 시작 주소를 담은 포인터 Cell ID |
| print-int | cellId, memberOf? / 정수를 `%d ` 형식으로 stdout에 추가하고 상세 단계에 printed:{cellId,text} 기록 |
| write | cellId,value,through? / 사슬이 실제 cellId를 가리켜야 함 |
| allocate | object,cells,resultCellId:null/ID / 객체 첫 Cell 주소를 결과 포인터에 씀 |
| free | pointerCellId / NULL 무동작, 할당 객체의 시작 주소만 허용 |
| return | frameId,result?:{cellId,value} / 활성 프레임 자동 저장 공간 종료 |
| diagnostic | code,message / 원인 단계에서 중단 |

`&a`는 a의 **값**을 읽지 않으므로 bind.fromCellId를 지정하지 않는다. `q`를 넘기면 q의 주소 값을 읽으므로 fromCellId='main.q'다. 함수 내부의 동적 read/write 값은 저작자가 계산한다. 엔진은 C 표현식 계산기가 아니다. 독립 검산이 저작 계산의 정확성을 보증한다.

자동 배열·구조체의 멤버는 owner=Object ID이며 해당 Frame.cellIds에도 등록한다. 같은 이름이어도 ID는 별개다. 반복 호출은 f1/f2처럼 새 ID를 사용한다. 구조체 값 복사는 각 필드 이벤트로, 배열 인자는 첫 원소 주소의 bind로 저작한다.

`compileScenario(scenario,input,limits?)` → 불변 Trace. 한도 steps 2000(초기·종료 진단 포함), depth 64, objects 256. `validateTrace(trace)` → `{code,path,message}[]`. `checkScenario(scenario)` → `{ok,issues,traces}` 기본과 모든 preset. expected는 `{presetId,checks:[{step:'last'|'step-N',cellId,value}],diagnosticCode?}`다. 의도한 진단도 expected에 적는다.

Snapshot: id initial/step-N,at,phase before/after/diagnostic,title,explanation,state,reads,writes:[{cellId,before,after}],diagnostic:null/{code,message}. Trace: version,id,title,kind,sources,inputs(선택값),presets,snapshots,metadata. `c-memory` 재생은 선택한 Snapshot을 코드·메모리·변화에 표시한다.

## 이진 트리의 소스 줄과 호출

- `tree:{rootCellId,fields:{key,left,right}}`를 지정한다. 필드 값은 각 객체의 Cell 이름이다. `root`, `left`, `right`에는 NULL 또는 객체 첫 Cell의 주소를 넣는다. 첫 Cell은 엔진이 객체를 찾는 기준이며 화면은 객체 주소와 멤버 주소를 구별한다. 순환·공유 자식·잘못된 링크는 `TREE_INVALID`다.
- 한 줄에서 일어난 상세 이벤트에는 같은 `lineStepId`와 `at`을 준다. ID는 한 번 실행된 줄 하나에만 사용한다. 재귀 호출 한 줄의 읽기 → call → bind → enter를 묶는다. 호출 프레임에는 `argumentSourceCellId`, `parameterCellId`, `resumeAt:{sourceId,line}|null`이 필요하다. bind의 `fromCellId`는 `argumentSourceCellId`와 일치해야 한다. `resumeAt:null`인 순회가 외부 호출자로 반환되면 재생을 종료한다.
- `trace.snapshots`는 상세 이벤트를 보존한다. `trace.lineSteps`의 `initial`과 `line-N`은 한 줄 단위 종료 상태다. `executed`와 `next`는 각 위치의 `{at,frameId}` 또는 null이다. `reads`와 `writes`는 한 줄에서 발생한 접근을 모으고, `prints`는 현재까지의 `{cellId,text}`를 차례로 담는다. 진단 시 다음 줄을 강조하지 않고 직전에 완료한 줄의 메모리를 표시한다.
- `getTreeView(trace.metadata.tree,step)`는 그 단계의 포인터·프레임·출력에서 노드, 활성 경로, NULL 가지, 출력 순번을 계산한다. `registerRenderer(kind,{render(step,selection,metadata)})`는 같은 스텝을 받아 DOM을 반환한다.

### 현재 변수 카드 설정

노드 매개변수가 있는 `c-tree` 사례는 `parameterCellId`로 활성 호출의 매개변수를 찾아 현재 노드 카드를 자동으로 표시한다. 사례의 호출 기록에서 변수명을 읽고, 호출 전과 최종 반환 후에는 `—`, NULL 인자에서는 `NULL`을 표시한다. 같은 매개변수를 가리키는 기존 활성 프레임 `watch` 항목은 한 번만 보인다.

선택 필드 `watch`에는 학습 목표에 필요한 추가 변수만 화면에 표시할 순서대로 넣는다. `name`은 코드에 나온 변수명, `label`은 변수 뜻이다. 고정 Cell을 표시하려면 `cellId`를 지정한다. 생략하면 현재 단계의 활성 프레임에 있는 `<activeFrame>.<name>` Cell을 표시한다.

```js
watch: [
  { name: 'n', label: '노드 수', cellId: 'stats.n' },
  { name: 'h', label: '최대 레벨', cellId: 'stats.h' },
  { name: 'd', label: '호출 레벨' },
],
```

카드는 현재 `lineStep.state.cells`에서 값을 읽고 `lineStep.writes`에 해당 Cell이 있으면 값을 강조한다. 트리 노드를 가리키는 포인터는 `p = 18번 노드`처럼 대상 노드를 표시하고, 널 포인터는 `NULL`로 표시한다. 현재 단계에 Cell이 없거나 수명이 끝났으면 `—`를 표시한다.
