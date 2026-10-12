import hashlib, json, shutil, subprocess, sys
from pathlib import Path
from mpe_source import sha256

S=Path(__file__).resolve().parents[1]

def test_install_has_no_ml_runtime_dependency(tmp_path):
    copied=tmp_path/'skill';shutil.copytree(S,copied,ignore=shutil.ignore_patterns('__pycache__'))
    result=subprocess.run([sys.executable,str(copied/'scripts/mpe_cli.py'),'--help'],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert 'extract' in result.stdout and 'publish' in result.stdout

def test_claude_link_and_provenance():
    repo=S.parents[2];link=repo/'.claude/skills/ds-problem-explain'
    assert link.is_symlink() and link.resolve()==S.resolve()
    data=json.loads((S/'assets/port-provenance.json').read_text())
    assert data['source_commit']=='1e2d5f81813a5481c78341545a13ab300f2d82c5'
    overrides={entry['destination']:entry for entry in data.get('local_overrides',[])}
    for entry in data['files']:
        path=S/entry['destination']
        override=overrides.get(entry['destination'])
        if override:
            assert sha256(path)==override['current_sha256']
            inserted=override['inserted_text'].encode('utf-8')
            current=path.read_bytes()
            assert current.count(inserted)==1
            restored=current.replace(inserted,b'',1)
            assert hashlib.sha256(restored).hexdigest()==override['base_sha256']==entry['destination_sha256']
        else:
            assert sha256(path)==entry['destination_sha256']
        if entry['destination'].startswith('assets/') and entry['source_path']:
            assert entry['source_sha256']==entry['destination_sha256']
