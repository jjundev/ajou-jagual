"""Verify reviewed-byte delivery, final file:// playback and contextual same-tab round trips."""
from pathlib import Path
import hashlib,json,re,sys
from playwright.sync_api import sync_playwright
repo=Path(sys.argv[1]).resolve();report=Path(sys.argv[2]).resolve();folder=repo/'복습노트/0928';files=sorted(folder.glob('인터렉티브_*.html'));assert len(files)==3
rows=[];note=folder/'정리노트_0928_ArrayStructureList.html'
with sync_playwright() as pw:
 b=pw.chromium.launch();context=b.new_context(offline=True);page=context.new_page()
 for file in files:
  pack=folder/'.pack'/('자료_'+file.stem);public, preview = file.read_bytes(), (pack/'preview.html').read_bytes()
  assert re.sub(rb'(data-ds-interactive-font href=")[^"]+', rb'\g<1>', public) == re.sub(rb'(data-ds-interactive-font href=")[^"]+', rb'\g<1>', preview)
  page.goto(file.as_uri());page.wait_for_selector('[data-snapshot="initial"]');page.evaluate('document.fonts.ready');assert page.evaluate("async () => (await document.fonts.load('400 16px Pretendard', '한글')).some(f => f.status === 'loaded')")
  page.locator('[data-action=next]').click();assert page.locator('#app').get_attribute('data-index')=='1';page.locator('[data-action=last]').click();assert page.locator('[data-action=next]').is_disabled()
  rows.append({'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'content_matches_reviewed_preview':True,'final_playback':'pass'})
 page.goto(note.as_uri());links=page.locator('[data-ds-interactive] a');assert links.count()==4
 sections=links.evaluate_all('(es)=>es.map(e=>e.closest("article,section").id)')
 for section in sections:
  # The existing note is paginated; open the actual topic as its table of contents does.
  page.goto(note.as_uri()+'#'+section)
  link=page.locator('#'+section+' [data-ds-interactive] a');assert link.get_attribute('target')=='_self';target=link.get_attribute('href');old=page.url;link.click();page.wait_for_selector('[data-snapshot="initial"]');assert len(context.pages)==1
  page.go_back();page.wait_for_selector('#'+section+' [data-ds-interactive]');assert page.url==old
  rows.append({'link':target,'same_tab_roundtrip':'pass'})
 b.close()
report.parent.mkdir(parents=True,exist_ok=True);report.write_text(json.dumps({'status':'pass','results':rows},ensure_ascii=False,indent=2),encoding='utf8');print('final paths: 3 reviewed materials, 4 same-tab round trips pass')
