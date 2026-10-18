"""Independent table oracle for the 1012 stack materials.

Does not import or read the scenario events/expected values. It recomputes, from the
C source semantics, every bind/declare/allocate/write the program performs and the
first undefined-behaviour point, then compares with traces compiled by the public engine.
Usage: python -I independent_1012.py SKILL_DIR RUN_DIR
"""
import json, subprocess, sys, shutil, itertools
from pathlib import Path

I = lambda v: {'kind': 'int', 'value': v}
P = lambda t: {'kind': 'pointer', 'target': t}
U = {'kind': 'uninitialized'}
X = {'kind': 'indeterminate'}
NAMES = ['A', 'B', 'C']


def linked_push(x):
    item, n, mode = x['item'], x['n'], x['mode']
    old = NAMES[n - 1] if n else None
    rows = [['f.s', P('s')], ['f.item', I(item)], ['f.temp', U],
            ['D', U], ['D.link', U], ['f.temp', P('D')],   # malloc success
            ['D', I(item)]]                                 # temp->item = item
    if mode == 'correct':
        rows += [['D.link', P(old)], ['s', P('D')]]        # link first, then top
    else:
        rows += [['s', P('D')], ['D.link', P('D')]]        # top first: link reads new top
    # push returns: its locals end; no live pointer targets them.
    reachable, seen = [], set()
    final = dict(rows)
    ptr = final['s']['target']
    while ptr and ptr not in seen and len(reachable) < 10:
        seen.add(ptr); reachable.append(ptr)
        ptr = final['D.link']['target'] if ptr == 'D' else (NAMES[NAMES.index(ptr) - 1] if ptr != 'A' else None)
    leaked = [k for k in NAMES[:n] if k not in reachable]
    return rows, None, {'s': final['s'], 'D.link': final['D.link'], 'D': final['D']}, {'reachable_from_top': reachable, 'leaked': leaked, 'cycle': ptr in seen}


def linked_pop(x):
    top, n, mode = x['top'], x['n'], x['mode']
    rows = [['f.s', P('s')], ['e.s', P('s')]]               # pop(&s); is_empty(s) copies f.s
    if n == 0:                                              # is_empty -> 1 -> exit(1)
        return rows, None, {'x': U, 's': P(None)}, {'exit': True}
    T, N = NAMES[n - 1], (NAMES[n - 2] if n > 1 else None)
    rows.append(['f.temp', P(T)])                           # temp = s->top
    if mode == 'correct':
        rows += [['f.item', I(top)], ['s', P(N)], ['f.temp', X], ['x', I(top)]]
        return rows, None, {'x': I(top), 's': P(N)}, {}
    if mode == 'late-read':
        rows += [['s', P(N)], ['f.temp', X]]                # free(temp) then temp->item
        return rows, 'INDETERMINATE_READ', {'x': U, 's': P(N)}, {}
    rows += [['f.item', I(top)], ['s', X], ['f.temp', X]]   # free before moving top: both aliases dead
    return rows, 'INDETERMINATE_READ', {'x': U, 's': X}, {}


def array_stack(x):
    item, n, mode = x['item'], x['n'], x['mode']
    VALUES = [7, 9, 5, 1, 6]
    arr = [I(VALUES[i]) if i < n else U for i in range(5)]
    slot = lambda i: 's' if i == 0 else f's.stack[{i}]'
    top = n - 1
    rows = [['p.s', P('s')], ['p.item', I(item)], ['fu.s', P('s')]]
    if top != 4:
        if mode == 'correct':
            top += 1; rows.append(['s.top', I(top)]); arr[top] = I(item); rows.append([slot(top), I(item)])
        else:
            if top < 0:
                return rows, 'OUT_OF_BOUNDS', {'s.top': I(-1), 'x': U}, {}
            arr[top] = I(item); rows.append([slot(top), I(item)]); top += 1; rows.append(['s.top', I(top)])
    rows += [['q.s', P('s')], ['em.s', P('s')]]
    if arr[top] == U:
        return rows, 'UNINITIALIZED_READ', {'s.top': I(top), 'x': U}, {}
    got = arr[top]; top -= 1
    rows += [['s.top', I(top)], ['x', got]]
    return rows, None, {'s.top': I(top), 'x': got}, {}


