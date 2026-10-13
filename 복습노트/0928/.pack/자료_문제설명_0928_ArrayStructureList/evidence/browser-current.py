from pathlib import Path
import sys,json,mimetypes
from urllib.parse import unquote,urlparse
from playwright.sync_api import sync_playwright
repo=Path(sys.argv[1]).resolve();base=Path('/private/tmp/ds-review-pdf-20261013/explanations-v2')
sys.path.insert(0,str(repo/'.agents/skills/ds-problem-explain/scripts'))
from mpe_cli import load_run,load_artifacts
results=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(channel='chrome')
 for run in sorted(p for p in base.iterdir() if (p/'run.json').exists()):
  item=load_run(run)[0];artifact=load_artifacts(item);stage=artifact.html.parent;source=item['pack'].path;errors=[];rows=[]
  def route(request):
   url=urlparse(request.request.url)
   if url.netloc!='ds.local':errors.append('External resource: '+request.request.url);request.abort();return
   rel=unquote(url.path).lstrip('/');candidate=stage/rel
   if not candidate.is_file():candidate=source.parent/rel
   if not candidate.resolve().is_relative_to(stage.resolve()) and not candidate.resolve().is_relative_to(source.parent.resolve()):request.abort();return
   if candidate.is_file():request.fulfill(body=candidate.read_bytes(),content_type=mimetypes.guess_type(candidate)[0] or 'application/octet-stream')
   else:errors.append('Missing resource: '+rel);request.abort()
  for width,height in [(1280,900),(375,812)]:
   page=browser.new_page(viewport={'width':width,'height':height});page.route('**/*',route)
   page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   page.goto('http://ds.local/'+artifact.html.name);page.evaluate('document.fonts.ready');page.wait_for_timeout(100)
   for theme in ('light','dark'):
    page.evaluate('(theme)=>{document.documentElement.dataset.theme=theme}',theme)
    for problem in item['pack'].problems:
     page.evaluate('(id)=>{location.hash=id}',problem.id);page.wait_for_function('(id)=>document.getElementById(id).classList.contains("is-current")',arg=problem.id);page.wait_for_timeout(70)
     value=page.evaluate('''() => ({mathErrors:document.querySelectorAll('.katex-error').length,external:[...document.querySelectorAll('script[src],link[rel="stylesheet"]')].filter(n=>new URL(n.src||n.href).hostname!=='ds.local').length,overflow:document.documentElement.scrollWidth>innerWidth+1,images:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,sections:[...document.querySelectorAll('.is-current [data-explanation]')].map(n=>n.dataset.explanation),active:document.querySelector('.is-current').id,summary:document.querySelectorAll('#panel-right .sum:not([hidden])').length})''')
     if value['mathErrors'] or value['external'] or value['overflow'] or value['images'] or len(value['sections'])!=7 or value['summary']!=1:errors.append(f'{width}/{theme}/{problem.id}: {value}')
     shots=item['folder']/'browser-current'/f'{width}-{theme}';shots.mkdir(parents=True,exist_ok=True)
     # Full card capture ignores outer scroller clipping; the viewport capture shows real navigation/summary.
     page.screenshot(path=str(shots/f'{problem.id}-viewport.png'))
     page.locator('#'+problem.id).screenshot(path=str(shots/f'{problem.id}-card.png'))
     visited=[]
     for section in value['sections']:
      node=page.locator('#'+problem.id+' [data-explanation="'+section+'"]')
      node.evaluate('(n)=>n.scrollIntoView({block:"start"})');page.wait_for_timeout(20)
      visited.append(section)
      if section=='verify':page.screenshot(path=str(shots/f'{problem.id}-verify.png'))
     value['visited_sections']=visited
     rows.append({'width':width,'height':height,'theme':theme,'id':problem.id,**value})
    # Exercise next/previous and TOC state in each variant.
    page.evaluate('(id)=>{location.hash=id}',item['pack'].problems[0].id);page.wait_for_timeout(50)
    page.locator('#pager-next').click();page.wait_for_timeout(80)
    if len(item['pack'].problems)>1 and page.locator('.is-current').get_attribute('id')!=item['pack'].problems[1].id:errors.append('next navigation failed')
    page.locator('#pager-prev').click();page.wait_for_timeout(80)
    if page.locator('.is-current').get_attribute('id')!=item['pack'].problems[0].id:errors.append('previous navigation failed')
   page.close()
  report={'range':run.name,'status':'fail' if errors else 'pass','errors':errors,'views':rows}
  (item['folder']/'evidence/browser-current.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));results.append(report);print(run.name,report['status'],len(rows),errors[:3],flush=True)
 browser.close()
(base/'browser-current-summary.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
assert all(not r['errors'] for r in results)
