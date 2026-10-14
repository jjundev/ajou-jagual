"""Append replacement overrides to ds-problem-explain's port-provenance.json.

Each destination is diffed against its HEAD bytes; the override is the smallest
context-padded set of hunks that undo_overrides() peels back to HEAD exactly.
Usage: record-ds-explain-overrides.py --reason TEXT DESTINATION...
"""
import argparse, difflib, hashlib, json, subprocess, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / '.agents/skills/ds-problem-explain'
sys.path[:0] = [str(SKILL / 'scripts'), str(SKILL / 'tests')]
from test_skill_files import undo_overrides  # noqa: E402

MAX_CONTEXT = 20


def sha(data): return hashlib.sha256(data).hexdigest()


def head_bytes(skill, destination):
    result = subprocess.run(['git', '-C', str(skill), 'show', f'HEAD:./{destination}'], capture_output=True)
    if result.returncode: raise SystemExit(f'{destination}: not in HEAD')
    return result.stdout


def replacements(old, new, k):
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    groups = difflib.SequenceMatcher(None, a, b, autojunk=False).get_grouped_opcodes(k)
    return [{'old': b''.join(a[g[0][1]:g[-1][2]]).decode(), 'new': b''.join(b[g[0][3]:g[-1][4]]).decode()} for g in groups]


def override(destination, old, new, reason):
    for k in range(MAX_CONTEXT + 1):
        entry = {'destination': destination, 'base_sha256': sha(old), 'current_sha256': sha(new),
                 'replacements': replacements(old, new, k), 'reason': reason}
        try:
            if undo_overrides(new, [entry]) == old: return entry
        except AssertionError:
            pass
    raise SystemExit(f'{destination}: no unique replacement set within {MAX_CONTEXT} context lines')


def record(skill, reason, destinations):
    skill = Path(skill); path = skill / 'assets/port-provenance.json'
    data = json.loads(path.read_text())
    added = []
    for destination in destinations:
        entry = next((e for e in data['files'] if e['destination'] == destination), None)
        if entry is None: raise SystemExit(f'{destination}: not a provenance destination')
        chain = [o for o in data.get('local_overrides', []) if o['destination'] == destination]
        recorded = chain[-1]['current_sha256'] if chain else entry['destination_sha256']
        old, new = head_bytes(skill, destination), (skill / destination).read_bytes()
        if sha(old) != recorded: raise SystemExit(f'{destination}: HEAD bytes are not the recorded ones')
        if old == new: continue
        added.append(override(destination, old, new, reason))
    if added:
        data.setdefault('local_overrides', []).extend(added)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return added


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--reason', required=True)
    parser.add_argument('destinations', nargs='+')
    args = parser.parse_args()
    for entry in record(SKILL, args.reason, args.destinations):
        print(f"recorded {entry['destination']}: {len(entry['replacements'])} replacement(s)")


if __name__ == '__main__':
    main()
