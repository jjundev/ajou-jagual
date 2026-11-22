"""Runtime acceptance for synchronized C tree execution, including drawer transitions."""

from playwright.sync_api import expect


CENTERED_ROWS = """list => {
      const top = list.getBoundingClientRect().top + list.clientTop;
      const current = list.querySelector('[aria-pressed=true]');
      const active = current.getBoundingClientRect();
      const target = current.dataset.stepIndex === '0' ? top + active.height / 2 : top + list.clientHeight / 2;
      if (Math.abs((active.top + active.bottom) / 2 - target) > 1 ||
          Math.abs(list.clientHeight - active.height * 3) > 1) return null;
      return Array.from(list.querySelectorAll('button[data-step-index]')).filter(button => {
        const row = button.getBoundingClientRect();
        return row.top >= top - 1 && row.bottom <= top + list.clientHeight + 1;
      }).map(button => Number(button.dataset.stepIndex));
    }"""


def centered_rows(history_list, wait=False):
    if wait:
        return history_list.page.wait_for_function(CENTERED_ROWS, arg=history_list.element_handle()).json_value()
    return history_list.evaluate(CENTERED_ROWS)


def check_history_touch(browser, url):
    with browser.new_context(viewport={'width': 375, 'height': 812}, is_mobile=True,
                             has_touch=True, offline=True, reduced_motion='reduce') as context:
        page = context.new_page()
        page.goto(url)
        page.evaluate('document.fonts.ready')
        popup = page.locator('.tree-playback-options')
        speed = page.locator('[data-action=tree-options]')
        expect(popup).to_be_hidden()
        page.get_by_role('button', name='다음 줄').tap()
        expect(popup).to_be_hidden()
        speed.tap()
        expect(popup).to_be_in_viewport(ratio=0.99)
        popup.locator('[data-speed="2"]').tap()
        expect(speed).to_have_text('2×')
        expect(popup).to_be_visible()
        page.locator('.brand').tap()
        expect(popup).to_be_hidden()
        speed.tap()
        popup.get_by_role('button', name='다음 출력').tap()
        expect(popup).to_be_hidden()
        expect(page.locator('.stdout-value')).to_have_text('1')
        devtools = context.new_cdp_session(page)

        def swipe(x, y, distance):
            def send(kind, points):
                devtools.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': points})

            send('touchStart', [{'x': x, 'y': y}])
            for step in range(1, 9):
                send('touchMove', [{'x': x, 'y': y + step * distance / 8}])
            send('touchEnd', [])

        page.locator('[data-action=scrub]').evaluate(
            '(e)=>{e.value=15;e.dispatchEvent(new Event("input",{bubbles:true}));}'
        )
        history = page.locator('.tree-history .step-list')
        stage = page.locator('.stage-viewport')
        follow = page.get_by_role('button', name='실행 위치로')
        page.locator('[data-action=toggle-left]').tap()
        expect(page.locator('.panel-left')).to_have_attribute('aria-modal','true')
        bounds = history.bounding_box()
        swipe(bounds['x'] + 60, bounds['y'] + 12, 65)
        expect(follow).to_be_visible()
        assert stage.evaluate('e => e.scrollTop') == 0
        follow.tap()
        assert centered_rows(history, wait=True) == [14, 15, 16]

        page.touchscreen.tap(374, 200)
        expect(page.locator('[data-action=toggle-left]')).to_be_focused()
        expect(history).to_be_hidden()
        for selector in ('.tree-scene', '.tree-output', '.playbar'):
            expect(page.locator(selector)).to_be_in_viewport(ratio=0.99)


