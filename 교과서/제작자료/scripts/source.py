"""Source-preserving inventory and review-only page rendering."""
from pathlib import Path
import hashlib, json, re, shutil, unicodedata
import pymupdf

def file_sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def resolve_local(base, relative):
    base=Path(base).resolve(); rel=Path(relative)
    if rel.is_absolute() or '..' in rel.parts: raise ValueError('path escape')
    current=base
    for part in rel.parts:
        hits=[p for p in current.iterdir() if unicodedata.normalize('NFC',p.name)==unicodedata.normalize('NFC',part)]
        if len(hits)!=1: raise ValueError(f'missing or ambiguous path: {relative}')
        current=hits[0]
        if current.is_symlink():raise ValueError('symlink path')
        if not current.resolve().is_relative_to(base): raise ValueError('symlink escape')
    return current

def inspect_sources(origin):
    entries={}
    for p in Path(origin).glob('*.pdf'):
        if p.is_symlink(): raise ValueError('symlink source')
        match=re.match(r'^(\d{2})_',p.name)
        if not match: raise ValueError(f'unknown source {p.name}')
        n=int(match[1])
        if n in entries: raise ValueError('duplicate chapter')
        with pymupdf.open(p) as doc:
            entries[n]={'id':f's{n:02}','path':'origin/'+p.name,'sha256':file_sha256(p),'page_count':len(doc)}
    if set(entries)!=set(range(1,15)): raise ValueError('expected chapters 1–14')
    return [entries[i] for i in range(1,15)]

def prepare_run(origin,run):
    run=Path(run);package=run/'package'; (package/'origin').mkdir(parents=True,exist_ok=True)
    support=package/'제작자료';support.mkdir(exist_ok=True); pages=run/'pages';pages.mkdir(exist_ok=True)
    sources=inspect_sources(origin); inventory={'schema_version':1,'sources':sources,'pages':[]}
    for source in sources:
        p=Path(origin)/Path(source['path']).name; shutil.copy2(p,package/source['path'])
        with pymupdf.open(p) as doc:
            for i,page in enumerate(doc,1):
                page.get_pixmap(dpi=200).save(pages/f"ch{source['id'][1:]}-p{i:02}.png")
                inventory['pages'].append({'source_id':source['id'],'pdf_page':i,'book_page':None,'occurrences':[], 'review':{'status':'pending','payload_sha256':None,'notes':[]}})
    (support/'inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
    return package
