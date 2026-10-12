"""Frozen EC2 rendering, offline routes and measured overflow inspection."""
from contextlib import contextmanager
from dataclasses import asdict
import copy
import importlib.util
import json
import mimetypes
from pathlib import Path
import sys
import types
from urllib.parse import unquote, urlparse
from pdf_types import Probe, PdfError

ASSETS=Path(__file__).resolve().parent.parent/'assets/pdf'
TEMPLATES=ASSETS/'ec2'
VENDOR=ASSETS/'vendor'
# Use the frozen implementation itself rather than maintaining a second transform.
_paths=types.ModuleType('paths');_paths.TEMPLATES=TEMPLATES
_previous=sys.modules.get('paths');sys.modules['paths']=_paths
try:
    _spec=importlib.util.spec_from_file_location('_ds_ec2_frozen',TEMPLATES/'render.py')
    _reference=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_reference)
finally:
    if _previous is None: sys.modules.pop('paths',None)
    else: sys.modules['paths']=_previous
load_template=_reference.load_template
inject=_reference.inject
_active=None

@contextmanager
def render_session():
    global _active
    if _active is not None:
        yield _active;return
    try:
        from playwright.sync_api import sync_playwright, Error as PlaywrightError
    except ImportError as exc:
        raise PdfError('Playwright is required; select an installed Python runtime') from exc
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome')
            _active=browser
            try: yield browser
            finally: _active=None;browser.close()
    except PlaywrightError as exc:
        raise PdfError('Chrome rendering failed: '+str(exc)) from exc


def resource_path(url):
    parsed=urlparse(url);path=unquote(parsed.path)
    prefix='/npm/katex@0.16.11/dist/'
    if parsed.netloc=='cdn.jsdelivr.net' and path.startswith(prefix):
        return VENDOR/'katex'/path[len(prefix):]
    prefix='/gh/orioncactus/pretendard@v1.3.9/dist/web/static/'
    if parsed.netloc=='cdn.jsdelivr.net' and path.startswith(prefix):
        rel=path[len(prefix):]
        return VENDOR/'pretendard'/('pretendard.css' if rel=='pretendard.min.css' else rel)
    return None

GEOMETRY_JS=r'''() => {
 const overflow=new Set((document.body.dataset.overflow||'').split(',').filter(Boolean));
 const geometry={},typography={};
 for(const p of document.querySelectorAll('.page')){
  const zoom=parseFloat(getComputedStyle(p).zoom)||1, pr=p.getBoundingClientRect();
  const rect=n=>{const r=n.getBoundingClientRect();return {x:(r.left-pr.left)/zoom,y:(r.top-pr.top)/zoom,w:r.width/zoom,h:r.height/zoom}};
  geometry[p.id]={page:{w:pr.width/zoom,h:pr.height/zoom},regions:[]};
  for(const n of p.querySelectorAll('.panel,.work,.hint-body,pre,table,.fig-band,img.fig,.sol-answer')){
   const r=rect(n);geometry[p.id].regions.push({tag:n.tagName,cls:n.className,...r});
   const cap=window.workbookVideoLayout?900:pr.height/zoom;
   if(r.x< -1||r.x+r.w>pr.width/zoom+1||r.y+r.h>cap+1||n.scrollWidth>n.clientWidth+2||n.scrollHeight>n.clientHeight+2)overflow.add(p.id);
   if(n.matches('pre,table,img.fig,.sol-answer')){
    const container=n.closest('.panel,.work,.hint-body') || n.parentElement;
    const cr=rect(container);
    if(r.x<cr.x-1||r.x+r.w>cr.x+cr.w+1||r.y+r.h>cr.y+cr.h+1)overflow.add(p.id);
   }
  }
  const panel=p.querySelector('.panel'),work=p.querySelector('.work');
  const scale=n=>{const t=getComputedStyle(n).transform;return t==='none'?1:new DOMMatrix(t).a};
  if(panel&&work)typography[p.id]={panel:parseFloat(getComputedStyle(panel).getPropertyValue('--fs'))||1,
    solution:parseFloat(getComputedStyle(work).getPropertyValue('--sfs'))||1,
    math:[...p.querySelectorAll('.katex-display>.katex')].map(scale),hints:[...p.querySelectorAll('.hint-strip-formula')].map(scale)};
 }
 return {ids:[...document.querySelectorAll('.page')].map(p=>p.id),overflow:[...overflow],geometry,typography,
 ready:document.documentElement.dataset.ready,math:typeof katex!=='undefined'&&typeof renderMathInElement!=='undefined',
 mathErrors:document.querySelectorAll('.katex-error').length,brokenImages:[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src),
 font:document.fonts.check('16px Pretendard')};
}'''


def _run(data,mode,layout,run,pdf=None):
    run=Path(run);run.mkdir(parents=True,exist_ok=True)
    html_path=run/f'{mode}-{layout}.html';html_path.write_text(inject(load_template(mode,layout),data),encoding='utf-8')
    errors=[]
    with render_session() as browser:
        page=browser.new_page(viewport={'width':1400,'height':1000})
        def route(req):
            url=req.request.url;parsed=urlparse(url)
            if parsed.scheme in ('data','file'): req.continue_();return
            path=resource_path(url)
            if path is not None and path.is_file():
                req.fulfill(body=path.read_bytes(),content_type=mimetypes.guess_type(path)[0] or 'application/octet-stream')
            else:
                errors.append('Missing/offline resource: '+url);req.abort()
        page.route('**/*',route)
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
        try:
            page.goto(html_path.resolve().as_uri())
            page.wait_for_function('document.documentElement.dataset.ready',timeout=120000)
            page.evaluate('document.fonts.ready')
            info=page.evaluate(GEOMETRY_JS)
            if info['ready']!='true':errors.append('Template ready: '+info['ready'])
            if not info['math']:errors.append('KaTeX/auto-render missing')
            if info['mathErrors']:errors.append('KaTeX errors')
            if info['brokenImages']:errors.append('Broken images: '+str(info['brokenImages']))
            # FontFaceSet.check alone accepts absent family fallback; demand loaded faces.
            if not page.evaluate("[...document.fonts].some(f=>f.family.includes('Pretendard')&&f.status==='loaded')"):
                errors.append('Pretendard not loaded')
            if pdf is not None:
                Path(pdf).parent.mkdir(parents=True,exist_ok=True)
                page.pdf(path=str(pdf),prefer_css_page_size=True,print_background=True)
            result=Probe(tuple(info['ids']),tuple(info['overflow']),tuple(dict.fromkeys(errors)),info['geometry'],info['typography'])
        finally:page.close()
    return result


def probe(data, mode, layout, run):
    return _run(data,mode,layout,run)


def render(data, mode, run, pdf):
    with render_session():
        measured=probe(data,mode,'a4',Path(run)/'a4')
        if measured.errors: return measured
        video=copy.deepcopy(data);video['meta']['typography']=measured.typography
        return _run(video,mode,'video-16x9',Path(run)/'video',pdf)
