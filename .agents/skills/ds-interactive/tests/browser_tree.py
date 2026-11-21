"""Runtime acceptance for synchronized C tree execution, including drawer transitions."""

import re

from playwright.sync_api import expect


def check_tree_case(page, width, height):
    app = page.locator('#app')
    def action(name):
        return page.locator(f'[data-action={name}]')

    def scrub(step):
        action('scrub').evaluate(
            '(e,n)=>{e.value=n;e.dispatchEvent(new Event("input",{bubbles:true}));}', step
        )

    def drawer(side, show):
        if page.viewport_size['width'] >= 1024:
            return
        toggle = action('toggle-' + side)
        if (toggle.get_attribute('aria-expanded') == 'true') != show:
            toggle.click() if show else page.keyboard.press('Escape')
        expect(toggle).to_have_attribute('aria-expanded', str(show).lower())

    def preset(case):
        drawer('left', True)
        action('preset').select_option(case)
        drawer('left', False)

    def next_line():
        current = page.locator('.code-line.current')
        return (current.get_attribute('data-source-id'), int(current.get_attribute('data-line'))) if current.count() else None

    def node(node_id):
        return page.locator(f'[data-node-id="node-{node_id}"]')

    output = page.locator('.stdout-value')
    lesson = page.evaluate("DSInteractive.scenario.id") == 'inorder-1105'
    cases = action('preset').locator('option').evaluate_all('(options)=>options.map(option=>option.value)')
    expected_outputs = {'default': '1 3 8 10 ', 'lecture': '3 7 12 18 26 27 31 ', 'empty': ''}
    total = 0
    for case in cases:
        preset(case)
        states = page.evaluate(
            """() => {
              const D=DSInteractive;
              const input=Object.fromEntries([...document.querySelectorAll('[data-input]')]
                .map(e=>[e.dataset.input,e.type==='number'?Number(e.value):e.value]));
              const t=D.compileScenario(D.scenario,input);
              return t.lineSteps.map(step=>({id:step.id,next:step.next,stdout:step.state.stdout.join(''),
                frame:step.state.activeFrame??'',view:D.getTreeView(t.metadata.tree,step)}));
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
                'frame':state['frame'], 'overflow':False,
                'nodes':[[n['id'],points[n['id']],str(n['outputOrder']) if n['outputOrder'] else None]
                         for n in state['view']['nodes']],
            }, (case, index, actual)
        if lesson:
            assert output.text_content() == expected_outputs[case]
        assert action('next').is_disabled()
        assert next_line() is None
        total += len(states)

    preset('default')
    if not lesson:
        return len(cases), total
    action('next-output').click()
    expect(node(1)).to_have_attribute('data-output-order','1')
    first_print = int(app.get_attribute('data-index'))
    assert output.text_content() == '1 '
    assert action('previous-output').is_disabled()
    action('prev').click()
    assert next_line() == ('walk',4) and output.text_content() == ''
    assert node(1).get_attribute('data-output-order') is None
    assert page.locator('[data-ended-frame]').count() == 1
    action('prev').click()
    left_null = int(app.get_attribute('data-index'))
    assert next_line() == ('walk',2)
    expect(page.locator('[data-null-side=left]')).to_have_attribute('data-parent-node','node-1')
    expect(page.locator('.tree-summary')).to_contain_text('NULL')
    action('next-output').click()
    assert int(app.get_attribute('data-index')) == first_print
    action('next-output').click()
    assert output.text_content() == '1 3 '
    action('previous-output').click()
    assert output.text_content() == '1 '
    action('next').click()
    expect(page.locator('[data-null-side=right]')).to_have_attribute('data-parent-node','node-1')
    action('next').click()
    assert next_line() == ('walk',6)

    node(1).click()
    expect(node(1)).to_have_attribute('aria-pressed','true')
    drawer('right', True)
    key = page.locator('.tree-memory [data-cell-id="node-1.key"]')
    expect(key).to_have_attribute('aria-pressed','true')
    stack = page.locator('.tree-stack')
    parameter = stack.locator('[data-frame-state=active] button').first
    parameter.click()
    expect(node(1)).to_have_class(re.compile(r'\bselected\b'))
    expect(parameter.locator('.tree-cell-value')).to_have_text('&node-1')
    expect(parameter.locator('.tree-cell-address')).to_contain_text('.p')
    expect(key.locator('.tree-cell-address')).to_have_text('자기 주소 &node-1.key')
    selected = app.get_attribute('data-selected-cell')
    current = app.get_attribute('data-snapshot')
    if width < 1024:
        page.set_viewport_size({'width':1024,'height':height})
        expect(page.locator('#panel-right')).not_to_have_attribute('aria-modal','true')
        expect(action('toggle-right')).to_be_focused()
        assert page.evaluate("!document.activeElement.closest('[aria-hidden=true]')")
        assert app.get_attribute('data-snapshot') == current
        assert app.get_attribute('data-selected-cell') == selected
        page.set_viewport_size({'width':width,'height':height})
        expect(action('toggle-right')).to_have_attribute('aria-expanded','false')
        assert page.evaluate("!document.activeElement.closest('[aria-hidden=true]')")
    else:
        expect(parameter).to_be_focused()

    action('play').click()
    expect(app).to_have_attribute('data-playing','true')
    preset('empty')
    expect(app).to_have_attribute('data-playing','false')
    expect(app).to_have_attribute('data-index','0')
    assert app.get_attribute('data-selected-cell') is None
    action('next').click()
    assert next_line() == ('walk',2)
    expect(page.locator('.tree-summary')).to_contain_text('NULL')
    action('next').click()
    assert next_line() is None
    for speed in ['0.5','1','2']:
        page.locator(f'[data-speed="{speed}"]').click()
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

    preset('default')
    scrub(left_null)
    assert page.evaluate("""() => [...document.querySelectorAll('.playbar button,.topbar button,.tree-jumps button')]
      .filter(b=>b.getClientRects().length).every(b=>{
        const r=b.getBoundingClientRect();
        return r.width>=44 && r.height>=44 && r.left>=0 && r.right<=innerWidth && r.top>=0 && r.bottom<=innerHeight;
      })""")
    return len(cases), total
