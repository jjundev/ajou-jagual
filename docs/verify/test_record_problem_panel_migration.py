import hashlib, importlib.util, json
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('record_problem_panel_migration', HERE / 'record-problem-panel-migration.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)


def sha(text): return hashlib.sha256(text.encode()).hexdigest()


def date_dir(tmp_path):
    d = tmp_path / '1012'; (d / '.pack').mkdir(parents=True)
    (d / '문제설명_1012_Queue.html').write_text('new html')
    (d / '.pack/문제설명_1012_Queue.md').write_text('new md')
    return d


def test_record_writes_before_after(tmp_path):
    d = date_dir(tmp_path)
    path = mod.record(d, {'문제설명_1012_Queue.html': sha('old html'), '.pack/문제설명_1012_Queue.md': sha('old md')})
    assert path == d / '.pack/migration-2026-10-14-problem-panel.json'
    assert json.loads(path.read_text()) == {
        'date': '2026-10-14', 'reason': 'problem panel (bio-problem-explain be26a42)', 'moved': [],
        'rewritten': {'문제설명_1012_Queue.html': {'before': sha('old html'), 'after': sha('new html')},
                      '.pack/문제설명_1012_Queue.md': {'before': sha('old md'), 'after': sha('new md')}}}


def test_record_refuses_existing(tmp_path):
    d = date_dir(tmp_path)
    existing = d / '.pack/migration-2026-10-14-problem-panel.json'; existing.write_text('{"keep": true}')
    with pytest.raises(SystemExit):
        mod.record(d, {'문제설명_1012_Queue.html': sha('old html')})
    assert existing.read_text() == '{"keep": true}'


def test_record_skips_unchanged(tmp_path):
    d = date_dir(tmp_path)
    path = mod.record(d, {'문제설명_1012_Queue.html': sha('old html'), '.pack/문제설명_1012_Queue.md': sha('new md')})
    assert list(json.loads(path.read_text())['rewritten']) == ['문제설명_1012_Queue.html']


def test_owned_before_covers_data_and_figure_folders(tmp_path):
    import subprocess
    repo = tmp_path / 'repo'; d = repo / '복습노트/1012'
    files = {'문제설명_1012_Queue.html': 'html', '복습문제_1012_Queue.html': 'source', '.pack/문제설명_1012_Queue.md': 'md',
             '.pack/정리노트_1012_Queue.md': 'note', '.pack/자료_문제설명_1012_Queue/validation.json': 'v',
             '.pack/자료_문제설명_1012_Queue/manifest.json': 'm', '.pack/figures_문제설명_1012_Queue/f.svg': 'svg'}
    for rel, text in files.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True); (d / rel).write_text(text)
    git = lambda *a: subprocess.run(['git', '-C', str(repo), *a], check=True, capture_output=True)
    git('init', '-q'); git('add', '.'); git('-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'base')
    (d / '.pack/자료_문제설명_1012_Queue/validation.json').write_text('v2'); (d / '문제설명_1012_Queue.html').write_text('html2')
    before = mod.owned_before(d, 'HEAD')
    assert set(before) == {'문제설명_1012_Queue.html', '.pack/문제설명_1012_Queue.md', '.pack/자료_문제설명_1012_Queue/validation.json',
                           '.pack/자료_문제설명_1012_Queue/manifest.json', '.pack/figures_문제설명_1012_Queue/f.svg'}
    assert before['.pack/자료_문제설명_1012_Queue/validation.json'] == sha('v')
    rewritten = json.loads(mod.record(d, before).read_text())['rewritten']
    assert set(rewritten) == {'문제설명_1012_Queue.html', '.pack/자료_문제설명_1012_Queue/validation.json'}
