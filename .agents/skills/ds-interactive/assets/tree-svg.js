(function (root) {
 'use strict';
 const D=root.DSInteractive;
 const svg=(tag,attrs)=>{
  const element=document.createElementNS('http://www.w3.org/2000/svg',tag);
  for(const [name,value] of Object.entries(attrs))element.setAttribute(name,value);
  return element;
 };

 function render(step,selection,metadata){
  const view=D.getTreeView(metadata.tree,step);
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
  scene.style.height=height+'px';

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
   button.style.top=point.y+'px';
   button.classList.toggle('active',active);
   button.classList.toggle('on-path',pathIds.has(node.id));
   button.classList.toggle('selected',!!selected);
   button.setAttribute('aria-pressed',String(!!selected));
   const statuses=[active?'현재 호출':pathIds.has(node.id)?'복귀 대기':''];
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
   label.style.top=end.y+'px';
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

 function cellButton(cell,step,selection,related){
  const button=D.el('button','tree-cell');
  button.type='button';
  button.dataset.cellId=cell.id;
  const selected=cell.id===selection;
  button.classList.toggle('related',related);
  button.classList.toggle('read',step.reads.includes(cell.id));
  button.classList.toggle('written',step.writes.some(write=>write.cellId===cell.id));
  button.setAttribute('aria-pressed',String(selected));
  const stored=formatTreeValue(cell.value,step.state);
  const value=cell.lifetime==='ended'?'수명 종료 · 마지막 값 '+stored:stored;
  button.append(D.el('span','tree-field',cell.name),D.el('strong','tree-cell-value',value),
   D.el('span','tree-cell-address','자기 주소 '+cell.address));
  return button;
 }

 function renderTreeDetails(step,selection,view){
  const stack=D.el('ol','tree-stack-list'), rows=D.el('div','tree-storage');
  const {state}=step, nodes=new Map(view.nodes.map(node=>[node.id,node]));
  const selected=state.cells[selection];
  const target=selected?.lifetime==='live'&&selected.value.kind==='pointer'?state.cells[selected.value.target]:null;
  const chosen=nodes.has(selected?.owner)?selected.owner:nodes.has(target?.owner)?target.owner:null;
  const labelFor=frame=>frame.parameterCellId===null?'호출자':frame.nodeId===null?'inorder(NULL)':'inorder('+nodes.get(frame.nodeId).key+'번 노드)';

  for(const [index,frame] of view.stack.entries()){
   const item=D.el('li','tree-frame');
   const waiting=view.stack[index-1]?.resumeAt;
   const status=index===0?'현재 실행':waiting?waiting.line+'행에서 재개':'순회가 끝날 때까지 대기';
   item.dataset.frameId=frame.frameId;
   item.dataset.frameState=index===0?'active':'waiting';
   item.append(D.el('h3','',labelFor(frame)),D.el('span','tree-frame-status',status));
   const cellIds=frame.parameterCellId?[frame.parameterCellId]:state.frames[frame.frameId].cellIds;
   for(const id of cellIds){
    const cell=state.cells[id];
    item.append(cellButton(cell,step,selection,chosen!==null&&state.cells[cell.value.target]?.owner===chosen));
   }
   stack.append(item);
  }
  const ended=state.frames[step.executed?.frameId];
  if(ended?.lifetime==='ended'&&ended.parameterCellId){
   const item=D.el('li','tree-frame tree-frame-ended');
   item.dataset.endedFrame=ended.id;
   item.append(D.el('h3','','방금 반환한 호출'),cellButton(state.cells[ended.parameterCellId],step,selection,false));
   stack.append(item);
  }

  for(const node of view.nodes){
   const group=D.el('section','tree-object');
   group.dataset.objectId=node.id;
   group.classList.toggle('related',chosen===node.id);
   group.append(D.el('h3','',node.key+'번 노드'));
   for(const id of [node.keyCellId,node.leftCellId,node.rightCellId]){
    const cell=state.cells[id];
    group.append(cellButton(cell,step,selection,chosen===node.id||chosen!==null&&state.cells[cell.value.target]?.owner===chosen));
   }
   rows.append(group);
  }
  if(!view.nodes.length)rows.append(D.el('p','empty','저장된 트리 노드가 없습니다.'));
  return {stack,rows,labelFor};
 }
 D.registerRenderer('c-tree',{render});
 Object.assign(D,{renderTreeDetails,formatTreeValue});
})(globalThis);
