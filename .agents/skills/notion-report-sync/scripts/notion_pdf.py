"""Print an untouched local Notion HTML export and verify the candidate PDF.

Printing does not establish export origin or freshness against Notion. Use the
skill's export procedure and shared ledger for those separately observed checks.
"""
from __future__ import annotations

import argparse
import base64
import copy
import html as html_module
import io
import json
from pathlib import Path
import unicodedata
from urllib.parse import unquote, urlsplit
import urllib.request

from PIL import Image, ImageDraw
from report_state import Ledger, STAGES, atomic_json, digest, fingerprint

DEFAULTS = {'margin_mm': 14, 'body_pt': 10, 'table_pt': 9, 'code_pt': 9,
            'section_breaks': [], 'paired_table_selector': None}


def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFC', text)
                   if not c.isspace() and c != '\u200b')


def check_text(units, pages, geometry=None, alternatives=()):
    streams = [(norm('\n'.join(pages)), geometry)] + [(norm('\n'.join(p)), g) for p, g in alternatives]
    full = streams[0][0]
    cursor = 0
    previous_position = None
    if geometry is not None and len(geometry) != len(full):
        raise ValueError('Unsupported PDF Unicode geometry; review extraction separately')
    for unit in units:
        text = norm(unit['text'])
        if not text:
            continue
        if geometry is None:
            start = full.find(text, cursor)
        else:
            # Paint order differs from reading order for fragmented native TOCs.
            # Match whole units in the text stream, then order their start glyphs
            # geometrically. Table source/analysis cells stay whole in that stream.
            candidates = []
            for compact, points in streams:
                if len(compact) != len(points):
                    raise ValueError('Unsupported PDF Unicode geometry')
                position = compact.find(text)
                while position >= 0:
                    point = points[position]
                    if previous_position is None or point > previous_position:
                        candidates.append((point, position))
                    position = compact.find(text, position + 1)
            if candidates:
                previous_position, start = min(candidates)
            else:
                start = -1
        if start < 0:
            raise ValueError('Missing, reordered, or repeated text lost: ' + unit['text'][:100])
        cursor = start + len(text)


def text_geometry(pdf, sort_lines=False):
    texts, geometry = [], []
    for index, page in enumerate(pdf):
        lines = []
        pdf_lines = [line for block in page.get_text('rawdict')['blocks'] for line in block.get('lines', [])]
        if sort_lines:
            pdf_lines.sort(key=lambda line: (round(line['bbox'][1] / 6) * 6, line['bbox'][0]))
        for line in pdf_lines:
            text = ''
            for span in line['spans']:
                for char in span['chars']:
                    text += char['c']
                    geometry.extend([(index, round(char['bbox'][1] / 6) * 6, char['bbox'][0])] * len(norm(char['c'])))
            lines.append(text)
        texts.append('\n'.join(lines))
    return texts, geometry


def check_indentation(codes, pdf_text):
    raw = unicodedata.normalize('NFC', pdf_text).replace('\u00a0', ' ')
    positions = [i for i, c in enumerate(raw) if not c.isspace() and c != '\u200b']
    compact = ''.join(raw[i] for i in positions)
    cursor = 0
    for code in codes:
        code = unicodedata.normalize('NFC', code).replace('\u00a0', ' ')
        for line in code.splitlines():
            text = norm(line)
            if not text:
                continue
            start = compact.find(text, cursor)
            while start >= 0:
                char_index = positions[start]
                line_start = raw.rfind('\n', 0, char_index) + 1
                observed = raw[line_start:char_index]
                if not observed.strip():
                    break
                start = compact.find(text, start + 1)
            if start < 0:
                raise ValueError('Code line lost before indentation check')
            expected_indent = line[:len(line) - len(line.lstrip())].expandtabs(8)
            if observed != expected_indent:
                raise ValueError('Code indentation differs: ' + repr(line[:100]))
            cursor = start + len(text)


def asset_bytes(src):
    parts = urlsplit(src)
    if parts.scheme == 'data':
        header, data = src.split(',', 1)
        return base64.b64decode(data) if ';base64' in header else unquote(data).encode()
    if parts.scheme != 'file':
        raise ValueError('Resolve required export assets locally before printing: ' + parts.scheme)
    return Path(unquote(parts.path)).read_bytes()


