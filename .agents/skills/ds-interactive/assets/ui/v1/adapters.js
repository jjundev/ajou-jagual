(function (root) {
  'use strict';
  const D = root.DSInteractive;

  function resultLine(title, text) {
    const result = D.el('section');
    result.append(D.el('h3', '', title), D.el('p', 'study-result-line', text));
    return result;
  }

  function watchCells(entries, active, cells, exclude) {
    return entries.flatMap(entry => {
      const id = entry.cellId ?? active + '.' + entry.name;
      if (exclude?.has(entry.name) && !entry.cellId) return [];
      const cell = cells[id];
      return [{id: entry.name, label: entry.label, name: entry.name, cell: id,
        value: cell?.lifetime === 'live' ? D.format(cell.value) : '—'}];
    });
  }

  function studyMemory(app, scenario) {
    let latest, diagram;
    const selectionDetails = ({state}, id) => {
      const cell = state.cells[id];
      if (!cell) return D.el('p', '', '메모리에서 변수를 선택하면 주소와 값을 확인할 수 있어요.');
      const details = D.el('dl');
      const add = (term, text) => details.append(D.el('dt', '', term), D.el('dd', '', text));
      add(cell.name + '의 주소', cell.address);
      add('저장 값', D.format(cell.value));
      if (cell.lifetime === 'ended') add('수명', '종료');
      if (cell.lifetime === 'live' && cell.value.kind === 'pointer' && cell.value.target !== null) {
        const target = state.cells[cell.value.target];
        if (target) add('대상의 값', D.format(target.value));
      }
      return details;
    };
    return {
      heading: '호출과 메모리',
      note: '주소는 기호로 표시',
      memory: true,
      selectionDetails,
      redraw() { if (diagram?.isConnected) D.drawArrows(diagram, latest.snapshot, latest.selection); },
      render(snapshot, {selection, trace}) {
        const {state, writes} = snapshot;
        const cells = Object.values(state.cells).filter(cell => cell.lifetime === 'live');
        const selected = state.cells[selection];
        const pointer = selected?.lifetime === 'live' && selected.value.kind === 'pointer' ? selected
          : cells.find(cell => cell.owner === state.activeFrame && cell.value.kind === 'pointer')
            || cells.find(cell => cell.value.kind === 'pointer');
        const firstPointer = pointer || Object.values(trace.snapshots.at(-1).state.cells)
          .find(cell => cell.value.kind === 'pointer');
        const target = pointer ? state.cells[pointer.value.target] : undefined;
        const current = [
          {id: 'pointer', name: firstPointer?.name, label: '현재 포인터', cell: pointer?.id,
            value: pointer && D.format(pointer.value)},
          {id: 'target', name: target?.name, label: '대상의 값', cell: target?.id,
            value: target && D.format(target.value)},
          ...watchCells(scenario.watch || [], state.activeFrame, state.cells),
        ];
        const lastWrite = state.cells[writes.at(-1)?.cellId];
        const persistent = cells.filter(cell => cell.value.kind === 'int' &&
          (cell.owner === state.activeFrame || state.objects[cell.owner]));
        const resultCells = target?.lifetime === 'live' ? [target]
          : lastWrite?.lifetime === 'live' ? [lastWrite] : persistent.slice(0, 2);
        const resultText = resultCells.map(cell => cell.name + ' = ' + D.format(cell.value)).join(' · ') || '아직 결과 없음';
        const overview = D.el('div', 'study-memory-scroll');
        overview.tabIndex = 0;
        overview.setAttribute('role', 'region');
        overview.setAttribute('aria-label', '호출과 메모리 그림');
        diagram = D.el('div', 'study-memory-cells');
        diagram.append(D.memoryRenderer.render(snapshot, selection));
        overview.append(diagram);
        latest = {snapshot, selection};
        requestAnimationFrame(() => { if (diagram.isConnected) D.drawArrows(diagram, latest.snapshot, latest.selection); });
        const detail = D.el('p', '', state.frames[state.activeFrame]?.functionId
          ? '현재 호출 · ' + state.frames[state.activeFrame].functionId : '현재 활성 호출 없음');
        const result = state.stdout.length ? resultLine('출력', state.stdout.join('')) : resultLine('실행 결과', resultText);
        return {overview, result, current, detail};
      },
    };
  }

  function studyTree(app, scenario, {stop, repaint}) {
    const renderer = D.renderers.get('c-tree');
    const events = new AbortController();
    let expanded, node, opener;
    const dialog = D.el('dialog', 'tree-inspector');
    const heading = D.el('h2', '', '노드 메모리');
    heading.id = 'study-inspector-title';
    dialog.setAttribute('aria-labelledby', heading.id);
    const header = D.el('div', 'tree-inspector-head');
    const close = D.el('button', 'text-btn', '닫기');
    close.type = 'button';
    header.append(heading, close);
    const body = D.el('div', 'tree-inspector-body');
    dialog.append(header, body);
    // A node opens a modal detail on both desktop and mobile.
    app.append(dialog);
    close.addEventListener('click', () => dialog.close(), {signal: events.signal});
    dialog.addEventListener('close', () => {
      node = null;
      [...app.querySelectorAll('button[data-node-id]')]
        .find(button => button.dataset.nodeId === opener)?.focus({preventScroll: true});
      opener = null;
    }, {signal: events.signal});
    app.addEventListener('click', event => {
      const button = event.target.closest('button');
      if (button?.dataset.inspectFrame) {
        expanded = expanded === button.dataset.inspectFrame ? null : button.dataset.inspectFrame;
        repaint();
      }
      if (button?.dataset.nodeId) {
        stop();
        node = opener = button.dataset.nodeId;
        repaint();
        dialog.showModal();
        close.focus({preventScroll: true});
      }
    }, {signal: events.signal});

    return {
      heading: '전체 트리',
      reset() {
        expanded = opener = node = null;
        if (dialog.open) dialog.close();
      },
      destroy() {
        events.abort();
        dialog.remove();
      },
      render(snapshot, {trace}) {
        const {state} = snapshot;
        const metadata = trace.metadata;
        const view = D.getTreeView(metadata.tree, snapshot);
        const parameterId = view.stack[0]?.parameterCellId;
        const parameter = state.cells[parameterId];
        const final = trace.lineSteps.at(-1).state;
        const names = new Set(Object.values(final.frames).filter(frame => frame.parameterCellId)
          .map(frame => final.cells[frame.parameterCellId].name));
        const pointer = parameter?.value;
        const targetCell = pointer && state.cells[pointer.target];
        const target = targetCell && view.nodes.find(item => item.id === targetCell.owner);
        const current = [{id: 'node', label: '현재 호출이 가리키는 노드', cell: parameterId,
          name: parameter?.name || (names.size === 1 ? [...names][0] : undefined),
          value: target ? target.key + '번 노드' : D.format(pointer)}];
        current.push(...watchCells(scenario.watch || [], state.activeFrame, state.cells, names));
        const overview = D.el('div', 'study-tree-scroll');
        overview.tabIndex = 0;
        overview.setAttribute('role', 'region');
        overview.setAttribute('aria-label', '트리 그림');
        overview.append(renderer.render(snapshot, null, metadata, view));
        const detail = D.el('section');
        const ended = state.frames[snapshot.executed?.frameId];
        detail.append(D.el('h3', '', '호출 스택'), D.renderStackDetails(snapshot, view, expanded,
          !snapshot.diagnostic && ended?.lifetime === 'ended' ? ended : null, metadata.tree.fields.key));
        if (node) body.replaceChildren(D.renderNodeDetails(snapshot, view, node));
        return {overview, result: resultLine('출력', state.stdout.join('') || '아직 출력 없음'), current, detail};
      },
    };
  }

  Object.assign(D, {studyMemory, studyTree});
})(globalThis);
