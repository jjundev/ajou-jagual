"""Independent table oracle for the 0921 interactive materials.

Does not import the scenario's events or expected values. For each input it re-executes
the C program's semantics in plain Python (recursion, array index loop, struct field copy)
and records every bind/declare/write the program performs plus the first point where
execution must stop (undefined behaviour or the call-depth guard). It then compares
that table with traces compiled by the public engine CLI (steps.cjs / compileScenario).
Usage: python -I independent_0921.py SKILL_DIR RUN_DIR
"""
import json, subprocess, sys, shutil, itertools
from pathlib import Path

I = lambda v: {'kind': 'int', 'value': v}
P = lambda t: {'kind': 'pointer', 'target': t}
U = {'kind': 'uninitialized'}
INT_MAX, INT_MIN = 2**31 - 1, -2**31
DEPTH = 64  # engine call-depth guard (main counts as one live frame)


def factorial(x):
    n, mode = x['n'], x['mode']
    rows = []

    class Stop(Exception):
        pass

    def call(k, value, slot):
        # live frames before this call: main + (k-1) factorial frames
        if 1 + (k - 1) >= DEPTH:
            raise Stop('LIMIT_REACHED')
        fid = f'f{k}'
        rows.append([f'{fid}.n', I(value)])                 # parameter n = copied argument
        if mode == 'lecture' and value <= 1:
            rows.append([slot, I(1)]); return 1             # base case returns 1 to caller slot
        rows.append([f'{fid}.ret', U])                      # visual slot for factorial(n-1)
        r = call(k + 1, value - 1, f'{fid}.ret')
        prod = value * r
        if prod > INT_MAX or prod < INT_MIN:
            raise Stop('SIGNED_OVERFLOW')
        rows.append([slot, I(prod)]); return prod

    try:
        r = call(1, n, 'r'); return rows, None, {'r': I(r)}
    except Stop as s:
        return rows, str(s), {'r': U}


CASES = {   # 'k' = B's constant term from the integer input
    'note': ((5, [10, 0, 0, 0, 6, 3]), (3, [10, 3, 0, 'k'])),
    'same': ((3, [8, 0, 7, 1]), (3, [10, 3, 0, 'k'])),
    'bigb': ((1, [6, 3]), (3, [10, 3, 0, 'k'])),
    'cancel': ((2, [3, 0, 1]), (2, [-3, 5, 'k'])),
    'constant': ((0, [7]), (0, ['k'])),
}


def poly(x):
    (Ad, Ac), (Bd, Bc) = CASES[x['case']]
    Bc = [x['k'] if c == 'k' else c for c in Bc]
    A = Ac + [0] * (6 - len(Ac)); B = Bc + [0] * (6 - len(Bc))   # missing initializers are 0
    rows = []
    w = lambda c, v: rows.append([c, I(v)])
    Apos = Bpos = Cpos = 0; w('Apos', 0); w('Bpos', 0); w('Cpos', 0)
    da, db = Ad, Bd; w('degree_a', da); w('degree_b', db)
    w('C.degree', Ad if Ad > Bd else Bd)
    C = {}
    while Apos <= Ad and Bpos <= Bd:
        if da > db:
            C[Cpos] = A[Apos]; w(f'C.coef[{Cpos}]', A[Apos]); w('Cpos', Cpos + 1); w('Apos', Apos + 1)
            Cpos += 1; Apos += 1; da -= 1; w('degree_a', da)
        elif da == db:
            s = A[Apos] + B[Bpos]; assert INT_MIN <= s <= INT_MAX
            C[Cpos] = s; w(f'C.coef[{Cpos}]', s); w('Cpos', Cpos + 1); w('Apos', Apos + 1); w('Bpos', Bpos + 1)
            Cpos += 1; Apos += 1; Bpos += 1; da -= 1; w('degree_a', da); db -= 1; w('degree_b', db)
        else:
            C[Cpos] = B[Bpos]; w(f'C.coef[{Cpos}]', B[Bpos]); w('Cpos', Cpos + 1); w('Bpos', Bpos + 1)
            Cpos += 1; Bpos += 1; db -= 1; w('degree_b', db)
    post = 0
    while Apos <= Ad:
        w(f'C.coef[{Cpos}]', A[Apos]); w('Cpos', Cpos + 1); w('Apos', Apos + 1); Cpos += 1; Apos += 1; post += 1
    while Bpos <= Bd:
        w(f'C.coef[{Cpos}]', B[Bpos]); w('Cpos', Cpos + 1); w('Bpos', Bpos + 1); Cpos += 1; Bpos += 1; post += 1
    final = {'C.degree': I(max(Ad, Bd)), 'Apos': I(Apos), 'Bpos': I(Bpos), 'Cpos': I(Cpos)}
    final.update({f'C.coef[{i}]': I(v) for i, v in C.items()})
    final.update({f'C.coef[{i}]': U for i in range(6) if i not in C})
    return rows, None, final, {'post_processing_iterations': post}


