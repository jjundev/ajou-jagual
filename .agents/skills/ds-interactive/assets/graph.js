(function (root) {
  'use strict';
  const D = root.DSInteractive;
  const namespace = 'http://www.w3.org/2000/svg';

  function svg(tag, attributes = {}) {
    const node = document.createElementNS(namespace, tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    return node;
  }

  function drawing(positions, vertices, matrix, visited, parents, current, inspection) {
    const picture = svg('svg', {
      class: 'graph-drawing', viewBox: '0 0 360 220', role: 'img',
      'aria-label': '무방향 그래프. 간선은 인접 행렬에서, 정점의 방문 값은 visited 배열에서 확인할 수 있습니다.',
    });

    for (const from of vertices) {
      for (const to of vertices.slice(from + 1)) {
        if (!matrix[from][to]) continue;
        const [x1, y1] = positions[from];
        const [x2, y2] = positions[to];
        const edge = svg('line', {x1, y1, x2, y2, 'data-edge': `${from}-${to}`});
        edge.classList.add('graph-edge');
        edge.classList.toggle('is-chosen', parents[to] === from || parents[from] === to);
        edge.classList.toggle('is-reading',
          Boolean(inspection && inspection.includes(from) && inspection.includes(to)));
        picture.append(edge);
      }
    }

    for (const vertex of vertices) {
      const [x, y] = positions[vertex];
      const node = svg('g', {
        class: 'graph-vertex', transform: `translate(${x} ${y})`, 'data-vertex': vertex,
      });
      node.classList.toggle('is-visited', visited[vertex] > 0);
      node.classList.toggle('is-current', vertex === current);
      const label = svg('text', {'text-anchor': 'middle', 'dominant-baseline': 'central'});
      label.textContent = vertex;
      node.append(svg('circle', {r: 26, class: 'graph-ring'}), svg('circle', {r: 20}), label);
      picture.append(node);
    }
    return picture;
  }

  function matrixTable(vertices, matrix, inspection) {
    const table = D.el('table', 'graph-matrix');
    table.append(D.el('caption', '', '인접 행렬'));
    const corner = D.el('th', '', 'v ∖ w');
    const head = D.el('tr');
    head.append(corner, ...vertices.map(v => {
      const th = D.el('th', '', v);
      th.scope = 'col';
      return th;
    }));
    const thead = D.el('thead');
    thead.append(head);
    const tbody = D.el('tbody');
    for (const v of vertices) {
      const row = D.el('tr');
      const th = D.el('th', '', v);
      th.scope = 'row';
      row.append(th);
      for (const w of vertices) {
        const item = D.el('td', '', matrix[v][w]);
        item.dataset.matrix = `${v}-${w}`;
        if (inspection?.[0] === v && inspection?.[1] === w) item.classList.add('is-reading');
        row.append(item);
      }
      tbody.append(row);
    }
    table.append(thead, tbody);
    return table;
  }

  function stateRow(label, items, empty, region) {
    const section = D.el('section', 'graph-state');
    section.dataset.graphState = region;
    section.append(D.el('h3', '', label));
    if (items.length) {
      const list = D.el('ol', 'graph-values');
      list.append(...items);
      section.append(list);
    } else {
      section.append(D.el('p', 'graph-empty', empty));
    }
    return section;
  }

  function chip(label, sub) {
    const item = D.el('li', '', label);
    if (sub !== undefined) item.append(D.el('small', '', sub));
    return item;
  }

  function render(snapshot, positions) {
    const {state, reads, writes, explanation, title} = snapshot;
    const value = id => {
      const cell = state.cells[id];
      return cell?.lifetime === 'live' && cell.value.kind === 'int' ? cell.value.value : undefined;
    };
    const vertices = positions.map((_, index) => index);
    const active = state.activeFrame;
    const current = value(`${active}.v`) ?? value(`${active}.i`);
    const matrix = vertices.map(v => vertices.map(w => value(`graph.a.${v}.${w}`)));
    const visited = vertices.map(v => value(`graph.visited.${v}`));
    const parents = vertices.map(v => value(`graph.parent.${v}`));
    const readAddress = reads.find(id => id.startsWith('graph.a.'));
    const inspection = readAddress?.split('.').slice(2).map(Number);
    const queueMode = snapshot.at.sourceId === 'bfs';
    const count = value('graph.count');

    const scene = D.el('div', 'graph-scene');
    const overview = D.el('div', 'graph-overview');
    const figure = D.el('figure', 'graph-figure');
    const legend = D.el('figcaption', 'graph-legend');
    for (const [name, style] of [['방문한 정점', 'visited'], ['현재 정점', 'current'], ['발견 간선', 'chosen'], ['검사 중', 'reading']]) {
      const entry = D.el('span', 'graph-key', name);
      entry.dataset.key = style;
      legend.append(entry);
    }
    figure.append(drawing(positions, vertices, matrix, visited, parents, current, inspection), legend);
    overview.append(figure, matrixTable(vertices, matrix, inspection));

    const message = D.el('div', 'graph-message');
    message.append(D.el('strong', '', title), D.el('p', '', explanation));

    const data = D.el('div', 'graph-data');
    const visits = vertices.map(v => {
      const item = chip(visited[v], `[${v}]`);
      item.dataset.visited = v;
      if (writes.some(w => w.cellId === `graph.visited.${v}`)) item.classList.add('is-written');
      else if (reads.includes(`graph.visited.${v}`)) item.classList.add('is-reading');
      return item;
    });
    const visitedRow = stateRow('visited', visits, '', 'visited');
    if (count !== undefined) {
      visitedRow.querySelector('h3').append(D.el('span', 'graph-count', `count = ${count}`));
    }
    if (queueMode) {
      const queue = [];
      const head = value(`${active}.head`);
      const tail = value(`${active}.tail`);
      for (let i = head; i < tail; i++) queue.push(chip(value(`${active}.q.${i}`)));
      data.append(stateRow('큐 · 앞 → 뒤', queue, '비어 있음', 'queue'));
    } else {
      const calls = [];
      for (let id = active; id; id = state.frames[id].caller) {
        const frame = state.frames[id];
        const v = value(`${id}.v`);
        const i = value(`${id}.i`);
        calls.push(chip(v === undefined ? 'find_connected_component()' : `dfs_mat(${v})`,
          v === undefined && i !== undefined ? `i = ${i}` : undefined));
      }
      data.append(stateRow('호출 스택 · 위 → 아래', calls, '비어 있음', 'stack'));
    }
    data.append(visitedRow, stateRow('출력 순서', state.stdout.map(v => chip(v.trim())), '아직 출력 없음', 'output'));
    scene.append(overview, message, data);
    return scene;
  }

  function mountGraphPlayer(app, scenario) {
    D.registerRenderer('c-graph', {render: snapshot => render(snapshot, scenario.graph.positions)});
    const q = selector => app.querySelector(selector);
    q('[data-action=toggle-left] span').textContent = '코드';
    q('[data-action=toggle-left]').setAttribute('aria-label', '코드 패널');
    q('#panel-left').setAttribute('aria-label', '코드 패널');
    q('#panel-left .panel-head h2').textContent = '코드';
    q('.pane-heading h2').textContent = '그래프 탐색';
    q('.scene-note').textContent = '정점 번호 오름차순';
    q('.stage').setAttribute('aria-label', '그래프와 실행 상태');
    q('.memory').setAttribute('aria-label', '그래프, 인접 행렬, 방문 상태');
    q('.view-btns').hidden = true;
    q('[data-action=option-addresses]').closest('section').hidden = true;
    q('.explanation').closest('section').hidden = true;
    q('.selection').closest('section').hidden = true;
    q('.provenance p').textContent = '← / → 단계 이동 · Space 재생 · Home / End 처음과 마지막.';
    const configuration = q('.configuration');
    configuration.querySelector('h2').hidden = true;
    q('[data-action=preset]').closest('label').hidden = true;
    q('.stage-viewport').before(configuration);
    const viewport = q('.stage-viewport');
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', '그래프 단계');
    const live = D.el('span', 'graph-sr');
    live.setAttribute('aria-live', 'polite');
    q('.stage').append(live);
    const player = D.mountPlayer(app, scenario);
    const syncMessage = () => {
      live.textContent = [q('.phase').textContent, q('.explanation').textContent].join('. ');
      const list = q('.step-list');
      const row = list.querySelector('[aria-pressed=true]');
      if (!row) return;
      const active = row.getBoundingClientRect();
      const visible = list.getBoundingClientRect();
      if (active.top < visible.top) list.scrollTop += active.top - visible.top;
      else if (active.bottom > visible.bottom) list.scrollTop += active.bottom - visible.bottom;
    };
    const observer = new MutationObserver(syncMessage);
    observer.observe(q('.explanation'), {childList: true});
    syncMessage();
    return {destroy() { observer.disconnect(); player.destroy(); }};
  }

  // The graph scene has its own SVG and does not position pointer arrows.
  D.drawArrows = () => {};
  D.mountGraphPlayer = mountGraphPlayer;
})(globalThis);
