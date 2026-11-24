"""Compare the bridge and degree screens with each preset's trace."""
from playwright.sync_api import expect
from browser_graph_layout import open_options


CHECK_SCENE = r"""({kind, input}) => {
  const app = document.querySelector('#app');
  const q = selector => app.querySelector(selector);
  const all = selector => [...app.querySelectorAll(selector)];
  const scrub = q('[data-action=scrub]');
  const scenario = DSInteractive.scenario;
  const trace = DSInteractive.compileScenario(scenario, input);
  const same = (actual, expected, message) => {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw Error(message + ' at step ' + scrub.value + ': ' + JSON.stringify({actual, expected}));
    }
  };
  const {vertices} = scenario.graph;
  same(Number(scrub.max) + 1, trace.snapshots.length, 'number of steps');
  for (const [index, snapshot] of trace.snapshots.entries()) {
    scrub.value = index;
    scrub.dispatchEvent(new Event('input', {bubbles: true}));
    const {cells} = snapshot.state;
    const value = id => cells[id]?.value.value;
    same(app.dataset.snapshot, snapshot.id, 'snapshot');
    same(q('.memory').dataset.step, snapshot.id, 'scene');
    same(q('.explanation').textContent, snapshot.explanation, 'step description');
    same(q('.code-line.current').dataset.sourceId, snapshot.at.sourceId, 'source');
    same(Number(q('.code-line.current').dataset.line), snapshot.at.line, 'source line');
    same(q('.code-line.current').classList.contains('executed'), snapshot.phase === 'after', 'executed line');
    const nextAt = (snapshot.phase === 'before' ? snapshot : trace.snapshots[index + 1])?.at;
    const marker = q('.graph-next-line,.study-next-line');
    same(marker?.dataset.sourceId, nextAt?.sourceId, 'next code source');
    same(marker?.dataset.line, nextAt ? String(nextAt.line) : undefined, 'next code line');
    same(Number(q('[data-action=step][aria-pressed=true]').dataset.stepIndex), index, 'history');
    same(snapshot.diagnostic, null, 'unexpected diagnostic');
    const watch = key => q('[data-graph-watch=' + key + '] .graph-watch-value,[data-study-watch=' + key + '] .study-watch-value').textContent;
    const vertex = q('.gi-current')?.dataset.graphVertex;
    const edge = q('.gi-edge.gi-focus')?.dataset.graphEdge;
    if (kind === 'bridges') {
      const bridges = scenario.graph.bridges.filter(([id]) => cells['order.' + id]);
      const route = [vertices[value('start')][0]];
      const crossed = bridges.filter(([id]) => value('order.' + id));
      for (const [, from, to] of [...crossed].sort((a, b) => value('order.' + a[0]) - value('order.' + b[0]))) {
        route.push(route.at(-1) === from ? to : from);
      }
      same(vertex, route.at(-1), 'current location');
      same(watch('position'), route.at(-1), 'location card');
      same(watch('crossings'), crossed.length + '/' + bridges.length, 'crossings card');
      same(q('.gi-route').textContent, route.join(' → '), 'route');
      same(all('.gi-edge.gi-used').map(e => e.dataset.graphEdge), crossed.map(([id]) => id), 'crossed bridges');
      same(edge, (snapshot.reads[0] ?? snapshot.writes[0]?.cellId)?.split('.')[1], 'bridge highlight');
      for (const [id] of vertices) {
        const count = bridges.filter(([, from, to]) => from === id || to === id).length;
        same(q('[data-stat=' + id + '] dd').textContent, count + (count % 2 ? ' · 홀수' : ' · 짝수'), 'degree card');
      }
      same(Boolean(q('.gi-verdict')), snapshot.at.line === 5, 'Euler verdict');
    } else {
      const v = value('v');
      const read = snapshot.reads[0];
      const {rowLine, columnLine} = scenario.graph;
      const line = snapshot.at.line;
      const ids = vertices.map(([id]) => id);
      same(vertex, String(v), 'selected vertex');
      same(watch('vertex'), String(v), 'vertex card');
      same(watch('axis'), line === rowLine ? v + '행' : line === columnLine ? v + '열' : '—', 'axis card');
      same(all('[data-matrix-cell]').map(e => Number(e.textContent)),
        ids.flatMap(from => ids.map(to => value('m.' + from + '.' + to))), 'matrix');
      same(all('td.gi-axis').map(e => e.dataset.matrixCell),
        line === rowLine ? ids.map(i => 'm.' + v + '.' + i)
          : line === columnLine ? ids.map(i => 'm.' + i + '.' + v) : [], 'current row or column');
      same(q('td.gi-focus')?.dataset.matrixCell, read, 'cell highlight');
      same(edge, read && value(read) ? read.slice(2).replace('.', '-') : undefined, 'arrow highlight');
      same(all('[data-stat] dd').map(e => Number(e.textContent)), [value('out'), value('in')], 'accumulators');
      same(q('[data-stat].gi-counter')?.dataset.stat, snapshot.writes[0]?.cellId, 'updated accumulator');
    }
  }
  return trace.snapshots.length;
}"""


def check_page(page, kind):
    action = lambda name: page.locator(f'[data-action={name}]')
    app = page.locator('#app')
    cases = page.evaluate("""() => {
      const {inputs, presets} = DSInteractive.scenario;
      return [{id: 'default', input: Object.fromEntries(inputs.map(d => [d.key, d.default]))}, ...presets];
    }""")
    checked = 0
    for case in cases:
        action('preset').select_option(case['id'])
        expect(app).to_have_attribute('data-index', '0')
        checked += page.evaluate(CHECK_SCENE, {'kind': kind, 'input': case['input']})
        expect(action('next')).to_be_disabled()
        open_options(page)
        action('first').click()

    action('preset').select_option('default')
    action('play').click()
    expect(app).to_have_attribute('data-playing', 'true')
    field = page.locator('[data-input=start]' if kind == 'bridges' else '[data-input=vertex]')
    direct = action('preset').locator('option[data-header-choice]')
    if kind == 'bridges' and direct.count():
        action('preset').select_option(direct.nth(1).get_attribute('value'))
        expect(field).to_have_value('B')
    elif kind == 'bridges':
        field.select_option(index=1)
    else:
        field.fill('')
        expect(field).to_have_attribute('aria-invalid', 'true')
        expect(action('play')).to_be_disabled()
        expect(page.locator('.input-error')).not_to_have_text('')
        field.fill('2')
        expect(field).to_have_attribute('aria-invalid', 'false')
    if kind == 'degree' and direct.count():
        expect(action('preset')).to_have_value(next(case['id'] for case in cases if case['input'] == {'matrix': 'g3', 'vertex': 2}))
    elif not direct.count():
        expect(action('preset')).to_have_value('custom')
    expect(app).to_have_attribute('data-playing', 'false')
    expect(app).to_have_attribute('data-index', '0')
    action('preset').select_option('default')
    page.locator('.stage-viewport').focus()
    page.keyboard.press('ArrowRight')
    expect(app).to_have_attribute('data-index', '1')
    page.keyboard.press('End')
    expect(action('next')).to_be_disabled()
    action('prev').click()
    open_options(page)
    page.locator('[data-speed="2"]').click()
    action('play').click()
    expect(app).to_have_attribute('data-playing', 'false', timeout=1800)
    expect(action('next')).to_be_disabled()
    open_options(page)
    action('first').click()
    page.keyboard.press('Escape')
    action('next').click()
    return len(cases), checked
