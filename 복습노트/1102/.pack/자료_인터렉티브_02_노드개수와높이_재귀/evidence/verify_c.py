"""Compare displayed C (plain and instrumented) with every trace line using Clang."""
from pathlib import Path
import json
import subprocess
import sys
from tempfile import TemporaryDirectory

root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
traces = json.loads((root / 'trace.json').read_text())
cases = json.loads((root / 'evidence/inputs.json').read_text())
measures = traces['default']['id'] == 'tree-measure-1102'

def run(code, instrument, rows, mode, driver):
    definitions = """
#include <stddef.h>
#include <stdio.h>

typedef struct Node {
    int data;
    struct Node *left, *right;
} Node;

static Node nodes[7];
"""
    if not rows and not instrument:
        definitions = definitions.replace('static Node nodes[7];', '')
    if measures:
        definitions += 'static int max(int a, int b) { return a > b ? a : b; }\n'
    if instrument:
        definitions += r"""
static int depth;
static void log_step(int line, Node *node, int a, int b, int value) {
    fprintf(stderr, "%d %d %td %d %d %d\n", line, depth - 1,
            node ? node - nodes : 0, a, b, value);
}
"""
        # Add observations to the actual displayed statements. Keep their branch and
        # arithmetic expressions and print the same stdout as in the plain build.
        code = code.splitlines()
        flag = 'sum' if measures else 'pre'
        code[0] += f' depth++; log_step(0, p, {flag}, 0, 0);'
        code[1] = ('    log_step(2, p, 0, 0, 0); ' + code[1].strip().replace(
            'return 0;' if measures else 'return;',
            '{ depth--; return 0; }' if measures else '{ depth--; return; }'))
        if measures:
            code[2] += ' log_step(3, p, 0, 0, 0);'
            code[3] += ' log_step(4, p, 0, 0, l);'
            code[4] += ' log_step(5, p, 0, 0, r);'
            code[5] = '    log_step(6, p, sum, 0, 0); ' + code[5].strip()
            for offset in (6,7):
                statement = code[offset].strip()
                expression = statement.removeprefix('return ').removesuffix(';')
                code[offset] = f'{{ int v = {expression}; log_step({offset + 1}, p, l, r, v); depth--; return v; }}'
        else:
            for offset in (2,6):
                code[offset] = f'    log_step({offset + 1}, p, pre, 0, 0); ' + code[offset].strip()
            for offset in (3,7):
                code[offset] = '{ ' + code[offset] + f' log_step({offset + 1}, p, 0, 0, p->data); }}'
            code[8] = '    log_step(9, p, 0, 0, 0); depth--;\n}'
        code = '\n'.join(code)
    def ptr(node):
        return f'&nodes[{node}]' if node else 'NULL'
    initializers = [f'    nodes[{i}] = (Node){{{key}, {ptr(left)}, {ptr(right)}}};'
                    for i, key, left, right in rows]
    entry = '\n'.join(initializers + [f'Node *root = {ptr(rows[0][0] if rows else 0)};'])
    declaration = 'int result;' if measures else ''
    output = 'printf("%d", result);' if measures else ''
    program = f'{definitions}\n{code}\nint main(void) {{\n{entry}\n{declaration}\n{driver}\n{output}\n}}\n'
    with TemporaryDirectory() as temporary:
        source = Path(temporary) / 'oracle.c'
        executable = source.with_suffix('')
        source.write_text(program)
        subprocess.run(['clang', '-std=c11', '-O0', '-Wall', '-Wextra', '-Werror',
                        str(source), '-o', str(executable)], check=True)
        proc = subprocess.run([str(executable)], check=True, capture_output=True, text=True)
    return proc.stdout, [tuple(map(int, line.split())) for line in proc.stderr.splitlines()]

