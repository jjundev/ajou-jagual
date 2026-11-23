(function () {
  'use strict';
  const sources = [
    {
      "id": "dfs",
      "label": "dfs_mat",
      "language": "c",
      "text": "void dfs_mat(GraphType *g, int v)\n{\n  visited[v] = 1;\n  printf(\"%d \", v);\n  for (int w = 0; w < N; w++) {\n    if (g->adj_mat[v][w] && !visited[w]) {\n      parent[w] = v;\n      dfs_mat(g, w);\n    }\n  }\n}",
      "provenance": {
        "path": "자료구조_강의록_2026/Software_10_Graph.pdf",
        "sha256": "d14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10",
        "page": 14,
        "supplement": true,
        "adjustments": "TRUE를 1로 쓰고 정점 수 N=5를 고정했습니다. 발견 간선을 parent[]에 기록합니다.",
        "note": "강의록 p14 기반 보충 C · TRUE를 1로 쓰고 정점 수 N=5를 고정했습니다. 발견 간선을 parent[]에 기록합니다."
      }
    },
    {
      "id": "bfs",
      "label": "bfs_mat",
      "language": "c",
      "text": "void bfs_mat(GraphType *g, int v)\n{\n  int w, q[N];\n  int head = 0, tail = 0;\n  visited[v] = 1;\n  printf(\"%d \", v);\n  q[tail] = v; tail++;\n  while (head < tail) {\n    v = q[head]; head++;\n    for (w = 0; w < N; w++) {\n      if (g->adj_mat[v][w] && !visited[w]) {\n        visited[w] = 1;\n        parent[w] = v;\n        printf(\"%d \", w);\n        q[tail] = w; tail++;\n      }\n    }\n  }\n}",
      "provenance": {
        "path": "자료구조_강의록_2026/Software_10_Graph.pdf",
        "sha256": "d14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10",
        "page": 16,
        "supplement": true,
        "adjustments": "QueueType 연산을 길이 5의 배열과 head·tail로 펼쳤습니다. 발견 간선을 parent[]에 기록합니다.",
        "note": "강의록 p16 기반 보충 C · QueueType 연산을 길이 5의 배열과 head·tail로 펼쳤습니다. 발견 간선을 parent[]에 기록합니다."
      }
    }
  ];

  const size = 5;
  const vertices = [0, 1, 2, 3, 4];
  const int = value => ({kind: 'int', value});
  const pointer = target => ({kind: 'pointer', target});
  const cell = (owner, field, value, name = field, type = 'int') => {
    const id = `${owner}.${field}`;
    return {id, owner, name, address: id, type, value, lifetime: 'live'};
  };
  const address = (v, w) => `graph.a.${v}.${w}`;
  const visited = v => `graph.visited.${v}`;
  const parent = v => `graph.parent.${v}`;
  const splitEdges = [[0, 1], [0, 2], [3, 4]];
  const matrixFor = edges => vertices.map(v => vertices.map(w => Number(edges.some(
    ([a, b]) => a === v && b === w || a === w && b === v,
  ))));

  function initialState(matrix, components = false) {
    const entries = vertices.flatMap(v => vertices.map(w =>
      cell('graph', `a.${v}.${w}`, int(matrix[v][w]), `adj_mat[${v}][${w}]`)));
    const globals = [];
    const staticCell = (field, value, name) => ({...cell('graph', field, int(value), name), owner: 'globals'});
    for (const v of vertices) {
      globals.push(staticCell(`visited.${v}`, 0, `visited[${v}]`));
      globals.push(staticCell(`parent.${v}`, -1, `parent[${v}]`));
    }
    if (components) globals.push(staticCell('count', 0, 'count'));

    return {
      frames: {}, activeFrame: null, stdout: [],
      objects: {
        graph: {id: 'graph', type: 'GraphType', storage: 'static', lifetime: 'live', cellIds: entries.map(c => c.id)},
        globals: {id: 'globals', type: '전역 탐색 상태', storage: 'static', lifetime: 'live', cellIds: globals.map(c => c.id)},
      },
      cells: Object.fromEntries([...entries, ...globals].map(c => [c.id, c])),
    };
  }

  function runtime(matrix) {
    const marked = vertices.map(() => 0);
    let sequence = 0;
    const events = [];
    const makeEvent = (sourceId, line, kind, label, explanation, fields) => {
      events.push({kind, at: {sourceId, line}, label, explanation, ...fields});
    };
    const writer = sourceId => (line, kind, label, explanation, fields) =>
      makeEvent(sourceId, line, kind, label, explanation, fields);

    function enter(sourceId, functionId, v, caller) {
      const id = `${sourceId}-${++sequence}`;
      const out = writer(sourceId);
      const callAt = caller?.at ?? {sourceId, line: 1};
      const atCall = writer(callAt.sourceId);
      const label = v === undefined ? functionId + '()' : `${functionId}(${v})`;
      atCall(callAt.line, 'call', '호출 공간 생성', `${label} 호출에 쓸 저장 공간을 만듭니다.`,
        {frame: {id, functionId, callSite: callAt, cellIds: [], lifetime: 'live'}});
      const g = pointer('graph.a.0.0');
      atCall(callAt.line, 'bind', '그래프 주소 전달', '매개변수 g에 그래프의 주소 값을 복사합니다.',
        {cell: cell(id, 'g', g, 'g', 'GraphType *'), value: g, fromCellId: caller && `${caller.id}.g`});
      if (v !== undefined) {
        atCall(callAt.line, 'bind', '정점 번호 전달', `매개변수 v에 정점 번호 ${v} 값을 복사합니다.`,
          {cell: cell(id, 'v', int(v)), value: int(v), fromCellId: caller?.argument});
      }
      out(1, 'enter', '함수 진입', `${label} 실행을 시작합니다.`, {frameId: id});
      return id;
    }

    function mark(out, line, v, tag) {
      marked[v] = tag;
      out(line, 'write', '방문 표시', `visited[${v}]를 ${tag}(으)로 표시합니다.`,
        {cellId: visited(v), value: int(tag)});
    }

    function print(out, line, v, cellId) {
      out(line, 'print-int', '정점 출력', `정점 번호 ${v} 값을 출력합니다.`, {cellId});
    }

    function scan(out, id, start, condition, v, visit, existingW) {
      const wCell = existingW ?? cell(id, 'w', int(0));
      const setup = `인접 행렬의 ${v}행을 w = 0부터 검사합니다.`;
      if (existingW) out(start, 'write', '행 검사 시작', setup, {cellId: wCell.id, value: int(0)});
      else out(start, 'declare', '행 검사 시작', setup, {cell: wCell});
      for (const w of vertices) {
        const adjacent = matrix[v][w];
        out(condition, 'read', adjacent ? '간선 확인' : '간선 없음',
          `adj_mat[${v}][${w}] = ${adjacent}. ` +
          (adjacent ? `이어서 visited[${w}]를 확인합니다.` : `&&의 왼쪽이 0이므로 visited[${w}]를 읽지 않습니다.`),
          {cellId: address(v, w), memberOf: `${id}.g`});
        if (adjacent) {
          const canVisit = marked[w] === 0;
          out(condition, 'read', canVisit ? '미방문 정점' : '이미 방문한 정점',
            `visited[${w}] = ${marked[w]}. ` +
            (canVisit ? `정점 ${w}에서 방문 처리를 시작합니다.` : '발견 간선을 추가하거나 다시 방문하지 않습니다.'),
            {cellId: visited(w)});
          if (canVisit) visit(w, wCell.id);
        }
        out(start, 'write', '다음 열로 이동', `w가 ${w + 1}이 됩니다.`, {cellId: wCell.id, value: int(w + 1)});
      }
      out(start, 'read', '행 검사 종료', `w = ${size}이므로 이 행의 반복을 끝냅니다.`, {cellId: wCell.id});
    }

    function discover(out, line, v, w) {
      out(line, 'write', '발견 간선 기록', `정점 ${w}의 발견 간선 (${v}, ${w})을 기록합니다.`,
        {cellId: parent(w), value: int(v)});
    }

    function dfs(v, tag, caller) {
      const out = writer('dfs');
      const id = enter('dfs', 'dfs_mat', v, caller);
      mark(out, 3, v, tag);
      print(out, 4, v, `${id}.v`);
      scan(out, id, 5, 6, v, (w, argument) => {
        discover(out, 7, v, w);
        dfs(w, tag, {id, argument, at: {sourceId: 'dfs', line: 8}});
      });
      const back = !caller ? '시작 호출을 마쳐 DFS가 끝납니다.' :
        caller.at.sourceId === 'dfs' ? '부모 호출로 돌아가 이어서 w를 증가시킵니다.' :
          '바깥 반복문으로 돌아가 이어서 i를 증가시킵니다.';
      out(11, 'return', 'DFS 반환', `dfs_mat(${v}) 반환. ${back}`, {frameId: id});
    }

    return {events, marked, writer, enter, mark, print, scan, discover, dfs};
  }

  function finalChecks(values, count) {
    const checks = values.map((value, v) => ({step: 'last', cellId: visited(v), value: int(value)}));
    if (count !== undefined) checks.push({step: 'last', cellId: 'graph.count', value: int(count)});
    return checks;
  }

  const lectureEdges = [[0, 1], [0, 2], [0, 4], [1, 2], [2, 3], [2, 4], [3, 4]];
  const setups = [
    {value: 'lecture-0', label: '강의 그래프 · 0번 출발', edges: lectureEdges, start: 0},
    {value: 'lecture-3', label: '강의 그래프 · 3번 출발', edges: lectureEdges, start: 3},
    {value: 'split-0', label: '분리 그래프 · 0번 출발', edges: splitEdges, start: 0},
  ];
  const modes = [{value: 'dfs', label: 'DFS'}, {value: 'bfs', label: 'BFS'}];
  const allCases = modes.flatMap(mode => setups.map(setup => ({
    id: `${mode.value}-${setup.value}`, label: `${mode.label} · ${setup.label}`,
    input: {mode: mode.value, setup: setup.value},
  })));
  const setupFor = input => setups.find(setup => setup.value === input.setup);

  function bfs(rt, start) {
    const out = rt.writer('bfs');
    const id = rt.enter('bfs', 'bfs_mat', start);
    const queue = [];
    const slot = i => `${id}.q.${i}`;
    const set = (line, label, explanation, cellId, value) =>
      out(line, 'write', label, explanation, {cellId, value: int(value)});
    const wCell = cell(id, 'w', {kind: 'uninitialized'});
    out(3, 'declare', '열 변수 선언', '인접 행렬의 열 번호를 담을 w를 선언합니다.', {cell: wCell});
    for (const i of vertices) {
      out(3, 'declare', '큐 배열 선언', `큐의 q[${i}] 칸을 확보합니다.`,
        {cell: cell(id, `q.${i}`, {kind: 'uninitialized'}, `q[${i}]`)});
    }
    const headCell = cell(id, 'head', int(0));
    const tailCell = cell(id, 'tail', int(0));
    for (const index of [headCell, tailCell]) {
      out(4, 'declare', '빈 큐 준비', `${index.name}를 0으로 초기화합니다.`, {cell: index});
    }

    function enqueue(line, v) {
      const tail = queue.length;
      queue.push(v);
      set(line, '큐에 정점 저장', `q[${tail}]에 정점 번호 ${v} 값을 씁니다.`, slot(tail), v);
      set(line, '큐 뒤에 추가', `tail이 ${tail + 1}이 되면서 큐에 정점 ${v} 추가가 끝납니다.`, tailCell.id, tail + 1);
    }

    rt.mark(out, 5, start, 1);
    rt.print(out, 6, start, `${id}.v`);
    enqueue(7, start);
    for (let head = 0; head < queue.length; head++) {
      const v = queue[head];
      out(8, 'observe', '큐에 남은 정점 확인', `head = ${head}, tail = ${queue.length}. 큐가 비어 있지 않습니다.`);
      out(9, 'read', '큐 앞 정점 읽기', `q[${head}]에 저장된 정점 번호 ${v} 값을 읽습니다.`, {cellId: slot(head)});
      set(9, '현재 정점 갱신', `큐 앞에서 읽은 정점 번호 ${v} 값을 v에 대입합니다.`, `${id}.v`, v);
      set(9, '큐 앞 정점 꺼내기', `head가 ${head + 1}이 되면서 큐에서 정점 ${v} 제거가 끝납니다.`, headCell.id, head + 1);
      rt.scan(out, id, 10, 11, v, (w, sourceCellId) => {
        rt.mark(out, 12, w, 1);
        rt.discover(out, 13, v, w);
        rt.print(out, 14, w, sourceCellId);
        enqueue(15, w);
      }, wCell);
    }
    out(8, 'observe', '큐가 비었음', `head와 tail이 ${queue.length}로 같아서 반복을 끝냅니다.`);
    out(19, 'return', 'BFS 반환', '큐를 모두 처리했습니다. 시작 정점에서 닿은 정점의 출력과 발견 간선을 확인해 보세요.',
      {frameId: id});
  }

  const scenario = {
    version: 1, id: 'graph-traversal-1119', kind: 'c-graph', title: 'DFS와 BFS의 실행',
    intro: 'DFS 또는 BFS를 고르고 실행해 보세요. 같은 그래프에서 호출 스택과 큐가 다음 정점을 어떻게 정하는지 비교할 수 있습니다.',
    takeaway: 'DFS는 미방문 이웃에서 즉시 재귀 호출합니다. BFS는 미방문 이웃을 방문 표시하고 큐에 넣어, 먼저 들어온 정점부터 꺼냅니다.',
    graph: {positions: [[95, 40], [38, 109], [95, 180], [194, 125], [310, 109]]},
    sources,
    inputs: [
      {key: 'mode', label: '탐색 방법', type: 'enum', default: 'dfs', options: modes},
      {key: 'setup', label: '그래프와 시작점', type: 'enum', default: 'lecture-0',
        options: setups.map(({value, label}) => ({value, label}))},
    ],
    presets: allCases.slice(1),
    expected: allCases.map(({id, input}, index) => ({
      presetId: index === 0 ? 'default' : id,
      checks: finalChecks(input.setup === 'split-0' ? [1, 1, 1, 0, 0] : [1, 1, 1, 1, 1]),
    })),
    initialState(input) { return initialState(matrixFor(setupFor(input).edges)); },
    generateEvents(input) {
      const {edges, start} = setupFor(input);
      const rt = runtime(matrixFor(edges));
      if (input.mode === 'dfs') rt.dfs(start, 1);
      else bfs(rt, start);
      return rt.events;
    },
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else globalThis.DSInteractive.scenario = scenario;
})();
