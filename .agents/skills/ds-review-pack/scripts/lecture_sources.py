"""Validate lecture-code provenance against the current local PDF and sessions."""
from pathlib import Path
import hashlib
import re

def validate_lecture_source(repo: Path, problem: dict, sessions: list[dict]) -> list[str]:
    errors=[]
    ref=problem.get('lecture_ref',{})
    if not isinstance(ref,dict): return ['lecture_ref must be an object']
    for key in ('path','sha256','example','taught_on'):
        if not isinstance(ref.get(key),str) or not ref[key]: errors.append(f'lecture_ref.{key} required')
    if not re.fullmatch(r'lecture-s\d{2}-p\d+-[a-z0-9-]+',problem.get('source','')): errors.append('invalid lecture source ID')
    if not isinstance(problem.get('objectives'),list) or not problem['objectives'] or not all(isinstance(x,str) and x for x in problem['objectives']): errors.append('objectives required')
    if not isinstance(problem.get('task_family'),str) or not problem['task_family']: errors.append('task_family required')
    dates=[s.get('date','').replace('-','')[-4:] for s in sessions]
    taught=str(ref.get('taught_on','')).replace('-','')[-4:]
    supplement=problem.get('scope')=='retained-supplement'
    if supplement and not str(problem.get('scope_evidence','')).strip():
        errors.append('retained supplement requires scope evidence and core coverage exclusion')
    if not dates or not taught or (taught>max(dates) and not supplement): errors.append('lecture example not taught by these sessions')
    chapter=re.match(r'lecture-s(\d+)-',problem.get('source',''))
    if chapter:
        ch=int(chapter[1]);scopes=[]
        for session in sessions:
            for match in re.finditer(r'S(\d+)\s*p(\d+)(?:\s*[–—-]\s*(\d+))?',session.get('slides','')):
                if int(match[1])==ch:scopes.append((int(match[2]),int(match[3] or match[2])))
        page=ref.get('pdf_page')
        if not supplement and scopes and type(page)==int and taught==max(dates) and not any(a<=page<=b for a,b in scopes):
            errors.append('lecture page outside taught session scope')
    if errors:return errors
    root=Path(repo).resolve(); path=(root/ref['path']).resolve()
    if Path(ref['path']).is_absolute() or not path.is_relative_to(root): return ['lecture path outside repository']
    if not path.is_file(): return ['lecture PDF missing']
    if hashlib.sha256(path.read_bytes()).hexdigest()!=ref['sha256']: errors.append('lecture PDF SHA256 mismatch')
    try:
        import pymupdf
        with pymupdf.open(path) as doc:
            page=ref.get('pdf_page')
            if type(page)!=int or not 1<=page<=len(doc):errors.append('lecture PDF page out of range')
            for extra in ref.get('extra_pages',[]):
                if type(extra)!=int or not 1<=extra<=len(doc):errors.append('extra lecture PDF page out of range')
    except Exception as exc:errors.append(f'lecture PDF unreadable: {exc}')
    return errors
