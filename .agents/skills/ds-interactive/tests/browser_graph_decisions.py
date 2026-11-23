"""Check the rendered MST and topological-sort state at every supported step."""
from playwright.sync_api import expect
from browser_graph_layout import open_options


CHECK_STEPS = """({input, view}) => {
  const scenario = DSInteractive.scenario;
  const {vertices, edges} = scenario.graph;
  const {snapshots} = DSInteractive.compileScenario(scenario, input);
  const q = selector => document.querySelector(selector);
  const all = selector => [...document.querySelectorAll(selector)];
  const scrub = q('[data-action=scrub]');
  const watch = name => q('[data-study-watch="' + name + '"] .study-watch-value').textContent;
  const same = (actual, expected, label) => {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw Error(view + ' ' + q('#app').dataset.snapshot + ' ' + label + ': ' +
        JSON.stringify(actual) + ' ≠ ' + JSON.stringify(expected));
    }
  };
  for (const [index, step] of snapshots.entries()) {
    scrub.value = index;
    scrub.dispatchEvent(new Event('input', {bubbles: true}));
    const {cells, stdout} = step.state;
    const value = cell => cells[cell].value.value;
    const current = q('.code-line.current');
    const history = q('.step-list [aria-pressed="true"]');
    same(q('#app').dataset.snapshot, step.id, 'snapshot');
    same(Number(current.dataset.line), step.at.line, 'line');
    same(current.dataset.sourceId, step.at.sourceId, 'source');
    same(Number(history.dataset.stepIndex), index, 'history');
    same(q('.explanation').textContent, step.explanation, 'explanation');
    same(document.documentElement.scrollWidth, innerWidth, 'horizontal overflow');
    const candidate = value('candidate');
    const diagramEdges = all('.decision-edge');
    if (view === 'mst') {
      const weights = edges.map(([,, w], e) => e === 8 && input.setup === 'tie' ? 27 : w);
      const name = e => edges[e].slice(0, 2).join('–') + '(' + weights[e] + ')';
      const order = edges.map((_, e) => e).filter(e => value('edge.' + e) > 0)
        .sort((a, b) => value('edge.' + a) - value('edge.' + b));
      const total = order.reduce((sum, e) => sum + weights[e], 0);
      const accepted = diagramEdges.filter(el => ['chosen', 'chosen-current', 'cycle'].includes(el.dataset.status))
        .map(el => Number(el.dataset.edge)).sort();
      same(accepted, [...order].sort(), 'accepted edges');
      same(diagramEdges.length, edges.length, 'all edges');
      for (const edge of diagramEdges) same(Number(edge.textContent), weights[edge.dataset.edge], 'weight');
      const candidateShown = candidate >= 0 && index < snapshots.length - 1;
      same(watch('candidate'), candidateShown ? name(candidate) : '—', 'candidate');
      same(watch('count'), order.length + ' / 6', 'edge count');
      same(q('[data-decision-state=mst-result]').textContent,
        (order.map(name).join(' · ') || '아직 없음') + '  |  총비용 ' + total, 'total and order');
      if (input.mode === 'prim') {
        const inside = new Set(['a', ...order.flatMap(e => edges[e].slice(0, 2))]);
        same(all('.decision-node[data-status=chosen]').map(el => el.dataset.node), [...inside].sort(), 'tree nodes');
        const boundary = edges.map(([a, b], e) => inside.has(a) !== inside.has(b) ? e : -1)
          .filter(e => e !== -1 && (!candidateShown || e !== candidate));
        same(diagramEdges.filter(el => el.dataset.status === 'boundary').map(el => Number(el.dataset.edge)),
          boundary, 'boundary edges');
      }
    } else {
      const expectedEdges = edges.map((_, e) => e).filter(e => value('edge.' + e));
      const present = diagramEdges.filter(el => el.dataset.status !== 'current').map(el => Number(el.dataset.edge));
      same(present, expectedEdges, 'active arrows');
      const removed = step.writes.find(write => write.cellId.startsWith('edge.'));
      same(diagramEdges.filter(el => el.dataset.status === 'current').map(el => el.dataset.edge),
        removed ? [removed.cellId.split('.')[1]] : [], 'removed arrow');
      const remaining = vertices.map(([v]) => v).filter(v => value('node.' + v));
      const inDegree = v => expectedEdges.filter(e => edges[e][1] === v).length;
      const ready = remaining.filter(v => v !== candidate && inDegree(v) === 0);
      for (const [v] of vertices) {
        const badge = q('.decision-node[data-node="' + v + '"] .decision-degree text');
        same(badge ? Number(badge.textContent) : null, remaining.includes(v) ? inDegree(v) : null, 'degree of ' + v);
      }
      same(all('.decision-node[data-status=chosen]').map(el => Number(el.dataset.node)), ready, 'ready nodes');
      same(watch('candidate'), remaining.includes(candidate) ? String(candidate) : '—', 'current vertex');
      same(watch('ready'), ready.join(', ') || '없음', 'ready card');
      same(q('[data-decision-state=topo-result]').textContent, stdout.map(v => v.trim()).join(' → ') || '아직 출력 없음', 'output');
      same(q('[data-decision-state=cycle]')?.textContent ?? null, value('failure') ? '0 → 2 → 5 → 0' : null, 'cycle');
    }
    for (const write of step.writes.filter(write => write.cellId === 'candidate')) {
      same(q('[data-study-watch=candidate]').hasAttribute('data-written'), true, 'candidate write');
    }
  }
  return snapshots.length;
}"""


def check_page(page, view):
    preset = page.locator('[data-action=preset]')
    app = page.locator('#app')
    cases = page.evaluate("""() => {
        const {inputs, presets} = DSInteractive.scenario;
        return [{id: 'default', input: Object.fromEntries(inputs.map(field => [field.key, field.default]))}, ...presets];
    }""")
    checked = 0
    for case in cases:
        preset.select_option(case['id'])
        expect(app).to_have_attribute('data-index', '0')
        checked += page.evaluate(CHECK_STEPS, {'input': case['input'], 'view': view})
        expect(page.locator('[data-action=next]')).to_be_disabled()

    if view == 'mst':
        preset.select_option('tie-kruskal')
        page.locator('[data-action=play]').click()
        page.locator('[data-mode-value=prim]').click()
        expect(app).to_have_attribute('data-playing', 'false')
        expect(app).to_have_attribute('data-index', '0')
        expect(preset).to_have_value('tie-prim')
        expect(page.locator('.code-line.current')).to_have_attribute('data-source-id', 'prim')
    else:
        preset.select_option('cycle')
        # Scrubbing every step above also verifies rewinding; exercise the actual output jump here.
        popup = open_options(page)
        popup.locator('[data-action=next-output]').click()
        expect(page.locator('[data-decision-state=topo-result]')).to_have_text('1')
        popup = open_options(page)
        popup.locator('[data-action=next-output]').click()
        expect(page.locator('[data-decision-state=topo-result]')).to_have_text('1 → 4')
        popup = open_options(page)
        popup.locator('[data-action=previous-output]').click()
        expect(page.locator('[data-decision-state=topo-result]')).to_have_text('1')

    preset.select_option('default')
    popup = open_options(page)
    popup.locator('[data-action=last]').click()
    expect(page.locator('[data-action=next]')).to_be_disabled()
    popup = open_options(page)
    popup.locator('[data-action=first]').click()
    expect(app).to_have_attribute('data-index', '0')
    return len(cases), checked
