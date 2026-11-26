(function (root) {
  'use strict';
  const D = root.DSInteractive;

  function studyArray({array}) {
    return {
      heading: array.heading,
      note: '읽은 칸은 점선, 값을 쓴 칸은 파란색으로 표시',
      render(step) {
        const {cells} = step.state;
        const liveInt = id => cells[id]?.lifetime === 'live' && cells[id].value.kind === 'int'
          ? cells[id].value.value : undefined;
        const current = array.watch.map(({name, label, cellId}) => ({
          id: name, name, label, cell: cellId, value: liveInt(cellId),
        }));
        const overview = D.el('div', 'study-arrays');
        for (const [rowIndex, row] of array.rows.entries()) {
          const section = D.el('section', 'study-array');
          section.dataset.arrayRow = rowIndex;
          const ended = cells[row.cells[0]]?.lifetime === 'ended';
          section.append(D.el('h3', '', row.label + (ended ? ' · 수명 종료' : '')));
          const grid = D.el('ol', 'array-grid');
          grid.style.setProperty('--array-length', row.cells.length);
          for (const [index, id] of row.cells.entries()) {
            const slot = D.el('li', 'array-slot');
            slot.dataset.arrayCell = id;
            slot.toggleAttribute('data-read', step.reads.includes(id));
            slot.toggleAttribute('data-written', step.writes.some(write => write.cellId === id));
            slot.toggleAttribute('data-split', array.splits?.[rowIndex] === index);
            const tags = D.el('span', 'array-markers');
            for (const marker of array.markers) {
              if (marker.row === rowIndex && index >= (marker.min ?? 0) &&
                  index <= (marker.max ?? row.cells.length - 1) && liveInt(marker.cellId) === index) {
                tags.append(D.el('span', 'array-marker', marker.label));
              }
            }
            slot.append(D.el('span', 'array-index', index),
              D.el('strong', 'array-value', liveInt(id) ?? '—'), tags);
            grid.append(slot);
          }
          section.append(grid);
          overview.append(section);
        }
        const result = D.el('section');
        result.append(D.el('h3', '', array.title), D.el('p', 'study-result-line', array.result(step)));
        const detail = D.el('dl', 'array-detail');
        detail.setAttribute('aria-label', '인덱스와 작업 변수');
        const watched = new Set(current.map(entry => entry.cell));
        const locals = Object.values(cells).filter(cell => cell.owner === step.state.activeFrame &&
          cell.lifetime === 'live' && cell.value.kind === 'int' && !watched.has(cell.id));
        for (const entry of locals) {
          detail.append(D.el('dt', '', entry.name), D.el('dd', '', D.format(entry.value)));
        }
        return {overview, result, current, detail};
      },
    };
  }

  function configureArrayCases(app, {inputs, presets}) {
    const [field] = inputs;
    if (inputs.length !== 1 || field.type !== 'enum') return;
    const covered = new Set([field.default, ...presets.map(preset => preset.input[field.key])]);
    if (!field.options.every(option => covered.has(option.value))) return;
    app.querySelector('[data-action=preset] option[value=default]').textContent =
      field.options.find(option => option.value === field.default).label;
    app.querySelector('.inputs select').closest('label').hidden = true;
  }

  Object.assign(D, {studyArray, configureArrayCases});
})(globalThis);
