"""Link a republished problem explanation's old hashes to its new ones (.pack/migration-2026-10-14-problem-panel.json).

Usage: record-problem-panel-migration.py 복습노트/<D>
Before-hashes are the committed (HEAD) bytes of 문제설명_*.html and .pack/문제설명_*.md;
run it after `mpe_cli.py publish` and before committing.
"""
import hashlib, json, subprocess, sys
from pathlib import Path

NAME = 'migration-2026-10-14-problem-panel.json'
REASON = 'problem panel (bio-problem-explain be26a42)'


def sha(data): return hashlib.sha256(data).hexdigest()


def record(date_dir, before):
    date_dir = Path(date_dir); path = date_dir / '.pack' / NAME
    if path.exists(): raise SystemExit(f'{path}: already recorded')
    rewritten = {}
    for rel, digest in before.items():
        after = sha((date_dir / rel).read_bytes())
        if after != digest:
            rewritten[rel] = {'before': digest, 'after': after}
    path.write_text(json.dumps({'date': '2026-10-14', 'reason': REASON, 'moved': [], 'rewritten': rewritten},
                               ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return path


def head_digest(path):
    data = subprocess.run(['git', 'show', f'HEAD:./{path.name}'], cwd=path.parent, capture_output=True, check=True).stdout
    return sha(data)


def main():
    date_dir = Path(sys.argv[1])
    owned = [*date_dir.glob('문제설명_*.html'), *date_dir.glob('.pack/문제설명_*.md')]
    if len(owned) != 2: raise SystemExit(f'{date_dir}: expected one explanation HTML and MD, found {len(owned)}')
    print(record(date_dir, {p.relative_to(date_dir).as_posix(): head_digest(p) for p in owned}))


if __name__ == '__main__':
    main()
