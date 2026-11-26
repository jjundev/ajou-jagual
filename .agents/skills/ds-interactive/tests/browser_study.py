"""Browser contract for the common learning UI, independent of scene semantics."""
from playwright.sync_api import expect
from browser_preset import check_preset_label

from browser_graph_layout import open_options

VIEWPORTS = [(1440, 900), (1280, 800), (1279, 800), (375, 812), (320, 812)]
HEADER_VIEWPORTS = [(720, 812), (721, 812), (900, 812), (901, 812)]
MOBILE_STAGES = ('initial', 'middle', 'last')


def check_header_layout(page):
    page.evaluate("""() => {
      const header = document.querySelector('.topbar');
      const selector = [...header.querySelectorAll('select')].find(control => control.checkVisibility());
      const modes = header.querySelector('.modes');
      const theme = header.querySelector('[data-action=theme]');
      const caseControls = modes.checkVisibility() ? [selector, modes] : [selector];
      const dropdown = selector.getBoundingClientRect();
      const themeBox = theme.getBoundingClientRect();
      if (innerWidth <= 900) {
        const firstRowBottom = Math.max(themeBox.bottom, header.querySelector('.brand').getBoundingClientRect().bottom);
        if (caseControls.some(control => control.getBoundingClientRect().top < firstRowBottom - 1)) {
          throw Error('Study header: the case and mode controls must sit below the title and theme');
        }
        return;
      }
      const controls = [...caseControls, theme].map(control => control.getBoundingClientRect());
      if (Math.abs((dropdown.top + dropdown.bottom) / 2 - (themeBox.top + themeBox.bottom) / 2) > 1 ||
          controls.slice(1).some((control, index) => {
            const gap = control.left - controls[index].right;
            return gap < 0 || gap > 9 || control.top >= dropdown.bottom || control.bottom <= dropdown.top;
          })) {
        throw Error('Study header: the horizontal controls must stay together without an empty column');
      }
    }""")


