"""Verify the restored exams and every published derivative without fabricating review."""
from pathlib import Path
import argparse
import importlib.util
import json
import subprocess
import sys

def verify(repo):
    if (repo/'docs/verify/2026-10-17-no-exam-coverage.json').exists():
        spec=importlib.util.spec_from_file_location('current_coverage',repo/'docs/verify/rerun-no-exam-coverage.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result=module.verify(repo)
        subprocess.run([sys.executable,str(repo/'docs/verify/exam-restore-20261017/verify_restored.py')],check=True)
        return result
    notes=repo/'복습노트'
    if not (any(notes.glob('*/복습문제_*.html')) or any(notes.glob('*/.pack/자료_복습팩/복습문제_*.json'))):
        raise ValueError('zero question inputs')
    sys.path.insert(0,str(repo/'.agents/skills/ds-review-pack/scripts'))
    from review_inventory import collect_reviews
    from review_audit import audit_reviews
    from update_review import extract_cards
    from review_input import read_review
    evidence=repo/'docs/verify/exam-restore-20261017'
    required=json.loads((evidence/'required-exams.json').read_text())
    baseline=json.loads((evidence/'baseline.json').read_text(encoding='utf-8'))
    rows=collect_reviews(repo)
    result=audit_reviews(repo,baseline=baseline,required_exams=required)
    assert result['status']=='pass',result
    cards=[q for row in rows for q in row['cards']]
    assert len(rows)==10 and len(cards)==71
    assert sum(q['source_kind']=='lecture-code' for q in cards)==30
    assert sum(q['source'].startswith('textbook-') for q in cards)==24
    assert sorted(q['source'] for q in cards if q['source'] in required)==required
    preserved=0
    for row in rows:
        path=Path(row['review_path']);relative=path.relative_to(repo).as_posix()
        previous=subprocess.check_output(['git','show','c3a1e8f:'+relative],cwd=repo).decode('utf-8')
        current={q['source']:q['raw'] for q in extract_cards(read_review(path))}
        for q in extract_cards(previous):
            assert current[q['source']]==q['raw'],('existing card changed',row['range'],q['source'])
            preserved+=1
    assert preserved==62
    spec=importlib.util.spec_from_file_location('previous_integrity',repo/'docs/verify/rerun-review-overhaul.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.verify(repo)
    subprocess.run([sys.executable,str(evidence/'verify_restored.py')],check=True)
    return dict(status='pass',pack_count=10,question_count=71,questions=71,input_location='published sources and fragments',exams=17,lecture=30,textbook=24,preserved_raw_cards=62,restored=9,scope='current source, retention, evidence, explanation and PDF integrity; saved reviews, no fresh visual review')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--kind',default='integrity')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        result=verify(args.repo.resolve())
        if args.output:
            args.output.mkdir(parents=True,exist_ok=True)
            (args.output/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False))
    except (AssertionError,ValueError,OSError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(1)
