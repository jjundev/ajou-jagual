"""Global question reuse audit. Similarity suggests review; it never deletes cards."""
from pathlib import Path
from itertools import combinations
import argparse
import html
import json
import re
from review_inventory import collect_reviews
from pack_layout import normalized_child
from html2md import Builder

POLICY_VERSION='review-questions-2026-10-17'

def normalized(statement):
    text=html.unescape(re.sub(r'<[^>]+>',' ',statement))
    return re.sub(r'\s+',' ',text).strip()

def signature(statement):
    text=normalized(statement)
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|\b[A-Za-z_]\w*\b|\d+(?:\.\d+)?|[^\s]',text)
    identifiers={};reserved=set('if else for while return int double float char void sizeof struct NULL printf'.split())
    result=[]
    for token in tokens:
        if token[0].isdigit():token='#'
        elif re.fullmatch(r'[A-Za-z_]\w*',token) and token not in reserved:
            token=identifiers.setdefault(token,f'v{len(identifiers)}')
        result.append(token)
    return ' '.join(result)

def identity(date,card):
    return {key:value for key,value in [('range',date),('id',card['id']),('content_sha256',card['content_sha256'])]}

def code_signature(statement):
    dom=Builder();dom.feed(statement)
    code='\n'.join(n.text() for n in dom.root.find_all(lambda n:n.tag=='pre'))
    if not code:return None
    result=signature(html.escape(code))
    return result if len(result.split())>=8 else None

def audit_reviews(repo: Path, *, overlays=None, decisions=None, baseline=None, required_exams=None):
    report=dict(policy_version=POLICY_VERSION,inputs=[],blocking=[],candidates=[],decisions=[],retained_similar_exams=[],status='fail')
    try: rows=collect_reviews(repo,overlays=overlays)
    except (ValueError,OSError,KeyError) as exc:
        report['blocking'].append({'error':str(exc)});return report
    if not rows:
        report['blocking'].append({'error':'no live review packs found'});return report
    report['inputs']=[{k:v for k,v in row.items() if k!='cards'} for row in rows]
    bank=normalized_child(normalized_child(Path(repo)/'from_the_past','기출'),'문제은행.json')
    aliases={q['id']:q.get('duplicate_of') for q in json.loads(bank.read_text(encoding='utf-8'))['problems']} if bank.exists() else {}
    def canonical(source):
        seen=set()
        while aliases.get(source) and source not in seen:seen.add(source);source=aliases[source]
        return source
    allcards=[(row['range'],c) for row in rows for c in row['cards']]
    expected=set(required_exams or [])
    try:
        for row in rows:
            selection=Path(row['manifest_path']).with_name('selection.json')
            if selection.is_file():
                expected.update(json.loads(selection.read_text(encoding='utf-8')).get('required_exam_sources',[]))
    except (ValueError,OSError,TypeError) as exc:
        report['blocking'].append({'error':'invalid saved exam retention: '+str(exc)})
        return report
    if baseline is not None:
        expected.update(c['source'] for row in baseline for c in row['cards'] if c['source'] in aliases)
    present={canonical(c['source']) for _,c in allcards}
    for source in sorted(expected):
        if source not in aliases:
            report['blocking'].append({'error':'required exam not in bank','source':source})
        elif canonical(source) not in present:
            report['blocking'].append({'missing_exam':source,'reason':'distinct baseline exam must be retained'})
    for (da,a),(db,b) in combinations(allcards,2):
        pair={'left':identity(da,a),'right':identity(db,b)}
        if canonical(a['source'])==canonical(b['source']):
            report['blocking'].append({**pair,'reason':'canonical source reused'});continue
        if a['content_sha256']==b['content_sha256']:
            report['blocking'].append({**pair,'reason':'identical question'});continue
        same_statement=signature(a['statement_html'])==signature(b['statement_html'])
        left_code=code_signature(a['statement_html']);right_code=code_signature(b['statement_html'])
        if not same_statement and not (left_code and left_code==right_code):continue
        # Distinct real exams are retained even when their algorithms/skills match.
        # Source aliases and identical question content were already checked above.
        if a['source'] in aliases and b['source'] in aliases:
            report['retained_similar_exams'].append({**pair,'reason':'different exam originals retained'})
            continue
        match=next((d for d in decisions or [] if d.get('left')==pair['left'] and d.get('right')==pair['right'] and d.get('decision') in ('distinct','duplicate') and d.get('reason') and d.get('evidence')),None)
        if match:
            report['decisions'].append(match)
            if match['decision']=='duplicate':report['blocking'].append({**pair,'reason':match['reason']})
        else:report['candidates'].append(pair)
    report['status']='fail' if report['blocking'] or report['candidates'] else 'pass'
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',required=True);ap.add_argument('--overlay');ap.add_argument('--decisions');ap.add_argument('--baseline',help='Pre-edit collect_reviews JSON; require every distinct existing exam');ap.add_argument('--required-exams',help='JSON array of required bank question IDs');ap.add_argument('--out',required=True)
    a=ap.parse_args()
    report=audit_reviews(Path(a.repo),overlays=json.loads(Path(a.overlay).read_text(encoding='utf-8')) if a.overlay else None,decisions=json.loads(Path(a.decisions).read_text(encoding='utf-8')) if a.decisions else None,baseline=json.loads(Path(a.baseline).read_text(encoding='utf-8')) if a.baseline else None,required_exams=json.loads(Path(a.required_exams).read_text(encoding='utf-8')) if a.required_exams else None)
    Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(report['status'],len(report['blocking']),'blocking',len(report['candidates']),'candidates',f'report={a.out}')
    return int(report['status']!='pass')

if __name__=='__main__':raise SystemExit(main())