def check_panel_layout(page, wide):
    left, right = [page.locator(f'[data-action=toggle-{side}]') for side in ('left', 'right')]
    code = page.locator('.source-pane')
    stack = page.locator('.tree-stack')
    explanation = page.locator('.tree-step-explanation')
    stage = page.locator('.stage')
    tree = page.locator('.tree-scene')
    layout_width = lambda: stage.bounding_box()['width']

    expect(left).to_be_visible()
    expect(right).to_be_visible()
    for toggle in (left, right):
        expect(toggle).to_have_attribute('aria-expanded', str(wide).lower())
    expect(tree).to_be_in_viewport(ratio=0.99)
    width = layout_width()
    if wide:
        left.click()
        expect(code).to_be_hidden()
        expect(stack).to_be_visible()
        left_closed_width = layout_width()
        assert left_closed_width > width
        right.click()
        expect(stack).to_be_hidden()
        assert layout_width() > left_closed_width
        left.click()
        expect(code).to_be_visible()
        expect(stack).to_be_hidden()
        right.click()
        assert layout_width() == width
    else:
        expect(code).to_be_hidden()
        expect(stack).to_be_hidden()
        for toggle, side, content in ((left, 'left', code), (right, 'right', stack)):
            toggle.click()
            drawer = page.locator(f'.panel-{side}')
            expect(drawer).to_have_attribute('aria-modal', 'true')
            expect(drawer.locator('[data-action=close-panels]')).to_be_focused()
            expect(content).to_be_visible()
            assert layout_width() == width
            page.keyboard.press('Tab')
            assert drawer.evaluate('e => e.contains(document.activeElement)')
            page.keyboard.press('Escape')
            expect(toggle).to_be_focused()
            expect(content).to_be_hidden()
    if wide:
        left.click()
    expect(page.locator('.memory-pane .tree-step-explanation')).to_be_visible()
    page.locator('[data-action=next]').click()
    page.locator('[data-action=next]').click()
    left.click()
    assert centered_rows(page.locator('.tree-history .step-list'), wait=True) == [1, 2, 3]
    left.click() if wide else page.keyboard.press('Escape')
    left.click()
    history = page.locator('.tree-history .step-list')
    expect(history).to_be_visible()
    assert centered_rows(history, wait=True) == [1, 2, 3]
    if not wide:
        page.keyboard.press('Escape')
    page.locator('[data-action=scrub]').evaluate(
        '(e)=>{e.value=0;e.dispatchEvent(new Event("input",{bubbles:true}));}'
    )
    expect(explanation).to_be_visible()


