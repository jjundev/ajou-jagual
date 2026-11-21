# ds-interactive Recursive Tree Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 학생이 C 중위 순회를 한 줄씩 실행하면서 코드, 호출 스택, 메모리 표, 전체 트리와 출력을 같은 시점에서 확인하는 오프라인 자료를 만든다.

**Architecture:** 공통 C 엔진의 상세 이벤트·상태를 보존한다. 트리 시나리오는 상세 이벤트를 줄 단위 화면으로 투영하고, 같은 메모리에서 노드 연결과 스택을 읽어 공통 플레이어에 표시한다.

**Tech Stack:** Node.js 20+, CommonJS, 네이티브 DOM·SVG, Python 3·Playwright·C 컴파일러(검증).

**Spec:** [ds-interactive 재귀 트리 설계](../specs/2026-11-21-ds-interactive-tree-design.md)

## Global Constraints

- Node.js 20 이상, CommonJS 시나리오·CLI, 브라우저 네이티브 DOM·SVG. 새 런타임 의존성은 0개다.
- 공개 HTML은 `file://`에서 오프라인으로 열리며 외부 HTTP 요청은 0건이다. 기존 공용 Pretendard 상대 경로를 사용한다.
- 주소는 기호 주소다. 포인터는 값으로 전달하고 노드의 정체성은 객체 ID로 비교한다.
- 기존 `c-memory` 시나리오·자료의 이벤트 단위 동작과 화면을 유지한다. `c-tree`는 같은 엔진의 상세 이벤트 위에 줄 단위 스냅샷을 투영한다.
- 기본 한도는 상세 스냅샷 2,000개, 호출 깊이 64, 객체 256개다. 오류·한도 진단에서는 재생을 멈춘다.
- 1024px 이상에서 좌우 패널을 사용한다. 1024px 미만은 기존 서랍 규칙, 44px 이상 주요 조작부, 키보드·포커스·텍스트 상태·reduced-motion을 지원한다.
- 현재 `review → save → link-notes` 경로를 사용한다. 스키마·내용·독립 검산·브라우저 증거가 모두 현재 해시와 일치할 때 강의 노트에 연결한다.

## Review Focus

1. 동일한 키를 가진 객체 두 개는 각자 올바른 출력 순번을 얻는다. 작업 3.
2. `p->left`의 멤버가 다른 객체에 속하면 읽기와 출력을 거부한다. 작업 1.
3. 호출 한 줄 도중 검증 또는 단계 한도에서 중단하면 성공한 호출이나 다음 줄로 보이지 않는다. 작업 2.
4. 오른쪽 NULL 호출이 끝나면 호출자의 닫는 중괄호에서 재개한다. 종료 상태를 먼저 표시하지 않는다. 작업 4.
5. 모바일의 메모리 서랍에서 선택한 뒤 데스크톱으로 전환해도 위치·선택·포커스가 일관된다. 작업 5.

---

## 파일 구조

모든 작업의 경로는 저장소 루트 기준이다. 명령 예제에서 `S=.agents/skills/ds-interactive`를 먼저 설정한다.

| 책임 | 경로 |
|---|---|
| C 읽기·출력과 상세 이벤트 기록 | `$S/assets/engine/memory.js`, `$S/assets/engine/trace.js` |
| 줄 단위 화면 모델 | `$S/assets/engine/line-steps.js` |
| 트리 상태 해석과 검증 | `$S/assets/engine/tree.js` |
| 코드·재생·서랍과 트리 렌더링 | `$S/assets/{player.js,shell.html,shell.js,player.css,tree-svg.js}`, `$S/scripts/build.cjs` |
| 첫 중위 순회 자료와 독립 C 검산 | `$S/examples/1105/inorder.cjs`, `$S/tests/fixtures/inorder_oracle.c`, `$S/tests/inorder_oracle.py` |
| 저작 안내와 설치 위치 | `$S/SKILL.md`, `$S/references/{scenario-api,design,verification}.md`, `복습노트/1105/` |

### 작업 1 · C 구조체 멤버 읽기와 정수 출력

**파일:** 수정 `$S/assets/engine/{memory,trace}.js`, 테스트 `$S/tests/engine.test.cjs`.

