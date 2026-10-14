import hashlib, importlib.util, json, subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('record_ds_explain_overrides', HERE / 'record-ds-explain-overrides.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

ORIGINAL = ''.join(f'line {i}\n' if i % 5 else 'same\n' for i in range(40))


def sha(data): return hashlib.sha256(data).hexdigest()


def git(repo, *args): subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True)


def skill(tmp_path):
    repo = tmp_path / 'repo'; s = repo / 'skill'
    (s / 'assets').mkdir(parents=True)
    (s / 'a.txt').write_text(ORIGINAL)
    provenance = {'source_commit': 'x', 'files': [{'destination': 'a.txt', 'destination_sha256': sha(ORIGINAL.encode())}], 'local_overrides': []}
    (s / 'assets/port-provenance.json').write_text(json.dumps(provenance))
    git(repo, 'init', '-q'); git(repo, 'add', '.'); git(repo, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qm', 'init')
    return repo, s


def commit(repo): git(repo, '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-qam', 'next')


def chain(s): return json.loads((s / 'assets/port-provenance.json').read_text())['local_overrides']


def test_record_appends_reversible_override(tmp_path):
    repo, s = skill(tmp_path)
    lines = ORIGINAL.splitlines(keepends=True)
    lines[0] = 'first changed\n'; lines[10] = 'same\n'; lines.insert(20, 'inserted\n'); lines[-1] = 'end changed\n'
    new = ''.join(lines).encode(); (s / 'a.txt').write_bytes(new)
    added = mod.record(s, 'why', ['a.txt'])
    assert len(added) == 1 and chain(s) == added
    entry = added[0]
    assert entry['destination'] == 'a.txt' and entry['reason'] == 'why'
    assert entry['current_sha256'] == sha(new) and entry['base_sha256'] == sha(ORIGINAL.encode())
    assert mod.undo_overrides(new, [entry]) == ORIGINAL.encode()


def test_record_chains_on_existing_override(tmp_path):
    repo, s = skill(tmp_path)
    (s / 'a.txt').write_text(ORIGINAL.replace('line 3\n', 'three\n')); mod.record(s, 'one', ['a.txt']); commit(repo)
    final = ORIGINAL.replace('line 3\n', 'three\n').replace('line 33\n', 'thirty-three\nmore\n')
    (s / 'a.txt').write_text(final); mod.record(s, 'two', ['a.txt'])
    assert len(chain(s)) == 2
    assert mod.undo_overrides(final.encode(), chain(s)) == ORIGINAL.encode()


def test_record_refuses_unrecorded_head(tmp_path):
    repo, s = skill(tmp_path)
    (s / 'a.txt').write_text(ORIGINAL + 'sneaked\n'); commit(repo)
    (s / 'a.txt').write_text(ORIGINAL + 'sneaked\nmore\n')
    with pytest.raises(SystemExit):
        mod.record(s, 'why', ['a.txt'])
    assert chain(s) == []


def test_record_noop_when_unchanged(tmp_path):
    repo, s = skill(tmp_path)
    assert mod.record(s, 'why', ['a.txt']) == [] and chain(s) == []
