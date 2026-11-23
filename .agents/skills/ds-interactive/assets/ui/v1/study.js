(function (root) {
  'use strict';
  const D = root.DSInteractive;

  function watchCard(entries, snapshot) {
    const card = D.el('dl', 'study-watch');
    card.setAttribute('aria-label', '현재 값');
    for (const {id, label, name, value, cell} of entries) {
      const row = D.el('div', 'study-watch-entry');
      const expression = D.el('dd');
      row.dataset.studyWatch = id;
      row.toggleAttribute('data-written', Boolean(cell && snapshot.writes.some(write => write.cellId === cell)));
      if (name) expression.append(D.el('code', '', name), ' = ');
      const current = D.el('strong', 'study-watch-value', value == null ? '—' : String(value));
      expression.append(current);
      row.append(D.el('dt', '', label), expression);
      card.append(row);
    }
    return card;
  }

  function mountPlayback(app, signal, jumpOutput) {
    const bar = app.querySelector('.playbar');
    const trigger = D.el('button', 'text-btn study-speed-trigger', '1×');
    trigger.type = 'button';
    trigger.dataset.action = 'study-options';
    trigger.setAttribute('aria-controls', 'study-playback-options');
    const popup = D.el('div', 'study-playback-options');
    popup.id = 'study-playback-options';
    popup.setAttribute('role', 'group');
    popup.setAttribute('aria-label', '재생 옵션');
    popup.append(bar.querySelector('.speeds'));

    const jumps = D.el('div', 'study-jumps');
    jumps.hidden = true;
    for (const [action, label] of [['previous-output', '이전 출력'], ['next-output', '다음 출력']]) {
      const button = D.el('button', 'btn', label);
      button.type = 'button';
      button.dataset.action = action;
      jumps.append(button);
    }
    popup.append(jumps);
    jumps.addEventListener('click', event => {
      const action = event.target.closest('button')?.dataset.action;
      if (action) jumpOutput(action === 'previous-output' ? -1 : 1);
    }, {signal});
    const endpoints = D.el('div', 'study-endpoints');
    for (const button of bar.querySelectorAll('[data-action=first], [data-action=last]')) {
      button.classList.replace('icon-btn', 'btn');
      button.textContent = button.getAttribute('aria-label');
      endpoints.append(button);
    }
    popup.append(endpoints);
    bar.append(trigger, popup);

    let pinned = false;
    function show(open) {
      popup.hidden = !open;
      trigger.setAttribute('aria-expanded', String(open));
    }
    function setSpeed(button) {
      trigger.textContent = button.textContent;
      trigger.setAttribute('aria-label', '재생 옵션 · 현재 배속 ' + button.textContent);
    }
    show(false);
    setSpeed(popup.querySelector('[data-speed="1"]'));
    const on = (target, event, handler) => target.addEventListener(event, handler, {signal});
    on(trigger, 'click', () => {
      pinned = !pinned;
      show(pinned);
    });
    on(bar, 'pointerenter', event => { if (event.pointerType === 'mouse') show(true); });
    on(bar, 'pointerleave', event => {
      if (event.pointerType === 'mouse' && !pinned && !popup.contains(document.activeElement)) show(false);
    });
    on(popup, 'focusout', event => {
      if (!pinned && !bar.matches(':hover') && !popup.contains(event.relatedTarget)) show(false);
    });
    on(document, 'pointerdown', event => {
      if (!bar.contains(event.target)) { pinned = false; show(false); }
    });
    on(document, 'keydown', event => {
      if (event.defaultPrevented || event.key !== 'Escape' || popup.hidden) return;
      event.preventDefault();
      if (popup.contains(document.activeElement)) trigger.focus({preventScroll: true});
      pinned = false;
      show(false);
    });
    on(popup, 'click', event => {
      const button = event.target.closest('button');
      if (button?.dataset.speed) setSpeed(button);
    });
    return {jumps, close() { pinned = false; show(false); }};
  }

  function mountStudyUi(app, design, {jumpOutput, signal}) {
    const q = selector => app.querySelector(selector);
    const on = (target, event, handler) => target.addEventListener(event, handler, {signal});
    const selection = q('.selection');
    const viewOptions = q('[data-action=option-addresses]').closest('section');
    const left = q('#panel-left');
    const right = q('#panel-right');
    const code = q('.source-pane');
    const list = q('.step-list');
    const history = list.closest('section');
    const historyTitle = history.querySelector('h2');
    const follow = D.el('button', 'text-btn study-follow', '실행 위치로');
    follow.type = 'button';
    follow.hidden = true;
    history.className = 'study-history';
    historyTitle.textContent = '줄 기록';
    historyTitle.id = 'study-history-title';
    historyTitle.after(follow);
    list.tabIndex = 0;
    list.setAttribute('role', 'region');
    list.setAttribute('aria-labelledby', historyTitle.id);
    list.removeAttribute('aria-label');
    code.append(history);
    q('.source-note').hidden = true;
    for (const [side, panel, label] of [['left', left, '실행 코드'], ['right', right, '실행 상태']]) {
      const toggle = q('[data-action=toggle-' + side + ']');
      toggle.querySelector('span').textContent = label;
      toggle.setAttribute('aria-label', label + ' 패널');
      toggle.title = label + ' 패널';
      panel.setAttribute('aria-label', label);
      panel.querySelector('.panel-head h2').remove();
    }
    q('.pane-heading h2').textContent = design.heading;
    q('.scene-note').textContent = design.note || '';
    q('.stage').setAttribute('aria-label', '실행 보기');
    const memory = q('.memory');
    memory.setAttribute('aria-label', '그림, 결과와 현재 값');
    q('.tree-output').remove();

    const header = q('.topbar');
    const configuration = q('.configuration');
    configuration.querySelector('h2').hidden = true;
    const headerInputs = D.el('div', 'study-header-tools');
    headerInputs.append(q('.modes'));
    header.insertBefore(headerInputs, q('[data-action=theme]'));
    const viewport = q('.stage-viewport');
    const presetLabel = q('[data-action=preset]').closest('label');
    if (presetLabel.hidden) {
      headerInputs.dataset.primary = 'setup';
      const label = q('.inputs label:not([hidden])');
      if (label?.firstChild?.nodeType === Node.TEXT_NODE) label.firstChild.remove();
      headerInputs.prepend(configuration);
    } else {
      headerInputs.prepend(presetLabel);
      configuration.classList.add('study-stage-inputs');
      viewport.before(configuration);
    }
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', '실행 단계');

    const message = q('.explanation').closest('section');
    message.className = 'study-explanation';
    message.querySelector('h2').hidden = true;
    message.querySelector('.phase').hidden = true;
    message.querySelector('.step-title').hidden = true;
    const changes = q('.changes').closest('section');
    const changeDetails = D.el('details', 'study-changes');
    changeDetails.append(D.el('summary', '', changes.querySelector('h2').textContent), q('.changes'));
    const details = D.el('section', 'study-details');
    details.append(D.el('h2', 'sec-title', '실행 상태 상세'));
    const state = D.el('div', 'study-detail-content');
    details.append(state);
    const zoom = q('.view-btns');
    if (design.memory) {
      viewOptions.append(zoom);
      details.append(selection, viewOptions);
    } else {
      zoom.remove();
    }
    details.append(changeDetails);
    const example = q('.provenance');
    example.querySelector('summary').textContent = '예제 정보';
    example.querySelector('p').textContent = '← / → 단계 이동 · Space 재생 · Home / End 처음과 마지막.';
    example.querySelector('p:last-child').hidden = true;
    example.querySelector('summary').after(q('.takeaway').closest('section'));
    left.querySelector('.panel-inner').replaceChildren(left.querySelector('.panel-head'), code);
    right.querySelector('.panel-inner').replaceChildren(right.querySelector('.panel-head'), details, example);
    memory.after(message);

    const scene = D.el('div', 'study-scene');
    memory.append(scene);
    const playback = mountPlayback(app, signal, jumpOutput);
    const {jumps} = playback;
    let followedTop = 0;
    let leftOpen = false;
    function noticeScroll() {
      const maxTop = list.scrollHeight - list.clientHeight;
      if (leftOpen && Math.abs(list.scrollTop - Math.min(followedTop, maxTop)) > 1) follow.hidden = false;
    }
    function syncHistory() {
      if (!leftOpen || !follow.hidden) return;
      const row = list.querySelector('[aria-pressed=true]');
      if (!row) return;
      const position = row.getBoundingClientRect();
      const top = list.getBoundingClientRect().top + list.clientTop;
      const center = top + (row.dataset.stepIndex === '0' ? position.height : list.clientHeight) / 2;
      list.scrollTop += Math.round(position.top + position.height / 2 - center);
      followedTop = list.scrollTop;
    }
    on(list, 'scroll', noticeScroll);
    on(follow, 'click', () => {
      list.focus({preventScroll: true});
      follow.hidden = true;
      syncHistory();
    });

    const explanation = message.querySelector('.explanation');
    const diagnostic = message.querySelector('.diagnostic');
    const changesList = changeDetails.querySelector('.changes');

    function paint(snapshot, stateInfo) {
      const focused = document.activeElement;
      const id = focused?.dataset.cellId, frame = focused?.dataset.inspectFrame;
      const node = focused?.dataset.nodeId;
      const overviewOffset = scene.firstElementChild?.scrollTop || 0;
      const {overview, result, current, detail} = design.render(snapshot, stateInfo);
      result.classList.add('study-result');
      scene.replaceChildren(overview, result, watchCard(current, snapshot));
      overview.scrollTop = overviewOffset;
      if (detail) state.replaceChildren(detail);
      memory.dataset.step = snapshot.id;
      explanation.textContent = snapshot.explanation || snapshot.title;
      diagnostic.textContent = snapshot.diagnostic?.message || '';
      changesList.replaceChildren(...snapshot.writes.map(write => {
        const row = D.el('div', 'change');
        row.append(D.el('strong', '', snapshot.state.cells[write.cellId]?.name || write.cellId),
          D.el('div', '', D.format(write.before) + ' → ' + D.format(write.after)));
        return row;
      }));
      if (!snapshot.writes.length) changesList.append(D.el('p', 'trace-message', '이 단계에서는 저장 값이 바뀌지 않았습니다.'));
      if (design.memory) selection.replaceChildren(design.selectionDetails(snapshot, stateInfo.selection));
      jumps.hidden = !stateInfo.hasOutput;
      q('[data-action=previous-output]').disabled = stateInfo.blocked || !stateInfo.hasPreviousOutput;
      q('[data-action=next-output]').disabled = stateInfo.blocked || !stateInfo.hasNextOutput;
      if (id || frame || node) {
        [...app.querySelectorAll('button[data-cell-id],button[data-inspect-frame],button[data-node-id]')]
          .find(button => id && button.dataset.cellId === id || frame && button.dataset.inspectFrame === frame ||
            node && button.dataset.nodeId === node)?.focus({preventScroll: true});
      }
    }

    return {
      syncPanels({leftOpen: opened, drawer}) {
        leftOpen = opened;
        if (leftOpen) history.after(message);
        else memory.after(message);
        if (drawer) playback.close();
        syncHistory();
      },
      paint,
      syncHistory,
      redraw() { design.redraw?.(); },
      reset() {
        playback.close();
        design.reset?.();
        follow.hidden = true;
        followedTop = list.scrollTop = 0;
      },
      destroy() {
        playback.close();
        design.destroy?.();
      },
    };
  }

  D.mountStudyUi = mountStudyUi;
})(globalThis);
