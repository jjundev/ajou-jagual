"""Extract all problem/solution blocks without using the explanation vendor."""
import base64
import json
import mimetypes
import hashlib
import html
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlparse
from html2md import Builder, Node, serialize, VOID, SVG_CSS
from pdf_types import Block, Card, Pack, PageSlice, PdfError
from pack_layout import pdf_report_path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def markup(node):
    if isinstance(node, str):
        return html.escape(node, quote=False)
    if node.tag == 'svg':
        return serialize(node)
    attrs = ''.join(f' {k}="{html.escape(v, quote=True)}"' for k,v in node.attrs.items())
    opening = f'<{node.tag}{attrs}>'
    return opening if node.tag in VOID else opening + ''.join(map(markup,node.children)) + f'</{node.tag}>'


def blocks(node):
    out=[]
    for child in node.children:
        if isinstance(child,str):
            if child.strip(): out.append(Block('prose',markup(child),child))
        elif child.tag=='summary' or 'answer' in child.classes:
            continue
        elif child.tag in ('ol','ul'):
            # Preserve list semantics and numbering while permitting item boundaries.
            start=int(child.attrs.get('start','1'))
            for i,li in enumerate(c for c in child.children if isinstance(c,Node) and c.tag=='li'):
                if 'steps' in child.classes:
                    out.append(Block('prose', ''.join(markup(c) for c in li.children), li.text()))
                else:
                    attrs=f' start="{start+i}"' if child.tag=='ol' else ''
                    out.append(Block('prose',f'<{child.tag}{attrs}>'+markup(li)+f'</{child.tag}>',li.text()))
        else:
            kind={'pre':'code','table':'table','svg':'figure','img':'figure'}.get(child.tag,'prose')
            # Expose wrappers containing code as independent blocks, in original order.
            if child.tag=='div' and any(isinstance(c,Node) and c.tag in ('pre','table') for c in child.children):
                out.extend(blocks(child))
            else:
                out.append(Block(kind,markup(child),child.text()))
    return tuple(out)


def ensure_report_owner(source):
    """A folder's shared report must describe exactly this one review."""
    source=Path(source).resolve()
    peers=[p for p in source.parent.iterdir() if p.is_file() and
           re.fullmatch(r'복습문제_\d{4}(?:-\d{4})?_.+\.html',unicodedata.normalize('NFC',p.name))]
    if len(peers)>1:
        raise PdfError('자료_PDF report collision: multiple reviews in same folder')
    report=pdf_report_path(source.parent)
    if report.exists():
        old=json.loads(report.read_text(encoding='utf-8'))
        owner=unicodedata.normalize('NFC',Path(old.get('source','')).name)
        if owner!=unicodedata.normalize('NFC',source.name):
            raise PdfError('자료_PDF report collision: existing report belongs to another source')


def read_pack(review: Path) -> Pack:
    review=Path(review).resolve()
    match=re.fullmatch(r'복습문제_(\d{4}(?:-\d{4})?)_(.+)\.html',unicodedata.normalize('NFC',review.name))
    if not match: raise PdfError(f'Invalid review filename: {review}')
    ensure_report_owner(review)
    builder=Builder();builder.feed(review.read_text(encoding='utf-8'))
    cards=[];seen=set()
    for node in builder.root.find_all(lambda n:n.tag=='article' and 'card' in n.classes):
        pid=node.attrs.get('id','')
        if not re.fullmatch(r'p[1-9]\d*',pid) or pid in seen: raise PdfError(f'Duplicate/invalid ID: {pid}')
        seen.add(pid)
        def find(cls): return next(node.find_all(lambda n:cls in n.classes),None)
        problem,solution,answer,hint=find('problem'),find('solution'),find('answer'),find('hint')
        if problem is None or solution is None or answer is None or not answer.text().strip():
            raise PdfError(f'{pid}: missing problem/solution/answer')
        title=next(node.find_all(lambda n:n.tag=='h3'),None)
        source=node.attrs.get('data-source','')
        kind='연습문제' if node.attrs.get('data-source-kind')=='textbook' else ('기출' if re.match(r'(?:\d{4}|unk)-(?:mid|final)-',source) or '기출' in source else '장말문제')
        title=re.sub(r'^P\d+\.\s*','',title.text() if title else pid)
        cards.append(Card(pid,source,kind,title,blocks(problem),blocks(solution),markup(answer),
                          ''.join(markup(c) for c in hint.children if not isinstance(c,Node) or c.tag!='summary') if hint else ''))
    return Pack(review,digest(review),match[1],match[2],tuple(cards))


