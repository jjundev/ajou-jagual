import hashlib,json
from pathlib import Path
from _util import REPO
from review_inventory import collect_reviews
from review_audit import audit_reviews,POLICY_VERSION
from lecture_sources import validate_lecture_source

def test_all_packs_current_revision_and_complete_coverage():
    rows=collect_reviews(REPO)
    assert len(rows)==10
    for row in rows:
        data=Path(row['manifest_path']).parent
        m=json.loads((data/'manifest.json').read_text(encoding='utf-8'))
        s=json.loads((data/'selection.json').read_text(encoding='utf-8'))
        assert s['mode']=='revision'
        assert s['policy_version']==POLICY_VERSION
        assert [q['id'] for q in s['selected']]==[q['id'] for q in m['problems']]
        assert s['coverage']
        assert all(q['verification']['result']=='pass' for q in s['selected'])
        for q in m['problems']:
            if q.get('source_kind')=='lecture-code':assert validate_lecture_source(REPO,q,m['sessions'])==[]
    assert audit_reviews(REPO)['status']=='pass'

def test_every_changed_card_has_mapping_and_verification():
    mappings=[]
    for row in collect_reviews(REPO):
        data=Path(row['manifest_path']).parent
        s=json.loads((data/'selection.json').read_text(encoding='utf-8'))
        mappings.extend(s['replacements'])
        assert all(q['verification'].get('evidence') for q in s['selected'])
    assert len(mappings)==72
    assert all(r['old_content_sha256'] and r['reason'] for r in mappings)
