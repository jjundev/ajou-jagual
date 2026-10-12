"""Exclusive final publication; verify current bytes, own-inode rollback, chapter JSON files last."""
from pathlib import Path
import argparse,json,os,shutil,tempfile
from model import canonical_digest,bank_counts
from source import resolve_local,file_sha256
from validate import validate_bank
from bank import bank_files,load_bank

def package_fingerprint(package):
    package=Path(package);files={p.name:file_sha256(p) for p in bank_files(package)}
    for name in ('inventory.json','asset-models.json','preview.html'):
        files['제작자료/'+name]=file_sha256(package/'제작자료'/name)
    for p in sorted((package/'assets').glob('*.svg')):files['assets/'+p.name]=file_sha256(p)
    return canonical_digest(files)

def verify_package(package):
    package=Path(package);s=package/'제작자료'
    try:
        bank=load_bank(package);inv=json.loads((s/'inventory.json').read_text());models=json.loads((s/'asset-models.json').read_text());manifest=json.loads((s/'verification.json').read_text())
        errors=validate_bank(bank,package,inv,models,complete=True)
        if errors:raise ValueError('\n'.join(errors))
        if manifest['package_sha256']!=package_fingerprint(package):raise ValueError('stale package verification')
        if manifest['content_review']['status']!='verified' or not manifest['content_review']['notes']:raise ValueError('content review incomplete')
        if manifest['origin_sha256']!={s['id']:s['sha256'] for s in bank['sources']}:raise ValueError('source manifest mismatch')
        expected={a['id']:a['sha256'] for a in bank['assets']};reviews=manifest['asset_reviews']
        if len(reviews)!=len(expected) or {a['id']:a['sha256'] for a in reviews}!=expected or any(a['status']!='verified' or not a['notes'] for a in reviews):raise ValueError('asset review incomplete')
        br=manifest['browser_reviews'];needed={('1280x900','light'),('1280x900','dark'),('375x812','light'),('375x812','dark')}
        if {(r['viewport'],r['theme']) for r in br}!=needed or any(r['status']!='verified' or not r['notes'] for r in br):raise ValueError('browser review incomplete')
        if manifest['unresolved']:raise ValueError('unresolved issues')
        if manifest['counts']!=bank_counts(bank,inv,models):raise ValueError('manifest count mismatch')
        return bank
    except (OSError,KeyError,json.JSONDecodeError) as e:raise ValueError('package is incomplete') from e

def publish_package(package,destination):
    package=Path(package);destination=Path(destination);bank=verify_package(package)
    def destination_sources():
        for source in bank['sources']:
            if file_sha256(resolve_local(destination,source['path']))!=source['sha256']:raise ValueError('destination source changed')
    destination_sources()
    files=[(p,Path('assets')/p.name) for p in sorted((package/'assets').glob('*.svg'))]
    support=package/'제작자료'
    # Data plus the requested repeatable validation tools, never arbitrary scratch files.
    approved=['inventory.json','asset-models.json','preview.html','verification.md','verification.json','question-bank.schema.json','README.md']
    approved += ['scripts/'+name for name in ['source.py','model.py','assets.py','validate.py','preview.py','bank.py','publish.py','requirements.txt']]
    approved += ['tests/'+name for name in ['conftest.py','test_source.py','test_model.py','test_assets.py','test_validation.py','test_delivery.py','test_bank.py']]
    files +=[(support/rel,Path('제작자료')/rel) for rel in approved if (support/rel).is_file()]
    if (package/'readme.md').is_file():files.append((package/'readme.md',Path('readme.md')))
    files.extend((p,Path(p.name)) for p in bank_files(package))
    for source,rel in files:
        if source.is_symlink():raise ValueError('package symlink')
        if (destination/rel).exists() or (destination/rel).is_symlink():raise ValueError('destination conflict: '+str(rel))
    made=[];created_dirs=[]
    with tempfile.TemporaryDirectory(prefix='.textbook-publish-',dir=destination) as staging:
        snapshot=Path(staging)/'snapshot';snapshot.mkdir()
        # Copy the entire deployment set before verifying and linking any final path.
        for source,rel in files:
            dest=snapshot/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
        for source in bank['sources']:
            origin=snapshot/source['path'];origin.parent.mkdir(exist_ok=True);shutil.copy2(resolve_local(package,source['path']),origin)
        verify_package(snapshot);destination_sources()
        try:
            for source,rel in files:
                temp=snapshot/rel;dest=destination/rel;parents=[];parent=dest.parent
                while not parent.exists():parents.append(parent);parent=parent.parent
                for parent in reversed(parents):parent.mkdir();created_dirs.append(parent)
                if not dest.parent.resolve().is_relative_to(destination.resolve()):raise ValueError('destination path escape')
                owned=temp.stat();identity=(owned.st_dev,owned.st_ino)
                os.link(temp,dest);made.append((dest,identity))
            destination_sources()
        except BaseException:
            for dest,identity in reversed(made):
                try:
                    stat=dest.lstat()
                    if (stat.st_dev,stat.st_ino)==identity:dest.unlink()
                except FileNotFoundError:pass
            for directory in reversed(created_dirs):
                try:directory.rmdir()
                except OSError:pass
            raise
    return [str(dest) for dest,identity in made]

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--package',type=Path,required=True);parser.add_argument('--destination',type=Path,required=True);args=parser.parse_args(argv)
    for path in publish_package(args.package,args.destination):print(path)
if __name__=='__main__':main()
