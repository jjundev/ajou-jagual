const {test}=require('node:test'),a=require('node:assert/strict');
const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target});
const cell=(id,value,owner='main')=>({id,name:id.split('.').at(-1),type:value.kind==='pointer'?'int *':'int',owner,address:`&${id}`,value,lifetime:'live'});
function setup(){const {initialMemory,applyEvent}=require('../assets/engine/memory.js');let s=initialMemory();
 const apply=e=>{const r=applyEvent(s,{at:{sourceId:'c',line:1},explanation:'test',...e});s=r.state;return r;};
 apply({kind:'call',frame:{id:'main',functionId:'main',cellIds:[],lifetime:'live'}});apply({kind:'enter',frameId:'main'});
 for(const c of [cell('main.a',I(10)),cell('main.b',I(20)),cell('main.q',P('main.a'))])apply({kind:'declare',cell:c});
 return {apply,get state(){return s;}};
}
test('parameter copy, aliases and double pointer writes retain caller identities',()=>{
 const x=setup(),old=structuredClone(x.state);
 x.apply({kind:'call',frame:{id:'f1',functionId:'f',cellIds:[],lifetime:'live'}});
 for(const [id,v] of [['x',I(10)],['p',P('main.a')],['r',P('main.a')],['pp',P('main.q')]])x.apply({kind:'bind',cell:cell('f1.'+id,v,'f1'),value:v});
 x.apply({kind:'enter',frameId:'f1'});x.apply({kind:'write',cellId:'f1.x',value:I(99)});
 a.equal(x.state.cells['main.a'].value.value,10);
 x.apply({kind:'write',cellId:'main.a',through:['f1.p'],value:I(30)});
 a.equal(x.state.cells['main.a'].value.value,30);a.equal(x.state.cells['f1.r'].value.target,'main.a');
 x.apply({kind:'write',cellId:'f1.p',value:P(null)});a.equal(x.state.cells['main.q'].value.target,'main.a');
 x.apply({kind:'write',cellId:'main.q',through:['f1.pp'],value:P('main.b')});a.equal(x.state.cells['main.q'].value.target,'main.b');
 a.equal(old.cells['main.a'].value.value,10);
 a.equal(x.apply({kind:'read',cellId:'main.b',through:['f1.r']}).diagnostic.code,'TARGET_MISMATCH');
});
test('automatic lifetime and allocated lifetime invalidate every alias; NULL free is a no-op',()=>{
 const x=setup();x.apply({kind:'declare',cell:cell('main.nil',P(null))});a.equal(x.apply({kind:'free',pointerCellId:'main.nil'}).diagnostic,null);
 x.apply({kind:'allocate',object:{id:'heap1',type:'int',storage:'allocated',cellIds:['h.0'],lifetime:'live'},cells:[cell('h.0',I(1),'heap1')],resultCellId:'main.q'});
 x.apply({kind:'declare',cell:cell('main.alias',P('h.0'))});x.apply({kind:'free',pointerCellId:'main.q'});
 a.equal(x.state.cells['main.alias'].value.kind,'indeterminate');a.equal(x.state.cells['h.0'].lifetime,'ended');
 a.equal(x.apply({kind:'read',cellId:'main.alias'}).diagnostic.code,'INDETERMINATE_READ');
 x.apply({kind:'call',frame:{id:'f',functionId:'f',cellIds:[],lifetime:'live'}});x.apply({kind:'enter',frameId:'f'});
 x.apply({kind:'declare',cell:cell('f.local',I(1),'f')});x.apply({kind:'write',cellId:'main.q',value:P('f.local')});x.apply({kind:'return',frameId:'f'});
 a.equal(x.state.cells['main.q'].value.kind,'indeterminate');a.equal(x.state.activeFrame,'main');
 a.equal(x.apply({kind:'call',frame:{id:'f',functionId:'f',cellIds:[]}}).diagnostic.code,'DUPLICATE_ID');
});
test('array cells and struct fields use independent storage and shallow pointer copies',()=>{
 const x=setup();x.apply({kind:'allocate',object:{id:'array',type:'int[2]',storage:'allocated',cellIds:['arr.0','arr.1'],lifetime:'live'},cells:[cell('arr.0',I(4),'array'),cell('arr.1',I(5),'array')],resultCellId:'main.q'});
 x.apply({kind:'declare',cell:cell('main.next',P('arr.1'))});x.apply({kind:'declare',cell:cell('main.copy',P('arr.1'))});
 x.apply({kind:'write',cellId:'arr.1',through:['main.copy'],value:I(9)});a.equal(x.state.cells['main.next'].value.target,'arr.1');a.equal(x.state.cells['arr.1'].value.value,9);
 a.equal(x.apply({kind:'free',pointerCellId:'main.next'}).diagnostic.code,'INVALID_FREE');
 a.equal(x.apply({kind:'read',cellId:'arr.2'}).diagnostic.code,'OUT_OF_BOUNDS');
});
test('null, uninitialized, inactive returns and depth/object limits diagnose',()=>{
 const x=setup();x.apply({kind:'declare',cell:cell('main.u',{kind:'uninitialized'})});a.equal(x.apply({kind:'read',cellId:'main.u'}).diagnostic.code,'UNINITIALIZED_READ');
 x.apply({kind:'write',cellId:'main.q',value:P(null)});a.equal(x.apply({kind:'read',cellId:'main.a',through:['main.q']}).diagnostic.code,'NULL_DEREFERENCE');
 a.equal(x.apply({kind:'return',frameId:'missing'}).diagnostic.code,'INVALID_RETURN');
 const {applyEvent}=require('../assets/engine/memory.js');a.equal(applyEvent(x.state,{kind:'call',frame:{id:'next',cellIds:[]}},{depth:1}).diagnostic.code,'LIMIT_REACHED');
 a.equal(applyEvent(x.state,{kind:'allocate',object:{id:'h',cellIds:[]},cells:[]},{objects:0}).diagnostic.code,'LIMIT_REACHED');
});
module.exports={setup,cell,I,P};
