(function(root){
 'use strict';
 const clone=x=>structuredClone(x);
 const initialMemory=()=>({frames:{},objects:{},cells:{},activeFrame:null,stdout:[]});
 function applyEvent(original,e,limits={}){
  const state=clone(original),reads=[],writes=[];
  const fault=(code,message)=>{throw {dsFault:true,code,message};};
  function get(id){const c=state.cells[id];if(!c)fault('OUT_OF_BOUNDS',`저장 공간 ${id}가 없습니다. 배열 경계와 대상을 확인하세요.`);if(c.lifetime!=='live')fault('LIFETIME_ENDED',`${id}의 수명이 끝났습니다.`);return c;}
  function read(id){const c=get(id);if(c.value.kind==='uninitialized')fault('UNINITIALIZED_READ',`${c.name}: 초기화되지 않은 값입니다.`);if(c.value.kind==='indeterminate')fault('INDETERMINATE_READ',`${c.name}: 대상 수명 종료 후 사용할 수 없는 값입니다.`);reads.push(id);return c.value;}
  function value(v){if(v?.kind==='int'&&Number.isSafeInteger(v.value))return;if(v?.kind==='pointer'){if(v.target!==null)get(v.target);return;}if(['uninitialized','indeterminate'].includes(v?.kind))return;fault('VALUE_INVALID','지원하지 않는 값입니다.');}
  function write(id,v){const c=get(id);value(v);writes.push({cellId:id,before:clone(c.value),after:clone(v)});c.value=clone(v);}
  function add(c,v=c.value){if(state.cells[c.id])fault('DUPLICATE_ID',c.id);if(!state.frames[c.owner]&&!state.objects[c.owner])fault('OWNER_MISSING',c.owner);value(v);state.cells[c.id]={...clone(c),value:clone(v),lifetime:'live'};const owner=state.frames[c.owner]||state.objects[c.owner];if(!owner.cellIds.includes(c.id))owner.cellIds.push(c.id);if(state.objects[c.owner]&&state.activeFrame&&state.objects[c.owner].storage==='automatic'){const f=state.frames[state.activeFrame];if(!f.cellIds.includes(c.id))f.cellIds.push(c.id);}writes.push({cellId:c.id,before:null,after:clone(v)});}
  function access(id,chain=[]){for(let i=0;i<chain.length;i++){const v=read(chain[i]);if(v.kind!=='pointer')fault('NOT_POINTER',chain[i]);if(v.target===null)fault('NULL_DEREFERENCE',`${chain[i]}는 NULL입니다. 역참조할 대상이 없습니다.`);if(v.target!==(chain[i+1]||id))fault('TARGET_MISMATCH','화살표의 실제 대상과 접근한 저장 공간이 다릅니다.');get(v.target);}get(id);}
  function end(ids){const ended=new Set(ids);for(const id of ids)if(state.cells[id])state.cells[id].lifetime='ended';for(const c of Object.values(state.cells))if(c.lifetime==='live'&&c.value.kind==='pointer'&&ended.has(c.value.target)){write(c.id,{kind:'indeterminate'});}for(const o of Object.values(state.objects))if(o.cellIds.length&&o.cellIds.every(id=>ended.has(id)))o.lifetime='ended';}
  try{
   switch(e.kind){
    case 'observe':break;
    case 'call':{
     if(state.frames[e.frame.id])fault('DUPLICATE_ID',e.frame.id);
     if(Object.values(state.frames).filter(f=>f.lifetime==='live').length>=(limits.depth??64))fault('LIMIT_REACHED','호출 깊이 한도에 도달했습니다.');
     state.frames[e.frame.id]={...clone(e.frame),cellIds:[],lifetime:'live',caller:state.activeFrame};break;}
    case 'enter':if(!state.frames[e.frameId]||state.frames[e.frameId].lifetime!=='live')fault('FRAME_MISSING',e.frameId);state.activeFrame=e.frameId;break;
    case 'bind':if(e.fromCellId){const v=read(e.fromCellId);if(JSON.stringify(v)!==JSON.stringify(e.value))fault('BIND_MISMATCH','복사 값과 호출자 값이 다릅니다.');}add(e.cell,e.value);break;
    case 'declare':add(e.cell);break;
    case 'read':access(e.cellId,e.through);read(e.cellId);break;
    case 'write':access(e.cellId,e.through);write(e.cellId,e.value);break;
    case 'allocate':{
     if(state.objects[e.object.id])fault('DUPLICATE_ID',e.object.id);
     if(Object.values(state.objects).filter(o=>o.lifetime==='live').length>=(limits.objects??256))fault('LIMIT_REACHED','객체 수 한도에 도달했습니다.');
     if(JSON.stringify(e.object.cellIds)!==JSON.stringify(e.cells.map(c=>c.id)))fault('OBJECT_INVALID','객체 Cell 순서가 다릅니다.');
     state.objects[e.object.id]={...clone(e.object),lifetime:'live'};for(const c of e.cells)add(c);if(e.resultCellId)write(e.resultCellId,{kind:'pointer',target:e.object.cellIds[0]});break;}
    case 'free':{
     const v=read(e.pointerCellId);if(v.kind!=='pointer')fault('INVALID_FREE','포인터 값이 필요합니다.');if(v.target===null)break;
     const c=get(v.target),o=state.objects[c.owner];if(!o||o.storage!=='allocated'||o.cellIds[0]!==c.id)fault('INVALID_FREE','할당된 객체 시작 주소만 해제할 수 있습니다.');end(o.cellIds);o.lifetime='ended';break;}
    case 'return':{
     if(state.activeFrame!==e.frameId)fault('INVALID_RETURN','활성 함수만 반환할 수 있습니다.');const f=state.frames[e.frameId];if(e.result)write(e.result.cellId,e.result.value);end(f.cellIds);f.lifetime='ended';state.activeFrame=f.caller;break;}
    case 'diagnostic':fault(e.code,e.message);break;
    default:fault('EVENT_UNSUPPORTED',e.kind);
   }
   return {state,reads:[...new Set(reads)],writes,diagnostic:null};
  }catch(err){if(!err.dsFault)throw err;return {state:clone(original),reads:[],writes:[],diagnostic:{code:err.code,message:err.message}};}
 }
 const api={initialMemory,applyEvent};if(typeof module!=='undefined'&&module.exports)module.exports=api;Object.assign(root.DSInteractive??={},api);
})(globalThis);
