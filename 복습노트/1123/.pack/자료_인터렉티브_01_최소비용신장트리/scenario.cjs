(function (root) {
  'use strict';

  const vertices = [
    ['a', 78, 36], ['b', 271, 36], ['c', 312, 112], ['d', 248, 191],
    ['e', 110, 191], ['f', 46, 112], ['g', 181, 106],
  ];
  const edges = [
    ['a', 'f', 10], ['c', 'd', 12], ['b', 'g', 15], ['b', 'c', 16],
    ['d', 'g', 18], ['d', 'e', 22], ['e', 'g', 25], ['e', 'f', 27], ['a', 'b', 29],
  ];
  const letters = vertices.map(([id]) => id);
  const int = value => ({kind: 'int', value});
  const edgeCell = index => 'edge.' + index;
  const weight = (index, input) => index === 8 && input.setup === 'tie' ? 27 : edges[index][2];
  const edgeLabel = (index, input) => edges[index].slice(0, 2).join('–') + '(' + weight(index, input) + ')';
  const provenance = (page, section, adjustments) => ({
    path: '자료구조_강의록_2026/Software_10_Graph.pdf',
    sha256: 'd14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10',
    page, section, supplement: true, adjustments,
  });

  function initialState() {
    const values = {candidate: -1, ...Object.fromEntries(edges.map((_, i) => [edgeCell(i), 0]))};
    const names = {candidate: '검사 간선', ...Object.fromEntries(edges.map(([a, b], i) => [edgeCell(i), a + '–' + b + ' 상태']))};
    const cells = Object.fromEntries(Object.entries(values).map(([id, value]) => [id, {
      id, name: names[id], owner: 'mst', type: 'int', address: id, value: int(value), lifetime: 'live',
    }]));
    return {frames: {}, activeFrame: null, stdout: [], cells,
      objects: {mst: {id: 'mst', type: '신장 트리 실행 상태', storage: 'static', lifetime: 'live', cellIds: Object.keys(cells)}}};
  }

  function* generateEvents(input) {
    const {mode} = input;
    const ranked = edges.map((_, index) => index).sort((i, j) => weight(i, input) - weight(j, input) || i - j);
    const parent = Object.fromEntries(letters.map(v => [v, v]));
    const find = v => parent[v] === v ? v : find(parent[v]);
    const inside = new Set(['a']);
    const work = (line, label, explanation, cellId, value) => ({
      at: {sourceId: mode, line}, label, explanation, kind: cellId ? 'write' : 'observe',
      ...(cellId && {cellId, value: int(value)}),
    });
    let chosen = 0;
    if (mode === 'kruskal') {
      for (const index of ranked) {
        const [a, b] = edges[index];
        const edge = edgeLabel(index, input);
        yield work(3, '다음 간선 확인', edge + '을 검사합니다.', 'candidate', index);
        const left = find(a);
        const right = find(b);
        yield work(4, '두 집합 비교', left === right
          ? a + '와 ' + b + '는 같은 연결 요소에 있습니다. 이미 두 정점 사이에 경로가 있습니다.'
          : a + '와 ' + b + '는 서로 다른 연결 요소에 있습니다.');
        if (left === right) {
          yield work(6, '사이클로 제외', edge + '을 추가하면 기존 경로가 닫혀 사이클이 생깁니다.', edgeCell(index), -1);
          continue;
        }
        parent[right] = left;
        yield work(5, '간선 채택 · 집합 합치기', edge + '을 채택하고 두 연결 요소를 합칩니다.', edgeCell(index), ++chosen);
        if (chosen === letters.length - 1) break;
      }
      yield work(7, '신장 트리 완성', '정점 7개를 잇는 간선 6개가 모였습니다. 나머지 간선은 검사하지 않습니다.');
      return;
    }

    while (inside.size < letters.length) {
      const boundary = ranked.filter(index => {
        const [a, b] = edges[index];
        return inside.has(a) !== inside.has(b);
      });
      // In ties, scan from the alphabetically first vertex already in the tree.
      const oriented = index => {
        const [a, b] = edges[index];
        return inside.has(a) ? a + b : b + a;
      };
      boundary.sort((i, j) => weight(i, input) - weight(j, input) || oriented(i).localeCompare(oriented(j), 'en'));
      const index = boundary[0];
      const [a, b] = edges[index];
      const next = inside.has(a) ? b : a;
      const edge = edgeLabel(index, input);
      yield work(3, '경계에서 최저 비용 찾기', '트리 안팎을 잇는 후보 중 ' + edge + '을 고릅니다.', 'candidate', index);
      inside.add(next);
      yield work(4, '정점과 간선 추가', edge + '과 바깥 정점 ' + next + '를 트리에 넣습니다.', edgeCell(index), ++chosen);
    }
    yield work(5, '신장 트리 완성', '정점이 모두 트리에 들어왔습니다. 채택한 간선의 가중치 합을 확인하세요.');
  }

  const presets = [
    {id: 'lecture-prim', label: '강의 예제 · Prim', input: {setup: 'lecture', mode: 'prim'}},
    {id: 'tie-kruskal', label: '동률 · Kruskal', input: {setup: 'tie', mode: 'kruskal'}},
    {id: 'tie-prim', label: '동률 · Prim', input: {setup: 'tie', mode: 'prim'}},
  ];
  const scenario = {
    version: 1, id: 'mst-1123', title: '최소 비용 신장 트리', kind: 'c-graph',
    intro: 'Kruskal과 Prim을 바꿔 가며 다음 후보가 정해지는 범위를 비교하세요.',
    takeaway: 'Kruskal은 전체 간선을 가중치순으로 검사하고, Prim은 현재 트리와 바깥을 잇는 간선에서 고릅니다. 연결된 가중 무방향 그래프에서 둘 다 최소 비용을 구합니다. 동률 입력에서 서로 다른 신장 트리의 총비용이 같은지 비교하세요.',
    sources: [
      {id: 'kruskal', label: 'Kruskal', language: 'pseudocode',
        provenance: provenance(22, '가중치 정렬과 union-find (pp.22–24)', '단계별 집합 비교와 제외를 분리했습니다. 동률이면 강의 표의 간선 순서를 따릅니다.'),
        text: [
          '가중치순으로 간선 정렬. T ← ∅, 각 정점을 개별 집합으로 초기화',
          '간선이 |V|−1개 모일 때까지 반복',
          '  e=(u,v) ← 미검사 간선 중 첫 번째',
          '  find(u)와 find(v)를 비교',
          '  서로 다르면 e를 T에 넣고 두 집합을 union',
          '  같은 집합이면 e를 제외',
          'T 반환',
        ].join('\n')},
      {id: 'prim', label: 'Prim', language: 'pseudocode',
        provenance: provenance(26, '시작 정점과 경계 간선 (pp.25–27)', '추가 간선 수도 |V|−1개가 되면 종료합니다. 선택한 간선을 함께 기록하고 동률이면 트리 안 정점, 바깥 정점 순으로 비교합니다.'),
        text: [
          'V_T ← {a}, T ← ∅',
          '모든 정점이 V_T에 포함될 때까지 반복',
          '  e=(u,v) ← V_T 안의 u에서 바깥 v로 가는 최저 비용 간선',
          '  v를 V_T에 넣고 e를 T에 추가',
          'T 반환',
        ].join('\n')},
    ],
    inputs: [
      {key: 'setup', label: '입력 그래프', type: 'enum', default: 'lecture',
        options: [{value: 'lecture', label: '강의 예제'}, {value: 'tie', label: '동률 예제'}]},
      {key: 'mode', label: '알고리즘', type: 'enum', default: 'kruskal',
        options: [{value: 'kruskal', label: 'Kruskal'}, {value: 'prim', label: 'Prim'}]},
    ],
    presets, initialState, generateEvents, expected: [
      ['default', [1, 2, 3, 4, -1, 5, -1, 6, 0]],
      ['lecture-prim', [1, 4, 6, 5, 0, 3, 0, 2, 0]],
      ['tie-kruskal', [1, 2, 3, 4, -1, 5, -1, 6, 0]],
      ['tie-prim', [1, 5, 3, 4, 0, 6, 0, 0, 2]],
    ].map(([presetId, values]) => ({
      presetId, checks: values.map((value, index) => ({step: 'last', cellId: edgeCell(index), value: int(value)})),
    })),
    graph: {view: 'mst', vertices, edges, weight},
  };

  if (typeof module === 'object' && module.exports) module.exports = scenario;
  else root.DSInteractive.scenario = scenario;
})(globalThis);
