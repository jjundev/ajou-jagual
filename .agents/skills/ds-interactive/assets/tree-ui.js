(function (root) {
 'use strict';
 const D = root.DSInteractive;

 function mountPlaybackOptions(app, trigger) {
  const bar = app.querySelector('.playbar');
  const stage = bar.closest('.stage');
  const speeds = bar.querySelector('.speeds');
  const popup = D.el('div','tree-playback-options');
  popup.id = 'tree-playback-options';
  popup.setAttribute('role','group');
  popup.setAttribute('aria-label','재생 옵션');
  trigger.classList.add('tree-speed-trigger');
  trigger.setAttribute('aria-controls',popup.id);

  const endpoints = D.el('div','tree-endpoints');
  endpoints.setAttribute('role','group');
  endpoints.setAttribute('aria-label','처음과 마지막 단계');
  for (const endpoint of bar.querySelectorAll('[data-action="first"], [data-action="last"]')) {
   endpoint.classList.replace('icon-btn','btn');
   endpoint.textContent = endpoint.getAttribute('aria-label');
   endpoints.append(endpoint);
  }
  popup.append(speeds, app.querySelector('.tree-jumps'), endpoints);
  bar.append(trigger, popup);

  const listeners = new AbortController();
  const on = (target, event, handler) => target.addEventListener(event,handler,{signal:listeners.signal});
  let openedBy = null;
  let leaveTimer;
  function fit() {
   const room = bar.getBoundingClientRect().top - stage.getBoundingClientRect().top;
   popup.style.setProperty('--playback-room',Math.max(0, room - 4)+'px');
  }
  const resize = new ResizeObserver(() => { if (openedBy) fit(); });
  resize.observe(stage);
  resize.observe(bar);
  function show(mode) {
   openedBy = mode;
   if (mode) fit();
   popup.hidden = !mode;
   trigger.setAttribute('aria-expanded',String(Boolean(mode)));
  }
  function setSpeed(button) {
   trigger.textContent = button.textContent;
   trigger.setAttribute('aria-label','재생 옵션 · 현재 배속 '+button.textContent);
  }
  function close(restoreFocus = true) {
   clearTimeout(leaveTimer);
   if (!openedBy) return false;
   const focusInside = popup.contains(document.activeElement);
   show(null);
   if (restoreFocus && focusInside) trigger.focus({preventScroll:true});
   return true;
  }

  on(bar,'pointerenter',event => {
   if (event.pointerType!=='mouse') return;
   clearTimeout(leaveTimer);
   if (!openedBy && !event.buttons) show('hover');
  });
  on(bar,'pointerleave',event => {
   if (event.pointerType==='mouse' && openedBy==='hover') {
    // Allow a diagonal move from the bar to the options above it.
    leaveTimer = setTimeout(() => {
     if (!popup.contains(document.activeElement)) close();
    }, 160);
   }
  });
  on(bar,'focusout',event => {
   if (!bar.contains(event.relatedTarget)) close(false);
  });
  on(document,'pointerdown',event => {
   if (!bar.contains(event.target)) close();
  });
  on(trigger,'click',() => {
   if (openedBy==='explicit') close();
   else {
    clearTimeout(leaveTimer);
    show('explicit');
   }
  });
  on(popup,'click',event => {
   const target = event.target.closest('button');
   if (target?.dataset.speed) setSpeed(target);
   else if (target) close();
  });

  setSpeed(speeds.querySelector('[aria-pressed=true]'));
  show(null);
  return {close,destroy() { close(false); listeners.abort(); resize.disconnect(); }};
 }

 function mountTreeUi(app, {scenario, stop, refresh}) {
  const q = selector => app.querySelector(selector);
  const action = name => q('[data-action="'+name+'"]');
  function button(label, name) {
   const el = D.el('button','text-btn',label);
   el.type = 'button';
   el.dataset.action = name;
   return el;
  }

  const header = q('.topbar');
  const left = q('.panel-left'), right = q('.panel-right');
  const code = q('.source-pane'), config = q('.configuration');
  const explanation = D.el('p','tree-step-explanation');
  explanation.setAttribute('role','status');
  const historyRegion = D.el('div','tree-history-region');
  const history = D.el('section','tree-history');
  const historyTitle = D.el('h2','sec-title tree-history-title','줄 기록');
  historyTitle.id = 'tree-history-title';
  const historyList = q('.step-list');
  const follow = button('실행 위치로','tree-follow-history');
  follow.classList.add('tree-history-follow');
  follow.hidden = true;
  historyList.tabIndex = 0;
  historyList.setAttribute('role','region');
  historyList.setAttribute('aria-labelledby',historyTitle.id);
  history.append(historyTitle, follow, historyList);
  historyRegion.append(history);
  code.append(historyRegion);
  q('.source-note').hidden = true;
  const tree = q('.memory-pane');
  tree.append(q('.tree-output'));
  q('.view-btns').remove();

  const sidebar = D.el('div','tree-sidebar');
  const stackTitle = D.el('h2','sec-title','호출 스택');
  stackTitle.tabIndex = -1;
  const stack = D.el('div','tree-stack');
  const example = D.el('details','tree-example');
  const exampleTitle = D.el('summary','sec-title','예제 정보');
  const info = D.el('div');
  example.append(exampleTitle, info);
  sidebar.append(stackTitle, stack, example);
  if (scenario.supplement) info.append(D.el('p','',scenario.supplement));
  info.append(D.el('p','','주소는 기호로 표시합니다.'));
  for (const source of scenario.sources.slice(1)) {
   info.append(D.el('h3','',source.label || source.id),D.el('pre','',source.text));
  }

  const headerTools = D.el('div','tree-header-tools');
  config.querySelector('h2').hidden = true;
  action('preset').parentElement.firstChild.remove();
  headerTools.append(config);
  header.insertBefore(headerTools,action('theme'));
  for (const [side, panel, label, content] of [
   ['left', left, '실행 코드', code],
   ['right', right, '호출 스택', sidebar],
  ]) {
   const toggle = action('toggle-'+side);
   toggle.setAttribute('aria-label',label+' 패널');
   toggle.title = label+' 패널';
   toggle.querySelector('span').textContent = label;
   panel.setAttribute('aria-label',label);
   const head = panel.querySelector('.panel-head');
   head.querySelector('h2').remove();
   panel.querySelector('.panel-inner').replaceChildren(head, content);
  }
  const playbackOptions = mountPlaybackOptions(app, button('','tree-options'));

  const dialog = D.el('dialog','tree-inspector');
  dialog.setAttribute('aria-labelledby','tree-inspector-title');
  const title = D.el('h2');
  title.id = 'tree-inspector-title';
  const closeButton = button('닫기','tree-close');
  const head = D.el('div','tree-inspector-head');
  head.append(title, closeButton);
  const memory = D.el('div','tree-inspector-body tree-memory');
  dialog.append(head, memory);
  q('.layout').append(dialog);

  let narrow = null, leftOpen = false, nodeId = null, frameId = null;
  let followedTop = 0;
  let resumeFrame = 0;
  const show = () => narrow ? dialog.showModal() : dialog.show();
  function syncPanels(state) {
   const changedMode = narrow!==state.narrow;
   narrow = state.narrow;
   leftOpen = state.leftOpen;
   const destination = !narrow && leftOpen ? code : tree;
   if (explanation.parentElement!==destination) destination.append(explanation);
   if (state.drawer) {
    playbackOptions.close(false);
    stop();
   }
   if (dialog.open && changedMode) {
    dialog.close();
    if (!narrow) right.inert = true;
    show();
    closeButton.focus({preventScroll:true});
   }
   if (leftOpen) syncHistory();
  }
  function close({restoreFocus = true, repaint = true} = {}) {
   if (!dialog.open) return;
   const selected = nodeId;
   nodeId = null;
   dialog.close();
   right.inert = !right.classList.contains('is-open');
   if (repaint) refresh();
   if (restoreFocus) {
    [...app.querySelectorAll('[data-node-id]')].find(el=>el.dataset.nodeId===selected)?.focus({preventScroll:true});
   }
  }
  function open(selectedNode) {
   playbackOptions.close(false);
   stop();
   nodeId = selectedNode;
   title.textContent = '노드 메모리';
   memory.scrollTop = 0;
   if (!narrow) right.inert = true;
   if (!dialog.open) show();
   refresh();
   closeButton.focus({preventScroll:true});
  }

  function click(event) {
   const target = event.target.closest('button');
   if (target?.matches('.tree-node')) open(target.dataset.nodeId);
   const name = target?.dataset.action;
   if (name==='tree-close') close();
   else if (name==='toggle-left' || name==='toggle-right') close({restoreFocus:false});
   else if (target===follow) {
    historyList.focus({preventScroll:true});
    follow.hidden = true;
    // A touch fling can deliver a final scroll offset after the resume tap.
    resumeFrame = requestAnimationFrame(() => {
     resumeFrame = 0;
     followedTop = historyList.scrollTop;
     syncHistory();
    });
    syncHistory();
   }
   else if (target?.dataset.inspectFrame) {
    frameId = frameId===target.dataset.inspectFrame ? null : target.dataset.inspectFrame;
    refresh();
   }
   if (event.target===dialog && narrow) {
    const rect = dialog.getBoundingClientRect();
    if (event.clientY<rect.top || event.clientX<rect.left || event.clientX>rect.right) close();
   }
  }
  function pauseAfterScroll() {
   if (!leftOpen || !follow.hidden || resumeFrame) return;
   const maxTop = historyList.scrollHeight - historyList.clientHeight;
   // A resize can clamp an earlier automatic position to the new scroll range.
   if (Math.abs(historyList.scrollTop - Math.min(followedTop, maxTop)) > 1) follow.hidden = false;
  }
  function syncHistory() {
   pauseAfterScroll();
   if (!leftOpen || !follow.hidden) return;
   const current = historyList.querySelector('[aria-pressed=true]');
   if (!current) return;
   const row = current.getBoundingClientRect();
   const top = historyList.getBoundingClientRect().top + historyList.clientTop;
   const target = top + (current.dataset.stepIndex==='0' ? row.height : historyList.clientHeight) / 2;
   historyList.scrollTop += Math.round(row.top + row.height / 2 - target);
   followedTop = historyList.scrollTop;
  }
  function cancel(event) { event.preventDefault(); close(); }
  function keydown(event) {
   if (event.defaultPrevented || event.key!=='Escape') return;
   if (playbackOptions.close()) {
    event.preventDefault();
   } else if (dialog.open && !narrow) {
    event.preventDefault();
    close();
   }
  }
  app.addEventListener('click',click);
  dialog.addEventListener('cancel',cancel);
  historyList.addEventListener('scroll',pauseAfterScroll);
  document.addEventListener('keydown',keydown);

  return {
   selection(step, view) {
    return view.nodes.find(node=>node.id===nodeId)?.keyCellId ??
     step.state.frames[frameId]?.parameterCellId ?? null;
   },
   paint(step, view, metadata, blocked) {
    const returned = step.state.frames[step.executed?.frameId];
    const ended = !step.diagnostic && returned?.lifetime==='ended' && returned.parameterCellId ? returned : null;
    const message = blocked ? '입력값을 확인해 주세요.' : step.diagnostic?.message || step.explanation || step.title;
    explanation.classList.toggle('is-error', blocked || Boolean(step.diagnostic));
    if (explanation.textContent!==message) explanation.textContent = message;
    if (nodeId!==null) memory.replaceChildren(D.renderNodeDetails(step,view,nodeId));
    const focused = stack.contains(document.activeElement) ? document.activeElement.dataset.inspectFrame : null;
    stack.replaceChildren(D.renderStackDetails(step,view,frameId,ended,metadata.tree.fields.key));
    if (focused) {
     const button = [...stack.querySelectorAll('[data-inspect-frame]')].find(el=>el.dataset.inspectFrame===focused);
     (button ?? stackTitle).focus({preventScroll:true});
    }
   },
   syncPanels,
   syncHistory,
   reset() {
    playbackOptions.close(false);
    cancelAnimationFrame(resumeFrame);
    resumeFrame = 0;
    follow.hidden = true;
    historyList.scrollTop = 0;
    followedTop = 0;
    frameId = null;
    close({restoreFocus:false,repaint:false});
   },
   destroy() {
    cancelAnimationFrame(resumeFrame);
    playbackOptions.destroy();
    close({restoreFocus:false,repaint:false});
    app.removeEventListener('click',click);
    dialog.removeEventListener('cancel',cancel);
    historyList.removeEventListener('scroll',pauseAfterScroll);
    document.removeEventListener('keydown',keydown);
   }
  };
 }

 D.mountTreeUi = mountTreeUi;
})(globalThis);
