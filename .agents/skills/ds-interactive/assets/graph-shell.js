(function (root) {
  'use strict';
  const D = root.DSInteractive;

  function watchCard(entries, snapshot) {
    const card = D.el('dl', 'graph-watch');
    card.setAttribute('aria-label', '현재 값');
    for (const {id, label, name, value, cell} of entries) {
      const row = D.el('div', 'graph-watch-entry');
      const expression = D.el('dd');
      row.dataset.graphWatch = id;
      row.toggleAttribute('data-written', Boolean(cell && snapshot.writes.some(write => write.cellId === cell)));
      if (name) expression.append(D.el('code', '', name), ' = ');
      const current = D.el('strong', 'graph-watch-value', value == null ? '—' : String(value));
      expression.append(current);
      row.append(D.el('dt', '', label), expression);
      card.append(row);
    }
    return card;
  }

  function mountPlayback(app, signal, hasOutput) {
    const bar = app.querySelector('.playbar');
    const trigger = D.el('button', 'text-btn graph-speed-trigger', '1×');
    trigger.type = 'button';
    trigger.dataset.action = 'graph-options';
    trigger.setAttribute('aria-controls', 'graph-playback-options');
    const popup = D.el('div', 'graph-playback-options');
    popup.id = 'graph-playback-options';
    popup.setAttribute('role', 'group');
    popup.setAttribute('aria-label', '재생 옵션');
    popup.append(bar.querySelector('.speeds'));

    let jumps;
    if (hasOutput) {
      jumps = D.el('div', 'graph-jumps');
      for (const [action, label] of [['previous-output', '이전 출력'], ['next-output', '다음 출력']]) {
        const button = D.el('button', 'btn', label);
        button.type = 'button';
        button.dataset.action = action;
        jumps.append(button);
      }
      popup.append(jumps);
    }
    const endpoints = D.el('div', 'graph-endpoints');
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
    return jumps;
  }

  function mountGraphShell(app, scenario, {render, heading, note, hasOutput = false}) {
    const q = selector => app.querySelector(selector);
    const events = new AbortController();
    const on = (target, event, handler) => target.addEventListener(event, handler, {signal: events.signal});
    const left = q('#panel-left');
    const right = q('#panel-right');
    const code = q('.source-pane');
    const list = q('.step-list');
    const history = list.closest('section');
    const historyTitle = history.querySelector('h2');
    const follow = D.el('button', 'text-btn graph-follow', '실행 위치로');
    follow.type = 'button';
    follow.hidden = true;
    history.className = 'graph-history';
    historyTitle.textContent = '줄 기록';
    historyTitle.id = 'graph-history-title';
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
    q('.pane-heading h2').textContent = heading;
    q('.scene-note').textContent = note;
    q('.stage').setAttribute('aria-label', '그래프 실행 보기');
    const memory = q('.memory');
    memory.setAttribute('aria-label', '그래프, 결과와 현재 값');
    q('.view-btns').hidden = true;
    q('.tree-output').remove();

    const header = q('.topbar');
    const configuration = q('.configuration');
    configuration.querySelector('h2').hidden = true;
    const headerInputs = D.el('div', 'graph-header-tools');
    headerInputs.append(q('.modes'));
    header.insertBefore(headerInputs, q('[data-action=theme]'));
    const viewport = q('.stage-viewport');
    const presetLabel = q('[data-action=preset]').closest('label');
    if (presetLabel.hidden) {
      headerInputs.prepend(configuration);
    } else {
      headerInputs.prepend(presetLabel);
      viewport.before(configuration);
    }
    viewport.tabIndex = 0;
    viewport.setAttribute('role', 'region');
    viewport.setAttribute('aria-label', '그래프 단계');

    const message = q('.explanation').closest('section');
    message.className = 'graph-explanation';
    message.querySelector('h2').hidden = true;
    message.querySelector('.phase').hidden = true;
    message.querySelector('.step-title').hidden = true;
    const changes = q('.changes').closest('section');
    const changeDetails = D.el('details', 'graph-changes');
    changeDetails.append(D.el('summary', '', changes.querySelector('h2').textContent), q('.changes'));
    const details = D.el('section', 'graph-details');
    details.append(D.el('h2', 'sec-title', '실행 상태 상세'));
    const state = D.el('div', 'graph-detail-content');
    const selection = q('.selection');
    selection.hidden = true;
    details.append(state, changeDetails, selection);
    const example = q('.provenance');
    example.querySelector('summary').textContent = '예제 정보';
    example.querySelector('p').textContent = '← / → 단계 이동 · Space 재생 · Home / End 처음과 마지막.';
    example.querySelector('p:last-child').hidden = true;
    example.querySelector('summary').after(q('.takeaway').closest('section'));
    left.querySelector('.panel-inner').replaceChildren(left.querySelector('.panel-head'), code);
    right.querySelector('.panel-inner').replaceChildren(right.querySelector('.panel-head'), details, example);
    memory.after(message);

    D.registerRenderer('c-graph', {render(snapshot) {
      const {overview, result, current, detail} = render(snapshot);
      const scene = D.el('div', 'graph-scene');
      result.classList.add('graph-result');
      scene.append(overview, result, watchCard(current, snapshot));
      state.replaceChildren(detail);
      return scene;
    }});

    let lastTrace;
    let followedTop = 0;
    let leftOpen = false;
    const jumps = mountPlayback(app, events.signal, hasOutput);
    let outputSteps = [];
    let outputTargets = {};
    function noticeScroll() {
      const maxTop = list.scrollHeight - list.clientHeight;
      if (leftOpen && Math.abs(list.scrollTop - Math.min(followedTop, maxTop)) > 1) follow.hidden = false;
    }
    function trackRow() {
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
      trackRow();
    });

    // The shared player owns the clock and execution. Decorate its shell update
    // to derive the graph controls from the exact entries it is displaying.
    const mountShell = D.mountShell;
    D.mountShell = (app, options) => {
      const shell = mountShell(app, {...options, onPanelsChange({narrow, drawer, leftOpen: opened}) {
        leftOpen = opened;
        if (leftOpen) {
          history.after(message);
          trackRow();
        } else {
          memory.after(message);
        }
        if (narrow && drawer && app.dataset.playing === 'true') q('[data-action=play]').click();
      }});
      if (jumps) on(jumps, 'click', event => {
        const target = outputTargets[event.target.closest('button')?.dataset.action];
        if (target !== undefined) options.onStep(target);
      });
      return {
        ...shell,
        update(trace, entries, step, invalid) {
          if (trace !== lastTrace) {
            lastTrace = trace;
            follow.hidden = true;
            followedTop = list.scrollTop = 0;
            if (jumps) outputSteps = entries.flatMap((entry, i) =>
              i && entry.state.stdout.length > entries[i - 1].state.stdout.length ? [i] : []);
          } else {
            noticeScroll();
          }
          shell.update(trace, entries, step, invalid);
          const shown = entries[step];
          const next = shown.phase === 'before' ? shown : entries[step + 1];
          const currentLine = q('.code-line.current');
          if (shown.phase === 'after') currentLine?.classList.add('executed');
          if (next && next.at.sourceId === currentLine?.dataset.sourceId) {
            q('.code-line[data-line="' + next.at.line + '"]')?.classList.add('graph-next-line');
          } else if (next) {
            const source = trace.sources.find(source => source.id === next.at.sourceId);
            const row = D.el('div', 'code-line graph-next-line graph-next-source');
            row.dataset.sourceId = next.at.sourceId;
            row.dataset.line = next.at.line;
            row.append(D.el('span', 'line-number', next.at.line), D.el('span', '',
              (source.label || source.id) + ' · ' + source.text.split('\n')[next.at.line - 1].trim()));
            q('.code').prepend(row);
          }
          if (jumps) {
            outputTargets = {
              'previous-output': outputSteps.findLast(index => index < step),
              'next-output': outputSteps.find(index => index > step),
            };
            for (const button of jumps.querySelectorAll('button')) {
              button.disabled = invalid || outputTargets[button.dataset.action] === undefined;
            }
          }
          trackRow();
        },
      };
    };
    let player;
    try {
      player = D.mountPlayer(app, scenario);
      if (presetLabel.hidden) {
        for (const label of configuration.querySelectorAll('.inputs label')) {
          if (label.firstChild?.nodeType === Node.TEXT_NODE) label.firstChild.remove();
        }
      }
    } finally {
      D.mountShell = mountShell;
    }
    return {destroy() { events.abort(); player.destroy(); }};
  }

  D.drawArrows = () => {};
  D.mountGraphShell = mountGraphShell;
})(globalThis);
