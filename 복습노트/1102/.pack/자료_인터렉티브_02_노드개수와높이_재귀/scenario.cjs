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
    "1-slides": {"mode": 1, "rows": [[1, 8, 2, 3], [2, 3, 4, 5], [3, 10, 6, 0], [4, 1, 0, 0], [5, 6, 0, 0], [6, 9, 0, 0]]},
    "1-skew": {"mode": 1, "rows": [[1, 8, 0, 2], [2, 10, 0, 3], [3, 14, 0, 0]]},
    "1-single": {"mode": 1, "rows": [[1, 8, 0, 0]]},
    "1-empty": {"mode": 1, "rows": []},
    "0-slides": {"mode": 0, "rows": [[1, 8, 2, 3], [2, 3, 4, 5], [3, 10, 6, 0], [4, 1, 0, 0], [5, 6, 0, 0], [6, 9, 0, 0]]},
    "0-skew": {"mode": 0, "rows": [[1, 8, 0, 2], [2, 10, 0, 3], [3, 14, 0, 0]]},
    "0-single": {"mode": 0, "rows": [[1, 8, 0, 0]]},
    "0-empty": {"mode": 0, "rows": []},
  };

  const scenario = {
    "version": 1,
    "id": "tree-measure-1102",
    "title": "노드 개수와 높이의 재귀 반환",
    "kind": "c-tree",
    "intro": "노드 개수와 높이에서 왼쪽·오른쪽 반환값을 어떻게 쓰는지 비교해 보세요.",
    "takeaway": "빈 서브트리는 0을 반환해요. 노드 개수는 양쪽의 합에 1을 더하고, 높이는 양쪽 중 큰 값에 1을 더해요.",
    "supplement": "강의의 두 알고리즘을 calc로 합치고 sum으로 계산을 고릅니다. 양쪽 호출을 별도 문장에 두어 화면의 왼쪽→오른쪽 실행이 C 코드와 일치합니다. p16의 트리 모양을 보존하고 식별용 숫자와 다른 트리 사례를 보충했습니다.",
    "sources": [
      {
        "id": "algorithm",
        "label": "calc 함수",
        "language": "c",
        "text": "int calc(Node *p, int sum) {\n  if (!p) return 0;\n  int l, r;\n  l = calc(p->left, sum);\n  r = calc(p->right, sum);\n  if (sum)\n    return 1 + l + r;\n  return 1 + max(l, r);\n}",
        "provenance": {
          "path": "자료구조_강의록_2026/Software_7_Tree.pdf",
          "sha256": "fa120f543b739f5d5dc437412cbef624c0c0324d32f2410f1c337b3615dbafde",
          "page": "16, 17",
          "section": "노드 개수 get_node_count · 높이 get_height",
          "supplement": true,
          "adjustments": "강의의 두 알고리즘을 calc로 합치고 sum으로 계산을 고릅니다. 양쪽 호출을 별도 문장에 두어 화면의 왼쪽→오른쪽 실행이 C 코드와 일치합니다. p16의 트리 모양을 보존하고 식별용 숫자와 다른 트리 사례를 보충했습니다."
        }
      },
      {
        "id": "driver-0",
        "label": "호출자",
        "language": "c",
        "text": "result = calc(root, 0);",
        "provenance": {
          "path": "복습노트/1102/.pack/정리노트_1102_Tree.md",
          "sha256": "fc1d03c324768fb743802285e382c2bd470355c36d70e49cf82fd3a619c74460",
          "section": "노드 개수 get_node_count · 높이 get_height",
          "supplement": true,
          "adjustments": "트리를 준비하는 호출자입니다. result는 호출 전에 선언해 두었습니다."
        }
      },
      {
        "id": "driver-1",
        "label": "호출자",
        "language": "c",
        "text": "result = calc(root, 1);",
        "provenance": {
          "path": "복습노트/1102/.pack/정리노트_1102_Tree.md",
          "sha256": "fc1d03c324768fb743802285e382c2bd470355c36d70e49cf82fd3a619c74460",
          "section": "노드 개수 get_node_count · 높이 get_height",
          "supplement": true,
          "adjustments": "트리를 준비하는 호출자입니다. result는 호출 전에 선언해 두었습니다."
        }
      }
    ],
    "inputs": [
      {
        "key": "exercise",
        "label": "실행 사례",
        "type": "enum",
        "default": "1-slides",
        "options": [
          {
            "value": "1-slides",
            "label": "노드 개수 · 강의 트리"
          },
          {
            "value": "1-skew",
            "label": "노드 개수 · 오른쪽 경사"
          },
          {
            "value": "1-single",
            "label": "노드 개수 · 노드 하나"
          },
          {
            "value": "1-empty",
            "label": "노드 개수 · 빈 트리"
          },
          {
            "value": "0-slides",
            "label": "높이 · 강의 트리"
          },
          {
            "value": "0-skew",
            "label": "높이 · 오른쪽 경사"
          },
          {
            "value": "0-single",
            "label": "높이 · 노드 하나"
          },
          {
            "value": "0-empty",
            "label": "높이 · 빈 트리"
          }
        ]
      }
    ],
    "presets": [
      {
        "id": "1-skew",
        "label": "노드 개수 · 오른쪽 경사",
        "input": {
          "exercise": "1-skew"
        }
      },
      {
        "id": "1-single",
        "label": "노드 개수 · 노드 하나",
        "input": {
          "exercise": "1-single"
        }
      },
      {
        "id": "1-empty",
        "label": "노드 개수 · 빈 트리",
        "input": {
          "exercise": "1-empty"
        }
      },
      {
        "id": "0-slides",
        "label": "높이 · 강의 트리",
        "input": {
          "exercise": "0-slides"
        }
      },
      {
        "id": "0-skew",
        "label": "높이 · 오른쪽 경사",
        "input": {
          "exercise": "0-skew"
        }
      },
      {
        "id": "0-single",
        "label": "높이 · 노드 하나",
        "input": {
          "exercise": "0-single"
        }
      },
      {
        "id": "0-empty",
        "label": "높이 · 빈 트리",
        "input": {
          "exercise": "0-empty"
        }
      }
    ],
    "expected": [
      {
        "presetId": "default",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 6
            }
          }
        ]
      },
      {
        "presetId": "1-skew",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 3
            }
          }
        ]
      },
      {
        "presetId": "1-single",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 1
            }
          }
        ]
      },
      {
        "presetId": "1-empty",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 0
            }
          }
        ]
      },
      {
        "presetId": "0-slides",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 3
            }
          }
        ]
      },
      {
        "presetId": "0-skew",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 3
            }
          }
        ]
      },
      {
        "presetId": "0-single",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 1
            }
          }
        ]
      },
      {
        "presetId": "0-empty",
        "checks": [
          {
            "step": "last",
            "cellId": "main.result",
            "value": {
              "kind": "int",
              "value": 0
            }
          }
        ]
      }
    ],
    "watch": [
      {
        "name": "l",
        "label": "왼쪽 반환값"
      },
      {
        "name": "r",
        "label": "오른쪽 반환값"
      },
      {
        "name": "result",
        "label": "루트 반환값",
        "cellId": "main.result"
      }
    ],
    tree,
    initialState({exercise}) { return createState(cases[exercise].rows, true); },
    *generateEvents({exercise}) {
      const {mode, rows} = cases[exercise];
      const {line, enter, nodes} = makeRecorder(rows, 'calc', 'sum', mode);

      function* call(number, parent, side, location, resumeAt, outputId) {
        const frame = yield* enter(number, parent, side, location, resumeAt);
        const nodeRead = {kind: 'read', cellId: frame.parameter.id};
        const returnValue = value => ({kind: 'return', frameId: frame.id,
          result: {cellId: outputId, value: integer(value)}});
        const outputName = side ? side[0] : 'result';
        const returned = ' → ' + outputName + '에 저장해요.';
        if (number === 0) {
          yield* line(at(2), 'NULL에서 0 반환', '빈 서브트리의 값 0' + returned, nodeRead, returnValue(0));
          return 0;
        }
        const {data, left, right} = nodes.get(number);
        yield* line(at(2), 'NULL 검사', 'p가 ' + data + '번 노드를 가리켜 왼쪽 재귀 호출로 넘어가요.', nodeRead);
        const leftCell = cell(frame.id, 'l', 'int', uninitialized);
        const rightCell = cell(frame.id, 'r', 'int', uninitialized);
        yield* line(at(3), '반환값 변수 선언', '양쪽 호출의 반환값을 받을 l과 r을 준비해요.',
          {kind: 'declare', cell: leftCell}, {kind: 'declare', cell: rightCell});
        const l = yield* call(left, frame, 'left', at(4), at(5), leftCell.id);
        const r = yield* call(right, frame, 'right', at(5), at(6), rightCell.id);
        yield* line(at(6), '계산 선택', mode ? '노드 개수는 두 서브트리의 값을 모두 더해요.'
          : '높이는 두 서브트리 중 큰 값을 골라요.', {kind: 'read', cellId: frame.flagCell.id});
        const value = 1 + (mode ? l + r : Math.max(l, r));
        const expression = mode ? '1 + ' + l + ' + ' + r : '1 + max(' + l + ', ' + r + ')';
        yield* line(at(mode ? 7 : 8), '계산 결과 반환', expression + ' = ' + value + returned,
          {kind: 'read', cellId: leftCell.id}, {kind: 'read', cellId: rightCell.id}, returnValue(value));
        return value;
      }

      yield* call(rows[0]?.[0] ?? 0, null, null, {sourceId: 'driver-' + mode, line: 1}, null, 'main.result');
    },
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else global.DSInteractive.scenario = scenario;
})(globalThis);
