(function (root) {
  const matrices = {
    g3: [[0, 1, 0], [1, 0, 1], [0, 0, 0]],
    empty: [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
  };
  const vertices = [['0', 55, 83], ['1', 180, 83], ['2', 305, 83]];
  const int = value => ({kind: 'int', value});
  const cellId = (from, to) => `m.${from}.${to}`;
  const source = {
    id: 'degree', label: '차수 계산 · 보충 C', language: 'c',
    text: `enum { N = 3 };

void degrees(int m[N][N], int v, int sum[2])
{
    for (int i = 0; i < N; ++i)
        sum[0] += m[v][i];

    for (int i = 0; i < N; ++i)
        sum[1] += m[i][v];
}`,
    provenance: {
      path: '자료구조_강의록_2026/Software_10_Graph.pdf', page: '6–7, 9',
      sha256: 'd14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10',
      supplement: true, adjustments: 'G3의 인접 행렬을 사용하고 문제설명 P9의 두 반복문을 한 함수에 담았어요.',
      note: 'sum[0]은 진출 차수, sum[1]은 진입 차수예요. 호출자가 두 칸을 0으로 초기화하고, 화면은 반복문의 읽기와 더하기를 나누어 보여 줘요.',
    },
  };
  const inputs = [
    {key: 'matrix', label: '그래프', type: 'enum', default: 'g3', options: [
      {value: 'g3', label: '강의 G3'}, {value: 'empty', label: '간선 0개'},
    ]},
    {key: 'vertex', label: '정점 v', type: 'integer', min: 0, max: 2, default: 1},
  ];
  const presets = [
    {id: 'sink', label: 'G3 · 정점 2', input: {matrix: 'g3', vertex: 2}},
    {id: 'reciprocal', label: 'G3 · 정점 0', input: {matrix: 'g3', vertex: 0}},
    {id: 'empty', label: '간선 0개', input: {matrix: 'empty', vertex: 1}},
  ];
  const at = (line, label, explanation) => ({at: {sourceId: source.id, line}, label, explanation});
  function initialState({matrix, vertex}) {
    const values = [['v', 'v', vertex], ['out', 'sum[0] · 진출', 0], ['in', 'sum[1] · 진입', 0]];
    for (const [from, row] of matrices[matrix].entries()) {
      for (const [to, value] of row.entries()) values.push([cellId(from, to), `m[${from}][${to}]`, value]);
    }
    const cells = Object.fromEntries(values.map(([id, name, value]) => [
      id, {id, name, type: 'int', owner: 'degree', address: '&' + id, value: int(value), lifetime: 'live'},
    ]));
    return {frames: {}, activeFrame: null, stdout: [],
      objects: {degree: {id: 'degree', type: '차수 계산', storage: 'static',
        cellIds: Object.keys(cells), lifetime: 'live'}}, cells};
  }
  function* generateEvents({matrix, vertex}) {
    const a = matrices[matrix];
    const sums = [];
    for (const [axis, id, name, line] of [
      ['row', 'out', '진출 차수', 6], ['column', 'in', '진입 차수', 9],
    ]) {
      let sum = 0;
      for (const i of a.keys()) {
        const [from, to] = axis === 'row' ? [vertex, i] : [i, vertex];
        const bit = a[from][to];
        const term = `m[${from}][${to}]`;
        const edge = `${from} → ${to}`;
        yield {kind: 'read', cellId: cellId(from, to),
          ...at(line, `${term} 읽기`, `${term} = ${bit}이에요. ${edge} 간선이 ${bit ? '있어요' : '없어요'}.`)};
        const previous = sum;
        sum += bit;
        yield {kind: 'write', cellId: id, value: int(sum),
          ...at(line, `${name}에 ${bit} 더하기`, `${name}의 누적값이 ${previous} + ${bit} = ${sum}이에요.`)};
      }
      sums.push(sum);
    }
    yield {kind: 'observe', ...at(10, '행과 열 비교',
      `${vertex}행의 합은 ${sums[0]}, ${vertex}열의 합은 ${sums[1]}이에요. 두 합을 구하는 데 각각 3칸을 읽었어요.`)};
  }
  const expected = [
    ['default', 2, 1], ['sink', 0, 1], ['reciprocal', 1, 1], ['empty', 0, 0],
  ].map(([presetId, out, incoming]) => ({
    presetId, checks: [
      {step: 'last', cellId: 'out', value: int(out)},
      {step: 'last', cellId: 'in', value: int(incoming)},
    ],
  }));
  const scenario = {
    version: 1, id: '1116-directed-degree', kind: 'c-graph', title: '인접 행렬로 진출·진입 차수 읽기',
    intro: '정점 v에서 나가는 화살표와 들어오는 화살표를 각각 몇 개로 예상하나요?',
    takeaway: 'm[i][j]에서 행 i는 출발점, 열 j는 도착점이에요. 출발점을 고정한 행은 진출 차수, 도착점을 고정한 열은 진입 차수를 줘요.',
    graph: {view: 'degree', vertices, rowLine: 6, columnLine: 9}, sources: [source], inputs, presets,
    initialState, generateEvents, expected,
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else root.DSInteractive.scenario = scenario;
})(globalThis);
