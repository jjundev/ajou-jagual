"""Check panel roles, rendered order, and the mobile first screen in Chromium."""
from playwright.sync_api import expect

GRAPH_VIEWPORTS = [(1440, 900), (1280, 800), (1279, 800), (375, 812)]
MOBILE_STAGES = ('initial', 'middle', 'last')


def bounds(page, width, height):
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    for element in page.locator('.topbar, .stage > .configuration, .playbar').all():
        box = element.bounding_box()
        assert box and box['x'] >= -1 and box['x'] + box['width'] <= width + 1, box
        assert box['y'] >= -1 and box['y'] + box['height'] <= height + 1, box
    for control in page.locator('.topbar button:visible, .transport-buttons button, '
                                '.graph-speed-trigger, .graph-header-tools select:visible, '
                                '.configuration :is(input, select):visible').all():
        box = control.bounding_box()
        assert box and min(box['width'], box['height']) >= 44, box


def scene_order(page, view, fallback_visible, first_screen=False):
    page.locator('.stage-viewport').evaluate('e => {e.scrollTop = 0; e.scrollLeft = 0}')
    page.evaluate("""({view, fallback, firstScreen}) => {
      const q = selector => document.querySelector(selector);
      const check = (ok, detail) => { if (!ok) throw Error('Graph layout: ' + detail); };
      const box = selector => {
        const el = q(selector);
        check(el?.checkVisibility({visibilityProperty:true, opacityProperty:true}), selector + ' must be shown');
        const rect = el.getBoundingClientRect();
        check(rect.width > 0 && rect.height > 0, selector + ' has no area');
        return rect;
      };
      const before = (a, b, label) => check(a.bottom <= b.top + 1, label + ' is out of order');
      const inside = (child, parent) => check(child.left >= parent.left - 1 && child.right <= parent.right + 1,
        'central content extends past its viewport');
      const header = box('.topbar');
      const selector = view === 'traversal' ? '[data-input=setup]' : '[data-action=preset]';
      const preset = q(selector);
      check(preset?.closest('.graph-header-tools'), 'case selector must be in the header');
      if (q('.modes button')) check(q('.modes').closest('.graph-header-tools'), 'mode must be in the header');
      const viewport = box('.stage-viewport');
      const playbar = box('.playbar');
      before(header, viewport, 'viewport');
      before(viewport, playbar, 'playback');
      if (view !== 'traversal') {
        const inputs = box('.stage > .configuration');
        before(header, inputs, 'additional input');
        before(inputs, viewport, 'viewport');
        belowOneRow();
      }
      function belowOneRow() {
        const fields = [...q('.stage > .configuration .inputs').querySelectorAll('input,select')];
        check(fields.length === 2 && Math.abs(fields[0].getBoundingClientRect().top -
          fields[1].getBoundingClientRect().top) <= 1, 'additional inputs must be on one row');
      }
      const scene = box('.memory');
      const figureSelector = view === 'traversal' ? '.graph-figure' : '.gi-figure';
      const figure = box(figureSelector);
      inside(scene, viewport);
      inside(figure, viewport);
      inside(box('.memory svg'), figure);
      let visual = figure;
      if (view !== 'bridges') {
        const matrixSelector = view === 'traversal' ? '.graph-matrix' : '.gi-matrix';
        const matrix = box(matrixSelector);
        check(q(matrixSelector) === q(figureSelector).nextElementSibling, 'matrix must immediately follow the graph');
        inside(matrix, viewport);
        if (q('.memory-pane').clientWidth < 470) before(figure, matrix, 'stacked matrix');
        else check(figure.right <= matrix.left + 1 && matrix.top < figure.bottom && figure.top < matrix.bottom,
          'wide layout must put the matrix next to the graph');
        if (matrix.bottom > figure.bottom) visual = matrix;
      }
      const result = box('.graph-result');
      const watch = box('.graph-watch');
      check(q('.graph-result').nextElementSibling === q('.graph-watch'), 'current values must follow the result');
      before(visual, result, 'result');
      before(result, watch, 'current values');
      inside(result, viewport);
      inside(watch, viewport);
      check(q('.graph-watch').querySelectorAll('[data-graph-watch]').length === 2, 'current values are incomplete');
      const message = q('.graph-explanation');
      if (fallback) {
        check(q('.memory').nextElementSibling === message, 'central explanation must follow the current values');
        before(watch, box('.graph-explanation'), 'explanation');
      } else {
        check(q('.graph-history').nextElementSibling === message, 'left explanation must follow the history');
      }
      if (firstScreen) {
        for (const selector of ['.graph-result', '.graph-watch', '.graph-watch-entry:first-child', '.graph-watch-entry:last-child']) {
          const rect = box(selector);
          const visibleBottom = Math.min(viewport.bottom, playbar.top, innerHeight);
          check(rect.top >= viewport.top - 1 && rect.bottom <= visibleBottom + 1,
            selector + ' is outside the initial mobile viewport');
          const el = q(selector);
          const atCenter = document.elementFromPoint(rect.left + rect.width / 2, rect.top + rect.height / 2);
          check(el.contains(atCenter), selector + ' is covered');
        }
      }
    }""", {'view': view, 'fallback': fallback_visible, 'firstScreen': first_screen})


