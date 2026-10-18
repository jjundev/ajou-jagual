"""Independent oracle for the 1008 materials.

Recomputes, from the inputs alone, every value copy (bind/declare/allocate) and write the C code
performs, then checks the final list/stack with plain Python lists. It never imports the JS engine
and never reads Scenario.expected; node is used only to obtain the Trace under test.
usage: python -I independent_1008.py SKILL_DIR RUN_DIR TOPIC OUT_JSON
"""
import json, shutil, subprocess, sys
from pathlib import Path

I = lambda v: {'kind': 'int', 'value': v}
P = lambda t: {'kind': 'pointer', 'target': t}
U = {'kind': 'uninitialized'}
X = {'kind': 'indeterminate'}
VALUES = [10, 20, 30, 40, 50]


def nd(k, n):
    return f'n{k}.data' if 1 <= k <= n else None


def walk(n, pos):
    """get_node_at(list, pos): rows written while walking, and the returned node."""
    rows = [['get.list', P('list1.head')], ['get.pos', I(pos)], ['get.i', U], ['get.tmp_node', P(nd(1, n))]]
    if pos < 0:
        return rows, None
    rows.append(['get.i', I(0)])
    cur = 1
    for i in range(pos):
        cur += 1
        rows += [['get.tmp_node', P(nd(cur, n))], ['get.i', I(i + 1)]]
    return rows, nd(cur, n)


def oracle_add(n, position, data):
    rows = [['add.list', P('list1.head')], ['add.position', I(position)], ['add.data', I(data)], ['add.p', U]]
    model = VALUES[:n]
    if not (0 <= position <= n):
        return rows, None, model
    rows += [['add.node', U], ['new.data', U], ['new.link', U], ['add.node', P('new.data')], ['new.data', I(data)]]
    w, prev = walk(n, position - 1)
    rows += w + [['add.p', P(prev)], ['ins.phead', P('list1.head')], ['ins.p', P(prev)], ['ins.new_node', P('new.data')]]
    if n == 0:
        rows += [['new.link', P(None)], ['list1.head', P('new.data')]]
    elif prev is None:
        rows += [['new.link', P('n1.data')], ['list1.head', P('new.data')]]
    else:
        k = int(prev[1])
        rows += [['new.link', P(nd(k + 1, n))], [f'n{k}.link', P('new.data')]]
    rows.append(['list1.length', I(n + 1)])
    model = model[:position] + [data] + model[position:]
    return rows, None, model


def oracle_delete(n, pos, mode):
    rows = [['del.list', P('list1.head')], ['del.pos', I(pos)], ['emp.list', P('list1.head')]]
    model = VALUES[:n]
    if not (n > 0 and 0 <= pos < n):
        return rows, None, model
    rows.append(['del.p', U])
    w, prev = walk(n, pos - 1)
    rows += w + [['del.p', P(prev)]]
    removed = nd(pos + 1, n) if prev else ('n1.data' if mode == 'fixed' else None)
    rows += [['rm.phead', P('list1.head')], ['rm.p', P(prev)], ['rm.removed', P(removed)]]
    if prev is None:
        rows.append(['list1.head', P(nd(2, n))])
    else:
        rows.append([f'{prev.split(".")[0]}.link', P(nd(pos + 2, n))])
    if removed:  # free() invalidates the only live alias, removed itself
        rows.append(['rm.removed', X])
    rows.append(['list1.length', I(n - 1)])
    return rows, None, model[:pos] + model[pos + 1:]


def oracle_stack(n, x, op):
    t = n - 1
    fn, cid = ('pop', 'emp') if op == 'pop' else ('push', 'full')
    rows = [['main.e', U]] if op == 'pop' else []
    rows.append([f'{fn}.s', P('s.stack[0]')])
    if op != 'pop':
        rows.append(['push.item', I(x)])
    rows.append([f'{cid}.s', P('s.stack[0]')])
    model = VALUES[:n]
    if op != 'pop' and n == 5:
        return rows, None, model
    if op == 'pop' and n == 0:
        return rows, 'PROGRAM_EXIT', model
    if op == 'push':
        rows += [['s.top', I(t + 1)], [f's.stack[{t + 1}]', I(x)]]
        return rows, None, model + [x]
    if op == 'wrong':
        if t < 0:
            return rows, 'OUT_OF_BOUNDS', model
        rows += [[f's.stack[{t}]', I(x)], ['s.top', I(t + 1)]]
        return rows, None, model[:t] + [x, None]
    rows += [['s.top', I(t - 1)], ['main.e', I(VALUES[t])]]
    return rows, None, model[:-1]