**인터페이스**

- `applyEvent(state,{kind:'read',cellId,memberOf?:pointerCellId},limits?) -> EventResult`. `memberOf`는 기존 `through`와 함께 지정할 수 없다.
- `applyEvent(state,{kind:'print-int',cellId,memberOf?:pointerCellId},limits?) -> EventResult`. 성공하면 `state.stdout`에 `String(value) + ' '`를 추가하고 `printed:{cellId,text}`를 반환한다. `trace.js`는 상세 스냅샷에 결과를 보존한다.

- [ ] **실패 테스트 작성.** `struct member reads and int output follow the actual owner`. 기존 구조체 테스트의 상태 생성 방식을 사용하고 `p`가 가리키는 객체와 다른 객체 각각에 `key=7`을 둔다. 확인 값은 아래와 같다.

```js
assert.deepEqual(readMember.reads, ['p', 'a.left']);
assert.deepEqual(printMember.state.stdout, ['7 ']);
assert.deepEqual(printMember.printed, {cellId: 'a.key', text: '7 '});
assert.equal(wrongOwner.diagnostic.code, 'TARGET_MISMATCH');
assert.deepEqual(wrongOwner.state.stdout, []);
assert.equal(nullBase.diagnostic.code, 'NULL_DEREFERENCE');
assert.equal(nonInteger.diagnostic.code, 'VALUE_INVALID');
```

- [ ] `node --test "$S/tests/engine.test.cjs"`를 실행해 멤버 읽기·출력 계약 위반으로 실패하는지 확인한다.
- [ ] `memory.js`의 기존 유효성 검사에서 기호 포인터의 대상이 살아 있는 객체의 첫 Cell인지, 필드의 owner가 그 객체인지 확인한다. 검사가 성공한 후에만 출력한다. 진단에서는 기존 상태 복원 경로를 사용한다.
- [ ] `node --test "$S/tests/engine.test.cjs" "$S/tests/trace.test.cjs"`를 실행해 모두 통과하는지 확인한다.
- [ ] 작업 파일 단위로 커밋한다. `feat(ds-interactive): trace struct member reads and output`

### 작업 2 · 상세 이벤트를 소스 줄로 표시

**파일:** 생성 `$S/assets/engine/line-steps.js`, 수정 `$S/assets/engine/trace.js`, 테스트 `$S/tests/line-steps.test.cjs`.

**인터페이스**

- `c-tree` 이벤트의 `lineStepId:string`은 한 번 실행된 소스 줄에 속하는 연속 이벤트에 공통으로 부여한다. 묶음 안 `at`은 동일하다. 같은 ID의 재등장은 오류다. `call.frame`에는 `resumeAt:Location|null`, `argumentSourceCellId:string`, `parameterCellId:string`을 넣는다. `parameterCellId`에 대한 bind의 `fromCellId`는 `argumentSourceCellId`와 일치해야 한다.
- `projectLineSteps(snapshots:Snapshot[]) -> DisplayStep[]`를 CommonJS와 브라우저에 노출한다. `DisplayStep`은 `{id,state,executed:Cursor|null,next:Cursor|null,reads,writes,prints,diagnostic,title,explanation}`이다. `Cursor={at:Location,frameId:string}`, `prints`는 현재 위치까지의 `{cellId,text}` 배열이다. `compileScenario`는 `c-tree`의 `trace.lineSteps`에 이 배열을 저장한다.
- 상세 스냅샷은 기존 ID·이벤트 경계를 보존하고 트리 기록에만 `lineStepId`, 적용한 `eventKind`, 실행 직전의 `frameIdBefore`를 추가한다. 투영 ID는 `initial`, `line-1`, …다. 다음 위치의 프레임은 해당 실행 직전 활성 프레임이다.

- [ ] **실패 테스트 작성.** `line steps preserve the caller across reused source lines`에서 `walk:3`의 읽기·call·bind·enter를 하나로 묶고 서로 다른 두 프레임에서 `walk:2`를 사용한다. `diagnostic ends an incomplete line`은 같은 호출 묶음 안에서 두 번째 이벤트를 한도 진단으로 바꾼다.

