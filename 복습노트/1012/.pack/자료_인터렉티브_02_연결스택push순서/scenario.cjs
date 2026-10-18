(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const J=(n,p)=>{const a=Math.abs(n),d=a%10,b=a===0||d===0||[1,3,6,7,8].includes(d),l=a!==0&&d!==0&&[1,7,8].includes(d);const [x,y]=p.split('/');return `${n}${p==='으로/로'?(b&&!l?x:y):(b?x:y)}`;};
 const cell=(id,name,type,owner,address,value)=>({id,name,type,owner,address,value,lifetime:'live'});
 const NAMES=['A','B','C'],VALUES=[10,20,30];
 const head=`#include <stdio.h>\n#include <stdlib.h>\ntypedef int element;\ntypedef struct StackNode {\n    element item;\n    struct StackNode *link;\n} StackNode;\ntypedef struct {\n    StackNode *top;\n} LinkedStackType;\n// 삽입 함수\nvoid push(LinkedStackType *s, element item)\n{\n    StackNode *temp=(StackNode *)malloc(sizeof(StackNode));\n    if( temp == NULL ){\n        fprintf(stderr, "메모리 할당에러\\n");\n        return;\n    }\n    else{\n        temp->item = item;\n`;
 const tail=`    }\n}\nint main(void)\n{\n    LinkedStackType s = { NULL };\n    /* 앞선 push로 노드 {{n}}개가 쌓여 있다고 가정 */\n    push(&s, {{item}});\n    return 0;\n}`;
 const provenance=supplement=>({path:'자료구조_강의록_2026/Software_5_Stack.pdf',page:17,section:'s0-linkedpush',sha256:'235bf69c42564fed2de833ae99701b849802d10093a028caa2bdfba1bc254e90',supplement,note:supplement?'비교용 오류 예 · 강의 push의 21·22줄 순서만 바꿨습니다.':'강의 p17 push 본문 · 타입 정의는 p16, 헤더·main 호출자·시작 노드는 보충입니다.',adjustments:supplement?'강의 push의 21·22줄 순서만 바꾼 비교용 오류 예제. 헤더·타입 정의(p16)·main 호출자는 보충.':'p17 push 본문 보존. p16 타입 정의의 별칭 오타 StackeNode를 StackNode로 고침. #include, main 호출자, 시작 노드 가정은 보충. malloc 성공을 가정하고 실패 분기는 실행하지 않음.'});
 const sources=[
  {id:'correct',label:'link 먼저 · 강의 push',language:'c',text:head+`        temp->link = s->top;\n        s->top = temp;\n`+tail,provenance:provenance(false)},
  {id:'wrong',label:'top 먼저 · 순서 오류 예',language:'c',text:head+`        s->top = temp;        /* 순서를 바꾼 오류 예 */\n        temp->link = s->top;\n`+tail,provenance:provenance(true)}
 ];
 const scenario={version:1,id:'linked-push',kind:'c-memory',title:'연결 스택 push: 무엇을 먼저 연결할까?',
  intro:'s.top이 맨 위 노드를 가리킵니다. 새 노드를 맨 앞에 붙일 때 link와 top 중 무엇을 먼저 바꿔야 기존 노드를 잃지 않을까요? A~D는 그림의 노드 이름표이고, &A는 A 노드(구조체 전체)의 시작 주소를 뜻하는 기호입니다.',
  takeaway:'새 노드의 link에 기존 top 주소를 먼저 적고, 그다음 top을 새 노드로 옮깁니다. top부터 바꾸면 기존 노드의 주소를 담은 곳이 사라집니다.',
  sources,
  inputs:[{key:'item',label:'넣을 값',type:'integer',default:40,min:-99,max:99},{key:'n',label:'시작 노드 수',type:'integer',default:3,min:0,max:3},{key:'mode',label:'연결 순서',type:'enum',default:'correct',options:[{value:'correct',label:'link 먼저 (강의)'},{value:'wrong',label:'top 먼저 (오류 예)'}]}],
  presets:[{id:'correct',label:'C→B→A 위에 D 넣기',input:{n:3,item:40,mode:'correct'}},{id:'wrong',label:'top부터 바꾸면?',input:{n:3,item:40,mode:'wrong'}},{id:'empty',label:'빈 스택에 넣기',input:{n:0,item:40,mode:'correct'}},{id:'empty-wrong',label:'빈 스택 + top 먼저',input:{n:0,item:40,mode:'wrong'}},{id:'same',label:'C와 같은 값 30 넣기',input:{n:3,item:30,mode:'correct'}},{id:'boundary',label:'경계 값 -99',input:{n:1,item:-99,mode:'correct'}}],
  initialState({n}){
   const state={frames:{main:{id:'main',functionId:'main',cellIds:['s'],lifetime:'live',caller:null}},objects:{'main.s':{id:'main.s',type:'LinkedStackType',storage:'automatic',cellIds:['s'],lifetime:'live'}},cells:{},activeFrame:'main',stdout:[]};
   for(let i=n-1;i>=0;i--){const k=NAMES[i];state.objects[k]={id:k,type:'StackNode',storage:'allocated',cellIds:[k,k+'.link'],lifetime:'live'};
    state.cells[k]=cell(k,'item','element',k,'&'+k,I(VALUES[i]));state.cells[k+'.link']=cell(k+'.link','link','StackNode *',k,'&'+k+'.link',P(i?NAMES[i-1]:null));}
   state.cells.s=cell('s','s.top','StackNode *','main.s','&s',P(n?NAMES[n-1]:null));return state;
  },
  generateEvents({n,item,mode}){
   const sourceId=mode,events=[],e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload});
   const oldTop=n?NAMES[n-1]:null,oldName=oldTop?`${oldTop} 노드`:'NULL';
   e('call',29,`push(&s, ${item})를 호출합니다. push만의 저장 공간을 만듭니다.`,{label:'push 호출',frame:{id:'f',functionId:'push',cellIds:[],lifetime:'live',callSite:{sourceId,line:29}}});
   e('bind',12,'&s라는 주소 값을 매개변수 s에 복사합니다. main의 구조체 s를 복제하지 않습니다.',{label:'&s → 매개변수 s',cell:cell('f.s','s','LinkedStackType *','f','&f.s',P('s')),value:P('s')});
   e('bind',12,`정수 ${J(item,'을/를')} 매개변수 item에 복사합니다.`,{label:`${item} → item`,cell:cell('f.item','item','element','f','&f.item',I(item)),value:I(item)});
   e('enter',13,'인자 복사가 끝나 push 본문으로 들어갑니다.',{label:'push 진입',frameId:'f'});
   e('declare',14,'지역 포인터 temp의 저장 공간을 만듭니다. 초기값은 오른쪽 malloc 호출의 결과로 정해집니다.',{label:'temp 선언',cell:cell('f.temp','temp','StackNode *','f','&f.temp',U)});
   e('allocate',14,'malloc이 StackNode 하나 크기의 새 노드 D를 할당하고 그 시작 주소를 temp에 씁니다. 실제 번지는 알 수 없어 &D로 표시합니다. 이 예제는 할당 성공을 가정합니다.',{label:'malloc → temp = &D',object:{id:'D',type:'StackNode',storage:'allocated',cellIds:['D','D.link']},cells:[cell('D','item','element','D','&D',U),cell('D.link','link','StackNode *','D','&D.link',U)],resultCellId:'f.temp'});
   e('read',15,'temp == NULL을 검사합니다. temp는 &D이므로 else 쪽으로 갑니다.',{label:'temp == NULL?',cellId:'f.temp'});
   e('read',20,`오른쪽 item의 값 ${J(item,'을/를')} 읽습니다.`,{label:'item 읽기',cellId:'f.item'});
   e('write',20,`temp를 따라가 D의 item에 ${J(item,'을/를')} 씁니다.`,{label:'temp->item = item',cellId:'D',through:['f.temp'],value:I(item)});
   if(mode==='correct'){
    e('read',21,`매개변수 s를 따라가 main의 s.top을 읽습니다. 값은 ${oldTop?'&'+oldTop:'NULL'}입니다.`,{label:'s->top 읽기',cellId:'s',through:['f.s']});
    e('read',21,'temp에 담긴 &D를 읽어 D의 link 필드 위치를 찾습니다.',{label:'temp 읽기',cellId:'f.temp'});
    e('write',21,oldTop?`D의 link에 &${oldTop}를 씁니다. 이제 D → ${NAMES.slice(0,n).reverse().join(' → ')} → NULL 연결이 생겼습니다. top은 아직 ${oldTop}를 가리킵니다.`:'빈 스택이었으므로 D의 link에 NULL을 씁니다. D가 마지막 노드가 됩니다.',{label:'temp->link = s->top',cellId:'D.link',value:P(oldTop)});
    e('read',22,'temp에 담긴 &D를 읽습니다.',{label:'temp 읽기',cellId:'f.temp'});
    e('write',22,oldTop?`s를 따라가 main의 s.top에 &D를 씁니다. ${oldTop}는 이미 D.link가 기억하므로 잃지 않습니다.`:'s를 따라가 main의 s.top에 &D를 씁니다.',{label:'s->top = temp',cellId:'s',through:['f.s'],value:P('D')});
   }else{
    e('read',21,'temp에 담긴 &D를 읽습니다.',{label:'temp 읽기',cellId:'f.temp'});
    e('write',21,oldTop?`s.top에 &D를 먼저 씁니다. &${oldTop}를 담고 있던 유일한 곳이 덮어써졌습니다. 수업에서 말한 "낙동강 오리알"이 되는 순간입니다.`:'s.top에 &D를 먼저 씁니다.',{label:'s->top = temp (먼저)',cellId:'s',through:['f.s'],value:P('D')});
    e('read',22,oldTop?'s->top을 읽으면 방금 쓴 &D가 나옵니다. 기존 top 주소는 더 이상 없습니다.':'s->top을 읽으면 원래 값 NULL이 아니라 방금 쓴 &D가 나옵니다.',{label:'s->top 읽기',cellId:'s',through:['f.s']});
    e('read',22,'temp에 담긴 &D를 읽어 D의 link 필드 위치를 찾습니다.',{label:'temp 읽기',cellId:'f.temp'});
    e('write',22,'D의 link에 &D를 씁니다. D가 자기 자신을 가리키는 고리가 됩니다.',{label:'temp->link = s->top',cellId:'D.link',value:P('D')});
   }
   e('return',24,'push가 끝나 매개변수 s, item과 지역 변수 temp의 수명이 끝납니다. malloc으로 받은 D 노드는 free 전까지 남습니다.',{label:'push 반환',frameId:'f'});
   e('observe',30,mode==='correct'?`top → ${['D',...NAMES.slice(0,n).reverse()].join(' → ')} → NULL입니다. 새 노드가 맨 앞에 붙고 기존 노드는 모두 이어져 있습니다.`:oldTop?`top → D → D → …로 D만 반복됩니다. ${NAMES.slice(0,n).reverse().join(', ')} 노드는 아직 할당되어 있지만 가리키는 포인터가 없어 다시 찾거나 free할 수 없습니다(메모리 누수).`:'잃은 노드는 없지만 D.link가 D 자신을 가리킵니다. NULL로 끝나지 않으므로 이 스택을 끝까지 순회하면 멈추지 않습니다.',{label:'호출 후 연결 확인'});
   return events;
  },
  expected:[{presetId:'default',checks:[{step:'last',cellId:'s',value:P('D')},{step:'last',cellId:'D.link',value:P('C')},{step:'last',cellId:'D',value:I(40)}]},{presetId:'wrong',checks:[{step:'last',cellId:'s',value:P('D')},{step:'last',cellId:'D.link',value:P('D')},{step:'last',cellId:'C.link',value:P('B')}]},{presetId:'empty',checks:[{step:'last',cellId:'D.link',value:P(null)}]},{presetId:'empty-wrong',checks:[{step:'last',cellId:'D.link',value:P('D')}]},{presetId:'same',checks:[{step:'last',cellId:'D',value:I(30)},{step:'last',cellId:'C',value:I(30)},{step:'last',cellId:'D.link',value:P('C')}]},{presetId:'boundary',checks:[{step:'last',cellId:'D',value:I(-99)},{step:'last',cellId:'D.link',value:P('A')}]}]
 };
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
