"""Hash-bound visual review gate and pack-level backup/rollback."""
try:
    import fcntl
except ImportError:
    fcntl=None
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
from pdf_cards import digest, ensure_report_owner
from pdf_types import PdfError
from pack_layout import pdf_report_path
from pdf_ds_layout import check_extension
from review_source import source_file, source_digest, problem_pdf_pages, nfc
from review_links import refresh_pages

def lock_handle(handle):
    if fcntl:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    else:
        import msvcrt
        try:
            handle.seek(0)
            if not handle.read(1):handle.write('0');handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        except OSError as exc:raise BlockingIOError('lock busy') from exc


def dump(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def stage_hashes(run):
    stage=Path(run)/'stage'
    return {p.relative_to(stage).as_posix():digest(p) for p in sorted(stage.rglob('*')) if p.is_file()}


def refreshed_documents(source, report):
    """Keep published PDF page links aligned if pagination changes on re-export."""
    prior = problem_pdf_pages(source)
    pages = report.get('probes', {}).get('problems', {}).get('page_ids', [])
    current = {pid: idx for idx, pid in enumerate(pages, 1) if pid in report.get('logical_ids', [])}
    if prior == current or not pages:
        return {}
    key = nfc(source.stem).removeprefix('복습문제_')
    root = source.parent
    updates = {}
    explain = root / '.pack' / f'자료_문제설명_{key}' / 'manifest.json'
    manifest = json.loads(explain.read_text(encoding='utf-8')) if explain.is_file() else None
    hashes_changed = False
    for ext, folder in (('.html', root), ('.md', root / '.pack')):
        path = folder / f'문제설명_{key}{ext}'
        if not path.is_file():
            continue
        raw = path.read_bytes()
        old = raw.decode('utf-8')
        old_hash = hashlib.sha256(raw).hexdigest()
        refreshed = refresh_pages(old, source, prior, current, markdown=ext == '.md')
        if refreshed == old:
            continue
        content = refreshed.encode('utf-8')
        updates[path] = (old_hash, content)
        rel = path.relative_to(root).as_posix()
        if manifest and manifest['files'].get(rel) == old_hash:
            manifest['files'][rel] = hashlib.sha256(content).hexdigest()
            hashes_changed = True
    if hashes_changed:
        updated = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        updates[explain] = (digest(explain), updated)
    return updates


def publish_stage(run,repo):
    run=Path(run).resolve();repo=Path(repo).resolve()
    report=json.loads((run/'report.json').read_text());source=Path(report['source']).resolve();dest=Path(report['dest']).resolve()
    if (not source.is_relative_to(repo) or not dest.is_relative_to(repo) or dest!=source.parent
            or not source_file(source).resolve().is_relative_to(repo)):
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
    with lock.open('a+') as handle:
        try:lock_handle(handle)
        except BlockingIOError as exc:raise PdfError('Pack publication lock busy') from exc
        if report.get('code_style_version'):
            from pdf_code import check_font_assets
            check_font_assets(report['code_font'])
            from review_pdf import check_stage
            errors=check_stage(run)
            if errors:raise PdfError('Final code/stage checks: '+ '; '.join(errors))
        ensure_report_owner(source)
        if 'layout_extension_sha256' in report:check_extension(report)
        if source_digest(source)!=report['source_sha256']:raise PdfError('Source changed since build')
        for name,sha in report.get('input_assets',{}).items():
            if digest(Path(name))!=sha:raise PdfError('Source image changed since build')
        backup=run/'backups'/uuid.uuid4().hex;backup.mkdir(parents=True)
        final_report=dict(report,status='published',browser=review)
        dump(run/'publish-report.json',final_report)
        files=[(run/'stage'/name,dest/name) for name in report['pdfs']]
        files.append((run/'publish-report.json',pdf_report_path(dest)))
        source_updates = refreshed_documents(source, report) if source_file(source).suffix == '.json' else {}
        if source_updates:
            for i, (target, (_, data)) in enumerate(source_updates.items()):
                draft = run / f'link-update-{i}.tmp'
                draft.write_bytes(data)
                files.append((draft, target))
        old=[];completed=[];temps=[]
        try:
            for index,(src,target) in enumerate(files):
                if not src.resolve().is_relative_to(run):raise PdfError('Stage path outside RUN')
                target.parent.mkdir(parents=True,exist_ok=True)
                if target in source_updates and digest(target) != source_updates[target][0]:
                    raise PdfError('PDF link document changed since stage: ' + target.name)
                previous=backup/f'{index}-{target.name}' if target.exists() else None
                if previous:shutil.copy2(target,previous)
                old.append((target,previous))
                temp=target.parent/('.'+target.name+'.'+uuid.uuid4().hex+'.tmp');temps.append(temp)
                with temp.open('wb') as output:
                    output.write(src.read_bytes());output.flush();os.fsync(output.fileno())
                os.replace(temp,target);completed.append(target)
            for folder in ({target.parent for _,target in files} if os.name!='nt' else []):
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
