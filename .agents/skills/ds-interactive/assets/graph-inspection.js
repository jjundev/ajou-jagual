(function (root) {
  'use strict';
  const D = root.DSInteractive;
  const namespace = 'http://www.w3.org/2000/svg';
  const value = (snapshot, id) => snapshot.state.cells[id]?.value.value;
  const hasWrite = (snapshot, id) => snapshot.writes.some(write => write.cellId === id);

  function svg(tag, attributes, text) {
    const element = document.createElementNS(namespace, tag);
    for (const [key, val] of Object.entries(attributes)) element.setAttribute(key, val);
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function drawGraph(vertices, edges, current, directed) {
    const points = new Map(vertices.map(([id, x, y]) => [id, [x, y]]));
    const scene = svg('svg', {
      class: 'gi-diagram', viewBox: `0 0 360 ${directed ? 159 : 248}`,
      role: 'img', 'aria-label': [
        ...edges.map(({id, from, to, order}) => directed ? `${from}에서 ${to}로`
          : `${id} 다리 ${from}와 ${to}${order ? `, ${order}번째 사용` : ', 아직 사용 전'}`),
        `강조한 정점 ${current}`,
      ].join('. '),
    });
    if (directed) {
      const marker = svg('marker', {
        id: 'gi-arrow', viewBox: '0 0 10 10', refX: 9, refY: 5,
        markerWidth: 5, markerHeight: 5, orient: 'auto',
      });
      marker.append(svg('path', {d: 'M0 0 10 5 0 10z'}));
      const defs = svg('defs', {});
      defs.append(marker);
      scene.append(defs);
    }
    for (const edge of edges) {
      const {id, from, to, bend, order, focus} = edge;
      const [x1, y1] = points.get(from);
      const [x2, y2] = points.get(to);
      const length = Math.hypot(x2 - x1, y2 - y1);
      const cx = (x1 + x2) / 2 + bend * (y1 - y2) / length;
      const cy = (y1 + y2) / 2 + bend * (x2 - x1) / length;
      const endLength = Math.hypot(cx - x2, cy - y2);
      const endX = directed ? x2 + 22 * (cx - x2) / endLength : x2;
      const endY = directed ? y2 + 22 * (cy - y2) / endLength : y2;
      const group = svg('g', {class: 'gi-edge', 'data-graph-edge': id});
      group.classList.toggle('gi-used', Boolean(order));
      group.classList.toggle('gi-focus', Boolean(focus));
      group.append(svg('path', {
        d: `M ${x1} ${y1} Q ${cx} ${cy} ${endX} ${endY}`,
        ...(directed && {'marker-end': 'url(#gi-arrow)'}),
      }));
      if (!directed) {
        group.append(svg('text', {
          x: (x1 + x2 + 2 * cx) / 4, y: (y1 + y2 + 2 * cy) / 4 - 4,
          'text-anchor': 'middle',
        }, order ? `${id} · ${order}` : id));
      }
      scene.append(group);
    }
    for (const [id, x, y] of vertices) {
      const group = svg('g', {class: 'gi-node', transform: `translate(${x} ${y})`, 'data-graph-vertex': id});
      group.classList.toggle('gi-current', id === current);
      group.append(svg('circle', {class: 'gi-halo', r: 25}), svg('circle', {r: 18}),
        svg('text', {'text-anchor': 'middle', 'dominant-baseline': 'central'}, id));
      scene.append(group);
    }
    return scene;
  }

  function panel(title, content) {
    const section = D.el('section', 'gi-panel');
    section.append(D.el('h3', '', title), content);
    return section;
  }

  function cards(entries) {
    const list = D.el('dl', 'gi-stats');
    for (const {label, result, key, emphasis} of entries) {
      const card = D.el('div', 'gi-stat');
      card.dataset.stat = key;
      if (emphasis) card.classList.add(emphasis);
      card.append(D.el('dt', '', label), D.el('dd', '', result));
      list.append(card);
    }
    return list;
  }

  function bridgeView(snapshot, graph) {
    const start = graph.vertices[value(snapshot, 'start')][0];
    const edges = graph.bridges
      .map(([id, from, to, bend]) => ({id, from, to, bend, order: value(snapshot, 'order.' + id),
        focus: snapshot.reads.includes('order.' + id) || hasWrite(snapshot, 'order.' + id)}))
      .filter(edge => edge.order !== undefined);
    const visited = edges.filter(edge => edge.order).sort((a, b) => a.order - b.order);
    const trail = [start];
    for (const edge of visited) trail.push(trail.at(-1) === edge.from ? edge.to : edge.from);
    const degree = graph.vertices.map(([id]) => ({
      id, count: edges.filter(edge => [edge.from, edge.to].includes(id)).length,
    }));
    const odd = degree.filter(({count}) => count % 2).map(({id}) => id);
    const reached = new Set([start]);
    for (let previous = 0; previous !== reached.size;) {
      previous = reached.size;
      for (const {from, to} of edges) {
        if (reached.has(from) || reached.has(to)) {
          reached.add(from);
          reached.add(to);
        }
      }
    }
    const connected = degree.every(({id, count}) => !count || reached.has(id));
    const stats = cards(degree.map(({id, count}) => ({
      key: id, label: id, result: `${count} · ${count % 2 ? '홀수' : '짝수'}`,
      emphasis: count % 2 ? 'gi-odd' : '',
    })));
    const parity = D.el('p', 'gi-meta', `홀수 차수 ${odd.length}개${odd.length ? ' (' + odd.join(', ') + ')' : ''} · ${connected ? '모든 다리가 연결됨' : '다리 배치가 끊어짐'}`);
    const analysis = D.el('div', 'gi-degree');
    analysis.append(stats, parity);
    const result = D.el('div', 'gi-trail');
    result.append(D.el('p', 'gi-route', trail.join(' → ')));
    if (snapshot.at.line === 5) {
      const verdict = !connected ? '떨어진 다리 묶음에 갈 수 없어서 전체를 잇는 경로가 없어요.'
        : odd.length === 0 ? '홀수 차수 정점이 0개예요. 출발점으로 돌아오는 오일러 회로가 있어요.'
          : odd.length === 2 ? `오일러 경로의 두 끝점은 ${odd.join('와 ')}예요. ${odd.includes(start) ? '선택한 출발점은 그중 하나예요.' : '출발점을 둘 중 하나로 바꿔 보세요.'}`
            : '끝점 두 곳을 제외한 모든 정점은 들어오는 다리와 나가는 다리가 짝을 이뤄야 해요. 여기서는 홀수 차수가 4개라 오일러 경로도 없어요.';
      result.append(D.el('p', 'gi-verdict', verdict));
    }
    const trailData = D.el('ol', 'gi-crossings');
    for (const [index, edge] of visited.entries()) {
      trailData.append(D.el('li', '', `${edge.id} · ${trail[index]} → ${trail[index + 1]}`));
    }
    const figure = D.el('figure', 'gi-figure');
    figure.append(drawGraph(graph.vertices, edges, trail.at(-1), false),
      D.el('figcaption', '', '같은 두 정점을 잇는 다리도 각각 세어요. 이름 옆의 숫자는 건넌 순서예요.'));
    const detail = D.el('div', 'gi-scene');
    detail.append(panel('이동 기록', visited.length ? trailData : D.el('p', 'gi-meta', '아직 건넌 다리 없음')),
      panel('정점별 차수', analysis));
    const current = [
      {id: 'position', label: '현재 위치', value: trail.at(-1)},
      {id: 'crossings', label: '건넌 다리 수', value: `${visited.length}/${edges.length}`},
    ];
    return {overview: figure, result: panel('이동 경로', result), current, detail};
  }

  function matrixTable(vertices, matrix, active, axis, v) {
    const table = D.el('table', 'gi-matrix');
    table.append(D.el('caption', '', '인접 행렬'));
    const row = D.el('tr');
    row.append(D.el('th', '', '출발 ↘ 도착'));
    for (const [col] of vertices) {
      const header = D.el('th', '', col);
      header.scope = 'col';
      header.classList.toggle('gi-axis', axis === 'in' && col === v);
      row.append(header);
    }
    const thead = D.el('thead');
    thead.append(row);
    const tbody = D.el('tbody');
    for (const [from] of vertices) {
      const bodyRow = D.el('tr');
      const header = D.el('th', '', from);
      header.scope = 'row';
      header.classList.toggle('gi-axis', axis === 'out' && from === v);
      bodyRow.append(header);
      for (const [to] of vertices) {
        const id = `m.${from}.${to}`;
        const item = D.el('td', '', matrix[from][to]);
        item.dataset.matrixCell = id;
        item.classList.toggle('gi-axis', (axis === 'out' && from === v) || (axis === 'in' && to === v));
        item.classList.toggle('gi-focus', id === active);
        if (id === active) item.setAttribute('aria-label', `읽는 값 ${matrix[from][to]}`);
        bodyRow.append(item);
      }
      tbody.append(bodyRow);
    }
    table.append(thead, tbody);
    return table;
  }

  function degreeView(snapshot, graph) {
    const {vertices, rowLine, columnLine} = graph;
    const v = String(value(snapshot, 'v'));
    const axis = snapshot.at.line === rowLine ? 'out' : snapshot.at.line === columnLine ? 'in' : null;
    const active = snapshot.reads[0];
    const matrix = vertices.map(([from]) => vertices.map(([to]) => value(snapshot, `m.${from}.${to}`)));
    const edges = [];
    for (const [from] of vertices) {
      for (const [to] of vertices) {
        if (matrix[from][to] === 1) {
          const coordinate = `m.${from}.${to}`;
          edges.push({id: `${from}-${to}`, from, to, bend: matrix[to][from] ? -63 : 0,
            focus: active === coordinate});
        }
      }
    }
    const figure = D.el('figure', 'gi-figure');
    figure.append(drawGraph(vertices, edges, v, true),
      D.el('figcaption', '', edges.length ? `정점 ${v}를 기준으로 읽어요.` : '화살표가 하나도 없어요.'));
    const counts = cards([['out', '진출 차수', '행'], ['in', '진입 차수', '열']].map(([id, label, name]) => ({
      key: id, label: `${label} · ${v}${name}`, result: value(snapshot, id),
      emphasis: hasWrite(snapshot, id) ? 'gi-counter' : '',
    })));
    const overview = D.el('div', 'graph-overview');
    overview.append(figure, matrixTable(vertices, matrix, active, axis, v));
    const result = panel('차수 누적값', counts);
    const current = [
      {id: 'vertex', label: '기준 정점', name: 'v', value: v, cell: 'v'},
      {id: 'axis', label: '읽는 행 또는 열', value: axis === 'out' ? v + '행' : axis === 'in' ? v + '열' : undefined},
    ];
    const status = D.el('p', 'gi-meta', active
      ? `[${active.split('.').slice(1).join(', ')}] = ${value(snapshot, active)}`
      : '이 단계에서 읽은 행렬 칸 없음');
    return {overview, result, current, detail: panel('읽은 행렬 칸', status)};
  }

  function render(snapshot, graph) {
    return graph.view === 'bridges' ? bridgeView(snapshot, graph) : degreeView(snapshot, graph);
  }

  function mountGraphPlayer(app, scenario) {
    const q = selector => app.querySelector(selector);
    const graph = scenario.graph;
    const bridges = graph.view === 'bridges';
    app.dataset.graphView = graph.view;
    const player = D.mountGraphShell(app, scenario, {
      render: snapshot => render(snapshot, graph),
      heading: bridges ? '땅과 다리' : '화살표와 인접 행렬',
      note: bridges ? '다리 이름순으로 건너기' : '행은 출발 · 열은 도착',
    });
    const configuration = q('.configuration');
    const preset = q('[data-action=preset]');
    preset.options[0].textContent = bridges ? '원본 · A 출발' : 'G3 · 정점 1';
    const custom = new Option('직접 설정', 'custom');
    custom.disabled = true;
    preset.append(custom);
    const hasCustomInput = () => scenario.inputs.some(input =>
      q(`[data-input="${input.key}"]`).value !== String(input.default));
    const syncPreset = event => {
      if (event.target.matches('[data-input]') && preset.value === 'default' && hasCustomInput()) {
        preset.value = 'custom';
      }
    };
    configuration.addEventListener('input', syncPreset);
    configuration.addEventListener('change', syncPreset);
    return {destroy() {
      configuration.removeEventListener('input', syncPreset);
      configuration.removeEventListener('change', syncPreset);
      player.destroy();
    }};
  }

  D.mountGraphPlayer = mountGraphPlayer;
})(globalThis);