def check_tree_case(page, width, height):
    app = page.locator('#app')
    wide = width >= 1280
    def action(name):
        return page.locator(f'[data-action={name}]')

    def scrub(step):
        action('scrub').evaluate(
            '(e,n)=>{e.value=n;e.dispatchEvent(new Event("input",{bubbles:true}));}', step
        )

    def preset(case):
        action('preset').select_option(case)

    inspector = page.locator('.tree-inspector')
    popup = page.locator('.tree-playback-options')
    speed_trigger = action('tree-options')
    def drawer(side):
        action('toggle-' + side).click()
        expect(page.locator('.panel-' + side)).to_have_attribute('aria-modal', 'true')

    def close_drawer(side):
        page.keyboard.press('Escape')
        expect(action('toggle-' + side)).to_be_focused()
        expect(page.locator('.panel-' + side)).to_be_hidden()

    def close_pane():
        page.keyboard.press('Escape')
        expect(inspector).to_be_hidden()

    def open_options():
        speed_trigger.click()
        expect(popup).to_be_visible()
        expect(inspector).to_be_hidden()

    def close_options():
        page.keyboard.press('Escape')
        expect(popup).to_be_hidden()

    def jump(name):
        open_options()
        popup.locator(f'[data-action={name}]').click()
        expect(popup).to_be_hidden()
        expect(speed_trigger).to_be_focused()

    def next_line():
        current = page.locator('.code-line.current')
        return (current.get_attribute('data-source-id'), int(current.get_attribute('data-line'))) if current.count() else None

    def node(node_id):
        return page.locator(f'[data-node-id="node-{node_id}"]')

    check_panel_layout(page, wide)
    assert page.locator('.memory-pane').is_visible()
    expect(page.locator('.tree-inspector')).to_be_hidden()
    assert page.locator('[data-action^=zoom-]').count() == 0, 'the tree should omit all zoom controls'
    expect(speed_trigger).to_have_text('1×')
    expect(popup).to_be_hidden()
    expect(speed_trigger).to_have_attribute('aria-expanded', 'false')
    assert popup.locator('.tree-jumps button').count() == 2
    bar = page.locator('.playbar')
    before = page.locator('.tree-scene').bounding_box()
    bar_box = bar.bounding_box()
    page.mouse.move(bar_box['x'] + bar_box['width'] - 26, bar_box['y'] + 4)
    expect(popup).to_be_in_viewport(ratio=0.99)
    expect(speed_trigger).to_have_attribute('aria-expanded', 'true')
    popup_box = popup.bounding_box()
    assert abs(popup_box['y'] + popup_box['height'] - bar_box['y']) <= 2
    page.mouse.move(popup_box['x'] + popup_box['width'] - 25, popup_box['y'] + 25, steps=12)
    expect(popup).to_be_visible()
    assert page.locator('.tree-scene').bounding_box() == before
    page.mouse.move(4, 4)
    expect(popup).to_be_hidden()

    speed_trigger.focus()
    speed_trigger.press('Enter')
    expect(popup).to_be_visible()
    page.keyboard.press('Tab')
    expect(popup.locator('[data-speed="0.5"]')).to_be_focused()
    close_options()
    expect(speed_trigger).to_be_focused()
    speed_trigger.press('Space')
    expect(popup).to_be_visible()
    close_options()

    action('play').click()
    open_options()
    expect(app).to_have_attribute('data-playing', 'true')
    popup.locator('[data-speed="2"]').click()
    expect(speed_trigger).to_have_text('2×')
    expect(app).to_have_attribute('data-playing', 'true')
    expect(popup).to_be_visible()
    popup.locator('[data-speed="1"]').click()
    close_options()
    action('play').click()
    scrub(0)

    if not wide:
        drawer('left')
    history = page.locator('.source-pane .tree-history')
    expect(history.locator('details, summary')).to_have_count(0)
    heading = history.get_by_role('heading', name='줄 기록', exact=True)
    expect(heading).to_be_visible()
    assert heading.evaluate("""e => {
      const heading = document.querySelector('.source-pane h2');
      const fields = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'color'];
      return fields.every(field => getComputedStyle(e)[field] === getComputedStyle(heading)[field]) &&
        Math.abs(e.getBoundingClientRect().left - heading.getBoundingClientRect().left) < 1;
    }"""), 'history and code titles should share typography and alignment'
    expect(page.get_by_text('다음 실행', exact=True)).to_have_count(0, timeout=1500)
    explanation = page.locator('.tree-step-explanation')
    expect(explanation).to_be_visible()
    if wide:
        assert explanation.evaluate("e => e.previousElementSibling.matches('.tree-history-region')")
    else:
        assert explanation.evaluate("e => e.previousElementSibling.matches('.tree-output, .tree-watch')")

    history_list = history.locator('.step-list')
    follow = page.get_by_role('button', name='실행 위치로')
    expect(follow).to_be_hidden()
    assert centered_rows(history_list) == [0, 1, 2], 'show the initial step at the top without an empty row'
    scrub(1)
    assert centered_rows(history_list) == [0, 1, 2], 'step 1 should be centered without scrolling'
    scrub(0)
    assert centered_rows(history_list) == [0, 1, 2]

    sidebar = page.locator('.tree-sidebar')
    stack = page.locator('.tree-stack')
    info_disclosure = sidebar.locator('details')
    if wide:
        expect(sidebar.get_by_role('heading', name='호출 스택')).to_be_visible()
        expect(stack).to_be_visible()
        expect(info_disclosure.locator('summary')).to_be_visible()
        assert info_disclosure.get_attribute('open') is None
    assert page.evaluate("""() => {
      const gap = (upper,lower) => {
        const rect = selector => document.querySelector(selector).getBoundingClientRect();
        return Math.round(rect(lower).top - rect(upper).bottom);
      };
      return gap('.source-pane .code','.tree-history h2') === 20 &&
        gap('.tree-history h2','.tree-history .step-list') === 8 &&
        gap('.tree-scene','.tree-output') === 12 &&
        (innerWidth < 1280 || (gap('.tree-history .step-list','.tree-step-explanation') === 12 &&
          gap('.tree-stack','.tree-example') === 20));
    }"""), 'apply the agreed vertical spacing'
    assert page.locator('.tree-output').evaluate("""e =>
      e.parentElement.matches('.memory-pane') && e.previousElementSibling.matches('.memory')
    """), 'stdout should sit directly under the tree in the same column'
    if page.locator('.tree-watch').count():
        assert page.locator('.tree-watch').evaluate(
            "e => e.previousElementSibling.matches('.tree-output')"
        ), 'watched values should sit directly under stdout'
    if not wide:
        close_drawer('left')

    output = page.locator('.stdout-value')
    lesson = page.evaluate("DSInteractive.scenario.id") == 'inorder-1105'
    watched_pointer = page.locator('.tree-watch [data-watch=p]')
    if lesson:
        expect(watched_pointer).to_have_count(1)
        expect(watched_pointer.locator('..').locator('code')).to_have_text('p')
    cases = action('preset').locator('option').evaluate_all('(options)=>options.map(option=>option.value)')
    expected_outputs = {'default': '1 3 8 10 ', 'lecture': '3 7 12 18 26 27 31 ', 'empty': ''}
    total = 0
    for case in cases:
        preset(case)
        if not wide:
            drawer('left')
        if lesson:
            assert history_list.locator('.step-txt > *').evaluate_all(
                'parts => parts.every(part => part.scrollWidth <= part.clientWidth + 1)'
            ), 'the 1105 history labels should fit on one line'
        states = page.evaluate(
            """() => {
              const D=DSInteractive;
              const input=Object.fromEntries([...document.querySelectorAll('[data-input]')]
                .map(e=>[e.dataset.input,e.type==='number'?Number(e.value):e.value]));
              const t=D.compileScenario(D.scenario,input);
              return t.lineSteps.map(step=>({
                id:step.id,next:step.next,stdout:step.state.stdout.join(''),explanation:step.explanation ?? step.title,
                frame:step.state.activeFrame??'',view:D.getTreeView(t.metadata.tree,step)
              }));
            }"""
        )
        # Reuse stable browser-visible DOM coordinates across every checkpoint.
        points = page.locator('.memory [data-node-id]').evaluate_all(
            '(nodes)=>Object.fromEntries(nodes.map(n=>[n.dataset.nodeId,[n.style.left,n.style.top]]))'
        )
        for index, state in enumerate(states):
            scrub(index)
            expected = state['next']
            actual = page.evaluate("""() => {
              const app=document.querySelector('#app'),code=document.querySelector('.code'),tree=document.querySelector('.memory');
              const line=code.querySelector('.current');
              return {id:app.dataset.snapshot,code:code.dataset.step,tree:tree.dataset.step,
                count:document.querySelector('output[data-step]').textContent,
                stdout:document.querySelector('.stdout-value').textContent,
                explanation:document.querySelector('.tree-step-explanation').textContent,
                next:line?[line.dataset.sourceId,Number(line.dataset.line)]:null,
                frame:app.dataset.activeFrame,
                nodes:[...tree.querySelectorAll('[data-node-id]')].map(n=>[
                  n.dataset.nodeId,[n.style.left,n.style.top],n.dataset.outputOrder??null]),
                overflow:document.documentElement.scrollWidth > innerWidth};
            }""")
            assert actual == {
                'id':state['id'], 'code':state['id'], 'tree':state['id'],
                'count':f'{index} / {len(states)-1}', 'stdout':state['stdout'],
                'next':[expected['at']['sourceId'],expected['at']['line']] if expected else None,
                'frame':state['frame'], 'explanation':state['explanation'], 'overflow':False,
                'nodes':[[n['id'],points[n['id']],str(n['outputOrder']) if n['outputOrder'] else None]
                         for n in state['view']['nodes']],
            }, (case, index, actual)
            if lesson:
                view = state['view']
                current = view['stack'][0]
                node_id = current['nodeId']
                if node_id is not None:
                    key = next(item['key'] for item in view['nodes'] if item['id'] == node_id)
                    pointer = f'{key}번 노드'
                else:
                    pointer = 'NULL' if current['parameterCellId'] is not None else '—'
                assert watched_pointer.text_content() == pointer, (case, index, pointer)
            rows = list(range(max(0, index-1), min(len(states), max(3, index+2))))
            assert centered_rows(history_list) == rows, (case, index, rows)
        if lesson:
            assert output.text_content() == expected_outputs[case]
        assert action('next').is_disabled()
        assert next_line() is None
        total += len(states)
        if not wide:
            close_drawer('left')

    preset('default')
    if not lesson:
        return len(cases), total

    if not wide:
        drawer('left')
    scrub(18)
    expect(explanation).to_have_text('8의 오른쪽 자식 주소로 inorder(10)을 호출했어요.')
    assert centered_rows(history_list) == [17, 18, 19]
    expect(history_list).to_be_visible()
    expect(explanation).to_be_in_viewport()
    if wide:
        action('next').click()
    else:
        scrub(19)
    expect(explanation).to_have_text('p가 10번 노드를 가리켜 왼쪽 자식 호출로 넘어가요.')
    assert centered_rows(history_list, wait=True) == [18, 19, 20]
    if not wide:
        close_drawer('left')
    preset('default')

    jump('next-output')
    expect(node(1)).to_have_attribute('data-output-order','1')
    first_print = int(app.get_attribute('data-index'))
    assert output.text_content() == '1 '
    expect(explanation).to_have_text('현재 노드의 키를 읽어 1 값을 출력했어요.')
    open_options()
    expect(action('previous-output')).to_be_disabled()
    close_options()
    action('prev').click()
    assert next_line() == ('walk',4) and output.text_content() == ''
    expect(explanation).to_have_text('왼쪽 자식이 NULL이라 1번 노드의 호출로 돌아왔어요.')
    expect(history_list.locator('[aria-pressed=true]')).to_contain_text('inorder(NULL) · 2행')
    assert node(1).get_attribute('data-output-order') is None
    action('prev').click()
    left_null = int(app.get_attribute('data-index'))
    assert next_line() == ('walk',2)
    expect(page.locator('[data-null-side=left]')).to_have_attribute('data-parent-node','node-1')
    if not wide:
        drawer('right')
    null_frame = page.get_by_role('button', name='inorder(NULL) 현재')
    null_frame.click()
    active_id = null_frame.get_attribute('data-inspect-frame')
    frame = page.locator('[data-inspect-frame="'+active_id+'"]')
    expect(stack.locator('.tree-cell-value')).to_have_text('NULL')
    expect(stack.locator('.tree-cell-address')).to_have_text('&'+active_id+'.p')
    if not wide:
        page.keyboard.press('Tab')
        assert sidebar.evaluate("e => e.parentElement.contains(document.activeElement)")
        page.set_viewport_size({'width':1440,'height':height})
        expect(page.locator('.panel-right')).not_to_have_attribute('aria-modal', 'true')
        expect(sidebar.locator('.tree-stack')).to_be_visible()
    expect(frame).to_have_attribute('aria-expanded','true')
    action('next').click()
    expect(frame).to_contain_text('수명 종료')
    expect(stack.locator('thead')).to_contain_text('마지막 값')
    scrub(0)
    expect(frame).to_contain_text('호출 전')
    expect(stack.locator('table')).to_have_count(0)
    scrub(left_null)
    expect(frame).to_contain_text('현재')
    expect(stack.locator('.tree-cell-value')).to_have_text('NULL')
    if not wide:
        page.set_viewport_size({'width':width,'height':height})
        expect(action('toggle-right')).to_have_attribute('aria-expanded','false')
        drawer('right')
        expect(frame).to_have_attribute('aria-expanded','true')
        close_drawer('right')
    else:
        frame.click()
        expect(frame).to_have_attribute('aria-expanded', 'false')

    jump('next-output')
    assert int(app.get_attribute('data-index')) == first_print
    jump('next-output')
    assert output.text_content() == '1 3 '
    jump('previous-output')
    assert output.text_content() == '1 '
    action('next').click()
    expect(page.locator('[data-null-side=right]')).to_have_attribute('data-parent-node','node-1')
    action('next').click()
    assert next_line() == ('walk',6)
    expect(explanation).to_have_text('오른쪽 자식이 NULL이라 1번 노드의 호출로 돌아왔어요.')
    assert output.text_content() == '1 '

    action('play').click()
    expect(app).to_have_attribute('data-playing','true')
    if wide:
        before = app.get_attribute('data-index')
        page.wait_for_function("(before) => document.querySelector('#app').dataset.index !== before", arg=before)
        expect(app).to_have_attribute('data-playing','true')
        assert stack.evaluate("""e => e.querySelector('[data-frame-state=active] button').dataset.inspectFrame
          === document.querySelector('#app').dataset.activeFrame""")
        action('play').click()
    else:
        drawer('right')
        expect(app).to_have_attribute('data-playing','false')
        close_drawer('right')
    node(3).click()
    expect(inspector.get_by_role('heading',name='3번 노드')).to_be_visible()
    expect(inspector.locator('.tree-object')).to_have_count(1)
    expect(inspector.locator('tbody tr')).to_have_count(3)
    expect(inspector.locator('[data-cell-id="node-3.key"] .tree-cell-address')).to_have_text('&node-3.key')
    expect(inspector.locator('[data-cell-id="node-3.right"] .tree-cell-value')).to_have_text('NULL')
    close_pane()
    expect(node(3)).to_be_focused()
    if wide:
        expect(stack).to_be_visible()

    if not wide:
        drawer('left')
    expect(action('step').first).to_be_visible()
    expect(follow).to_be_hidden()
    scrub(0)
    viewport = page.locator('.stage-viewport')
    outer_top = viewport.evaluate('e => e.scrollTop')
    last = int(action('scrub').get_attribute('max'))
    scrub(last - 1)
    assert centered_rows(history_list) == [last-2, last-1, last]
    assert history_list.evaluate('e => e.scrollTop') > 0
    assert viewport.evaluate('e => e.scrollTop') == outer_top

    history_list.hover()
    page.mouse.wheel(0, -3000)
    expect(follow).to_be_visible()
    assert history_list.evaluate('e => e.scrollTop') == 0
    expect(action('step').first).to_be_visible()
    if wide:
        action('play').click()
    else:
        scrub(last)
    expect(app).to_have_attribute('data-playing', 'false')
    expect(explanation).to_have_text('루트 호출에서 반환해 순회를 마쳤어요.')
    assert history_list.evaluate('e => e.scrollTop') == 0
    follow.click()
    expect(follow).to_be_hidden()
    expect(history_list).to_be_focused()
    assert centered_rows(history_list) == [last-1, last]
    if wide:
        action('prev').click()
        action('play').click()
        expect(app).to_have_attribute('data-playing', 'false')
        expect(follow).to_be_hidden()
        assert centered_rows(history_list) == [last-1, last]
    scrub(last - 2)
    assert centered_rows(history_list, wait=True) == [last-3, last-2, last-1]

    expect(inspector).to_be_hidden()
    assert action('step').count() == int(action('scrub').get_attribute('max')) + 1
    expect(action('step').nth(1)).to_contain_text('main · 1행')
    expect(action('step').nth(left_null)).to_contain_text('inorder(1) · 3행')
    expect(action('step').nth(left_null+1)).to_contain_text('inorder(NULL) · 2행')
    expect(action('step').nth(first_print)).to_contain_text('inorder(1) · 4행')
    expect(action('step').filter(has_text='inorder(3) · 4행')).to_have_count(1)
    action('step').nth(left_null).click()
    expect(action('step').nth(left_null)).to_have_attribute('aria-pressed','true')
    expect(app).to_have_attribute('data-index',str(left_null))
    assert next_line() == ('walk',2)
    expect(explanation).to_have_text('1의 왼쪽 자식이 비어 있어 inorder(NULL)을 호출했어요.')
    expect(explanation).to_be_visible()

    if not wide:
        close_drawer('left')
        drawer('right')
    info_disclosure.locator('summary').click()
    expect(info_disclosure.get_by_text('inorder(root);', exact=True)).to_be_visible()
    assert '.pack/' not in info_disclosure.inner_text()
    assert '§4 순회' not in info_disclosure.inner_text()
    expect(info_disclosure.get_by_text('void inorder(Node *p)', exact=False)).to_have_count(0)
    if not wide:
        close_drawer('right')
        drawer('right')
        expect(info_disclosure).to_have_attribute('open','')
    info_disclosure.locator('summary').click()
    if not wide:
        close_drawer('right')

    if width >= 1280:
        node(1).click()
        preset('empty')
        expect(inspector).to_be_hidden()
    else:
        action('play').click()
        expect(app).to_have_attribute('data-playing','true')
        preset('empty')
    expect(app).to_have_attribute('data-playing','false')
    expect(app).to_have_attribute('data-index','0')
    expect(follow).to_be_hidden()
    if not wide:
        drawer('left')
    assert centered_rows(history_list) == [0, 1, 2]
    if not wide:
        close_drawer('left')
    assert app.get_attribute('data-selected-cell') is None
    action('next').click()
    assert next_line() == ('walk',2)
    expect(page.locator('.tree-empty')).to_contain_text('NULL')
    action('next').click()
    assert next_line() is None
    expect(explanation).to_have_text('루트가 NULL이므로 키를 출력하지 않고 순회를 마쳤어요.')
    open_options()
    for speed in ['0.5','1','2']:
        speed_button = page.locator(f'[data-speed="{speed}"]')
        speed_button.click()
        expect(speed_button).to_have_attribute('aria-pressed','true')
        expect(speed_trigger).to_have_text(f'{speed}×')
    close_options()
    jump('first')
    expect(app).to_have_attribute('data-index','0')
    jump('last')
    expect(app).to_have_attribute('data-index','2')
    action('prev').click()
    action('play').click()
    expect(app).to_have_attribute('data-playing','false')
    expect(app).to_have_attribute('data-index','2')
    assert next_line() is None

    page.locator('.tree-viewport').click(position={'x':5,'y':5})
    page.keyboard.press('Home')
    expect(app).to_have_attribute('data-index','0')
    page.keyboard.press('ArrowRight')
    expect(app).to_have_attribute('data-index','1')
    page.keyboard.press('End')
    expect(action('next')).to_be_disabled()

    preset('lecture')
    scene = page.locator('.tree-scene')
    scrub(7)
    position = scene.bounding_box()['y']
    scrub(8)
    assert abs(scene.bounding_box()['y'] - position) < 1, 'return message should keep the tree in place'
    assert page.evaluate("""() => [...document.querySelectorAll('.playbar button,.topbar button,.tree-header-tools select')]
      .filter(b=>b.getClientRects().length).every(b=>{
        const r=b.getBoundingClientRect();
        return r.width>=44 && r.height>=44 && r.left>=0 && r.right<=innerWidth && r.top>=0 && r.bottom<=innerHeight;
      })""")
    assert page.evaluate("""() => ['.tree-scene','.tree-output'].every(s=>{
      const r=document.querySelector(s).getBoundingClientRect();
      return r.top>=0 && r.bottom<=innerHeight && r.left>=0 && r.right<=innerWidth;
    })"""), 'lecture tree and output should fit together'
    assert page.locator('.tree-scene').evaluate("""e=>e.getBoundingClientRect().bottom <=
      e.closest('.stage-viewport').getBoundingClientRect().bottom + 1"""), 'whole tree must fit inside the visible viewport'
    return len(cases), total
