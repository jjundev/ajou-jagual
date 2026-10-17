import json
from _util import MINI_RUN
from update_review import build_revision,revision_hash,extract_cards
from assemble import build_review

def test_revision_replaces_removes_and_reorders_cards():
    m=json.loads((MINI_RUN/'manifest.json').read_text(encoding='utf-8'))
    old=build_review(m,MINI_RUN)
    cards={c['id']:c['raw'] for c in extract_cards(old)}
    revised=build_revision(old,manifest=m,cards=cards)
    assert build_revision(revised,manifest=m,cards=cards)==revised
    assert [c['source'] for c in extract_cards(revised)]==[q['source'] for q in m['problems']]
    assert 'data-revision=' in revised
    assert "od-review-solved:" in revised and "dataset.revision" in revised
    changed=dict(cards);key=next(iter(changed));changed[key]+=' changed'
    assert revision_hash(m,cards)!=revision_hash(m,changed)

def test_revision_preserves_svg_title_without_overlapping_main_edits():
    m=json.loads((MINI_RUN/'manifest.json').read_text(encoding='utf-8'))
    old=build_review(m,MINI_RUN)
    old=old.replace('</article>','<svg><title>Diagram title</title></svg></article>',1)
    m['review_title']='A much longer replacement title than the nested SVG title'
    cards={c['id']:c['raw'] for c in extract_cards(old)}
    revised=build_revision(old,manifest=m,cards=cards)
    assert '<title>Diagram title</title>' in revised
    assert len(extract_cards(revised))==len(cards)
    assert build_revision(revised,manifest=m,cards=cards)==revised
    assert revised.count('</main>')==1
    assert '</main>\n  <footer>' in revised
