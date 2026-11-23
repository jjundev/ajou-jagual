"""Compare trail playback with fixed routes and enumerate all legal outcomes."""
import json
import sys
from pathlib import Path

bridges = dict(zip('abcdefgh', ['AB', 'AB', 'AC', 'AC', 'AD', 'BD', 'CD', 'CD']))
cases = {
    'default': ('abcdefg', 'A', 'abcdef', (5, 3, 3, 3), None),
    'two-odd': ('bcdefg', 'C', 'cbfedg', (4, 2, 3, 3), 'D'),
    'even': ('bcdef', 'A', 'bfecd', (4, 2, 2, 2), 'A'),
    'split': ('abgh', 'A', 'ab', (2, 2, 2, 2), None),
}


def endpoints(at, left):
    if not left:
        return {at}
    ends = set()
    for bridge in sorted(left):
        a, b = bridges[bridge]
        if at == a or at == b:
            ends |= endpoints(b if at == a else a, left - {bridge})
    return ends


traces = json.loads(Path(sys.argv[1]).read_text())
assert set(traces) == cases.keys()
for key, (edges, start, route, degrees, end) in cases.items():
    snapshots = traces[key]['snapshots']
    assert tuple(sum(v in bridges[e] for e in edges) for v in 'ABCD') == degrees
    assert endpoints(start, set(edges)) == ({end} if end else set())
    actual = []
    at = start
    for snapshot in snapshots:
        cells = snapshot['state']['cells']
        assert not snapshot['diagnostic']
        assert cells['start']['value']['value'] == 'ABCD'.index(start)
        for write in snapshot['writes']:
            edge = write['cellId'].split('.')[-1]
            a, b = bridges[edge]
            assert edge in edges and edge not in actual and at in (a, b)
            assert write['before']['value'] == 0
            assert write['after']['value'] == len(actual) + 1
            at = b if at == a else a
            actual.append(edge)
        assert {e: cells['order.' + e]['value']['value'] for e in edges} == {
            e: actual.index(e) + 1 if e in actual else 0 for e in edges
        }
    assert ''.join(actual) == route, (key, actual)
    assert not any(at in bridges[e] for e in set(edges) - set(actual))
    print(key, 'degrees', degrees, 'played', route, 'final vertex', at, 'legal finish', end)
