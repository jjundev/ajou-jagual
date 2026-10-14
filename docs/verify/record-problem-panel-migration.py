"""Link a republished problem explanation's old hashes to its new ones (.pack/migration-2026-10-14-problem-panel.json).

Usage: record-problem-panel-migration.py [--base REV] 복습노트/<D>
Before-hashes are the bytes at REV (default HEAD) of every file the explanation publish owns:
문제설명_*.html, .pack/문제설명_*.md, .pack/자료_문제설명_*/**, .pack/figures_문제설명_*/**.
"""
import argparse, hashlib, json, subprocess, unicodedata
from fnmatch import fnmatch
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


def owned(rel):
    """Paths (relative to the date folder) a problem explanation publish owns."""
    parts = rel.split('/')
    return (len(parts) == 1 and fnmatch(rel, '문제설명_*.html')) or (len(parts) == 2 and fnmatch(rel, '.pack/문제설명_*.md')) or (
        len(parts) > 2 and parts[0] == '.pack' and (fnmatch(parts[1], '자료_문제설명_*') or fnmatch(parts[1], 'figures_문제설명_*')))


def owned_before(date_dir, rev):
    """SHA-256 at rev of every explanation-owned file in the date folder."""
    date_dir = Path(date_dir)
    git = lambda *a: subprocess.run(['git', *a], cwd=date_dir, capture_output=True, check=True).stdout
    names = git('ls-tree', '-r', '-z', '--name-only', rev, '--', '.').decode().split('\0')
    nfc = lambda n: unicodedata.normalize('NFC', n)
    return {nfc(n): sha(git('show', f'{rev}:./{n}')) for n in names if n and owned(nfc(n))}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--base', default='HEAD', help='commit holding the files before this republish')
    parser.add_argument('date_dir', type=Path)
    args = parser.parse_args()
    print(record(args.date_dir, owned_before(args.date_dir, args.base)))


if __name__ == '__main__':
    main()
