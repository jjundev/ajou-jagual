(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const cell=(id,name,type,owner,value)=>({id,name,type,owner,address:`&${id}`,value,lifetime:'live'});
 // Number + particle: pick the Korean particle by how the number is read aloud.
 const josa=s=>s.replace(/(\d+)(을|를|이|가|은|는|으로|로|과|와)(?=[\s.,)!?]|$)/g,(m,num,p)=>{const v=Number(num),d=v%10,bat=v===0||d===0||[1,3,6,7,8].includes(d),rieul=d!==0&&[1,7,8].includes(d);const pick={'을':bat?'을':'를','를':bat?'을':'를','이':bat?'이':'가','가':bat?'이':'가','은':bat?'은':'는','는':bat?'은':'는','과':bat?'과':'와','와':bat?'과':'와','으로':bat&&!rieul?'으로':'로','로':bat&&!rieul?'으로':'로'}[p];return num+pick;});
 const VALUES=[10,20,30];
 const text=[
  '#include <stdio.h>',
  '#include <stdlib.h>',
  'typedef int element;',
  'typedef struct ListNode {',
  '    element data;',
  '    struct ListNode *link;',
  '} ListNode;',
  'typedef struct {',
  '    ListNode *head;',
  '    int length;',
  '} ListType;',
  'void error(char *message) { fprintf(stderr, "%s\\n", message); exit(1); }',
  '// phead: 리스트의 헤드 포인터의 포인터',
  '// p : 선행 노드',
  '// new_node : 삽입될 노드',
  'void insert_node(ListNode **phead, ListNode *p, ListNode *new_node)',
  '{',
  '    if( *phead == NULL ){        // 공백리스트인 경우',
  '        new_node->link = NULL;',
  '        *phead = new_node;',
  '    }',
  '    else if( p == NULL ){ // p가 NULL이면 첫번째 노드로 삽입',
  '        new_node->link = *phead;',
  '        *phead = new_node;',
  '    }',
  '    else {                       // p 다음에 삽입',
  '        new_node->link = p->link;',
  '        p->link = new_node;',
  '    }',
  '}',
  '// 리스트안에서 pos 위치의 노드를 반환한다.',
  'ListNode *get_node_at(ListType *list, int pos)',
  '{',
  '    int i;',
  '    ListNode *tmp_node = list->head;',
  '    if( pos < 0 ) return NULL;',
  '    for (i=0; i<pos; i++)',
  '        tmp_node = tmp_node->link;',
  '    return tmp_node;',
  '}',
  '// 주어진 위치에 데이터를 삽입한다.',
  'void add(ListType *list, int position, element data)',
  '{',
  '    ListNode *p;',
  '    if ((position >= 0) && (position <= list->length)){',
  '        ListNode *node = (ListNode *)malloc(sizeof(ListNode));',
  '        if( node == NULL ) error("메모리 할당에러");',
  '        node->data = data;',
  '        p = get_node_at(list, position-1);',
  '        insert_node(&(list->head), p, node);',
  '        list->length++;',
  '    }',
  '}',
  'int main(void)',
  '{',
  '    ListType list1;  /* 보충: 길이 {{n}}인 리스트(앞에서부터 10, 20, 30 중 n개)를 준비한 상태 */',
  '    add(&list1, {{position}}, {{data}});',
  '    return 0;',
  '}'
 ].join('\n');
 const lines=text.split('\n');
 function L(needle,nth=1){let seen=0;for(let i=0;i<lines.length;i++)if(lines[i].includes(needle)&&++seen===nth)return i+1;throw Error('line not found: '+needle);}
 const scenario={version:1,id:'list-add',kind:'c-memory',title:'위치를 선행 노드로 바꿔 삽입하기',
  intro:'main의 list1과 이미 연결된 노드를 확인하세요. add는 위치를 받지만, insert_node는 선행 노드 포인터를 받습니다.',
  takeaway:'get_node_at(list, position-1)이 위치를 선행 노드 포인터로 바꿉니다. position이 0이면 NULL이 되어 insert_node가 head를 바꾸고, &(list->head)를 넘겼기 때문에 호출자의 head가 실제로 바뀝니다.',
  sources:[{id:'add',label:'add · get_node_at · insert_node',language:'c',text,provenance:{note:'S4 p47 get_node_at·add와 p25 insert_node 원문 · 헤더·ListNode·error·main과 준비된 list1은 보충했습니다.',path:'자료구조_강의록_2026/Software_4_List.pdf',page:47,section:'s0-adapter',supplement:false,sha256:'8daec2b3ba1a39259dfc9dea63ed8f492976da6392359e48a40d491a82254a62',adjustments:'get_node_at·add 본문은 S4 p47, insert_node 본문과 주석은 S4 p25, ListType은 S4 p45 원문. 줄 앞 공백만 정리. #include, ListNode 정의, error 함수, main과 준비된 list1은 보충.'}}],
  inputs:[{key:'position',label:'position',type:'integer',default:1,min:-99,max:99},{key:'data',label:'data',type:'integer',default:15,min:-99,max:99},{key:'n',label:'처음 노드 수',type:'integer',default:3,min:0,max:3}],
  presets:[
   {id:'middle',label:'가운데 삽입 · position=1',input:{n:3,position:1,data:15}},
   {id:'front',label:'맨 앞 삽입 · position=0',input:{n:3,position:0,data:-99}},
   {id:'tail',label:'맨 뒤 삽입 · position=length',input:{n:3,position:3,data:99}},
   {id:'empty',label:'빈 리스트에 삽입',input:{n:0,position:0,data:7}},
   {id:'over',label:'범위 밖 · position=4',input:{n:3,position:4,data:40}},
   {id:'negative',label:'음수 위치 · position=-1',input:{n:3,position:-1,data:5}}
  ],
  initialState({n}){
   const cells={},objects={};
   cells['list1.head']=cell('list1.head','head','ListNode *','list1',P(n?'n1.data':null));
   cells['list1.length']=cell('list1.length','length','int','list1',I(n));
   objects.list1={id:'list1',type:'ListType list1',storage:'automatic',cellIds:['list1.head','list1.length'],lifetime:'live'};
   for(let k=1;k<=n;k++){
    objects[`n${k}`]={id:`n${k}`,type:'ListNode (malloc)',storage:'allocated',cellIds:[`n${k}.data`,`n${k}.link`],lifetime:'live'};
    cells[`n${k}.data`]=cell(`n${k}.data`,'data','element',`n${k}`,I(VALUES[k-1]));
    cells[`n${k}.link`]=cell(`n${k}.link`,'link','ListNode *',`n${k}`,P(k<n?`n${k+1}.data`:null));
   }
   return {frames:{main:{id:'main',functionId:'main',cellIds:['list1.head','list1.length'],lifetime:'live',caller:null}},objects,cells,activeFrame:'main',stdout:[]};
  },
  *generateEvents({n,position,data}){
   const e=(kind,line,label,explanation,payload={})=>({kind,at:{sourceId:'add',line},label:josa(label),explanation:josa(explanation),...payload});
   const node=k=>k>=1&&k<=n?`n${k}.data`:null;
   yield e('call',L('add(&list1'),'add 호출 준비',`add(&list1, ${position}, ${data})를 호출합니다. add만의 저장 공간을 새로 만듭니다.`,{frame:{id:'add',functionId:'add',cellIds:[],lifetime:'live',callSite:{sourceId:'add',line:L('add(&list1')}}});
   yield e('bind',L('void add('),'list ← &list1 복사','&list1이라는 주소 값을 매개변수 list에 복사합니다. list1 구조체가 복제되지는 않습니다. list1의 시작 주소는 첫 멤버 head의 주소와 같아서 &list1.head로 표시합니다.',{cell:cell('add.list','list','ListType *','add',P('list1.head')),value:P('list1.head')});
   yield e('bind',L('void add('),'position 복사',`정수 ${position}을 매개변수 position에 복사합니다.`,{cell:cell('add.position','position','int','add',I(position)),value:I(position)});
   yield e('bind',L('void add('),'data 복사',`정수 ${data}를 매개변수 data에 복사합니다.`,{cell:cell('add.data','data','element','add',I(data)),value:I(data)});
   yield e('enter',L('void add(')+1,'add 진입','인자 복사가 끝나 add 본문으로 들어갑니다.',{frameId:'add'});
   yield e('declare',L('    ListNode *p;'),'p 선언','선행 노드를 담을 지역 포인터 p를 만듭니다. 아직 값이 없습니다.',{cell:cell('add.p','p','ListNode *','add',U)});
   yield e('read',L('(position >= 0)'),'position >= 0 검사',position>=0?`position=${position}은 0 이상입니다. 다음 조건을 검사합니다.`:`position=${position}은 0보다 작습니다. && 연산은 여기서 거짓으로 끝나 list->length를 읽지 않습니다.`,{cellId:'add.position'});
   const valid=position>=0&&position<=n;
   if(position>=0)yield e('read',L('(position >= 0)'),'list->length 읽기',`list가 가리키는 list1의 length는 ${n}입니다. ${position} <= ${n}은 ${position<=n?'참':'거짓'}입니다.`,{cellId:'list1.length'});
   if(!valid){
    yield e('return',L('void add(')+11,'add 반환',`조건이 거짓이라 노드를 만들지 않고 add가 끝납니다. 유효한 위치는 0부터 length(${n})까지입니다.`,{frameId:'add'});
    yield e('observe',L('return 0;'),'호출자 결과 확인',`list1은 그대로입니다. head와 length=${n}이 바뀌지 않았습니다.`);
    return;
   }
   yield e('declare',L('ListNode *node ='),'node 선언','malloc 결과를 담을 지역 포인터 node를 만듭니다.',{cell:cell('add.node','node','ListNode *','add',U)});
   yield e('allocate',L('ListNode *node ='),'새 노드 할당','malloc이 ListNode 하나의 공간을 만들고 그 시작 주소를 node에 저장합니다. 새 노드의 data와 link는 아직 정해지지 않았습니다.',{object:{id:'new',type:'ListNode (새 malloc)',storage:'allocated',cellIds:['new.data','new.link']},cells:[cell('new.data','data','element','new',U),cell('new.link','link','ListNode *','new',U)],resultCellId:'add.node'});
   yield e('read',L('if( node == NULL )'),'node NULL 검사','node는 새 노드를 가리키므로 NULL이 아닙니다. error는 호출하지 않습니다.',{cellId:'add.node'});
   yield e('write',L('node->data = data;'),'node->data에 쓰기',`node를 따라가 새 노드의 data에 ${data}를 씁니다.`,{cellId:'new.data',value:I(data),through:['add.node']});
   const pos=position-1;
   yield e('call',L('p = get_node_at('),'get_node_at 호출 준비',`위치 ${position}에 넣으려면 바로 앞 노드가 필요합니다. 그래서 position-1=${pos}을 넘깁니다.`,{frame:{id:'get',functionId:'get_node_at',cellIds:[],lifetime:'live',callSite:{sourceId:'add',line:L('p = get_node_at(')}}});
   yield e('bind',L('ListNode *get_node_at('),'list 주소 값 복사','add의 list에 있던 주소 값을 get_node_at의 list에 복사합니다. 두 list는 다른 변수지만 같은 list1을 가리킵니다.',{cell:cell('get.list','list','ListType *','get',P('list1.head')),value:P('list1.head'),fromCellId:'add.list'});
   yield e('bind',L('ListNode *get_node_at('),'pos ← position-1',`계산한 값 ${pos}을 pos에 복사합니다.`,{cell:cell('get.pos','pos','int','get',I(pos)),value:I(pos)});
   yield e('enter',L('ListNode *get_node_at(')+1,'get_node_at 진입','get_node_at 본문으로 들어갑니다. add는 결과를 기다립니다.',{frameId:'get'});
   yield e('declare',L('    int i;'),'i 선언','반복 변수 i를 만듭니다.',{cell:cell('get.i','i','int','get',U)});
   yield e('read',L('*tmp_node = list->head'),'list->head 읽기',`list를 따라가 list1의 head를 읽습니다. 값은 ${n?'&n1.data(첫 노드)':'NULL(빈 리스트)'}입니다.`,{cellId:'list1.head',through:['get.list']});
   yield e('declare',L('*tmp_node = list->head'),'tmp_node 초기화','읽은 head 값을 tmp_node에 복사해 둡니다.',{cell:cell('get.tmp_node','tmp_node','ListNode *','get',P(node(1)))});
   yield e('read',L('if( pos < 0 )'),'pos < 0 검사',pos<0?'pos가 -1이라 선행 노드가 없습니다. NULL을 돌려줍니다.':`pos=${pos}는 0 이상입니다. 노드를 따라갑니다.`,{cellId:'get.pos'});
   let result=null;
   if(pos<0){
    yield e('return',L('if( pos < 0 )'),'NULL 반환','반환값 NULL이 add의 p에 저장되고, get_node_at의 저장 공간은 끝납니다.',{frameId:'get',result:{cellId:'add.p',value:P(null)}});
   }else{
    yield e('write',L('for (i=0;'),'i = 0','반복을 시작하며 i에 0을 씁니다.',{cellId:'get.i',value:I(0)});
    let cur=1;
    for(let i=0;;i++){
     yield e('read',L('for (i=0;'),`i < pos 검사 (i=${i})`,`${i} < ${pos}은 ${i<pos?'참이라 한 칸 이동합니다.':'거짓이라 반복을 끝냅니다.'}`,{cellId:'get.i'});
     if(i>=pos)break;
     yield e('read',L('tmp_node = tmp_node->link;'),`n${cur}->link 읽기`,`tmp_node가 가리키는 n${cur}의 link를 읽습니다. 다음 노드 n${cur+1}의 주소입니다.`,{cellId:`n${cur}.link`});
     cur++;
     yield e('write',L('tmp_node = tmp_node->link;'),'tmp_node 이동',`tmp_node에 n${cur}의 주소를 씁니다. 노드 자체는 바뀌지 않습니다.`,{cellId:'get.tmp_node',value:P(node(cur))});
     yield e('write',L('for (i=0;'),'i++',`i를 ${i+1}로 늘립니다.`,{cellId:'get.i',value:I(i+1)});
    }
    result=node(cur);
    yield e('read',L('return tmp_node;'),'tmp_node 읽기',`반환할 tmp_node는 n${cur}을 가리킵니다. position ${position}의 바로 앞 노드입니다.`,{cellId:'get.tmp_node'});
    yield e('return',L('return tmp_node;'),'선행 노드 반환',`n${cur}의 주소가 add의 p에 저장됩니다. get_node_at의 i, pos, tmp_node는 수명이 끝납니다.`,{frameId:'get',result:{cellId:'add.p',value:P(result)}});
   }
   yield e('call',L('insert_node(&(list->head)'),'insert_node 호출 준비','&(list->head)는 list1의 head 변수 자체의 주소입니다. head에 담긴 첫 노드 주소가 아니라 head를 바꿀 수 있는 주소를 넘깁니다.',{frame:{id:'ins',functionId:'insert_node',cellIds:[],lifetime:'live',callSite:{sourceId:'add',line:L('insert_node(&(list->head)')}}});
   yield e('bind',L('void insert_node('),'phead ← &(list->head)','list가 가리키는 구조체에서 head 멤버의 주소를 계산해 phead에 복사합니다. phead는 head 변수를 가리킵니다.',{cell:cell('ins.phead','phead','ListNode **','ins',P('list1.head')),value:P('list1.head')});
   yield e('bind',L('void insert_node('),'p 복사',result?`add의 p에 있던 n${result.slice(1,2)}의 주소를 insert_node의 p에 복사합니다.`:'add의 p에 있던 NULL을 insert_node의 p에 복사합니다.',{cell:cell('ins.p','p','ListNode *','ins',P(result)),value:P(result),fromCellId:'add.p'});
   yield e('bind',L('void insert_node('),'new_node 복사','새 노드의 주소를 new_node에 복사합니다.',{cell:cell('ins.new_node','new_node','ListNode *','ins',P('new.data')),value:P('new.data'),fromCellId:'add.node'});
   yield e('enter',L('void insert_node(')+1,'insert_node 진입','insert_node 본문으로 들어갑니다.',{frameId:'ins'});
   yield e('read',L('if( *phead == NULL )'),'*phead 읽기',`phead를 따라가 head를 읽습니다. ${n?'첫 노드 주소가 있어 공백 리스트가 아닙니다.':'NULL이므로 공백 리스트입니다.'}`,{cellId:'list1.head',through:['ins.phead']});
   if(!n){
    yield e('write',L('new_node->link = NULL;'),'new_node->link = NULL','새 노드가 마지막 노드이므로 link에 NULL을 씁니다.',{cellId:'new.link',value:P(null)});
    yield e('write',L('*phead = new_node;'),'*phead = new_node','phead를 따라가 list1의 head에 새 노드 주소를 씁니다. 호출자의 head가 바뀝니다.',{cellId:'list1.head',value:P('new.data'),through:['ins.phead']});
   }else if(!result){
    yield e('read',L('else if( p == NULL )'),'p == NULL 검사','p가 NULL입니다. 선행 노드가 없으니 맨 앞에 넣습니다.',{cellId:'ins.p'});
    yield e('read',L('new_node->link = *phead;'),'*phead 읽기','phead를 따라가 현재 첫 노드 주소 &n1.data를 읽습니다.',{cellId:'list1.head',through:['ins.phead']});
    yield e('write',L('new_node->link = *phead;'),'new_node->link = 첫 노드','새 노드의 link가 기존 첫 노드 n1을 가리키게 합니다.',{cellId:'new.link',value:P('n1.data')});
    yield e('write',L('*phead = new_node;',2),'*phead = new_node','phead를 따라가 list1의 head에 새 노드 주소를 씁니다. phead 자신은 그대로이고, 대상인 head가 바뀝니다.',{cellId:'list1.head',value:P('new.data'),through:['ins.phead']});
   }else{
    const k=Number(result.slice(1,2)),next=node(k+1);
    yield e('read',L('else if( p == NULL )'),'p == NULL 검사',`p는 n${k}을 가리키므로 NULL이 아닙니다. p 다음에 넣습니다.`,{cellId:'ins.p'});
    yield e('read',L('new_node->link = p->link;'),`p->link 읽기`,`p가 가리키는 n${k}의 link를 읽습니다. 값은 ${next?`&${next}`:'NULL'}입니다.`,{cellId:`n${k}.link`});
    yield e('write',L('new_node->link = p->link;'),'new_node->link = p->link',`새 노드가 ${next?`n${k+1}`:'NULL'}을 가리키게 먼저 연결합니다. 이 순서라야 뒤쪽 노드를 잃지 않습니다.`,{cellId:'new.link',value:P(next)});
    yield e('write',L('p->link = new_node;'),'p->link = new_node',`n${k}의 link를 새 노드로 바꿉니다. head는 바뀌지 않습니다.`,{cellId:`n${k}.link`,value:P('new.data')});
   }
   yield e('return',L('void insert_node(')+14,'insert_node 반환','phead, p, new_node 매개변수의 수명이 끝납니다. 연결은 노드와 list1에 남습니다.',{frameId:'ins'});
   yield e('read',L('list->length++;'),'list->length 읽기',`list1의 length ${n}을 읽습니다.`,{cellId:'list1.length'});
   yield e('write',L('list->length++;'),'length 증가',`length를 ${n+1}로 늘립니다.`,{cellId:'list1.length',value:I(n+1)});
   yield e('return',L('void add(')+11,'add 반환','add의 list, position, data, p, node가 끝납니다. malloc한 새 노드는 리스트에 연결되어 남습니다.',{frameId:'add'});
   const order=VALUES.slice(0,n).map(String);order.splice(position,0,String(data));
   yield e('observe',L('return 0;'),'호출자 결과 확인',`head부터 따라가면 ${order.join(' → ')} 순서입니다. length=${n+1}.`);
  },
  expected:[
   {presetId:'default',checks:[{step:'last',cellId:'n1.link',value:P('new.data')},{step:'last',cellId:'new.link',value:P('n2.data')},{step:'last',cellId:'list1.length',value:I(4)},{step:'last',cellId:'list1.head',value:P('n1.data')}]},
   {presetId:'front',checks:[{step:'last',cellId:'list1.head',value:P('new.data')},{step:'last',cellId:'new.link',value:P('n1.data')},{step:'last',cellId:'new.data',value:I(-99)}]},
   {presetId:'tail',checks:[{step:'last',cellId:'n3.link',value:P('new.data')},{step:'last',cellId:'new.link',value:P(null)}]},
   {presetId:'empty',checks:[{step:'last',cellId:'list1.head',value:P('new.data')},{step:'last',cellId:'new.link',value:P(null)},{step:'last',cellId:'list1.length',value:I(1)}]},
   {presetId:'over',checks:[{step:'last',cellId:'list1.length',value:I(3)},{step:'last',cellId:'n3.link',value:P(null)}]},
   {presetId:'negative',checks:[{step:'last',cellId:'list1.length',value:I(3)},{step:'last',cellId:'list1.head',value:P('n1.data')}]}
  ]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
