(function (root) {
 'use strict';
 const invalid = message => { throw Object.assign(new Error(message), {code:'LINE_STEP_INVALID'}); };
 const sameLocation = (a,b) => a?.sourceId===b?.sourceId && a?.line===b?.line;
 const cursor = snapshot => snapshot && {at:snapshot.at, frameId:snapshot.frameIdBefore};

 function validateLine(before, group, next) {
  const first=group[0], last=group.at(-1);
  const callerId=first.frameIdBefore;
  if(!callerId||before.state.activeFrame!==callerId)invalid('실행할 줄의 활성 호출이 일치하지 않습니다.');
  if(last.diagnostic)return;
  const call=group.find(step=>step.eventKind==='call');
  if(call){
   const newId=last.state.activeFrame, frame=last.state.frames[newId];
   const bind=group.find(step=>step.eventKind==='bind'&&step.writes.some(write=>write.cellId===frame?.parameterCellId));
   const source=before.state.cells[frame?.argumentSourceCellId];
   const parameter=last.state.cells[frame?.parameterCellId];
   if(group.filter(step=>step.eventKind==='call').length!==1||before.state.frames[newId]||
    frame?.caller!==callerId||!call.state.frames[newId]||last.eventKind!=='enter'||
    !source||parameter?.owner!==newId||bind?.fromCellId!==frame.argumentSourceCellId||
    (frame.resumeAt!==null&&(!frame.resumeAt?.sourceId||!Number.isInteger(frame.resumeAt?.line)||frame.resumeAt.line<1))||
    !next||next.frameId!==newId){
    invalid('호출 줄의 인자 복사, 새 호출 또는 복귀 위치가 올바르지 않습니다.');
   }
  }else if(group.some(step=>step.eventKind==='return')){
   const frame=before.state.frames[callerId];
   if(last.eventKind!=='return'||last.state.activeFrame!==frame.caller||
    (frame.resumeAt===null ? next!==null : !next||next.frameId!==frame.caller||!sameLocation(next.at,frame.resumeAt))){
    invalid('반환 뒤 호출자와 재개할 줄이 일치하지 않습니다.');
   }
  }else if(last.state.activeFrame!==callerId||next&&next.frameId!==callerId){
   invalid('새 호출이나 반환 없이 활성 호출이 바뀌었습니다.');
  }
 }

 function projectLineSteps(snapshots) {
  const [initial,...events]=snapshots, groups=[], seen=new Set();
  for(const snapshot of events){
   const {lineStepId}=snapshot;
   if(typeof lineStepId!=='string'||!lineStepId)invalid('트리 이벤트에 소스 줄 ID가 필요합니다.');
   const group=groups.at(-1);
   if(group?.[0].lineStepId===lineStepId){
    if(!sameLocation(group[0].at,snapshot.at))invalid('한 줄 묶음의 소스 위치가 다릅니다.');
    group.push(snapshot);
   }else{
    if(seen.has(lineStepId))invalid('소스 줄 ID가 연속되지 않은 단계에 재사용되었습니다.');
    seen.add(lineStepId);
    groups.push([snapshot]);
   }
  }
  const steps=[{id:'initial',state:initial.state,executed:null,next:cursor(events[0])??null,
   reads:[],writes:[],prints:[],diagnostic:null,title:initial.title,explanation:initial.explanation}];
  for(const [index,group] of groups.entries()){
   const first=group[0], last=group.at(-1), previous=steps.at(-1);
   const next=last.diagnostic?null:cursor(groups[index+1]?.[0])??null;
   validateLine(previous,group,next);
   const writes=new Map(), reads=new Set(), prints=[...previous.prints];
   // Keep partial events in the detailed trace; show the last complete line on failure.
   if(!last.diagnostic){
    for(const event of group){
     for(const id of event.reads)reads.add(id);
     for(const write of event.writes){
      const earlier=writes.get(write.cellId);
      writes.set(write.cellId,earlier?{...write,before:earlier.before}:write);
     }
     if(event.printed)prints.push(event.printed);
    }
   }
   steps.push({id:'line-'+(index+1),state:last.diagnostic?previous.state:last.state,
    executed:cursor(first),next,reads:[...reads],writes:[...writes.values()],prints,
    diagnostic:last.diagnostic,title:first.title,explanation:first.explanation});
  }
  return steps;
 }
 const api={projectLineSteps};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 Object.assign(root.DSInteractive??={},api);
})(globalThis);
