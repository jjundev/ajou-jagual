import json,copy,shutil
from pathlib import Path
import pytest
from model import canonical_digest,question_payload,asset_payload,page_payload
from validate import validate_bank

@pytest.fixture
def candidate(tmp_path):
    package=Path(__file__).parents[1].parent
    for name in ['origin','assets']:shutil.copytree(package/name,tmp_path/name)
    bank=__import__('publish').load_bank(package);inv=json.loads((package/'제작자료/inventory.json').read_text());models=json.loads((package/'제작자료/asset-models.json').read_text())
    for page in inv['pages']:
        page['review']={'status':'verified','payload_sha256':canonical_digest(page_payload(page,bank['sources'],tmp_path)),'notes':[{'locator':'test','text':'synthetic test seal'}]}
    for asset in bank['assets']:
        asset['review']={'status':'verified','payload_sha256':canonical_digest(asset_payload(bank,asset,tmp_path,models)),'notes':[{'locator':'test','text':'synthetic test seal'}]}
    for q in bank['questions']:
        q['review']={'status':'verified','payload_sha256':canonical_digest(question_payload(bank,q,tmp_path,inv,models)),'notes':[{'locator':'test','text':'synthetic test seal'}]}
    return bank,inv,models,tmp_path

def test_complete_inventory(candidate):
    b,i,m,p=candidate;assert validate_bank(b,p,i,m,complete=True)==[]

@pytest.mark.parametrize('what',['source','model','svg','question','page'])
def test_dependency_changes_invalidate_review(candidate,what):
    b,i,m,p=candidate
    if what=='source':(p/b['sources'][0]['path']).write_bytes(b'changed')
    elif what=='model':m['models'][0]['layout']['height']+=1
    elif what=='svg':(p/b['assets'][0]['path']).write_text('<svg/>')
    elif what=='page':i['pages'][0]['occurrences'].pop()
    else:b['questions'][0]['content'][0]['text']+=' changed'
    assert validate_bank(b,p,i,m,complete=True)

def test_missing_continuation(candidate):
    b,i,m,p=candidate
    pg=next(pg for pg in i['pages'] if any(o['role']=='continuation' for o in pg['occurrences']))
    pg['occurrences']=[o for o in pg['occurrences'] if o['role']!='continuation']
    assert validate_bank(b,p,i,m,complete=True)

def test_unknown_duplicate_pending_and_blocking(candidate):
    b,i,m,p=candidate
    b['questions'].append(copy.deepcopy(b['questions'][0]));assert validate_bank(b,p,i,m)
    b['questions'].pop();b['questions'][0]['source_refs'][0]['source_id']='unknown';assert validate_bank(b,p,i,m)
    b['questions'][0]['source_refs'][0]['source_id']='s01';b['questions'][0]['review']['status']='pending';assert validate_bank(b,p,i,m,complete=True)
    b['questions'][0]['issues'].append({'kind':'unreadable','description':'blocked','source_refs':b['questions'][0]['source_refs'],'blocking':True});assert validate_bank(b,p,i,m,complete=True)

def test_figure_table_kind_mismatch(candidate):
    b,i,m,p=candidate
    q=next(q for q in b['questions'] if q['id']=='ch02-q21');q['content'][1]['type']='table'
    assert any('kind' in e for e in validate_bank(b,p,i,m))

def test_literal_record_text_and_bottom_link():
    package=Path(__file__).parents[1].parent;model=next(m for m in json.loads((package/'제작자료/asset-models.json').read_text())['models'] if m['id']=='ch06-q14-records')
    texts=[p.get('text','') for p in model['data']['primitives']];assert any('Heigh: 1.7'==t for t in texts);assert not any('Height:' in t for t in texts)
    # Four record nodes have horizontal link-field divider, below all data text.
    dividers=[p for p in model['data']['primitives'] if p['tag']=='line' and p['attrs'].get('y1')==p['attrs'].get('y2')==185]
    assert len(dividers)==4
