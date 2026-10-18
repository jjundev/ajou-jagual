(function (root) {
 'use strict';
 /** @typedef {{kind:'int',value:number}|{kind:'pointer',target:string|null}|{kind:'uninitialized'|'indeterminate'}} Value */
 /** @typedef {{id:string,name:string,type:string,owner:string,address:string,value:Value,lifetime:'live'|'ended'}} Cell */
 /** @typedef {{frames:Object,objects:Object,cells:Object,activeFrame:string|null,stdout:string[]}} MemoryState */
 /** @typedef {{sourceId:string,line:number}} Location */
 /** @typedef {{kind:string,at:Location,explanation:string}} Event */
 /** @typedef {{id:string,at:Location,phase:string,state:MemoryState,reads:string[],writes:Object[],diagnostic:Object|null}} Snapshot */
 /** @typedef {{version:1,id:string,kind:string,sources:Object[],inputs:Object[],presets:Object[],snapshots:Snapshot[],metadata:Object}} Trace */
 /** @typedef {{version:1,id:string,title:string,kind:string,sources:Object[],inputs:Object[],presets:Object[],initialState:Function,generateEvents:Function,expected:Object[]}} Scenario */
 const issue=(code,path,message)=>({code,path,message});
 function validateInput(defs,input) {
  return defs.flatMap(d=>{
   const v=input[d.key];const valid=d.type==='integer' ? Number.isSafeInteger(v)&&v>=(d.min??-Infinity)&&v<=(d.max??Infinity) : d.type==='enum'&&d.options?.some(o=>o.value===v);
   return valid?[]:[issue('INPUT_INVALID',d.key,`${d.label||d.key}: ${d.type==='integer'?`${d.min} ~ ${d.max} 사이 정수`:'목록의 값'}를 입력하세요.`)];
  });
 }
 const api={validateInput,issue};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 Object.assign(root.DSInteractive??={},api);
})(globalThis);
