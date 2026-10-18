const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),p=require('node:path'),os=require('node:os');
test('step limit stops consuming an event generator before unbounded author work',()=>{
 const {compileScenario}=require('../assets/engine/trace.js');const s={version:1,id:'gen',kind:'c-memory',title:'gen',sources:[{id:'c',text:'x'}],inputs:[],presets:[],initialState:()=>({frames:{},objects:{},cells:{},activeFrame:null,stdout:[]}),*generateEvents(){for(let n=0;n<3;n++)yield {kind:'observe',at:{sourceId:'c',line:1},explanation:'step'};throw Error('read beyond limit');}};
 const t=compileScenario(s,{},{steps:3});a.equal(t.snapshots.length,3);a.equal(t.snapshots.at(-1).diagnostic.code,'LIMIT_REACHED');
});
test('nested evidence bytes are covered by review hashes',()=>{
 const {currentHashes}=require('../scripts/review.cjs'),dir=fs.mkdtempSync(p.join(os.tmpdir(),'ds-hash-'));try{fs.mkdirSync(p.join(dir,'evidence/browser'),{recursive:true});fs.writeFileSync(p.join(dir,'evidence/browser/screen.png'),'pixels');a.ok(currentHashes(dir)['evidence/browser/screen.png']);}finally{fs.rmSync(dir,{force:true,recursive:true});}
});
test('default depth and object limits accept their last slot and stop the next allocation',()=>{
 const {initialMemory,applyEvent}=require('../assets/engine/memory.js');let state=initialMemory();
 for(let n=0;n<64;n++){let r=applyEvent(state,{kind:'call',frame:{id:'f'+n,functionId:'f',cellIds:[]}});a.equal(r.diagnostic,null);state=applyEvent(r.state,{kind:'enter',frameId:'f'+n}).state;}
 a.equal(applyEvent(state,{kind:'call',frame:{id:'overflow',cellIds:[]}}).diagnostic.code,'LIMIT_REACHED');
 for(let n=0;n<256;n++){const r=applyEvent(state,{kind:'allocate',object:{id:'o'+n,type:'int',storage:'allocated',cellIds:['c'+n]},cells:[{id:'c'+n,name:'n',type:'int',owner:'o'+n,address:'&c'+n,value:{kind:'int',value:n},lifetime:'live'}],resultCellId:null});a.equal(r.diagnostic,null);state=r.state;}
 a.equal(applyEvent(state,{kind:'allocate',object:{id:'excess',cellIds:[]},cells:[]}).diagnostic.code,'LIMIT_REACHED');
});
test('automatic struct copies fields shallowly, array parameter binds an address and return ends only copied fields',()=>{
 const {initialMemory,applyEvent}=require('../assets/engine/memory.js');let state=initialMemory();const apply=e=>{const r=applyEvent(state,e);a.equal(r.diagnostic,null);state=r.state;};
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),cell=(id,owner,value)=>({id,name:id.split('.').at(-1),type:value.kind==='pointer'?'int *':'int',owner,address:'&'+id,value,lifetime:'live'});
 apply({kind:'call',frame:{id:'main',functionId:'main',cellIds:[]}});apply({kind:'enter',frameId:'main'});
 apply({kind:'allocate',object:{id:'array',type:'int[2]',storage:'automatic',cellIds:['arr.0','arr.1']},cells:[cell('arr.0','array',I(4)),cell('arr.1','array',I(5))],resultCellId:null});
 apply({kind:'allocate',object:{id:'original',type:'struct Node',storage:'automatic',cellIds:['s.count','s.link']},cells:[cell('s.count','original',I(1)),cell('s.link','original',P('arr.0'))],resultCellId:null});
 apply({kind:'call',frame:{id:'f',functionId:'copy',cellIds:[]}});apply({kind:'enter',frameId:'f'});
 apply({kind:'allocate',object:{id:'copy',type:'struct Node',storage:'automatic',cellIds:['copy.count','copy.link']},cells:[cell('copy.count','copy',I(1)),cell('copy.link','copy',P('arr.0'))],resultCellId:null});
 apply({kind:'bind',cell:cell('f.array','f',P('arr.0')),value:P('arr.0')});apply({kind:'write',cellId:'copy.count',value:I(9)});apply({kind:'write',cellId:'arr.0',through:['copy.link'],value:I(7)});
 a.equal(state.cells['s.count'].value.value,1);a.equal(state.cells['s.link'].value.target,'arr.0');a.equal(state.cells['arr.0'].value.value,7);a.ok(state.frames.f.cellIds.includes('copy.link'));
 apply({kind:'return',frameId:'f'});a.equal(state.objects.copy.lifetime,'ended');a.equal(state.objects.original.lifetime,'live');a.equal(state.cells['arr.0'].lifetime,'live');
});
