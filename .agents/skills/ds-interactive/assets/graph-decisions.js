(function (root) {
  'use strict';
  const D = root.DSInteractive;
  const svg = (tag, attrs = {}) => {
    const element = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [name, value] of Object.entries(attrs)) element.setAttribute(name, value);
    return element;
  };

  function diagram(vertices, edges, nodes, {directed = false, label}) {
    const drawing = svg('svg', {class: 'decision-diagram', viewBox: '0 0 360 224', role: 'img', 'aria-label': label});
    if (directed) {
      const defs = svg('defs');
      for (const status of ['available', 'current', 'cycle']) {
        const marker = svg('marker', {
          id: 'decision-arrow-' + status, class: 'decision-arrow-' + status,
          viewBox: '0 0 9 9', refX: 8, refY: 4.5, markerWidth: 9, markerHeight: 9,
          markerUnits: 'userSpaceOnUse', orient: 'auto',
        });
        marker.append(svg('path', {d: 'M 0 0 L 9 4.5 L 0 9 Z'}));
        defs.append(marker);
      }
      drawing.append(defs);
    }
    const positions = new Map(vertices.map(([v, x, y]) => [v, [x, y]]));
    for (const {index, from, to, status, weight, curved} of edges) {
      const [x, y] = positions.get(from);
      const [tx, ty] = positions.get(to);
      const length = Math.hypot(tx - x, ty - y);
      const dx = (tx - x) / length;
      const dy = (ty - y) / length;
      const reach = directed ? 19 : 0;
      const path = curved ? 'M 296 98 Q 171 -53 46 43' :
        'M ' + (x + dx * reach) + ' ' + (y + dy * reach) + ' L ' + (tx - dx * reach) + ' ' + (ty - dy * reach);
      const edge = svg('g', {class: 'decision-edge', 'data-edge': index, 'data-status': status});
      const line = svg('path', {d: path});
      if (directed) line.setAttribute('marker-end', 'url(#decision-arrow-' + status + ')');
      edge.append(line);
      if (weight !== undefined) {
        const text = svg('text', {x: (x + tx) / 2, y: (y + ty) / 2, 'text-anchor': 'middle', dy: '.32em'});
        text.textContent = weight;
        edge.append(text);
      }
      drawing.append(edge);
    }
    for (const [v, x, y] of vertices) {
      const {status, degree} = nodes.get(v);
      const node = svg('g', {class: 'decision-node', 'data-node': v, 'data-status': status, transform: 'translate(' + x + ' ' + y + ')'});
      node.append(svg('circle', {r: 16}));
      const text = svg('text', {'text-anchor': 'middle', dy: '.32em'});
      text.textContent = v;
      node.append(text);
      if (degree !== undefined) {
        const badge = svg('g', {class: 'decision-degree', transform: 'translate(17 -16)'});
        badge.append(svg('circle', {r: 10}));
        const count = svg('text', {'text-anchor': 'middle', dy: '.32em'});
        count.textContent = degree;
        badge.append(count);
        node.append(badge);
      }
      drawing.append(node);
    }
    return drawing;
  }

  function overview(drawing, entries) {
    const figure = D.el('figure', 'decision-figure');
    const legend = D.el('figcaption', 'decision-legend');
    for (const [status, label] of entries) {
      const key = D.el('span', '', label);
      key.dataset.status = status;
      legend.append(key);
    }
    figure.append(drawing, legend);
    return figure;
  }

  function section(title, text, key) {
    const panel = D.el('section');
    const line = D.el('p', 'study-result-line', text);
    if (key) line.dataset.decisionState = key;
    panel.append(D.el('h3', '', title), line);
    return panel;
  }

  function pathsFrom(start, accepted) {
    const paths = new Map([[start, []]]);
    for (const [vertex, path] of paths) {
      for (const edge of accepted) {
        const next = edge.from === vertex ? edge.to : edge.to === vertex ? edge.from : null;
        if (next !== null && !paths.has(next)) paths.set(next, [...path, edge]);
      }
    }
    return paths;
  }

  function mst(snapshot, graph, input) {
    const {vertices, edges, weight} = graph;
    const {cells} = snapshot.state;
    const prim = input.mode === 'prim';
    const rank = index => cells['edge.' + index].value.value;
    const all = edges.map(([from, to], index) => ({
      from, to, index, rank: rank(index), weight: weight(index, input),
    }));
    const accepted = all.filter(edge => edge.rank > 0).sort((a, b) => a.rank - b.rank);
    const end = snapshot.phase !== 'before' && snapshot.at.line === (prim ? 5 : 7);
    const candidate = end ? undefined : all[cells.candidate.value.value];
    const label = edge => edge.from + '–' + edge.to + '(' + edge.weight + ')';
    const total = accepted.reduce((sum, edge) => sum + edge.weight, 0);
    const inside = new Set(['a', ...accepted.flatMap(edge => [edge.from, edge.to])]);
    const boundary = all.filter(edge => inside.has(edge.from) !== inside.has(edge.to));
    const path = !prim && candidate && candidate.rank <= 0
      ? pathsFrom(candidate.from, accepted).get(candidate.to) : undefined;
    const pathEdges = new Set((path || []).map(edge => edge.index));
    const nodes = new Map(vertices.map(([v]) => [v, {status: prim && inside.has(v) ? 'chosen' : 'available'}]));
    const statuses = all.map(edge => ({...edge, status:
      edge === candidate && edge.rank < 0 ? 'rejected-current' :
      edge === candidate ? (edge.rank > 0 ? 'chosen-current' : 'current') :
      pathEdges.has(edge.index) ? 'cycle' : edge.rank > 0 ? 'chosen' :
      edge.rank < 0 ? 'rejected' : prim && boundary.includes(edge) ? 'boundary' : 'available',
    }));
    // Paint the candidate last so intersecting edges cannot hide its label.
    if (candidate) statuses.push(...statuses.splice(candidate.index, 1));
    const detail = D.el('div', 'decision-details');
    if (prim) {
      detail.append(section('트리에 포함된 정점', [...inside].sort().join(', '), 'inside'),
        section('현재 경계 간선', boundary.sort((a, b) => a.weight - b.weight).map(label).join(' · ') || '없음', 'boundary'));
    } else {
      const seen = new Set();
      const groups = [];
      for (const [v] of vertices) {
        if (seen.has(v)) continue;
        const group = [...pathsFrom(v, accepted).keys()].sort();
        group.forEach(id => seen.add(id));
        groups.push('{' + group.join(', ') + '}');
      }
      detail.append(section('연결 요소', groups.join(' · '), 'components'));
      if (path) {
        let next = candidate.from;
        const points = [next, ...path.map(edge => (next = edge.from === next ? edge.to : edge.from))];
        detail.append(section('두 끝점 사이의 기존 경로', points.join(' → '), 'cycle-path'));
      }
      const queued = all.filter(edge => edge.rank === 0 && edge !== candidate)
        .sort((a, b) => a.weight - b.weight).map(label);
      detail.append(section('아직 검사하지 않은 간선', queued.join(' · ') || '없음', 'unexamined'));
    }
    const legend = prim ? [['chosen', '채택 · 트리 내부'], ['boundary', '경계 간선'], ['current', '현재 간선']]
      : [['chosen', '채택'], ['current', '현재 간선'], ['rejected', '제외']];
    return {
      overview: overview(diagram(vertices, statuses, nodes, {label: '가중 무방향 그래프'}), legend),
      result: section(end ? '최소 비용 신장 트리' : '채택한 간선',
        (accepted.map(label).join(' · ') || '아직 없음') + '  |  총비용 ' + total, 'mst-result'),
      current: [
        {id: 'candidate', label: '현재 간선', value: candidate && label(candidate), cell: 'candidate'},
        {id: 'count', label: '채택한 간선 수', value: accepted.length + ' / ' + (vertices.length - 1),
          cell: candidate?.rank > 0 ? 'edge.' + candidate.index : undefined},
      ],
      detail,
    };
  }

  function topo(snapshot, graph) {
    const {vertices, edges} = graph;
    const {cells, stdout} = snapshot.state;
    const active = edges.flatMap(([from, to], index) =>
      cells['edge.' + index].value.value ? [{from, to, index, curved: from === 5 && to === 0}] : []);
    const degrees = new Map(vertices.map(([v]) => [v, 0]));
    for (const {to} of active) degrees.set(to, degrees.get(to) + 1);
    const remaining = vertices.map(([v]) => v).filter(v => cells['node.' + v].value.value);
    const candidate = cells.candidate.value.value;
    const ready = remaining.filter(v => degrees.get(v) === 0 && v !== candidate);
    const failure = Boolean(cells.failure.value.value);
    const removed = snapshot.writes.find(write => write.cellId.startsWith('edge.'));
    const nodes = new Map(vertices.map(([v]) => {
      const visible = remaining.includes(v);
      return [v, {
        status: !visible ? 'removed' : candidate === v ? 'current' : ready.includes(v) ? 'chosen' : 'available',
        degree: visible ? degrees.get(v) : undefined,
      }];
    }));
    const cycle = new Set([0, 5, 8]);
    const diagramEdges = active.map(edge => ({...edge, status: failure && cycle.has(edge.index) ? 'cycle' : 'available'}));
    if (removed) {
      const index = Number(removed.cellId.split('.')[1]);
      const [from, to] = edges[index];
      diagramEdges.push({index, from, to, status: 'current'});
    }
    const output = stdout.map(text => text.trim()).join(' → ');
    const activeVertex = remaining.includes(candidate) ? candidate : undefined;
    const detail = D.el('div', 'decision-details');
    detail.append(section('남은 정점과 진입 차수', remaining.map(v => v + '(' + degrees.get(v) + ')').join(' · ') || '없음', 'degrees'),
      section('남은 방향 간선', active.map(({from, to}) => from + '→' + to).join(' · ') || '없음', 'active-edges'));
    if (failure) detail.append(section('사이클', '0 → 2 → 5 → 0', 'cycle'));
    return {
      overview: overview(diagram(vertices, diagramEdges, nodes, {directed: true, label: '선수 과목 그래프와 진입 차수'}),
        [['chosen', '진입 차수 0'], ['current', '선택·제거 중'], ['removed', '제거된 정점']]),
      result: section(failure ? '위상 정렬 불가' : remaining.length ? '출력 순서' : '위상 정렬 완료',
        output || '아직 출력 없음', 'topo-result'),
      current: [
        {id: 'candidate', label: '현재 정점', value: activeVertex, cell: 'candidate'},
        {id: 'ready', label: '다음에 고를 수 있는 정점', value: ready.join(', ') || '없음'},
      ],
      detail,
    };
  }

  D.mountGraphPlayer = (app, scenario) => {
    const graph = scenario.graph;
    const spanning = graph.view === 'mst';
    app.dataset.graphView = graph.view;
    const preset = app.querySelector('[data-action=preset]');
    const player = D.mountGraphShell(app, scenario, {
      heading: spanning ? '가중 무방향 그래프' : '선수 과목 그래프',
      render(snapshot, {trace}) {
        // Mode changes retain the graph variant. Keep the case selector aligned with the same input.
        const match = scenario.presets.find(item => Object.keys(trace.inputs)
          .every(key => item.input[key] === trace.inputs[key]));
        preset.value = match?.id || 'default';
        return spanning ? mst(snapshot, graph, trace.inputs) : topo(snapshot, graph);
      },
    });
    preset.options[0].textContent = spanning ? '강의 예제 · Kruskal' : '번호순 선택';
    app.querySelector('[data-input=setup]').closest('label').hidden = true;
    return player;
  };
})(globalThis);
