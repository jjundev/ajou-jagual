"""Run synthetic browser acceptance: python browser_acceptance.py EMPTY_SCRATCH."""
import sys,json
from pathlib import Path
SKILL=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(SKILL/'scripts'),str(SKILL/'tests')]
from helpers import acceptance_pack
from mpe_render import build_explanation,check_artifacts
from playwright.sync_api import sync_playwright
root=Path(sys.argv[1]).resolve();root.mkdir(parents=True,exist_ok=True)
if any(root.iterdir()): raise SystemExit('acceptance scratch must be empty')
pack,fragments=acceptance_pack(root/'repo')
import shutil
shutil.rmtree(root/'stage',ignore_errors=True)
art=build_explanation(pack,fragments,root/'stage',root/'repo')
assert check_artifacts(pack,art)==[]
# p2 stands in for a problem without an original (helpers' review sources always carry one)
import re
art.html.write_text(re.sub(r'<details class="original" data-original-problem="p2">.*?</details>','',art.html.read_text(),count=1,flags=re.S))
from mpe_preview import preview_server

results=[]
with preview_server((art,)) as (server, paths), sync_playwright() as pw:
 port=server.server_port
 url=f'http://127.0.0.1:{port}{paths[0]}'
 browser=pw.chromium.launch()
 for width,height in [(1280,900),(1024,768),(375,812)]:
  for theme in ['light','dark']:
   page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme)
   logs=[];failed=[];external=[]
   page.on('pageerror',lambda e:logs.append(str(e)))
   page.on('console',lambda e:logs.append(e.text) if e.type=='error' else None)
   page.on('requestfailed',lambda r:failed.append(r.url))
   page.on('response',lambda r:failed.append(str(r.status)+' '+r.url) if r.status>=400 else None)
   page.on('request',lambda r:external.append(r.url) if not r.url.startswith(f'http://127.0.0.1:{port}/') else None)
   page.goto(url+'#p1',wait_until='networkidle');page.wait_for_timeout(100)
   if width>=1024:
    assert page.locator('#panel-prob .probs [data-problem-for="p1"]').is_visible()
    assert page.locator('#p1 > [data-problem-for]').count()==0
    assert page.locator('#panel-prob [role=tab][data-tab="problem"]').get_attribute('aria-selected')=='true'
    assert page.locator('#panel-right').is_hidden() and page.locator('#toggle-prob').get_attribute('aria-expanded')=='true'
    L,P,C=[page.locator(s).bounding_box() for s in ('#panel-left','#panel-prob','.content')]
    assert P['x']+P['width']<=C['x']+1 and (not page.locator('#panel-left').is_visible() or L['x']+L['width']<=P['x']+1)
    assert page.locator('#panel-right-title').inner_text()=='페이지 요약' and page.locator('#toggle-right').inner_text()=='요약'
    assert page.locator('#tab-original').is_visible()
    page.locator('#tab-original').click()
    orig=page.locator('#tabpanel-original details.original[data-original-problem="p1"][open]')
    assert orig.is_visible() and '원래 질문' in orig.inner_text()
    assert orig.locator('summary').is_hidden() and page.locator('#tabpanel-problem').is_hidden()
    assert page.locator('[data-problem-for="p1"] details.original').count()==0
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.locator('#p1 [data-problem-for="p1"] details.original:not([open])').count()==1
    page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(150)
    assert page.locator('details.original[data-original-problem="p1"]').count()==1 and orig.is_visible()
    page.goto(url+'#p2');page.wait_for_timeout(100)
    assert page.locator('#tab-original').is_hidden()
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true' and page.locator('[data-problem-for="p2"]').is_visible()
    page.goto(url+'#p1');page.wait_for_timeout(100)
    assert page.locator('#tab-original').get_attribute('aria-selected')=='true'
    page.locator('#tab-original').focus();page.keyboard.press('ArrowRight')
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true'
   else:
    toggle=page.locator('#p1 .problem-toggle')
    assert toggle.get_attribute('aria-expanded')=='false' and not page.locator('#p1 [data-problem-for="p1"]').is_visible()
    toggle.click();assert page.locator('#p1 [data-problem-for="p1"]').is_visible() and toggle.inner_text()=='문제 접기'
    assert page.locator('#p1 [data-problem-for="p1"] details.original:not([open])').count()==1
    assert page.locator('#tab-original').is_hidden()
    assert page.locator('#toggle-prob').is_hidden() and page.locator('#panel-prob').is_hidden()
   assert page.locator('#p1 [data-explanation="understand"]').is_visible()
   # long code in the problem scrolls inside its own block, never the document
   if width<1024 and page.locator('#p1 .problem-toggle').get_attribute('aria-expanded')=='false':page.locator('#p1 .problem-toggle').click()
   pre=page.locator('[data-problem-for="p1"] pre:visible').first
   assert pre.evaluate("e=>e.scrollWidth>e.clientWidth&&['auto','scroll'].includes(getComputedStyle(e).overflowX)")
   assert page.evaluate('document.scrollingElement.scrollWidth<=innerWidth')
   if width<1024:page.locator('#p1 .problem-toggle').click()
   page.goto(url+'#p2');page.wait_for_timeout(100)
   if width<1024:
    page.locator('#p2 .problem-toggle').click()
    assert page.locator('#p2 [data-problem-for="p2"] details.original').count()==0
   assert page.locator('.verdict-card').count()==0 and page.locator('.review-choice').count()==0
   if width>=1024:
    page.goto(url+'#p2');page.wait_for_timeout(100)
    page.locator('[data-problem-for="p2"] img').first.click()
    assert page.locator('dialog.figure-sheet[open] img').is_visible()
    page.keyboard.press('Escape');page.wait_for_timeout(100)
    assert page.locator('dialog.figure-sheet[open]').count()==0
    page.locator('[data-problem-for="p2"] svg[aria-label="문제 화살표"]').click()
    assert page.locator('dialog.figure-sheet[open] svg').is_visible()
    assert page.evaluate('(()=>{const a=[...document.querySelectorAll("[id]")].map(e=>e.id);return a.length===new Set(a).size})()')
    page.keyboard.press('Escape');page.wait_for_timeout(100)
   page.goto(url+'#p1');page.wait_for_timeout(100)
   page.emulate_media(media='print');page.wait_for_timeout(150)
   assert page.locator('#p1 > [data-problem-for="p1"] [data-source-problem="p1"]').is_visible()
   assert page.locator('#p1 > [data-problem-for="p1"]').is_visible() and page.locator('.problem-toggle:visible').count()==0
   assert page.locator('#p1 > [data-problem-for="p1"] details.original[open]').is_visible()
   page.emulate_media(media='screen');page.wait_for_timeout(150)
   if width>=1024:assert page.locator('#panel-prob .probs [data-problem-for="p1"]').is_visible()
   else:assert page.locator('#p1 .problem-toggle').is_visible()
   page.goto(url,wait_until='networkidle')
   page.locator('#pager-next').click();page.wait_for_timeout(100)
   assert page.locator('#p1').is_visible()
   for token in ['pre code','table','svg[aria-label="상태 그림"]','img']:
    assert page.locator(f'#p1 {token}, [data-problem-for="p1"] {token}').count()>0,token
   assert page.locator('#p1 .katex').count()>0
   assert page.locator('#p1 [data-explanation="start"] .katex').first.evaluate('(e)=>getComputedStyle(e).overflowX')=='visible'
   page.locator('#toggle-right').click()
   page.wait_for_timeout(250)
   assert page.locator('#panel-right').is_visible()
   assert page.locator('#panel-right .summary-group').count()>0
   if width<800:page.locator('#panel-right [data-panel-close]').click()
   else:
    handle=page.locator('#panel-right .panel-resize');handle.focus();handle.press('ArrowLeft');handle.press('Home')
    page.locator('#toggle-right').click()
   page.locator('#pager-next').click();assert page.locator('#p2').is_visible()
   page.locator('#pager-prev').click();assert page.locator('#p1').is_visible()
   page.locator('#toggle-left').click();page.wait_for_timeout(250)
   if width>=1024 and page.locator('#toggle-left').get_attribute('aria-expanded')=='false':page.locator('#toggle-left').click()
   page.locator('#panel-left a[href="#p2"]').click();page.wait_for_timeout(150)
   assert page.locator('#p2').is_visible()
   page.locator('#theme-toggle').click();page.wait_for_timeout(100)
   page.locator('#theme-toggle').click()
   page.set_viewport_size({'width':width+10,'height':height});page.set_viewport_size({'width':width,'height':height})
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   assert page.locator('.katex-error').count()==0
   assert page.locator('#p2 img[alt="검증용 픽셀"]').evaluate('(e)=>e.complete && e.naturalWidth>0')
   page.screenshot(path=str(root/f'{width}-{theme}.png'),full_page=True)
   assert not logs and not failed and not external,(logs,failed,external)
   if (width,theme)==(1280,'light'):
    # cross: closed problem panel stays closed across the 1024 boundary
    page.locator('#toggle-prob').click();assert page.locator('#panel-prob').is_hidden()
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.locator('#p2 .problem-toggle').count()==1 and page.locator('#toggle-prob').is_hidden()
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150)
    assert page.locator('#panel-prob').is_hidden();page.locator('#toggle-prob').click()
    # grow: widening the problem panel leaves the content readable
    if page.locator('#toggle-left').get_attribute('aria-expanded')=='false':page.locator('#toggle-left').click()
    h=page.locator('#panel-prob .panel-resize');h.focus()
    for _ in range(20):h.press('Shift+ArrowRight')
    assert page.locator('.content').bounding_box()['width']>=380
    # widened problem panel + summary: the problem panel narrows for now instead of disappearing
    page.locator('#toggle-right').click();page.wait_for_timeout(250)
    assert all(page.locator(s).is_visible() for s in ('#panel-left','#panel-prob','#panel-right'))
    assert page.locator('.content').bounding_box()['width']>=320 and page.evaluate('document.querySelector(".layout").scrollWidth<=innerWidth')
    page.locator('#toggle-right').click();page.wait_for_timeout(250)
    assert page.locator('#panel-prob').bounding_box()['width']>=600
    h.press('Home')
    # crowded: at 1024 three panels do not fit, so the TOC steps aside until there is room again
    page.set_viewport_size({'width':1024,'height':768});page.wait_for_timeout(150)
    if page.locator('#panel-right').is_hidden():page.locator('#toggle-right').click()
    page.wait_for_timeout(250)
    assert page.locator('#panel-prob').is_visible() and page.locator('#panel-right').is_visible()
    assert page.locator('#panel-left').is_hidden() and page.locator('#toggle-left').get_attribute('aria-expanded')=='false'
    assert page.evaluate('document.querySelector(".layout").scrollWidth<=innerWidth') and page.locator('.content').bounding_box()['width']>=320
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(250)
    assert all(page.locator(s).is_visible() for s in ('#panel-left','#panel-prob','#panel-right'))
    assert page.locator('.content').bounding_box()['width']>=320
    # legacy: old saved panel state and a saved summary tab fall back to the problem panel
    page.evaluate("localStorage.clear();localStorage.setItem('od-panels:explain','{\"right\":true}');localStorage.setItem('ds-problem-explain-tab','\"summary\"')")
    page.goto(url+'#p1');page.reload();page.wait_for_timeout(150)
    assert page.locator('#panel-right').is_hidden() and page.locator('#panel-prob').is_visible()
    assert page.locator('#tab-problem').get_attribute('aria-selected')=='true'
    box=lambda s:page.locator(s).bounding_box()
    def drag(a,b,steps=8):page.mouse.move(*a);page.mouse.down();page.mouse.move(*b,steps=steps);page.mouse.up();page.wait_for_timeout(150)
    def headgap():T,G=box('#panel-prob .panel-tabs'),box('#panel-prob .prob-dock');return ((T['x']+T['width']+G['x'])/2,T['y']+T['height']/2)
    page.evaluate('localStorage.clear()');page.goto(url+'#p1');page.reload();page.wait_for_timeout(150)
    assert page.locator('#panel-prob [data-dock="left"]').get_attribute('aria-checked')=='true'
    # radios: arrows pick the next position without turning the page
    page.locator('#panel-prob [data-dock="left"]').focus();page.keyboard.press('ArrowRight');page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='right' and page.evaluate('document.activeElement.dataset.dock')=='right' and page.locator('#p1').is_visible()
    page.keyboard.press('ArrowLeft');page.wait_for_timeout(150);assert page.locator('.layout').get_attribute('data-prob-dock')=='left'
    assert page.evaluate("[...document.querySelectorAll('.prob-dock [role=radio]')].map(b=>b.tabIndex)")==[0,-1,-1]
    # tab-no-drag: clicking a tab in the docked head does not undock
    page.locator('#tab-original').click();assert page.locator('.layout').get_attribute('data-prob-dock')=='left';page.locator('#tab-problem').click()
    # right: content | prob | summary, toggle sits before 요약, both open independently
    page.locator('#panel-prob [data-dock="right"]').click();page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='right' and page.locator('#panel-prob [data-dock="right"]').get_attribute('aria-checked')=='true'
    assert box('#panel-prob')['x']>=box('.content')['x']+box('.content')['width']-1
    assert abs(box('#panel-prob')['y']-box('.content')['y'])<=1 and page.evaluate('document.querySelector(".layout").scrollHeight<=document.querySelector(".layout").clientHeight+1')  # one row
    assert page.evaluate("document.getElementById('toggle-prob').nextElementSibling.id")=='toggle-right'
    w0=box('#panel-prob')['width'];h=page.locator('#panel-prob .panel-resize');h.focus();h.press('ArrowLeft');assert box('#panel-prob')['width']>w0;h.press('Home')  # right-docked handle sits on the left edge: ArrowLeft widens
    page.locator('#toggle-right').click();page.wait_for_timeout(250)
    assert box('#panel-prob')['x']+box('#panel-prob')['width']<=box('#panel-right')['x']+1
    page.locator('#toggle-prob').click();assert page.locator('#panel-prob').is_hidden() and page.locator('#panel-right').is_visible()
    page.locator('#toggle-prob').click();page.wait_for_timeout(150);assert page.locator('.layout').get_attribute('data-prob-dock')=='right'
    # right-crowded: at 1024 the TOC steps aside first
    page.set_viewport_size({'width':1024,'height':768});page.wait_for_timeout(250)
    assert page.locator('#panel-prob').is_visible() and page.locator('#panel-right').is_visible() and page.locator('#panel-left').is_hidden()
    assert page.evaluate('document.querySelector(".layout").scrollWidth<=innerWidth') and box('.content')['width']>=320
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(250);page.locator('#toggle-right').click();page.wait_for_timeout(250)
    # float: fixed card, content grows, default geometry under the top bar
    cw=box('.content')['width'];page.locator('#panel-prob [data-dock="float"]').click();page.wait_for_timeout(150)
    assert page.locator('#panel-prob').evaluate('e=>getComputedStyle(e).position')=='fixed' and box('.content')['width']>cw
    F=box('#panel-prob');top=box('.topbar');assert abs(F['width']-420)<=1 and F['y']>=top['y']+top['height']
    assert page.evaluate("document.getElementById('toggle-prob').previousElementSibling.id")=='toggle-left'
    # move by the grip, resize by the corner, both clamp
    M=box('#panel-prob .float-move');drag((M['x']+M['width']/2,M['y']+M['height']/2),(M['x']+M['width']/2-200,M['y']+M['height']/2+100))
    F2=box('#panel-prob');assert abs(F2['x']-(F['x']-200))<=1 and abs(F2['y']-(F['y']+100))<=1
    R=box('#panel-prob .float-resize');drag((R['x']+R['width']/2,R['y']+R['height']/2),(R['x']-600,R['y']-600))
    F3=box('#panel-prob');assert abs(F3['width']-280)<=1 and abs(F3['height']-200)<=1
    page.locator('#panel-prob .float-move').focus();page.keyboard.press('ArrowRight');assert abs(box('#panel-prob')['x']-(F3['x']+16))<=1
    # at the minimum size the tabs stay on one line and the head does not overflow
    assert page.evaluate("['tab-problem','tab-original'].every(id=>{const r=document.createRange();r.selectNodeContents(document.getElementById(id));return new Set([...r.getClientRects()].map(c=>Math.round(c.top))).size===1})") and page.evaluate("(h=>h.scrollWidth<=h.clientWidth)(document.querySelector('#panel-prob .panel-head'))")
    # corner drag shows the diagonal cursor
    R=box('#panel-prob .float-resize');page.mouse.move(R['x']+8,R['y']+8);page.mouse.down();page.mouse.move(R['x']+30,R['y']+30,steps=3)
    assert page.evaluate('getComputedStyle(document.body).cursor')=='nwse-resize';page.mouse.up();page.wait_for_timeout(100)
    # Enter on the corner restores the default size
    page.locator('#panel-prob .float-resize').focus();page.keyboard.press('Enter');assert abs(box('#panel-prob')['width']-420)<=1
    # the window stays above the 이전/다음 bar
    M=box('#panel-prob .float-move');drag((M['x']+M['width']/2,M['y']+M['height']/2),(M['x']+M['width']/2,M['y']+2000))
    assert box('#panel-prob')['y']+box('#panel-prob')['height']<=box('.pager')['y']+1
    # reload keeps float + geometry
    F4=box('#panel-prob');page.reload();page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='float' and abs(box('#panel-prob')['x']-F4['x'])<=1
    # float-cross: narrow screen hides it, coming back restores it; focus moves to the inline toggle
    page.locator('#panel-prob .float-move').focus()
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.locator('#panel-prob').is_hidden() and page.locator('#p1 .problem-toggle').count()==1
    assert page.evaluate("document.activeElement===document.querySelector('#p1 .problem-toggle')")
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150)
    assert page.locator('#panel-prob').is_visible() and abs(box('#panel-prob')['x']-F4['x'])<=1
    # a drag cut off by the screen narrowing below 1024 ends cleanly
    M=box('#panel-prob .float-move');page.mouse.move(M['x']+5,M['y']+5);page.mouse.down();page.mouse.move(M['x']-40,M['y']+40,steps=4)
    page.set_viewport_size({'width':900,'height':height});page.wait_for_timeout(150)
    assert page.evaluate("!document.body.classList.contains('is-dragging')&&getComputedStyle(document.body).cursor!=='grabbing'")
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150);page.mouse.up();page.wait_for_timeout(100)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='float';F4=box('#panel-prob')
    # snap: dragging to the right edge shows the preview, dropping docks right
    M=box('#panel-prob .float-move');page.mouse.move(M['x']+5,M['y']+5);page.mouse.down();page.mouse.move(1270,M['y']+5,steps=8)
    assert page.locator('.dock-preview').is_visible();page.mouse.up();page.wait_for_timeout(150)
    assert page.locator('.layout').get_attribute('data-prob-dock')=='right' and page.locator('.dock-preview').is_hidden()
    # undock: dragging the docked head's empty gap 24px+ makes it float under the pointer
    g=headgap();drag(g,(640,400))
    assert page.locator('.layout').get_attribute('data-prob-dock')=='float';F5=box('#panel-prob')
    assert F5['x']<=640<=F5['x']+F5['width'] and F5['y']<=400<=F5['y']+F5['height']
    # float-clamp: a saved position from a bigger screen comes back inside
    page.evaluate("localStorage.setItem('od-panels:explain:v2:prob',JSON.stringify({dock:'float',x:1500,y:-50,w:420,h:500}))")
    page.set_viewport_size({'width':1100,'height':height});page.reload();page.wait_for_timeout(150)
    F6=box('#panel-prob');top=box('.topbar');assert F6['x']>=0 and F6['x']+F6['width']<=1100 and F6['y']>=top['y']+top['height']
    # bad-pref: unknown dock or broken JSON falls back to left
    for v in ['{"dock":"top"}','{broken']:
     page.evaluate(f"localStorage.setItem('od-panels:explain:v2:prob',{json.dumps(v)})");page.reload();page.wait_for_timeout(150)
     assert page.locator('.layout').get_attribute('data-prob-dock')=='left'
    page.set_viewport_size({'width':1280,'height':height});page.wait_for_timeout(150)
    assert not logs,logs
   results.append({'viewport':[width,height],'theme':theme,'console_errors':logs,'failed_resources':failed,'external_requests':external,'overflow':False,'interaction':'TOC, next/prev, summary, close, resize, theme pass'})
   page.close()
 # touch: a tablet-wide touch screen can move the floating window by its grip and undock the head
 ctx=browser.new_context(viewport={'width':1180,'height':820},has_touch=True);page=ctx.new_page();cdp=ctx.new_cdp_session(page)
 page.goto(url+'#p1',wait_until='networkidle');page.evaluate("localStorage.setItem('od-panels:explain:v2:prob',JSON.stringify({dock:'float'}))");page.reload();page.wait_for_timeout(200)
 def touchdrag(x,y,dx,dy):
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
  for i in range(1,11):cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+dx*i/10,'y':y+dy*i/10}]});page.wait_for_timeout(16)
  cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});page.wait_for_timeout(150)
 B0=page.locator('#panel-prob').bounding_box();M=page.locator('#panel-prob .float-move').bounding_box()
 touchdrag(M['x']+M['width']/2,M['y']+M['height']/2,-150,60);B1=page.locator('#panel-prob').bounding_box()
 assert abs(B1['x']-(B0['x']-150))<=2 and abs(B1['y']-(B0['y']+60))<=2,(B0,B1)
 page.locator('#panel-prob [data-dock="left"]').click();page.wait_for_timeout(150)
 T,G=[page.locator(s).bounding_box() for s in ('#panel-prob .panel-tabs','#panel-prob .prob-dock')]
 touchdrag((T['x']+T['width']+G['x'])/2,T['y']+T['height']/2,300,200)
 assert page.locator('.layout').get_attribute('data-prob-dock')=='float'
 ctx.close()
 browser.close()

(root/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False))