def check_controls(page):
    """Measure every option and the current control content with loaded fonts."""
    page.evaluate(r"""() => {
      const q = selector => [...document.querySelectorAll(selector)];
      const verify = (ok, message) => { if (!ok) throw Error('Study controls: ' + message); };
      const controls = q('.study-header-tools :is(select,button),.study-stage-inputs :is(input,select)')
        .filter(control => control.checkVisibility());
      const primarySelector = document.querySelector('[data-action=preset]').closest('label').hidden
        ? '.study-header-tools .inputs label:not([hidden]) select' : '.study-header-tools [data-action=preset]';
      verify(document.querySelector(primarySelector)?.checkVisibility(), 'case selector is absent or out of position');
      const mode = DSInteractive.scenario.inputs.find(field => field.key === 'mode' && field.type === 'enum');
      if (mode) verify(q('.study-header-tools .modes button').filter(button => button.checkVisibility()).length === mode.options.length,
        'mode controls are incomplete');
      const viewportWidth = document.documentElement.clientWidth;
      for (const control of q('.topbar > button,.transport-buttons button,.study-speed-trigger')) {
        const box = control.getBoundingClientRect();
        verify(box.width >= 44 && box.height >= 44 && box.left >= -1 && box.right <= viewportWidth + 1,
          (control.getAttribute('aria-label') || control.textContent) + ' is out of bounds or too small');
      }
      verify(document.documentElement.scrollWidth <= viewportWidth && innerWidth === viewportWidth,
        'document extends beyond the viewport');
      const top = document.querySelector('.topbar').getBoundingClientRect();
      const stage = document.querySelector('.stage-viewport').getBoundingClientRect();
      const playback = document.querySelector('.playbar').getBoundingClientRect();
      verify(top.top >= 0 && stage.top >= top.bottom - 1 && playback.bottom <= innerHeight + 1,
        'header, scene and playback extend outside the viewport');
      const measured = document.createElement('span');
      Object.assign(measured.style, {position: 'fixed', visibility: 'hidden', whiteSpace: 'pre'});
      document.body.append(measured);
      try {
        for (const control of controls) {
          const style = getComputedStyle(control);
          const box = control.getBoundingClientRect();
          const label = control.getAttribute('aria-label') || control.textContent;
          verify(box.left >= -1 && box.right <= viewportWidth + 1 && box.width >= 44 && box.height >= 44, label);
          verify(box.bottom <= stage.top + 1, label + ' overlaps the scene');
          for (const fraction of [.25, .5, .75]) {
            const at = document.elementFromPoint(box.left + box.width * fraction, box.top + box.height / 2);
            verify(at === control || control.contains(at), label + ' is covered');
          }
          const padding = control.matches('button') && innerWidth > 480 ? 16 : 12;
          const headerSelect = control.matches('.study-header-tools select') &&
            Number(document.querySelector('#app').dataset.uiVersion) >= 7;
          const arrowSpace = control.matches('select') ? (headerSelect ? 34 : 30) : padding;
          verify(parseFloat(style.paddingInlineStart) === padding && parseFloat(style.paddingInlineEnd) === arrowSpace,
            label + ' has incorrect horizontal padding');
          if (control.matches('select')) {
            const arrow = getComputedStyle(control.parentElement, '::after');
            verify(arrow.insetInlineEnd === (headerSelect ? '16px' : '12px') && arrow.pointerEvents === 'none',
              label + ' has incorrect arrow spacing');
            Object.assign(measured.style, {
              fontFamily: style.fontFamily, fontSize: style.fontSize, fontWeight: style.fontWeight,
              letterSpacing: style.letterSpacing,
            });
            const innerWidth = box.width - padding - arrowSpace -
              parseFloat(style.borderInlineStartWidth) - parseFloat(style.borderInlineEndWidth);
            for (const option of control.options) {
              measured.textContent = option.label;
              verify(measured.getBoundingClientRect().width <= innerWidth + 1, option.label + ' is truncated');
            }
          } else {
            verify(control.scrollWidth <= control.clientWidth + 1 && control.scrollHeight <= control.clientHeight + 1,
              label + ' is truncated');
          }
        }
        for (const [index, control] of controls.entries()) {
          const a = control.getBoundingClientRect();
          for (const other of controls.slice(index + 1)) {
            const b = other.getBoundingClientRect();
            verify(a.right <= b.left + 1 || b.right <= a.left + 1 || a.bottom <= b.top + 1 || b.bottom <= a.top + 1,
              'controls overlap');
          }
        }
      } finally { measured.remove(); }
    }""")


def check_scene(page, kind, *, fallback, first_screen=False):
    page.evaluate(r"""({kind, fallback, firstScreen}) => {
      const q = selector => document.querySelector(selector);
      const verify = (ok, message) => { if (!ok) throw Error('Study layout: ' + message); };
      const rect = element => {
        verify(element?.checkVisibility({visibilityProperty: true, opacityProperty: true}),
          (element?.className || 'required element') + ' is hidden or absent');
        const box = element.getBoundingClientRect();
        verify(box.width > 0 && box.height > 0, 'required element has no size');
        return box;
      };
      const viewport = q('.stage-viewport');
      viewport.scrollTop = viewport.scrollLeft = 0;
      const scene = q('.study-scene');
      const result = q('.study-result');
      const watch = q('.study-watch');
      verify(scene?.children.length === 3 && scene.children[1] === result && scene.children[2] === watch,
        'expected overview, result and current values in order');
      verify(watch?.querySelector('[data-study-watch] .study-watch-value'), 'current value is absent');
      const view = rect(viewport), overview = rect(scene.firstElementChild), resultBox = rect(result), card = rect(watch);
      verify(overview.bottom <= resultBox.top + 1 && resultBox.bottom <= card.top + 1,
        'result or current values are out of order');
      for (const box of [overview, resultBox, card]) {
        verify(box.left >= view.left - 1 && box.right <= view.right + 1, 'horizontal clipping in the scene');
      }
      const explanation = q('.study-explanation');
      verify(explanation && (fallback ? q('.memory').nextElementSibling : q('.study-history').nextElementSibling) === explanation,
        'step explanation is in the wrong place');
      if (kind === 'c-graph' && ['traversal', 'degree'].includes(q('#app').dataset.graphView)) {
        const matrix = q('.graph-matrix,.gi-matrix'), figure = q('.graph-figure,.gi-figure');
        verify(matrix && figure && matrix === figure.nextElementSibling, 'matrix is out of order');
        const a = rect(figure), b = rect(matrix);
        verify(scene.clientWidth < 470 ? a.bottom <= b.top + 1 :
          a.right <= b.left + 1 && b.top < a.bottom && a.top < b.bottom, 'matrix is in the wrong position');
      }
      if (firstScreen) {
        const bottom = Math.min(view.bottom, rect(q('.playbar')).top, innerHeight);
        for (const el of [result, watch, ...watch.querySelectorAll('.study-watch-entry')]) {
          const box = rect(el);
          verify(box.top >= view.top - 1 && box.bottom <= bottom + 1,
            el.className + ' is outside the first mobile screen');
          // Sample the element interior to catch overlays as well as overflow clipping.
          verify(el.contains(document.elementFromPoint(box.x + box.width / 2, box.y + box.height / 2)),
            el.className + ' is covered');
        }
      }
    }""", {'kind': kind, 'fallback': fallback, 'firstScreen': first_screen})


