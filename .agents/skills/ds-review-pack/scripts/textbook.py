"""Validated, isolated adapter for the source-only textbook package."""
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
import unicodedata
from bank import BankError

@dataclass
class TextbookCatalog:
    package: Path
    questions: dict
    chapters: dict
    sources: dict
    assets: dict

_MAPPING = {1:1,2:2,3:3,4:5,5:6,6:4,7:4,8:7,9:8,10:10,11:10,12:9,13:12,14:11}

def course_chapters(chapter: int) -> set[int]:
    return {_MAPPING[chapter]}

def resolve_package(path: Path) -> Path:
    path = Path(path).expanduser().absolute()
    if path.is_dir():
        return path.resolve()
    current = Path(path.anchor)
    for part in path.parts[1:]:
        if not current.is_dir():
            raise BankError(f'교과서 폴더 없음: {path}')
        matches = [p for p in current.iterdir() if unicodedata.normalize('NFC',p.name)==unicodedata.normalize('NFC',part)]
        if len(matches)!=1:
            raise BankError(f'교과서 경로를 찾을 수 없음: {path}')
        current = matches[0]
    if not current.is_dir():
        raise BankError(f'교과서 폴더 없음: {path}')
    return current.resolve()

def load_textbook(package: Path, *, python: str) -> TextbookCatalog:
    package = resolve_package(package)
    validator = package/'제작자료/scripts/validate.py'
    try:
        result = subprocess.run([python,str(validator),str(package),'--complete'],capture_output=True,text=True,timeout=120)
    except (OSError,subprocess.SubprocessError) as e:
        raise BankError(f'교과서 검증 실행 실패 ({python}; PyMuPDF/jsonschema 필요): {e}') from e
    if result.returncode:
        raise BankError(f'교과서 검증 실패 ({python}; PyMuPDF/jsonschema 확인):\n{result.stdout}{result.stderr}')
    fields = {k:{} for k in ('questions','chapters','sources','assets')}
    for file in sorted(package.glob('*.json')):
        data = json.loads(file.read_text(encoding='utf8'))
        for key,out in fields.items():
            for item in data.get(key,[]):
                if item['id'] in out and out[item['id']]!=item:
                    raise BankError(f'교과서 중복 ID: {item["id"]}')
                out[item['id']] = item
    return TextbookCatalog(package,**fields)

def eligible(question: dict) -> bool:
    return (question.get('review',{}).get('status')=='verified' and not any(
        issue.get('blocking') or issue.get('kind') in {'unreadable','figure-incomplete','external-context'}
        for issue in question.get('issues',[])))

def textbook_candidates(catalog: TextbookCatalog, range_ch: set[int], taught: set[int], used: set[str], *, concept_overrides=None) -> list[dict]:
    rows=[]
    for q in catalog.questions.values():
        original=q['id'];chapter=catalog.chapters[q['chapter_id']]['number']
        chapters=course_chapters(chapter) | set((concept_overrides or {}).get(original,[]))
        # Overrides are independently reviewed alternative concept mappings, not permission to teach a whole chapter.
        mapped=set((concept_overrides or {}).get(original,[])) or chapters
        if eligible(q) and mapped<=taught and mapped & range_ch and 'textbook-'+original not in used:
            rows.append(dict(q,id='textbook-'+original,question_id=original,source_kind='textbook',chapters=sorted(mapped),type=q['kind'],answer=None))
    ranks={'trace':0,'code-read':0,'short':1,'choice':1,'code-write':1,'mixed':2,'essay':2}
    return sorted(rows,key=lambda q:(ranks.get(q['type'],3),q['question_id']))
