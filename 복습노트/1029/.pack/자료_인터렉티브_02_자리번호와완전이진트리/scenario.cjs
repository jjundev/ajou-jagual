(function (root) {
 'use strict';
 const note = '복습노트/1029/.pack/정리노트_1029_Tree.md';
 const sha256 = '34e60dec63e704c7d6f8f65ce4c2bf725a04cd782f7a69094ec7937a8290242b';
 const tree = {rootCellId:'main.root', fields:{key:'key',left:'left',right:'right'}};
 const int = value => ({kind:'int',value});
 const nodeId = key => 'node-' + key;
 const keyCell = key => nodeId(key) + '.key';
 const ptr = key => ({kind:'pointer',target:key === null ? null : keyCell(key)});
 const cell = (owner,name,type,value) => ({
  id:owner+'.'+name, name, type, owner, address:'&'+owner+'.'+name, value, lifetime:'live'
 });
 const read = (cellId,memberOf) => ({kind:'read',cellId,...(memberOf && {memberOf})});
 const write = (cellId,value) => ({kind:'write',cellId,value:int(value)});
 const print = (cellId,memberOf) => ({kind:'print-int',cellId,memberOf});
 const at = (sourceId,line) => ({sourceId,line});

 function memory(nodes, mainCells = [], extraObjects = []) {
  const callerCells = [cell('main','root','Node *',ptr(nodes[0]?.[0] ?? null)),...mainCells];
  const cells = Object.fromEntries(callerCells.map(value => [value.id,value]));
  const objects = {};
  function addObject(id,type,storage,fields) {
   objects[id] = {id,type,storage,cellIds:fields.map(field => field.id),lifetime:'live'};
   for (const field of fields) cells[field.id] = field;
  }
  for (const [key,left,right] of nodes) {
   const id = nodeId(key);
   addObject(id,'Node','static',[
    cell(id,'key','int',int(key)),
    cell(id,'left','Node *',ptr(left)),
    cell(id,'right','Node *',ptr(right))
   ]);
  }
  for (const [id,type,fields] of extraObjects) addObject(id,type,'static',fields);
  const main = {id:'main',functionId:'main',caller:null,
   cellIds:callerCells.map(value => value.id),lifetime:'live'};
  return {frames:{main},objects,cells,activeFrame:'main',stdout:[]};
 }

 function lineWriter() {
  let next = 0;
  return function* line(location,label,explanation,events = [{kind:'observe'}]) {
   const lineStepId = 'exec-' + (++next);
   for (const event of events) yield {at:location,lineStepId,label,explanation,...event};
  };
 }

 function selectors(labels) {
  const [first,...rest] = Object.entries(labels);
  return {
   inputs:[{key:'example',label:'트리 사례',type:'enum',default:first[0],
    options:Object.entries(labels).map(([value,label]) => ({value,label}))}],
   presets:rest.map(([id,label]) => ({id,label,input:{example:id}}))
  };
 }

 function finalChecks(values) {
  return Object.entries(values).map(([presetId,entries]) => ({
   presetId,checks:Object.entries(entries).map(([cellId,value]) => ({step:'last',cellId,value:int(value)}))
  }));
 }

 const cases = {
  packed:[1,2,3,4,5],
  gap:[1,2,3,4,6],
  perfect:[1,2,3,4,5,6,7],
  single:[1],
  empty:[]
 };
 const provenance = {path:note,sha256,section:'§7–8 이진 트리 분류와 자리 번호',
  page:'7–8',supplement:true,adjustments:'p7 자리 번호, p8 인덱스로 만든 관찰용 C 배열 판정'};
 const main = line => at('scan',line);
 const scalar = (name,value) => cell('main',name,'int',int(value));

 const scenario = {
  version:1,id:'slots-1029',kind:'c-tree',tree,title:'자리 번호와 완전 이진 트리',
  watch:[
   {name:'i',label:'검사 자리',cellId:'main.i'},
   {name:'n',label:'노드 수',cellId:'main.n'},
   {name:'last',label:'마지막 점유',cellId:'main.last'},
   {name:'gap',label:'첫 빈자리',cellId:'main.gap'},
   {name:'limit',label:'검사 끝',cellId:'main.limit'}
  ],
  intro:'루트부터 위에서 아래로, 같은 층은 왼쪽부터 자리를 세어요. 첫 빈자리 뒤에 노드가 나오는지 살펴보세요. 노드 옆의 작은 숫자는 출력 순서예요.',
  supplement:'숫자는 노드의 자리 번호예요. 부모가 i번이면 왼쪽은 2i, 오른쪽은 2i+1이에요. limit은 마지막 레벨의 끝 번호예요. 배열 검사는 학습용 보충이에요.',
  sources:[{id:'scan',label:'자리 번호 검사',language:'c',provenance,text:[
   'for (i = 1; i <= limit; ++i) {',
   '  if (!slot[i]) {',
   '    if (!gap) gap = i;',
   '    continue;',
   '  }',
   '  printf("%d ", slot[i]->key);',
   '  ++n;',
   '  last = i;',
   '}',
   'complete = (n == last);',
   'perfect = n > 0 && n == limit;'
  ].join('\n')}],
  ...selectors({
   packed:'완전 · 자리 1~5',gap:'중간 빈칸 · 자리 5 비움',perfect:'포화 · 자리 1~7',
   single:'루트만',empty:'빈 트리'
  }),
  expected:finalChecks({
   default:{'main.gap':6,'main.n':5,'main.last':5,'main.complete':1,'main.perfect':0},
   gap:{'main.gap':5,'main.n':5,'main.last':6,'main.complete':0,'main.perfect':0},
   perfect:{'main.gap':0,'main.n':7,'main.last':7,'main.complete':1,'main.perfect':1},
   single:{'main.gap':0,'main.n':1,'main.last':1,'main.complete':1,'main.perfect':1},
   empty:{'main.gap':0,'main.n':0,'main.last':0,'main.complete':1,'main.perfect':0}
  }),
  initialState({example}) {
   const occupied = new Set(cases[example]);
   const limit = upperSlot(occupied);
   const valueAt = i => occupied.has(i) ? i : null;
   const nodes = [...occupied].map(i => [i,valueAt(2*i),valueAt(2*i+1)]);
   const slots = Array.from({length:limit+1},(_,i) => cell('slot',String(i),'Node *',ptr(valueAt(i))));
   return memory(nodes,[
    scalar('i',0),scalar('limit',limit),scalar('gap',0),scalar('n',0),scalar('last',0),
    scalar('complete',0),scalar('perfect',0)
   ],[['slot','Node *[]',slots]]);
  },
  *generateEvents({example}) {
   const occupied = new Set(cases[example]);
   const limit = upperSlot(occupied);
   const line = lineWriter();
   let gap = 0;
   let n = 0;
   let last = 0;
   for (let i = 1; i <= limit+1; i++) {
    const checks = i === 1 ? [] : [read('main.i')];
    const outcome = i <= limit ? i+'번 자리를 검사해요.' : '검사할 자리가 더 없어요.';
    yield* line(main(1),i <= limit ? '자리 '+i+' 검사' : '자리 검사 종료',outcome,
     [...checks,write('main.i',i),read('main.i'),read('main.limit')]);
    if (i > limit) break;

    const slot = 'slot.'+i;
    const filled = occupied.has(i);
    yield* line(main(2),filled ? '노드 있음' : '빈자리',
     filled ? (gap ? i+'번은 노드가 있어요. 그 앞의 '+gap+'번 자리가 이미 비어 있었어요.'
      : i+'번 자리에 노드가 있어요.') : i+'번 자리는 비어 있어요.',
     [read('main.i'),read(slot)]);
    if (!filled) {
     yield* line(main(3),'첫 빈자리 확인',
      gap ? '첫 빈자리 번호 '+gap+'를 유지해요.' : '첫 빈자리인 '+i+'를 gap에 저장해요.',
      [read('main.gap'),...(!gap ? [read('main.i'),write('main.gap',i)] : [])]);
     if (!gap) gap = i;
     yield* line(main(4),'다음 자리로','빈자리는 세지 않고 다음 번호로 넘어가요.');
     continue;
    }

    yield* line(main(6),'자리 번호 출력',i+'번이 채워져 있어 출력에 번호를 더해요.',
     [read('main.i'),print(keyCell(i),slot)]);
    yield* line(main(7),'노드 수 증가','지금까지 채워진 자리는 '+(n+1)+'개예요.',
     [read('main.n'),write('main.n',++n)]);
    last = i;
    yield* line(main(8),'마지막 번호 기록','지금까지 채워진 마지막 자리 번호는 '+last+'예요.',
     [read('main.i'),write('main.last',last)]);
   }

   const complete = n === last;
   const perfect = n > 0 && n === limit;
   yield* line(main(10),'완전 여부 판정',
    !n ? '빈 트리는 빈칸 뒤에 놓인 노드가 없어서 이 예제에서는 완전 조건을 만족한다고 봐요.'
     : complete ? '1번부터 '+last+'번까지 '+n+'개가 빈틈없이 차 있어 완전 이진 트리예요.'
     : '마지막 번호는 '+last+'인데 노드는 '+n+'개예요. '+gap+'번이 중간에 비어 있어 기타 이진 트리예요.',
    [read('main.n'),read('main.last'),write('main.complete',Number(complete))]);

   const next = last+1;
   const nextSpot = Math.floor(next/2)+'번의 '+(next%2 ? '오른쪽' : '왼쪽')+' 자식 자리';
   yield* line(main(11),'포화 여부 판정',
    n === 0 ? '포화 판정은 노드가 하나 이상일 때만 해요. 첫 노드는 1번 루트에 놓아요.'
     : perfect ? '현재 레벨의 끝인 '+limit+'번까지 모두 차 있어 포화이기도 해요. 다음 '+next+'번은 '+nextSpot+'예요.'
     : complete ? '현재 레벨의 끝 '+limit+'번까지 자리가 남아 있어요. 다음 '+next+'번은 '+nextSpot+'예요.'
     : '중간 빈자리가 남아 있어요. '+gap+'번 한 곳을 채우면 이 사례는 완전 이진 트리가 돼요.',
    [read('main.n'),...(n > 0 ? [read('main.n'),read('main.limit')] : []),
     write('main.perfect',Number(perfect))]);
  }
 };

 function upperSlot(occupied) {
  const last = Math.max(0,...occupied);
  return last ? 2 ** (Math.floor(Math.log2(last))+1) - 1 : 0;
 }

 if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
 else root.DSInteractive.scenario = scenario;
})(globalThis);
