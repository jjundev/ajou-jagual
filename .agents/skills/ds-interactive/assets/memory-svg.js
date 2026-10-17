(function(root){
 const D=root.DSInteractive,renderers=new Map();
 function registerRenderer(kind,renderer){if(!renderer||typeof renderer.render!=='function')throw Error('Renderer requires render');renderers.set(kind,renderer);}
 const format=v=>!v?'—':v.kind==='int'?String(v.value):v.kind==='pointer'?(v.target===null?'NULL':`&${v.target}`):v.kind==='uninitialized'?'미초기화':'사용 불가';
 const el=(tag,cls,text)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=text;return x;};
 const memoryRenderer={render(snapshot,selection){
  const container=el('div','memory-content');container.style.display='contents';const s=snapshot.state,groups=[...Object.values(s.frames),...Object.values(s.objects)];
  for(const g of groups){const cells=Object.values(s.cells).filter(c=>c.owner===g.id);const frame=el('section','frame');frame.dataset.frameId=g.id;
   const h=el('h3','',g.functionId?`${g.functionId}()`:`${g.type}`);h.append(el('small','',`${g.id} · ${g.lifetime==='ended'?'수명 종료':g.id===s.activeFrame?'실행 중':'대기'}`));frame.append(h);
   for(const c of cells){const b=el('button','cell');b.type='button';b.dataset.cellId=c.id;b.classList.toggle('written',snapshot.writes.some(w=>w.cellId===c.id));b.classList.toggle('read',snapshot.reads.includes(c.id));b.classList.toggle('selected',selection===c.id);b.classList.toggle('ended',c.lifetime==='ended');b.setAttribute('aria-pressed',String(selection===c.id));b.setAttribute('aria-label',`${c.name}, 저장 값 ${format(c.value)}, 자신의 주소 ${c.address}${c.lifetime==='ended'?', 수명 종료':''}`);
    b.append(el('span','cell-name',c.name),el('span','cell-address',`${c.type} · ${c.address}`),el('span','cell-value',c.lifetime==='ended'?`수명 종료 · ${format(c.value)}`:format(c.value)));frame.append(b);
   }container.append(frame);
  }if(!groups.length)container.append(el('p','empty','아직 호출 프레임이 없습니다.'));return container;
 }};
 function drawArrows(container,snapshot,selection){
  container.querySelector('.memory-svg')?.remove();const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('class','memory-svg');svg.setAttribute('aria-hidden','true');
  const base=container.getBoundingClientRect(),ratio=base.width/container.offsetWidth||1;svg.setAttribute('viewBox',`0 0 ${container.offsetWidth} ${container.offsetHeight}`);svg.innerHTML='<defs><marker id="ds-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor"/></marker></defs>';
  let lane=0;
  for(const c of Object.values(snapshot.state.cells)){if(c.lifetime!=='live'||c.value.kind!=='pointer'||c.value.target===null)continue;const from=[...container.querySelectorAll('[data-cell-id]')].find(x=>x.dataset.cellId===c.id),to=[...container.querySelectorAll('[data-cell-id]')].find(x=>x.dataset.cellId===c.value.target);if(!from||!to)continue;
   const f=from.getBoundingClientRect(),t=to.getBoundingClientRect(),same=Math.abs(f.left-t.left)<3;
   let x1=(f.right-base.left)/ratio,y1=(f.top+f.height*.65-base.top)/ratio,x2=((same?t.right:t.left)-base.left)/ratio,y2=(t.top+t.height*.5-base.top)/ratio;
   if(!same&&f.left>t.left){x1=(f.left-base.left)/ratio;x2=(t.right-base.left)/ratio;}
   const bend=same?Math.min(container.offsetWidth-2,x1+8+(lane++%3)*5):(x1+x2)/2;
   const path=document.createElementNS(ns,'path');path.setAttribute('d',`M${x1},${y1} C${bend},${y1} ${bend},${y2} ${x2},${y2}`);path.setAttribute('fill','none');path.setAttribute('stroke','currentColor');path.setAttribute('stroke-width',selection===c.id?'2.5':'1.4');path.setAttribute('marker-end','url(#ds-arrow)');path.style.color='var(--accent)';svg.append(path);
  }container.append(svg);
 }
 registerRenderer('c-memory',memoryRenderer);Object.assign(D,{registerRenderer,renderers,memoryRenderer,drawArrows,format,el});
})(globalThis);
