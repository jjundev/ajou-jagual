(function (global) {
  'use strict';

  const tree = {rootCellId: 'main.root', fields: {key: 'data', left: 'left', right: 'right'}};
  const nodeId = id => 'node-' + id;
  const dataId = id => nodeId(id) + '.data';
  const pointer = id => ({kind: 'pointer', target: id === 0 ? null : dataId(id)});
  const integer = value => ({kind: 'int', value});
  const uninitialized = {kind: 'uninitialized'};
  const pointerType = 'Node *';
  const cell = (owner, name, type, value) => ({
    id: owner + '.' + name, name, type, owner,
    address: '&' + owner + '.' + name, value, lifetime: 'live',
  });
  const at = line => ({sourceId: 'algorithm', line});

  function createState(rows, measures) {
    const root = cell('main', 'root', pointerType, pointer(rows[0]?.[0] ?? 0));
    const locals = [root];
    if (measures) locals.push(cell('main', 'result', 'int', uninitialized));
    const cells = Object.fromEntries(locals.map(local => [local.id, local]));
    const objects = {};
    for (const [number, data, left, right] of rows) {
      const id = nodeId(number);
      const fields = [
        cell(id, 'data', 'int', integer(data)),
        cell(id, 'left', pointerType, pointer(left)),
        cell(id, 'right', pointerType, pointer(right)),
      ];
      objects[id] = {id, type: 'Node', storage: 'static',
        cellIds: fields.map(field => field.id), lifetime: 'live'};
      for (const field of fields) cells[field.id] = field;
    }
    const main = {id: 'main', functionId: 'main', caller: null, cellIds: locals.map(local => local.id), lifetime: 'live'};
    return {frames: {main}, objects, cells, activeFrame: 'main', stdout: []};
  }

  function makeRecorder(rows, fn, flag, mode) {
    const nodes = new Map(rows.map(([id, data, left, right]) => [id, {data, left, right}]));
    let frameIndex = 0;
    let lineIndex = 0;

    function* line(location, label, explanation, ...events) {
      const lineStepId = 'run-' + (++lineIndex);
      for (const event of events) yield {at: location, lineStepId, label, explanation, ...event};
    }

    function* enter(number, parent, side, location, resumeAt) {
      const id = 'call-' + (++frameIndex);
      const parameter = cell(id, 'p', pointerType, pointer(number));
      const flagCell = cell(id, flag, 'int', integer(mode));
      const argument = parent ? nodeId(parent.number) + '.' + side : tree.rootCellId;
      const sideLabel = side === 'left' ? '왼쪽' : '오른쪽';
      const target = number === 0 ? 'NULL' : nodes.get(number).data + '번 노드의 주소';
      yield* line(location, parent ? sideLabel + ' 호출' : '루트 호출',
        (parent ? sideLabel + ' 링크의 ' : 'root에 저장된 ') + '포인터 값(' + target + ')을 새 호출의 p에 복사했어요.',
        {kind: 'read', cellId: argument, ...(parent && {memberOf: parent.parameter.id})},
        {kind: 'call', frame: {id, functionId: fn, callSite: location, resumeAt,
          argumentSourceCellId: argument, parameterCellId: parameter.id}},
        {kind: 'bind', cell: parameter, value: parameter.value, fromCellId: argument},
        {kind: 'bind', cell: flagCell, value: flagCell.value, ...(parent && {fromCellId: parent.flagCell.id})},
        {kind: 'enter', frameId: id});
      return {id, parameter, flagCell, number};
    }

    return {nodes, line, enter};
  }

  const cases = {
    "1-example": {"mode": 1, "rows": [[1, 8, 2, 3], [2, 3, 4, 0], [3, 10, 0, 5], [4, 1, 0, 0], [5, 14, 0, 0]]},
    "1-same": {"mode": 1, "rows": [[1, 7, 0, 2], [2, 7, 0, 0]]},
    "1-empty": {"mode": 1, "rows": []},
    "0-example": {"mode": 0, "rows": [[1, 8, 2, 3], [2, 3, 4, 0], [3, 10, 0, 5], [4, 1, 0, 0], [5, 14, 0, 0]]},
    "0-same": {"mode": 0, "rows": [[1, 7, 0, 2], [2, 7, 0, 0]]},
    "0-empty": {"mode": 0, "rows": []},
  };

  const scenario = {
    "version": 1,
    "id": "traversal-1102",
    "title": "전위·후위 순회 한 줄씩 실행하기",
    "kind": "c-tree",
    "intro": "사례에서 전위 또는 후위를 골라 같은 트리의 출력 순서를 비교해 보세요.",
    "takeaway": "전위는 현재 노드를 출력하고 두 자식을 호출해요. 후위는 두 자식 호출을 마친 뒤 현재 노드를 출력해요.",
    "supplement": "재귀 함수를 한 함수에 합치고 pre로 출력 위치를 고릅니다. NULL 조기 반환과 출력 구분용 공백을 추가했습니다. 트리와 호출자는 보충 예제입니다.",
    "sources": [
      {
        "id": "algorithm",
        "label": "walk 함수",
        "language": "c",
        "text": "void walk(Node *p, int pre) {\n  if (!p) return;\n  if (pre)\n    printf(\"%d \", p->data);\n  walk(p->left, pre);\n  walk(p->right, pre);\n  if (!pre)\n    printf(\"%d \", p->data);\n}",
        "provenance": {
          "path": "자료구조_강의록_2026/Software_7_Tree.pdf",
          "sha256": "fa120f543b739f5d5dc437412cbef624c0c0324d32f2410f1c337b3615dbafde",
          "page": "10, 12",
          "section": "전위 순회와 목차 · 후위 순회와 디렉토리 용량",
          "supplement": true,
          "adjustments": "재귀 함수를 한 함수에 합치고 pre로 출력 위치를 고릅니다. NULL 조기 반환과 출력 구분용 공백을 추가했습니다. 트리와 호출자는 보충 예제입니다."
        }
      },
      {
        "id": "driver-0",
        "label": "호출자",
        "language": "c",
        "text": "walk(root, 0);",
        "provenance": {
          "path": "복습노트/1102/.pack/정리노트_1102_Tree.md",
          "sha256": "fc1d03c324768fb743802285e382c2bd470355c36d70e49cf82fd3a619c74460",
          "section": "전위 순회와 목차 · 후위 순회와 디렉토리 용량",
          "supplement": true,
          "adjustments": "트리를 준비하는 호출자입니다."
        }
      },
      {
        "id": "driver-1",
        "label": "호출자",
        "language": "c",
        "text": "walk(root, 1);",
        "provenance": {
          "path": "복습노트/1102/.pack/정리노트_1102_Tree.md",
          "sha256": "fc1d03c324768fb743802285e382c2bd470355c36d70e49cf82fd3a619c74460",
          "section": "전위 순회와 목차 · 후위 순회와 디렉토리 용량",
          "supplement": true,
          "adjustments": "트리를 준비하는 호출자입니다."
        }
      }
    ],
    "inputs": [
      {
        "key": "exercise",
        "label": "실행 사례",
        "type": "enum",
        "default": "1-example",
        "options": [
          {
            "value": "1-example",
            "label": "전위 · 비대칭 트리"
          },
          {
            "value": "1-same",
            "label": "전위 · 같은 값 두 노드"
          },
          {
            "value": "1-empty",
            "label": "전위 · 빈 트리"
          },
          {
            "value": "0-example",
            "label": "후위 · 비대칭 트리"
          },
          {
            "value": "0-same",
            "label": "후위 · 같은 값 두 노드"
          },
          {
            "value": "0-empty",
            "label": "후위 · 빈 트리"
          }
        ]
      }
    ],
    "presets": [
      {
        "id": "1-same",
        "label": "전위 · 같은 값 두 노드",
        "input": {
          "exercise": "1-same"
        }
      },
      {
        "id": "1-empty",
        "label": "전위 · 빈 트리",
        "input": {
          "exercise": "1-empty"
        }
      },
      {
        "id": "0-example",
        "label": "후위 · 비대칭 트리",
        "input": {
          "exercise": "0-example"
        }
      },
      {
        "id": "0-same",
        "label": "후위 · 같은 값 두 노드",
        "input": {
          "exercise": "0-same"
        }
      },
      {
        "id": "0-empty",
        "label": "후위 · 빈 트리",
        "input": {
          "exercise": "0-empty"
        }
      }
    ],
    "expected": [],
    tree,
    initialState({exercise}) { return createState(cases[exercise].rows, false); },
    *generateEvents({exercise}) {
      const {mode, rows} = cases[exercise];
      const {line, enter, nodes} = makeRecorder(rows, 'walk', 'pre', mode);

      function* call(number, parent, side, location, resumeAt) {
        const frame = yield* enter(number, parent, side, location, resumeAt);
        const returnEvent = {kind: 'return', frameId: frame.id};
        const nodeRead = {kind: 'read', cellId: frame.parameter.id};
        if (number === 0) {
          yield* line(at(2), 'NULL 반환', resumeAt
            ? 'p가 NULL이에요. 출력 없이 호출자의 ' + resumeAt.line + '행으로 돌아가요.'
            : '빈 트리예요. 출력 없이 순회를 마쳐요.', nodeRead, returnEvent);
          return;
        }
        const {data, left, right} = nodes.get(number);
        yield* line(at(2), 'NULL 검사', 'p가 ' + data + '번 노드를 가리켜 순회를 계속해요.', nodeRead);
        const flagRead = {kind: 'read', cellId: frame.flagCell.id};
        const print = {kind: 'print-int', cellId: dataId(number), memberOf: frame.parameter.id};
        yield* line(at(3), '전위 조건', mode ? '전위 순회라 자식 호출 전에 현재 값을 출력해요.'
          : '후위 순회라 두 자식 호출부터 진행해요.', flagRead);
        if (mode) yield* line(at(4), '현재 값 출력', '자식으로 내려가기 전에 값 ' + data + ' 출력.', print);
        yield* call(left, frame, 'left', at(5), at(6));
        yield* call(right, frame, 'right', at(6), at(7));
        yield* line(at(7), '후위 조건', mode ? '전위 순회에서 이미 현재 값을 출력했어요.'
          : '두 자식 호출이 모두 끝나 현재 값을 출력해요.', flagRead);
        if (!mode) yield* line(at(8), '현재 값 출력', '두 자식 호출이 끝난 뒤 값 ' + data + ' 출력.', print);
        yield* line(at(9), '현재 호출 반환', resumeAt
          ? '현재 호출을 마치고 호출자의 ' + resumeAt.line + '행으로 돌아가요.'
          : '루트 호출에서 반환해 순회를 마쳐요.', returnEvent);
      }

      yield* call(rows[0]?.[0] ?? 0, null, null, {sourceId: 'driver-' + mode, line: 1}, null);
    },
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else global.DSInteractive.scenario = scenario;
})(globalThis);
