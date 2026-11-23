"""Compile the displayed C routine with observation hooks and compare each read/add."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

run = Path(sys.argv[1])
source = (run / 'source.c').read_text()
original = source
for axis, expression in enumerate(('m[v][i]', 'm[i][v]')):
    statement = f'sum[{axis}] += {expression};'
    assert source.count(statement) == 1
    source = source.replace(statement, f'{{ int before = sum[{axis}]; {statement}'
                            f'printf("%d %d %d %d\\n", {axis}, i, before, sum[{axis}]); }}')
driver = r'''
int main(void) {
    int g3[N][N] = {{0,1,0},{1,0,1},{0,0,0}};
    int empty[N][N] = {{0}};
    for (int test = 0; test < 4; ++test) {
        int sum[2] = {0};
        int v = test == 1 ? 2 : test == 2 ? 0 : 1;
        printf("case %d\n", test);
        degrees(test == 3 ? empty : g3, v, sum);
        printf("end %d %d\n", sum[0], sum[1]);
    }
}
'''
outputs = []
with tempfile.TemporaryDirectory() as folder:
    for body in (original, source):
        c_file = Path(folder) / 'verify.c'
        exe = c_file.with_suffix('')
        c_file.write_text('#include <stdio.h>\n' + body + driver)
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        str(c_file), '-o', str(exe)], check=True)
        outputs.append(subprocess.check_output([exe], text=True).splitlines())
assert outputs[0] == [line for line in outputs[1] if line.startswith(('case', 'end'))]
traces = json.loads((run / 'trace.json').read_text())
assert set(traces) == {'default', 'sink', 'reciprocal', 'empty'}
destinations = [(2, 1), (0, 1), (1, 1), (0, 0)]
lines = iter(outputs[1])
for case_id, key in enumerate(('default', 'sink', 'reciprocal', 'empty')):
    trace = traces[key]
    assert next(lines) == f'case {case_id}'
    assert all(not s['diagnostic'] for s in trace['snapshots'])
    operations = [s for s in trace['snapshots'] if s['reads'] or s['writes']]
    assert len(operations) == 12
    v = (1, 2, 0, 1)[case_id]
    for read, write in zip(operations[::2], operations[1::2]):
        axis, i, before, after = map(int, next(lines).split())
        a, b = (i, v) if axis else (v, i)
        cell = f'm.{a}.{b}'
        assert read['reads'] == [cell], (key, cell, read['reads'])
        assert read['state']['cells'][cell]['value']['value'] == after - before
        assert len(write['writes']) == 1
        change = write['writes'][0]
        assert change['cellId'] == ('in' if axis else 'out')
        assert (change['before']['value'], change['after']['value']) == (before, after)
    out, incoming = destinations[case_id]
    assert next(lines) == f'end {out} {incoming}'
    final = trace['snapshots'][-1]['state']['cells']
    assert (final['out']['value']['value'], final['in']['value']['value']) == (out, incoming)
    print(key, 'all 6 C reads and additions matched', out, incoming)
