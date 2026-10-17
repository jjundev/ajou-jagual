import json
from _util import SCRIPTS
from test_review_inventory import make_pack
from review_audit import audit_reviews

def exam_bank(repo, aliases=None):
    path=repo/'from_the_past/기출/문제은행.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'problems':[{'id':s,'duplicate_of':a} for s,a in (aliases or {'exam-a':None,'exam-b':None}).items()]}))

def test_distinct_exams_survive_same_algorithm_even_duplicate_decision(tmp_path):
    exam_bank(tmp_path)
    make_pack(tmp_path,'0914','exam-a')
    other=make_pack(tmp_path,'0917','exam-b')
    other.write_text(other.read_text().replace('x=1','y=2'))
    report=audit_reviews(tmp_path)
    assert report['status']=='pass' and not report['candidates']
    assert report['retained_similar_exams']

def test_exact_reprint_and_bank_alias_still_block(tmp_path):
    exam_bank(tmp_path,{'exam-a':None,'exam-b':'exam-a'})
    make_pack(tmp_path,'0914','exam-a')
    other=make_pack(tmp_path,'0917','exam-b')
    other.write_text(other.read_text().replace('x=1','y=2'))
    assert audit_reviews(tmp_path)['blocking']

def test_baseline_detects_lost_distinct_exam(tmp_path):
    from review_inventory import collect_reviews
    exam_bank(tmp_path)
    make_pack(tmp_path,'0914','exam-a')
    other=make_pack(tmp_path,'0917','exam-b')
    other.write_text(other.read_text().replace('x=1','y=2'))
    before=collect_reviews(tmp_path)
    replacement=make_pack(tmp_path/'stage','0917','lecture-new')
    replacement.write_text(replacement.read_text().replace('x=1','printf("new")'))
    report=audit_reviews(tmp_path,overlays={'0917':replacement},baseline=before)
    assert report['status']=='fail'
    assert any(x.get('missing_exam')=='exam-b' for x in report['blocking'])

def test_required_exam_list_is_enforced(tmp_path):
    exam_bank(tmp_path)
    make_pack(tmp_path,'0914','exam-a')
    report=audit_reviews(tmp_path,required_exams=['exam-a','exam-b'])
    assert any(x.get('missing_exam')=='exam-b' for x in report['blocking'])

def test_saved_required_exams_apply_without_cli_flags(tmp_path):
    exam_bank(tmp_path)
    review=make_pack(tmp_path,'0914','exam-a')
    (review.parent/'.pack/자료_복습팩/selection.json').write_text(json.dumps({'required_exam_sources':['exam-a','exam-b']}))
    report=audit_reviews(tmp_path)
    assert any(x.get('missing_exam')=='exam-b' for x in report['blocking'])

def test_global_sources_and_variants_blocked(tmp_path):
    make_pack(tmp_path,'0914');make_pack(tmp_path,'0917')
    assert audit_reviews(tmp_path)['blocking']

def test_cross_source_numeric_and_identifier_candidate(tmp_path):
    make_pack(tmp_path,'0914','one');p=make_pack(tmp_path,'0917','two')
    p.write_text(p.read_text().replace('x=1','y=2'))
    report=audit_reviews(tmp_path)
    assert report['candidates']
    pair=report['candidates'][0]
    decision={**pair,'decision':'distinct','reason':'Different requested skills','evidence':['manual comparison']}
    assert audit_reviews(tmp_path,decisions=[decision])['status']=='pass'
    p.write_text(p.read_text().replace('y=2','z=3'))
    assert audit_reviews(tmp_path,decisions=[decision])['status']=='fail'

def test_overlay_keeps_unmodified_packs_in_scope(tmp_path):
    make_pack(tmp_path,'0914','one');make_pack(tmp_path,'0917','two')
    overlay=make_pack(tmp_path/'stage','0917','one')
    assert audit_reviews(tmp_path,overlays={'0917':overlay})['blocking']

def test_nfd_root_and_manifest_duplicates_are_not_silently_empty(tmp_path):
    import unicodedata
    make_pack(tmp_path,'0914');make_pack(tmp_path,'0917')
    for root in (tmp_path/'복습노트').iterdir():
        data=root/'.pack/자료_복습팩';data.rename(data.with_name(unicodedata.normalize('NFD',data.name)))
    notes=tmp_path/'복습노트';notes.rename(notes.with_name(unicodedata.normalize('NFD',notes.name)))
    report=audit_reviews(tmp_path)
    assert len(report['inputs'])==2 and report['status']=='fail' and report['blocking']
    assert audit_reviews(tmp_path/'empty')['status']=='fail'

def test_code_clone_with_reworded_prompt_still_requires_review(tmp_path):
    a=make_pack(tmp_path,'0914','one');b=make_pack(tmp_path,'0917','two')
    a.write_text(a.read_text().replace('Q<pre>x=1;</pre>','다음 코드의 출력을 쓰세요.<pre>int x=1; printf("%d",x+1);</pre>'))
    b.write_text(b.read_text().replace('Q<pre>x=1;</pre>','다음 코드를 실행한 결과를 구하세요.<pre>int y=2; printf("%d",y+2);</pre>'))
    assert audit_reviews(tmp_path)['candidates']

def test_different_diagrams_are_reviewable_not_exact_duplicates(tmp_path):
    a=make_pack(tmp_path,'0914','one');b=make_pack(tmp_path,'0917','two')
    for path,shape in [(a,'<circle r="1"/>'),(b,'<rect width="2" height="3"/>')]:
        path.write_text(path.read_text().replace('Q<pre>x=1;</pre>','그림의 넓이를 구하세요.<img src="figure.svg">'))
        (path.parent/'figure.svg').write_text('<svg>'+shape+'</svg>')
    report=audit_reviews(tmp_path)
    assert report['blocking']==[] and report['candidates']
    decision={**report['candidates'][0],'decision':'distinct','reason':'circle area versus rectangle area','evidence':['different figure bytes inspected']}
    assert audit_reviews(tmp_path,decisions=[decision])['status']=='pass'
