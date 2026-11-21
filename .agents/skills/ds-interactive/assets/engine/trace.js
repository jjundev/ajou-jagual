(function(root){
 'use strict';
 const api=typeof module!=='undefined'&&module.exports?{...require('./contract.js'),...require('./memory.js'),...require('./line-steps.js'),...require('./tree.js')}:root.DSInteractive;
 function freeze(x){if(x&&typeof x==='object'){Object.freeze(x);for(const v of Object.values(x))freeze(v);}return x;}
 function compileScenario(s,input,limits={}){
  const issues=api.validateInput(s.inputs,input);if(issues.length)throw Object.assign(new Error(issues.map(x=>x.message).join(' ')),{code:'INPUT_INVALID',issues});
  const iterator=s.generateEvents(input)[Symbol.iterator]();let next=iterator.next();
  const sources=structuredClone(s.sources).map(source=>({...source,text:source.text.replace(/\{\{(\w+)\}\}/g,(_,key)=>{if(!Number.isSafeInteger(input[key]))throw Error('Source template requires integer input: '+key);return String(input[key]);})}));
  let state=structuredClone(s.initialState(input));const first={sourceId:next.value?.at.sourceId||sources[0].id,line:next.value?.at.line||1};
  const snapshots=[{id:'initial',at:first,phase:'before',title:'호출 전 · 초기 상태',explanation:s.intro||'입력을 확인하고 한 단계씩 실행해 보세요.',state:structuredClone(state),reads:[],writes:[],diagnostic:null}];
  while(!next.done){const e=next.value;
   const exhausted=snapshots.length>=(limits.steps??2000)-1;
   const event=exhausted?{...e,kind:'diagnostic',code:'LIMIT_REACHED',message:'단계 수 한도에 도달했습니다.'}:e;
   const frameIdBefore=state.activeFrame;
   const r=api.applyEvent(state,event,limits);state=r.state;
   const lineRecord=s.kind==='c-tree'?{lineStepId:e.lineStepId,eventKind:event.kind,frameIdBefore,
    ...(event.kind==='bind'&&{fromCellId:event.fromCellId})}:{};
   snapshots.push({id:`step-${snapshots.length}`,at:event.at,phase:r.diagnostic?'diagnostic':'after',title:e.label||e.kind,explanation:e.explanation,...r,...lineRecord});
   if(r.diagnostic){iterator.return?.();break;}next=iterator.next();
  }
  const trace={version:1,id:s.id,title:s.title,kind:s.kind,sources,inputs:structuredClone(input),presets:structuredClone(s.presets),snapshots,metadata:{supplement:s.supplement||'',addressModel:'기호 주소 · 실제 ABI 배치 아님'}};
  const structural=validateTrace(trace);if(structural.length)throw Object.assign(new Error(JSON.stringify(structural)),{code:'TRACE_INVALID',issues:structural});
  if(s.kind==='c-tree'){
   trace.metadata.tree=structuredClone(s.tree);
   trace.lineSteps=api.projectLineSteps(snapshots);
   for(const step of trace.lineSteps)api.getTreeView(trace.metadata.tree,step);
  }
  return freeze(trace);
 }
 function validateTrace(t){
  const issues=[],add=(code,path,message)=>issues.push(api.issue(code,path,message));
  if(t.version!==1||!t.id||!t.kind||!Array.isArray(t.snapshots)||!t.snapshots.length)return [api.issue('TRACE_INVALID','trace','필수 필드가 없습니다.')];
  const seen=new Set();let stopped=false;
  t.snapshots.forEach((s,i)=>{
   const path=`snapshots[${i}]`,source=t.sources?.find(x=>x.id===s.at?.sourceId);
   if(!source||!Number.isInteger(s.at.line)||s.at.line<1||s.at.line>source.text.split('\n').length)add('LOCATION_INVALID',path,'소스 줄 범위가 맞지 않습니다.');
   if(seen.has(s.id))add('DUPLICATE_ID',path,s.id);seen.add(s.id);
   if(stopped)add('AFTER_DIAGNOSTIC',path,'진단 뒤 단계가 있습니다.');stopped=!!s.diagnostic;
   for(const [id,c]of Object.entries(s.state.cells)){
    if(c.id!==id||!s.state.frames[c.owner]&&!s.state.objects[c.owner])add('CELL_INVALID',path,id);
    if(c.lifetime==='live'&&c.value.kind==='pointer'&&c.value.target!==null&&s.state.cells[c.value.target]?.lifetime!=='live')add('POINTER_INVALID',path,id);
   }
   for(const w of s.writes){if(JSON.stringify(s.state.cells[w.cellId]?.value)!==JSON.stringify(w.after))add('WRITE_INVALID',path,w.cellId);if(i&&JSON.stringify(t.snapshots[i-1].state.cells[w.cellId]?.value??null)!==JSON.stringify(w.before))add('WRITE_BEFORE_INVALID',path,w.cellId);}
  });return issues;
 }
 function checkScenario(s){const cases=[{id:'default',input:Object.fromEntries(s.inputs.map(d=>[d.key,d.default]))},...s.presets];const traces={},issues=[];
  for(const c of cases){try{const t=compileScenario(s,c.input);traces[c.id]=t;for(const ex of (s.expected||[]).filter(x=>x.presetId===c.id)){if((t.snapshots.at(-1).diagnostic?.code||null)!==(ex.diagnosticCode||null))issues.push(api.issue('EXPECTED_DIAGNOSTIC',c.id,'진단 불일치'));for(const ck of ex.checks){const snap=ck.step==='last'?t.snapshots.at(-1):t.snapshots.find(x=>x.id===ck.step);if(JSON.stringify(snap?.state.cells[ck.cellId]?.value)!==JSON.stringify(ck.value))issues.push(api.issue('EXPECTED_VALUE',c.id,ck.cellId));}}}catch(e){issues.push(api.issue(e.code||'SCENARIO_ERROR',c.id,e.message));}}
  return {ok:!issues.length,issues,traces};
 }
 const out={compileScenario,validateTrace,checkScenario};if(typeof module!=='undefined'&&module.exports)module.exports=out;Object.assign(root.DSInteractive??={},out);
})(globalThis);
