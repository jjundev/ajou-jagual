"""Validate original bytes, inventory completeness, safe SVGs and review bindings."""
from pathlib import Path
import argparse,json
from collections import Counter
from model import validate_structure,blocks,question_blocks,canonical_digest,question_payload,asset_payload,page_payload
from source import resolve_local,file_sha256
from assets import validate_model,validate_svg,render_svg
from bank import load_bank

def validate_bank(bank,book_dir,inventory,models,*,complete=False):
    errors=validate_structure(bank)
    if errors:return errors
    def error(locator,text):errors.append(f'{locator}: {text}')
    def index(items,kind):
        ids=[x['id'] for x in items]
        if len(ids)!=len(set(ids)):error(kind,'duplicate IDs')
        return {x['id']:x for x in items}
    sources=index(bank['sources'],'sources');chapters=index(bank['chapters'],'chapters');questions=index(bank['questions'],'questions');assets=index(bank['assets'],'assets');modelmap=index(models['models'],'models')
    def source_refs(refs,locator):
        for r in refs:
            s=sources.get(r['source_id'])
            if not s or not 1<=r['pdf_page']<=s['page_count']:error(locator,'unknown source/page')
            elif r.get('book_page')!=page_map.get((r['source_id'],r['pdf_page']),{}).get('book_page'):error(locator,'book page differs from inventory')
    page_map={}
    for page in inventory['pages']:
        key=(page['source_id'],page['pdf_page'])
        if key in page_map:error(str(key),'duplicate inventory page')
        page_map[key]=page
    if inventory['sources']!=bank['sources']:error('inventory','source inventory differs')
    expected={(s['id'],p) for s in sources.values() for p in range(1,s['page_count']+1)}
    if set(page_map)!=expected:error('inventory','missing or extra source pages')
    for sid,s in sources.items():
        try:
            if file_sha256(resolve_local(book_dir,s['path']))!=s['sha256']:error(sid,'source byte hash changed')
        except (ValueError,OSError):error(sid,'missing or unsafe source path')
    for cid,c in chapters.items():
        if c['id']!=f"ch{c['number']:02}" or any(s not in sources for s in c['source_ids']):error(cid,'invalid chapter reference')
    def reviewed(obj,payload,locator):
        review=obj['review']
        if complete and review['status']!='verified':error(locator,'review not verified')
        if review['status']=='verified':
            if not review['notes']:error(locator,'review notes absent')
            try:
                if review['payload_sha256']!=canonical_digest(payload()):error(locator,'stale review payload')
            except (ValueError,StopIteration,OSError,KeyError):error(locator,'review dependency missing')
    for page in inventory['pages']:
        reviewed(page,lambda p=page:page_payload(p,bank['sources'],book_dir),f"page:{page['source_id']}:{page['pdf_page']}")
    used=set()
    for aid,a in assets.items():
        source_refs(a['source_refs'],aid);model=modelmap.get(a['model_id'])
        if not model:error(aid,'missing model');continue
        for e in validate_model(model):error(aid,e)
        try:
            path=resolve_local(book_dir,a['path']);svg=path.read_text()
            if not a['path'].startswith('assets/') or path.suffix!='.svg':error(aid,'invalid asset path')
            if file_sha256(path)!=a['sha256']:error(aid,'SVG byte hash changed')
            for e in validate_svg(svg):error(aid,e)
            if render_svg(model,a['alt'])!=svg:error(aid,'SVG differs from structural model')
        except (ValueError,OSError,KeyError):error(aid,'SVG or model unavailable')
        reviewed(a,lambda a=a:asset_payload(bank,a,book_dir,models),aid)
    if set(modelmap)!={a['model_id'] for a in assets.values()}:error('models','missing or unused models')
    for qid,q in questions.items():
        if q['chapter_id'] not in chapters:error(qid,'unknown chapter')
        if qid!=f"{q['chapter_id']}-q{int(q['number']):02}":error(qid,'ID/number mismatch')
        source_refs(q['source_refs'],qid)
        if q['printed_answer']:source_refs(q['printed_answer']['source_refs'],qid+'/printed_answer')
        qblocks=list(question_blocks(q));qassets={b['asset_id'] for b in qblocks if b['type'] in ('figure','table')};used.update(qassets)
        if not qassets<=set(assets):error(qid,'unknown asset reference')
        for block in qblocks:
            if block['type'] in ('figure','table') and block['asset_id'] in assets:
                m=modelmap.get(assets[block['asset_id']]['model_id'])
                if m and (block['type']=='table')!=(m['kind']=='table'):error(qid,'block/model kind mismatch')
        qsubs=[item['label'] for b in qblocks if b['type']=='subquestions' for item in b['items']]
        labels=[o['label'] for o in q['options']]
        if len(labels)!=len(set(labels)):error(qid,'duplicate options')
        occurrences=[]
        for page in inventory['pages']:
            for o in page['occurrences']:
                if o['question_id']==qid:occurrences.append((page,o))
        if sum(o['role']=='start' for p,o in occurrences)!=1:error(qid,'expected one start occurrence')
        observed_pages={(p['source_id'],p['pdf_page']) for p,o in occurrences};qpages={(r['source_id'],r['pdf_page']) for r in q['source_refs']}
        if observed_pages!=qpages:error(qid,'missing continuation or source page')
        if any(o['number']!=q['number'] for p,o in occurrences):error(qid,'inventory number differs')
        observed_options=[label for p,o in occurrences for label in o['option_labels']]
        observed_subs=[label for p,o in occurrences for label in o['subquestion_labels']]
        if observed_options!=labels:error(qid,'option labels/order differ from inventory')
        if observed_subs!=qsubs:error(qid,'subquestion labels/order differ from inventory')
        observed_assets={aid for p,o in occurrences for aid in o['asset_ids']}
        if observed_assets!=qassets:error(qid,'asset set differs from inventory')
        for p,o in occurrences:
            for aid in o['asset_ids']:
                if aid in assets and not any(r['source_id']==p['source_id'] and r['pdf_page']==p['pdf_page'] for r in assets[aid]['source_refs']):error(qid,'asset source page differs')
        if complete and any(i['blocking'] or i['kind'] in ('unreadable','figure-incomplete') for i in q['issues']):error(qid,'blocking issue')
        reviewed(q,lambda q=q:question_payload(bank,q,book_dir,inventory,models),qid)
    if used!=set(assets):error('assets','unreferenced assets')
    for p in inventory['pages']:
        for o in p['occurrences']:
            if o['question_id'] not in questions:error('inventory','unknown question occurrence')
    if complete:
        if {c['number'] for c in chapters.values()}!=set(range(1,15)) or len(sources)!=14 or len(page_map)!=44:error('complete','expected 14 chapters, 14 sources, 44 pages')
        for c in chapters:
            nums=[int(q['number']) for q in questions.values() if q['chapter_id']==c]
            if not nums or sorted(nums)!=list(range(1,max(nums)+1)):error(c,'missing or duplicate original number')
    return errors

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('bank',type=Path);parser.add_argument('--complete',action='store_true');args=parser.parse_args(argv)
    book=args.bank.resolve();support=book/'제작자료';bank=load_bank(book);inv=json.loads((support/'inventory.json').read_text());models=json.loads((support/'asset-models.json').read_text())
    errors=validate_bank(bank,book,inv,models,complete=args.complete)
    if errors:print('\n'.join(errors));return 1
    print(f"PASS chapters={len(bank['chapters'])} sources={len(bank['sources'])} pages={len(inv['pages'])} questions={len(bank['questions'])} assets={len(bank['assets'])}");return 0
if __name__=='__main__':raise SystemExit(main())
