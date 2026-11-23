"""Bio shell behaviour on DS materials; no biology renderer dependency."""
from pathlib import Path
import hashlib,json,sys
from playwright.sync_api import sync_playwright
from browser_acceptance import discover_pages

def check_tree_widths(page):
    step = page.locator('#app').get_attribute('data-index')
    def handle(side):
        return page.locator(f'[data-resize={side}]')

    def panel(side):
        return page.locator(f'.panel-{side}')

    def measure(side, width):
        page.wait_for_function(
            """([side, width]) => Math.abs(
                document.querySelector('.panel-' + side).getBoundingClientRect().width - width
            ) < 1""", arg=[side, width])
        assert handle(side).get_attribute('aria-valuenow') == str(width)

    def drag(side, movement):
        bar = handle(side).bounding_box()
        assert bar is not None
        x, y = bar['x'] + bar['width'] / 2, bar['y'] + 100
        page.mouse.move(x, y)
        page.mouse.down()
        page.mouse.move(x + movement, y, steps=4)
        page.mouse.up()

    for side, initial, delta in (('left', 320, 48), ('right', 300, -84)):
        measure(side, initial)
        drag(side, delta)
        measure(side, initial + abs(delta))
    handle('left').focus()
    page.keyboard.press('Shift+ArrowRight')
    measure('left', 432)
    handle('right').focus()
    page.keyboard.press('ArrowLeft')
    measure('right', 400)
    assert page.locator('#app').get_attribute('data-index') == step

    left_toggle = page.locator('[data-action=toggle-left]')
    left_toggle.click()
    panel('left').wait_for(state='hidden')
    left_toggle.click()
    measure('left', 432)
    page.reload()
    measure('left', 432)
    measure('right', 400)

    page.set_viewport_size({'width': 1440, 'height': 900})
    drag('right', -250)
    measure('right', 608)
    page.set_viewport_size({'width': 1280, 'height': 768})
    measure('left', 432)
    measure('right', 448)
    page.wait_for_function(
        "document.querySelector('.stage').getBoundingClientRect().width >= 400")
    page.set_viewport_size({'width': 375, 'height': 812})
    page.wait_for_function("document.querySelector('[data-resize=left]').tabIndex === -1")
    assert handle('left').is_hidden() and handle('right').is_hidden()
    page.set_viewport_size({'width': 1440, 'height': 900})
    measure('left', 432)
    measure('right', 608)

    handle('left').dblclick()
    measure('left', 320)
    measure('right', 608)
    handle('right').focus()
    page.keyboard.press('Home')
    measure('right', 300)
    page.reload()
    measure('left', 320)
    measure('right', 300)


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
     tree=page.evaluate("DSInteractive.scenario.kind==='c-tree'")
     assert page.locator('.topbar').count()==1,'missing biology topbar'
     if page.locator('#interactive-theme').count():page.emulate_media(color_scheme=theme)
     elif theme=='dark':page.locator('[data-action=theme]').click()
     assert page.evaluate('getComputedStyle(document.querySelector("#app")).backgroundColor')==('rgb(255, 255, 255)' if theme=='light' else 'rgb(23, 23, 28)')
     if tree and width<1280:page.locator('[data-action=toggle-left]').click()
     typography=page.evaluate('''(()=>{const style=s=>{const el=document.querySelector(s);if(!el)return null;const c=getComputedStyle(el);return [c.fontFamily,c.fontSize,c.fontWeight,c.lineHeight]};return {body:style('#app'),brand:style('.brand'),section:style('.source-pane .sec-title')||style('.sec-title'),prose:style('.tree-step-explanation')||style('.explanation'),warning:style('.takeaway'),faces:[...document.fonts].filter(f=>f.family==='Pretendard').map(f=>[f.weight,f.status])};})()''')
     assert typography['body']==['Pretendard, system-ui, sans-serif','16px','400','25.6px'],typography
     assert typography['brand'][1:]==(['15px','700','24px'] if tree and width<=720 else ['17px','700','27.2px'])
     assert typography['section'][1:]==(['16px','700','22.4px'] if tree else ['19px','700','26.6px'])
     assert typography['prose'][1:]==(['14px','400','21px'] if tree else ['15px','400','24px'])
     if not tree:assert typography['warning'][1:]==['15px','400','25.5px']
     weights={'400','600','700'} if tree else {'400','500','600','700'}
     assert {(weight,'loaded') for weight in weights} <= set(map(tuple,typography['faces'])),typography['faces']
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth && document.documentElement.scrollHeight<=innerHeight')
     stage=page.locator('.stage').bounding_box();bar=page.locator('.playbar').bounding_box()
     assert stage['x']+stage['width']<=width+1,'stage clipped by min-content width'
     header_action='toggle-right'
     top_control=page.locator('[data-action='+header_action+']').bounding_box()
     assert top_control['x']+top_control['width']<=width+1,'header control clipped'
     assert stage['x']<=bar['x'] and bar['x']+bar['width']<=stage['x']+stage['width']+1
     assert bar['y']+bar['height']<=height
     assert page.locator('.memory-pane').is_visible()
     if tree:
      assert page.get_by_role('heading',name='줄 기록',exact=True).is_visible()
      assert page.locator('.tree-history :is(details, summary)').count()==0
      assert page.locator('.tree-history .step-list').is_visible()
      page.locator('[data-action=step]').last.click()
      assert page.locator('[data-action=next]').is_disabled()
      assert page.locator('[data-action=step][aria-pressed=true]').count()==1
      assert page.locator('.tree-history .step-list').is_visible()
      assert page.locator('.source-pane .code').is_visible()
      for option in ['addresses','arrows']:
       assert page.locator('[data-action=option-'+option+']').is_hidden()
      assert page.locator('[data-action^=zoom-]').count()==0
      if width<1280:page.keyboard.press('Escape')
     else:
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
       page.set_viewport_size({'width':1440,'height':900});page.evaluate('() => new Promise(resolve => requestAnimationFrame(resolve))');right_handle.focus()
       for _ in range(30):page.keyboard.press('ArrowLeft')
       page.set_viewport_size({'width':375,'height':812})
       page.wait_for_function("document.querySelector('[data-resize=left]').tabIndex === -1")
       page.set_viewport_size({'width':width,'height':height})
       page.wait_for_function("document.querySelector('[data-resize=left]').tabIndex === 0")
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
      page.locator('.panel-left .code').wait_for(state='visible')
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
     if tree and width==1440 and theme=='light':
      check_tree_widths(page)
     topic=page.evaluate('DSInteractive.scenario.id');page.screenshot(path=str(out/f'{file.parent.name}-{topic}-{width}-{theme}.png'))
     rows.append({'topic':topic,'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'viewport':[width,height],'theme':theme,'typography':typography,'status':'pass'})
     print(f'{topic} {width} {theme}: bio shell pass',flush=True)
  browser.close()
 assert not errors,errors;assert not requests,requests
 (out/'ui.json').write_text(json.dumps({'status':'pass','results':rows,'console_errors':errors,'external_requests':requests},ensure_ascii=False,indent=2),encoding='utf8')
 print(f'UI combinations: {len(rows)} pass')
if __name__=='__main__':main(*sys.argv[1:3])
