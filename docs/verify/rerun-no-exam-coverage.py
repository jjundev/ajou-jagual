"""Recheck current scope mappings, preserved questions and published derivatives."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys

DISCLOSURE='<p><strong>후속 수업 보충:</strong> S1 p21의 최대값 알고리즘은 0914 수업에서 분석했어요. 이 문항은 보존하되 0907 핵심 범위의 평가 문항으로 세지 않아요.</p>'

def verify(repo):
    sys.path.insert(0,str(repo/'.agents/skills/ds-review-pack/scripts'))
    from review_inventory import collect_reviews
    from review_audit import audit_reviews
    from update_review import extract_cards
    from review_input import read_review
    from lecture_sources import validate_lecture_source
    evidence=repo/'docs/verify/no-exam-coverage-20261017'
    baseline=json.loads((evidence/'baseline.json').read_text(encoding='utf-8'))
    audit=audit_reviews(repo,baseline=baseline)
    assert audit['status']=='pass',audit
    rows=collect_reviews(repo);cards=[c for r in rows for c in r['cards']]
    assert len(rows)==10 and len(cards)==88
    assert sum(c['source_kind']=='lecture-code' for c in cards)==47
    assert sum(c['source_kind']=='textbook' for c in cards)==24
    raw={(r['range'],q['id']):q['raw'] for r in rows for q in extract_cards(read_review(r['review_path']))}
    preserved=json.loads((evidence/'all-preserved.json').read_text(encoding='utf-8'))
    assert len(preserved)==71
    for q in preserved:
        actual=raw[q['range'],q['id']]
        if q['range']=='0907' and q['id']=='p4':actual=actual.replace(DISCLOSURE,'')
        assert hashlib.sha256(actual.encode()).hexdigest()==q['raw_sha256'],q
    goals=0
    for row in rows:
        m=json.loads(Path(row['manifest_path']).read_text(encoding='utf-8'))
        for q in m['problems']:
            if q.get('source_kind')=='lecture-code':assert not validate_lecture_source(repo,q,m['sessions'])
        if row['range'] not in ['0907','0921','0928','1001','1005','1008']:continue
        selection=json.loads(Path(row['manifest_path']).with_name('selection.json').read_text(encoding='utf-8'))
        valid={q['id'] for q in m['problems'] if q.get('scope')!='retained-supplement'}
        assert selection['coverage_review']['status']=='pass'
        assert all(q['questions'] and set(q['questions'])<=valid for q in selection['coverage'])
        goals+=len(selection['coverage'])
    assert goals==62
    spec=importlib.util.spec_from_file_location('artifact_integrity',repo/'docs/verify/rerun-review-overhaul.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.verify(repo)
    subprocess.run([sys.executable,str(evidence/'verify_new.py')],check=True)
    return dict(status='pass',pack_count=10,question_count=88,exams=17,lecture=47,textbook=24,
                added=17,preserved=71,core_goals=62,scope='current mappings, source/evidence hashes and derivative integrity; saved actual reviews, no new visual review')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--output',type=Path);ap.add_argument('--kind',default='integrity')
    args=ap.parse_args()
    try:result=verify(args.repo.resolve())
    except (OSError,ValueError,AssertionError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(1)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))
