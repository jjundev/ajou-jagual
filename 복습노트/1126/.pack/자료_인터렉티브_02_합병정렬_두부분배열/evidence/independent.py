"""Compile source with observation points and compare C's ordered accesses to trace.json."""
import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

run = Path(sys.argv[1])
topic = sys.argv[2]
traces = json.loads((run/'trace.json').read_text())
source = (run/'source.c').read_text()

def arm(code, old, new):
    assert code.count(old) == 1, old
    return code.replace(old, new)

header = r'''#include <stdio.h>
static int read_cell(const int *values, int i, const char *name) {
    printf("R %s.%d\n", name, i);
    return values[i];
}
static void write_cell(int *values, int i, int value, const char *name) {
    values[i] = value;
    printf("W %s.%d %d\n", name, i, value);
}
#define READ(array, i) read_cell(array, i, #array)
#define WRITE(array, i, value) write_cell(array, i, value, #array)
#define SCALAR(name) printf("W f.%s %d\n", #name, name)
'''
# Inside the given C loop, record evaluation of the array operand after its bounds check.
if topic == 'partition':
    data = [[5,3,8,4,9,1,6,2,7], [5,5,8,5,9,1,6,5,7], list(range(1,10)), list(range(9,0,-1))]
    header += r'''#define SWAP_AT(a, b) do { \
    temp = READ(list, a); SCALAR(temp); \
    WRITE(list, a, READ(list, b)); \
    WRITE(list, b, temp); \
} while (0)
'''
    code = source
    for name, line in [('low', 'low = left;'), ('high', 'high = right + 1;'),
                       ('pivot', 'pivot = list[left];'), ('low', 'low++;'), ('high', 'high--;')]:
        if line.endswith('++;') or line.endswith('--;'):
            replacement = '{ ' + line + ' SCALAR(' + name + '); }'
        else:
            replacement = line.replace('list[left]', 'READ(list, left)') + ' SCALAR(' + name + ');'
        code = arm(code, line, replacement)
    code = code.replace('list[low] < pivot', 'READ(list, low) < pivot').replace('list[high] > pivot', 'READ(list, high) > pivot')
    code = arm(code, 'SWAP(list[low], list[high], temp)', 'SWAP_AT(low, high)')
    code = arm(code, 'SWAP(list[left], list[high], temp)', 'SWAP_AT(left, high)')
    functions = code
    action = 'int q = partition(list, 0, 8); printf("W main.q %d\\n", q);'
    scalars = {'f.pivot','f.temp','f.low','f.high','main.q'}
else:
    data = [[10,27,12,20], [1,2,7,9], [2,5,2,3], [2,5,2,3]]
    header += '''static int take_left(int *list, int b1, int b2, int inclusive) {
    int a = READ(list, b1);
    int b = READ(list, b2);
    return inclusive ? a <= b : a < b;
}
'''
    code = arm(source, 'list[b1] < list[b2]', 'take_left(list, b1, b2, 0)')
    for name in ('b1', 'b2'):
        code = code.replace(f'sorted[index] = list[{name}];', f'WRITE(sorted, index, READ(list, {name}));')
        code = code.replace(f'{name}++;', f'{name}++; SCALAR({name});')
    code = code.replace('index++;', 'index++; SCALAR(index);')
    for name, stmt in [('b1','int b1 = left;'), ('b2','int b2 = mid + 1;'), ('index','int index = 0;')]:
        code = arm(code, stmt, stmt + f' SCALAR({name});')
    code = arm(code, 'for (int i = 0; i < index; i++)\n        list[left + i] = sorted[i];',
               'for (int i = 0; i < index; i++) {\n        if (i == 0) SCALAR(i);\n        WRITE(list, left + i, READ(sorted, i));\n        printf("W f.i %d\\n", i + 1);\n    }')
    functions = code + '\n' + code.replace('void merge(', 'void merge_stable(').replace('take_left(list, b1, b2, 0)', 'take_left(list, b1, b2, 1)')
    action = 'if (c == 3) merge_stable(list, 0, 1, 3); else merge(list, 0, 1, 3);'
    scalars = {'f.b1','f.b2','f.i','f.index'}

def is_array(cell):
    return cell.startswith(('list.', 'sorted.'))

initializers = ',\n        '.join('{' + ', '.join(map(str, values)) + '}' for values in data)
length = len(data[0])
main = f'''
int main(void) {{
    int cases[][ {length} ] = {{
        {initializers}
    }};
    for (int c = 0; c < 4; c++) {{
        printf("CASE %d\\n", c);
        int *list = cases[c];
        {action}
        printf("OUT");
        for (int i = 0; i < {length}; i++) printf(" %d", list[i]);
        printf("\\n");
    }}
}}
'''
# Validate the literal source as a separate translation unit before compiling the instrumented copy.
with TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    plain = tmp/'source.c'
    plain.write_text(('#define SWAP(a,b,t) ((t)=(a),(a)=(b),(b)=(t))\n' if topic == 'partition' else '') + source)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-c',str(plain),'-o',str(tmp/'source.o')], check=True)
    c = run/'evidence/observe.c'
    c.write_text(header + functions + main)
    binary = tmp/'observe'
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined',
                    '-fno-sanitize-recover=undefined', str(c),'-o',str(binary)], check=True)
    output = subprocess.check_output([str(binary)], text=True)
(run/'evidence/c-accesses.txt').write_text(output)
actual = ['CASE ' + entry for entry in output.split('CASE ')[1:]]
for i, ((key, trace), oracle, values) in enumerate(zip(traces.items(), actual, data, strict=True)):
    steps = trace['snapshots']
    def values_of(step):
        return [step['state']['cells'][f'list.{j}']['value']['value'] for j in range(length)]
    assert values_of(steps[0]) == values
    expected = [f'CASE {i}']
    for step in steps:
        expected.extend(f'R {cell}' for cell in step['reads'] if is_array(cell))
        expected.extend(f'W {w["cellId"]} {w["after"]["value"]}' for w in step['writes']
                        if w['after']['kind'] == 'int' and (is_array(w['cellId']) or w['cellId'] in scalars))
    final = values_of(steps[-1])
    expected.append('OUT ' + ' '.join(map(str, final)))
    actual_lines = oracle.splitlines()
    if expected != actual_lines:
        from difflib import unified_diff
        raise AssertionError('\n'.join(unified_diff(actual_lines, expected, fromfile='C', tofile='Trace')))
    print(f'{key}: {len(expected)-2} ordered accesses and final array agree with C11: {final}')
