const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {applyEvent, initialMemory} = require('../assets/engine/memory.js');

function renderChanges() {
  const el = (tag, className, text) => ({
    tag, className, text, children: [],
    append(...children) { this.children.push(...children); },
    replaceChildren(...children) { this.children = children; },
  });
  const DSInteractive = {
    applyEvent, el,
    format: value => ({
      int: value?.value?.toString(),
      uninitialized: '미초기화',
      indeterminate: '사용 불가',
      pointer: value?.target === null ? 'NULL' : '&' + value?.target,
    })[value?.kind],
  };
  const source = require.resolve('../assets/panel-changes.js');
  vm.runInNewContext(fs.readFileSync(source, 'utf8'), {DSInteractive});
  return {
    apply: DSInteractive.applyEvent,
    rows(result) {
      const container = el('div');
      DSInteractive.renderPanelChanges(container, result);
      return container.children.map(row => row.children.map(child => child.text));
    },
  };
}

test('cell origin distinguishes parameter binding, declaration, writes, and allocation', () => {
  const {apply, rows} = renderChanges();
  const int = value => ({kind:'int', value});
  const frame = {id:'f', functionId:'search', cellIds:[], lifetime:'live'};
  const cell = (id, owner='f', type='int') => ({id, owner, name:id, type, lifetime:'live'});
  let {state} = apply(initialMemory(), {kind:'call', frame});
  const step = event => {
    const result = apply(state, event);
    assert.equal(result.diagnostic, null);
    state = result.state;
    return result;
  };

  const vertex = step({kind:'bind', cell:cell('v'), value:int(0), label:'정점 번호 전달'});
  assert.deepEqual(rows(vertex), [['v (정점 번호)', '전달 전 → 0']]);

  const initialized = step({kind:'declare', cell:{...cell('w'), value:int(0)}});
  assert.deepEqual(rows(initialized), [['w', '선언 전 → 0']]);
  const update = step({kind:'write', cellId:'w', value:int(1)});
  assert.deepEqual(rows(update), [['w', '0 → 1']]);

  // A tree can group a declaration and a later write into one displayed source line.
  const grouped = {...update, writes:[{...update.writes[0], before:initialized.writes[0].before}]};
  assert.deepEqual(rows(grouped), [['w', '선언 전 → 1']]);

  const empty = {kind:'uninitialized'};
  assert.deepEqual(rows(step({kind:'declare', cell:{...cell('p','f','Node *'), value:empty}})),
    [['p', '선언 전 → 미초기화']]);
  const node = {id:'node', type:'Node', storage:'allocated', cellIds:['data']};
  assert.deepEqual(rows(step({kind:'allocate', object:node, cells:[
    {...cell('data','node'), address:'&new.data', value:empty},
  ], resultCellId:'p'})), [['data', '할당 전 → 미초기화'], ['p', '미초기화 → &new.data']]);
});

test('pointer bindings show the graph object or the authored target address', () => {
  const {apply, rows} = renderChanges();
  const state = initialMemory();
  state.frames.f = {id:'f', functionId:'search', cellIds:['x'], lifetime:'live'};
  state.objects.graph = {id:'graph', type:'GraphType', storage:'static', cellIds:['graph.a.0.0']};
  const value = {kind:'int', value:0};
  state.cells['graph.a.0.0'] = {id:'graph.a.0.0', owner:'graph', value, lifetime:'live'};
  state.cells.x = {id:'x', owner:'f', value, address:'&main.x', lifetime:'live'};
  const bind = (name, target) => apply(state, {
    kind:'bind', cell:{id:name, name, owner:'f', lifetime:'live'}, value:{kind:'pointer', target},
  });
  assert.deepEqual(rows(bind('g','graph.a.0.0')), [['g (그래프 포인터)', '전달 전 → 그래프 주소']]);
  assert.deepEqual(rows(bind('p','x')), [['p', '전달 전 → &main.x']]);
  assert.deepEqual(rows(bind('p',null)), [['p', '전달 전 → NULL']]);
});
