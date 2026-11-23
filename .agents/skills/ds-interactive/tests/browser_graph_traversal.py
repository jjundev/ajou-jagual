"""Exercise the published graph scenes against every recorded state in offline Chromium."""
from playwright.sync_api import expect
from browser_graph_layout import open_options


CHECK_SCENE = r"""({input, first, last}) => {
  const app = document.querySelector('#app');
  const scrub = app.querySelector('[data-action=scrub]');
  const trace = DSInteractive.compileScenario(DSInteractive.scenario, input);
  const q = selector => app.querySelector(selector);
  const names = selector => [...app.querySelectorAll(selector)].map(e => e.firstChild.textContent);
  const ensure = (value, label, index) => { if (!value) throw Error(label + ' step=' + index); };
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  for (let index = first; index < Math.min(last, trace.snapshots.length); ++index) {
    const snapshot = trace.snapshots[index];
    scrub.value = index;
    scrub.dispatchEvent(new Event('input', {bubbles:true}));
    ensure(app.dataset.snapshot === snapshot.id && q('.memory').dataset.step === snapshot.id, 'snapshot', index);
    ensure(q('.explanation').textContent === snapshot.explanation, 'explanation', index);
    const line = q('.code-line.current');
    ensure(line.dataset.sourceId === snapshot.at.sourceId && Number(line.dataset.line) === snapshot.at.line, 'code', index);
    ensure(line.classList.contains('executed') === (snapshot.phase === 'after'), 'executed line', index);
    const nextAt = (snapshot.phase === 'before' ? snapshot : trace.snapshots[index + 1])?.at;
    const marker = q('.graph-next-line,.study-next-line');
    ensure(marker?.dataset.sourceId === nextAt?.sourceId &&
      marker?.dataset.line === (nextAt ? String(nextAt.line) : undefined), 'next code line', index);
    ensure(Number(q('[data-action=step][aria-pressed=true]').dataset.stepIndex) === index, 'history', index);
    const {cells, frames, activeFrame: active, stdout} = snapshot.state;
    const value = id => cells[id]?.value?.value;
    const vertices = DSInteractive.scenario.graph.positions.map((_, i) => i);
    const parent = vertices.map(v => value('graph.parent.' + v));
    const chosen = [...app.querySelectorAll('.graph-edge.is-chosen')].map(e => e.dataset.edge).sort();
    const expected = parent.flatMap((p, v) => p === -1 ? [] : [[p, v].sort((a,b)=>a-b).join('-')]).sort();
    ensure(same(chosen, expected), 'discovery edge', index);
    const actual = q('.graph-vertex.is-current')?.dataset.vertex;
    const current = value(active + '.v') ?? value(active + '.i');
    ensure(actual === (vertices.includes(current) ? String(current) : undefined), 'current vertex', index);
    const read = snapshot.reads.find(id => id.startsWith('graph.a.'));
    const expectedRead = read?.split('.').slice(2).join('-');
    ensure(q('.graph-matrix .is-reading')?.dataset.matrix === expectedRead, 'matrix read', index);
    const reading = [...app.querySelectorAll('.graph-edge.is-reading')].map(e => e.dataset.edge);
    const readingEdge = read && value(read) ? [expectedRead.split('-').sort().join('-')] : [];
    ensure(same(reading, readingEdge), 'checked edge', index);
    ensure(same(names('#panel-right [data-visited]'), vertices.map(v => String(value('graph.visited.' + v)))), 'visited', index);
    ensure(same(names('[data-graph-state=output] li'), stdout.map(v => v.trim())), 'output', index);
    if (input.mode === 'bfs') {
      const queue = [];
      for (let i = value(active + '.head'); i < value(active + '.tail'); i++) queue.push(String(value(active + '.q.' + i)));
      ensure(same(names('#panel-right [data-graph-state=queue] li'), queue), 'queue', index);
    } else {
      const stack = [];
      for (let id = active; id; id = frames[id].caller) {
        stack.push(frames[id].functionId + '(' + (value(id + '.v') ?? '') + ')');
      }
      ensure(same(names('#panel-right [data-graph-state=stack] li'), stack), 'stack', index);
    }
    const watch = key => q('[data-graph-watch=' + key + '] .graph-watch-value,[data-study-watch=' + key + '] .study-watch-value').textContent;
    ensure(watch('vertex') === (vertices.includes(current) ? String(current) : '—'), 'current value', index);
    const count = value('graph.count');
    if (count !== undefined) ensure(watch('count') === String(count), 'count', index);
    else ensure(watch('neighbor') === (read?.split('.').at(-1) ?? '—'), 'neighbor', index);
    ensure(!snapshot.diagnostic, 'diagnostic', index);
  }
  return trace.snapshots.length;
}"""


def check_page(page, width):
    action = lambda name: page.locator(f'[data-action={name}]')
    app = page.locator('#app')
    setup = page.locator('[data-input=setup]')
    choices = setup.locator('option').evaluate_all('(options) => options.map(o => o.value)')
    modes = page.locator('[data-mode-value]').evaluate_all('(buttons) => buttons.map(b => b.dataset.modeValue)')
    combinations = 0
    checked = 0

    for mode in modes or [None]:
        for choice in choices:
            setup.select_option(choice)
            args = {'setup': choice}
            if mode:
                page.locator(f'[data-mode-value={mode}]').click()
                assert page.locator(f'[data-mode-value={mode}]').get_attribute('aria-pressed') == 'true'
                args['mode'] = mode
            expect(app).to_have_attribute("data-index", "0")
            count = int(action('scrub').get_attribute('max')) + 1
            for index in range(0, count, 32):
                assert count == page.evaluate(CHECK_SCENE, {'input': args, 'first': index, 'last': index+32})
            expect(action('next')).to_be_disabled()
            action('prev').click()
            expect(app).to_have_attribute('data-index', str(count-2))
            open_options(page)
            action('first').click()
            expect(app).to_have_attribute('data-index', '0')
            combinations += 1
            checked += count

    action('play').click()
    expect(app).to_have_attribute('data-playing', 'true')
    setup.select_option(choices[0])
    expect(app).to_have_attribute('data-playing', 'false')
    expect(app).to_have_attribute('data-index', '0')

    page.locator('.stage-viewport').focus()
    page.keyboard.press('ArrowRight')
    expect(app).to_have_attribute('data-index', '1')
    page.keyboard.press('Home')
    expect(app).to_have_attribute('data-index', '0')
    page.keyboard.press('End')
    expect(action('next')).to_be_disabled()
    action('prev').click()
    open_options(page)
    for speed in ('0.5', '1', '2'):
        button = page.locator(f'[data-speed="{speed}"]')
        button.click()
        expect(button).to_have_attribute('aria-pressed', 'true')
    action('play').click()
    expect(app).to_have_attribute('data-playing', 'false', timeout=1800)
    expect(action('next')).to_be_disabled()

    if width >= 1280:
        page.locator('[data-step-index="2"]').click()
        expect(app).to_have_attribute('data-index', '2')

    open_options(page)
    action('first').click()
    expect(action('previous-output')).to_be_disabled()
    action('next-output').click()
    first_output = int(app.get_attribute('data-index'))
    expect(page.locator(':is(.graph-result,.study-result) li')).to_have_count(1)
    action('next-output').click()
    expect(page.locator(':is(.graph-result,.study-result) li')).to_have_count(2)
    action('previous-output').click()
    expect(app).to_have_attribute('data-index', str(first_output))
    action('first').click()
    page.keyboard.press('Escape')
    action('next').click()
    return combinations, checked
