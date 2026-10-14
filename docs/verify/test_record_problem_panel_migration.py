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
