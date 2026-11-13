"""The pinned, repository-local resources shared by problem explanations."""
import json
import os
from pathlib import Path
from urllib.parse import quote

from mpe_source import inside, sha256
from mpe_types import ExplainError

SHARED_ROOT = Path('복습노트/_assets/problem-explain/v1')
PROVENANCE_SHA256 = 'c953ecb4573b74379b1599a52f234b195bb335cf119fd9b35997c2a98b6abfeb'
PAGE_ASSETS = {
    'pretendard/pretendard.css',
    'katex/katex.min.css',
    'katex/katex.min.js',
    'katex/contrib/auto-render.min.js',
}


def shared_assets(repo: Path) -> dict:
    root = inside(repo / SHARED_ROOT, repo)
    provenance = inside(root / 'provenance.json', repo)
    if not provenance.is_file() or sha256(provenance) != PROVENANCE_SHA256:
        raise ExplainError(f'공용 자원 출처 목록 변경/누락: {provenance}')
    files = json.loads(provenance.read_text(encoding='utf-8'))['files']
    for name, digest in files.items():
        file = inside(root / name, root)
        if not file.is_file() or sha256(file) != digest:
            raise ExplainError(f'공용 자원 변경/누락: {file}')
    return {'root': SHARED_ROOT.as_posix(), 'files': {**files, 'provenance.json': PROVENANCE_SHA256}}


def verify_shared_assets(repo: Path, manifest: dict) -> bool:
    """Verify v2 dependencies while retaining support for v1 local bundles."""
    if manifest['version'] == 1 and 'shared_assets' not in manifest:
        return False
    if manifest['version'] != 2 or manifest.get('shared_assets') != shared_assets(repo):
        raise ExplainError('공용 자원 manifest 불일치')
    return True


def vendor_url(repo: Path, destination: Path) -> str:
    return quote(Path(os.path.relpath(repo / SHARED_ROOT, destination)).as_posix(), safe='/')
