"""Independent verifier for the S10 topological-sort examples. Run with trace.json."""
from pathlib import Path
import json
import sys


EDGES = [(0, 2), (0, 3), (1, 3), (1, 4), (2, 3), (2, 5), (3, 5), (4, 5), (5, 0)]
EXPECTED = {'default': [0, 1, 2, 3, 4, 5], 'slide': [1, 4, 0, 2, 3, 5], 'cycle': [1, 4]}


def verify(traces):
    answers = {}
    for case, trace in traces.items():
        original = EDGES if case == 'cycle' else EDGES[:-1]
        remaining = set(range(6))
        active = set(original)
        expected = EXPECTED[case]
        candidate = -1
        output = []
        failure = False
        table = []

        def degrees():
            return {v: sum(to == v for _, to in active) for v in sorted(remaining)}

        def ready():
            return [v for v, count in degrees().items() if count == 0]

        for index, snapshot in enumerate(trace['snapshots']):
            line = snapshot['at']['line']
            values = {key: cell['value']['value'] for key, cell in snapshot['state']['cells'].items()}
            assert snapshot['diagnostic'] is None and snapshot['at']['sourceId'] == 'topo'
            if not index:
                table.append({'initial': degrees(), 'ready': ready()})
            elif line == 3:
                candidate = expected[len(output)]
                assert candidate in ready()
            elif line == 4:
                assert candidate not in output and candidate in ready()
                output.append(candidate)
            elif line == 5:
                [write] = snapshot['writes']
                arrow = EDGES[int(write['cellId'].split('.')[1])]
                assert arrow[0] == candidate and candidate == output[-1]
                before = degrees()[arrow[1]]
                active.remove(arrow)
                assert degrees()[arrow[1]] == before - 1
                table.append({'removed_arrow': arrow, 'target_degree': degrees()[arrow[1]]})
            elif line == 6:
                assert not any(edge[0] == candidate for edge in active)
                remaining.remove(candidate)
                assert active == {(a, b) for a, b in original if a in remaining and b in remaining}
                table.append({'removed_vertex': candidate, 'degrees': degrees(), 'ready': ready()})
            elif line == 2:
                assert remaining and not ready() and case == 'cycle'
                assert {(0, 2), (2, 5), (5, 0)} <= active
                assert len(trace['snapshots']) - 1 == index
                failure = True
            else:
                assert line == 7 and not remaining and not active and len(trace['snapshots']) - 1 == index

            assert values['candidate'] == candidate
            assert values['failure'] == failure
            assert [values['node.' + str(v)] for v in range(6)] == [int(v in remaining) for v in range(6)]
            assert [values['edge.' + str(i)] for i in range(len(EDGES))] == [int(e in active) for e in EDGES]
            assert [int(v) for v in snapshot['state']['stdout']] == output
        assert output == expected
        if failure:
            assert remaining == {0, 2, 3, 5} and degrees() == {0: 1, 2: 1, 3: 2, 5: 2}
        else:
            assert all(output.index(a) < output.index(b) for a, b in original)
        answers[case] = {'output': output, 'cycle': failure, 'verified_snapshots': len(trace['snapshots']),
                         'steps': table}
    assert answers['slide']['output'] != answers['default']['output']
    return answers


if __name__ == '__main__':
    print(json.dumps(verify(json.loads(Path(sys.argv[1]).read_text())), indent=2))
