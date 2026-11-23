(function (root) {
  'use strict';
  const D = root.DSInteractive;

  function mountPlayer(app, scenario, graph) {
    const q = selector => app.querySelector(selector);
    const events = new AbortController();
    const on = (target, event, listener) => target.addEventListener(event, listener, {signal: events.signal});
    const tree = scenario.kind === 'c-tree';
    const defaults = Object.fromEntries(scenario.inputs.map(field => [field.key, field.default]));
    const presets = new Map(scenario.presets.map(item => [item.id, item.input]));
    const [onlyField] = scenario.inputs;
    const presetCoversTree = tree && scenario.inputs.length === 1 && onlyField.type === 'enum' &&
      onlyField.options.every(option => option.value === onlyField.default ||
        scenario.presets.some(item => item.input[onlyField.key] === option.value));
    const play = q('[data-action=play]');
    const scrub = q('[data-action=scrub]');
    const preset = q('[data-action=preset]');
    const modes = q('.modes');
    let input = {...defaults};
    let trace, selection;
    let step = 0;
    let speed = 1;
    let timer = null;
    app.dataset.kind = scenario.kind;
    q('h1').textContent = document.title = scenario.title;
    q('.takeaway').textContent = scenario.takeaway || '';
    q('.provenance-text').textContent = scenario.sources.map(source =>
      [source.label || source.id, source.provenance?.path, source.provenance?.page && 'p' + source.provenance.page,
        source.provenance?.section, source.provenance?.adjustments].filter(Boolean).join(' · ')).join('\n');

    const defaultLabel = presetCoversTree ? onlyField.options.find(option => option.value === onlyField.default).label : '기본 입력';
    preset.append(new Option(defaultLabel, 'default'));
    for (const item of scenario.presets) preset.append(new Option(item.label, item.id));
    if (presetCoversTree) q('.inputs').hidden = true;

    for (const field of scenario.inputs) {
      const label = D.el('label', '', field.label);
      const control = document.createElement(field.type === 'enum' ? 'select' : 'input');
      control.dataset.input = field.key;
      control.setAttribute('aria-label', field.label);
      if (field.type === 'integer') {
        control.type = 'number';
        control.min = field.min;
        control.max = field.max;
        control.step = 1;
      } else {
        for (const option of field.options) control.append(new Option(option.label, option.value));
      }
      if (field.type === 'enum' && field.key === 'mode') {
        label.hidden = true;
        modes.hidden = false;
        for (const option of field.options) {
          const button = D.el('button', '', option.label);
          button.type = 'button';
          button.dataset.modeValue = option.value;
          modes.append(button);
        }
      }
      label.append(control);
      q('.inputs').append(label);
      const change = () => {
        input[field.key] = field.type === 'integer' ? control.valueAsNumber : control.value;
        preset.value = 'default';
        recompile();
      };
      on(control, field.type === 'integer' ? 'input' : 'change', change);
    }

    const design = graph || (tree ? D.studyTree(app, scenario, {stop, repaint: paint}) :
      D.studyMemory(app, scenario));
    const ui = D.mountStudyUi(app, design, {jumpOutput, signal: events.signal});
    const shell = D.mountShell(app, {
      onStep: move,
      onSpeed(value) {
        speed = value;
        if (timer !== null) {
          clearInterval(timer);
          timer = setInterval(advance, 900 / speed);
        }
      },
      redraw: ui.redraw,
      onPanelsChange(state) {
        ui.syncPanels(state);
        if (state.drawer) stop();
      },
    });
    const entries = () => trace.lineSteps || trace.snapshots;

    function updatePlay(playing) {
      app.dataset.playing = String(playing);
      play.setAttribute('aria-label', playing ? '일시정지' : '재생');
      play.innerHTML = playing
        ? '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5h4v14H7zM14 5h4v14h-4z"/></svg>'
        : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5l12 7-12 7z"/></svg>';
    }
    function stop() {
      clearInterval(timer);
      timer = null;
      updatePlay(false);
    }
    function advance() {
      step++;
      paint();
      if (step >= entries().length - 1) stop();
    }
    function toggle() {
      if (play.disabled) return;
      if (timer !== null) { stop(); return; }
      if (entries().length === 1) return;
      if (step === entries().length - 1) step = 0;
      updatePlay(true);
      paint();
      timer = setInterval(advance, 900 / speed);
    }
    function move(index) {
      if (play.disabled) return;
      stop();
      step = Math.max(0, Math.min(entries().length - 1, index));
      paint();
    }
    function outputStep(direction) {
      const steps = entries();
      for (let i = step + direction; i > 0 && i < steps.length; i += direction) {
        if (steps[i].state.stdout.length > steps[i - 1].state.stdout.length) return i;
      }
      return -1;
    }
    function jumpOutput(direction) {
      const target = outputStep(direction);
      if (target >= 0) move(target);
    }

    function paintCode(snapshot, following) {
      const executed = tree ? snapshot.executed?.at : snapshot.phase !== 'before' && snapshot.at;
      const next = tree ? snapshot.next?.at : snapshot.phase === 'before' ? snapshot.at : following?.at;
      const primary = trace.sources.find(source => source.id === (executed || next)?.sourceId) || trace.sources[0];
      const code = q('.code');
      const currentRow = location => {
        const source = trace.sources.find(item => item.id === location.sourceId);
        return codeRow(source, location.line, source.text.split('\n')[location.line - 1]);
      };
      function codeRow(source, line, text) {
        const same = loc => loc?.sourceId === source.id && loc?.line === line;
        const row = D.el('div', 'code-line');
        row.dataset.sourceId = source.id;
        row.dataset.line = line;
        row.classList.toggle('current', same(executed || next));
        row.classList.toggle('executed', same(executed));
        row.classList.toggle('study-next-line', same(next));
        if (same(executed || next)) row.setAttribute('aria-current', 'step');
        row.append(D.el('span', 'line-number', line), D.el('span', '', text));
        return row;
      }
      const lines = primary.text.split('\n').map((line, index) => codeRow(primary, index + 1, line));
      if (next && next.sourceId !== primary.id) {
        const auxiliary = currentRow(next);
        auxiliary.classList.add('study-next-source');
        const source = trace.sources.find(item => item.id === next.sourceId);
        auxiliary.lastElementChild.prepend((source.label || source.id) + ' · ');
        lines.unshift(auxiliary);
      }
      code.replaceChildren(...lines);
      code.dataset.step = snapshot.id;
      const active = code.querySelector('.current');
      if (active) {
        const row = active.getBoundingClientRect(), visible = code.getBoundingClientRect();
        if (row.top < visible.top) code.scrollTop += row.top - visible.top;
        else if (row.bottom > visible.bottom) code.scrollTop += row.bottom - visible.bottom;
      }
    }

    function paint() {
      const steps = entries();
      const snapshot = steps[step];
      app.dataset.snapshot = snapshot.id;
      app.dataset.index = step;
      app.dataset.activeFrame = snapshot.state.activeFrame ?? '';
      q('output[data-step]').textContent = `${step} / ${steps.length - 1}`;
      q('output[data-step]').dataset.step = snapshot.id;
      scrub.max = steps.length - 1;
      scrub.value = step;
      for (const button of modes.querySelectorAll('button')) {
        button.setAttribute('aria-pressed', String(button.dataset.modeValue === input.mode));
      }
      paintCode(snapshot, steps[step + 1]);
      ui.paint(snapshot, {selection, trace, blocked: play.disabled,
        hasOutput: steps.at(-1).state.stdout.length > steps[0].state.stdout.length,
        hasPreviousOutput: outputStep(-1) >= 0, hasNextOutput: outputStep(1) >= 0});
      for (const action of ['first', 'prev']) q('[data-action=' + action + ']').disabled = step === 0 || play.disabled;
      for (const action of ['last', 'next']) q('[data-action=' + action + ']').disabled = step === steps.length - 1 || play.disabled;
      shell.update(trace, steps, step, play.disabled);
      ui.syncHistory();
    }

    function recompile() {
      stop();
      selection = null;
      step = 0;
      ui.reset();
      const issues = D.validateInput(scenario.inputs, input);
      q('.input-error').textContent = issues.map(issue => issue.message).join(' ');
      for (const control of app.querySelectorAll('[data-input]')) {
        const value = input[control.dataset.input];
        control.value = Number.isNaN(value) ? '' : value;
        control.setAttribute('aria-invalid', String(issues.some(issue => issue.path === control.dataset.input)));
      }
      play.disabled = scrub.disabled = Boolean(issues.length);
      if (!issues.length) trace = D.compileScenario(scenario, input);
      paint();
    }

    on(preset, 'change', () => {
      input = {...(preset.value === 'default' ? defaults : presets.get(preset.value))};
      recompile();
    });
    on(scrub, 'input', () => move(Number(scrub.value)));
    on(app, 'click', event => {
      const button = event.target.closest('button');
      if (button?.matches('.study-memory-cells button[data-cell-id]')) {
        selection = button.dataset.cellId;
        paint();
      }
      if (button?.dataset.modeValue !== undefined) {
        input.mode = button.dataset.modeValue;
        preset.value = 'default';
        recompile();
      }
      switch (button?.dataset.action) {
        case 'first': move(0); break;
        case 'prev': move(step - 1); break;
        case 'next': move(step + 1); break;
        case 'last': move(entries().length - 1); break;
        case 'play': toggle(); break;
        case 'theme': {
          const dark = document.documentElement.dataset.theme !== 'dark';
          document.documentElement.dataset.theme = dark ? 'dark' : 'light';
          button.innerHTML = dark
            ? '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4 4l2 2m12 12 2 2M2 12h2m16 0h2M4 20l2-2M18 6l2-2"/></svg>'
            : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg>';
          button.setAttribute('aria-label', dark ? '밝은 테마로 전환' : '어두운 테마로 전환');
          button.title = button.getAttribute('aria-label');
          break;
        }
      }
    });
    on(document, 'keydown', event => {
      if (event.defaultPrevented || app.querySelector('dialog:modal,[aria-modal=true]') ||
        event.target.matches?.('input,select,textarea,button,summary,.step-list')) return;
      const actions = {
        ' ': toggle, ArrowLeft: () => move(step - 1), ArrowRight: () => move(step + 1),
        Home: () => move(0), End: () => move(entries().length - 1),
      };
      if (Object.hasOwn(actions, event.key)) { event.preventDefault(); actions[event.key](); }
    });
    recompile();
    return {destroy() {
      stop();
      shell.destroy();
      ui.destroy();
      events.abort();
    }};
  }

  D.mountPlayer = mountPlayer;
  // Existing graph renderers already supply the four view regions.
  D.mountGraphShell = mountPlayer;
})(globalThis);
