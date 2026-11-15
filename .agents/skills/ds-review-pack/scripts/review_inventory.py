"""Read only live, date-root review cards; stage overlays replace one whole pack."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote,urlsplit
from html2md import Builder
from pack_layout import pack_folders, nfc, normalized_child
from update_review import Spans
from review_source import NAME, review_paths, read_review, source_digest

def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def card_content(raw):
    spans=Spans(raw).spans
    # The question includes code/options/figures, but never disclosure answers.
    question=next((raw[s:e] for t,a,s,e in spans if {'question','problem'} & set(a.get('class','').split())),None)
    original=next((raw[s:e] for t,a,s,e in spans if t=='details' and 'original' in a.get('class','').split()),'')
    if question is None:
        raise ValueError('manifest card has no question region')
    return question,original

def collect_reviews(repo: Path, *, overlays=None):
    overlays=overlays or {}
    rows=[]
    roots=pack_folders(repo)
    if set(overlays)-{nfc(p.name) for p in roots}:
        raise ValueError('overlay has unknown range')
    for root in roots:
        date=nfc(root.name)
        matches=[p for p in review_paths(root) if NAME.fullmatch(nfc(p.name))[1] == date]
        if len(matches)!=1: raise ValueError(f'{date}: ambiguous review/manifest')
        review=Path(overlays.get(date,matches[0])).resolve()
        manifest=normalized_child(review.parent/'.pack','자료_복습팩')/'manifest.json'
        m=json.loads(manifest.read_text(encoding='utf-8'))
        if m.get('range')!=date: raise ValueError(f'{date}: manifest range mismatch')
        text=read_review(review)
        cards=[]
        for t,a,s,e in sorted(Spans(text).spans,key=lambda r:r[2]):
            if t!='article' or 'card' not in a.get('class','').split(): continue
            question,original=card_content(text[s:e])
            normalized=re.sub(r'\s+',' ',question).strip()
            dom=Builder();dom.feed(question)
            assets=[]
            for node in dom.root.find_all(lambda n:n.tag=='img' and 'src' in n.attrs):
                src=node.attrs['src'];url=urlsplit(src)
                if url.scheme or url.netloc:continue
                asset=(review.parent/unquote(url.path)).resolve()
                if not asset.is_file():raise ValueError(f'{date}: manifest question image missing: {src}')
                assets.append((src,hashlib.sha256(asset.read_bytes()).hexdigest()))
            if assets:normalized+='\n'+json.dumps(assets,ensure_ascii=False,sort_keys=True)
            cards.append(dict(id=a.get('id'),source=a.get('data-source'),source_kind=a.get('data-source-kind','past-exam'),statement_html=question,original_html=original,content_sha256=digest(normalized)))
        expected=[(q['id'],q['source'],q.get('source_kind','past-exam')) for q in m['problems']]
        if [(q['id'],q['source'],q['source_kind']) for q in cards]!=expected:
            raise ValueError(f'{date}: manifest/card mismatch')
        if len({q['id'] for q in cards})!=len(cards): raise ValueError(f'{date}: manifest duplicate ID')
        rows.append(dict(range=date,review_path=str(review),manifest_path=str(manifest),source_sha256=source_digest(review),manifest_sha256=digest(manifest.read_text(encoding='utf-8')),cards=cards))
    return rows
