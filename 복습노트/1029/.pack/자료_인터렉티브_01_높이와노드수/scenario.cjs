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

 const full = [[1,2,3],[2,4,5],[3,6,7],[4,null,null],[5,null,null],[6,null,null],[7,null,null]];
 const chain = length => Array.from({length},(_,i) => [i+1,i+1 < length ? i+2 : null,null]);
 const cases = {full,skew7:chain(7),skew3:chain(3),single:chain(1),empty:[]};
 const visit = line => at('visit',line);
 const driver = line => at('driver',line);
 const provenance = {path:note,sha256,section:'§5–6 간선 수·노드 수와 높이',
  page:'5–6',supplement:true,adjustments:'강의 그림의 연결을 숫자 키로 구성하고 관찰용 C 함수를 작성함'};

 const scenario = {
  version:1,id:'height-1029',kind:'c-tree',tree,title:'이진 트리의 높이와 노드 수',
  watch:[
   {name:'n',label:'노드 수',cellId:'stats.n'},
   {name:'h',label:'최대 레벨',cellId:'stats.h'},
   {name:'d',label:'호출 레벨'}
  ],
  intro:'루트는 레벨 1이에요. 노드를 셀 때마다 지금까지 도달한 가장 깊은 레벨을 확인해 보세요.',
  supplement:'강의 p5–6의 트리 모양을 재현했어요. C 방문 함수와 빈 트리·루트만 있는 사례는 학습용 보충이에요. 출력의 숫자는 방문한 노드의 번호예요.',
  sources:[
   {id:'visit',label:'노드 수와 최대 레벨 세기',language:'c',provenance,text:[
    'void visit(Node *p, int d) {',
    '    if (!p) return;',
    '    ++n;',
    '    if (d > h) h = d;',
    '    printf("%d ", p->key);',
    '    visit(p->left, d + 1);',
    '    visit(p->right, d + 1);',
    '}'
   ].join('\n')},
   {id:'driver',label:'호출자 · n과 h는 0에서 시작',language:'c',provenance,
    text:'visit(root, 1);\nreport(n, h);'}
  ],
  ...selectors({
   full:'포화 · 노드 7개',skew7:'경사 · 노드 7개',skew3:'경사 · 노드 3개',
   single:'루트만',empty:'빈 트리'
  }),
  expected:finalChecks({
   default:{'stats.n':7,'stats.h':3},skew7:{'stats.n':7,'stats.h':7},
   skew3:{'stats.n':3,'stats.h':3},single:{'stats.n':1,'stats.h':1},empty:{'stats.n':0,'stats.h':0}
  }),
  initialState({example}) {
   return memory(cases[example],[],[['stats','static int',[
    cell('stats','n','int',int(0)),cell('stats','h','int',int(0))
   ]]]);
  },
  *generateEvents({example}) {
   const nodes = new Map(cases[example].map(([key,left,right]) => [key,{left,right}]));
   const line = lineWriter();
   let nextFrame = 0;
   let n = 0;
   let h = 0;

   function* walk(key,depth,arg,location,resumeAt,parent = null) {
    const id = 'call-' + (++nextFrame);
    const p = cell(id,'p','Node *',ptr(key));
    const d = cell(id,'d','int',int(depth));
    const target = key === null ? 'NULL' : key+'번 노드';
    yield* line(location,parent ? parent.side+' 호출' : '루트 호출',
     (parent ? parent.key+'번 노드의 '+parent.side+' 자식 ' : '루트 ')+target+
      '의 포인터와 레벨 인자 '+depth+'를 새 호출에 전달해요.',[
      read(arg,parent?.p),...(parent ? [read(parent.d)] : []),
      {kind:'call',frame:{id,functionId:'visit',callSite:location,resumeAt,
       argumentSourceCellId:arg,parameterCellId:p.id}},
      {kind:'bind',cell:p,value:p.value,fromCellId:arg},
      {kind:'bind',cell:d,value:d.value},
      {kind:'enter',frameId:id}
     ]);
    const back = parent
     ? parent.key+'번 노드의 '+resumeAt.line+'행으로 돌아가요.'
     : '호출자의 결과 확인으로 돌아가요.';
    yield* line(visit(2),key === null ? 'NULL이라 반환' : '노드 확인',
     key === null ? '대상이 NULL이라 노드나 레벨을 세지 않아요. '+back
      : key+'번 노드가 있는 레벨 '+depth+'을 계산에 사용할 수 있어요.',
     [read(p.id),...(key === null ? [{kind:'return',frameId:id}] : [])]);
    if (key === null) return;

    yield* line(visit(3),'노드 1개 더 세기',
     key+'번 노드를 세어 n이 '+n+'에서 '+(n+1)+'로 늘어요.',
     [read('stats.n'),write('stats.n',++n)]);
    const previous = h;
    h = Math.max(h,depth);
    yield* line(visit(4),'최대 레벨 비교',
     depth > previous ? '레벨 '+depth+'에 처음 도달했어요. 기존 최대 '+previous+'보다 깊으므로 h를 '+h+'로 올려요.'
      : '레벨 '+depth+'까지 왔어요. 기존 최대 '+h+' 이하여서 h를 유지해요.',
     [read(d.id),read('stats.h'),...(depth > previous ? [read(d.id),write('stats.h',h)] : [])]);
    yield* line(visit(5),'방문 번호 출력',key+'번 노드의 번호를 출력해요.',
     [print(keyCell(key),p.id)]);

    const {left,right} = nodes.get(key);
    yield* walk(left,depth+1,nodeId(key)+'.left',visit(6),visit(7),{key,p:p.id,d:d.id,side:'왼쪽'});
    yield* walk(right,depth+1,nodeId(key)+'.right',visit(7),visit(8),{key,p:p.id,d:d.id,side:'오른쪽'});
    yield* line(visit(8),'방문 완료',key+'번 노드의 두 자식을 모두 확인했어요. '+back,
     [{kind:'return',frameId:id}]);
   }

   yield* walk(cases[example][0]?.[0] ?? null,1,tree.rootCellId,driver(1),driver(2));
   const result = n === 0
    ? '빈 트리의 높이를 0으로 둬요. 노드와 간선은 모두 0개예요.'
    : '노드 '+n+'개 · 높이 '+h+' · 간선 '+(n-1)+'개. '+(
      example === 'full' ? '레벨별로 1 + 2 + 4개를 놓으면 7개를 높이 3에 담아요.'
      : example === 'skew7' ? '같은 7개라도 한 레벨에 하나씩 놓으면 높이가 7이에요.'
      : example === 'skew3' ? '같은 높이 3에서 한 레벨에 하나씩 놓으면 3개가 필요해요.'
      : '루트 하나가 레벨 1을 이루고 부모 간선은 없어요.');
   yield* line(driver(2),'높이와 노드 수 확인',result,[read('stats.n'),read('stats.h')]);
  }
 };

 if (typeof module !== 'undefined' && module.exports) module.exports = scenario;
 else root.DSInteractive.scenario = scenario;
})(globalThis);
