import hashlib, json, shutil, subprocess, sys
from pathlib import Path
from mpe_source import sha256

S=Path(__file__).resolve().parents[1]

def test_install_has_no_ml_runtime_dependency(tmp_path):
    copied=tmp_path/'skill';shutil.copytree(S,copied,ignore=shutil.ignore_patterns('__pycache__'))
    result=subprocess.run([sys.executable,str(copied/'scripts/mpe_cli.py'),'--help'],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert 'extract' in result.stdout and 'publish' in result.stdout and 'rerender' in result.stdout

def undo_overrides(current,chain):
    """Peel approved local edits newest-first; each step must restore its recorded base bytes exactly."""
    for override in reversed(chain):
        assert hashlib.sha256(current).hexdigest()==override['current_sha256']
        if 'inserted_text' in override:
            inserted=override['inserted_text'].encode('utf-8')
            assert current.count(inserted)==1
            current=current.replace(inserted,b'',1)
        for change in reversed(override.get('replacements',[])):
            new,old=change['new'].encode('utf-8'),change['old'].encode('utf-8')
            assert current.count(new)==1
            current=current.replace(new,old,1)
        assert hashlib.sha256(current).hexdigest()==override['base_sha256']
    return current

def test_claude_link_and_provenance():
    repo=S.parents[2];link=repo/'.claude/skills/ds-problem-explain'
    assert link.is_symlink() and link.resolve()==S.resolve()
    data=json.loads((S/'assets/port-provenance.json').read_text())
    assert data['source_commit']=='1e2d5f81813a5481c78341545a13ab300f2d82c5'
    overrides={}
    for entry in data.get('local_overrides',[]):
        overrides.setdefault(entry['destination'],[]).append(entry)
    for entry in data['files']:
        path=S/entry['destination']
        chain=overrides.get(entry['destination'])
        if chain:
            assert sha256(path)==chain[-1]['current_sha256']
            assert hashlib.sha256(undo_overrides(path.read_bytes(),chain)).hexdigest()==entry['destination_sha256']
        else:
            assert sha256(path)==entry['destination_sha256']
        if entry['destination'].startswith('assets/') and entry['source_path']:
            assert entry['source_sha256']==entry['destination_sha256']

def test_skill_documents_rerender_and_panel():
    skill=(S/'SKILL.md').read_text();verification=(S/'references/verification.md').read_text()
    assert '### 레이아웃만 바뀐 기존 발행분 재발행' in skill and 'mpe_cli.py rerender' in skill
    assert 'od-panels:explain:v2:prob' in skill and '원문 탭' in verification and '띄우기' in verification