def check_layout(page, kind, width, height, theme):
    narrow = width < 1280
    toggle = lambda side: page.locator(f'[data-action=toggle-{side}]')
    app = page.locator('#app')
    ui_version = int(app.get_attribute('data-ui-version'))
    if ui_version >= 2:
        check_preset_label(page)
    expect(page.locator('.brand')).to_be_visible()
    for side in ('left', 'right'):
        expect(toggle(side)).to_have_attribute('aria-expanded', str(not narrow).lower())
    check_controls(page)
    check_scene(page, kind, fallback=narrow)
    if narrow:
        if int(page.locator('[data-action=scrub]').get_attribute('max')):
            page.locator('[data-action=play]').click()
            expect(app).to_have_attribute('data-playing', 'true')
        toggle('left').tap() if width <= 375 else toggle('left').click()
        expect(app).to_have_attribute('data-playing', 'false')
        expect(page.locator('#panel-left')).to_have_attribute('aria-modal', 'true')
        assert page.locator('.stage').evaluate('e => e.inert')
    left = page.locator('#panel-left')
    boxes = [left.locator(selector).bounding_box() for selector in ('.code', '.study-history', '.study-explanation')]
    assert all(boxes) and all(a['y'] + a['height'] <= b['y'] + 1 for a, b in zip(boxes, boxes[1:])), boxes
    listing = left.locator('.step-list')
    if kind == 'c-graph' and ui_version >= 4:
        from browser_graph_history import check_graph_history
        check_graph_history(page)
    else:
        assert abs(listing.bounding_box()['height'] - 3 * listing.locator('button').first.bounding_box()['height']) <= 2
    if listing.evaluate('e => e.scrollHeight > e.clientHeight'):
        listing.evaluate('e => e.scrollTop = e.scrollHeight')
        follow = left.locator('.study-follow')
        expect(follow).to_be_visible()
        follow.click()
        expect(follow).to_be_hidden()
        assert listing.evaluate('e => e.scrollTop') <= 1
    if narrow:
        page.keyboard.press('Escape')
        expect(toggle('left')).to_be_focused()
        toggle('right').tap() if width <= 375 else toggle('right').click()
        expect(page.locator('#panel-right')).to_have_attribute('aria-modal', 'true')
    else:
        toggle('left').click()
        expect(toggle('right')).to_have_attribute('aria-expanded', 'true')
    right = page.locator('#panel-right')
    expect(right.locator('.study-details > h2')).to_have_text('실행 상태 상세')
    expect(right.locator('.provenance summary').first).to_have_text('예제 정보')
    assert not right.locator('.provenance').evaluate('e => e.open')
    assert right.locator('.study-details').bounding_box()['y'] < right.locator('.provenance').bounding_box()['y']
    if narrow:
        page.keyboard.press('Escape')
        expect(toggle('right')).to_be_focused()
    check_scene(page, kind, fallback=True)
    if not narrow:
        toggle('left').click()
        handles = [page.locator('[data-resize=left]'), page.locator('[data-resize=right]')]
        for handle, width_hint, arrow in zip(handles, (320, 300), ('ArrowRight', 'ArrowLeft')):
            expect(handle).to_have_attribute('aria-valuenow', str(width_hint))
            handle.focus()
            page.keyboard.press(arrow)
            expect(handle).to_have_attribute('aria-valuenow', str(width_hint + 16))
        page.reload()
        page.wait_for_selector('#app[data-snapshot=initial]')
        page.evaluate('document.fonts.ready')
        if theme == 'dark' and not page.locator('#interactive-theme').count():
            page.locator('[data-action=theme]').click()
        for handle, width_hint in zip(handles, (320, 300)):
            expect(handle).to_have_attribute('aria-valuenow', str(width_hint + 16))
            handle.focus()
            page.keyboard.press('Home')
            expect(handle).to_have_attribute('aria-valuenow', str(width_hint))
        assert page.locator('.stage').bounding_box()['width'] >= 400
        if width == 1280:
            page.set_viewport_size({'width': 1279, 'height': height})
            expect(toggle('left')).to_have_attribute('aria-expanded', 'false')
            expect(toggle('right')).to_have_attribute('aria-expanded', 'false')
            page.set_viewport_size({'width': 1280, 'height': height})
            expect(toggle('left')).to_have_attribute('aria-expanded', 'true')
            expect(toggle('right')).to_have_attribute('aria-expanded', 'true')
    assert page.locator('.transport-buttons button:visible').count() == 3
    popup = open_options(page)
    for button in popup.locator('button:visible').all():
        box = button.bounding_box()
        assert min(box['width'], box['height']) >= 44
    popup.locator('[data-speed="1"]').focus()
    page.keyboard.press('Escape')
    expect(popup).to_be_hidden()
    expect(page.locator('[data-action=study-options]')).to_be_focused()
    check_scene(page, kind, fallback=narrow)