def open_options(page):
    trigger = page.locator('[data-action=graph-options],[data-action=study-options]')
    popup = page.locator('.graph-playback-options,.study-playback-options')
    if not popup.is_visible():
        trigger.click()
    expect(trigger).to_have_attribute('aria-expanded', 'true')
    return popup


def mobile_first_screen(page, view, out, topic, theme):
    scrub = page.locator('[data-action=scrub]')
    last = int(scrub.get_attribute('max'))
    stages = []
    for stage, step in zip(MOBILE_STAGES, (0, last // 2, last)):
        scrub.evaluate("""(el, step) => {
          el.value = step;
          el.dispatchEvent(new Event('input', {bubbles: true}));
        }""", step)
        expect(page.locator('#app')).to_have_attribute('data-index', str(step))
        scene_order(page, view, fallback_visible=True, first_screen=True)
        page.screenshot(path=str(out / f'{topic}-375-{theme}-{stage}.png'))
        stages.append(stage)
    scrub.evaluate("el => {el.value=0; el.dispatchEvent(new Event('input', {bubbles:true}));}")
    return stages


def check_layout(page, view, width, height, theme):
    expect(page.locator('#app')).to_have_attribute('data-graph-view', view)
    expect(page.locator('.brand')).to_be_visible()
    left = page.locator('[data-action=toggle-left]')
    right = page.locator('[data-action=toggle-right]')
    left_panel = page.locator('#panel-left')
    right_panel = page.locator('#panel-right')
    narrow = width < 1280
    for toggle in (left, right):
        expect(toggle).to_have_attribute('aria-expanded', str(not narrow).lower())
    bounds(page, width, height)
    scene_order(page, view, narrow)

    if narrow:
        page.locator('[data-action=play]').click()
        expect(page.locator('#app')).to_have_attribute('data-playing', 'true')
        left.tap() if width == 375 else left.click()
        expect(page.locator('#app')).to_have_attribute('data-playing', 'false')
        expect(left_panel).to_have_attribute('aria-modal', 'true')
    code = left_panel.locator('.code')
    history = left_panel.locator('.graph-history')
    message = left_panel.locator('.graph-explanation')
    for section in (code, history, message):
        expect(section).to_be_visible()
    positions = [section.bounding_box() for section in (code, history, message)]
    assert all(a['y'] + a['height'] <= b['y'] + 1 for a, b in zip(positions, positions[1:])), positions
    assert code.evaluate('e => e.scrollWidth <= e.clientWidth + 1'), 'clipped code'
    row_height = history.locator('.steps button').first.bounding_box()['height']
    assert abs(history.locator('.steps').bounding_box()['height'] - 3 * row_height) <= 2
    history.locator('.steps').evaluate('e => e.scrollTop = e.scrollHeight')
    expect(history.locator('.graph-follow')).to_be_visible()
    history.locator('.graph-follow').click()
    expect(history.locator('.steps')).to_be_focused()
    expect(history.locator('.graph-follow')).to_be_hidden()
    assert history.locator('.steps').evaluate('e => e.scrollTop') <= 1

    if narrow:
        assert page.locator('.stage').evaluate('e => e.inert')
        page.keyboard.press('Shift+Tab')
        assert left_panel.evaluate('e => e.contains(document.activeElement)')
        page.keyboard.press('Escape')
        expect(left).to_be_focused()
        right.tap() if width == 375 else right.click()
        expect(right_panel).to_have_attribute('aria-modal', 'true')
    else:
        left.click()
        expect(right).to_have_attribute('aria-expanded', 'true')

    right_sections = right_panel.locator('.panel-inner > :is(section, details):visible')
    expect(right_sections).to_have_count(2)
    detail, example = right_sections.nth(0), right_sections.nth(1)
    expect(detail.locator('h2')).to_have_text('실행 상태 상세')
    state = detail.locator('.graph-detail-content')
    if view == 'traversal':
        expect(state.locator('[data-graph-state] h3')).to_have_text(['호출 스택 · 위 → 아래', 'visited'])
    elif view == 'bridges':
        expect(state.locator('.gi-panel h3')).to_have_text(['이동 기록', '정점별 차수'])
    else:
        expect(state.locator('.gi-panel h3')).to_have_text(['읽은 행렬 칸'])
    expect(detail.locator('.graph-changes summary')).to_have_text('변경 전 → 후')
    expect(example.locator('summary')).to_have_text('예제 정보')
    assert not example.evaluate('e => e.open')
    assert detail.bounding_box()['y'] + detail.bounding_box()['height'] <= example.bounding_box()['y'] + 1
    if narrow:
        page.keyboard.press('Escape')
        expect(right).to_be_focused()
    scene_order(page, view, True)

    if not narrow:
        left.click()
        stage = page.locator('.stage')
        handles = page.locator('[data-resize=left]'), page.locator('[data-resize=right]')
        for handle, default, key in zip(handles, (320, 300), ('ArrowRight', 'ArrowLeft')):
            expect(handle).to_have_attribute('aria-valuenow', str(default))
            handle.focus()
            page.keyboard.press(key)
            expect(handle).to_have_attribute('aria-valuenow', str(default + 16))
        page.reload()
        page.wait_for_selector('#app[data-snapshot=initial]')
        page.evaluate('document.fonts.ready')
        if theme == 'dark' and not page.locator('#interactive-theme').count():
            page.locator('[data-action=theme]').click()
        for handle, default in zip(handles, (320, 300)):
            expect(handle).to_have_attribute('aria-valuenow', str(default + 16))
            handle.focus()
            page.keyboard.press('Home')
            expect(handle).to_have_attribute('aria-valuenow', str(default))
        handles[1].focus()
        for _ in range(9):
            page.keyboard.press('Shift+ArrowLeft')
        assert stage.bounding_box()['width'] >= 400
        handles[1].dblclick()
        expect(handles[1]).to_have_attribute('aria-valuenow', '300')
        right.click()
        expect(left).to_have_attribute('aria-expanded', 'true')
        scene_order(page, view, False)
        right.click()
        if width == 1280:
            page.set_viewport_size({'width': 1279, 'height': height})
            for toggle in (left, right):
                expect(toggle).to_have_attribute('aria-expanded', 'false')
            page.set_viewport_size({'width': width, 'height': height})
            for toggle in (left, right):
                expect(toggle).to_have_attribute('aria-expanded', 'true')

    expect(page.locator('.graph-playback-options')).to_be_hidden()
    assert page.locator('.transport-buttons button:visible').count() == 3
    popup = open_options(page)
    for control in popup.locator('button:visible').all():
        box = control.bounding_box()
        assert box and min(box['width'], box['height']) >= 44
    expect(popup.locator('[data-action=next-output]')).to_have_count(int(view == 'traversal'))
    popup.locator('[data-speed="1"]').focus()
    page.keyboard.press('Escape')
    expect(popup).to_be_hidden()
    expect(page.locator('[data-action=graph-options]')).to_be_focused()
    scene_order(page, view, narrow)
