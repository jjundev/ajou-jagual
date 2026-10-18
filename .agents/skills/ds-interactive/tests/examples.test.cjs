const {test}=require('node:test'),a=require('node:assert/strict');
const {compileScenario,checkScenario}=require('../assets/engine/trace.js');
const load=id=>require('../examples/0928/'+id+'.cjs');
const defaults=s=>Object.fromEntries(s.inputs.map(d=>[d.key,d.default]));
function run(id,input={}){const s=load(id);return compileScenario(s,{...defaults(s),...input});}
const last=t=>t.snapshots.at(-1).state.cells;
test('swap compares value copy, address copy and alias; all integer boundaries',()=>{
 const s=load('value-address');a.equal(checkScenario(s).ok,true);
 for(const [av,bv]of [[1,2],[-99,99],[99,-99],[3,3]]){
  let c=last(run('value-address',{a:av,b:bv,mode:'value'}));a.equal(c['main.a'].value.value,av);a.equal(c['main.b'].value.value,bv);
  c=last(run('value-address',{a:av,b:bv,mode:'address'}));a.equal(c['main.a'].value.value,bv);a.equal(c['main.b'].value.value,av);
  c=last(run('value-address',{a:av,b:bv,mode:'alias'}));a.equal(c['main.a'].value.value,av);a.equal(c['main.b'].value.value,bv);
 }
});
test('pointer target changes then local pointer becomes NULL, caller pointer retains target',()=>{
 const t=run('pointer-target');a.equal(checkScenario(load('pointer-target')).ok,true);a.equal(last(t)['main.a'].value.value,20);a.equal(last(t)['main.q'].value.target,'main.a');
 const nul=t.snapshots.find(x=>x.writes.some(w=>w.cellId==='f.p'&&w.after.kind==='pointer'&&w.after.target===null));a.equal(nul.state.cells['main.q'].value.target,'main.a');
 a.equal(run('pointer-target',{mode:'null'}).snapshots.at(-1).diagnostic.code,'NULL_DEREFERENCE');
 for(const v of [-99,99])a.equal(last(run('pointer-target',{a:v,value:v}))['main.a'].value.value,v);
});
test('double pointer changes caller q while single pointer only rebinds callee',()=>{
 a.equal(checkScenario(load('double-pointer')).ok,true);
 for(const [mode,target] of [['single','main.a'],['double','main.b']]){const c=last(run('double-pointer',{mode}));a.equal(c['main.q'].value.target,target);a.equal(c['main.a'].value.value,10);a.equal(c['main.b'].value.value,20);}
 a.equal(run('double-pointer',{mode:'null'}).snapshots.at(-1).diagnostic.code,'NULL_DEREFERENCE');
});
test('displayed source uses current input and starts on the active code variant',()=>{
 const t=run('value-address',{a:-99,b:99,mode:'value'});a.ok(t.sources.find(s=>s.id==='value').text.includes('int a = -99, b = 99;'));a.equal(t.snapshots[0].at.sourceId,'value');
});