def pixel_key(data):
    with Image.open(io.BytesIO(data)) as image:
        if getattr(image, 'is_animated', False):
            raise ValueError('Animated image requires a separately reviewed print representation')
        rgba = image.convert('RGBA')
        return (rgba.size, digest(rgba.tobytes()))


def settings_for(config):
    settings = copy.deepcopy(DEFAULTS)
    if config:
        unknown = set(config) - set(settings)
        if unknown:
            raise ValueError('Unknown print settings: ' + ', '.join(sorted(unknown)))
        settings.update(config)
    for key in ('margin_mm', 'body_pt', 'table_pt', 'code_pt'):
        if type(settings[key]) not in (int, float) or not 5 <= settings[key] <= (35 if key == 'margin_mm' else 24):
            raise ValueError('Unsupported print setting: ' + key)
    if not isinstance(settings['section_breaks'], list) or any(s not in ('h1', 'h2', 'h3') for s in settings['section_breaks']):
        raise ValueError('section_breaks must be a list of heading tags')
    if settings['paired_table_selector'] is not None and not isinstance(settings['paired_table_selector'], str):
        raise ValueError('paired_table_selector must be a CSS selector')
    return {**settings, 'landscape': True}


def fetch_remote_asset(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        data = response.read(20_000_001)
        mime = response.headers.get_content_type()
    if len(data) > 20_000_000:
        raise ValueError('External export resource exceeds supported size')
    return data, mime


def print_html(source, output, evidence, *, config=None, config_path=None, state_path=None,
               remote_loader=fetch_remote_asset):
    from playwright.sync_api import sync_playwright
    source, output, evidence = (Path(p).resolve() for p in (source, output, evidence))
    if output.exists() or evidence.exists():
        raise FileExistsError('Use a distinct candidate and a new evidence directory')
    if (output == source or source.parent in output.parents or
            evidence == source.parent or source.parent in evidence.parents):
        raise ValueError('Print output must be separate from the source export')
    settings = settings_for(config)
    state_file = Path(state_path).resolve() if state_path else evidence / 'state.json'
    ledger = Ledger(state_file)
    prior = ledger.refresh() if state_file.exists() else {}
    expected_parents = {s: prior[s]['version'] if s in prior else None for s in STAGES[:STAGES.index('print')]}
    margin = settings['margin_mm']
    width, height = ((297 - margin * 2) * 96 / 25.4, (210 - margin * 2) * 96 / 25.4)
    css = f'''
    @page {{size: A4 landscape; margin: {margin}mm;}}
    @media print {{
      body {{margin:0!important;padding:0!important;max-width:none!important;
             font-size:{settings['body_pt']}pt;line-height:1.4;}}
      article.page {{width:100%;max-width:none;}}
      table, table.simple-table {{width:100%;table-layout:fixed;font-size:{settings['table_pt']}pt;}}
      td,th {{min-width:0!important;overflow-wrap:anywhere;vertical-align:top;}}
      tr {{break-inside:avoid;}} thead {{display:table-header-group;break-after:avoid;}}
      tbody tr:first-child {{break-before:avoid;}}
      figure:has(table) {{break-inside:auto;}}
      h1,h2,h3,h4,h5,h6 {{break-after:avoid;}}
      p:has(+table),p:has(+figure:has(table)),p:has(+pre),p:has(+figure.image) {{break-after:avoid;}}
      .table_of_contents {{font-size:.9em;}}
      .table_of_contents-item {{font-size:inherit;padding-block:.12em;break-inside:avoid;}}
      pre,.code {{font-size:{settings['code_pt']}pt;white-space:pre-wrap;overflow-wrap:anywhere;}}
      pre.print-keep,.print-image-group,.print-code-group,.print-table-group,figure.image {{break-inside:avoid;}}
      pre.print-flow {{break-inside:auto;}}
      figure.image img {{max-width:100%;max-height:{height * .76}px;width:auto;height:auto;object-fit:contain;}}
      p {{orphans:2;widows:2;}} p.print-empty {{display:none;}}
      .print-break {{break-before:page;}}
    }}'''
    source_before = fingerprint(source)
    dependencies = {str(source): source_before}
    if config_path:
        path = Path(config_path).resolve()
        if json.loads(path.read_text()) != (config or {}):
            raise ValueError('Print configuration changed before rendering')
        dependencies[str(path)] = fingerprint(path)
    blocked = []
    remote_resources = []
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        try:
            page = browser.new_page(viewport={'width': int(width), 'height': int(height)})
            page.set_default_timeout(15000)
            def route(request_route):
                url = request_route.request.url
                if urlsplit(url).scheme in ('http', 'https'):
                    if request_route.request.resource_type in ('stylesheet', 'font', 'script'):
                        try:
                            data, mime = remote_loader(url)
                            if request_route.request.resource_type == 'stylesheet' and mime != 'text/css':
                                raise ValueError('Expected a stylesheet')
                            remote_resources.append({'url': url, 'mime': mime, 'data': data})
                            request_route.fulfill(status=200, body=data, content_type=mime,
                                                  headers={'access-control-allow-origin': '*'})
                        except Exception:
                            blocked.append(urlsplit(url)._replace(query='', fragment='').geturl())
                            request_route.abort()
                    else:
                        blocked.append(urlsplit(url)._replace(query='', fragment='').geturl())
                        request_route.abort()
                else:
                    request_route.continue_()
            page.route('**/*', route)
            def requested(request):
                parts = urlsplit(request.url)
                if parts.scheme == 'file':
                    path = Path(unquote(parts.path))
                    if path.is_file() and str(path.resolve()) not in dependencies:
                        dependencies[str(path.resolve())] = fingerprint(path)
            page.on('requestfinished', requested)
            def request_failed(request):
                if request.resource_type in ('stylesheet', 'font', 'script', 'image'):
                    blocked.append(urlsplit(request.url)._replace(query='', fragment='').geturl())
            page.on('requestfailed', request_failed)
            page.goto(source.as_uri(), wait_until='networkidle')
            page.wait_for_function("document.fonts.status === 'loaded'")
            page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
            if blocked:
                raise ValueError('External export assets must be resolved locally: ' + repr(blocked))
            before = page.locator('body').text_content()
            links = page.locator('a').evaluate_all("xs=>xs.map(x=>x.getAttribute('href'))")
            fonts = page.locator('article.page,body').evaluate_all('xs=>xs.map(x=>getComputedStyle(x).fontFamily)')
            content = page.evaluate('''settings=>{
              const selector='h1,h2,h3,h4,h5,h6,p,pre,td,th,figcaption,li,blockquote,summary,.table_of_contents-item';
              const units=[...document.querySelectorAll(selector)].filter(x=>!x.parentElement.closest(selector));
              const ordered=units.map(x=>({node:x,tag:x.tagName,id:x.id,text:x.innerText}));
              const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
              while(walker.nextNode()){
                const node=walker.currentNode,p=node.parentElement;
                if(node.textContent.trim()&&!p.closest('script,style,noscript')&&!p.closest(selector))
                  ordered.push({node,tag:p.tagName,id:p.id,text:node.textContent});
              }
              ordered.sort((a,b)=>a.node.compareDocumentPosition(b.node)&Node.DOCUMENT_POSITION_FOLLOWING?-1:1);
              const tables=[...document.querySelectorAll('table')].filter(t=>settings.paired_table_selector ?
                t.matches(settings.paired_table_selector) : /^(소스\\s*코드|source\\s*code)$/i.test(t.rows[0]?.cells[0]?.innerText.trim()||''));
              const rows=tables.flatMap(t=>[...t.rows].slice(1).map(r=>({id:r.id,cells:[...r.cells].map(c=>c.innerText)})));
              const codeNodes=[...document.querySelectorAll('pre'),...tables.flatMap(t=>[...t.rows].slice(1).map(r=>r.cells[0]))];
              codeNodes.sort((a,b)=>a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING?-1:1);
              return {units:ordered.map(({node,...item})=>item),rows,
                codes:codeNodes.map(x=>x.innerText),images:[...document.images].map(x=>({src:x.src,
                  width:x.naturalWidth,height:x.naturalHeight,label:(()=>{let p=x.closest('figure')?.previousElementSibling;
                    while(p?.tagName==='P'&&!p.textContent.trim())p=p.previousElementSibling;
                    return p?.tagName==='P'&&p.textContent.trim().length<120?p.innerText.trim():null;})()}))};
            }''', settings)
            for image in content['images']:
                data = asset_bytes(image['src'])
                if not image['width'] or not image['height']:
                    raise ValueError('Unloaded image')
                image['sha256'] = digest(data)
                image['pixel_key'] = pixel_key(data)
                if urlsplit(image['src']).scheme == 'file':
                    path = Path(unquote(urlsplit(image['src']).path))
                    dependencies[str(path.resolve())] = fingerprint(path)
            page.add_style_tag(content=css)
            page.emulate_media(media='print')
            layout = page.evaluate('''({settings,height})=>{
              const tooTall=[];
              for(const t of document.querySelectorAll('table')){
                if(!t.rows.length)continue;
                const explicit=[...t.rows[0].cells].map(c=>parseFloat(c.style.width)||0);
                const hasMixed=explicit.some(w=>w>0)&&explicit.some(w=>!w);
                const widths=[...t.rows[0].cells].map((c,i)=>explicit[i]||(hasMixed?Math.max(350,c.getBoundingClientRect().width):c.getBoundingClientRect().width));
                const total=widths.reduce((a,b)=>a+b,0);
                if(total>0)for(const row of t.rows)for(let i=0;i<row.cells.length;i++)
                  if(widths[i])row.cells[i].style.width=100*widths[i]/total+'%';
              }
              for(const p of document.querySelectorAll('p'))if(!p.textContent.trim())p.classList.add('print-empty');
              for(const tag of settings.section_breaks){
                for(const h of [...document.querySelectorAll('.page-body > '+tag)].slice(1))h.classList.add('print-break');
              }
              for(const table of document.querySelectorAll('table')){
                const target=table.closest('figure')||table;
                let start=target.previousElementSibling;
                while(start?.tagName==='P'&&start.textContent.trim().length<120)start=start.previousElementSibling;
                if(!start||!/^H[1-6]$/.test(start.tagName)||start.parentElement!==target.parentElement)continue;
                const first=table.tBodies[0]?.rows[0];
                if(first && table.getBoundingClientRect().top-start.getBoundingClientRect().top+
                   first.getBoundingClientRect().height+(table.tHead?.getBoundingClientRect().height||0)>height-8)
                  tooTall.push(start.textContent.trim()+' + first row');
                if(target.getBoundingClientRect().bottom-start.getBoundingClientRect().top<height-8){
                  const range=document.createRange();range.setStartBefore(start);range.setEndAfter(target);
                  const group=document.createElement('div');group.className='print-table-group';
                  if(start.classList.contains('print-break')){group.classList.add('print-break');start.classList.remove('print-break');}
                  range.surroundContents(group);
                }else{
                  // Chromium can orphan the heading despite a chain of break-after
                  // rules around a fragmented table. Start that large table's section
                  // on a fresh page; paired rows still determine legal table breaks.
                  let breakStart=start;
                  if(!settings.section_breaks.includes(start.tagName.toLowerCase())){
                    let parent=start.previousElementSibling;
                    while(parent?.tagName==='P')parent=parent.previousElementSibling;
                    if(parent && /^H[1-6]$/.test(parent.tagName) && parent.tagName<start.tagName &&
                       first && table.getBoundingClientRect().top-parent.getBoundingClientRect().top+
                       first.getBoundingClientRect().height+(table.tHead?.getBoundingClientRect().height||0)<height-8)
                      breakStart=parent;
                  }
                  breakStart.classList.add('print-break');
                }
              }
              for(const pre of document.querySelectorAll('pre'))pre.classList.add(
                pre.getBoundingClientRect().height<height-45?'print-keep':'print-flow');
              for(const x of document.querySelectorAll('figure.image,pre.print-keep')){
                let label=x.previousElementSibling;
                while(label?.tagName==='P'&&!label.textContent.trim())label=label.previousElementSibling;
                if(label?.tagName==='P'&&label.textContent.trim().length<120 &&
                  x.getBoundingClientRect().bottom-label.getBoundingClientRect().top<height){
                  const range=document.createRange();range.setStartBefore(label);range.setEndAfter(x);
                  const group=document.createElement('div');group.className=x.tagName==='PRE'?'print-code-group':'print-image-group';
                  range.surroundContents(group);
                }
              }
              for(const table of document.querySelectorAll('table')){
                const head=table.tHead?.getBoundingClientRect().height||0;
                for(const body of table.tBodies)for(const row of body.rows)
                  if(row.getBoundingClientRect().height+head>height-8)tooTall.push(row.id||row.innerText.slice(0,80));
              }
              return {tallRows:tooTall,
                overflow:[...document.querySelectorAll('td,th,pre,img')].filter(x=>x.scrollWidth>x.clientWidth+2).map(x=>x.id||x.tagName)};
            }''', {'settings': settings, 'height': height})
            if layout['tallRows']:
                raise ValueError('Table row cannot fit on a page: ' + repr(layout['tallRows']))
            if layout['overflow']:
                raise ValueError('Horizontal overflow: ' + repr(layout['overflow']))
            if page.locator('body').text_content() != before or page.locator('a').evaluate_all("xs=>xs.map(x=>x.getAttribute('href'))") != links:
                raise ValueError('Print adjustments changed text or links')
            if page.locator('article.page,body').evaluate_all('xs=>xs.map(x=>getComputedStyle(x).fontFamily)') != fonts:
                raise ValueError('Print font family changed')
            evidence.mkdir(parents=True)
            if remote_resources:
                (evidence / 'assets').mkdir()
                for asset in remote_resources:
                    path = evidence / 'assets' / (digest(asset['url'].encode()) + '.asset')
                    path.write_bytes(asset.pop('data'))
                    asset['cache'] = fingerprint(path)
                    dependencies[str(path)] = asset['cache']
            output.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(path=str(output), format='A4', landscape=True, prefer_css_page_size=True,
                     display_header_footer=False, print_background=True)
            printed = page.content().replace('<head>', '<head><base href="' + html_module.escape(source.as_uri(), quote=True) + '">', 1)
            (evidence / 'print.html').write_text(printed)
            (evidence / 'print.css').write_text(css)
            atomic_json(evidence / 'content.json', content)
        finally:
            browser.close()
    for saved in dependencies.values():
        if fingerprint(Path(saved['path'])) != saved:
            raise ValueError('Export input changed while printing')
    inputs = {f'input-{i}': Path(saved['path']) for i, saved in enumerate(dependencies.values())}
    inputs.update(pdf=output, content=evidence / 'content.json', css=evidence / 'print.css',
                  print_copy=evidence / 'print.html')
    receipt = {'schema_version': 1, 'source': source_before, 'pdf': fingerprint(output),
               'dependencies': dependencies, 'settings': settings,
               'remote_resources': remote_resources,
               'state_path': str(state_file),
               'inputs': {k: fingerprint(v) for k, v in inputs.items()}, 'renderer': 'Playwright Chromium',
               'origin_and_remote_freshness': 'not verified by print tool'}
    atomic_json(evidence / 'print.json', receipt)
    ledger.record('print', inputs, values=settings, evidence=[str(evidence / 'print.json')],
                  expected_inputs=receipt['inputs'], expected_parents=expected_parents)
    receipt['print_stage_version'] = ledger.data['stages']['print']['version']
    atomic_json(evidence / 'print.json', receipt)
    return receipt


def current_receipt(evidence):
    evidence = Path(evidence).resolve()
    receipt = json.loads((evidence / 'print.json').read_text())
    if receipt.get('schema_version') != 1:
        raise ValueError('Unsupported print receipt')
    for saved in receipt['inputs'].values():
        if fingerprint(Path(saved['path'])) != saved:
            raise ValueError('Print input or PDF changed; regenerate before verification: ' + saved['path'])
    current = Ledger(Path(receipt['state_path'])).refresh().get('print', {})
    if (current.get('version') != receipt.get('print_stage_version') or current.get('status') != 'verified'):
        raise ValueError('This PDF candidate is not the current verified print in the shared ledger')
    return receipt


def verify(evidence):
    import fitz
    from pypdf import PdfReader
    evidence = Path(evidence).resolve()
    receipt = current_receipt(evidence)
    content = json.loads((evidence / 'content.json').read_text())
    result_path = evidence / 'verification.json'
    ledger = Ledger(Path(receipt['state_path']))
    inputs = {k: Path(v['path']) for k, v in receipt['inputs'].items()}
    try:
        with fitz.open(receipt['pdf']['path']) as pdf:
            texts = [p.get_text() for p in pdf]
            if not texts or any(abs(p.rect.width - 841.89) > 1 or abs(p.rect.height - 595.28) > 1 for p in pdf):
                raise ValueError('Every page must be A4 landscape')
            geometric_text, geometry = text_geometry(pdf)
            sorted_text, sorted_geometry = text_geometry(pdf, sort_lines=True)
            check_text(content['units'], geometric_text, geometry=geometry,
                       alternatives=[(sorted_text, sorted_geometry)])
            # PyMuPDF coalesces some adjacent space glyphs. pypdf preserves the
            # actual Chromium code-space runs; use it for this separate check.
            reader = PdfReader(receipt['pdf']['path'])
            code_text = '\n'.join(p.extract_text() or '' for p in reader.pages)
            check_indentation(content['codes'], code_text)
            paired = []
            for row in content['rows']:
                pages = [i + 1 for i, text in enumerate(texts)
                         if all(norm(cell) in norm(text) for cell in row['cells'])]
                if not pages:
                    raise ValueError('Paired source/analysis row split or missing: ' + row['id'])
                paired.append({'id': row['id'], 'pages': pages})
            expected_images = [tuple([tuple(i['pixel_key'][0]), i['pixel_key'][1]]) for i in content['images']]
            actual_images = []
            renders = evidence / 'pages'
            if renders.exists():
                # A new verification run has a new directory; earlier review images remain evidence.
                index = 2
                while (evidence / f'pages-{index}').exists():
                    index += 1
                renders = evidence / f'pages-{index}'
            renders.mkdir()
            thumbs, render_paths = [], []
            for index, page in enumerate(pdf):
                info = page.get_image_info(xrefs=True)
                if not page.get_text().strip() and not info:
                    raise ValueError('Blank PDF page: ' + str(index + 1))
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines', []):
                        for span in line['spans']:
                            x0, y0, x1, y1 = span['bbox']
                            if x0 < -.5 or y0 < -.5 or x1 > page.rect.width + .5 or y1 > page.rect.height + .5:
                                raise ValueError('Clipped text on page: ' + str(index + 1))
                masks = {entry[0]: entry[1] for entry in page.get_images(full=True)}
                for image in info:
                    xref = image['xref']
                    if not xref:
                        raise ValueError('Inline PDF image needs manual identity verification')
                    pix = fitz.Pixmap(pdf, xref)
                    if masks.get(xref):
                        pix = fitz.Pixmap(pix, fitz.Pixmap(pdf, masks[xref]))
                    if pix.colorspace.n != 3:
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    mode = 'RGBA' if pix.alpha else 'RGB'
                    rgba = Image.frombytes(mode, (pix.width, pix.height), pix.samples).convert('RGBA')
                    actual_images.append((rgba.size, digest(rgba.tobytes())))
                    position = len(actual_images) - 1
                    if position >= len(content['images']):
                        raise ValueError('Unexpected image occurrence')
                    label = content['images'][position].get('label')
                    if label and norm(label) not in norm(texts[index]):
                        raise ValueError('Screenshot label isolated from image')
                    x0, y0, x1, y1 = image['bbox']
                    if x0 < -.5 or y0 < -.5 or x1 > page.rect.width + .5 or y1 > page.rect.height + .5:
                        raise ValueError('Clipped image')
                    if abs((x1-x0)/(y1-y0) - pix.width/pix.height) > .02:
                        raise ValueError('Image aspect ratio changed')
                path = renders / f'page-{index + 1:03}.png'
                page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(path)
                render_paths.append(path)
                with Image.open(path) as image:
                    image.thumbnail((400, 283))
                    thumb = Image.new('RGB', (420, 310), '#dddddd')
                    thumb.paste(image, ((420-image.width)//2, 23))
                    ImageDraw.Draw(thumb).text((10, 5), str(index + 1), fill='black')
                    thumbs.append(thumb)
            if actual_images != expected_images:
                raise ValueError('Image pixels, count, or occurrence order differs')
            for start in range(0, len(thumbs), 12):
                batch = thumbs[start:start+12]
                sheet = Image.new('RGB', (1260, ((len(batch)+2)//3)*310), 'white')
                for i, thumb in enumerate(batch):
                    sheet.paste(thumb, ((i%3)*420, (i//3)*310))
                sheet.save(renders / f'contact-{start//12+1:03}.png')
            result = {'pdf': receipt['pdf'], 'pages': len(pdf), 'paired_rows': len(paired),
                      'paired_row_pages': paired, 'image_occurrences': len(actual_images),
                      'content': 'verified', 'visual_review': 'not verified',
                      'renders': [fingerprint(p) for p in render_paths],
                      'contact_sheets': [fingerprint(p) for p in sorted(renders.glob('contact-*.png'))]}
        current_receipt(evidence)
        atomic_json(result_path, result)
        tracked = {**inputs, 'verification': result_path, 'receipt': evidence / 'print.json'}
        expected = {**receipt['inputs'], 'verification': fingerprint(result_path), 'receipt': fingerprint(evidence / 'print.json')}
        ledger.record('content', tracked, evidence=[str(result_path)], expected_inputs=expected,
                      expected_parents={'print': receipt['print_stage_version']},
                      values={'pdf_sha256': receipt['pdf']['sha256'], 'print_version': receipt['print_stage_version']})
        return result
    except Exception as error:
        atomic_json(result_path, {'content': 'failed', 'error': str(error), 'visual_review': 'not verified'})
        try:
            ledger.record('content', inputs, status='failed', evidence=[str(result_path)],
                          expected_parents={'print': receipt['print_stage_version']})
        except ValueError:
            pass  # Do not mark a different candidate's content failed.
        raise


def record_review(evidence, reviewed_pages, notes):
    evidence = Path(evidence).resolve()
    receipt = current_receipt(evidence)
    verification = json.loads((evidence / 'verification.json').read_text())
    ledger = Ledger(Path(receipt['state_path']))
    current = ledger.refresh().get('content', {})
    if (verification.get('content') != 'verified' or current.get('status') != 'verified' or
            current.get('values', {}).get('pdf_sha256') != receipt['pdf']['sha256'] or
            current.get('values', {}).get('print_version') != receipt['print_stage_version'] or
            current.get('inputs', {}).get('verification') != fingerprint(evidence / 'verification.json')):
        raise ValueError('Current automated verification required first')
    if sorted(reviewed_pages) != list(range(1, verification['pages'] + 1)) or not notes.strip():
        raise ValueError('Record every actually reviewed page and nonempty review notes')
    renders = verification['renders'] + verification['contact_sheets']
    if any(fingerprint(Path(r['path'])) != r for r in renders):
        raise ValueError('Review images changed since verification')
    review = {'pdf': receipt['pdf'], 'reviewed_pages': reviewed_pages, 'notes': notes,
              'renders': renders, 'visual_review': 'verified'}
    review_path = evidence / 'visual-review.json'
    atomic_json(review_path, review)
    inputs = {f'render-{i}': Path(r['path']) for i, r in enumerate(renders)}
    inputs.update(pdf=Path(receipt['pdf']['path']), review=review_path)
    expected = {f'render-{i}': r for i, r in enumerate(renders)}
    expected.update(pdf=receipt['pdf'], review=fingerprint(review_path))
    ledger.record('visual', inputs, evidence=[str(review_path)], expected_inputs=expected,
                  expected_parents={'print': receipt['print_stage_version'], 'content': current['version']})
    return review


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    printing = commands.add_parser('print')
    printing.add_argument('--html', type=Path, required=True)
    printing.add_argument('--output', type=Path, required=True)
    printing.add_argument('--evidence', type=Path, required=True)
    printing.add_argument('--config', type=Path)
    printing.add_argument('--state', type=Path)
    commands.add_parser('verify').add_argument('--evidence', type=Path, required=True)
    review = commands.add_parser('review', help='Record an actual human/agent visual review; does not perform it')
    review.add_argument('--evidence', type=Path, required=True)
    review.add_argument('--pages', type=int, nargs='+', required=True)
    review.add_argument('--notes', required=True)
    args = parser.parse_args()
    if args.command == 'print':
        config = json.loads(args.config.read_text()) if args.config else None
        result = print_html(args.html, args.output, args.evidence, config=config,
                            config_path=args.config, state_path=args.state)
    elif args.command == 'verify':
        result = verify(args.evidence)
    else:
        result = record_review(args.evidence, args.pages, args.notes)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