```js
assert.equal(afterCall.executed.frameId, 'parent');
assert.deepEqual(afterCall.next, {at: {sourceId:'walk', line:2}, frameId:'child'});
assert.deepEqual(afterReturn.next, {at: {sourceId:'walk', line:4}, frameId:'parent'});
assert.equal(afterReturn.state.cells['child.p'].lifetime, 'ended');
assert.equal(terminal.next, null);
assert.equal(interrupted.diagnostic.code, 'LIMIT_REACHED');
assert.equal(interrupted.next, null);
assert.equal(interrupted.state.activeFrame, 'parent');
assert.throws(() => projectLineSteps(badResumeSnapshots), {code:'LINE_STEP_INVALID'});
assert.equal('lineSteps' in legacyTrace, false);
```

- [ ] `node --test "$S/tests/line-steps.test.cjs"`로 투영 계약의 실패를 확인한다.
- [ ] `projectLineSteps`에서 초기 화면과 각 묶음의 끝 상태를 생성한다. 읽기는 합집합, 동일 칸의 쓰기는 첫 이전 값과 마지막 이후 값으로 모은다. 출력은 성공한 상세 이벤트에서 누적한다. 진단 묶음은 마지막으로 확인된 상태와 진단을 표시한다. 소스 위치·인자 Cell·복귀 위치의 계약 위반은 `LINE_STEP_INVALID`로 보고한다. 반환 뒤 활성 호출과 `resumeAt`가 다음 묶음과 맞는지 검증한다. 순회 진입 프레임에서 외부 호출자로 반환할 때 `resumeAt:null`이면 화면은 순회 종료다.
- [ ] `node --test "$S/tests/line-steps.test.cjs" "$S/tests/trace.test.cjs"`에서 모두 통과하는지 확인한다.
- [ ] 작업 파일 단위로 커밋한다. `feat(ds-interactive): project C events into source line steps`

### 작업 3 · 메모리에서 트리와 활성 경로 계산

**파일:** 생성 `$S/assets/engine/tree.js`, 수정 `$S/assets/engine/trace.js`, 테스트 `$S/tests/tree.test.cjs`.

**인터페이스**

- 시나리오의 `tree:{rootCellId:string,fields:{key:string,left:string,right:string}}`를 `trace.metadata.tree`에 보존한다. 필드 지정 값은 해당 객체의 Cell 이름이다. 루트와 링크는 `NULL` 또는 객체 첫 Cell을 가리키는 포인터다.
- `getTreeView(tree:TreeDescriptor,step:DisplayStep) -> {rootId,nodes,stack,activeNodeId,nullEdge}`. `nodes`는 `{id,key,keyCellId,leftCellId,rightCellId,leftId,rightId,outputOrder}` 목록, `stack`은 활성 호출부터 부모 순서의 `{frameId,nodeId,parameterCellId,resumeAt}` 목록이다. `nullEdge`는 `{nodeId,side:'left'|'right'}|null`이다. 외부 호출자의 카드와 루트의 NULL은 각각 호출자와 빈 트리로 표시한다.
- 구조가 잘못되면 `TREE_INVALID` 이슈로 제작을 막는다. 진단 단계는 마지막으로 확인된 메모리 상태를 표시한다.

- [ ] **실패 테스트 작성.** `identical keys keep different output labels`는 키가 7인 왼쪽 노드 `left`과 루트 `root`가 있는 트리에 순서대로 출력을 추가한다. `tree links reject cycles and shared children`는 같은 fixture에서 링크만 바꾼다.

```js
assert.deepEqual(view.nodes.map(n => [n.id, n.outputOrder]).sort(), [['left',1],['root',2]]);
assert.deepEqual(nullView.nullEdge, {nodeId:'left', side:'left'});
assert.equal(emptyView.rootId, null);
assert.deepEqual(emptyView.nodes, []);
assert.throws(() => getTreeView(tree, cyclic), {code:'TREE_INVALID'});
assert.throws(() => getTreeView(tree, sharedChild), {code:'TREE_INVALID'});
```

