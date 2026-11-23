(function () {
  'use strict';
  const sources = [
    {
      "id": "components",
      "label": "find_connected_component",
      "language": "c",
      "text": "void find_connected_component(GraphType *g)\n{\n  count = 0;\n  for (int i = 0; i < N; i++) {\n    if (!visited[i]) {\n      count++;\n      dfs_mat(g, i);\n    }\n  }\n}",
      "provenance": {
        "path": "자료구조_강의록_2026/Software_10_Graph.pdf",
        "sha256": "d14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10",
        "page": 17,
        "supplement": true,
        "adjustments": "정점 수를 N=5로 고정하고 for 선언과 중괄호를 정리했습니다.",
        "note": "강의록 p17 기반 보충 C · 정점 수를 N=5로 고정하고 for 선언과 중괄호를 정리했습니다."
      }
    },
    {
      "id": "dfs",
      "label": "성분 번호를 쓰는 dfs_mat",
      "language": "c",
      "text": "void dfs_mat(GraphType *g, int v)\n{\n  visited[v] = count;\n  printf(\"%d \", v);\n  for (int w = 0; w < N; w++) {\n    if (g->adj_mat[v][w] && !visited[w]) {\n      parent[w] = v;\n      dfs_mat(g, w);\n    }\n  }\n}",
      "provenance": {
        "path": "자료구조_강의록_2026/Software_10_Graph.pdf",
        "sha256": "d14a1223c5c792c7f0439a3cbdf89b0764bf3271278ce61fbb552ac793e24f10",
        "page": 14,
        "supplement": true,
        "adjustments": "p17 설명에 따라 visited[v]에 count를 씁니다. 발견 간선을 parent[]에 기록합니다.",
        "note": "강의록 p14 기반 보충 C · p17 설명에 따라 visited[v]에 count를 씁니다. 발견 간선을 parent[]에 기록합니다."
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

  const setups = [
    {value: 'lecture', label: '강의 그래프 · (0,1), (0,2), (3,4)', edges: splitEdges,
      groups: [1, 1, 1, 2, 2], count: 2},
    {value: 'bridge', label: '(2,3) 추가', edges: [...splitEdges, [2, 3]],
      groups: [1, 1, 1, 1, 1], count: 1},
    {value: 'isolated', label: '(3,4) 제거', edges: splitEdges.slice(0, -1),
      groups: [1, 1, 1, 2, 3], count: 3},
  ];
  const setupFor = input => setups.find(setup => setup.value === input.setup);

  const scenario = {
    version: 1, id: 'graph-components-1119', kind: 'c-graph', title: '연결 성분 찾기',
    intro: '간선 하나를 잇거나 끊은 사례를 선택해 보세요. 바깥 루프의 i와 DFS가 각 정점에 붙이는 번호를 비교할 수 있습니다.',
    takeaway: '바깥 루프가 visited[i] = 0인 정점을 찾을 때 count를 늘립니다. 그 DFS가 닿는 정점은 모두 같은 번호를 받습니다.',
    graph: {positions: [[59, 52], [47, 163], [156, 100], [265, 52], [302, 160]]},
    sources,
    inputs: [{key: 'setup', label: '그래프', type: 'enum', default: 'lecture',
      options: setups.map(({value, label}) => ({value, label}))}],
    presets: setups.slice(1).map(({value, label}) => ({id: value, label, input: {setup: value}})),
    expected: setups.map(({value, groups, count}, index) => ({
      presetId: index === 0 ? 'default' : value, checks: finalChecks(groups, count),
    })),
    initialState(input) { return initialState(matrixFor(setupFor(input).edges), true); },
    generateEvents(input) {
      const rt = runtime(matrixFor(setupFor(input).edges));
      const out = rt.writer('components');
      const id = rt.enter('components', 'find_connected_component');
      const countCell = 'graph.count';
      let count = 0;
      const iCell = cell(id, 'i', int(0));

      out(3, 'write', '성분 수 초기화', 'count를 0으로 초기화합니다.', {cellId: countCell, value: int(0)});
      out(4, 'declare', '바깥 루프 시작', '정점 번호 i = 0부터 방문 여부를 확인합니다.', {cell: iCell});
      for (const i of vertices) {
        const tag = rt.marked[i];
        out(5, 'read', tag === 0 ? '새 성분의 시작점' : '표시된 정점 건너뛰기',
          `visited[${i}] = ${tag}. ` + (tag === 0 ? '새 성분에서 DFS를 시작합니다.' : '이미 성분 번호가 있으므로 다음 정점으로 넘어갑니다.'),
          {cellId: visited(i)});
        if (tag === 0) {
          count++;
          out(6, 'write', '성분 번호 증가', `count = ${count}. 지금 시작하는 DFS가 이 번호를 씁니다.`,
            {cellId: countCell, value: int(count)});
          rt.dfs(i, count, {id, argument: iCell.id, at: {sourceId: 'components', line: 7}});
        }
        out(4, 'write', '다음 정점으로 이동', `바깥 루프의 i가 ${i + 1}이 됩니다.`,
          {cellId: iCell.id, value: int(i + 1)});
      }
      out(4, 'read', '바깥 루프 종료', `i = ${size}이므로 모든 정점의 방문 여부를 확인했습니다.`, {cellId: iCell.id});
      out(10, 'return', '연결 성분 찾기 완료', `count = ${count}. 같은 visited 값을 가진 정점끼리 한 연결 성분입니다.`, {frameId: id});
      return rt.events;
    },
  };

  if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
  else globalThis.DSInteractive.scenario = scenario;
})();