def check_mobile_stages(page, kind, out, topic, theme):
    scrub = page.locator('[data-action=scrub]')
    last = int(scrub.get_attribute('max'))
    checked = []
    for stage, index in zip(MOBILE_STAGES, (0, last // 2, last)):
        seek(page, index)
        check_scene(page, kind, fallback=True, first_screen=True)
        page.screenshot(path=str(out / f'{topic}-375-{theme}-{stage}.png'))
        checked.append(stage)
    seek(page, 0)
    return checked


def seek(page, index):
    page.locator('[data-action=scrub]').evaluate(
        "(el, i) => { el.value=i; el.dispatchEvent(new Event('input', {bubbles:true})); }", index)
    expect(page.locator('#app')).to_have_attribute('data-index', str(index))


CHECK_CASE = r"""({input, kind}) => {
  const app = document.querySelector('#app');
  const q = selector => app.querySelector(selector);
  const all = selector => [...app.querySelectorAll(selector)];
  const trace = DSInteractive.compileScenario(DSInteractive.scenario, input);
  const steps = trace.lineSteps || trace.snapshots;
  const scrub = q('[data-action=scrub]');
  const format = value => !value ? '—' : value.kind === 'int' ? String(value.value)
    : value.kind === 'pointer' ? value.target === null ? 'NULL' : '&' + value.target
    : value.kind === 'uninitialized' ? '미초기화' : '사용 불가';
  function same(actual, expected, description) {
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw Error(description + ' at ' + scrub.value + ': ' + JSON.stringify({actual, expected}));
    }
  }
  same(Number(scrub.max) + 1, steps.length, 'trace length');
  for (const [index, step] of steps.entries()) {
    scrub.value = index;
    scrub.dispatchEvent(new Event('input', {bubbles: true}));
    const {cells, activeFrame, stdout} = step.state;
    same(app.dataset.snapshot, step.id, 'snapshot');
    same(q('.study-explanation .explanation').textContent, step.explanation || step.title, 'explanation');
    same(q('.memory').dataset.step, step.id, 'scene snapshot');
    same(q('[aria-pressed=true][data-step-index]').dataset.stepIndex, String(index), 'history');
    const location = step.executed?.at || step.next?.at || step.at;
    if (location) {
      same(q('.code-line.current').dataset.line, String(location.line), 'code line');
      same(q('.code-line.current').dataset.sourceId, location.sourceId, 'code source');
    }
    const watch = key => q('[data-study-watch=' + key + '] .study-watch-value')?.textContent;
    const result = q('.study-result-line').textContent;
    if (kind === 'c-tree') {
      const tree = DSInteractive.getTreeView(trace.metadata.tree, step);
      same(all('.tree-node').map(node => node.dataset.nodeId), tree.nodes.map(node => node.id), 'nodes');
      const parameter = cells[tree.stack[0]?.parameterCellId];
      const targetCell = cells[parameter?.value.target];
      const node = tree.nodes.find(node => node.id === targetCell?.owner);
      same(watch('node'), node ? node.key + '번 노드' : format(parameter?.value), 'node card');
      same(result, stdout.join('') || '아직 출력 없음', 'tree output');
    } else {
      const rendered = Object.fromEntries(all('.study-memory-cells [data-cell-id]').map(element =>
        [element.dataset.cellId, element.querySelector('.cell-value').textContent]));
      for (const cell of Object.values(cells)) {
        const prefix = cell.lifetime === 'ended' ? '수명 종료 · ' : '';
        same(rendered[cell.id], prefix + format(cell.value), 'cell ' + cell.id);
      }
      const pointers = Object.values(cells).filter(cell => cell.lifetime === 'live' && cell.value.kind === 'pointer');
      const pointer = pointers.find(cell => cell.owner === activeFrame) || pointers[0];
      const target = cells[pointer?.value.target];
      same(watch('pointer'), format(pointer?.value), 'pointer card');
      same(watch('target'), format(target?.value), 'target card');
      if (stdout.length) same(result, stdout.join(''), 'pointer output');
      else if (target?.lifetime === 'live') same(result, target.name + ' = ' + format(target.value), 'pointer result');
    }
  }
  return steps.length;
}"""


def check_tree_or_memory(page, kind, width):
    preset = page.locator('[data-action=preset]')
    cases = page.evaluate("""() => {
      const {inputs, presets} = DSInteractive.scenario;
      return [{id: 'default', input: Object.fromEntries(inputs.map(field => [field.key, field.default]))}, ...presets];
    }""")
    checked = 0
    for case in cases:
        preset.select_option(case['id'])
        checked += page.evaluate(CHECK_CASE, {'input': case['input'], 'kind': kind})
        expect(page.locator('[data-action=next]')).to_be_disabled()
    preset.select_option('default')
    app = page.locator('#app')
    popup = open_options(page)
    if int(page.locator('[data-action=scrub]').get_attribute('max')):
        popup.locator('[data-action=last]').click()
        expect(page.locator('[data-action=next]')).to_be_disabled()
        popup.locator('[data-action=first]').click()
        expect(app).to_have_attribute('data-index', '0')
    page.keyboard.press('Escape')
    if kind == 'c-tree':
        node = page.locator('.tree-node').first
        if node.count():
            node.click()
            expect(page.locator('.tree-inspector[open] .tree-fields')).to_be_visible()
            page.keyboard.press('Escape')
            expect(node).to_be_focused()
    else:
        number = page.locator('.study-stage-inputs input[type=number]').first
        if number.count():
            number.fill('')
            expect(number).to_have_attribute('aria-invalid', 'true')
            expect(page.locator('[data-action=play]')).to_be_disabled()
            preset.select_option('default')
            expect(number).to_have_attribute('aria-invalid', 'false')
        cell = page.locator('.study-memory-cells button[data-cell-id]').first
        if cell.count():
            cell.click()
            expect(page.locator('.selection dl')).to_have_count(1)
            expect(cell).to_be_focused()
        if width < 1280:
            page.locator('[data-action=toggle-right]').click()
        panel = page.locator('#panel-right')
        zoom = panel.locator('[data-action=zoom-in]')
        zoom.click()
        expect(page.locator('.memory')).not_to_have_attribute('data-scale', '1')
        panel.locator('[data-action=zoom-reset]').click()
        expect(page.locator('.memory')).to_have_attribute('data-scale', '1')
        addresses = panel.locator('[data-action=option-addresses]')
        addresses.click()
        expect(app).to_have_attribute('data-addresses', 'false')
        addresses.click()
        expect(app).to_have_attribute('data-addresses', 'true')
        if width < 1280:
            page.keyboard.press('Escape')
    return len(cases), checked