- [ ] `node --test "$S/tests/tree.test.cjs"`로 실패를 확인한다.
- [ ] `getTreeView`는 활성 프레임에서 `caller`를 따라간다. `p`의 이름이 아니라 호출에 복사된 고유 Cell을 사용한다. 현재 NULL 호출의 `argumentSourceCellId`에서 빈 가지를 찾는다. 트리 뷰를 줄 단위 상태마다 검증하며 포인터와 필드의 타입·수명, 루트, 순환, 공유 자식을 확인한다. 노드의 출력 순번을 키가 아닌 `printed.cellId`로 찾는다.
- [ ] `node --test "$S/tests/tree.test.cjs" "$S/tests/line-steps.test.cjs"`에서 모두 통과하는지 확인한다.
- [ ] 작업 파일 단위로 커밋한다. `feat(ds-interactive): derive binary tree views from C memory`

### 작업 4 · 중위 순회와 별도 C 검산

**파일:** 생성 `$S/examples/1105/inorder.cjs`, `$S/tests/fixtures/inorder_oracle.c`, `$S/tests/inorder_oracle.py`, `$S/tests/inorder.test.cjs`.

**인터페이스**

- `inorder.cjs`는 기존 Scenario v1을 등록한다. enum `treeCase`의 기본 값은 `intro`, preset ID와 값은 `lecture`, `empty`다. 소스 ID `walk`는 설계의 여섯 줄, `driver`는 `inorder(root);` 한 줄이다. 1105 강의 트리와 보충 C 코드의 근거를 구분한다.
- `python3 "$S/tests/inorder_oracle.py" "$TREE_RUN/trace.json"`는 `CC` 또는 `cc`로 fixture를 빌드한 뒤 세 사례를 실행한다. 표준 출력에는 사례별 비교 결과를 JSON으로 기록한다. 비교 항목은 호출·복귀의 줄, 부모/자식 객체와 좌우 방향, 인자 주소에 대응하는 객체 ID, NULL 검사, 출력이다. C에서는 객체의 주소를 해당 객체 ID에 대응시켜 비교한다.

- [ ] **실패 테스트 작성.** `inorder runs all three cases and returns to the right line`에서 다음 조건을 확인한다. 출력 문자열 마지막 공백도 검증한다.

```js
assert.equal(intro.snapshots.at(-1).state.stdout.join(''), '1 3 8 10 ');
assert.equal(lecture.snapshots.at(-1).state.stdout.join(''), '3 7 12 18 26 27 31 ');
assert.deepEqual(empty.snapshots.at(-1).state.stdout, []);
assert.equal(afterRightNull.next.at.line, 6);
assert.equal(afterRightNull.next.frameId, leafFrame);
assert.equal(afterLeftNull.next.at.line, 4);
assert.deepEqual(afterLeftNull.state.stdout, []);
assert.equal(afterFirstPrint.state.stdout.join(''), '1 ');
```

- [ ] `node --test "$S/tests/inorder.test.cjs"`로 실패를 확인한다.
- [ ] `generateEvents(input)`를 작성한다. 보충 호출자와 초기 노드 객체를 선언하고, 호출·조건·왼쪽·출력·오른쪽·닫는 중괄호의 위치를 설계와 맞춘다. 왼쪽 호출의 `resumeAt`는 4행, 오른쪽 호출의 `resumeAt`는 6행이다. 호출자에서 순회가 반환되는 시점까지 추적한다. 인자의 원본 Cell이 `bind.fromCellId`와 일치하게 한다.
- [ ] C fixture를 별도로 작성해 같은 세 입력과 재귀 함수의 관측값을 기록한다. Python은 JS 엔진을 호출하지 않고 저장된 상세 Trace와 대조한다. 컴파일 환경이 없으면 기존 스킬의 독립 계산표 절차를 사용해 `compiler_unavailable`을 증거에 명시한다.
- [ ] `node --test "$S/tests/inorder.test.cjs"`와 아래 명령으로 세 사례가 통과하는지 확인한다.

```sh
TREE_RUN=$(mktemp -d)
node "$S/scripts/check.cjs" "$S/examples/1105/inorder.cjs"
node "$S/scripts/steps.cjs" "$S/examples/1105/inorder.cjs" > "$TREE_RUN/trace.json"
python3 "$S/tests/inorder_oracle.py" "$TREE_RUN/trace.json"
```

