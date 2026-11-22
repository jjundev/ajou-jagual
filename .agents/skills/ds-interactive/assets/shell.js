(function(root){
 const D=root.DSInteractive;
 // View state is independent of the execution Trace. No scene adapter owns panels.
 function mountShell(app,{onStep,onSpeed,redraw,onPanelsChange}){
  const q=s=>app.querySelector(s),listeners=[],on=(el,type,fn)=>{el.addEventListener(type,fn);listeners.push(()=>el.removeEventListener(type,fn));};
  const layout=q('.layout'),panels={left:q('.panel-left'),right:q('.panel-right')},toggles={left:q('[data-action=toggle-left]'),right:q('[data-action=toggle-right]')};
  const tree=app.dataset.kind==='c-tree';
  const compact=matchMedia(tree?'(width < 1280px)':'(width < 1024px)');
  const stage=q('.stage'),header=q('.topbar');
  const sides=['left','right'], sibling=side=>side==='left'?'right':'left';
  const limits={left:{min:220,max:480,prop:'--pl-user'},right:{min:280,max:720,prop:'--pr-user'}};
  const handles={left:q('[data-resize=left]'),right:q('[data-resize=right]')};
  const treeWidthKey='ds-interactive:tree-panel-widths';
  const treeDefaults={left:320,right:300};
  const shown={...treeDefaults};
  const sceneMin=400;
  let narrow=compact.matches,drawer=null,open={left:true,right:true},widths={left:null,right:null},scale=1,trace=null,drag=null;
  const defaults=side=>tree?treeDefaults[side]:side==='left'?Math.max(260,Math.min(320,innerWidth*.2)):Math.max(320,Math.min(400,innerWidth*.24));
  if(tree){
   try{
    const saved=JSON.parse(localStorage.getItem(treeWidthKey));
    for(const side of sides){
     const value=saved?.[side], {min,max}=limits[side];
     if(Number.isInteger(value)&&value>=min&&value<=max)widths[side]=value;
    }
   }catch{/* The current visit can still use custom widths. */}
  }
  function saveTreeWidths(){
   try{localStorage.setItem(treeWidthKey,JSON.stringify(widths));}catch{/* The current visit retains the widths. */}
  }
  function maxTreeWidth(side){
   const other=sibling(side),{min,max}=limits[side];
   return Math.max(min,Math.min(max,innerWidth-sceneMin-(open[other]?shown[other]:0)));
  }
  function syncTreeWidths(){
   if(narrow)return;
   // Fit the preferred widths for this viewport without changing stored values.
   const room=innerWidth-sceneMin;
   for(const side of sides)shown[side]=widths[side]??defaults(side);
   if(open.left&&open.right){
    shown.right=Math.max(limits.right.min,Math.min(shown.right,room-shown.left));
    shown.left=Math.max(limits.left.min,Math.min(shown.left,room-shown.right));
   }else for(const side of sides)shown[side]=Math.min(shown[side],room);
   for(const side of sides){
    layout.style.setProperty(limits[side].prop,shown[side]+'px');
    handles[side].setAttribute('aria-valuenow',String(shown[side]));
    handles[side].setAttribute('aria-valuemax',String(maxTreeWidth(side)));
   }
  }
  function setWidth(side,value){
   if(tree){
    const width=Math.round(Math.max(limits[side].min,Math.min(maxTreeWidth(side),value)));
    if(width===shown[side])return;
    widths[side]=width;
    syncTreeWidths();
    return;
   }
const other=side==='left'?'right':'left',lo=side==='left'?220:280,hi=side==='left'?480:720;
   const room=innerWidth-320-(open[other]?(widths[other]||defaults(other)):0);widths[side]=Math.max(lo,Math.min(hi,room,value));sync();}
  function sync(){
   layout.classList.toggle('is-docked',!narrow);
   // Reopening a dock or crossing the breakpoint can invalidate a width that
   // was legal while its sibling was closed. Reserve the scene before layout.
   if(!tree&&!narrow&&open.left&&open.right){const room=innerWidth-320;let left=widths.left||defaults('left'),right=widths.right||defaults('right');
    if(left+right>room){right=Math.max(280,room-left);left=Math.max(220,Math.min(left,room-right));widths.left=left;widths.right=right;}}
   if(tree)syncTreeWidths();
   for(const side of sides){const active=narrow?drawer===side:open[side],panel=panels[side];panel.classList.toggle('is-open',active);panel.inert=!active;panel.setAttribute('aria-hidden',String(!active));toggles[side].setAttribute('aria-expanded',String(active));
    if(narrow&&active){panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');}else{panel.removeAttribute('role');panel.removeAttribute('aria-modal');}
    const handle=handles[side];handle.tabIndex=narrow?-1:0;
    if(tree)continue;
    handle.setAttribute('aria-valuenow',String(Math.round(widths[side]||defaults(side))));
    if(widths[side])layout.style.setProperty(side==='left'?'--pl-user':'--pr-user',widths[side]+'px');else layout.style.removeProperty(side==='left'?'--pl-user':'--pr-user');
   }
   const modal=narrow&&drawer!==null;
   q('.scrim').classList.toggle('is-on',modal);
   stage.inert=modal;
   header.inert=modal;
   onPanelsChange?.({narrow,drawer,leftOpen:narrow?drawer==='left':open.left});
   requestAnimationFrame(redraw);
  }
  function close(){const was=drawer;drawer=null;sync();if(was)toggles[was].focus({preventScroll:true});}
  function toggle(side){if(narrow){if(drawer===side){close();return;}drawer=side;sync();panels[side].querySelector('[data-action=close-panels]').focus({preventScroll:true});}
   else{open[side]=!open[side];sync();if(!open[side])toggles[side].focus({preventScroll:true});}}
  on(app,'click',e=>{const btn=e.target.closest('button'),action=btn?.dataset.action;
   if(action==='toggle-left')toggle('left');if(action==='toggle-right')toggle('right');if(e.target.closest('[data-action=close-panels]'))close();
   if(action==='step')onStep(Number(btn.dataset.stepIndex));
   if(btn?.dataset.speed){for(const b of app.querySelectorAll('[data-speed]'))b.setAttribute('aria-pressed',String(b===btn));onSpeed(Number(btn.dataset.speed));}
   if(action?.startsWith('option-')){const key=action.slice(7);app.dataset[key]=String(app.dataset[key]!=='true');btn.setAttribute('aria-pressed',app.dataset[key]);requestAnimationFrame(redraw);}
   if(action?.startsWith('zoom-')){scale=action==='zoom-reset'?1:Math.round(Math.max(.6,Math.min(1.8,scale+(action==='zoom-in'?.1:-.1)))*10)/10;
    const memory=q('.memory');memory.dataset.scale=String(scale);memory.style.setProperty('--zoom',String(scale));redraw();if(action==='zoom-reset'){q('.stage-viewport').scrollTop=0;q('.stage-viewport').scrollLeft=0;}}
  });
  on(document,'keydown',e=>{
   if(!e.defaultPrevented&&narrow&&drawer){if(e.key==='Escape'){e.preventDefault();close();return;}if(e.key==='Tab'){
    const focusable=[...panels[drawer].querySelectorAll('button,input,select,summary,[tabindex="0"]')].filter(el=>{
     const closedSummary=el.closest('details:not([open])')?.querySelector(':scope > summary');
     return !el.disabled&&el.getClientRects().length&&(!closedSummary||closedSummary.contains(el));
    });
    const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}
   }}
  });
  function endDrag(){
   if(!drag)return;
   drag=null;
   layout.classList.remove('is-resizing');
   if(tree)saveTreeWidths();
  }
  for(const side of sides){
   const handle=handles[side], direction=side==='left'?1:-1;
   function resetWidth(){
    widths[side]=null;
    if(tree){syncTreeWidths();saveTreeWidths();}else sync();
   }
   if(tree){
    handle.setAttribute('aria-controls',panels[side].id);
    on(handle,'dblclick',()=>{if(!narrow&&open[side])resetWidth();});
   }
   on(handle,'keydown',e=>{
    if(narrow||!open[side]||!['ArrowLeft','ArrowRight','Home'].includes(e.key))return;
    e.preventDefault();e.stopPropagation();
    if(e.key==='Home'){resetWidth();return;}
    const current=tree?shown[side]:(widths[side]||defaults(side));
    const step=tree&&e.shiftKey?64:16;
    setWidth(side,current+(e.key==='ArrowRight'?1:-1)*direction*step);
    if(tree)saveTreeWidths();
   });
   on(handle,'pointerdown',e=>{
    if(narrow||!open[side]||e.button!==0||drag)return;
    e.preventDefault();
    const width=tree?panels[side].getBoundingClientRect().width:(widths[side]||defaults(side));
    drag={side,id:e.pointerId,x:e.clientX,width};
    handle.setPointerCapture(e.pointerId);
    layout.classList.add('is-resizing');
   });
   on(handle,'pointermove',e=>{
    if(narrow||!drag||drag.side!==side||drag.id!==e.pointerId)return;
    setWidth(side,drag.width+(e.clientX-drag.x)*direction);
   });
   for(const type of ['pointerup','pointercancel','lostpointercapture']){
    on(handle,type,e=>{if(drag?.id===e.pointerId)endDrag();});
   }
  }
  on(compact,'change',()=>{
   const focused=document.activeElement?.closest('.panel');
   const captured=drag;
   endDrag();
   if(captured&&handles[captured.side].hasPointerCapture(captured.id))handles[captured.side].releasePointerCapture(captured.id);
   narrow=compact.matches;
   drawer=null;
   sync();
   if(focused)toggles[focused===panels.left?'left':'right'].focus({preventScroll:true});
  });
  on(window,'resize',()=>{
   if(tree){syncTreeWidths();return;}
   if(!narrow)for(const side of sides)if(widths[side])setWidth(side,widths[side]);
   sync();
  });
  const observer=new ResizeObserver(redraw);observer.observe(q('.stage-viewport'));observer.observe(q('.memory'));sync();
  return {update(next,entries,step,invalid=false){if(trace!==next){trace=next;const list=q('.step-list');list.replaceChildren(...entries.map((s,i)=>{const b=D.el('button','btn');b.dataset.action='step';b.dataset.stepIndex=i;const text=D.el('span','step-txt');const row=s.executed?.at||s.at;
    const where=row?`${row.line}행 · ${s.diagnostic?'진단':s.phase==='before'?'실행 전':'실행 후'}`:'실행 전';
    if(tree){
     const frame=s.state.frames[s.executed?.frameId];
     const call=frame?D.treeCallLabel(s.state,frame,trace.metadata.tree.fields.key):
      trace.sources.find(source=>source.id===row?.sourceId)?.label;
     const label=row?[call,row.line+'행'].filter(Boolean).join(' · '):'초기 상태';
     text.append(D.el('b','',label));
     if(row)text.append(D.el('span','',s.title));
     b.append(D.el('span','num',i),text);
    }else{
     text.append(D.el('b','',s.title),D.el('span','',where));b.append(D.el('span','step-num num',i),text);
    }
    return b;}));}
   for(const b of app.querySelectorAll('[data-action=step]')){b.setAttribute('aria-pressed',String(Number(b.dataset.stepIndex)===step));b.disabled=invalid;}
  },destroy(){observer.disconnect();listeners.forEach(f=>f());stage.inert=header.inert=false;}};
 }
 D.mountShell=mountShell;
})(globalThis);
