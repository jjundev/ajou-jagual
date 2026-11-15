"""Surgical review updates and rollback publication; existing raw cards remain intact."""
from html.parser import HTMLParser
from html import escape
from pathlib import Path
import os
import re
import tempfile
import hashlib
import json

def revision_hash(manifest, cards):
    payload=json.dumps({'problems':manifest['problems'],'cards':cards},ensure_ascii=False,sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:20]

def build_revision(existing_html, *, manifest, cards):
    source=existing_html;spans=Spans(source).spans
    ordered=[q['id'] for q in manifest['problems']]
    if set(cards)!=set(ordered):raise ValueError('revision cards/manifest mismatch')
    for q in manifest['problems']:
        parsed=extract_cards(cards[q['id']])
        if len(parsed)!=1 or parsed[0]['id']!=q['id'] or parsed[0]['source']!=q['source']:raise ValueError('revision fragment identity mismatch')
    sections=[]
    populated={q['part'] for q in manifest['problems']}
    parts=[part for part in manifest['parts'] if part['id'] in populated]
    for part in parts:
        content='\n'.join(cards[q['id']] for q in manifest['problems'] if q['part']==part['id'])
        sections.append(f'<section id="{part["id"]}"><h2>{escape(part["title"])}</h2>\n{content}\n</section>')
    main='<main>\n<div class="hero"><h1>'+escape(manifest['review_title'])+'</h1><p>'+manifest['review_intro']+'</p></div>\n'+'\n'.join(sections)+'\n</main>'
    edits=[]
    main_span=next(row for row in spans if row[0]=='main')
    for tag,attrs,start,end in spans:
        if main_span[2]<start<main_span[3]:continue
        if tag=='main':edits.append((start,end,main))
        elif tag=='nav' and 'toc' in attrs.get('class','').split():
            toc=''.join(f'<a href="#{p["id"]}">{escape(p["short"])}</a>' for p in parts)
            edits.append((start,end,'<nav class="toc" aria-label="목차">'+toc+'</nav>'))
        elif tag=='title':edits.append((start,end,'<title>'+escape(manifest['review_title'])+'</title>'))
        elif tag=='footer':edits.append((start,end,'<footer>'+manifest['footer_review']+'</footer>'))
        elif tag=='meta' and attrs.get('name')=='description':edits.append((start,end,'<meta name="description" content="'+escape(manifest['review_title'],quote=True)+'">'))
    for start,end,replacement in sorted(edits,reverse=True):source=source[:start]+replacement+source[end:]
    return stamp_revision(source, manifest, cards)

def stamp_revision(source, manifest, cards):
    version=revision_hash(manifest,cards)
    source=re.sub(r'(<body\b[^>]*?)\sdata-revision="[^"]*"',r'\1',source)
    source=re.sub(r'<body\b',f'<body data-revision="{version}"',source,count=1)
    source=source.replace("'od-review-solved:' + RANGE;","'od-review-solved:' + RANGE + ':' + document.body.dataset.revision;")
    return source

class Spans(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source=source;self.lines=[0];self.stack=[];self.spans=[]
        for m in re.finditer('\n',source):self.lines.append(m.end())
        self.feed(source)
    def position(self):
        line,col=self.getpos();return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs):
        if tag == 'meta':
            self.spans.append((tag, dict(attrs), self.position(), self.position() + len(self.get_starttag_text())))
        if tag in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:return
        self.stack.append((tag,dict(attrs),self.position()))
    def handle_startendtag(self,tag,attrs):pass
    def handle_endtag(self,tag):
        if not self.stack:return
        if self.stack[-1][0]!=tag:raise ValueError(f'unbalanced HTML: {tag}')
        t,a,start=self.stack.pop();end=self.source.index('>',self.position())+1
        self.spans.append((t,a,start,end))

def extract_cards(source):
    return [dict(id=a.get('id',''),source=a.get('data-source',''),raw=source[start:end]) for t,a,start,end in sorted(Spans(source).spans,key=lambda row:row[2]) if t=='article' and 'card' in a.get('class','').split()]

def check_preserved(before,after):
    old=extract_cards(before);new={c['id']:c for c in extract_cards(after)}
    return [f'기존 카드 변경/누락: {c["id"]}' for c in old if c['id'] not in new or new[c['id']]!=c]

