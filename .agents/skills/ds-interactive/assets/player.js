(function(root){
 const D=root.DSInteractive;
 function mountPlayer(app,scenario){
  const renderer=D.renderers.get(scenario.kind);if(!renderer)throw Error(`Renderer missing: ${scenario.kind}`);
  const tree=scenario.kind==='c-tree';
  const defaults=Object.fromEntries(scenario.inputs.map(d=>[d.key,d.default]));
  const byPreset=new Map(scenario.presets.map(p=>[p.id,p.input]));
  const caseField=tree&&scenario.inputs.length===1&&scenario.inputs[0].type==='enum'&&scenario.inputs[0];
  const casesCovered=caseField&&caseField.options.every(o=>o.value===caseField.default||
   scenario.presets.some(p=>p.input[caseField.key]===o.value));
  const q=s=>app.querySelector(s),listeners=[],on=(node,event,fn)=>{node.addEventListener(event,fn);listeners.push(()=>node.removeEventListener(event,fn));};
  app.dataset.kind=scenario.kind;
  if(tree){
   for(const element of app.querySelectorAll('.tree-only'))element.hidden=false;
   q('.stage').setAttribute('aria-label','트리 실행 보기');
   q('.pane-heading h2').textContent='전체 트리';
   q('.memory').setAttribute('aria-label','이진 트리와 현재 호출 경로');
   q('[data-action=prev]').setAttribute('aria-label','이전 줄');
   q('[data-action=next]').setAttribute('aria-label','다음 줄');
   q('[data-action=option-arrows]').hidden=true;
   q('[data-action=option-addresses]').closest('section').hidden=true;
   if(casesCovered)q('.inputs').hidden=true;
  }
  let input={...defaults},trace,step=0,selection=null,timer=null,destroyed=false,speed=1;
  q('h1').textContent=scenario.title;document.title=scenario.title;q('.takeaway').textContent=scenario.takeaway||'';
  const preset=q('[data-action=preset]');preset.append(new Option(casesCovered?caseField.options.find(o=>o.value===caseField.default).label:'기본 입력','default'));for(const p of scenario.presets)preset.append(new Option(p.label,p.id));
  for(const d of scenario.inputs){const label=D.el('label','',d.label);const field=d.type==='enum'?document.createElement('select'):document.createElement('input');field.dataset.input=d.key;field.setAttribute('aria-label',d.label);if(d.type==='integer'){field.type='number';field.min=d.min;field.max=d.max;field.step='1';}else for(const o of d.options)field.append(new Option(o.label,o.value));label.append(field);q('.inputs').append(label);if(d.type==='enum'&&d.key==='mode'){label.hidden=true;q('.modes').hidden=false;for(const o of d.options){const b=D.el('button','',o.label);b.dataset.action='mode';b.dataset.modeValue=o.value;q('.modes').append(b);}}const change=()=>{const value=d.type==='integer'?(field.value===''?NaN:Number(field.value)):field.value;if(Object.is(input[d.key],value))return;input[d.key]=value;preset.value='default';recompile();};on(field,'change',change);if(d.type==='integer')on(field,'input',change);}
  const play=q('[data-action=play]');const playIcon=running=>{play.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'+(running?'<rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/>':'<path d="M7 5l12 7-12 7z"/>')+'</svg>';};
  const entries=()=>trace.lineSteps||trace.snapshots;
  function redraw(){if(trace&&!destroyed&&!tree)D.drawArrows(q('.memory'),entries()[step],selection);}
  const treeUi=tree?D.mountTreeUi(app,{scenario,stop,refresh:paint}):null;
  const shell=D.mountShell(app,{onStep:move,onSpeed:value=>{speed=value;if(timer!==null){stop();toggle();}},redraw,onPanelsChange:treeUi?.syncPanels});
  function stop(){if(timer!==null)clearInterval(timer);timer=null;playIcon(false);play.setAttribute('aria-label','재생');app.dataset.playing='false';}
  function printNeighbor(direction){
   const steps=entries();
   for(let i=step+direction;i>0&&i<steps.length;i+=direction){
    if(steps[i].prints.length>steps[i-1].prints.length)return i;
   }
   return -1;
  }
  function paintCode(s){
   const position=tree?s.next?.at:s.at;
   const executed=tree?s.executed?.at:null;
   const source=trace.sources.find(item=>item.id===(position||executed)?.sourceId)||trace.sources[0];
   const code=q('.code');
   code.replaceChildren();
   const primary=trace.sources[0];
   const auxiliary=tree?trace.sources.filter(item=>item!==primary&&
    (item.id===position?.sourceId||item.id===executed?.sourceId)):[];
   const shownSources=tree?[...auxiliary,primary]:[source];
   for(const shown of shownSources){
    for(const [i,line] of shown.text.split('\n').entries()){
     const current=position?.sourceId===shown.id&&position.line===i+1;
     const completed=executed?.sourceId===shown.id&&executed.line===i+1;
     if(tree&&shown!==primary&&!current&&!completed)continue;
     const row=D.el('div','code-line');
     row.dataset.line=i+1;
     row.dataset.sourceId=shown.id;
     row.classList.toggle('current',current);
     row.classList.toggle('executed',completed);
     if(completed||current&&!executed)row.setAttribute('aria-current','step');
     row.append(D.el('span','line-number',i+1),D.el('span','',line));
     code.append(row);
    }
   }
   code.dataset.step=s.id;
   const active=code.querySelector('.executed')||code.querySelector('.current');
   if(active){
    const row=active.getBoundingClientRect(),box=code.getBoundingClientRect();
    if(row.top<box.top)code.scrollTop+=row.top-box.top;
    else if(row.bottom>box.bottom)code.scrollTop+=row.bottom-box.bottom;
   }
   if(tree)return;
   q('.source-label').textContent=source.label||source.id;
   q('.source-note').textContent=source.provenance?.note||
    (source.provenance?.supplement?'학습용 보충 코드 · 강의 개념을 함수 호출로 확장했습니다.':'강의 swap 함수 · 호출자와 헤더는 검산용으로 보충했습니다.');
   q('.phase').textContent=
    `${source.label||source.id} · ${s.at.line}행 · ${s.phase==='diagnostic'?'진단 후 중단':s.phase==='before'?'실행 전':'실행 후'}`;
  }
  function paintTree(s,view){
   treeUi.paint(s,view,trace.metadata,play.disabled);
   app.dataset.activeFrame=s.state.activeFrame??'';
   if(selection===null)delete app.dataset.selectedCell;else app.dataset.selectedCell=selection;
   q('.stdout-value').textContent=s.state.stdout.join('');
   q('[data-action=previous-output]').disabled=printNeighbor(-1)<0;
   q('[data-action=next-output]').disabled=printNeighbor(1)<0;
  }
  function paint(){
   if(destroyed)return;
   const focused=document.activeElement, focusedCell=focused?.dataset.cellId;
   const region=focused?.closest('.memory');
   for(const b of app.querySelectorAll('[data-mode-value]'))b.setAttribute('aria-pressed',String(b.dataset.modeValue===input.mode));
   const steps=entries(),s=steps[step];
   app.dataset.snapshot=s.id;app.dataset.index=step;
   q('output[data-step]').textContent=`${step} / ${steps.length-1}`;
   q('output[data-step]').dataset.step=s.id;
   const scrub=q('[data-action=scrub]');
   scrub.max=steps.length-1;scrub.value=step;
   paintCode(s);
   const memory=q('.memory');
   const view=tree?D.getTreeView(trace.metadata.tree,s):null;
   if(tree)selection=treeUi.selection(s,view);
   memory.replaceChildren(renderer.render(s,selection,trace.metadata,view));
   memory.dataset.step=s.id;
   if(tree)paintTree(s,view);else paintMemory(s);
   for(const action of ['first','prev'])q(`[data-action=${action}]`).disabled=step===0;for(const action of ['last','next'])q(`[data-action=${action}]`).disabled=step===entries().length-1;
   shell.update(trace,steps,step,play.disabled);
   treeUi?.syncHistory();
   if(focusedCell&&region)[...region.querySelectorAll('[data-cell-id]')].find(b=>b.dataset.cellId===focusedCell)?.focus({preventScroll:true});
  }
  function paintMemory(s){
   redraw();
   q('.step-title').textContent=s.title;q('.explanation').textContent=s.explanation;
   q('.diagnostic').textContent=s.diagnostic?`${s.diagnostic.code}: ${s.diagnostic.message} 이후 실행은 진행하지 않습니다.`:'';
   q('.changes').replaceChildren(...s.writes.map(w=>{const row=D.el('div','change');row.append(D.el('strong','',s.state.cells[w.cellId]?.name||w.cellId),D.el('div','',`${D.format(w.before)} → ${D.format(w.after)}`));return row;}));if(!s.writes.length)q('.changes').append(D.el('p','trace-message','이 단계에서는 저장 값이 바뀌지 않았습니다.'));
   const c=s.state.cells[selection], desc=q('.selection');
   desc.replaceChildren();
   if(c){
    desc.append(D.el('strong','',`${c.name} · ${c.id}`),document.createElement('br'),
     document.createTextNode(`자신의 주소 ${c.address} / 저장 값 ${D.format(c.value)}`));
    if(c.lifetime==='live'&&c.value.kind==='pointer'&&c.value.target){
     const target=s.state.cells[c.value.target];
     desc.append(document.createElement('br'),document.createTextNode(`대상 ${target.id}의 값 ${D.format(target.value)}`));
    }
   }else desc.textContent='변수를 선택하면 값과 주소를 구분해 볼 수 있습니다.';
  }
  function recompile(){stop();treeUi?.reset();step=0;selection=null;const issues=D.validateInput(scenario.inputs,input);q('.input-error').textContent=issues.map(i=>i.message).join(' ');for(const field of app.querySelectorAll('[data-input]')){const v=input[field.dataset.input];field.value=Number.isNaN(v)?'':v;field.setAttribute('aria-invalid',String(issues.some(i=>i.path===field.dataset.input)));}play.disabled=!!issues.length;
   if(issues.length){if(trace)paint();for(const a of ['first','prev','next','last','scrub',...(tree?['previous-output','next-output']:[])])q(`[data-action=${a}]`).disabled=true;return;}q('[data-action=scrub]').disabled=false;trace=D.compileScenario(scenario,input);paint();}
  function move(n){if(play.disabled)return;stop();step=Math.max(0,Math.min(entries().length-1,n));paint();}
  function toggle(){if(play.disabled)return;if(timer!==null){stop();return;}if(step===entries().length-1)step=0;playIcon(true);play.setAttribute('aria-label','일시정지');app.dataset.playing='true';paint();timer=setInterval(()=>{step++;paint();if(step>=entries().length-1)stop();},900/speed);}
  on(preset,'change',()=>{input={...(preset.value==='default'?defaults:byPreset.get(preset.value))};recompile();});
  on(app,'click',e=>{const cell=e.target.closest('[data-cell-id]');if(cell&&!tree){selection=cell.dataset.cellId;paint();return;}const action=e.target.closest('[data-action]')?.dataset.action;
   if(action==='mode'){const value=e.target.closest('[data-mode-value]').dataset.modeValue;input.mode=value;preset.value='default';recompile();}
   if(action==='first')move(0);if(action==='prev')move(step-1);if(action==='next')move(step+1);if(action==='last')move(entries().length-1);if(action==='play')toggle();
   if(tree&&(action==='previous-output'||action==='next-output')){
    const next=printNeighbor(action==='previous-output'?-1:1);
    if(next>=0)move(next);
   }
   if(action==='theme'){const dark=document.documentElement.dataset.theme!=='dark';document.documentElement.dataset.theme=dark?'dark':'light';q('[data-action=theme]').innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true">'+(dark?'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>':'<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>')+'</svg>';q('[data-action=theme]').setAttribute('aria-label',dark?'밝은 테마로 전환':'어두운 테마로 전환');}
  });
  on(q('[data-action=scrub]'),'input',e=>move(Number(e.target.value)));
  on(document,'keydown',e=>{if(e.defaultPrevented||app.querySelector('dialog:modal,[aria-modal=true]')||/INPUT|SELECT|TEXTAREA|BUTTON|SUMMARY/.test(e.target.tagName)||e.target.matches?.('.tree-history .step-list'))return;if(['ArrowLeft','ArrowRight','Home','End',' '].includes(e.key)){e.preventDefault();if(e.key===' ')toggle();else move(e.key==='Home'?0:e.key==='End'?entries().length-1:step+(e.key==='ArrowRight'?1:-1));}});
  on(window,'resize',redraw);
  if(!tree){q('.provenance-text').textContent=scenario.sources.map(s=>`${s.label}: ${s.provenance?.path||'보충 예제'}${s.provenance?.page?' · p'+s.provenance.page:''}${s.provenance?.section?' · '+s.provenance.section:''}${s.provenance?.adjustments?' · '+s.provenance.adjustments:''}`).join('\n');q('.provenance-text').style.whiteSpace='pre-line';}
  recompile();
  return {destroy(){stop();destroyed=true;treeUi?.destroy();shell.destroy();listeners.forEach(f=>f());}};
 }
 D.mountPlayer=mountPlayer;
})(globalThis);
