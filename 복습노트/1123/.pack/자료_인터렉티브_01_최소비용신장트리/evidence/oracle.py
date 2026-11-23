"""Independent verifier for the S10 MST examples. Run with trace.json."""
from itertools import combinations
from pathlib import Path
import json
import sys


EDGES = ('af', 'cd', 'bg', 'bc', 'dg', 'de', 'eg', 'ef', 'ab')
VERTICES = set('abcdefg')


def reachable(start, chosen):
    reached = {start}
    while True:
        expanded = reached | {end for a, b in chosen for begin, end in [(a, b), (b, a)] if begin in reached}
        if expanded == reached:
            return reached
        reached = expanded


def verify(traces):
    answers = {}
    for case, trace in traces.items():
        prim = trace['inputs']['mode'] == 'prim'
        weights = dict(zip(EDGES, [10, 12, 15, 16, 18, 22, 25, 27,
                                  27 if trace['inputs']['setup'] == 'tie' else 29]))
        trees = [subset for subset in combinations(EDGES, 6) if reachable('a', subset) == VERTICES]
        best = min(sum(weights[edge] for edge in tree) for tree in trees)
        examined = []
        chosen = []
        rejected = []
        candidate = None
        cheaper = []
        snapshots = trace['snapshots']
        assert snapshots[0]['phase'] == 'before'
        for index, snapshot in enumerate(snapshots):
            line = snapshot['at']['line']
            cells = snapshot['state']['cells']
            values = {key: cell['value']['value'] for key, cell in cells.items()}
            assert snapshot['at']['sourceId'] == trace['inputs']['mode']
            assert snapshot['diagnostic'] is None
            if index and line == 3:
                candidate = EDGES[values['candidate']]
                if prim:
                    inside = reachable('a', chosen)
                    choices = [e for e in EDGES if len(set(e) & inside) == 1]
                    minimum = min(weights[e] for e in choices)
                    assert candidate in choices and weights[candidate] == minimum
                    cheaper.append([candidate, choices])
                else:
                    eligible = sorted(set(EDGES) - set(examined), key=lambda e: (weights[e], EDGES.index(e)))
                    assert candidate == eligible[0]
                examined.append(candidate)
            elif index and not prim and line == 4:
                assert not snapshot['writes'] and candidate == examined[-1]
            elif index and ((prim and line == 4) or (not prim and line in [5, 6])):
                connected = candidate[1] in reachable(candidate[0], chosen)
                assert connected == (line == 6)
                (rejected if connected else chosen).append(candidate)
            elif index:
                assert line == (5 if prim else 7) and index == len(snapshots) - 1
                assert len(chosen) == 6
            assert values['candidate'] == (EDGES.index(candidate) if candidate else -1)
            assert [values['edge.' + str(e)] for e in range(9)] == [
                chosen.index(edge) + 1 if edge in chosen else -1 if edge in rejected else 0 for edge in EDGES
            ]
        assert sum(weights[edge] for edge in chosen) == best == 102
        answers[case] = {'examined': examined, 'chosen': chosen, 'rejected': rejected,
                         'prim_boundaries': cheaper, 'minimum_cost': best, 'trees_enumerated': len(trees),
                         'minimum_trees': sum(sum(weights[e] for e in tree) == best for tree in trees),
                         'verified_snapshots': len(snapshots)}
    assert set(answers['default']['chosen']) == set(answers['lecture-prim']['chosen'])
    assert set(answers['tie-kruskal']['chosen']) != set(answers['tie-prim']['chosen'])
    return answers


if __name__ == '__main__':
    print(json.dumps(verify(json.loads(Path(sys.argv[1]).read_text())), indent=2))
