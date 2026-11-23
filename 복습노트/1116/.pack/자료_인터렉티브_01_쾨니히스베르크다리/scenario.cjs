(function (root) {
  const vertices = [['A', 82, 123], ['B', 82, 206], ['C', 82, 40], ['D', 285, 123]];
  const bridges = [
    ['a', 'A', 'B', 40], ['b', 'A', 'B', -40], ['c', 'A', 'C', -40],
    ['d', 'A', 'C', 40], ['e', 'A', 'D', 0], ['f', 'B', 'D', 0],
    ['g', 'C', 'D', 0], ['h', 'C', 'D', 42],
  ];
  const topologies = {
    original: 'abcdefg',
    twoOdd: 'bcdefg',
    even: 'bcdef',
    split: 'abgh',
  };
  const int = value => ({kind: 'int', value});
  const source = {
    id: 'walk', label: '다리 건너기 의사코드', language: 'pseudocode',
    text: [
      '다리_건너기(출발점)',
      '    현재 위치의 미사용 다리를 이름순으로 고른다',
      '    다리를 건너고 순서를 기록한다',
      '    건널 수 있는 동안 반복한다',
      '    남은 다리와 도착점을 확인한다',
    ].join('\n'),
    provenance: {
      path: '자료구조_강의록_2026/Software_10_Graph.pdf', page: '3',
      sha256: 'd14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10',
      supplement: true, adjustments: 'p3의 다리 그림을 토대로 건너기 순서를 보충했어요.',
      note: '학습용 의사코드예요. 이 규칙은 가능한 경로를 모두 찾지 않고 한 번의 시도를 보여 줘요.',
    },
  };
  const inputs = [
    {key: 'layout', label: '다리 배치', type: 'enum', default: 'original', options: [
      {value: 'original', label: '다리 7개'},
      {value: 'twoOdd', label: 'a 제거'},
      {value: 'even', label: 'a·g 제거'},
      {value: 'split', label: '두 쌍 분리'},
    ]},
    {key: 'start', label: '출발점', type: 'enum', default: 'A',
      options: vertices.map(([value]) => ({value, label: value}))},
  ];
  const presets = [
    {id: 'two-odd', label: '열린 경로', input: {layout: 'twoOdd', start: 'C'}},
    {id: 'even', label: '회로', input: {layout: 'even', start: 'A'}},
    {id: 'split', label: '연결 끊김', input: {layout: 'split', start: 'A'}},
  ];
  const at = (line, label, explanation) => ({at: {sourceId: source.id, line}, label, explanation});
  const edgeId = edge => 'order.' + edge;
  function initialState({layout, start}) {
    const id = 'walk';
    const values = [['start', '출발점', 'ABCD'.indexOf(start)],
      ...[...topologies[layout]].map(edge => [edgeId(edge), `다리 ${edge}를 건넌 순서`, 0])];
    const cells = Object.fromEntries(values.map(([key, name, value]) => [
      key, {id: key, name, type: 'int', owner: id, address: '&' + key, value: int(value), lifetime: 'live'},
    ]));
    return {
      frames: {}, activeFrame: null, stdout: [],
      objects: {[id]: {id, type: '건너기 기록', storage: 'static',
        cellIds: Object.keys(cells), lifetime: 'live'}}, cells,
    };
  }
  function* generateEvents({layout, start}) {
    const unused = bridges.filter(([edge]) => topologies[layout].includes(edge));
    let current = start;
    let order = 0;
    while (true) {
      const index = unused.findIndex(([, a, b]) => a === current || b === current);
      if (index < 0) break;
      const [[edge, a, b]] = unused.splice(index, 1);
      const next = current === a ? b : a;
      yield {kind: 'read', cellId: edgeId(edge),
        ...at(2, `다리 ${edge} 고르기`, `${current}에서 건널 수 있는 미사용 다리 중 ${edge}를 골라요.`)};
      order += 1;
      yield {kind: 'write', cellId: edgeId(edge), value: int(order),
        ...at(3, `${current} → ${next}`, `다리 ${edge}를 ${order}번째로 건너 ${next}에 도착했어요.`)};
      current = next;
    }
    const result = unused.length
      ? `${current}에서 더 건널 수 없어요. 다리 ${unused.map(([edge]) => edge).join(', ')}가 남았어요.`
      : current === start
        ? `모든 다리를 한 번씩 건너 출발점 ${start}로 돌아왔어요.`
        : `모든 다리를 한 번씩 건넜어요. 출발점은 ${start}, 도착점은 ${current}예요.`;
    yield {kind: 'observe', ...at(5, '건너기 결과', result)};
  }
  const expected = [
    ['default', 'a', 1, 'g', 0], ['two-odd', 'c', 1, 'g', 6],
    ['even', 'b', 1, 'd', 5], ['split', 'a', 1, 'h', 0],
  ].map(([presetId, first, one, last, order]) => ({
    presetId, checks: [
      {step: 'step-2', cellId: edgeId(first), value: int(one)},
      {step: 'last', cellId: edgeId(last), value: int(order)},
    ],
  }));
  const scenario = {
    version: 1, id: '1116-bridges', kind: 'c-graph', title: '쾨니히스베르크 다리 건너기',
    intro: '먼저 홀수 차수인 지점을 찾고, 출발점으로 돌아올 수 있을지 예상해 보세요.',
    takeaway: '간선이 있는 정점들이 연결되어 있다면, 홀수 정점이 0개면 회로가 가능해요. 2개면 한 홀수 정점에서 다른 홀수 정점으로 가는 경로가 가능해요.',
    graph: {view: 'bridges', vertices, bridges}, sources: [source], inputs, presets,
    initialState, generateEvents, expected,
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else root.DSInteractive.scenario = scenario;
})(globalThis);
