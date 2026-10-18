(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const cell=(id,name,type,owner,value)=>({id,name,type,owner,address:`&${id}`,value,lifetime:'live'});
 // Number + particle: pick the Korean particle by how the number is read aloud.
 const josa=s=>s.replace(/(\d+)(을|를|이|가|은|는|으로|로|과|와)(?=[\s.,)!?]|$)/g,(m,num,p)=>{const v=Number(num),d=v%10,bat=v===0||d===0||[1,3,6,7,8].includes(d),rieul=d!==0&&[1,7,8].includes(d);const pick={'을':bat?'을':'를','를':bat?'을':'를','이':bat?'이':'가','가':bat?'이':'가','은':bat?'은':'는','는':bat?'은':'는','과':bat?'과':'와','와':bat?'과':'와','으로':bat&&!rieul?'으로':'로','로':bat&&!rieul?'으로':'로'}[p];return num+pick;});
 const VALUES=[10,20,30];
 const ORIGINAL='        remove_node(&(list->head),p,(p!=NULL)?p->link:NULL);';
 const FIXED='        remove_node(&(list->head),p,(p!=NULL)?p->link:list->head); // 보충 비교';
 const body=call=>[
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
  '// phead : 헤드 포인터에 대한 포인터',
  '// p: 삭제될 노드의 선행 노드',
  '// removed: 삭제될 노드',
  'void remove_node(ListNode **phead, ListNode *p, ListNode *removed)',
  '{',
  '    if( p == NULL )',
  '        *phead = (*phead)->link;',
  '    else',
  '        p->link = removed->link;',
  '    free(removed);',
  '}',
  'int is_empty(ListType *list)',
  '{',
  '    if( list->head == NULL ) return 1;',
  '    else return 0;',
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
  '// 주어진 위치의 데이터를 삭제한다.',
  'void delete(ListType *list, int pos)',
  '{',
  '    if (!is_empty(list) && (pos >= 0) && (pos < list->length)){',
  '        ListNode *p = get_node_at(list, pos-1);',
  call,
  '        list->length--;',
  '    }',
  '}',
  'int main(void)',
  '{',
  '    ListType list1;  /* 보충: 길이 {{n}}인 리스트(앞에서부터 10, 20, 30 중 n개)를 준비한 상태 */',
  '    delete(&list1, {{pos}});',
  '    return 0;',
  '}'
 ].join('\n');
 const lines=body(ORIGINAL).split('\n');
 function L(needle,nth=1){let seen=0;for(let i=0;i<lines.length;i++)if(lines[i].includes(needle)&&++seen===nth)return i+1;throw Error('line not found: '+needle);}
 const CALL=L('remove_node(&(list->head)');
 const prov=(supplement,adjustments,note)=>({note,path:'자료구조_강의록_2026/Software_4_List.pdf',page:48,section:'s0-adapter',supplement,sha256:'8daec2b3ba1a39259dfc9dea63ed8f492976da6392359e48a40d491a82254a62',adjustments});
 const scenario={version:1,id:'list-delete',kind:'c-memory',title:'첫 위치를 삭제하면 무엇이 해제될까?',
  intro:'list1과 연결된 노드를 확인하세요. delete는 pos-1의 선행 노드를 구하고, 세 번째 인자로 지울 노드를 remove_node에 넘깁니다.',
  takeaway:'원본 p48은 pos가 0일 때 removed에 NULL을 넘깁니다. remove_node는 head만 옮기고 free(NULL)은 아무것도 하지 않으므로, 첫 노드는 할당된 채 아무 포인터도 가리키지 않는 누수가 됩니다.',
  sources:[
   {id:'original',label:'원본 delete · S4 p48',language:'c',text:body(ORIGINAL),provenance:prov(false,'delete 본문은 S4 p48, remove_node 본문과 주석은 S4 p28, is_empty는 S4 p46, get_node_at은 S4 p47, ListType은 S4 p45 원문. 줄 앞 공백만 정리. #include, ListNode 정의, main과 준비된 list1은 보충.','S4 p48 delete와 p28 remove_node 원문 그대로 · 헤더·main과 준비된 list1은 보충했습니다.')},
   {id:'fixed',label:'보충 비교 · 첫 노드를 removed로 전달',language:'c',text:body(FIXED),provenance:prov(true,'원본 p48과 비교하기 위한 보충 수정. 셋째 인자의 NULL을 list->head로 바꾼 한 줄만 다르다. 강의에서 제시한 수정 코드가 아니다.','보충 비교 · 셋째 인자 한 줄만 list->head로 바꿨습니다. 강의 수정 코드가 아닙니다.')}
  ],
  inputs:[{key:'pos',label:'pos',type:'integer',default:0,min:-99,max:99},{key:'n',label:'처음 노드 수',type:'integer',default:3,min:0,max:3},{key:'mode',label:'셋째 인자',type:'enum',default:'original',options:[{value:'original',label:'원본 · NULL'},{value:'fixed',label:'보충 · head'}]}],
  presets:[
   {id:'leak',label:'원본 · 첫 노드 삭제',input:{n:3,pos:0,mode:'original'}},
   {id:'fixed-front',label:'보충 비교 · 첫 노드 삭제',input:{n:3,pos:0,mode:'fixed'}},
   {id:'middle',label:'가운데 삭제 · pos=1',input:{n:3,pos:1,mode:'original'}},
   {id:'last',label:'마지막 삭제 · pos=2',input:{n:3,pos:2,mode:'original'}},
   {id:'single',label:'노드 하나 · pos=0',input:{n:1,pos:0,mode:'original'}},
   {id:'empty',label:'빈 리스트',input:{n:0,pos:0,mode:'original'}},
   {id:'over',label:'범위 밖 · pos=3',input:{n:3,pos:3,mode:'original'}},
   {id:'negative',label:'음수 위치 · pos=-1',input:{n:3,pos:-1,mode:'original'}}
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
  *generateEvents({n,pos,mode}){
   const sourceId=mode;
   const e=(kind,line,label,explanation,payload={})=>({kind,at:{sourceId,line},label:josa(label),explanation:josa(explanation),...payload});
   const node=k=>k>=1&&k<=n?`n${k}.data`:null,name=t=>t?t.split('.')[0]:'NULL';
   const END=L('void delete(')+7;
   yield e('call',L('delete(&list1'),'delete 호출 준비',`delete(&list1, ${pos})를 호출합니다. delete만의 저장 공간을 만듭니다.`,{frame:{id:'del',functionId:'delete',cellIds:[],lifetime:'live',callSite:{sourceId,line:L('delete(&list1')}}});
   yield e('bind',L('void delete('),'list ← &list1 복사','&list1이라는 주소 값을 list에 복사합니다. list1의 시작 주소는 첫 멤버 head의 주소와 같아서 &list1.head로 표시합니다.',{cell:cell('del.list','list','ListType *','del',P('list1.head')),value:P('list1.head')});
   yield e('bind',L('void delete('),'pos 복사',`정수 ${pos}를 pos에 복사합니다.`,{cell:cell('del.pos','pos','int','del',I(pos)),value:I(pos)});
   yield e('enter',L('void delete(')+1,'delete 진입','delete 본문으로 들어갑니다.',{frameId:'del'});
   yield e('call',L('if (!is_empty(list)'),'is_empty 호출 준비','조건의 첫 부분 !is_empty(list)부터 계산합니다.',{frame:{id:'emp',functionId:'is_empty',cellIds:[],lifetime:'live',callSite:{sourceId,line:L('if (!is_empty(list)')}}});
   yield e('bind',L('int is_empty('),'list 주소 값 복사','delete의 list에 있던 주소 값을 is_empty의 list에 복사합니다.',{cell:cell('emp.list','list','ListType *','emp',P('list1.head')),value:P('list1.head'),fromCellId:'del.list'});
   yield e('enter',L('int is_empty(')+1,'is_empty 진입','is_empty 본문으로 들어갑니다.',{frameId:'emp'});
   yield e('read',L('if( list->head == NULL )'),'list->head 읽기',`list를 따라가 head를 읽습니다. ${n?'첫 노드 주소가 있으니 0을 돌려줍니다.':'NULL이니 1을 돌려줍니다.'}`,{cellId:'list1.head',through:['emp.list']});
   yield e('return',L(n?'else return 0;':'if( list->head == NULL )'),`is_empty 반환 ${n?0:1}`,n?'0을 돌려줍니다. !0은 참이라 다음 조건을 봅니다.':'1을 돌려줍니다. !1은 거짓이라 && 뒤의 조건은 계산하지 않습니다.',{frameId:'emp'});
   const valid=n>0&&pos>=0&&pos<n;
   if(n){
    yield e('read',L('if (!is_empty(list)'),'pos >= 0 검사',pos>=0?`pos=${pos}는 0 이상입니다.`:`pos=${pos}는 음수라 조건이 거짓입니다. list->length는 읽지 않습니다.`,{cellId:'del.pos'});
    if(pos>=0)yield e('read',L('if (!is_empty(list)'),'list->length 읽기',`length는 ${n}입니다. ${pos} < ${n}은 ${pos<n?'참':'거짓'}입니다.`,{cellId:'list1.length'});
   }
   if(!valid){
    yield e('return',END,'delete 반환',`조건이 거짓이라 아무 노드도 지우지 않고 delete가 끝납니다.${n?` 유효한 pos는 0부터 ${n-1}까지입니다.`:''}`,{frameId:'del'});
    yield e('observe',L('    return 0;'),'호출자 결과 확인',`list1은 그대로입니다. length=${n}.`);
    return;
   }
   const before=pos-1,prev=node(pos),target=node(pos+1),after=node(pos+2);
   yield e('declare',L('ListNode *p = get_node_at('),'p 선언','선행 노드를 받을 지역 포인터 p를 만듭니다. 호출 결과로 초기화됩니다.',{cell:cell('del.p','p','ListNode *','del',U)});
   yield e('call',L('ListNode *p = get_node_at('),'get_node_at 호출 준비',`지울 위치 ${pos}의 바로 앞을 찾기 위해 pos-1=${before}을 넘깁니다.`,{frame:{id:'get',functionId:'get_node_at',cellIds:[],lifetime:'live',callSite:{sourceId,line:L('ListNode *p = get_node_at(')}}});
   yield e('bind',L('ListNode *get_node_at('),'list 주소 값 복사','delete의 list 주소 값을 get_node_at의 list에 복사합니다.',{cell:cell('get.list','list','ListType *','get',P('list1.head')),value:P('list1.head'),fromCellId:'del.list'});
   yield e('bind',L('ListNode *get_node_at('),'pos ← pos-1',`계산한 값 ${before}을 get_node_at의 pos에 복사합니다. delete의 pos와는 다른 변수입니다.`,{cell:cell('get.pos','pos','int','get',I(before)),value:I(before)});
   yield e('enter',L('ListNode *get_node_at(')+1,'get_node_at 진입','get_node_at 본문으로 들어갑니다.',{frameId:'get'});
   yield e('declare',L('    int i;'),'i 선언','반복 변수 i를 만듭니다.',{cell:cell('get.i','i','int','get',U)});
   yield e('read',L('*tmp_node = list->head'),'list->head 읽기','list를 따라가 head를 읽습니다. 첫 노드 n1의 주소입니다.',{cellId:'list1.head',through:['get.list']});
   yield e('declare',L('*tmp_node = list->head'),'tmp_node 초기화','읽은 head 값을 tmp_node에 복사합니다.',{cell:cell('get.tmp_node','tmp_node','ListNode *','get',P('n1.data'))});
   yield e('read',L('if( pos < 0 )'),'pos < 0 검사',before<0?'pos가 -1이라 선행 노드가 없습니다. NULL을 돌려줍니다.':`pos=${before}는 0 이상입니다. 노드를 따라갑니다.`,{cellId:'get.pos'});
   if(before<0){
    yield e('return',L('if( pos < 0 )'),'NULL 반환','반환값 NULL이 delete의 p를 초기화합니다. get_node_at의 저장 공간은 끝납니다.',{frameId:'get',result:{cellId:'del.p',value:P(null)}});
   }else{
    yield e('write',L('for (i=0;'),'i = 0','반복을 시작하며 i에 0을 씁니다.',{cellId:'get.i',value:I(0)});
    let cur=1;
    for(let i=0;;i++){
     yield e('read',L('for (i=0;'),`i < pos 검사 (i=${i})`,`${i} < ${before}은 ${i<before?'참이라 한 칸 이동합니다.':'거짓이라 반복을 끝냅니다.'}`,{cellId:'get.i'});
     if(i>=before)break;
     yield e('read',L('tmp_node = tmp_node->link;'),`n${cur}->link 읽기`,`tmp_node가 가리키는 n${cur}의 link를 읽습니다.`,{cellId:`n${cur}.link`});
     cur++;
     yield e('write',L('tmp_node = tmp_node->link;'),'tmp_node 이동',`tmp_node에 n${cur}의 주소를 씁니다.`,{cellId:'get.tmp_node',value:P(node(cur))});
     yield e('write',L('for (i=0;'),'i++',`i를 ${i+1}로 늘립니다.`,{cellId:'get.i',value:I(i+1)});
    }
    yield e('read',L('return tmp_node;'),'tmp_node 읽기',`tmp_node는 n${cur}을 가리킵니다. 지울 위치 ${pos}의 바로 앞 노드입니다.`,{cellId:'get.tmp_node'});
    yield e('return',L('return tmp_node;'),'선행 노드 반환',`n${cur}의 주소가 delete의 p를 초기화합니다.`,{frameId:'get',result:{cellId:'del.p',value:P(prev)}});
   }
   // Third argument: (p!=NULL)?p->link:NULL (original) or list->head (supplement).
   yield e('read',CALL,'p != NULL 검사',prev?`p는 n${name(prev).slice(1)}을 가리키므로 셋째 인자는 p->link입니다.`:mode==='original'?'p가 NULL이라 원본의 셋째 인자는 NULL입니다. 지울 첫 노드의 주소를 넘기지 않습니다.':'p가 NULL이라 보충 코드의 셋째 인자는 list->head, 즉 지울 첫 노드입니다.',{cellId:'del.p'});
   let removed;
   if(prev){removed=target;yield e('read',CALL,'p->link 읽기',`선행 노드의 link를 읽습니다. 지울 노드 ${name(target)}의 주소입니다.`,{cellId:`${name(prev)}.link`});}
   else if(mode==='fixed'){removed='n1.data';yield e('read',CALL,'list->head 읽기','list를 따라가 head를 읽습니다. 지울 첫 노드 n1의 주소입니다.',{cellId:'list1.head',through:['del.list']});}
   else removed=null;
   yield e('call',CALL,'remove_node 호출 준비','&(list->head)는 head 변수 자체의 주소입니다. remove_node가 head를 바꿀 수 있습니다.',{frame:{id:'rm',functionId:'remove_node',cellIds:[],lifetime:'live',callSite:{sourceId,line:CALL}}});
   yield e('bind',L('void remove_node('),'phead ← &(list->head)','list가 가리키는 구조체의 head 멤버 주소를 phead에 복사합니다.',{cell:cell('rm.phead','phead','ListNode **','rm',P('list1.head')),value:P('list1.head')});
   yield e('bind',L('void remove_node('),'p 복사',prev?`선행 노드 ${name(prev)}의 주소를 p에 복사합니다.`:'NULL을 p에 복사합니다.',{cell:cell('rm.p','p','ListNode *','rm',P(prev)),value:P(prev),fromCellId:'del.p'});
   yield e('bind',L('void remove_node('),'removed 복사',removed?`지울 노드 ${name(removed)}의 주소를 removed에 복사합니다.`:'셋째 인자 NULL을 removed에 복사합니다. 지울 노드의 주소가 어디에도 전달되지 않았습니다.',{cell:cell('rm.removed','removed','ListNode *','rm',P(removed)),value:P(removed)});
   yield e('enter',L('void remove_node(')+1,'remove_node 진입','remove_node 본문으로 들어갑니다.',{frameId:'rm'});
   yield e('read',L('if( p == NULL )'),'p == NULL 검사',prev?'p가 NULL이 아니라 else 쪽을 실행합니다.':'p가 NULL이라 head를 다음 노드로 옮깁니다.',{cellId:'rm.p'});
   if(!prev){
    yield e('read',L('*phead = (*phead)->link;'),'*phead 읽기','phead를 따라가 head를 읽습니다. 첫 노드 n1의 주소입니다.',{cellId:'list1.head',through:['rm.phead']});
    yield e('read',L('*phead = (*phead)->link;'),'(*phead)->link 읽기',`n1의 link를 읽습니다. 값은 ${n>1?'&n2.data':'NULL'}입니다.`,{cellId:'n1.link'});
    yield e('write',L('*phead = (*phead)->link;'),'*phead = n1의 link',`phead를 따라가 list1의 head에 ${n>1?'n2의 주소':'NULL'}를 씁니다. ${mode==='original'?'이제 n1을 가리키던 head 값이 사라졌습니다.':'removed는 아직 n1을 가리킵니다.'}`,{cellId:'list1.head',value:P(node(2)),through:['rm.phead']});
   }else{
    yield e('read',L('p->link = removed->link;'),'removed->link 읽기',`지울 노드 ${name(target)}의 link를 읽습니다. 값은 ${after?`&${after}`:'NULL'}입니다.`,{cellId:`${name(target)}.link`});
    yield e('write',L('p->link = removed->link;'),'p->link 건너뛰기',`${name(prev)}의 link가 ${after?name(after):'NULL'}을 가리키게 바꿔 ${name(target)}을 리스트에서 뺍니다.`,{cellId:`${name(prev)}.link`,value:P(after)});
   }
   yield e('free',L('free(removed);'),removed?`free(${name(removed)})`:'free(NULL)',removed?`removed가 가리키는 ${name(removed)}를 해제합니다. 그 노드를 가리키던 removed는 더 이상 사용할 수 없는 값이 됩니다.`:'removed가 NULL이라 free(NULL)은 아무것도 하지 않습니다. n1은 여전히 할당되어 있습니다.',{pointerCellId:'rm.removed'});
   yield e('return',L('void remove_node(')+7,'remove_node 반환','phead, p, removed의 수명이 끝납니다.',{frameId:'rm'});
   yield e('read',L('list->length--;'),'list->length 읽기',`length ${n}을 읽습니다.`,{cellId:'list1.length'});
   yield e('write',L('list->length--;'),'length 감소',`length를 ${n-1}로 줄입니다.`,{cellId:'list1.length',value:I(n-1)});
   yield e('return',END,'delete 반환','delete의 list, pos, p 수명이 끝납니다.',{frameId:'del'});
   const left=VALUES.slice(0,n).filter((_,i)=>i!==pos);
   yield e('observe',L('    return 0;'),'호출자 결과 확인',`${left.length?'head부터 따라가면 '+left.join(' → '):'head가 NULL인 빈 리스트'}이고 length=${n-1}입니다. `+(!prev&&mode==='original'?'그러나 n1 객체는 해제되지 않았고, 이제 n1을 가리키는 포인터가 하나도 없습니다. 다시 free할 방법이 없는 메모리 누수입니다.':`${name(removed)} 객체는 해제되어 수명이 끝났습니다.`));
  },
  expected:[
   {presetId:'default',checks:[{step:'last',cellId:'list1.head',value:P('n2.data')},{step:'last',cellId:'n1.data',value:I(10)},{step:'last',cellId:'list1.length',value:I(2)}]},
   {presetId:'fixed-front',checks:[{step:'last',cellId:'list1.head',value:P('n2.data')},{step:'last',cellId:'list1.length',value:I(2)}]},
   {presetId:'middle',checks:[{step:'last',cellId:'n1.link',value:P('n3.data')},{step:'last',cellId:'list1.length',value:I(2)}]},
   {presetId:'last',checks:[{step:'last',cellId:'n2.link',value:P(null)}]},
   {presetId:'single',checks:[{step:'last',cellId:'list1.head',value:P(null)},{step:'last',cellId:'list1.length',value:I(0)},{step:'last',cellId:'n1.link',value:P(null)}]},
   {presetId:'empty',checks:[{step:'last',cellId:'list1.head',value:P(null)},{step:'last',cellId:'list1.length',value:I(0)}]},
   {presetId:'over',checks:[{step:'last',cellId:'list1.length',value:I(3)}]},
   {presetId:'negative',checks:[{step:'last',cellId:'list1.length',value:I(3)}]}
  ]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
