"""File-based evidence and freshness checks; no remote state is inferred."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
import uuid

STAGES = ('images', 'notion', 'html', 'print', 'content', 'visual')
# Track earlier checks even when intermediate stages have not been recorded yet.
PARENTS = {stage: list(STAGES[:i]) for i, stage in enumerate(STAGES)}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, value: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                         prefix='.' + path.name, delete=False) as stream:
            name = stream.name
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def fingerprint(path: Path) -> dict:
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': digest(path.read_bytes()) if path.is_file() else None}


class Ledger:
    def __init__(self, path: Path, page_id: str | None = None):
        self.path = Path(path)
        self.requested_page = page_id
        self.data = (json.loads(self.path.read_text()) if self.path.exists() else
                     {'schema_version': 1, 'page_id': page_id, 'stages': {}, 'history': []})
        if self.data.get('schema_version') != 1:
            raise ValueError('Unsupported state schema')
        if page_id and self.data.get('page_id') not in (None, page_id):
            raise ValueError('State belongs to another page')
        if page_id:
            self.data['page_id'] = page_id
        self.page_id = self.data.get('page_id')

    @contextmanager
    def transaction(self):
        # Atomic replacement prevents torn JSON; a locked reload additionally
        # prevents a long-running client's stale copy from deleting newer stages.
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_name(self.path.name + '.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                if self.path.exists():
                    latest = json.loads(self.path.read_text())
                    if latest.get('schema_version') != 1:
                        raise ValueError('Unsupported state schema')
                    if self.requested_page and latest.get('page_id') not in (None, self.requested_page):
                        raise ValueError('State belongs to another page')
                    self.data = latest
                if self.requested_page:
                    self.data['page_id'] = self.requested_page
                self.page_id = self.data.get('page_id')
                yield
                atomic_json(self.path, self.data)
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _refresh(self) -> dict:
        stages = self.data['stages']
        for stage in STAGES:
            record = stages.get(stage)
            if not record or record['status'] != 'verified':
                continue
            reasons = []
            for key, saved in record['inputs'].items():
                if fingerprint(Path(saved['path'])) != saved:
                    reasons.append('changed or missing input: ' + key)
            for parent, version in record['parents'].items():
                current = stages.get(parent)
                # An absent stage remains unverified, without denying an independent
                # local check. Adding/replacing it later invalidates dependent evidence.
                if ((current and current['status'] != 'verified') or
                        (current.get('version') if current else None) != version):
                    reasons.append('upstream changed or unverified: ' + parent)
            if reasons:
                record.update(status='stale', reasons=reasons)
        return stages

    def refresh(self) -> dict:
        with self.transaction():
            return self._refresh()

    def record(self, stage: str, inputs: dict[str, Path], *, values: dict | None = None,
               evidence: list[str] | None = None, status: str = 'verified',
               depends_on: list[str] | None = None, expected_inputs: dict | None = None,
               expected_parents: dict | None = None):
        if stage not in STAGES or status not in ('verified', 'failed', 'not verified'):
            raise ValueError('Unsupported stage or status')
        dependencies = PARENTS[stage] if depends_on is None else depends_on
        if any(p not in STAGES[:STAGES.index(stage)] for p in dependencies):
            raise ValueError('Dependencies must precede the recorded stage')
        with self.transaction():
            fingerprints = {k: fingerprint(v) for k, v in inputs.items()}
            if any(v['sha256'] is None for v in fingerprints.values()):
                raise ValueError('Cannot record missing input files')
            if expected_inputs is not None and fingerprints != expected_inputs:
                raise ValueError('Inputs changed after the check; cannot certify current files')
            stages = self._refresh()
            parents = {p: stages[p]['version'] if p in stages else None for p in dependencies}
            if expected_parents is not None and any(parents.get(p) != v for p, v in expected_parents.items()):
                raise ValueError('Upstream candidate changed during verification')
            if stage in stages:
                self.data['history'].append({'stage': stage, **stages[stage]})
            stages[stage] = {
                'status': status, 'version': uuid.uuid4().hex,
                'recorded_at': datetime.now(timezone.utc).isoformat(),
                'inputs': fingerprints, 'values': values or {}, 'evidence': evidence or [],
                'parents': parents,
            }
            self._refresh()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    status = commands.add_parser('status')
    status.add_argument('--state', type=Path, required=True)
    record = commands.add_parser('record', help='Record externally observed Notion/HTML checks')
    record.add_argument('--state', type=Path, required=True)
    record.add_argument('--page-id', required=True)
    record.add_argument('--stage', choices=['notion', 'html'], required=True)
    record.add_argument('--inputs', type=Path, required=True,
                        help='JSON object mapping evidence/input names to file paths')
    record.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    ledger = Ledger(args.state, getattr(args, 'page_id', None))
    if args.command == 'record':
        if not args.evidence.is_file():
            parser.error('Evidence file does not exist')
        paths = json.loads(args.inputs.read_text())
        paths = {k: (args.inputs.parent / v).resolve() for k, v in paths.items()}
        paths['evidence'] = args.evidence.resolve()
        paths['input_mapping'] = args.inputs.resolve()
        ledger.record(args.stage, paths, evidence=[str(args.evidence.resolve())])
    states = ledger.refresh()
    print(json.dumps({s: states.get(s, {'status': 'not verified'}) for s in STAGES},
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
