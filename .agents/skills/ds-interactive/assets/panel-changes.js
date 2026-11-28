(function (D) {
  'use strict';

  // Keep the origin of a new cell available even when a tree groups several events into one line.
  const applyEvent = D.applyEvent;
  D.applyEvent = (state, event, limits) => {
    const result = applyEvent(state, event, limits);
    for (const write of result.writes) {
      if (write.before === null) {
        result.state.cells[write.cellId].creation = {kind: event.kind, label: event.label};
      }
    }
    return result;
  };

  const beforeCreation = {
    bind: '전달 전',
    declare: '선언 전',
    allocate: '할당 전',
  };

  function format(value, state) {
    if (value?.kind !== 'pointer' || value.target === null) return D.format(value);
    const target = state.cells[value.target];
    const object = state.objects[target?.owner];
    if (object?.type === 'GraphType' && object.cellIds[0] === target.id) return '그래프 주소';
    return target?.address?.startsWith('&') ? target.address : D.format(value);
  }

  function renderPanelChanges(container, {state, writes}) {
    container.replaceChildren(...writes.map(write => {
      const cell = state.cells[write.cellId];
      const creation = write.before === null ? cell?.creation : null;
      const before = write.before === null ? beforeCreation[creation?.kind] ?? '저장 공간 없음' :
        format(write.before, state);
      const after = format(write.after, state);
      const name = cell?.name ?? write.cellId;
      let role;
      if (creation?.kind === 'bind') {
        if (after === '그래프 주소') role = '그래프 포인터';
        else if (creation.label === '정점 번호 전달') role = '정점 번호';
      }
      const row = D.el('div', 'change');
      row.append(D.el('strong', '', role ? name + ' (' + role + ')' : name),
        D.el('div', '', before + ' → ' + after));
      return row;
    }));
    if (!writes.length) container.append(D.el('p', 'trace-message', '이 단계에서는 저장 값이 바뀌지 않았습니다.'));
  }

  D.renderPanelChanges = renderPanelChanges;
})(DSInteractive);
