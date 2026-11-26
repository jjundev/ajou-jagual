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
    lecture: [5, 3, 8, 4, 9, 1, 6, 2, 7],
    equal: [5, 5, 8, 5, 9, 1, 6, 5, 7],
    smallest: [1, 2, 3, 4, 5, 6, 7, 8, 9],
    largest: [9, 8, 7, 6, 5, 4, 3, 2, 1],
  };
  const options = [
    {value: 'lecture', label: '강의 예제'},
    {value: 'equal', label: '같은 키 포함'},
    {value: 'smallest', label: '피벗이 최솟값'},
    {value: 'largest', label: '피벗이 최댓값'},
  ];
  const length = examples.lecture.length;
  const scenario = {
    version: 1, id: '1126-quick-partition', kind: 'c-memory',
    title: '퀵 정렬의 피벗 분할',
    intro: '맨 앞의 값을 피벗으로 삼습니다. low와 high는 어디에서 멈출까요?',
    takeaway: '두 인덱스가 만나거나 교차할 때 high 자리에 피벗이 놓이는 과정을 확인하세요.',
    sources: [
  {
    "id": "partition",
    "label": "S9 p26 partition",
    "language": "c",
    "text": "int partition(int list[], int left, int right)\n{\n    int pivot, temp;\n    int low, high;\n\n    low = left;\n    high = right + 1;\n    pivot = list[left];\n    do {\n        do\n            low++;\n        while (low <= right && list[low] < pivot);\n        do\n            high--;\n        while (high >= left && list[high] > pivot);\n        if (low < high) SWAP(list[low], list[high], temp);\n    } while (low < high);\n\n    SWAP(list[left], list[high], temp);\n    return high;\n}",
    "provenance": {
      "path": "자료구조_강의록_2026/Software_9_Sorting.pdf",
      "sha256": "f24fa0f39ec39b47dd942eac1a1ab81fdeb592fb608c0d6248a4299266827cac",
      "page": 26,
      "section": "p25 스캔 그림과 p26 구현, STT Part 08",
      "adjustments": "p26 C의 공백 정리. SWAP은 p10의 3대입 매크로를 검산에 추가한다. p26 구현은 강의에서 다음 시간에 예고했다.",
      "supplement": false
    }
  }
],
    inputs: [{key: 'example', label: '입력 배열', type: 'enum', default: 'lecture', options}],
    presets: options.slice(1).map(({value, label}) => ({id: value, label, input: {example: value}})),
    array: {
      heading: '분할 중인 배열',
      rows: [row('list', 'list', length)],
      markers: [
        {cellId: 'f.low', label: 'L', row: 0},
        {cellId: 'f.high', label: 'H', row: 0},
        {cellId: 'main.q', label: 'q', row: 0},
      ],
      watch: [watch('low', '오른쪽으로 스캔'), watch('high', '왼쪽으로 스캔'),
        watch('pivot', '비교 기준'), watch('q', '확정된 피벗 위치', 'main.q')],
      title: '분할 결과',
      result(step) {
        const q = value(step, 'main.q');
        return q === undefined ? '피벗 위치 확정 전'
          : 'q = ' + q + ' · 다음 구간 ' + (q ? '[0, ' + (q - 1) + ']' : '공백') +
            ' / ' + (q < length - 1 ? '[' + (q + 1) + ', ' + (length - 1) + ']' : '공백');
      },
    },
    initialState({example}) {
      const state = start('partition', examples[example], {left: 0, right: length - 1});
      state.cells['main.q'] = cell('main.q', 'q', 'main', empty);
      state.frames.main.cellIds.push('main.q');
      return state;
    },
    generateEvents({example}) {
      const data = examples[example].slice(), right = data.length - 1, pivot = data[0];
      const r = recorder('partition');
      r.local(3, 'pivot', empty, '피벗 값을 담을 변수를 선언합니다.');
      r.local(3, 'temp', empty, '교환 중 원래 값을 보관할 임시 변수를 선언합니다.');
      r.local(4, 'low', empty, '오른쪽으로 움직일 인덱스를 선언합니다.');
      r.local(4, 'high', empty, '왼쪽으로 움직일 인덱스를 선언합니다.');
      let low = 0, high = right + 1;
      r.read(6, 'f.left', '왼쪽 경계 읽기', 'left를 읽습니다.');
      r.write(6, 'f.low', low, 'low 시작 위치', '먼저 증가하므로 low는 왼쪽 경계에서 시작합니다.');
      r.read(7, 'f.right', '오른쪽 경계 읽기', 'right를 읽습니다.');
      r.write(7, 'f.high', high, 'high 시작 위치', '먼저 감소하므로 high는 오른쪽 경계 다음에서 시작합니다.');
      r.read(8, 'list.0', '첫 원소 읽기', '배열 맨 앞에서 피벗 값을 읽습니다.');
      r.write(8, 'f.pivot', pivot, '피벗 값 저장', '피벗 값 ' + pivot + '을 저장합니다.');
      function swap(line, a, b) {
        const left = data[a], right = data[b];
        r.read(line, 'list.' + a, '첫 값 읽기', 'list[' + a + ']에서 ' + left + '을 읽습니다.');
        r.write(line, 'f.temp', left, 'temp에 보관', '첫 값 ' + left + '을 임시 변수에 보관합니다.');
        r.read(line, 'list.' + b, '둘째 값 읽기', 'list[' + b + ']에서 ' + right + '을 읽습니다.');
        r.write(line, 'list.' + a, right, '첫 칸에 쓰기', 'list[' + a + ']에 ' + right + '을 씁니다.');
        r.read(line, 'f.temp', 'temp 읽기', '보관했던 첫 값을 다시 읽습니다.');
        r.write(line, 'list.' + b, left, '둘째 칸에 쓰기', 'list[' + b + ']에 ' + left + '을 씁니다.');
        [data[a], data[b]] = [right, left];
      }
      do {
        do {
          low++;
          r.write(11, 'f.low', low, 'low 한 칸 이동', 'low를 ' + low + '로 증가시킵니다.');
          if (low <= right) {
            const pass = data[low] < pivot;
            r.read(12, 'list.' + low, 'low 쪽 비교', data[low] + (pass ? ' < ' : ' ≥ ') + pivot +
              (pass ? '이므로 low가 더 오른쪽으로 갑니다.' : '이므로 low가 멈춥니다.'));
          } else {
            r.note(12, 'low 경계 도달', 'low가 right보다 커서 배열 원소를 읽지 않습니다.');
          }
        } while (low <= right && data[low] < pivot);
        do {
          high--;
          r.write(14, 'f.high', high, 'high 한 칸 이동', 'high를 ' + high + '로 감소시킵니다.');
          const pass = data[high] > pivot;
          r.read(15, 'list.' + high, 'high 쪽 비교', data[high] + (pass ? ' > ' : ' ≤ ') + pivot +
            (pass ? '이므로 high가 더 왼쪽으로 갑니다.' : '이므로 high가 멈춥니다.'));
        } while (high >= 0 && data[high] > pivot);
        if (low < high) {
          r.note(16, '교환 조건 성립', 'low < high이므로 두 정지 위치의 값을 교환합니다.');
          swap(16, low, high);
        } else {
          r.note(16, '교환 조건 불성립', '두 인덱스가 만나거나 교차해 정지 위치끼리의 교환을 건너뜁니다.');
        }
        r.note(17, '반복 조건 확인', low < high ? 'low < high이므로 양쪽 스캔을 반복합니다.'
          : 'low ≥ high이므로 스캔이 끝납니다.');
      } while (low < high);
      r.note(19, '피벗의 자리 결정', high === 0 ? 'high가 맨 앞이므로 피벗은 제자리에서 교환됩니다.'
        : '맨 앞의 피벗을 high가 가리키는 칸과 바꿉니다.');
      swap(19, 0, high);
      r.read(20, 'f.high', '반환할 인덱스 읽기', '확정된 위치 high를 읽습니다.');
      r.finish(20, '호출자에게 q = ' + high + '를 돌려줍니다. 이후에는 q를 제외한 두 구간을 정렬합니다.',
        {cellId: 'main.q', value: int(high)});
      return r.events;
    },
    expected: [
      {presetId: 'default', checks: [check('main.q', 4), check('list.4', 5)]},
      {presetId: 'equal', checks: [check('main.q', 3), check('list.3', 5)]},
      {presetId: 'smallest', checks: [check('main.q', 0), check('list.0', 1)]},
      {presetId: 'largest', checks: [check('main.q', 8), check('list.8', 9)]},
    ],
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else root.DSInteractive.scenario = scenario;
})(globalThis);
