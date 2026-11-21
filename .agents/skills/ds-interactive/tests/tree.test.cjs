const {test} = require('node:test');
const assert = require('node:assert/strict');
const {initialMemory, applyEvent} = require('../assets/engine/memory.js');
const {compileScenario} = require('../assets/engine/trace.js');
const treeEngine = globalThis.DSInteractive;
const tree = {rootCellId:'main.root', fields:{key:'key',left:'left',right:'right'}};
const pointer = target => ({kind:'pointer',target});
const cell = (owner,name,value) => ({id:owner+'.'+name, name, owner, value, address:'&'+owner+'.'+name});

function fixture(){
 let state=initialMemory();
 function apply(event){const result=applyEvent(state,event); assert.equal(result.diagnostic,null); state=result.state;}
 function node(id,left){
  const cells=[cell(id,'key',{kind:'int',value:7}),cell(id,'left',pointer(left)),cell(id,'right',pointer(null))];
  apply({kind:'allocate',object:{id,cellIds:cells.map(c=>c.id)},cells});
 }
 node('left',null);
 node('root','left.key');
 apply({kind:'call',frame:{id:'main',functionId:'main'}});
 apply({kind:'enter',frameId:'main'});
 apply({kind:'declare',cell:cell('main','root',pointer('root.key'))});
 return {state,prints:[]};
}

test('identical keys keep different output labels',()=>{
 const step=fixture();
 step.prints=[{cellId:'left.key',text:'7 '},{cellId:'root.key',text:'7 '}];
 step.state.stdout=['7 ','7 '];
 const view=treeEngine.getTreeView(tree,step);
 assert.deepEqual(view.nodes.map(n=>[n.id,n.outputOrder]).sort(),[['left',1],['root',2]]);
 assert.equal(view.activeNodeId,null);
});

test('null activation identifies the exact child edge and an empty root draws no nodes',()=>{
 const step=fixture();
 step.state.activeFrame='null';
 step.state.frames.null={id:'null',caller:'main',lifetime:'live',cellIds:['null.p'],
  parameterCellId:'null.p',argumentSourceCellId:'left.left',resumeAt:{sourceId:'walk',line:4}};
 step.state.cells['null.p']={...cell('null','p',pointer(null)),lifetime:'live'};
 const view=treeEngine.getTreeView(tree,step);
 assert.deepEqual(view.nullEdge,{nodeId:'left',side:'left'});
 assert.equal(view.stack[0].parameterCellId,'null.p');
 const empty=fixture();
 empty.state.cells['main.root'].value=pointer(null);
 assert.equal(treeEngine.getTreeView(tree,empty).rootId,null);
 assert.deepEqual(treeEngine.getTreeView(tree,empty).nodes,[]);
});

test('tree links reject cycles, shared children and interior destinations',()=>{
 for(const [id,target] of [['left.left','root.key'],['root.right','left.key'],['root.left','left.right']]){
  const step=fixture();
  step.state.cells[id].value=pointer(target);
  assert.throws(()=>treeEngine.getTreeView(tree,step),{code:'TREE_INVALID'});
 }
 const sample=fixture();
 assert.throws(()=>compileScenario({
  kind:'c-tree',id:'bad-tree',inputs:[],presets:[],sources:[{id:'walk',text:'1'}],
  initialState:()=>sample.state,generateEvents:()=>[],tree:{...tree,rootCellId:'missing'}
 },{}),{code:'TREE_INVALID'});
});