def build_update(existing_html,cards,*,title,intro,footer):
    source=existing_html;spans=Spans(source).spans
    part=next((row for row in spans if row[0]=='section' and row[1].get('id')=='partD'),None)
    additions=extract_cards(''.join(cards))
    if len(additions)!=len(cards):raise ValueError('each fragment must have one card')
    old=extract_cards(source);old_d=extract_cards(source[part[2]:part[3]]) if part else []
    base=[c for c in old if c not in old_d]
    ids=[c['id'] for c in base+additions]
    if len(set(ids))!=len(ids):raise ValueError('duplicate card IDs')
    new_sources=[c['source'] for c in additions]
    if len(set(new_sources))!=len(new_sources):raise ValueError('duplicate textbook source')
    if any(not c['source'].startswith('textbook-') for c in additions):raise ValueError('textbook source required')
    if old_d and {c['source']:c['id'] for c in old_d}!={c['source']:c['id'] for c in additions}:raise ValueError('rerun cannot reassign source or ID')
    maximum=max([int(c['id'][1:]) for c in base if re.fullmatch('p[0-9]+',c['id'])] or [0])
    if [c['id'] for c in additions]!=[f'p{maximum+i+1}' for i in range(len(additions))]:raise ValueError('append consecutive pN IDs')
    section='<section id="partD"><h2>D. 교과서 연습문제</h2>\n'+'\n'.join(cards)+'\n</section>'
    edits=[]
    if part:edits.append((part[2],part[3],section))
    else:
        main=next(row for row in spans if row[0]=='main');end=source.rfind('</main',main[2],main[3]);edits.append((end,end,section+'\n'))
    card_spans = [row for row in spans if row[0] == 'article' and 'card' in row[1].get('class', '').split()]
    head = next((row for row in spans if row[0]=='head'), None)
    for t,a,start,end in spans:
        if part and part[2] <= start < part[3]:
            continue
        if t=='title' and head and head[2] < start < head[3]:edits.append((start,end,'<title>'+escape(title)+'</title>'))
        elif t=='meta' and a.get('name')=='description':
            edits.append((start,end,'<meta name="description" content="'+escape(title,quote=True)+'">'))
        elif t=='nav' and 'toc' in a.get('class','').split() and not part:
            at=source.rfind('</nav',start,end);edits.append((at,at,'<a href="#partD">D 교과서</a>'))
        elif t=='div' and 'hero' in a.get('class','').split():
            edits.append((start,end,'<div class="hero"><h1>'+escape(title)+'</h1><p>'+intro+'</p></div>'))
        elif t=='footer' and not any(c[2] <= start < c[3] for c in card_spans):edits.append((start,end,'<footer>'+footer+'</footer>'))
    for start,end,replacement in sorted(edits,reverse=True):source=source[:start]+replacement+source[end:]
    source=source.replace('그 문제의 기출 원문, 힌트, 풀이','그 문제의 원문, 힌트, 풀이')
    # Do not touch wording inside the existing cards.
    errors=check_preserved(existing_html if not part else existing_html[:part[2]]+existing_html[part[3]:],source)
    if errors:raise ValueError('\n'.join(errors))
    return source

def publish_update(files,*,backup):
    backup=Path(backup);backup.mkdir(parents=True,exist_ok=False)
    originals={p:p.read_bytes() if p.exists() else None for p in files}
    for i,(p,data) in enumerate(originals.items()):
        if data is not None:(backup/f'{i:03}-{p.name}').write_bytes(data)
    temporaries={};published=[]
    try:
        for p,data in files.items():
            if data is None:
                continue
            p.parent.mkdir(parents=True,exist_ok=True)
            fd,name=tempfile.mkstemp(prefix='.review-update-',dir=p.parent)
            with os.fdopen(fd,'wb') as f:f.write(data)
            temporaries[p]=Path(name)
        for p,data in files.items():
            current=p.read_bytes() if p.exists() else None
            if current!=originals[p]:raise ValueError(f'target changed after backup: {p}')
            if data is None:
                p.unlink(missing_ok=True)
            else:
                os.replace(temporaries[p],p)
            published.append(p)
    except BaseException:
        for p in reversed(published):
            if originals[p] is None:p.unlink()
            else:p.write_bytes(originals[p])
        raise
    finally:
        for temp in temporaries.values():temp.unlink(missing_ok=True)
