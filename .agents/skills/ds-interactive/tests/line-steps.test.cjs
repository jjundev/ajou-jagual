const {test} = require('node:test');
const assert = require('node:assert/strict');
const {compileScenario} = require('../assets/engine/trace.js');
const {initialMemory, applyEvent} = require('../assets/engine/memory.js');
const legacy = require('../examples/0928/value-address.cjs');

const at = line => ({sourceId:'walk', line});
const pointer = {kind:'pointer', target:null};
const cell = (owner, name) => ({id:owner+'.'+name, owner, name, value:pointer, type:'Node *', address:'&'+owner+'.'+name});

function fixture(resumeLine = 4, from = 'parent.p') {
 let state = initialMemory();
 for (const event of [
  {kind:'call', frame:{id:'parent', functionId:'main'}},
  {kind:'enter', frameId:'parent'},
  {kind:'declare', cell:cell('parent','p')},
  {kind:'declare', cell:cell('parent','other')}
 ]) state = applyEvent(state,event).state;

 function* generateEvents(){
  const emit = (id, line, event) => ({lineStepId:id, at:at(line), ...event});
  yield emit('parent-test',2,{kind:'read', cellId:'parent.p'});
  yield emit('call',3,{kind:'read', cellId:'parent.p'});
  yield emit('call',3,{kind:'call', frame:{
   id:'child', functionId:'inorder', resumeAt:at(resumeLine),
   argumentSourceCellId:'parent.p', parameterCellId:'child.p'
  }});
  yield emit('call',3,{kind:'bind', cell:cell('child','p'), fromCellId:from, value:pointer});
  yield emit('call',3,{kind:'enter', frameId:'child'});
  yield emit('child-test',2,{kind:'read', cellId:'child.p'});
  yield emit('child-test',2,{kind:'return', frameId:'child'});
  yield emit('resume',4,{kind:'observe'});
 }
 return {
  id:'fixture', title:'fixture', kind:'c-tree', inputs:[], presets:[],
  tree:{rootCellId:'parent.p', fields:{key:'key',left:'left',right:'right'}},
  sources:[{id:'walk',text:'1\n2\n3\n4\n5'}],
  initialState:()=>state, generateEvents
 };
}

test('line steps preserve the caller across reused source lines', () => {
 const trace = compileScenario(fixture(),{});
 const [initial, parentTest, afterCall, afterReturn, terminal] = trace.lineSteps;
 assert.deepEqual(initial.next,{at:at(2),frameId:'parent'});
 assert.equal(parentTest.executed.frameId,'parent');
 assert.equal(afterCall.executed.frameId,'parent');
 assert.deepEqual(afterCall.next,{at:at(2),frameId:'child'});
 assert.deepEqual(afterCall.reads,['parent.p']);
 assert.deepEqual(afterCall.writes.map(w=>w.cellId),['child.p']);
 assert.equal(afterReturn.executed.frameId,'child');
 assert.deepEqual(afterReturn.next,{at:at(4),frameId:'parent'});
 assert.equal(afterReturn.state.cells['child.p'].lifetime,'ended');
 assert.equal(terminal.next,null);
 const input = Object.fromEntries(legacy.inputs.map(def=>[def.key,def.default]));
 const legacyTrace = compileScenario(legacy,input);
 assert.equal('lineSteps' in legacyTrace,false);
 assert.equal('eventKind' in legacyTrace.snapshots[1],false);
});

test('diagnostic ends an incomplete line without presenting a partial call', () => {
 for (const limits of [{steps:4},{steps:5},{depth:1}]) {
  const trace = compileScenario(fixture(),{},limits);
  const interrupted = trace.lineSteps.at(-1);
  assert.equal(interrupted.diagnostic.code,'LIMIT_REACHED');
  assert.equal(interrupted.next,null);
  assert.equal(interrupted.state.activeFrame,'parent');
  assert.equal(interrupted.state.frames.child,undefined);
  assert.deepEqual(interrupted.writes,[]);
 }
});

test('invalid resume lines and wrong bind sources cannot produce a projected trace', () => {
 assert.throws(()=>compileScenario(fixture(5),{}),{code:'LINE_STEP_INVALID'});
 assert.throws(()=>compileScenario(fixture(4,'parent.other'),{}),{code:'LINE_STEP_INVALID'});
});
