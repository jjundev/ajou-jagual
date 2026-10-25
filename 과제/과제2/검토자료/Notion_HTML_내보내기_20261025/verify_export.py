"""Validate the export-derived PDF against the original Notion HTML and its assets."""
from pathlib import Path
import json,re,hashlib,zipfile,unicodedata
from urllib.parse import unquote,urlsplit
from playwright.sync_api import sync_playwright
import fitz
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent
HTML=next((ROOT/'원본').glob('*.html'))
PDF=ROOT.parents[1]/'보고서_노션_A4가로.pdf'
def norm(s): return re.sub(r'\s+','',unicodedata.normalize('NFKC',s).replace('\u200b',''))

def main():
 with sync_playwright() as p:
  b=p.chromium.launch();page=b.new_page();page.goto(HTML.as_uri(),wait_until='networkidle')
  title=page.locator('.page-title').inner_text()
  source_rows=page.locator('table').evaluate_all('''ts=>ts.filter(t=>t.rows[0].cells[0].textContent==='소스코드').flatMap(t=>[...t.rows].slice(1).map(r=>({id:r.id,code:r.cells[0].innerText,analysis:r.cells[1].innerText})))''')
  paragraphs=page.locator('.page-body > p, .page-body > h1, .page-body > h2, .page-body > pre').all_text_contents()
  images=page.locator('img').evaluate_all('(xs)=>xs.map(x=>x.src)')
  b.close()
 d=fitz.open(PDF);texts=[p.get_text() for p in d];full=norm(''.join(texts));normalized=[norm(t) for t in texts]
 assert '404b06d263bc81cdb588d36e59ca3a77' in HTML.name
 assert '프로세스 메모리 관리' in title
 assert len(images)==6 and len(source_rows)==20
 for content in paragraphs:
  if norm(content):assert norm(content) in full,content[:90]
 matches=[]
 for row in source_rows:
  pages=[i+1 for i,t in enumerate(normalized) if norm(row['code']) in t and norm(row['analysis']) in t]
  assert pages, 'Code/analysis row split, missing or altered: '+row['id']
  matches.append({'id':row['id'],'pages':pages})
 for token in ['하네스','고정 시드','Sanitizer','32건','관찰한 종료 코드','캡처용 빌드','래퍼']: assert token not in ''.join(texts),token
 # Original extracted HTML and image bytes remain identical to the ZIP members.
 z=next(ROOT.glob('*.zip'))
 with zipfile.ZipFile(z) as f:
  for member in f.infolist():assert (ROOT/'원본'/member.filename).read_bytes()==f.read(member)
 for url in images:assert Path(unquote(urlsplit(url).path)).is_file()
 bounds=[]
 for i,p in enumerate(d):
  assert abs(p.rect.width-841.89)<1 and abs(p.rect.height-595.28)<1
  for block in p.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     x0,y0,x1,y1=span['bbox']
     if x0<0 or y0<0 or x1>p.rect.width+1 or y1>p.rect.height+1:bounds.append((i+1,span['text']))
 assert not bounds,bounds
 out=ROOT/'PDF_검토';out.mkdir(exist_ok=True)
 thumbs=[]
 for i,p in enumerate(d):
  p.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(out/f'page-{i+1:02}.png')
  im=Image.open(out/f'page-{i+1:02}.png');im.thumbnail((400,284));thumb=Image.new('RGB',(420,312),'#ddd');thumb.paste(im,((420-im.width)//2,20));ImageDraw.Draw(thumb).text((8,3),str(i+1),fill='black');thumbs.append(thumb)
 for start in range(0,len(thumbs),12):
  batch=thumbs[start:start+12];sheet=Image.new('RGB',(1260,312*((len(batch)+2)//3)),'white')
  for i,t in enumerate(batch):sheet.paste(t,((i%3)*420,(i//3)*312))
  sheet.save(out/f'contact-{start//12+1}.png')
 result={'pdf':str(PDF),'pdf_sha256':hashlib.sha256(PDF.read_bytes()).hexdigest(),'pages':len(d),'a4_landscape_all_pages':True,'original_export_matches_zip':True,'code_analysis_rows':matches,'all_paragraphs_headings_and_code_extract':True,'images':len(images),'pdf_image_count':sum(len(p.get_images()) for p in d),'outside_bounds':bounds,'visual_review':'pending'}
 (ROOT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print('Verified',len(d),'A4 landscape pages;',len(matches),'paired code/analysis rows; all paragraphs and code extracted; original ZIP assets unchanged; 6 images.')
 print('Page headings:',[(i+1,t[:32].replace('\n',' / ')) for i,t in enumerate(texts)])

if __name__=='__main__':main()
