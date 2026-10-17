const {test}=require('node:test'),a=require('node:assert/strict');
function scenario(events){return {version:1,id:'tiny',title:'tiny',kind:'c-memory',sources:[{id:'c',text:'int a;\na = 1;',language:'c'}],inputs:[],presets:[],initialState:()=>({frames:{},objects:{},cells:{},activeFrame:null,stdout:[]}),generateEvents:()=>events.map(e=>({at:{sourceId:'c',line:2},explanation:'observe',...e})),expected:[]};}
test('trace is deterministic, immutable, stops at diagnostics and enforces step limits',()=>{
 const {compileScenario,validateTrace}=require('../assets/engine/trace.js');const s=scenario([{kind:'observe',label:'ready'},{kind:'diagnostic',code:'ORDER_UNSPECIFIED',message:'hold'},{kind:'observe',label:'never'}]);
 const t=compileScenario(s,{});a.equal(t.snapshots.length,3);a.equal(t.snapshots.at(-1).diagnostic.code,'ORDER_UNSPECIFIED');a.deepEqual(t,compileScenario(s,{}));a.ok(Object.isFrozen(t.snapshots[1].state));a.deepEqual(validateTrace(t),[]);
 const limited=compileScenario(scenario(Array.from({length:5},()=>({kind:'observe'}))),{},{steps:3});a.equal(limited.snapshots.length,3);a.equal(limited.snapshots.at(-1).diagnostic.code,'LIMIT_REACHED');
 const bad=structuredClone(t);bad.snapshots[0].at.line=99;a.ok(validateTrace(bad).some(i=>i.code==='LOCATION_INVALID'));
});
test('trace validator catches writes inconsistent with state and bad pointer targets',()=>{
 const {compileScenario,validateTrace}=require('../assets/engine/trace.js');const t=structuredClone(compileScenario(scenario([{kind:'observe'}]),{}));
 t.snapshots[1].writes=[{cellId:'missing',before:null,after:{kind:'int',value:2}}];a.ok(validateTrace(t).length);
});
