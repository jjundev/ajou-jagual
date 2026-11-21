"""Compare the authored trace to observations from a separately compiled C traversal."""

import difflib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


def observed_trace(trace):
    def object_for(cell_id, state):
        target = state['cells'][cell_id]['value']['target']
        return 'NULL' if target is None else state['cells'][target]['owner']

    def argument(frame, state):
        caller = state['frames'][frame['caller']]
        parent_cell = caller.get('parameterCellId')
        parent = object_for(parent_cell, state) if parent_cell else 'NULL'
        side = state['cells'][frame['argumentSourceCellId']]['name']
        return parent, side

    observations = []
    for previous, snapshot in zip(trace['snapshots'], trace['snapshots'][1:]):
        assert snapshot['diagnostic'] is None
        state = snapshot['state']
        kind = snapshot['eventKind']
        where = snapshot['at']
        frame = state['frames'][snapshot['frameIdBefore']]
        if kind == 'enter':
            assert where['sourceId'] in ('driver', 'walk')
            entered = state['frames'][state['activeFrame']]
            target = object_for(entered['parameterCellId'], state)
            assert target == object_for(entered['argumentSourceCellId'], previous['state'])
            parent, side = argument(entered, state)
            event = 'call'
        elif kind == 'read' and where == {'sourceId': 'walk', 'line': 2}:
            assert frame['parameterCellId'] in snapshot['reads']
            event = 'test'
        elif kind == 'print-int':
            event = 'print'
        elif kind == 'return':
            event = 'return'
        else:
            continue

        if event != 'call':
            target = object_for(frame['parameterCellId'], state)
            parent, side = argument(frame, state)
            if event == 'print':
                info = snapshot['printed']
                assert state['cells'][info['cellId']]['owner'] == target
                assert info['text'] == state['stdout'][-1]
            if event == 'return':
                assert state['activeFrame'] == frame['caller']
                assert state['cells'][frame['parameterCellId']]['lifetime'] == 'ended'
        observations.append(f"{event} {where['sourceId']} {where['line']} {target} {parent} {side}")
    return observations


def main(trace_path):
    traces = json.loads(trace_path.read_text())
    assert set(traces) == {'default', 'lecture', 'empty'}

    with tempfile.TemporaryDirectory() as folder:
        program = Path(folder) / 'inorder-oracle'
        source = Path(__file__).parent / 'fixtures' / 'inorder_oracle.c'
        compiler = shlex.split(os.environ.get('CC', 'cc'))
        subprocess.run([*compiler, '-std=c11', '-Wall', '-Wextra', '-Werror', str(source), '-o', str(program)], check=True)
        cases = {}
        for case, trace in traces.items():
            run = subprocess.run([str(program), case], capture_output=True, text=True, check=True)
            expected = run.stderr.splitlines()
            observed = observed_trace(trace)
            assert observed == expected, '\n'.join(difflib.unified_diff(expected, observed, 'C', 'Trace'))
            assert ''.join(trace['snapshots'][-1]['state']['stdout']) == run.stdout
            cases[case] = {'matched': True, 'events': len(expected), 'stdout': run.stdout}
        print(json.dumps({'compiler': compiler, 'cases': cases}, indent=2))


if __name__ == '__main__':
    main(Path(sys.argv[1]))
