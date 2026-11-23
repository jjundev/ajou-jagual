"""file:// offline browser acceptance. ROOT = repo or run folder, SCRATCH must be empty."""
from pathlib import Path
import json,sys,hashlib
from playwright.sync_api import sync_playwright
from browser_tree import check_history_touch, check_tree_case
from browser_graph_traversal import check_page as check_graph_traversal

def discover_pages(root):
 root=Path(root).resolve()
 if root.is_file() and root.suffix=='.html':return [root]
 if (root/'preview.html').is_file():return [root/'preview.html']
 published=sorted((root/'복습노트').glob('**/인터렉티브_*.html')) if (root/'복습노트').is_dir() else sorted(root.glob('인터렉티브_*.html'))
 return published or sorted(root.glob('**/preview.html'))

def main(root,scratch):
 root=Path(root).resolve();out=Path(scratch).resolve();out.mkdir(parents=True,exist_ok=True)
 assert not list(out.iterdir()),'SCRATCH must be empty'
 pages=discover_pages(root)
 assert pages,'No materials found: pass a repository, date directory, RUN directory or HTML file'
 results=[];errors=[];external=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch();context=browser.new_context(offline=True,reduced_motion='reduce')
  context.route('**/*',lambda route: (external.append(route.request.url),route.abort()) if route.request.url.startswith(('http:','https:')) else route.continue_())
  page=context.new_page();page.set_default_timeout(10000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  def left(opened):
   if page.viewport_size['width']<1024 and (page.locator('[data-action=toggle-left]').get_attribute('aria-expanded')=='true')!=opened:page.locator('[data-action=toggle-left]').click() if opened else page.keyboard.press('Escape')
  for file in pages:
   digest=hashlib.sha256(file.read_bytes()).hexdigest()
   for width,height in [(1440,900),(1024,768),(375,812)]:
    for theme in ['light','dark']:
     page.set_viewport_size({'width':width,'height':height});page.goto(file.as_uri());page.wait_for_selector('[data-snapshot="initial"]');page.evaluate('document.fonts.ready')
     if theme=='dark':page.locator('[data-action=theme]').click()
     assert page.locator('html').get_attribute('data-theme')==theme
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(file,width,'overflow')
     assert page.evaluate("async () => (await document.fonts.load('400 16px Pretendard', '한글')).some(f => f.status === 'loaded')")
     if page.locator('.graph-scene').count():
      count, checked = check_graph_traversal(page, width, height)
      topic = page.evaluate('DSInteractive.scenario.id')
      page.screenshot(path=str(out/f'{topic}-{width}-{theme}.png'))
      results.append({'topic':topic,'file':file.name,'sha256':digest,'viewport':[width,height],
                      'theme':theme,'presets':count,'snapshots_checked':checked,'status':'pass'})
      continue
     if page.evaluate('DSInteractive.scenario.kind')=='c-tree':
      topic=page.evaluate('DSInteractive.scenario.id')
      page.screenshot(path=str(out/f'{file.parent.name}-{topic}-{width}-{theme}.png'),full_page=True)
      count,checked,current_node_checked=check_tree_case(page,width,height)
      if width<1280:page.locator('[data-action=toggle-left]').click()
      history=page.get_by_role('heading',name='줄 기록',exact=True)
      history.scroll_into_view_if_needed()
      page.wait_for_function("""() => {
        const list=document.querySelector('.tree-history .step-list');
        const active=list.querySelector('[aria-pressed=true]').getBoundingClientRect();
        const visible=list.getBoundingClientRect();
        return active.top>=visible.top && active.bottom<=visible.bottom;
      }""")
      page.screenshot(path=str(out/f'{file.parent.name}-{topic}-{width}-{theme}-history.png'),full_page=True)
      if width<1280:
       page.keyboard.press('Escape')
       page.locator('[data-action=toggle-right]').click()
      page.screenshot(path=str(out/f'{file.parent.name}-{topic}-{width}-{theme}-stack.png'),full_page=True)
      if width<1280:page.keyboard.press('Escape')
      first_node=page.locator('.tree-node.active')
      if first_node.count():
       first_node.click()
       page.screenshot(path=str(out/f'{file.parent.name}-{topic}-{width}-{theme}-node.png'),full_page=True)
       page.keyboard.press('Escape')
      touch_checked=topic=='inorder-1105' and width==375 and theme=='light'
      if touch_checked:
       check_history_touch(browser,file.as_uri())
      print(f'{topic} {width} {theme}: {checked} line steps',flush=True)
      results.append({'topic':topic,'file':file.name,'sha256':digest,
                      'viewport':[width,height],'theme':theme,'presets':count,'snapshots_checked':checked,
                      'touch_checked':touch_checked,'current_node_checked':current_node_checked,'status':'pass'})
      continue
     left(True)
     presets=page.locator('[data-action=preset] option').evaluate_all('(es)=>es.map(e=>e.value)');steps_checked=0
     for preset in presets:
      left(True);page.locator('[data-action=preset]').select_option(preset);left(False)
      states=page.evaluate('DSInteractive.compileScenario(DSInteractive.scenario,Object.fromEntries([...document.querySelectorAll("[data-input]")].map(e=>[e.dataset.input,e.type==="number"?Number(e.value):e.value]))).snapshots');count=len(states)
      for step in range(count):
       page.locator('[data-action=scrub]').evaluate('(e,n)=>{e.value=n;e.dispatchEvent(new Event("input",{bubbles:true}));}',step)
       expected='initial' if step==0 else f'step-{step}'
       assert page.locator('#app').get_attribute('data-snapshot')==expected
       assert page.locator('.code').get_attribute('data-step')==expected
       assert page.locator('.memory').get_attribute('data-step')==expected
       assert page.locator('output[data-step]').inner_text()==f'{step} / {count-1}'
       # Compare rendered storage to the shared Trace; Python oracle checks semantics separately.
       state=states[step]
       rendered=page.locator('[data-cell-id]').evaluate_all('(es)=>Object.fromEntries(es.map(e=>[e.dataset.cellId,e.querySelector(".cell-value")?.textContent]))')
       for cell in state['state']['cells'].values():
        row=rendered.get(cell['id'])
        v=cell['value'];value=str(v['value']) if v['kind']=='int' else ('NULL' if v['target'] is None else '&'+v['target']) if v['kind']=='pointer' else '미초기화' if v['kind']=='uninitialized' else '사용 불가'
        assert row==('수명 종료 · '+value if cell['lifetime']=='ended' else value),(file,preset,step,cell,row)
       current=page.locator('.code-line.current');assert current.get_attribute('data-line')==str(state['at']['line'])
       assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
       steps_checked+=1
      if width<1024:
       left(True);assert page.locator('.source-pane').is_visible();left(False);assert page.locator('.memory-pane').is_visible()
      assert page.locator('[data-action=next]').is_disabled()
      page.locator('[data-action=first]').click();assert page.locator('#app').get_attribute('data-index')=='0'
      page.locator('[data-action=next]').click();assert page.locator('#app').get_attribute('data-index')=='1'
      page.locator('[data-action=prev]').click();assert page.locator('#app').get_attribute('data-index')=='0'
      page.locator('[data-action=last]').click();assert page.locator('#app').get_attribute('data-index')==str(count-1)
     left(True);page.locator('[data-action=preset]').select_option('default');num=page.locator('input[type=number]').first
     for value in ['-99','99']:
      num.fill(value);num.dispatch_event('change');assert page.locator('#app').get_attribute('data-index')=='0';assert page.locator('.input-error').inner_text()==''
     left(False);page.locator('[data-action=last]').click();left(True);num.fill('');num.dispatch_event('change');assert page.locator('[data-action=play]').is_disabled();assert page.locator('.input-error').inner_text();assert page.locator('#app').get_attribute('data-index')=='0'
     page.locator('[data-action=preset]').select_option('default');left(False);page.locator('[data-action=play]').click();assert page.locator('#app').get_attribute('data-playing')=='true'
     left(True);num.fill('7');num.dispatch_event('change');assert page.locator('#app').get_attribute('data-playing')=='false';assert page.locator('#app').get_attribute('data-index')=='0';page.wait_for_timeout(550);assert page.locator('#app').get_attribute('data-index')=='0'
     left(False);page.locator('[data-action=next]').click();page.locator('[data-cell-id]').first.click();assert page.locator('.cell.selected').count()==1
     page.locator('body').click(position={'x':3,'y':3});page.keyboard.press('Home');assert page.locator('#app').get_attribute('data-index')=='0';page.keyboard.press('ArrowRight');assert page.locator('#app').get_attribute('data-index')=='1';page.keyboard.press('End');assert page.locator('[data-action=next]').is_disabled()
     for speed in ['0.5','1','2']:page.locator('[data-speed="'+speed+'"]').click()
     # Last transition at 2x must stop its own timer.
     page.locator('[data-action=prev]').click();page.locator('[data-action=play]').click();page.wait_for_timeout(550);assert page.locator('#app').get_attribute('data-playing')=='false'
     left(True);page.locator('[data-action=preset]').select_option('default');left(False);page.locator('[data-action=scrub]').evaluate('(e)=>{e.value=Math.min(6,Number(e.max));e.dispatchEvent(new Event("input",{bubbles:true}));}')
     topic=page.evaluate('DSInteractive.scenario.id')
     page.screenshot(path=str(out/f'{file.parent.name}-{topic}-{width}-{theme}.png'),full_page=True)
     print(f'{topic} {width} {theme}: {steps_checked} snapshots',flush=True)
     results.append({'topic':topic,'file':file.name,'sha256':digest,'viewport':[width,height],'theme':theme,'presets':len(presets),'snapshots_checked':steps_checked,'status':'pass'})
   assert hashlib.sha256(file.read_bytes()).hexdigest()==digest, (file,'changed during browser checks')
  browser.close()
 assert not errors,errors;assert not external,external
 report={'status':'pass','transport':'file://, offline=True','results':results,'console_errors':errors,'external_requests':external}
 (out/'browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':'pass','combinations':len(results),'snapshots_checked':sum(x['snapshots_checked'] for x in results),'external_requests':len(external),'console_errors':len(errors)}))
if __name__=='__main__':main(*sys.argv[1:3])