- [ ] 작업 파일 단위로 커밋한다. `feat(ds-interactive): add verified inorder traversal cases`

### 작업 5 · 오프라인 플레이어와 트리 화면

**파일:** 생성 `$S/assets/tree-svg.js`, `$S/tests/browser_tree.py`. 수정 `$S/assets/{player.js,shell.html,shell.js,player.css}`, `$S/scripts/build.cjs`, `$S/tests/build.test.cjs`, `$S/tests/browser_acceptance.py`.

**인터페이스**

- `registerRenderer('c-tree', {render(step,selection,metadata)})`. `selection`은 기존 Cell ID를 유지한다. 노드 버튼은 객체 ID를 `data-node-id`로 표시하고 해당 객체의 `key` Cell을 선택한다. 포인터를 선택하면 저장된 대상 객체를 강조한다.
- 트리 페이지의 `data-snapshot` 및 `data-step`은 `DisplayStep.id`를 사용한다. 테스트는 `data-active-frame`, `data-null-side`, `data-output-order`, `[data-action=previous-output]`, `[data-action=next-output]`으로 읽는다. 트리·코드·스택·출력은 공통 현재 인덱스를 사용한다.
- `browser_tree.py`는 `check_tree_case(page, width, height) -> tuple[int, int]`로 preset 수와 확인한 줄 단계를 반환한다. 공통 `browser_acceptance.py`는 열린 자료의 kind가 `c-tree`일 때 이 함수를 호출하고 `c-memory`에서는 기존 검사를 수행한다. 저장소 전체 검사도 두 종류를 함께 발견한다. 공통 검사는 1440×900, 1024×768, 375×812에서 밝은·어두운 테마의 스크린샷과 JSON을 남긴다.

- [ ] **실패 테스트 작성.** 기존 빌드 테스트에 `inorder build embeds the tree renderer`를 추가하고, 브라우저 검사에는 아래 조건을 넣는다. 사례 신호를 확인할 때 임의 대기 대신 상태 셀렉터를 기다린다.

```python
assert left_null_code == ('walk', 2) and left_null_side == 'left'
assert after_return_code == ('walk', 4) and after_return_output == ''
assert after_print_output.strip() == '1' and node_1_output_order == '1'
assert previous_output_after_rewind == '' and label_after_rewind is None
assert after_resize_step == before_resize_step
assert after_resize_selected_cell == before_resize_selected_cell
assert not focus_inside_hidden_panel
assert console_errors == [] and external_requests == []
```

- [ ] `node --test "$S/tests/build.test.cjs"`로 `c-tree` 빌드가 실패하는지 확인한다.
- [ ] `build.cjs`에 `c-tree`와 브라우저 의존 순서(`memory → line-steps/tree → trace → renderer → player`)를 연결한다. 플레이어와 단계 목록·슬라이더·재생은 트리에서 `lineSteps`, 포인터 자료에서 `snapshots`를 사용한다. 출력 이동은 현재보다 엄격히 앞뒤인 출력 직후를 선택한다. 진단과 정상 종료에서는 다음 줄 강조를 지운다.
- [ ] 트리 레이아웃은 자식 방향과 깊이로 좌표를 정하고 단계 이동 때 레이아웃을 고정한다. 현재 경로·NULL·출력 순번을 텍스트와 모양으로 구별한다. 모바일 서랍과 중앙 요약, 키보드 조작, 양방향 선택을 연결한다.
- [ ] 모든 preset과 모든 단계의 화면 인덱스·코드 위치를 대조한다. 앞뒤 이동, 출력 이동, 재생 중 사례 변경, 양방향 선택, 단계 유지·포커스, 모바일 버튼 경계, 다크 모드를 검사한다. 아래 명령으로 새 빌드와 기존 0928 재빌드의 오프라인 회귀를 검사한다.

