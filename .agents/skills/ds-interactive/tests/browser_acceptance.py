"""file:// offline browser acceptance. ROOT = repo or run folder, SCRATCH must be empty."""
from pathlib import Path
import json,sys,hashlib,re
from playwright.sync_api import sync_playwright
from browser_tree import check_history_touch, check_tree_case
import browser_study
from browser_header_selector import check_header_selector
from browser_graph_traversal import check_page as check_graph_traversal
from browser_graph_inspection import check_page as check_graph_inspection
from browser_graph_decisions import check_page as check_graph_decisions
from browser_graph_layout import GRAPH_VIEWPORTS, check_layout, mobile_first_screen, scene_order

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
  browser=pw.chromium.launch()
  def new_page(**kwargs):
   context=browser.new_context(offline=True,reduced_motion='reduce',**kwargs)
   context.route('**/*',lambda route: (external.append(route.request.url),route.abort()) if route.request.url.startswith(('http:','https:')) else route.continue_())
   page=context.new_page();page.set_default_timeout(10000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   return page
  desktop=new_page()
  touch=new_page(is_mobile=True,has_touch=True)
  page=desktop
  def left(opened):
   if page.viewport_size['width']<1024 and (page.locator('[data-action=toggle-left]').get_attribute('aria-expanded')=='true')!=opened:page.locator('[data-action=toggle-left]').click() if opened else page.keyboard.press('Escape')
  for file in pages:
   original=file.read_bytes();digest=hashlib.sha256(original).hexdigest()
   desktop.goto(file.as_uri());desktop.wait_for_selector('[data-snapshot="initial"]')
   kind=desktop.evaluate('DSInteractive.scenario.kind')
   ui_version=desktop.locator('#app').get_attribute('data-ui-version')
   viewports=(browser_study.VIEWPORTS if ui_version else
              GRAPH_VIEWPORTS if kind=='c-graph' else [(1440,900),(1024,768),(375,812)])
   if ui_version and int(ui_version)>=5:
    viewports=[*viewports,*browser_study.HEADER_VIEWPORTS]
   for width,height in viewports:
    page=touch if width<=375 and (ui_version or kind=='c-graph') else desktop
    for theme in ['light','dark']:
     page.emulate_media(color_scheme=theme)
     page.set_viewport_size({'width':width,'height':height});page.goto(file.as_uri());page.wait_for_selector('[data-snapshot="initial"]');page.evaluate('document.fonts.ready')
     if theme=='dark' and not page.locator('#interactive-theme').count():page.locator('[data-action=theme]').click()
     assert page.locator('html').get_attribute('data-theme')==theme
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(file,width,'overflow')
     assert page.evaluate("async () => (await document.fonts.load('400 16px Pretendard', '한글')).some(f => f.status === 'loaded')")
     if ui_version:
      topic=page.evaluate('DSInteractive.scenario.id')
      browser_study.check_layout(page, kind, width, height, theme)
      header_checked=check_header_selector(page) if int(ui_version)>=3 else {}
      if int(ui_version)>=5:
       browser_study.check_header_layout(page)
       header_checked['header_layout_checked']=True
      if int(ui_version)>=7:
       header_checked['header_padding_checked']=True
      mobile=browser_study.check_mobile_stages(page, kind, out, topic, theme) if width==375 else None
      if kind=='c-graph':
       view=page.locator('#app').get_attribute('data-graph-view')
       if view in ('mst', 'topo'):
        count, checked = check_graph_decisions(page, view)
       else:
        count, checked = (check_graph_traversal(page, width) if view=='traversal'
                          else check_graph_inspection(page, view))
      else:
       count, checked=browser_study.check_tree_or_memory(page, kind, width)
      if page.locator('.study-playback-options').is_visible():page.keyboard.press('Escape')
      browser_study.check_scene(page, kind, fallback=width<1280, first_screen=width==375)
      build=hashlib.sha256(re.sub(rb'(data-ds-interactive-font href=")[^"]*', rb'\g<1>', original, count=1)).hexdigest()
      page.screenshot(path=str(out/f'{topic}-{width}-{theme}.png'))
      results.append({'topic':topic,'file':file.name,'sha256':digest,'build_sha256':build,
                      'viewport':[width,height],'theme':theme,'kind':kind,'ui_version':int(ui_version),
                      'layout_checked':True,'controls_checked':True,'mobile_first_screen':mobile,
                      'preset_label_checked':int(ui_version)>=2,**header_checked,
                      **({'graph_history_checked': True} if kind=='c-graph' and int(ui_version)>=4 else {}),
                      'presets':count,'snapshots_checked':checked,'status':'pass'})
      print(f'{topic} {width} {theme}: common UI and {checked} snapshots',flush=True)
      continue
     if kind=='c-graph':
      view=page.evaluate("DSInteractive.scenario.graph?.view ?? 'traversal'")
      topic=page.evaluate('DSInteractive.scenario.id')
      check_layout(page, view, width, height, theme)
      mobile=mobile_first_screen(page, view, out, topic, theme) if width==375 else None
      count, checked = (check_graph_traversal(page, width) if view=='traversal'
                        else check_graph_inspection(page, view))
      if page.locator('.graph-playback-options').is_visible():page.keyboard.press('Escape')
      scene_order(page, view, width < 1280, first_screen=width==375)
      build=hashlib.sha256(re.sub(rb'(data-ds-interactive-font href=")[^"]*', rb'\g<1>', original, count=1)).hexdigest()
      topic=page.evaluate('DSInteractive.scenario.id')
      page.screenshot(path=str(out/f'{topic}-{width}-{theme}.png'))
      results.append({'topic':topic,'file':file.name,'sha256':digest,'build_sha256':build,
                      'viewport':[width,height],'theme':theme,'graph_view':view,'graph_layout_version':2,'mobile_first_screen':mobile,
                      'presets':count,'snapshots_checked':checked,'status':'pass'})
      print(f'{topic} {width} {theme}: graph layout and {checked} snapshots',flush=True)
      continue
     if kind=='c-tree':
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
