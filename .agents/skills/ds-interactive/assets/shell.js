(function(root){
 const D=root.DSInteractive;
 // View state is independent of the execution Trace. No scene adapter owns panels.
 function mountShell(app,{onStep,onSpeed,redraw}){
  const q=s=>app.querySelector(s),listeners=[],on=(el,type,fn)=>{el.addEventListener(type,fn);listeners.push(()=>el.removeEventListener(type,fn));};
  const layout=q('.layout'),panels={left:q('.panel-left'),right:q('.panel-right')},toggles={left:q('[data-action=toggle-left]'),right:q('[data-action=toggle-right]')};
  let narrow=innerWidth<1024,drawer=null,open={left:true,right:true},widths={left:null,right:null},scale=1,trace=null,drag=null;
  const defaults=side=>side==='left'?Math.max(260,Math.min(320,innerWidth*.2)):Math.max(320,Math.min(400,innerWidth*.24));
  function setWidth(side,value){const other=side==='left'?'right':'left',lo=side==='left'?220:280,hi=side==='left'?480:720;
   const room=innerWidth-320-(open[other]?(widths[other]||defaults(other)):0);widths[side]=Math.max(lo,Math.min(hi,room,value));sync();}
  function sync(){
   // Reopening a dock or crossing the breakpoint can invalidate a width that
   // was legal while its sibling was closed. Reserve the scene before layout.
   if(!narrow&&open.left&&open.right){const room=innerWidth-320;let left=widths.left||defaults('left'),right=widths.right||defaults('right');
    if(left+right>room){right=Math.max(280,room-left);left=Math.max(220,Math.min(left,room-right));widths.left=left;widths.right=right;}}
   for(const side of ['left','right']){const active=narrow?drawer===side:open[side],panel=panels[side];panel.classList.toggle('is-open',active);panel.inert=!active;panel.setAttribute('aria-hidden',String(!active));toggles[side].setAttribute('aria-expanded',String(active));
    if(narrow&&active){panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');}else{panel.removeAttribute('role');panel.removeAttribute('aria-modal');}
    const handle=q(`[data-resize=${side}]`);handle.setAttribute('aria-valuenow',String(Math.round(widths[side]||defaults(side))));handle.tabIndex=narrow?-1:0;
    if(widths[side])layout.style.setProperty(side==='left'?'--pl-user':'--pr-user',widths[side]+'px');else layout.style.removeProperty(side==='left'?'--pl-user':'--pr-user');
   }
   q('.scrim').classList.toggle('is-on',narrow&&drawer!==null);q('.stage').inert=narrow&&drawer!==null;requestAnimationFrame(redraw);
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
   if(narrow&&drawer){if(e.key==='Escape'){e.preventDefault();close();return;}if(e.key==='Tab'){
    const focusable=[...panels[drawer].querySelectorAll('button,input,select,summary,[tabindex="0"]')].filter(x=>!x.disabled&&x.getClientRects().length);
    const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}
   }}
  });
  for(const side of ['left','right']){const handle=q(`[data-resize=${side}]`);
   on(handle,'keydown',e=>{if(!['ArrowLeft','ArrowRight','Home'].includes(e.key))return;e.preventDefault();e.stopPropagation();
    if(e.key==='Home'){widths[side]=null;sync();}else setWidth(side,(widths[side]||defaults(side))+(e.key==='ArrowRight'?1:-1)*(side==='left'?1:-1)*16);});
   on(handle,'pointerdown',e=>{if(narrow||e.button!==0)return;e.preventDefault();drag={side,id:e.pointerId,x:e.clientX,width:widths[side]||defaults(side)};handle.setPointerCapture(e.pointerId);layout.classList.add('is-resizing');});
   on(handle,'pointermove',e=>{if(!drag||drag.id!==e.pointerId)return;setWidth(side,drag.width+(e.clientX-drag.x)*(side==='left'?1:-1));});
   const end=()=>{drag=null;layout.classList.remove('is-resizing');};on(handle,'pointerup',end);on(handle,'pointercancel',end);on(handle,'lostpointercapture',end);
  }
  on(window,'resize',()=>{const next=innerWidth<1024;if(next!==narrow){const focused=document.activeElement?.closest('.panel');narrow=next;drawer=null;sync();if(focused)toggles[focused===panels.left?'left':'right'].focus({preventScroll:true});}
   else{if(!narrow)for(const side of ['left','right'])if(widths[side])setWidth(side,widths[side]);sync();}});
  const observer=new ResizeObserver(redraw);observer.observe(q('.stage-viewport'));observer.observe(q('.memory'));sync();
  return {update(next,step,invalid=false){if(trace!==next){trace=next;const list=q('.step-list');list.replaceChildren(...next.snapshots.map((s,i)=>{const b=D.el('button','btn');b.dataset.action='step';b.dataset.stepIndex=i;const text=D.el('span','step-txt');text.append(D.el('b','',s.title),D.el('span','',`${s.at.line}행 · ${s.phase==='before'?'실행 전':s.phase==='diagnostic'?'진단':'실행 후'}`));b.append(D.el('span','step-num num',i),text);return b;}));}
   for(const b of app.querySelectorAll('[data-action=step]')){b.setAttribute('aria-pressed',String(Number(b.dataset.stepIndex)===step));b.disabled=invalid;}
  },destroy(){observer.disconnect();listeners.forEach(f=>f());q('.stage').inert=false;}};
 }
 D.mountShell=mountShell;
})(globalThis);