def checked_log(trace, mode):
    observed = []
    depth = -1
    calls = prints = returns = 0
    argument_links = {}
    for previous, step in zip(trace['lineSteps'], trace['lineSteps'][1:]):
        assert step['diagnostic'] is None
        state, before = step['state'], previous['state']
        frame_id = step['executed']['frameId']
        frame = state['frames'][frame_id]
        line = step['executed']['at']['line']
        active = state['activeFrame']
        cells = state['cells']
        def int_value(id):
            return cells[id]['value']['value']
        def node_id(target):
            return int(target.split('.')[0].removeprefix('node-')) if target else 0
        flag = 'sum' if measures else 'pre'
        if active != frame_id and state['frames'][active]['caller'] == frame_id:
            called = state['frames'][active]
            parameter = called['parameterCellId']
            source = called['argumentSourceCellId']
            assert source in step['reads']
            assert cells[parameter]['value'] == before['cells'][source]['value']
            assert cells[parameter]['owner'] == active
            assert cells[parameter]['lifetime'] == 'live'
            names = {write['cellId'] for write in step['writes']}
            assert parameter in names and f'{active}.{flag}' in names
            assert int_value(f'{active}.{flag}') == mode
            if frame_id == 'main':
                assert source == 'main.root'
            else:
                parent_target = before['cells'][frame['parameterCellId']]['value']['target']
                side = 'left' if line == (4 if measures else 5) else 'right'
                assert source == parent_target.replace('.data', '.' + side)
                assert f'{frame_id}.{flag}' in step['reads']
                assert frame['parameterCellId'] in step['reads']
                expected_resume = line + 1
                assert called['resumeAt']['line'] == expected_resume
                if measures:
                    assert cells[f'{frame_id}.{side[0]}']['value']['kind'] == 'uninitialized'
            depth += 1
            calls += 1
            argument_links[active] = source
            observed.append((0, depth, node_id(cells[parameter]['value']['target']), mode, 0, 0))
            continue

        parameter = frame['parameterCellId']
        node = node_id(before['cells'][parameter]['value']['target'])
        if line == 2:
            assert parameter in step['reads']
            observed.append((2, depth, node, 0, 0, 0))
        elif measures and line == 3:
            assert {item['cellId'] for item in step['writes']} == {f'{frame_id}.l', f'{frame_id}.r'}
            assert all(item['after']['kind'] == 'uninitialized' for item in step['writes'])
            observed.append((3, depth, node, 0, 0, 0))
        elif line in ((6,) if measures else (3,7)):
            assert f'{frame_id}.{flag}' in step['reads']
            observed.append((line, depth, node, mode, 0, 0))
        elif not measures and line in (4,8):
            printed = step['prints'][-1]
            assert len(step['prints']) == len(previous['prints']) + 1
            assert printed['cellId'] == before['cells'][parameter]['value']['target']
            assert parameter in step['reads'] and printed['cellId'] in step['reads']
            observed.append((line, depth, node, 0, 0, int(printed['text'])))
            prints += 1
        elif not measures:
            assert line == 9
            observed.append((9, depth, node, 0, 0, 0))

        if frame['lifetime'] == 'ended':
            assert active == frame['caller']
            assert all(cells[c]['lifetime'] == 'ended' for c in frame['cellIds'])
            assert (step['next']['at'] if step['next'] else None) == frame['resumeAt']
            if measures:
                caller = state['frames'][active]
                if active == 'main':
                    destination = 'main.result'
                else:
                    side = argument_links[frame_id].split('.')[-1]
                    destination = active + '.' + side[0]
                assert [item['cellId'] for item in step['writes']] == [destination]
                assert before['cells'][destination]['value']['kind'] == 'uninitialized'
                value = int_value(destination)
                if line == 2:
                    assert value == node == 0
                else:
                    lhs, rhs = f'{frame_id}.l', f'{frame_id}.r'
                    assert set(step['reads']) == {lhs, rhs}
                    observed.append((line, depth, node, int_value(lhs), int_value(rhs), value))
                if active != 'main':
                    parent = cells[caller['parameterCellId']]['value']['target']
                    observed.append((frame['callSite']['line'], depth-1, node_id(parent), 0, 0, value))
            depth -= 1
            returns += 1
    assert depth == -1 and calls == returns
    return observed, (calls, returns, prints)

report = []
for name, trace in traces.items():
    case = cases[trace['inputs']['exercise']]
    rows, mode = case['rows'], case['mode']
    code = trace['sources'][0]['text']
    driver = next(s['text'] for s in trace['sources'] if s['id'] == f'driver-{mode}')
    expected, raw = run(code, False, rows, mode, driver)
    captured, log = run(code, True, rows, mode, driver)
    observed, (calls, returns, prints) = checked_log(trace, mode)
    end = trace['lineSteps'][-1]['state']
    result = str(end['cells']['main.result']['value']['value']) if measures else ''.join(end['stdout'])
    assert not raw and expected == captured == result, (name, expected, captured, result)
    assert log == observed, (name, log, observed)
    assert calls == 2 * len(rows) + 1
    report.append(dict(case=name, mode=mode, calls=calls, returns=returns, prints=prints,
                       compared_c_checkpoints=len(log), observed_stdout=result,
                       meaning='root result (printed by harness)' if measures else 'traversal stdout',
                       c_checkpoints=log))
print(json.dumps({'compiler': subprocess.check_output(['clang','--version'],text=True).splitlines()[0],
                  'status':'pass', 'cases':report}, indent=2))