def figures_from(raw, source, assets):
    builder=Builder();builder.feed(raw);figures=[]
    def walk(node):
        for child in list(node.children):
            if not isinstance(child,Node): continue
            if child.tag in ('svg','img'):
                if child.tag=='svg':
                    # XML namespace and inherited review SVG styles for standalone rendering.
                    svg=serialize(child)
                    if 'xmlns=' not in svg: svg=svg.replace('<svg','<svg xmlns="http://www.w3.org/2000/svg"',1)
                    svg=svg.replace('>', '><style>'+SVG_CSS+'</style>',1)
                    vb=child.attrs.get('viewbox','0 0 640 240').split()
                    w,h=map(float,vb[-2:]);blob=svg.encode();suffix='.svg'
                else:
                    src=child.attrs.get('src','')
                    if src.startswith('data:'):
                        meta,encoded=src.split(',',1);blob=base64.b64decode(encoded) if ';base64' in meta else unquote(encoded).encode();suffix='.svg' if 'svg' in meta else '.png'
                    else:
                        parsed=urlparse(src)
                        if parsed.scheme: raise PdfError('Remote image unsupported: '+src)
                        path=(source.parent/unquote(parsed.path)).resolve()
                        if not path.is_relative_to(source.parent): raise PdfError('Image outside pack: '+src)
                        blob=path.read_bytes();suffix=path.suffix
                    if suffix=='.svg':
                        m=re.search(rb'viewBox=["\']([^"\']+)',blob)
                        w,h=map(float,m[1].split()[-2:]) if m else (640,240)
                    else:
                        from PIL import Image
                        import io
                        w,h=Image.open(io.BytesIO(blob)).size
                if w<=0 or h<=0: raise PdfError('Invalid figure dimensions')
                name=hashlib.sha256(blob).hexdigest()+suffix;assets.mkdir(parents=True,exist_ok=True);(assets/name).write_bytes(blob)
                figures.append({'src':(assets/name).resolve().as_uri(),'w_mm':w*25.4/96,'h_mm':h*25.4/96,'sha256':hashlib.sha256(blob).hexdigest()})
                node.children.remove(child)
            else: walk(child)
    walk(builder.root)
    return ''.join(markup(c) for c in builder.root.children),figures


def freeze_inline_html(raw, source, assets):
    """Freeze images in place, including solution, answer and hint content."""
    builder=Builder();builder.feed(raw)
    images=list(builder.root.find_all(lambda n:n.tag=='img'))
    svgs=list(builder.root.find_all(lambda n:n.tag=='svg'))
    if not images and not svgs:return raw
    for img in images:
        src=img.attrs.get('src','')
        if src.startswith('data:'):continue
        url=urlparse(src)
        if url.scheme or url.netloc:raise PdfError('Remote image unsupported: '+src)
        path=(source.parent/unquote(url.path)).resolve()
        if not path.is_relative_to(source.parent):raise PdfError('Image outside pack: '+src)
        blob=path.read_bytes();name=hashlib.sha256(blob).hexdigest()+path.suffix
        assets.mkdir(parents=True,exist_ok=True);(assets/name).write_bytes(blob)
        mime=mimetypes.guess_type(path)[0] or 'application/octet-stream'
        img.attrs['src']='data:'+mime+';base64,'+base64.b64encode(blob).decode('ascii')
    for svg in svgs:
        svg.attrs.setdefault('xmlns','http://www.w3.org/2000/svg')
        style=Node('style');style.children=[SVG_CSS];svg.children.insert(0,style)
    return ''.join(markup(c) for c in builder.root.children)


def to_payload(pack: Pack, mode: str, pages: tuple[PageSlice,...], assets: Path) -> dict:
    if mode not in ('problems','answers'): raise PdfError('Invalid mode')
    by_id={c.id:c for c in pack.cards};problems=[]
    for page in pages:
        c=by_id[page.logical_id]
        # Explicit source identity: only these tables are learner worksheets.
        worksheet = pack.range == '1012' and c.id in ('p2','p3')
        code = ''.join(b.html for b in page.problem if b.kind == 'code')
        workspace = ''.join(b.html for b in page.problem if b.kind == 'table') if worksheet and mode == 'problems' else ''
        body = ''.join(b.html for b in page.problem if b.kind != 'code' and not (workspace and b.kind == 'table'))
        ask,figures=figures_from(body,pack.source,assets)
        number=c.id[1:]+(f' (계속 {page.continuation})' if page.continuation>1 else '')
        p={'id':page.physical_id,'kind':c.kind,'number':number,'title':c.title,'section':c.source,
           'book_page':None,'difficulty':0,'sol':False,'original_lang':'ko',
           'html':{'original':'','conditions':'','ask':ask,'code':code},'workspace_html':workspace,'figures':figures,
           'hints':[{'label':'풀이 방향','html':freeze_inline_html(c.hint_html,pack.source,assets)}] if page.show_hint and c.hint_html else []}
        if mode=='answers':
            p['solution']={'steps':[{'label':'','html':freeze_inline_html(b.html,pack.source,assets)} for b in page.solution],
                           'answer':freeze_inline_html(c.answer_html,pack.source,assets) if page.show_answer else ''}
        problems.append(p)
    return {'meta':{'mode':mode,'title':f'{pack.range} {pack.slug}','chapter':'자료구조및알고리즘이해','total':len(pages)},'problems':problems}
