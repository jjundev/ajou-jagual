"""Exercise the published graph scenes against every recorded state in offline Chromium."""
from playwright.sync_api import expect


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
    ensure(q('.graph-message p').textContent === snapshot.explanation, 'explanation', index);
    const line = q('.code-line.current');
    ensure(line.dataset.sourceId === snapshot.at.sourceId && Number(line.dataset.line) === snapshot.at.line, 'code', index);
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
    ensure(same(names('[data-visited]'), vertices.map(v => String(value('graph.visited.' + v)))), 'visited', index);
    ensure(same(names('[data-graph-state=output] li'), stdout.map(v => v.trim())), 'output', index);
    if (input.mode === 'bfs') {
      const queue = [];
      for (let i = value(active + '.head'); i < value(active + '.tail'); i++) queue.push(String(value(active + '.q.' + i)));
      ensure(same(names('[data-graph-state=queue] li'), queue), 'queue', index);
    } else {
      const stack = [];
      for (let id = active; id; id = frames[id].caller) {
        stack.push(frames[id].functionId + '(' + (value(id + '.v') ?? '') + ')');
      }
      ensure(same(names('[data-graph-state=stack] li'), stack), 'stack', index);
    }
    const count = value('graph.count');
    if (count !== undefined) ensure(q('.graph-count').textContent === 'count = ' + count, 'count', index);
    ensure(!snapshot.diagnostic, 'diagnostic', index);
  }
  return trace.snapshots.length;
}"""


def boundaries(page, width, height):
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    for selector in ['.topbar', '.stage', '.graph-figure', '.graph-matrix', '.playbar', '[data-action=last]']:
        box = page.locator(selector).bounding_box()
        assert box and box["x"] >= -1 and box["x"] + box["width"] <= width + 1, (selector, width, box)
    play = page.locator('.playbar').bounding_box()
    assert play["y"] + play["height"] <= height + 1
    for choice in page.locator('.transport-buttons button, .speeds button').all():
        box = choice.bounding_box()
        assert box["width"] >= 44 and box["height"] >= 44, box


def check_page(page, width, height):
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
            boundaries(page, width, height)
            action('prev').click()
            expect(app).to_have_attribute('data-index', str(count-2))
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
    for speed in ('0.5', '1', '2'):
        button = page.locator(f'[data-speed="{speed}"]')
        button.click()
        expect(button).to_have_attribute('aria-pressed', 'true')
    action('play').click()
    expect(app).to_have_attribute('data-playing', 'false', timeout=1800)
    expect(action('next')).to_be_disabled()

    left = action('toggle-left')
    left.click()
    if width < 1024:
        expect(page.locator('#panel-left')).to_have_attribute('aria-modal', 'true')
        expect(page.locator('#panel-left .code')).to_be_visible()
        page.keyboard.press('Shift+Tab')
        assert page.evaluate('document.activeElement.closest("#panel-left") !== null')
        page.keyboard.press('Escape')
        expect(left).to_be_focused()
        action('toggle-right').click()
        expect(page.locator('#panel-right')).to_have_attribute('aria-modal', 'true')
        page.locator('#panel-right button[data-action=close-panels]').click()
        expect(action('toggle-right')).to_be_focused()
    else:
        expect(left).to_have_attribute('aria-expanded', 'false')
        left.click()
        handle = page.locator('[data-resize=left]')
        handle.focus()
        before = int(handle.get_attribute('aria-valuenow'))
        page.keyboard.press('ArrowRight')
        assert int(handle.get_attribute('aria-valuenow')) > before
        page.keyboard.press('Home')
        expect(page.locator('#panel-left .code')).to_be_visible()
        page.locator('[data-step-index="2"]').click()
        expect(app).to_have_attribute('data-index', '2')
        action('last').click()

    boundaries(page, width, height)
    return combinations, checked
