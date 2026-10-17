"""Bio shell behaviour on DS materials; no biology renderer dependency."""
from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
from browser_acceptance import discover_pages

def main(root,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);rows=[];errors=[];requests=[]
 with sync_playwright() as pw:
  browser=pw.chromium.launch();ctx=browser.new_context(offline=True,reduced_motion='reduce')
  ctx.route('**/*',lambda r:(requests.append(r.request.url),r.abort()) if r.request.url.startswith(('http:','https:')) else r.continue_())
  page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
  for file in discover_pages(root):
   for width,height in [(1440,900),(1024,768),(375,812)]:
    for theme in ['light','dark']:
     page.set_viewport_size({'width':width,'height':height});page.goto(file.as_uri());page.wait_for_selector('[data-snapshot]');page.evaluate('document.fonts.ready')
     assert page.locator('.topbar').count()==1,'missing biology topbar'
     if theme=='dark':page.locator('[data-action=theme]').click()
     assert page.evaluate('getComputedStyle(document.querySelector("#app")).backgroundColor')==('rgb(255, 255, 255)' if theme=='light' else 'rgb(23, 23, 28)')
     typography=page.evaluate('''(()=>{const style=s=>{const c=getComputedStyle(document.querySelector(s));return [c.fontFamily,c.fontSize,c.fontWeight,c.lineHeight]};return {body:style('#app'),brand:style('.brand'),section:style('.sec-title'),prose:style('.explanation'),warning:style('.takeaway'),faces:[...document.fonts].filter(f=>f.family==='Pretendard').map(f=>[f.weight,f.status])};})()''')
     assert typography['body']==['Pretendard, system-ui, sans-serif','16px','400','25.6px'],typography
     assert typography['brand'][1:]==['17px','700','27.2px']
     assert typography['section'][1:]==['19px','700','26.6px']
     assert typography['prose'][1:]==['15px','400','24px']
     assert typography['warning'][1:]==['15px','400','25.5px']
     assert sorted(typography['faces'])==[['400','loaded'],['500','loaded'],['600','loaded'],['700','loaded']],typography['faces']
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
     stage=page.locator('.stage').bounding_box();bar=page.locator('.playbar').bounding_box()
     assert stage['x']+stage['width']<=width+1,'stage clipped by min-content width'
     assert page.locator('[data-action=toggle-right]').bounding_box()['x']+page.locator('[data-action=toggle-right]').bounding_box()['width']<=width+1,'header control clipped'
     assert stage['x']<=bar['x'] and bar['x']+bar['width']<=stage['x']+stage['width']+1
     assert bar['y']+bar['height']<=height
     assert page.locator('.memory-pane').is_visible()
     toggle=page.locator('[data-action=toggle-left]');toggle.click()
     if width>=1024:
      assert not page.locator('.panel-left').is_visible();toggle.click()
      handle=page.locator('[data-resize=left]');handle.focus();before=int(handle.get_attribute('aria-valuenow'));page.keyboard.press('ArrowRight');assert int(handle.get_attribute('aria-valuenow'))>before;page.keyboard.press('Home')
      page.locator('[data-action=toggle-right]').click();assert not page.locator('.panel-right').is_visible();page.locator('[data-action=toggle-right]').click()
      # A width chosen with one dock closed must be reconciled when it reopens.
      toggle.click();right_handle=page.locator('[data-resize=right]');right_handle.focus()
      page.keyboard.press('Home')
      for _ in range(30):page.keyboard.press('ArrowLeft')
      toggle.click()
      right_box=page.locator('.panel-right').bounding_box()
      assert right_box['x']+right_box['width']<=width+1,'reopened sibling clips resized dock'
      assert page.locator('.stage').bounding_box()['width']>=319
      right_handle.focus();page.keyboard.press('Home')
      page.set_viewport_size({'width':1440,'height':900});right_handle.focus()
      for _ in range(30):page.keyboard.press('ArrowLeft')
      page.set_viewport_size({'width':375,'height':812});page.set_viewport_size({'width':width,'height':height})
      right_box=page.locator('.panel-right').bounding_box()
      assert right_box['x']+right_box['width']<=width+1,'dock width stale after mobile breakpoint'
      assert page.locator('.stage').bounding_box()['width']>=319
      for side in ['left','right']:page.locator('[data-resize='+side+']').focus();page.keyboard.press('Home')
     else:
      assert page.locator('.panel-left').is_visible();assert not page.locator('.panel-right').is_visible()
      assert page.locator('.panel-left').get_attribute('aria-modal')=='true'
      page.keyboard.press('Shift+Tab');assert page.evaluate('document.activeElement.closest(".panel-left")!==null'),'drawer focus escaped'
      page.keyboard.press('Escape');assert not page.locator('.panel-left').is_visible();assert toggle.evaluate('(e)=>e===document.activeElement')
      page.locator('[data-action=toggle-right]').click();assert page.locator('.panel-right').is_visible();page.locator('.panel-right button[data-action=close-panels]').click()
      toggle.click()
     # Left code and full step list reflect the exact same Trace, including last diagnostic.
     assert page.locator('.panel-left .code').is_visible()
     page.locator('[data-action=step]').last.click();assert page.locator('[data-action=next]').is_disabled()
     selected=page.locator('[data-action=step][aria-pressed=true]');assert selected.count()==1
     selected.scroll_into_view_if_needed();assert selected.is_visible()
     if width<1024:page.keyboard.press('Escape')
     for speed in ['0.5','1','2']:
      page.locator('[data-speed="'+speed+'"]').click();assert page.locator('[data-speed="'+speed+'"]').get_attribute('aria-pressed')=='true'
     # Zoom is independent from execution; arrows use local rather than scaled CSS coordinates.
     page.locator('[data-action=first]').click();page.locator('[data-action=next]').click();step=page.locator('#app').get_attribute('data-index')
     page.locator('[data-action=zoom-in]').click();assert float(page.locator('.memory').get_attribute('data-scale'))>1
     assert page.locator('#app').get_attribute('data-index')==step
     page.locator('[data-action=zoom-reset]').click();assert page.locator('.memory').get_attribute('data-scale')=='1'
     if width<1024:toggle.click()
     page.locator('[data-action=option-addresses]').click();assert not page.locator('.cell-address').first.is_visible()
     page.locator('[data-action=option-addresses]').click();page.locator('[data-action=option-arrows]').click();assert not page.locator('.memory-svg').is_visible();page.locator('[data-action=option-arrows]').click()
     if width<1024:page.keyboard.press('Escape')
     assert page.locator('.memory-pane').is_visible()
     topic=page.evaluate('DSInteractive.scenario.id');page.screenshot(path=str(out/f'{topic}-{width}-{theme}.png'))
     rows.append({'topic':topic,'viewport':[width,height],'theme':theme,'typography':typography,'status':'pass'})
     print(f'{topic} {width} {theme}: bio shell pass',flush=True)
  browser.close()
 assert not errors,errors;assert not requests,requests
 (out/'ui.json').write_text(json.dumps({'status':'pass','results':rows,'console_errors':errors,'external_requests':requests},ensure_ascii=False,indent=2),encoding='utf8')
 print(f'UI combinations: {len(rows)} pass')
if __name__=='__main__':main(*sys.argv[1:3])
