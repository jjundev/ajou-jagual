(function (root) {
  'use strict';
  const int = value => ({kind: 'int', value});
  const empty = {kind: 'uninitialized'};
  const ids = (name, length) => Array.from({length}, (_, i) => name + '.' + i);
  const cell = (id, name, owner, value) => ({
    id, name, type: 'int', owner, address: '&' + name, value, lifetime: 'live',
  });
  function start(functionId, values, parameters) {
    const list = ids('list', values.length);
    const cells = Object.fromEntries(values.map((value, i) =>
      [list[i], cell(list[i], 'list[' + i + ']', 'list', int(value))]));
    for (const [name, value] of Object.entries(parameters)) {
      cells['f.' + name] = cell('f.' + name, name, 'f', int(value));
    }
    return {
      cells, objects: {list: {id: 'list', type: 'int[]', storage: 'automatic', cellIds: list, lifetime: 'live'}},
      frames: {
        main: {id: 'main', functionId: 'main', cellIds: list.slice(), lifetime: 'live', caller: null},
        f: {id: 'f', functionId, cellIds: Object.keys(cells).filter(id => id.startsWith('f.')),
          lifetime: 'live', caller: 'main'},
      },
      activeFrame: 'f', stdout: [],
    };
  }
  function recorder(sourceId) {
    const events = [];
    const emit = (kind, line, label, explanation, data) =>
      events.push({kind, at: {sourceId, line}, label, explanation, ...data});
    return {
      events,
      note: (line, label, text) => emit('observe', line, label, text),
      local: (line, name, value, text) =>
        emit('declare', line, name + ' 선언', text, {cell: cell('f.' + name, name, 'f', value)}),
      read: (line, id, label, text) => emit('read', line, label, text, {cellId: id}),
      write: (line, id, value, label, text) =>
        emit('write', line, label, text, {cellId: id, value: int(value)}),
      finish: (line, text, result) => emit('return', line, '호출 종료', text, {frameId: 'f', result}),
    };
  }
  const row = (label, name, length) => ({label, cells: ids(name, length)});
  const watch = (name, label, cellId = 'f.' + name) => ({name, label, cellId});
  const value = (step, id) => step.state.cells[id]?.value.value;
  const listText = (step, length) => ids('list', length).map(id => value(step, id)).join(' · ');
  const check = (cellId, value) => ({step: 'last', cellId, value: int(value)});
  const examples = {
    lecture: [10, 27, 12, 20],
    left: [1, 2, 7, 9],
    strict: [2, 5, 2, 3],
    stable: [2, 5, 2, 3],
  };
  const options = [
    {value: 'lecture', label: '강의 예제'},
    {value: 'left', label: '왼쪽이 먼저 소진'},
    {value: 'strict', label: '동점이면 오른쪽 먼저'},
    {value: 'stable', label: '동점이면 왼쪽 먼저'},
  ];
  const length = 4, mid = 1, right = 3;
  const scenario = {
    version: 1, id: '1126-merge-heads', kind: 'c-memory',
    title: '정렬된 두 부분 배열의 합병',
    intro: 'list[0..1]과 list[2..3]은 각각 정렬되어 있습니다. 두 구간의 첫 후보를 비교하세요.',
    takeaway: '선택된 구간의 인덱스만 움직이고 한쪽이 소진되면 다른 쪽의 남은 값을 복사하는 과정을 확인하세요.',
    sources: [
  {
    "id": "merge",
    "label": "합병 · 오른쪽 우선",
    "language": "c",
    "text": "void merge(int list[], int left, int mid, int right)\n{\n    int b1 = left;\n    int b2 = mid + 1;\n    int sorted[4];\n    int index = 0;\n    while (b1 <= mid && b2 <= right) {\n        if (list[b1] < list[b2]) {\n            sorted[index] = list[b1];\n            b1++;\n        } else {\n            sorted[index] = list[b2];\n            b2++;\n        }\n        index++;\n    }\n    while (b1 <= mid) {\n        sorted[index] = list[b1];\n        b1++;\n        index++;\n    }\n    while (b2 <= right) {\n        sorted[index] = list[b2];\n        b2++;\n        index++;\n    }\n    for (int i = 0; i < index; i++)\n        list[left + i] = sorted[i];\n}",
    "provenance": {
      "path": "자료구조_강의록_2026/Software_9_Sorting.pdf",
      "sha256": "f24fa0f39ec39b47dd942eac1a1ab81fdeb592fb608c0d6248a4299266827cac",
      "page": 21,
      "section": "p18 왼쪽 4원소 합병, p21 의사코드, STT Part 06–07",
      "adjustments": "실행용 C 보충. e1/e2 대신 mid/right를 직접 참조하고 길이 4에 맞춰 임시 배열을 둔다.",
      "supplement": true
    }
  },
  {
    "id": "merge-stable",
    "label": "합병 · 왼쪽 우선",
    "language": "c",
    "text": "void merge(int list[], int left, int mid, int right)\n{\n    int b1 = left;\n    int b2 = mid + 1;\n    int sorted[4];\n    int index = 0;\n    while (b1 <= mid && b2 <= right) {\n        if (list[b1] <= list[b2]) {\n            sorted[index] = list[b1];\n            b1++;\n        } else {\n            sorted[index] = list[b2];\n            b2++;\n        }\n        index++;\n    }\n    while (b1 <= mid) {\n        sorted[index] = list[b1];\n        b1++;\n        index++;\n    }\n    while (b2 <= right) {\n        sorted[index] = list[b2];\n        b2++;\n        index++;\n    }\n    for (int i = 0; i < index; i++)\n        list[left + i] = sorted[i];\n}",
    "provenance": {
      "path": "자료구조_강의록_2026/Software_9_Sorting.pdf",
      "sha256": "f24fa0f39ec39b47dd942eac1a1ab81fdeb592fb608c0d6248a4299266827cac",
      "page": 21,
      "section": "p21 의사코드와 p22 안정성 설명",
      "adjustments": "동일 키에서 원래 앞에 있던 왼쪽 원소를 먼저 꺼내도록 <=를 적용하는 비교 사례다.",
      "supplement": true
    }
  }
],
    inputs: [{key: 'example', label: '합병 사례', type: 'enum', default: 'lecture', options}],
    presets: options.slice(1).map(({value, label}) => ({id: value, label, input: {example: value}})),
    array: {
      heading: '원본 배열과 임시 배열',
      rows: [row('list', 'list', length), row('sorted', 'sorted', length)],
      markers: [{cellId: 'f.b1', label: 'b1', row: 0, min: 0, max: mid},
        {cellId: 'f.b2', label: 'b2', row: 0, min: mid + 1, max: right},
        {cellId: 'f.index', label: '쓰기', row: 1}],
      splits: {0: mid + 1},
      watch: [watch('b1', '왼쪽 첫 후보'), watch('b2', '오른쪽 첫 후보'),
        watch('index', '임시 배열 쓰기 위치'), watch('i', '원본에 복사할 위치')],
      title: '원본 배열의 현재 값',
      result: step => listText(step, length),
    },
    initialState({example}) {
      const state = start('merge', examples[example], {left: 0, mid, right});
      state.objects.sorted = {id: 'sorted', type: 'int[]', storage: 'automatic', cellIds: [], lifetime: 'live'};
      return state;
    },
    generateEvents({example}) {
      const data = examples[example], stable = example === 'stable', sorted = [];
      const r = recorder(stable ? 'merge-stable' : 'merge');
      let b1 = 0, b2 = 2, index = 0;
      r.read(3, 'f.left', '왼쪽 경계 읽기', '첫 구간 시작 위치를 읽습니다.');
      r.local(3, 'b1', int(b1), '왼쪽의 첫 후보는 list[0]입니다.');
      r.read(4, 'f.mid', '중앙 경계 읽기', 'mid 다음 칸이 오른쪽 구간의 시작입니다.');
      r.local(4, 'b2', int(b2), '오른쪽의 첫 후보는 list[2]입니다.');
      for (let i = 0; i < length; i++) {
        r.events.push({kind: 'declare', at: {sourceId: stable ? 'merge-stable' : 'merge', line: 5},
          label: '임시 배열 칸 선언', explanation: 'sorted[' + i + ']는 아직 값이 없습니다.',
          cell: cell('sorted.' + i, 'sorted[' + i + ']', 'sorted', empty)});
      }
      r.local(6, 'index', int(0), '임시 배열의 첫 칸부터 채웁니다.');
      function copy(side, line, tail) {
        const isLeft = side === '왼쪽', source = isLeft ? b1 : b2;
        r.read(line, 'list.' + source, side + ' 후보 읽기',
          (tail ? '남은 ' : '선택한 ') + side + ' 구간에서 ' + data[source] + '를 읽습니다.');
        sorted[index] = data[source];
        r.write(line, 'sorted.' + index, sorted[index], '임시 배열에 쓰기',
          'sorted[' + index + ']에 ' + side + ' 구간의 값 ' + sorted[index] + '을 씁니다.');
        const next = isLeft ? ++b1 : ++b2;
        const name = isLeft ? 'b1' : 'b2';
        r.write(line + 1, 'f.' + name, next, name + ' 이동', '값을 가져온 ' + side + ' 구간의 인덱스를 늘립니다.');
      }
      function advance(line) {
        r.write(line, 'f.index', ++index, '쓰기 위치 이동', '다음 임시 배열 칸으로 이동합니다.');
      }
      while (b1 <= mid && b2 <= right) {
        r.note(7, '두 구간 모두 후보 있음', '두 구간에 비교할 값이 남아 있습니다.');
        const a = data[b1], b = data[b2];
        const left = stable ? a <= b : a < b;
        const side = left ? '왼쪽' : '오른쪽';
        r.read(8, 'list.' + b1, '왼쪽 비교값 읽기', '왼쪽 후보는 ' + a + '입니다.');
        r.read(8, 'list.' + b2, '오른쪽 비교값 읽기', a + '와 ' + b + '을 비교해 ' + side +
          ' 값을 고릅니다.' + (a === b ? ' 같은 키에서는 이 사례의 비교 연산자가 순서를 정합니다.' : ''));
        copy(side, left ? 9 : 12, false);
        advance(15);
      }
      r.note(7, '두 후보 비교 종료', (b1 > mid ? '왼쪽' : '오른쪽') + ' 구간이 먼저 소진되었습니다.');
      while (b1 <= mid) { copy('왼쪽', 18, true); advance(20); }
      while (b2 <= right) { copy('오른쪽', 23, true); advance(25); }
      r.local(27, 'i', int(0), '완성된 임시 배열을 원본의 합병 범위에 되돌려 씁니다.');
      for (let i = 0; i < index; i++) {
        r.read(28, 'sorted.' + i, '임시 배열 읽기', 'sorted[' + i + ']에서 ' + sorted[i] + '을 읽습니다.');
        r.write(28, 'list.' + i, sorted[i], '원본 배열에 복사', 'list[' + i + ']에 복사합니다.');
        r.write(27, 'f.i', i + 1, '복사 위치 이동', '다음 칸으로 이동합니다.');
      }
      r.finish(29, '합병 범위가 오름차순입니다. 임시 배열과 지역 변수의 수명이 끝납니다.');
      return r.events;
    },
    expected: [
      {presetId: 'default', checks: [10, 12, 20, 27].map((v, i) => check('list.' + i, v))},
      {presetId: 'left', checks: [1, 2, 7, 9].map((v, i) => check('list.' + i, v))},
      {presetId: 'strict', checks: [2, 2, 3, 5].map((v, i) => check('list.' + i, v))},
      {presetId: 'stable', checks: [2, 2, 3, 5].map((v, i) => check('list.' + i, v))},
    ],
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else root.DSInteractive.scenario = scenario;
})(globalThis);