def struct(x):
    a, b, mode = x['x'], x['y'], x['mode']
    if mode == 'uninit':   # person a, b; b = a;  -> first field read of an uninitialized object
        return [], 'UNINITIALIZED_READ', {'b.age': U, 'b.height': U}
    if mode == 'copy':
        rows = [['a.age', I(a)], ['a.height', I(b)],          # initializer
                ['b.age', I(a)], ['b.height', I(b)],          # b = a : field by field
                ['a.age', I(a + 1)]]                          # a.age = a.age + 1 (b untouched)
        return rows, None, {'a.age': I(a + 1), 'a.height': I(b), 'b.age': I(a), 'b.height': I(b)}
    rows = [['n2.data', I(b)], ['n2.link', P(None)], ['n1.data', I(a)], ['n1.link', P('n2.data')],
            ['c.data', I(a)], ['c.link', P('n2.data')],      # c = n1 : pointer value copied, n2 shared
            ['c.data', I(a + 1)], ['n2.data', I(0)],          # c.link->data = 0 writes n2
            ['seen', I(0)]]                                   # n1.link->data sees the same n2
    return rows, None, {'n1.data': I(a), 'n1.link': P('n2.data'), 'c.data': I(a + 1), 'c.link': P('n2.data'), 'n2.data': I(0), 'seen': I(0)}


ORACLES = {'factorial-frames': factorial, 'poly-add-index': poly, 'struct-assign-copy': struct}


def verify(trace):
    topic = trace['id']; out = ORACLES[topic](trace['inputs'])
    rows, diag, final = out[0], out[1], out[2]; extra = out[3] if len(out) > 3 else {}
    actual = [[w['cellId'], w['after']] for s in trace['snapshots'] for w in s['writes']]
    assert actual == rows, (topic, trace['inputs'], actual[:12], rows[:12])
    got = trace['snapshots'][-1]['diagnostic']; got = got['code'] if got else None
    assert got == diag, (topic, trace['inputs'], got, diag)
    cells = trace['snapshots'][-1]['state']['cells']
    for k, v in final.items():
        assert cells[k]['value'] == v, (topic, trace['inputs'], k, cells[k]['value'], v)
    return {'case': trace.get('_case'), 'input': trace['inputs'], 'writes_checked': len(actual), 'diagnostic': diag,
            'final': final, **extra, 'status': 'pass'}


def grid(scenario):
    s = json.loads(subprocess.check_output(['node', '-e', "const s=require(process.argv[1]);console.log(JSON.stringify(s.inputs))", str(scenario)], encoding='utf8'))
    vals = []
    for d in s:
        if d['type'] == 'enum': vals.append([o['value'] for o in d['options']])
        else: vals.append(sorted({d['min'], d['max'], d['default'], -3, -1, 0, 1, 7, 12, 13, 14, 63, 64} & set(range(d['min'], d['max'] + 1))))
    return [dict(zip([d['key'] for d in s], combo)) for combo in itertools.product(*vals)]


if __name__ == '__main__':
    skill, run = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(); scenario = run / 'scenario.cjs'
    traces = json.loads(subprocess.check_output(['node', str(skill / 'scripts/steps.cjs'), str(scenario)], encoding='utf8'))
    reports = []
    for case, t in traces.items():
        t['_case'] = case; reports.append(verify(t))
    js = "const s=require(process.argv[1]),e=require(process.argv[2]);const xs=JSON.parse(process.argv[3]);console.log(JSON.stringify(xs.map(x=>e.compileScenario(s,x))))"
    inputs = grid(scenario)
    for t in json.loads(subprocess.check_output(['node', '-e', js, str(scenario), str(skill / 'assets/engine/trace.js'), json.dumps(inputs)], encoding='utf8')):
        t['_case'] = 'grid'; reports.append(verify(t))
    topic = next(iter(traces.values()))['id']
    result = {'method': 'independent Python C-semantics table (every bind/declare/write in order, stop point, final cells)',
              'topic': topic, 'compiler_unavailable': not any(shutil.which(c) for c in ['gcc', 'clang', 'cl', 'cc', 'tcc']),
              'compiler_note': 'gcc/clang/cl/cc/tcc not on PATH; no Visual Studio/MSYS2/MinGW install; WSL has only docker-desktop distro; Docker engine not running. UB paths are never executed.',
              'total': len(reports), 'cases': reports, 'status': 'pass'}
    (run / 'evidence' / 'independent.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({'topic': topic, 'status': 'pass', 'cases': len(reports), 'writes': sum(r['writes_checked'] for r in reports)}))
