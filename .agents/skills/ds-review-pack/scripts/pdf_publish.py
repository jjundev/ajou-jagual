"""Hash-bound visual review gate and pack-level backup/rollback."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
from pdf_cards import digest, ensure_report_owner
from pdf_types import PdfError


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def stage_hashes(run):
    stage=Path(run)/'stage'
    return {p.relative_to(stage).as_posix():digest(p) for p in sorted(stage.rglob('*')) if p.is_file()}


def publish_stage(run,repo):
    run=Path(run).resolve();repo=Path(repo).resolve()
    report=json.loads((run/'report.json').read_text());source=Path(report['source']).resolve();dest=Path(report['dest']).resolve()
    if not source.is_relative_to(repo) or not dest.is_relative_to(repo) or dest!=source.parent:
        raise PdfError('Publication outside repository/source directory')
    if not (run/'review.json').exists():raise PdfError('Actual browser review required')
    review=json.loads((run/'review.json').read_text())
    if review.get('status')!='pass' or not review.get('reviewer') or not review.get('evidence'):
        raise PdfError('Actual browser review not pass')
    if review.get('report_sha256')!=digest(run/'report.json') or review.get('artifact_hashes')!=stage_hashes(run) or report['artifact_hashes']!=stage_hashes(run):
        raise PdfError('Stage changed after visual review')
    if report['checks']['status']!='pass' or report['checks']['errors']:raise PdfError('Machine checks not pass')
    lockdir=Path(tempfile.gettempdir())/'ds-pdf-locks';lockdir.mkdir(exist_ok=True)
    lock=lockdir/(hashlib.sha256(str(dest).encode()).hexdigest()+'.lock')
    with lock.open('a') as handle:
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:raise PdfError('Pack publication lock busy') from exc
        ensure_report_owner(source)
        if digest(source)!=report['source_sha256']:raise PdfError('Source changed since build')
        for name,sha in report.get('input_assets',{}).items():
            if digest(Path(name))!=sha:raise PdfError('Source image changed since build')
        backup=run/'backups'/uuid.uuid4().hex;backup.mkdir(parents=True)
        final_report=dict(report,status='published',browser=review)
        dump(run/'publish-report.json',final_report)
        files=[(run/'stage'/name,dest/name) for name in report['pdfs']]
        files.append((run/'publish-report.json',dest/'자료_PDF/pdf-validation.json'))
        old=[];completed=[];temps=[]
        try:
            for index,(src,target) in enumerate(files):
                if not src.resolve().is_relative_to(run):raise PdfError('Stage path outside RUN')
                target.parent.mkdir(parents=True,exist_ok=True)
                previous=backup/f'{index}-{target.name}' if target.exists() else None
                if previous:shutil.copy2(target,previous)
                old.append((target,previous))
                temp=target.parent/('.'+target.name+'.'+uuid.uuid4().hex+'.tmp');temps.append(temp)
                with temp.open('wb') as output:
                    output.write(src.read_bytes());output.flush();os.fsync(output.fileno())
                os.replace(temp,target);completed.append(target)
            for folder in {target.parent for _,target in files}:
                fd=os.open(folder,os.O_RDONLY)
                try:os.fsync(fd)
                finally:os.close(fd)
        except BaseException:
            for target,previous in reversed(old):
                if target not in completed:continue
                if previous:shutil.copy2(previous,target)
                elif target.exists():target.unlink()
            raise
        finally:
            for temp in temps:
                if temp.exists():temp.unlink()
        return backup
