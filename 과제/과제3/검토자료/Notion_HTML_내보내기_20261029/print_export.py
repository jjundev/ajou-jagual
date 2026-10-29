"""Print the genuine Notion HTML export, preserving its text and bundled images."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import unquote,urlsplit
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parent
SOURCE=next((ROOT/'원본').glob('*.html'))
OUTPUT=ROOT.parents[1]/'보고서_노션_A4가로.pdf'
PRINT=ROOT/'인쇄'
CSS='''
@page { size: A4 landscape; margin: 14mm; }
@media print {
 html { font-size: 13.333px; }
 body { margin: 0 !important; padding: 0; color: rgb(55,53,47); font-size: 10pt; line-height: 1.4; }
 article.page { width: 100%; max-width: none; }
 h1 { font-size: 16pt; break-after: avoid; }
 h2 { font-size: 12pt; break-after: avoid; }
 h3 { font-size: 10.5pt; break-after: avoid; }
 .page-title { font-size: 22pt; }
 .table_of_contents { font-size: 9pt; columns: 2; column-gap: 20pt; }
 .table_of_contents-item { break-inside: avoid; }
 .page-body > .first-chapter, .page-body > .chapter-first-section { break-before: auto; }
 table { width: 100%; table-layout: fixed; }
 .simple-table { font-size: 8.7pt; }
 th,td { min-width: 0 !important; overflow-wrap: anywhere; vertical-align: top; line-height: 1.4; }
 tr { break-inside: avoid; }
 thead { display: table-header-group; }
 .page-body > h1, .page-body > h2 { break-before: page; }
 .page-body > h1 + p + h2 { break-before: auto; }
 h2 + p, .page-body > p:has(+ figure.image), .page-body > p:has(+ pre) { break-after: avoid; }
 .code { break-inside: avoid; }
 .code.language-c { break-inside: auto; }
 figure:has(table) { break-inside: auto; page-break-inside: auto; }
 .code { font-size: 8.2pt; line-height: 1.35; white-space: pre-wrap; overflow-wrap: anywhere; break-inside: auto; }
 figure.image { break-inside: avoid; page-break-inside: avoid; }
 figure.image img { max-width: 100%; max-height: 152mm; width: auto; height: auto; object-fit: contain; }
 figcaption { font-size: 8.5pt; }
 p { orphans: 2; widows: 2; }
}
'''

def main():
 PRINT.mkdir(exist_ok=True)
 raw=SOURCE.read_text()
 # The only source-file change is inserting print CSS into a separate copy.
 rendered=raw.replace('</head>','<style id="a4-landscape-print">'+CSS+'</style></head>')
 copy=SOURCE.parent/'.temporary-print.html'
 assert not copy.exists()
 copy.write_text(rendered)
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch(); page=browser.new_page(viewport={'width':1123,'height':794})
   page.goto(SOURCE.as_uri(),wait_until='networkidle')
   before=page.locator('body').text_content()
   blocks=page.locator('.page-body > *').evaluate_all('(xs)=>xs.map(x=>({id:x.id,tag:x.tagName,cls:x.className,text:x.textContent.slice(0,70)}))')
   (PRINT/'blocks.json').write_text(json.dumps(blocks,ensure_ascii=False,indent=2)+'\n')
   page.goto(copy.as_uri(),wait_until='networkidle');page.emulate_media(media='print');page.evaluate('document.fonts.ready')
   # Scale exported table column widths proportionally without changing cell text.
   page.evaluate('''()=>{for(const t of document.querySelectorAll('table')){let head=t.rows[0];let widths=[...head.cells].map(c=>parseFloat(c.style.width)||c.getBoundingClientRect().width);let sum=widths.reduce((a,b)=>a+b,0);for(const row of t.rows)for(let i=0;i<row.cells.length;i++)row.cells[i].style.width=(widths[i]/sum*100)+'%';}}''')
   page.evaluate('''()=>{let firstChapter=true,firstSection=true;for(const x of document.querySelector('.page-body').children){if(x.tagName==='H1'){if(firstChapter){x.classList.add('first-chapter');firstChapter=false;}firstSection=true;}else if(x.tagName==='H2'&&firstSection){x.classList.add('chapter-first-section');firstSection=false;}}}''')
   assert page.locator('body').text_content()==before
   images=page.locator('img').evaluate_all('(xs)=>xs.map(x=>({src:x.src,loaded:x.complete&&x.naturalWidth>0,width:x.naturalWidth,height:x.naturalHeight}))')
   assert len(images)==5 and all(i['loaded'] for i in images)
   metrics=page.locator('td,th,pre,img').evaluate_all('(xs)=>xs.filter(x=>x.scrollWidth>x.clientWidth+2).map(x=>({id:x.id,tag:x.tagName,scroll:x.scrollWidth,client:x.clientWidth}))')
   assert not metrics,metrics
   page.pdf(path=str(OUTPUT),format='A4',landscape=True,print_background=True,prefer_css_page_size=True,display_header_footer=False)
   # Save an inspectable print copy, with assets resolvable relative to its location.
   html=page.content();html=html.replace('<head>','<head><base href="'+SOURCE.parent.as_uri()+'/">',1)
   (PRINT/'보고서_인쇄용.html').write_text(html)
   browser.close()
  (PRINT/'인쇄.css').write_text(CSS)
  receipt={'source_html':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'output':str(OUTPUT),'pdf_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),'provenance':'Notion native HTML export (default sans mode) -> Chromium A4 landscape print','body_text_unchanged':True,'image_count':len(images),'images':images,'overflow':metrics,'print_headers_footers':False}
  (ROOT/'print.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
  print('Printed genuine Notion HTML; body text unchanged; 5 local images loaded; no horizontal overflow:',OUTPUT)
 finally: copy.unlink()

if __name__=='__main__': main()