def final_list(state):
    cells = state['cells']
    out, cur, seen = [], cells['list1.head']['value']['target'], set()
    while cur:
        assert cur not in seen and cells[cur]['lifetime'] == 'live', cur
        seen.add(cur)
        out.append(cells[cur]['value']['value'])
        cur = cells[cur.replace('.data', '.link')]['value']['target']
    assert len(out) == cells['list1.length']['value']['value'], 'length mismatch'
    return out


def unreachable_live_nodes(state):
    """Allocated objects still live but pointed to by no live cell."""
    cells, objs = state['cells'], state['objects']
    targets = {c['value']['target'] for c in cells.values() if c['lifetime'] == 'live' and c['value']['kind'] == 'pointer'}
    return sorted(o['id'] for o in objs.values() if o['storage'] == 'allocated' and o['lifetime'] == 'live' and o['cellIds'][0] not in targets)


def final_stack(state):
    cells = state['cells']
    top = cells['s.top']['value']['value']
    return [cells[f's.stack[{i}]']['value'].get('value') for i in range(top + 1)]


def verify(topic, trace):
    x = trace['inputs']
    if topic == 'list-add':
        rows, diag, model = oracle_add(x['n'], x['position'], x['data'])
    elif topic == 'list-delete':
        rows, diag, model = oracle_delete(x['n'], x['pos'], x['mode'])
    else:
        rows, diag, model = oracle_stack(x['n'], x['x'], x['op'])
    actual = [[w['cellId'], w['after']] for s in trace['snapshots'] for w in s['writes']]
    assert actual == rows, (topic, x, actual, rows)
    last = trace['snapshots'][-1]
    got = last['diagnostic']['code'] if last['diagnostic'] else None
    assert got == diag, (topic, x, got, diag)
    report = {'input': x, 'writes_checked': len(rows), 'diagnostic': got}
    state = last['state']
    if topic == 'array-stack':
        if not diag:
            assert final_stack(state) == model, (x, final_stack(state), model)
            if x['op'] == 'pop' and x['n'] > 0:
                assert state['cells']['main.e']['value'] == I(VALUES[x['n'] - 1])
        report['final_stack'] = model
    else:
        got_list = final_list(state)
        assert got_list == model, (x, got_list, model)
        leak = unreachable_live_nodes(state)
        want_leak = ['n1'] if topic == 'list-delete' and x['mode'] == 'original' and x['pos'] == 0 and x['n'] > 0 else []
        assert leak == want_leak, (x, leak, want_leak)
        freed = sorted(o['id'] for o in state['objects'].values() if o['lifetime'] == 'ended')
        if topic == 'list-delete' and x['n'] > 0 and 0 <= x['pos'] < x['n'] and not want_leak:
            assert freed == [f"n{x['pos'] + 1}"], (x, freed)
        else:
            assert freed == [], (x, freed)
        report.update(final_list=model, leaked=leak, freed=freed)
    report['status'] = 'pass'
    return report


GRID = {
    'list-add': lambda: [{'n': n, 'position': p, 'data': d} for n in range(4) for p in (-99, -1, 0, 1, 2, 3, 4, 99) for d in (-99, 0, 99)],
    'list-delete': lambda: [{'n': n, 'pos': p, 'mode': m} for n in range(4) for p in (-99, -1, 0, 1, 2, 3, 99) for m in ('original', 'fixed')],
    'array-stack': lambda: [{'n': n, 'x': v, 'op': o} for n in range(6) for v in (-99, 0, 99) for o in ('push', 'pop', 'wrong')],
}

if __name__ == '__main__':
    skill, run, topic, out = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
    scenario = (run / 'scenario.cjs').resolve()
    presets = json.loads(subprocess.check_output(['node', str(skill / 'scripts/steps.cjs'), str(scenario)], encoding='utf8'))
    reports = [dict(case=k, **verify(topic, t)) for k, t in presets.items()]
    js = ("const s=require(process.argv[1]),e=require(process.argv[2]),g=JSON.parse(process.argv[3]);"
          "console.log(JSON.stringify(g.map(x=>e.compileScenario(s,x))));")
    grid = json.loads(subprocess.check_output(['node', '-e', js, str(scenario), str(skill / 'assets/engine/trace.js'), json.dumps(GRID[topic]())], encoding='utf8'))
    reports += [dict(case='grid', **verify(topic, t)) for t in grid]
    result = {'method': 'independent Python write/bind table + final list/stack model', 'topic': topic,
              'compiler_unavailable': not any(shutil.which(c) for c in ['gcc', 'clang', 'cl', 'tcc']),
              'ub_executed': False, 'total': len(reports), 'writes': sum(r['writes_checked'] for r in reports),
              'cases': reports, 'status': 'pass'}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps({k: result[k] for k in ('topic', 'total', 'writes', 'compiler_unavailable', 'status')}, ensure_ascii=False))
