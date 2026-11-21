(function (root) {
 'use strict';
 const cases={
  intro:[[8,3,10],[3,1,null],[1,null,null],[10,null,null]],
  lecture:[[18,7,26],[7,3,12],[3,null,null],[12,null,null],[26,null,31],[31,27,null],[27,null,null]],
  empty:[]
 };
 const note='복습노트/1105/.pack/정리노트_1105_Tree.md';
 const tree={rootCellId:'main.root',fields:{key:'key',left:'left',right:'right'}};
 const at=(sourceId,line)=>({sourceId,line});
 const walk=line=>at('walk',line);
 const nodeId=key=>'node-'+key;
 const keyCell=key=>nodeId(key)+'.key';
 const pointer=key=>({kind:'pointer',target:key===null?null:keyCell(key)});
 const cell=(owner,name,type,value)=>({
  id:owner+'.'+name,name,type,owner,address:'&'+owner+'.'+name,value,lifetime:'live'
 });

 const scenario={
  version:1,id:'inorder-1105',kind:'c-tree',tree,title:'중위 순회 한 줄씩 실행하기',
  intro:'다음 줄을 실행하며 전체 트리에서 현재 호출을 찾아보세요.',
  takeaway:'왼쪽 호출이 반환되면 현재 키를 출력합니다. 오른쪽 호출도 반환되면 현재 호출을 끝냅니다.',
  supplement:'1105 강의의 트리와 방문 순서를 바탕으로 실행을 관찰할 C 함수와 호출자를 보충했습니다.',
  sources:[
   {id:'walk',label:'inorder 함수',language:'c',text:[
    'void inorder(Node *p) {',
    '    if (p == NULL) return;',
    '    inorder(p->left);',
    '    printf("%d ", p->key);',
    '    inorder(p->right);',
    '}'
   ].join('\n'),provenance:{path:note,section:'§4 순회 · 중위 순회',supplement:true}},
   {id:'driver',label:'호출자',language:'c',text:'inorder(root);',
    provenance:{path:note,section:'§4 순회 · 중위 순회',supplement:true}}
  ],
  inputs:[{key:'treeCase',label:'트리 사례',type:'enum',default:'intro',options:[
   {value:'intro',label:'입문 트리 · 4개 노드'},
   {value:'lecture',label:'1105 강의 트리 · 7개 노드'},
   {value:'empty',label:'빈 트리 · NULL'}
  ]}],
  presets:[
   {id:'lecture',label:'1105 강의 트리',input:{treeCase:'lecture'}},
   {id:'empty',label:'빈 트리',input:{treeCase:'empty'}}
  ],
  initialState({treeCase}){
   const root=cell('main','root','Node *',pointer(cases[treeCase][0]?.[0]??null));
   const cells={[root.id]:root}, objects={};
   for(const [key,left,right] of cases[treeCase]){
    const id=nodeId(key);
    const fields=[
     cell(id,'key','int',{kind:'int',value:key}),
     cell(id,'left','Node *',pointer(left)),
     cell(id,'right','Node *',pointer(right))
    ];
    objects[id]={id,type:'Node',storage:'static',cellIds:fields.map(field=>field.id),lifetime:'live'};
    for(const field of fields)cells[field.id]=field;
   }
   const main={id:'main',functionId:'main',caller:null,cellIds:[root.id],lifetime:'live'};
   return {frames:{main},objects,cells,activeFrame:'main',stdout:[]};
  },
  *generateEvents({treeCase}){
   const nodes=new Map(cases[treeCase].map(([key,left,right])=>[key,{left,right}]));
   let nextFrame=0, nextLine=0;
   function* line(at,title,explanation,events){
    const lineStepId='inorder-'+(++nextLine);
    for(const event of events)yield {at,lineStepId,label:title,explanation,...event};
   }
   function* call(key,sourceCellId,callSite,resumeAt,memberOf,side){
    const id='call-'+(++nextFrame), value=pointer(key), parameter=cell(id,'p','Node *',value);
    const inputName=side?'p->'+side:'root';
    const argument=key===null?'NULL':key+'번 노드의 주소';
    const wait=resumeAt?' 현재 호출은 '+resumeAt.line+'행에서 재개합니다.':'';
    yield* line(callSite,side?(side==='left'?'왼쪽 자식 호출':'오른쪽 자식 호출'):'루트에서 순회 시작',
     inputName+'에 저장된 '+argument+'를 새 호출의 p에 복사합니다.'+wait,[
      {kind:'read',cellId:sourceCellId,...(memberOf&&{memberOf})},
      {kind:'call',frame:{id,functionId:'inorder',callSite,resumeAt,
       argumentSourceCellId:sourceCellId,parameterCellId:parameter.id}},
      {kind:'bind',cell:parameter,value,fromCellId:sourceCellId},
      {kind:'enter',frameId:id}
     ]);
    const resume=resumeAt?' 호출자의 '+resumeAt.line+'행으로 돌아갑니다.':' 호출자로 돌아가 순회가 끝납니다.';
    yield* line(walk(2),key===null?'NULL 기저 사례에서 반환':'NULL 조건 검사',
     key===null?'p가 NULL이므로 반환합니다. 이 호출의 p는 수명이 끝납니다.'+resume:
      'p가 '+argument+'를 담고 있어 다음 줄에서 왼쪽 자식을 호출합니다.',[
      {kind:'read',cellId:parameter.id},
      ...(key===null?[{kind:'return',frameId:id}]:[])
     ]);
    if(key===null)return;
    const {left,right}=nodes.get(key);
    yield* call(left,nodeId(key)+'.left',walk(3),walk(4),parameter.id,'left');
    yield* line(walk(4),'현재 키 출력','왼쪽 호출에서 돌아왔습니다. p가 가리키는 노드의 key '+key+'을(를) 읽어 출력합니다.',[
     {kind:'print-int',cellId:keyCell(key),memberOf:parameter.id}
    ]);
    yield* call(right,nodeId(key)+'.right',walk(5),walk(6),parameter.id,'right');
    yield* line(walk(6),'현재 호출에서 반환','오른쪽 호출이 끝났습니다. 현재 호출의 p는 수명이 끝납니다.'+resume,[
     {kind:'return',frameId:id}
    ]);
   }
   yield* call(cases[treeCase][0]?.[0]??null,tree.rootCellId,at('driver',1),null);
  }
 };
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;
 else root.DSInteractive.scenario=scenario;
})(globalThis);
