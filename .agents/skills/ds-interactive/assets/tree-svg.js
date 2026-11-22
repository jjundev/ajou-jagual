(function (root) {
 'use strict';
 const D=root.DSInteractive;
 const svg=(tag,attrs)=>{
  const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const [name,value] of Object.entries(attrs))element.setAttribute(name,value);
  return element;
 };

 function render(step,selection,metadata,view=D.getTreeView(metadata.tree,step)){
  const scene=D.el('div','tree-scene');
  if(view.rootId===null){
   scene.append(D.el('p','tree-empty','빈 트리 · root = NULL'));
   return scene;
  }

  const nodes=new Map(view.nodes.map(node=>[node.id,node])), points=new Map();
  let slot=0, maxDepth=0;
  function place(id,depth){
   if(id===null)return;
   const node=nodes.get(id);
   place(node.leftId,depth+1);
   points.set(id,{x:++slot,y:40+depth*76});
   maxDepth=Math.max(maxDepth,depth);
   place(node.rightId,depth+1);
  }
  place(view.rootId,0);
  const width=slot+1, height=108+maxDepth*76;
  scene.style.minWidth=Math.max(224,width*42)+'px';
  scene.style.setProperty('--tree-height',height+'px');

  const links=svg('svg',{class:'tree-links',viewBox:'0 0 '+width+' '+height,preserveAspectRatio:'none','aria-hidden':'true'});
  const pathIds=new Set(view.stack.map(frame=>frame.nodeId));
  const selectedCell=step.state.cells[selection];
  function edge(from,to,className){
   links.append(svg('line',{x1:from.x,y1:from.y,x2:to.x,y2:to.y,class:className,'vector-effect':'non-scaling-stroke'}));
  }
  scene.append(links);
  for(const node of view.nodes){
   const point=points.get(node.id);
   for(const child of [node.leftId,node.rightId]){
    if(child!==null)edge(point,points.get(child),pathIds.has(node.id)&&pathIds.has(child)?'tree-path':'tree-edge');
   }
   const active=view.activeNodeId===node.id;
   const selected=selectedCell?.owner===node.id||
    selectedCell?.lifetime==='live'&&selectedCell.value.kind==='pointer'&&step.state.cells[selectedCell.value.target]?.owner===node.id;
   const label=String(node.key);
   const button=D.el('button','tree-node',label);
   button.type='button';
   button.dataset.nodeId=node.id;
   button.dataset.cellId=node.keyCellId;
   button.style.left=(point.x/width*100)+'%';
   button.style.top=(point.y/height*100)+'%';
   button.classList.toggle('active',active);
   button.classList.toggle('on-path',pathIds.has(node.id));
   button.classList.toggle('selected',!!selected);
   button.setAttribute('aria-haspopup','dialog');
   button.setAttribute('aria-controls','tree-inspector');
   const statuses=[active?'현재 호출':pathIds.has(node.id)?'복귀 대기':'',selected?'상세 보기 선택됨':''];
   if(node.outputOrder!==null){
    const order=D.el('span','tree-order',node.outputOrder);
    order.setAttribute('aria-hidden','true');
    button.dataset.outputOrder=node.outputOrder;
    button.append(order);
    statuses.push('출력 '+node.outputOrder+'번째');
   }
   button.setAttribute('aria-label',[label+'번 노드',...statuses.filter(Boolean)].join(', '));
   scene.append(button);
  }
  if(view.nullEdge){
   const {nodeId,side}=view.nullEdge;
   const point=points.get(nodeId);
   const end={x:point.x+(side==='left'?-.57:.57),y:point.y+47};
   edge(point,end,'tree-null-path');
   const label=D.el('span','tree-null-label','NULL');
   label.dataset.nullSide=side;
   label.dataset.parentNode=nodeId;
   label.style.left=(end.x/width*100)+'%';
   label.style.top=(end.y/height*100)+'%';
   scene.append(label);
  }
  return scene;
 }

 function formatTreeValue(value,state){
  if(value?.kind==='pointer'&&value.target!==null){
   const cell=state.cells[value.target], object=state.objects[cell?.owner];
   if(object?.cellIds[0]===cell?.id&&object)return '&'+object.id;
  }
  return D.format(value);
 }

 function memoryTable(step, ids, ended=false){
  const table=D.el('table','tree-fields');
  const header=table.createTHead().insertRow();
  for(const name of ['필드',ended?'마지막 값':'저장 값','주소']){
   const column=D.el('th','',name);
   column.scope='col';
   header.append(column);
  }
  const body=table.createTBody();
  for(const id of ids){
   const cell=step.state.cells[id];
   const row=body.insertRow();
   row.dataset.cellId=id;
   const name=D.el('th','',cell.name);
   name.scope='row';
   const read=!ended&&step.reads.includes(id), written=!ended&&step.writes.some(write=>write.cellId===id);
   if(read||written)name.append(D.el('small','',written?'쓰기':'읽기'));
   row.append(name,D.el('td','tree-cell-value',formatTreeValue(cell.value,step.state)),
    D.el('td','tree-cell-address',cell.address));
  }
  return table;
 }

 function renderNodeDetails(step, view, nodeId){
  const node=view.nodes.find(item=>item.id===nodeId);
  if(!node)return D.el('p','empty','이 단계에는 이 노드가 없습니다.');
  const section=D.el('section','tree-object');
  section.dataset.objectId=nodeId;
  section.append(D.el('h3','',node.key+'번 노드'),
   memoryTable(step,[node.keyCellId,node.leftCellId,node.rightCellId]));
  return section;
 }

 function treeCallLabel(state, frame, keyField){
  const value=state.cells[frame.parameterCellId]?.value;
  if(!value)return frame.functionId;
  const target=state.cells[value.target];
  const node=state.objects[target?.owner];
  const key=node?.cellIds.map(id=>state.cells[id]).find(cell=>cell.name===keyField);
  return frame.functionId+'('+(key?.value.value ?? formatTreeValue(value,state))+')';
 }

 function renderStackDetails(step, view, selectedId, justReturned, keyField){
  const list=D.el('ol','tree-stack-list');
  const {state}=step;
  const rows=view.stack.map((frame,index)=>({
   id:frame.frameId,
   label:frame.parameterCellId===null?'호출자':treeCallLabel(state,state.frames[frame.frameId],keyField),
   status:index===0?'현재':view.stack[index-1].resumeAt ? view.stack[index-1].resumeAt.line+'행에서 재개' : '대기'
  }));
  for(const id of new Set([justReturned?.id,selectedId])){
   if(!id||rows.some(row=>row.id===id))continue;
   const returned=state.frames[id];
   const label=returned?treeCallLabel(state,returned,keyField):'선택한 호출';
   rows.push({id,label,status:returned?'수명 종료':'호출 전'});
  }
  for(const row of rows){
   const frame=state.frames[row.id];
   const item=D.el('li','tree-frame');
   if(row.status==='현재')item.dataset.frameState='active';
   const expanded=row.id===selectedId;
   const button=D.el('button','tree-frame-button');
   button.type='button';
   button.dataset.inspectFrame=row.id;
   button.setAttribute('aria-expanded',String(expanded));
   button.append(D.el('span','',row.label),D.el('span','tree-frame-status',row.status));
   item.append(button);
   if(expanded&&frame){
    const ids=frame.parameterCellId?[frame.parameterCellId]:frame.cellIds;
    item.append(memoryTable(step,ids,frame.lifetime==='ended'));
   }
   list.append(item);
  }
  return list;
 }

 D.registerRenderer('c-tree',{render});
 Object.assign(D,{treeCallLabel,renderNodeDetails,renderStackDetails});
})(globalThis);
