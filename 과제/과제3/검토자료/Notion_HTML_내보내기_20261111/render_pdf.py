"""Print the genuine, current Notion export with presentation-only adjustments."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
HTML = next((ROOT / "원본").glob("*.html"))
OUTPUT = ROOT / "보고서_노션_A4가로_후보.pdf"
PRINT = ROOT / "인쇄"
CSS = r"""
@page { size: A4 landscape; margin: 14mm; }
@media print {
 html { font-size: 13.333px; }
 body { margin: 0 !important; padding: 0 !important; max-width: none !important;
        color: rgb(55,53,47); background: white; font-size: 10pt; line-height: 1.4; }
 article.page { width: 100%; max-width: none; }
 .page-title { font-size: 22pt; line-height: 1.2; }
 h1 { font-size: 16pt; break-after: avoid; }
 h2 { font-size: 12pt; break-after: avoid; }
 h3 { font-size: 10.5pt; break-after: avoid; }
 .page-body > h1:not(.first-chapter) { break-before: page; }
 .page-body > h2:not(.chapter-first-section) { break-before: page; }
 .table_of_contents { font-size: 9pt; columns: 2; column-gap: 20pt; }
 .table_of_contents-item { break-inside: avoid; }
 table { width: 100%; table-layout: fixed; }
 .simple-table { font-size: 9pt; }
 th, td { min-width: 0 !important; overflow-wrap: anywhere; vertical-align: top; line-height: 1.4; }
 tr { break-inside: avoid; page-break-inside: avoid; }
 thead { display: table-header-group; break-after: avoid; }
 thead tr { break-after: avoid; }
 tbody tr:first-child { break-before: avoid; }
 figure:has(table) { break-inside: auto; page-break-inside: auto; }
 h2 + p, p:has(+ pre), p:has(+ figure.image), p:has(+ figure:has(table)) { break-after: avoid; }
 .code { font-size: 8.7pt; line-height: 1.35; white-space: pre-wrap;
         overflow-wrap: anywhere; break-inside: avoid; }
 .code[data-notion-code-syntax="c"] { break-inside: auto; }
 figure.image { break-inside: avoid; page-break-inside: avoid; }
 .print-image-group { break-inside: avoid; page-break-inside: avoid; }
 figure.image img { max-width: 100%; max-height: 150mm; width: 100%; height: auto; object-fit: contain; }
 figcaption { font-size: 8.7pt; line-height: 1.4; }
 p { orphans: 2; widows: 2; }
 p:empty, p.print-empty { display: none; }
}
"""


def main():
    PRINT.mkdir(exist_ok=True)
    raw = HTML.read_bytes()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1016, "height": 688})
        page.goto(HTML.as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        before = page.locator("body").text_content()
        code_before = page.locator("pre").all_text_contents()
        links_before = page.locator("a").evaluate_all("xs=>xs.map(x=>x.getAttribute('href'))")
        snapshot = page.locator(".page-body").evaluate("""body=>({
          title:document.querySelector('.page-title').textContent,
          headings:[...body.querySelectorAll(':scope > h1,:scope > h2,:scope > h3')].map(x=>({id:x.id,text:x.textContent})),
          paragraphs:[...body.querySelectorAll(':scope > p,:scope > pre,:scope > figure.image figcaption')].map(x=>({id:x.id,tag:x.tagName,text:x.textContent})),
          tables:[...body.querySelectorAll('table')].map(t=>({id:t.id,rows:[...t.rows].map(r=>({id:r.id,cells:[...r.cells].map(c=>c.textContent)}))})),
          images:[...body.querySelectorAll('img')].map(x=>({src:x.src,loaded:x.complete&&x.naturalWidth>0,w:x.naturalWidth,h:x.naturalHeight})),
          font:getComputedStyle(document.querySelector('article')).fontFamily
        })""")
        assert all(i["loaded"] for i in snapshot["images"])
        assert all(s in before for s in ["퀀텀 소진으로 중단되지 않는다", "current도 모든 필드가 0이어서", "T3·T4 종료 후"])
        page.add_style_tag(content=CSS)
        page.emulate_media(media="print")
        page.evaluate("""()=>{
          for(const t of document.querySelectorAll('table')){
            const widths=[...t.rows[0].cells].map(c=>parseFloat(c.style.width)||c.getBoundingClientRect().width);
            const sum=widths.reduce((a,b)=>a+b,0);
            for(const row of t.rows)for(let i=0;i<row.cells.length;i++)row.cells[i].style.width=(widths[i]/sum*100)+'%';
          }
          document.querySelector('.page-body > h1')?.classList.add('first-chapter');
          let firstSection=true;
          for(const x of document.querySelector('.page-body').children){
            if(x.tagName==='H1')firstSection=true;
            else if(x.tagName==='H2'&&firstSection){x.classList.add('chapter-first-section');firstSection=false;}
            if(x.tagName==='P'&&!x.textContent.trim())x.classList.add('print-empty');
          }
          for(const figure of document.querySelectorAll('figure.image')){
            const label=figure.previousElementSibling;
            if(label?.tagName==='P'&&label.textContent.trim()==='실제 터미널 실행 화면'){
              const range=document.createRange();range.setStartBefore(label);range.setEndAfter(figure);
              const group=document.createElement('div');group.className='print-image-group';range.surroundContents(group);
            }
          }
        }""")
        page.evaluate("document.fonts.ready")
        assert page.locator("body").text_content() == before
        assert page.locator("pre").all_text_contents() == code_before
        assert page.locator("a").evaluate_all("xs=>xs.map(x=>x.getAttribute('href'))") == links_before
        assert page.locator("article").evaluate("x=>getComputedStyle(x).fontFamily") == snapshot["font"]
        overflow = page.locator("td,th,pre,img").evaluate_all("""xs=>xs.filter(x=>x.scrollWidth>x.clientWidth+2)
          .map(x=>({tag:x.tagName,id:x.id,scroll:x.scrollWidth,client:x.clientWidth}))""")
        assert not overflow, overflow
        row_heights = page.locator("tr").evaluate_all("xs=>xs.map(x=>({id:x.id,height:x.getBoundingClientRect().height}))")
        assert max(r["height"] for r in row_heights) < 688, "A paired row is taller than a page"
        page.pdf(path=str(OUTPUT), format="A4", landscape=True, prefer_css_page_size=True,
                 print_background=True, display_header_footer=False)
        rendered = page.content().replace("<head>", '<head><base href="'+HTML.as_uri()+'">', 1)
        (PRINT / "보고서_인쇄용.html").write_text(rendered)
        (PRINT / "인쇄.css").write_text(CSS)
        (ROOT / "html-content.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2)+"\n")
        receipt = {"source_html": str(HTML), "source_sha256": hashlib.sha256(raw).hexdigest(),
                   "pdf": str(OUTPUT), "pdf_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
                   "renderer": "Playwright Chromium", "format": "A4 landscape", "margins_mm": 14,
                   "headers_and_footers": False, "text_code_indentation_links_and_font_unchanged": True,
                   "images": len(snapshot["images"]), "overflow": overflow, "maximum_paired_row_height_px": max(r["height"] for r in row_heights)}
        (ROOT / "print.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n")
        browser.close()
    assert HTML.read_bytes() == raw
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
