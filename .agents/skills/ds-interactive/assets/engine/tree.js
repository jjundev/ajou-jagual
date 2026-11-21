(function (root) {
 'use strict';
 const invalid = message => { throw Object.assign(new Error(message), {code:'TREE_INVALID'}); };

 function getTreeView(tree, step) {
  const {state,prints}=step;
  const fields=tree?.fields;
  const names=[fields?.key,fields?.left,fields?.right];
  if(!tree?.rootCellId||names.some(name=>typeof name!=='string'||!name)||new Set(names).size!==3){
   invalid('루트와 key·left·right 필드를 지정하세요.');
  }
  function pointerTarget(cellId) {
   const cell=state.cells[cellId];
   if(cell?.lifetime!=='live'||cell.value.kind!=='pointer')invalid(cellId+'에 유효한 포인터 값이 필요합니다.');
   if(cell.value.target===null)return null;
   const target=state.cells[cell.value.target], object=state.objects[target?.owner];
   if(target?.lifetime!=='live'||object?.lifetime!=='live'||object.cellIds[0]!==target.id){
    invalid(cellId+'는 노드 객체의 시작 주소를 가리켜야 합니다.');
   }
   return object.id;
  }
  function field(object,name) {
   const matches=object.cellIds.map(id=>state.cells[id]).filter(cell=>cell?.name===name);
   const cell=matches[0];
   if(matches.length!==1||cell.owner!==object.id||cell.lifetime!=='live'){
    invalid(object.id+'에 유효한 '+name+' 필드가 필요합니다.');
   }
   return cell;
  }

  const rootId=pointerTarget(tree.rootCellId), nodes=new Map();
  const outputOrders=new Map();
  for(const [i,print] of prints.entries()){
   if(!outputOrders.has(print.cellId))outputOrders.set(print.cellId,i+1);
  }
  function visit(id){
   if(id===null)return;
   if(nodes.has(id))invalid(id+'에 순환 링크 또는 둘 이상의 부모가 있습니다.');
   const object=state.objects[id];
   const key=field(object,fields.key), left=field(object,fields.left), right=field(object,fields.right);
   if(key.value.kind!=='int'||!Number.isSafeInteger(key.value.value))invalid(key.id+'에 정수 키가 필요합니다.');
   const node={id,key:key.value.value,keyCellId:key.id,leftCellId:left.id,rightCellId:right.id,
    leftId:pointerTarget(left.id),rightId:pointerTarget(right.id),outputOrder:outputOrders.get(key.id)??null};
   nodes.set(id,node);
   visit(node.leftId);
   visit(node.rightId);
  }
  visit(rootId);
  const nodeList=[...nodes.values()];
  const keyCells=new Set(nodeList.map(node=>node.keyCellId));
  if(prints.some(print=>!keyCells.has(print.cellId)))invalid('출력은 트리에 있는 노드의 key Cell을 읽어야 합니다.');

  const stack=[], frames=new Set();
  let nullEdge=null;
  for(let id=state.activeFrame;id!==null;id=state.frames[id].caller){
   const frame=state.frames[id];
   if(frame?.lifetime!=='live'||frames.has(id))invalid('활성 호출 경로가 올바르지 않습니다.');
   frames.add(id);
   const parameterCellId=frame.parameterCellId??null;
   const nodeId=parameterCellId===null?null:pointerTarget(parameterCellId);
   if(parameterCellId!==null&&state.cells[parameterCellId].owner!==id)invalid('인자 Cell의 소유자가 다른 호출입니다.');
   if(nodeId!==null&&!nodes.has(nodeId))invalid('순회 인자가 루트 트리 밖을 가리킵니다.');
   if(!stack.length&&parameterCellId!==null&&nodeId===null){
    const argument=frame.argumentSourceCellId;
    const owner=nodes.get(state.cells[argument]?.owner);
    if(owner?.leftCellId===argument&&owner.leftId===null)nullEdge={nodeId:owner.id,side:'left'};
    if(owner?.rightCellId===argument&&owner.rightId===null)nullEdge={nodeId:owner.id,side:'right'};
   }
   stack.push({frameId:id,nodeId,parameterCellId,resumeAt:frame.resumeAt??null});
  }
  return {rootId,nodes:nodeList,stack,activeNodeId:stack[0]?.nodeId??null,nullEdge};
 }
 const api={getTreeView};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 Object.assign(root.DSInteractive??={},api);
})(globalThis);
