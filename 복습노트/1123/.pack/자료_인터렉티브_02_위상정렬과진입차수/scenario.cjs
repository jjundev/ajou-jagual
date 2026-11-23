(function (root) {
  'use strict';

  const vertices = [[0, 53, 61], [1, 53, 170], [2, 180, 61],
    [3, 180, 115], [4, 180, 170], [5, 307, 115]];
  const edges = [[0, 2], [0, 3], [1, 3], [1, 4], [2, 3], [2, 5], [3, 5], [4, 5], [5, 0]];
  const ids = vertices.map(([id]) => id);
  const int = value => ({kind: 'int', value});
  const edgeCell = index => 'edge.' + index;
  const nodeCell = id => 'node.' + id;

  function initialState({setup}) {
    const entries = [
      ['candidate', '선택 정점', -1],
      ['failure', '정렬 불가', 0],
      ...ids.map(id => [nodeCell(id), id + ' 남아 있음', 1]),
      ...edges.map(([from, to], index) => [edgeCell(index), from + ' → ' + to + ' 남아 있음',
        Number(index < edges.length - 1 || setup === 'cycle')]),
    ];
    const cells = Object.fromEntries(entries.map(([id, name, value]) => [id, {
      id, name, owner: 'topo', type: 'int', address: id, value: int(value), lifetime: 'live',
    }]));
    return {frames: {}, activeFrame: null, stdout: [], cells,
      objects: {topo: {id: 'topo', type: '위상 정렬 실행 상태', storage: 'static', lifetime: 'live', cellIds: Object.keys(cells)}}};
  }

  function* generateEvents({setup}) {
    const active = new Set(edges.keys());
    if (setup !== 'cycle') active.delete(edges.length - 1);
    const remaining = new Set(ids);
    const priority = setup === 'slide' ? [1, 4, 0, 2, 3, 5] : ids;
    const event = (line, label, explanation, kind = 'observe', fields = {}) =>
      ({at: {sourceId: 'topo', line}, label, explanation, kind, ...fields});
    const write = (line, label, explanation, cellId, value) =>
      event(line, label, explanation, 'write', {cellId, value: int(value)});

    while (remaining.size) {
      const destinations = new Set([...active].map(index => edges[index][1]));
      const ready = priority.filter(v => remaining.has(v) && !destinations.has(v));
      if (!ready.length) {
        yield write(2, '사이클 때문에 정렬 불가',
          '0 → 2 → 5 → 0은 서로를 기다리는 사이클입니다. 남은 정점에 진입 차수 0인 후보가 없어 종료합니다.',
          'failure', 1);
        return;
      }
      const [v] = ready;
      yield write(3, '진입 차수 0인 정점 선택',
        '후보 ' + ready.join(', ') + ' 중 정점 ' + v + '을 고릅니다.', 'candidate', v);
      yield event(4, '정점 출력', '정점 ' + v + '을 출력 순서 뒤에 붙입니다.', 'print-int', {cellId: 'candidate'});
      for (const index of active) {
        const [from, to] = edges[index];
        if (from !== v) continue;
        const before = [...active].filter(edge => edges[edge][1] === to).length;
        active.delete(index);
        yield write(5, '나가는 간선 제거',
          from + ' → ' + to + '를 지워 정점 ' + to + '의 진입 차수를 ' + before + '에서 ' +
            (before - 1) + '로 줄입니다.', edgeCell(index), 0);
      }
      remaining.delete(v);
      yield write(6, '출력한 정점 제거', '정점 ' + v + '을 남은 그래프에서 지웁니다.', nodeCell(v), 0);
    }
    yield event(7, '위상 정렬 완료', '모든 정점을 출력했습니다. 각 화살표의 출발점이 도착점보다 앞에 있는지 확인하세요.');
  }

  const scenario = {
    version: 1, id: 'topological-sort-1123', title: '위상 정렬과 진입 차수', kind: 'c-graph',
    intro: '정점 옆 숫자는 남은 그래프에서 들어오는 간선 수입니다. 진입 차수가 0인 정점부터 출력합니다.',
    takeaway: '진입 차수 0인 후보가 여러 개라면 여러 위상 정렬 순서가 나올 수 있습니다. 정점이 남았는데 후보가 없으면 사이클이 있어 위상 정렬을 완성할 수 없습니다.',
    sources: [{
      id: 'topo', label: '위상 정렬', language: 'pseudocode',
      provenance: {
        path: '자료구조_강의록_2026/Software_10_Graph.pdf',
        sha256: 'd14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10',
        page: 37, section: '선수 과목 그래프와 정점 제거 (pp.35–37)',
        supplement: true, adjustments: '슬라이드의 비어 있는 반복 상한을 남은 정점 조건으로 명시하고 간선과 정점 제거를 나누었습니다.',
      },
      text: [
        '정점이 남아 있는 동안 반복',
        '  진입 차수 0인 정점이 없으면 정렬 불가로 종료',
        '  진입 차수 0인 정점 v 선택',
        '  v 출력',
        '  v에서 나가는 각 간선을 지우고 도착점의 진입 차수를 1 감소',
        '  남은 그래프에서 v 제거',
        '위상 정렬 완료',
      ].join('\n'),
    }],
    inputs: [{key: 'setup', label: '선수 과목 그래프', type: 'enum', default: 'ascending', options: [
      {value: 'ascending', label: '번호순 선택'},
      {value: 'slide', label: '강의 그림 순서'},
      {value: 'cycle', label: '사이클 추가'},
    ]}],
    presets: [
      {id: 'slide', label: '강의 그림 순서', input: {setup: 'slide'}},
      {id: 'cycle', label: '사이클 추가', input: {setup: 'cycle'}},
    ],
    initialState, generateEvents,
    expected: [['default', 0], ['slide', 0], ['cycle', 1]].map(([presetId, value]) => ({
      presetId, checks: [{step: 'last', cellId: 'failure', value: int(value)}],
    })),
    graph: {view: 'topo', vertices, edges},
  };

  if (typeof module === 'object' && module.exports) module.exports = scenario;
  else root.DSInteractive.scenario = scenario;
})(globalThis);