```sh
TREE_RUN=$(mktemp -d)
node "$S/scripts/build.cjs" "$S/examples/1105/inorder.cjs" "$TREE_RUN/preview.html"
python3 "$S/tests/browser_acceptance.py" "$TREE_RUN/preview.html" "$(mktemp -d)"
POINTER_RUN=$(mktemp -d)
for name in value-address pointer-target double-pointer; do
  mkdir -p "$POINTER_RUN/$name"
  node "$S/scripts/build.cjs" "$S/examples/0928/$name.cjs" "$POINTER_RUN/$name/preview.html" || exit 1
done
python3 "$S/tests/browser_acceptance.py" "$POINTER_RUN" "$(mktemp -d)"
node --test "$S/tests/"*.test.cjs
```

- [ ] 스크린샷을 육안 확인한다. NULL 가지 끝, 호출 경로·출력 번호의 가독성, 패널·재생 바·그림 경계, 모바일 요약을 확인한다.
- [ ] 작업 파일 단위로 커밋한다. `feat(ds-interactive): play recursive tree traces offline`

### 작업 6 · 스킬 저작 가이드와 1105 자료 저장

**파일:** 수정 `$S/SKILL.md`, `$S/references/{scenario-api,design,verification}.md`, `복습노트/1105/정리노트_1105_Tree.html`. 생성 `복습노트/1105/인터렉티브_NN_중위순회_실행.html`과 대응 `.pack/자료_인터렉티브_NN_중위순회_실행/`. 실제 번호는 `save.cjs`가 정한다.

**인터페이스**

- 기존 `check → steps → build → review → save → link-notes` 명령을 사용한다. `review.json`의 네 판정은 실제 증거를 바탕으로 기록한다.
- 1105 `s0-inorder`의 새 링크 문구에서 관찰할 대상은 NULL 호출이 복귀하는 줄이다. 링크는 같은 탭에서 새 HTML을 연다.

- [ ] `SKILL.md`와 가이드에 `c-tree` 저작 조건, 상세 이벤트와 줄 묶음의 차이, 출력과 복귀 위치 필드, 검산·브라우저 검사 방법을 문서화한다.
- [ ] TREE_RUN을 새 고유 작업 디렉터리로 정하고 1105 예제를 `"$TREE_RUN/scenario.cjs"`로 복사한다. `brief.md`, `source.json`, `trace.json`, `preview.html`, `note-links.json`, `evidence/`를 작성한다. 1105 정리노트 절·강의 근거 페이지·파일 해시와 보충 코드를 기록한다. 강의 PDF를 근거에 넣으면 해당 페이지를 열어 확인한다. 모든 preset의 출력을 비교하고 기준 세 장면의 소스·인자·복귀·수명을 직접 대조한다.
- [ ] 아래 명령으로 검토를 초기화한다. 실제 schema/content/independent/browser 증거와 현재 해시를 기록한 뒤 검토를 확인하고 저장한다.

```sh
node "$S/scripts/review.cjs" init "$TREE_RUN"
node "$S/scripts/review.cjs" check "$TREE_RUN"
node "$S/scripts/save.cjs" "$TREE_RUN" "복습노트/1105" 중위순회_실행
```

- [ ] 저장 결과의 실제 pack 경로를 `TREE_PACK`, HTML 경로를 `TREE_HTML`로 사용한다. 링크 dry-run에서 해당 절 한 곳이 예정대로 연결되는지 확인한 뒤 적용한다.

```sh
node "$S/scripts/link-notes.cjs" "$TREE_PACK/note-links.json" --dry-run
node "$S/scripts/link-notes.cjs" "$TREE_PACK/note-links.json"
node "$S/scripts/review.cjs" check "$TREE_PACK"
node "$S/scripts/relink.cjs" "$PWD" 1105 --dry-run
python3 "$S/tests/browser_acceptance.py" "$TREE_HTML" "$(mktemp -d)"
```

- [ ] `relink`는 `unchanged`여야 한다. 브라우저에서 실제 1105 노트의 링크 클릭, 같은 탭 이동, 뒤로가기, 최종 공개본에서 기준 세 단계가 재현되는지 확인한다. 검토 증거가 가리키는 포인터 자료·트리 자료와 최종 경로를 보고한다.
- [ ] 백업이나 개인 작업 파일을 제외하고 작업 파일 단위로 커밋한다. `docs(ds-interactive): publish the inorder traversal lesson`
