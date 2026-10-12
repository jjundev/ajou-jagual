"""Canonical content contracts; review hashes bind current source/model/SVG bytes."""
from pathlib import Path
import hashlib,json
from jsonschema import Draft202012Validator
from source import resolve_local,file_sha256
Bank=Inventory=AssetModel=ChapterPart=dict
SCHEMA=json.loads((Path(__file__).resolve().parents[1]/'question-bank.schema.json').read_text())
def canonical_digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def validate_structure(bank):
    return [f"{'/'.join(map(str,e.path))}: {e.message}" for e in Draft202012Validator(SCHEMA).iter_errors(bank)]
def validate_chapter_part(part):
    schema=dict(SCHEMA);schema['$ref']='#/$defs/chapterPart'
    for key in ('type','properties','required','additionalProperties'):schema.pop(key,None)
    return [str(e.message) for e in Draft202012Validator(schema).iter_errors(part)]
def blocks(content):
    for b in content:
        yield b
        if b['type']=='subquestions':
            for item in b['items']:yield from blocks(item['content'])
def question_blocks(q):
    yield from blocks(q['content'])
    for o in q['options']:yield from blocks(o['content'])
def current_sources(bank,refs,book_dir):
    sources={s['id']:s for s in bank['sources']}
    return {sid:file_sha256(resolve_local(book_dir,sources[sid]['path'])) for sid in sorted({r['source_id'] for r in refs})}
def page_payload(page,sources,book_dir):
    s=next(s for s in sources if s['id']==page['source_id'])
    return {'page':{k:v for k,v in page.items() if k!='review'},'source_sha256':file_sha256(resolve_local(book_dir,s['path']))}
def asset_payload(bank,asset,book_dir,models):
    return {'asset':{k:v for k,v in asset.items() if k!='review'},'sources':current_sources(bank,asset['source_refs'],book_dir),'svg_sha256':file_sha256(resolve_local(book_dir,asset['path'])),'model':next(m for m in models['models'] if m['id']==asset['model_id'])}
def question_payload(bank,q,book_dir,inventory,models):
    refs=q['source_refs']+(q['printed_answer']['source_refs'] if q['printed_answer'] else [])
    asset_ids={b['asset_id'] for b in question_blocks(q) if b['type'] in ('figure','table')}
    return {'question':{k:v for k,v in q.items() if k!='review'},'sources':current_sources(bank,refs,book_dir),'pages':[p for p in inventory['pages'] if any(p['source_id']==r['source_id'] and p['pdf_page']==r['pdf_page'] for r in refs)],'assets':[asset_payload(bank,a,book_dir,models) for a in bank['assets'] if a['id'] in asset_ids]}

def bank_counts(bank,inventory,models):
    return {'chapters':len(bank['chapters']),'sources':len(bank['sources']),'pages':len(inventory['pages']),'questions':len(bank['questions']),'assets':len(bank['assets']),'options':sum(len(q['options']) for q in bank['questions']),'subquestions':sum(len(b['items']) for q in bank['questions'] for b in question_blocks(q) if b['type']=='subquestions'),'figures':sum(m['kind']!='table' for m in models['models']),'tables':sum(m['kind']=='table' for m in models['models'])}
