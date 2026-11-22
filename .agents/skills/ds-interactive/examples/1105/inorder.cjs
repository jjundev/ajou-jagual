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
  intro:'루트에서 순회를 시작할 준비가 됐어요.',
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
   function* call(key,sourceCellId,callSite,resumeAt,parent){
    const id='call-'+(++nextFrame), value=pointer(key), parameter=cell(id,'p','Node *',value);
    const side=parent?.side==='left'?'왼쪽':'오른쪽';
    const label='inorder('+(key??'NULL')+')';
    const callMessage=parent ?
     (key===null ? parent.key+'의 '+side+' 자식이 비어 있어 '+label+'을 호출했어요.' :
      parent.key+'의 '+side+' 자식 주소로 '+label+'을 호출했어요.') :
     (key===null ? '루트가 비어 있어 inorder(NULL)을 호출했어요.' :
      '루트 노드의 주소로 '+label+'을 호출했어요.');
    yield* line(callSite,parent?side+' 자식 호출':'루트에서 순회 시작',callMessage,[
      {kind:'read',cellId:sourceCellId,...(parent&&{memberOf:parent.parameterId})},
      {kind:'call',frame:{id,functionId:'inorder',callSite,resumeAt,
       argumentSourceCellId:sourceCellId,parameterCellId:parameter.id}},
      {kind:'bind',cell:parameter,value,fromCellId:sourceCellId},
      {kind:'enter',frameId:id}
     ]);
    const nullReturn=parent ? side+' 자식이 NULL이라 '+parent.key+'번 노드의 호출로 돌아왔어요.' :
     '루트가 NULL이므로 키를 출력하지 않고 순회를 마쳤어요.';
    yield* line(walk(2),key===null?'NULL이라 반환':'NULL 조건 검사',
     key===null?nullReturn:'p가 '+key+'번 노드를 가리켜 왼쪽 자식 호출로 넘어가요.',[
      {kind:'read',cellId:parameter.id},
      ...(key===null?[{kind:'return',frameId:id}]:[])
     ]);
    if(key===null)return;
    const {left,right}=nodes.get(key);
    yield* call(left,nodeId(key)+'.left',walk(3),walk(4),{key,parameterId:parameter.id,side:'left'});
    yield* line(walk(4),'현재 키 출력','현재 노드의 키를 읽어 '+key+' 값을 출력했어요.',[
     {kind:'print-int',cellId:keyCell(key),memberOf:parameter.id}
    ]);
    yield* call(right,nodeId(key)+'.right',walk(5),walk(6),{key,parameterId:parameter.id,side:'right'});
    const returned=parent ? key+'번 노드의 순회를 마치고 '+parent.key+'번 노드의 호출로 돌아왔어요.' :
     '루트 호출에서 반환해 순회를 마쳤어요.';
    yield* line(walk(6),'현재 호출에서 반환',returned,[
     {kind:'return',frameId:id}
    ]);
   }
   yield* call(cases[treeCase][0]?.[0]??null,tree.rootCellId,at('driver',1),null);
  }
 };
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;
 else root.DSInteractive.scenario=scenario;
})(globalThis);