ORACLES = {'linked-push': linked_push, 'linked-pop': linked_pop, 'array-stack': array_stack}


def verify(trace):
    actual = [[w['cellId'], w['after']] for s in trace['snapshots'] for w in s['writes']]
    rows, diag, final, extra = ORACLES[trace['id']](trace['inputs'])
    assert actual == rows, (trace['inputs'], actual, rows)
    last = trace['snapshots'][-1]
    got = last['diagnostic']['code'] if last['diagnostic'] else None
    assert got == diag, (trace['inputs'], got, diag)
    for cid, v in final.items():
        assert last['state']['cells'][cid]['value'] == v, (trace['inputs'], cid, last['state']['cells'][cid]['value'], v)
    if trace['id'] == 'linked-push':
        live = {c: o for c, o in last['state']['objects'].items() if o['storage'] == 'allocated' and o['lifetime'] == 'live'}
        assert set(live) == set(NAMES[:trace['inputs']['n']]) | {'D'}
    if trace['id'] == 'linked-pop' and diag is None and trace['inputs']['n']:
        T = NAMES[trace['inputs']['n'] - 1]
        assert last['state']['objects'][T]['lifetime'] == 'ended'
    return {'input': trace['inputs'], 'writes_checked': len(actual), 'diagnostic': got, 'final': final, **extra, 'status': 'pass'}


GRID = {
    'linked-push': {'item': [-99, -1, 0, 1, 10, 30, 99], 'n': [0, 1, 2, 3], 'mode': ['correct', 'wrong']},
    'linked-pop': {'top': [-99, -1, 0, 10, 30, 99], 'n': [0, 1, 2, 3], 'mode': ['correct', 'late-read', 'free-first']},
    'array-stack': {'item': [-99, -1, 0, 4, 9, 99], 'n': [0, 1, 2, 3, 4, 5], 'mode': ['correct', 'wrong']},
}

if __name__ == '__main__':
    skill, run = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
    scenario = run / 'scenario.cjs'
    presets = json.loads(subprocess.check_output(['node', str(skill / 'scripts/steps.cjs'), str(scenario)], encoding='utf8'))
    sid = next(iter(presets.values()))['id']
    grid = [dict(zip(GRID[sid], combo)) for combo in itertools.product(*GRID[sid].values())]
    js = "const s=require(process.argv[1]),e=require(process.argv[2]);console.log(JSON.stringify(JSON.parse(process.argv[3]).map(x=>e.compileScenario(s,x))));"
    traces = json.loads(subprocess.check_output(['node', '-e', js, str(scenario), str(skill / 'assets/engine/trace.js'), json.dumps(grid)], encoding='utf8'))
    cases = [{'case': k, **verify(t)} for k, t in presets.items()] + [{'case': 'grid', **verify(t)} for t in traces]
    result = {'method': 'independent Python C-semantics table (bind/declare/allocate/write order, free aliasing, diagnostics, final cells)',
              'topic': sid, 'compiler_unavailable': not any(shutil.which(c) for c in ['gcc', 'clang', 'cl', 'cc']),
              'compiler_note': 'gcc/clang/cl/cc not on PATH; WSL has no gcc; Docker engine not running. UB paths are never executed.',
              'total': len(cases), 'cases': cases, 'status': 'pass'}
    out = run / 'evidence'; out.mkdir(exist_ok=True)
    (out / 'independent.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    shutil.copyfile(__file__, out / 'independent_1012.py')
    print(json.dumps({'topic': sid, 'status': 'pass', 'cases': len(cases)}))
