"""Recheck current artifacts and saved independent evidence; never invent a fresh review."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(repo):
    notes=repo/'복습노트'
    if not notes.is_dir() or not (any(notes.glob('*/복습문제_*.html'))
                              or any(notes.glob('*/.pack/자료_복습팩/복습문제_*.json'))):
        raise ValueError('zero question inputs')
    sys.path.insert(0,str(repo/'.agents/skills/ds-review-pack/scripts'))
    from review_inventory import collect_reviews
    from review_audit import audit_reviews
    from review_input import read_archive, source_file, source_digest
    rows=collect_reviews(repo);audit=audit_reviews(repo)
    if audit['status']!='pass':raise ValueError('global review audit failed')
    latest=repo/'docs/verify/2026-10-17-no-exam-coverage.json'
    if not latest.exists():latest=repo/'docs/verify/2026-10-17-exam-restore.json'
    report=json.loads((latest if latest.exists() else repo/'docs/verify/2026-10-17-review-question-overhaul.json').read_text(encoding='utf-8'))
    if len(rows)!=len(report['packs']):raise ValueError('pack set changed')
    for row in rows:
        source=source_file(row['review_path'])
        observed=source_digest(source)
        previous=read_archive(source).get('html_sha256') if source.suffix=='.json' else observed
        root=Path(row['review_path']).parent
        m=json.loads(Path(row['manifest_path']).read_text(encoding='utf-8'))
        s=json.loads((Path(row['manifest_path']).parent/'selection.json').read_text(encoding='utf-8'))
        if len(row['cards'])!=len(s['selected']):raise ValueError('selected question count changed')
        for card,q in zip(row['cards'],s['selected']):
            v=q['verification']
            if card['id']!=q['id'] or card['source']!=q['source'] or v['result']!='pass' or v['content_sha256']!=card['content_sha256']:
                raise ValueError('question or independent verification changed: '+row['range']+'/'+card['id'])
            for evidence in q['evidence']:
                if sha(repo/evidence['path'])!=evidence['sha256']:raise ValueError('independent evidence changed')
        data=root/'.pack'/f'자료_문제설명_{m["range"]}_{m["slug"]}'
        em=json.loads((data/'manifest.json').read_text(encoding='utf-8'))
        ev=json.loads((data/'validation.json').read_text(encoding='utf-8'))
        if em['source_sha256'] not in (observed,previous) or ev['input_hash']!=em['input_hash']:
            raise ValueError('explanation source or input changed')
        for key in ('source_visual','content','independent','browser'):
            if ev[key]['status']!='pass':raise ValueError('unapproved explanation '+key)
        for name,digest in em['files'].items():
            if sha(root/name)!=digest:raise ValueError('explanation artifact changed: '+name)
        pdf=json.loads((root/'.pack/자료_PDF/pdf-validation.json').read_text(encoding='utf-8'))
        if pdf['source_sha256'] not in (observed,previous) or pdf['status']!='published':raise ValueError('PDF source/stage changed')
        for name in pdf['pdfs']:
            if sha(root/name)!=pdf['artifact_hashes'][name]:raise ValueError('PDF artifact changed')
    for name,digest in report['protected_files'].items():
        if sha(repo/name)!=digest:raise ValueError('protected file changed: '+name)
    return dict(status='pass',pack_count=len(rows),question_count=sum(len(r['cards']) for r in rows),input_location='published sources and fragments',scope='current artifact integrity and saved independent verification; no fresh human review')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--kind',default='integrity');ap.add_argument('--output',type=Path)
    a=ap.parse_args()
    try:result=verify(a.repo.resolve())
    except (OSError,ValueError,KeyError) as exc:print(str(exc));return 1
    if a.output:
        a.output.mkdir(parents=True,exist_ok=True)
        (a.output/'summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
