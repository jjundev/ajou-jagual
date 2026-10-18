(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const J=(n,p)=>{const a=Math.abs(n),d=a%10,b=a===0||d===0||[1,3,6,7,8].includes(d),l=a!==0&&d!==0&&[1,7,8].includes(d);const [x,y]=p.split('/');return `${n}${p==='으로/로'?(b&&!l?x:y):(b?x:y)}`;};
 const cell=(id,name,type,owner,address,value)=>({id,name,type,owner,address,value,lifetime:'live'});
 const NAMES=['A','B','C'],BASE=[10,20],values=(n,top)=>[...BASE.slice(0,n-1),top];
 const head=`#include <stdio.h>\n#include <stdlib.h>\ntypedef int element;\ntypedef struct StackNode {\n    element item;\n    struct StackNode *link;\n} StackNode;\ntypedef struct {\n    StackNode *top;\n} LinkedStackType;\nint is_empty(LinkedStackType *s)\n{\n    return (s->top == NULL);\n}\n// 삭제 함수\nelement pop(LinkedStackType *s)\n{\n    if( is_empty(s) ) {\n        fprintf(stderr, "스택이 비어있음\\n");\n        exit(1);\n    }\n    else{\n        StackNode *temp=s->top;\n`;
 const tail=`    }\n}\nint main(void)\n{\n    LinkedStackType s = { NULL };\n    /* 앞선 push로 노드 {{n}}개가 쌓여 있다고 가정 */\n    int x = pop(&s);\n    return 0;\n}`;
 const BODY={
  correct:`        int item = temp->item;\n        s->top = s->top->link;\n        free(temp);\n        return item;\n`,
  'late-read':`        s->top = s->top->link;\n        free(temp);\n        return temp->item;    /* 오류 예: 해제 후 읽기 */\n        /* item을 미리 보관하지 않음 */\n`,
  'free-first':`        int item = temp->item;\n        free(temp);           /* 오류 예: 먼저 해제 */\n        s->top = s->top->link;\n        return item;\n`
 };
 const provenance=supplement=>({path:'자료구조_강의록_2026/Software_5_Stack.pdf',page:18,section:'s0-linkedpop',sha256:'235bf69c42564fed2de833ae99701b849802d10093a028caa2bdfba1bc254e90',supplement,note:supplement?'비교용 오류 예 · 강의 pop의 보관·이동·해제 순서를 바꿨습니다.':'강의 p18 pop 본문 · is_empty, 헤더, main 호출자, 시작 노드는 보충입니다.',adjustments:supplement?'강의 pop의 보관·해제 순서를 바꾼 비교용 오류 예제. UB 지점은 실행하지 않고 해당 단계에서 중단.':'p18 pop 본문 보존. p16 타입 정의(StackeNode 오타를 StackNode로 고침), is_empty(top == NULL), #include, main 호출자, 시작 노드 가정은 보충.'});
 const sources=[
  {id:'correct',label:'값 보관 → top 이동 → free · 강의 pop',language:'c',text:head+BODY.correct+tail,provenance:provenance(false)},
  {id:'late-read',label:'free 뒤에 temp->item 읽기 · 오류 예',language:'c',text:head+BODY['late-read']+tail,provenance:provenance(true)},
  {id:'free-first',label:'top 이동 전에 free · 오류 예',language:'c',text:head+BODY['free-first']+tail,provenance:provenance(true)}
 ];
 const scenario={version:1,id:'linked-pop',kind:'c-memory',title:'연결 스택 pop: 보관하고, 옮기고, 해제하기',
  intro:'s.top이 맨 위 노드를 가리킵니다. 그 노드를 free하기 전에 무엇을 따로 보관해야 할까요? A~C는 그림의 노드 이름표이고, &C는 C 노드(구조체 전체)의 시작 주소를 뜻하는 기호입니다.',
  takeaway:'temp로 기존 첫 노드를 잡고, 값을 item에 복사하고, top을 다음 노드로 옮긴 뒤에 free합니다. free한 노드와 그 노드를 가리키던 포인터는 다시 읽을 수 없습니다.',
  sources,
  inputs:[{key:'top',label:'맨 위 노드 값',type:'integer',default:30,min:-99,max:99},{key:'n',label:'시작 노드 수',type:'integer',default:3,min:0,max:3},{key:'mode',label:'처리 순서',type:'enum',default:'correct',options:[{value:'correct',label:'강의 순서'},{value:'late-read',label:'해제 후 읽기 (오류 예)'},{value:'free-first',label:'먼저 해제 (오류 예)'}]}],
  presets:[{id:'correct',label:'C→B→A에서 꺼내기',input:{top:30,n:3,mode:'correct'}},{id:'last',label:'노드 하나에서 꺼내기',input:{top:30,n:1,mode:'correct'}},{id:'empty',label:'빈 스택에서 꺼내면?',input:{top:30,n:0,mode:'correct'}},{id:'late-read',label:'free 뒤에 값을 읽으면?',input:{top:30,n:3,mode:'late-read'}},{id:'free-first',label:'top을 옮기기 전에 free하면?',input:{top:30,n:3,mode:'free-first'}},{id:'boundary',label:'경계 값 -99 꺼내기',input:{top:-99,n:2,mode:'correct'}}],
  initialState({n,top}){const VALUES=values(n,top);
   const state={frames:{main:{id:'main',functionId:'main',cellIds:['s','x'],lifetime:'live',caller:null}},objects:{'main.s':{id:'main.s',type:'LinkedStackType',storage:'automatic',cellIds:['s'],lifetime:'live'}},cells:{},activeFrame:'main',stdout:[]};
   for(let i=n-1;i>=0;i--){const k=NAMES[i];state.objects[k]={id:k,type:'StackNode',storage:'allocated',cellIds:[k,k+'.link'],lifetime:'live'};
    state.cells[k]=cell(k,'item','element',k,'&'+k,I(VALUES[i]));state.cells[k+'.link']=cell(k+'.link','link','StackNode *',k,'&'+k+'.link',P(i?NAMES[i-1]:null));}
   state.cells.s=cell('s','s.top','StackNode *','main.s','&s',P(n?NAMES[n-1]:null));state.cells.x=cell('x','x','int','main','&x',U);return state;
  },
  generateEvents({n,top,mode}){const VALUES=values(n,top);
   const sourceId=mode,events=[],e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload});
   const T=n?NAMES[n-1]:null,N=n>1?NAMES[n-2]:null,val=n?VALUES[n-1]:null,next=N?'&'+N:'NULL';
   e('call',34,'pop(&s)를 호출합니다. pop만의 저장 공간을 만듭니다.',{label:'pop 호출',frame:{id:'f',functionId:'pop',cellIds:[],lifetime:'live',callSite:{sourceId,line:34}}});
   e('bind',16,'&s라는 주소 값을 매개변수 s에 복사합니다.',{label:'&s → 매개변수 s',cell:cell('f.s','s','LinkedStackType *','f','&f.s',P('s')),value:P('s')});
   e('enter',17,'pop 본문으로 들어갑니다.',{label:'pop 진입',frameId:'f'});
   e('call',18,'is_empty(s)를 호출합니다. is_empty도 자기 매개변수 s를 따로 가집니다.',{label:'is_empty 호출',frame:{id:'e',functionId:'is_empty',cellIds:[],lifetime:'live',callSite:{sourceId,line:18}}});
   e('bind',11,'pop의 s에 담긴 &s를 읽어 is_empty의 s에 복사합니다. 두 매개변수는 서로 다른 변수입니다.',{label:'s의 값 → is_empty의 s',cell:cell('e.s','s','LinkedStackType *','e','&e.s',P('s')),value:P('s'),fromCellId:'f.s'});
   e('enter',12,'is_empty 본문으로 들어갑니다.',{label:'is_empty 진입',frameId:'e'});
   e('read',13,T?`s->top은 &${T}이므로 NULL이 아닙니다. 결과는 0입니다.`:'s->top이 NULL이므로 결과는 1(비어 있음)입니다.',{label:'s->top == NULL?',cellId:'s',through:['e.s']});
   e('return',14,`is_empty가 ${T?0:1}을 돌려주고 끝납니다.`,{label:`is_empty 반환 ${T?0:1}`,frameId:'e'});
   if(!T){e('observe',20,'빈 스택이므로 오류 메시지를 출력하고 exit(1)을 호출합니다. exit은 반복문만 빠져나가는 것이 아니라 프로그램 전체를 끝냅니다. 그래서 pop은 값을 돌려주지 않고 x도 초기화되지 않습니다.',{label:'exit(1) · 프로그램 종료'});return events;}
   e('read',23,`s를 따라가 s.top의 값 &${T}를 읽습니다.`,{label:'s->top 읽기',cellId:'s',through:['f.s']});
   e('declare',23,`temp에 &${T}를 저장합니다. 이제 temp와 s.top이 같은 ${T} 노드를 가리킵니다.`,{label:`temp = &${T}`,cell:cell('f.temp','temp','StackNode *','f','&f.temp',P(T))});
   const readItem=line=>{e('read',line,`temp를 따라가 ${T} 노드의 item ${J(val,'을/를')} 읽습니다.`,{label:'temp->item 읽기',cellId:T,through:['f.temp']});e('declare',line,`item 변수에 ${J(val,'을/를')} 복사해 둡니다. 노드를 해제해도 이 값은 남습니다.`,{label:`item = ${val}`,cell:cell('f.item','item','int','f','&f.item',I(val))});};
   const moveTop=line=>{e('read',line,`s를 따라가 s.top의 값 &${T}를 읽습니다.`,{label:'s->top 읽기',cellId:'s',through:['f.s']});e('read',line,`s->top이 가리키는 ${T} 노드의 link를 읽습니다. 값은 ${next}입니다.`,{label:'s->top->link 읽기',cellId:T+'.link'});e('write',line,N?`s.top에 &${N}를 씁니다. 이제 맨 위는 ${N}이고, ${T}는 temp만 가리킵니다.`:`s.top에 NULL을 씁니다. 스택이 비었고, ${T}는 temp만 가리킵니다.`,{label:`s->top = ${next}`,cellId:'s',through:['f.s'],value:P(N)});};
   if(mode==='correct'){
    readItem(24);moveTop(25);
    e('free',26,`free(temp)로 ${T} 노드를 반납합니다. temp가 담던 주소 값은 이제 사용할 수 없는 값이 되며, 노드의 item과 link도 수명이 끝납니다.`,{label:'free(temp)',pointerCellId:'f.temp'});
    e('read',27,`보관해 둔 item ${J(val,'을/를')} 읽습니다. 해제된 노드를 읽지 않습니다.`,{label:'item 읽기',cellId:'f.item'});
    e('return',27,`${J(val,'을/를')} x에 돌려주고 pop의 s, temp, item 수명이 끝납니다.`,{label:`pop 반환 → x = ${val}`,frameId:'f',result:{cellId:'x',value:I(val)}});
    e('observe',35,`x = ${val}, s.top = ${next}입니다. ${T} 노드는 반납되었고 나머지 연결은 그대로입니다.`,{label:'호출 후 확인'});
   }else if(mode==='late-read'){
    moveTop(24);
    e('free',25,`free(temp)로 ${T} 노드를 반납합니다. 값을 따로 보관하지 않았습니다.`,{label:'free(temp)',pointerCellId:'f.temp'});
    e('read',26,`temp->item을 읽으려면 temp를 따라가야 하지만, temp는 해제된 노드를 가리키던 값이라 사용할 수 없습니다. 정의되지 않은 동작이므로 여기서 멈춥니다.`,{label:'temp->item 읽기 · 해제 후',cellId:T,through:['f.temp']});
   }else{
    readItem(24);
    e('free',25,`top을 옮기기 전에 free(temp)를 호출합니다. ${T} 노드가 반납되어 temp뿐 아니라 같은 노드를 가리키던 s.top도 사용할 수 없는 값이 됩니다.`,{label:'free(temp) · 먼저',pointerCellId:'f.temp'});
    e('read',26,`s->top->link를 구하려면 s.top을 읽어야 하지만 s.top은 해제된 노드를 가리키던 값입니다. ${T} 노드의 link는 이미 사라졌으므로 여기서 멈춥니다.`,{label:'s->top 읽기 · 해제 후',cellId:'s',through:['f.s']});
   }
   return events;
  },
  expected:[{presetId:'default',checks:[{step:'last',cellId:'x',value:I(30)},{step:'last',cellId:'s',value:P('B')}]},{presetId:'last',checks:[{step:'last',cellId:'x',value:I(30)},{step:'last',cellId:'s',value:P(null)}]},{presetId:'empty',checks:[{step:'last',cellId:'x',value:U},{step:'last',cellId:'s',value:P(null)}]},{presetId:'late-read',checks:[],diagnosticCode:'INDETERMINATE_READ'},{presetId:'free-first',checks:[],diagnosticCode:'INDETERMINATE_READ'},{presetId:'boundary',checks:[{step:'last',cellId:'x',value:I(-99)},{step:'last',cellId:'s',value:P('A')}]}]
 };
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
