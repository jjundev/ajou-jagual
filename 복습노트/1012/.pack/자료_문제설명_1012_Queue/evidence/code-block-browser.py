import json,sys,threading,http.server,functools
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path.cwd().resolve();sys.path.insert(0,str(root/'.agents/skills/ds-problem-explain/scripts'))
from mpe_cli import load_run,load_artifacts
report=json.loads((root/'docs/verify/2026-10-13-ds-code-blocks.json').read_text())
class Handler(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}/'
with sync_playwright() as pw:
 browser=pw.chromium.launch()
 for record in report['packs']:
  item=load_run(record['run'])[0];art=load_artifacts(item);dest=item['folder']/'evidence/code-block-browser';dest.mkdir(exist_ok=True)
  results=[]
  for width,height in [(1280,900),(375,812)]:
   for theme in ['light','dark']:
    page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme)
    logs=[];failed=[];external=[]
    page.on('pageerror',lambda e:logs.append(str(e)))
    page.on('console',lambda e:logs.append(e.text) if e.type=='error' else None)
    page.on('requestfailed',lambda r:failed.append(r.url))
    page.on('response',lambda r:failed.append(str(r.status)+' '+r.url) if r.status>=400 else None)
    page.on('request',lambda r:external.append(r.url) if not r.url.startswith(origin) else None)
    page.goto(origin+art.html.relative_to(root).as_posix(),wait_until='networkidle')
    for i,pid in enumerate(record['problem_ids']):
     page.locator('#pager-next').click();page.wait_for_timeout(40)
     assert page.locator('#'+pid).is_visible(),pid
     assert page.locator('#'+pid+' [data-explanation]').count()==7
     assert page.locator('.katex-error').count()==0
     assert page.locator('#'+pid+' img').evaluate_all('(es)=>es.every(e=>e.complete&&e.naturalWidth>0)')
     assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(record['date'],pid,width,theme,'overflow')
     metrics=page.locator('#'+pid+' pre').evaluate_all('''es=>es.map(e=>{let s=getComputedStyle(e);return {client:e.clientWidth,scroll:e.scrollWidth,padding:s.padding,border:s.borderTopWidth,size:s.fontSize,line:s.lineHeight,whiteSpace:s.whiteSpace,background:s.backgroundColor,color:s.color,codeChildren:e.querySelectorAll(':scope > code').length,codePadding:getComputedStyle(e.querySelector('code')).padding}})''')
     assert all(m['padding']=='16px' and m['border']=='1px' and m['size']=='14px' and m['whiteSpace']=='pre' and m['codePadding']=='0px' for m in metrics),(pid,metrics)
     if i==0 or (metrics and width==375 and theme=='dark'):
      page.screenshot(path=str(dest/f'{width}-{theme}-{pid}.png'),full_page=True)
     results.append({'problem':pid,'viewport':[width,height],'theme':theme,'document_overflow':False,'code_blocks':metrics})
    page.locator('#pager-prev').click();assert page.locator('#'+record['problem_ids'][-2]).is_visible()
    page.locator('#pager-next').click();assert page.locator('#'+record['problem_ids'][-1]).is_visible()
    if width<800 or not page.locator('#panel-right').is_visible():page.locator('#toggle-right').click()
    page.wait_for_timeout(250);assert page.locator('#panel-right').is_visible();assert page.locator('#panel-right .sum').count()>0 or page.locator('#panel-right').inner_text().strip()
    if width<800:page.locator('#panel-right [data-panel-close]').click()
    page.locator('#toggle-left').click();page.wait_for_timeout(250)
    if width>=800:page.locator('#toggle-left').click()
    page.locator('#panel-left a[href="#'+record['problem_ids'][0]+'"]').click();page.wait_for_timeout(150);assert page.locator('#'+record['problem_ids'][0]).is_visible()
    page.locator('#theme-toggle').click();page.locator('#theme-toggle').click()
    assert not logs and not failed and not external,(logs,failed,external)
    page.close()
  (dest/'results.json').write_text(json.dumps({'date':record['date'],'questions':results,'console_errors':[],'resource_errors':[],'external_requests':[],'navigation_summary_theme':'pass'},ensure_ascii=False,indent=2))
  print(record['date'],len(results),'question-viewports PASS',flush=True)
 browser.close()
server.shutdown()
