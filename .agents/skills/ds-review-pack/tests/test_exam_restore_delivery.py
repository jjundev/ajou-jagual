"""The restored corpus must keep distinct exams and all previously retained cards."""
import json
import os
from pathlib import Path
from _util import REPO
from review_source import read_review
from review_inventory import collect_reviews
from review_audit import audit_reviews

def current_rows():
    overlay=os.environ.get('DS_REVIEW_TEST_OVERLAY')
    return collect_reviews(REPO,overlays=json.loads(Path(overlay).read_text(encoding='utf-8')) if overlay else None)

def test_all_distinct_exams_and_lecture_textbook_cards_retained():
    rows=current_rows();cards=[q for row in rows for q in row['cards']]
    required=json.loads((REPO/'docs/verify/exam-restore-20261017/required-exams.json').read_text())
    assert len(cards)==71
    assert sum(q['source_kind']=='lecture-code' for q in cards)==30
    assert sum(q['source'].startswith('textbook-') for q in cards)==24
    assert sorted(q['source'] for q in cards if q['source'] in required)==required
    baseline=json.loads((REPO/'docs/verify/exam-restore-20261017/baseline.json').read_text(encoding='utf-8'))
    current={q['source']:q for q in cards}
    for row in baseline:
        for q in row['cards']:
            assert current[q['source']]['id']==q['id']
            assert current[q['source']]['content_sha256']==q['content_sha256']

def test_restored_original_loop_has_consistent_count_examples():
    row=next(r for r in current_rows() if r['range']=='0914')
    from update_review import extract_cards
    card=next(c for c in extract_cards(read_review(Path(row['review_path']))) if c['source']=='unk-final-ltk-q1')
    raw=card['raw']
    assert '29 + 58 = 87' in raw
    assert 'i = 2 → 58번' in raw
    assert '바꾼 변형' not in raw
    assert 'k&lt;30' in raw and '29n(n-1)/2' in raw
