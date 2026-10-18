(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const J=(n,p)=>{const a=Math.abs(n),d=a%10,b=a===0||d===0||[1,3,6,7,8].includes(d),l=a!==0&&d!==0&&[1,7,8].includes(d);const [x,y]=p.split('/');return `${n}${p==='으로/로'?(b&&!l?x:y):(b?x:y)}`;};
 const cell=(id,name,type,owner,address,value)=>({id,name,type,owner,address,value,lifetime:'live'});
 const SIZE=5,VALUES=[7,9,5,1,6],slot=i=>i===0?'s':`s.stack[${i}]`;
 const head=`#include <stdio.h>\n#include <stdlib.h>\n#define MAX_STACK_SIZE 5\ntypedef int element;\ntypedef struct {\n    element stack[MAX_STACK_SIZE];\n    int top;\n} StackType;\nint is_empty(StackType *s)\n{\n    return (s->top == -1);\n}\nint is_full(StackType *s)\n{\n    return (s->top == (MAX_STACK_SIZE-1));\n}\n// 삽입 함수\nvoid push(StackType *s, element item)\n{\n    if( is_full(s) ) {\n        fprintf(stderr,"스택 포화 에러\\n");\n        return;\n    }\n`;
 const tail=`}\n// 삭제 함수\nelement pop(StackType *s)\n{\n    if( is_empty(s) ) {\n        fprintf(stderr, "스택 공백 에러\\n");\n        exit(1);\n    }\n    else return s->stack[(s->top)--];\n}\nint main(void)\n{\n    StackType s;\n    /* 앞선 push로 원소 {{n}}개가 쌓여 있다고 가정 */\n    push(&s, {{item}});\n    int x = pop(&s);\n    return 0;\n}`;
 const provenance=supplement=>({path:'자료구조_강의록_2026/Software_5_Stack.pdf',page:14,section:'s0-pushpop',sha256:'235bf69c42564fed2de833ae99701b849802d10093a028caa2bdfba1bc254e90',supplement,note:supplement?'비교용 오류 예 · push의 전위 ++만 후위 ++로 바꿨습니다.':'강의 p13–14 코드 · 헤더, MAX_STACK_SIZE 5, main 호출자, 시작 원소는 보충입니다.',adjustments:supplement?'강의 push의 전위 ++를 후위 ++로 바꾼 비교용 오류 예제. UB 지점은 실행하지 않고 해당 단계에서 중단.':'p13 StackType·is_empty·is_full과 p14 push·pop 본문 보존(init·peek 생략). #include, MAX_STACK_SIZE 5, main 호출자, 시작 원소 가정은 보충.'});
 const sources=[
  {id:'correct',label:'++top 후 저장 · 강의 push',language:'c',text:head+`    else s->stack[++(s->top)] = item;\n`+tail,provenance:provenance(false)},
  {id:'wrong',label:'저장 후 top++ · 오류 예',language:'c',text:head+`    else s->stack[(s->top)++] = item;   /* 오류 예 */\n`+tail,provenance:provenance(true)}
 ];
 const scenario={version:1,id:'array-stack',kind:'c-memory',title:'배열 스택: ++top과 top--의 위치',
  intro:'s.top은 맨 위 원소의 인덱스입니다(빈 스택은 -1). push는 top을 언제 올리고, pop은 top을 언제 내릴까요? 같은 구조체 s를 push와 pop이 주소로 함께 바꿉니다.',
  takeaway:'push는 "증가부터 하고 쓴다": ++(s->top)의 새 값이 저장 위치입니다. pop의 (s->top)--는 감소 전 값으로 원소를 고르고, 함수가 돌아가기 전에 top을 하나 내립니다.',
  sources,
  inputs:[{key:'item',label:'push할 값',type:'integer',default:4,min:-99,max:99},{key:'n',label:'시작 원소 수',type:'integer',default:2,min:0,max:5},{key:'mode',label:'push 증가 위치',type:'enum',default:'correct',options:[{value:'correct',label:'전위 ++ (강의)'},{value:'wrong',label:'후위 ++ (오류 예)'}]}],
  presets:[{id:'correct',label:'[7, 9]에 4 넣고 꺼내기',input:{n:2,item:4,mode:'correct'}},{id:'wrong',label:'후위 ++로 바꾸면?',input:{n:2,item:4,mode:'wrong'}},{id:'empty',label:'빈 스택(top = -1)',input:{n:0,item:4,mode:'correct'}},{id:'empty-wrong',label:'빈 스택 + 후위 ++',input:{n:0,item:4,mode:'wrong'}},{id:'full',label:'꽉 찬 스택에 push',input:{n:5,item:4,mode:'correct'}},{id:'boundary',label:'마지막 칸에 -99',input:{n:4,item:-99,mode:'correct'}}],
  initialState({n}){
   const ids=[...Array(SIZE).keys()].map(slot);
   const state={frames:{main:{id:'main',functionId:'main',cellIds:[...ids,'s.top','x'],lifetime:'live',caller:null}},objects:{'main.s':{id:'main.s',type:'StackType',storage:'automatic',cellIds:[...ids,'s.top'],lifetime:'live'}},cells:{},activeFrame:'main',stdout:[]};
   ids.forEach((id,i)=>{state.cells[id]=cell(id,`s.stack[${i}]`,'element','main.s',i?`&s.stack[${i}]`:'&s.stack[0] (= &s)',i<n?I(VALUES[i]):U);});
   state.cells['s.top']=cell('s.top','s.top','int','main.s','&s.top',I(n-1));state.cells.x=cell('x','x','int','main','&x',U);return state;
  },
  generateEvents({n,item,mode}){
   const sourceId=mode,events=[],e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload});
   const check=(id,fn,line,from,owner,body,result,text)=>{
    e('call',line,`${fn}(s)를 호출합니다.`,{label:`${fn} 호출`,frame:{id,functionId:fn,cellIds:[],lifetime:'live',callSite:{sourceId,line}}});
    e('bind',owner,'호출한 함수의 s에 담긴 &s를 읽어 새 매개변수 s에 복사합니다.',{label:`s의 값 → ${fn}의 s`,cell:cell(id+'.s','s','StackType *',id,`&${id}.s`,P('s')),value:P('s'),fromCellId:from});
    e('enter',owner+1,`${fn} 본문으로 들어갑니다.`,{label:`${fn} 진입`,frameId:id});
    e('read',body,'매개변수 s에 담긴 &s를 읽어 구조체 s를 찾습니다.',{label:'s 읽기',cellId:id+'.s'});
    e('read',body,text,{label:'s->top 읽기',cellId:'s.top'});
    e('return',body+1,`${fn}${fn==='is_full'?'이':'가'} ${J(result,'을/를')} 돌려주고 끝납니다.`,{label:`${fn} 반환 ${result}`,frameId:id});
   };
   let top=n-1;
   e('call',39,`push(&s, ${item})를 호출합니다.`,{label:'push 호출',frame:{id:'p',functionId:'push',cellIds:[],lifetime:'live',callSite:{sourceId,line:39}}});
   e('bind',18,'&s라는 주소 값을 매개변수 s에 복사합니다. 배열 다섯 칸과 top을 복제하지 않습니다.',{label:'&s → 매개변수 s',cell:cell('p.s','s','StackType *','p','&p.s',P('s')),value:P('s')});
   e('bind',18,`정수 ${J(item,'을/를')} 매개변수 item에 복사합니다.`,{label:`${item} → item`,cell:cell('p.item','item','element','p','&p.item',I(item)),value:I(item)});
   e('enter',19,'push 본문으로 들어갑니다.',{label:'push 진입',frameId:'p'});
   const full=top===SIZE-1;
   check('fu','is_full',20,'p.s',13,15,full?1:0,full?`s.top이 4 = MAX_STACK_SIZE-1이므로 포화입니다.`:`s.top이 ${top}이므로 4가 아닙니다. 포화가 아닙니다.`);
   if(full){
    e('observe',21,'포화이므로 오류 메시지를 출력합니다. 배열 밖에 쓰지 않고 바로 돌아갑니다.',{label:'포화 에러 출력'});
    e('return',22,'push가 아무 칸도 바꾸지 않고 끝납니다.',{label:'push 반환 (저장 없음)',frameId:'p'});
   }else{
    e('read',24,'s에 담긴 &s를 읽어 구조체 s를 찾습니다.',{label:'s 읽기',cellId:'p.s'});
    e('read',24,`현재 s.top ${J(top,'을/를')} 읽습니다.`,{label:'s->top 읽기',cellId:'s.top'});
    if(mode==='correct'){
     e('write',24,`전위 ++: s.top을 ${J(top+1,'으로/로')} 올리고, 증가한 값 ${J(top+1,'이/가')} 저장할 인덱스가 됩니다. 수업의 "증가부터 하고 써라"입니다.`,{label:`++(s->top) → ${top+1}`,cellId:'s.top',value:I(top+1)});
     e('read',24,`저장할 item ${J(item,'을/를')} 읽습니다.`,{label:'item 읽기',cellId:'p.item'});
     e('write',24,`증가한 인덱스의 빈 칸 s.stack[${top+1}]에 ${J(item,'을/를')} 씁니다. 기존 원소는 그대로입니다.`,{label:`s->stack[${top+1}] = ${item}`,cellId:slot(top+1),value:I(item)});
     top++;
    }else{
     e('read',24,`저장할 item ${J(item,'을/를')} 읽습니다.`,{label:'item 읽기',cellId:'p.item'});
     if(top<0){e('write',24,'후위 ++의 식 값은 증가 전 -1입니다. s.stack[-1]은 배열 밖이라 쓰면 정의되지 않은 동작입니다. 여기서 멈춥니다.',{label:'s->stack[-1] = item · 범위 밖',cellId:'s.stack[-1]',value:I(item)});return events;}
     e('write',24,`후위 ++의 식 값은 증가 전 ${top}입니다. 맨 위 원소 s.stack[${top}]의 ${J(VALUES[top],'을/를')} ${J(item,'으로/로')} 덮어씁니다.`,{label:`s->stack[${top}] = ${item} · 덮어쓰기`,cellId:slot(top),value:I(item)});
     e('write',24,`s.top도 ${J(top+1,'이/가')} 됩니다. 같은 식 안의 두 변경 순서는 C가 정하지 않지만, 저장 위치는 증가 전 값이었습니다. 이제 top은 아직 아무것도 쓰지 않은 칸 s.stack[${top+1}]의 인덱스입니다.`,{label:`(s->top)++ → ${top+1}`,cellId:'s.top',value:I(top+1)});
     top++;
    }
    e('return',25,'push가 끝나 매개변수 s, item의 수명이 끝납니다. main의 s는 남습니다.',{label:'push 반환',frameId:'p'});
   }
   e('call',40,'pop(&s)를 호출합니다.',{label:'pop 호출',frame:{id:'q',functionId:'pop',cellIds:[],lifetime:'live',callSite:{sourceId,line:40}}});
   e('bind',27,'&s라는 주소 값을 pop의 매개변수 s에 복사합니다.',{label:'&s → 매개변수 s',cell:cell('q.s','s','StackType *','q','&q.s',P('s')),value:P('s')});
   e('enter',28,'pop 본문으로 들어갑니다.',{label:'pop 진입',frameId:'q'});
   check('em','is_empty',29,'q.s',9,11,0,`s.top이 ${top}이므로 -1이 아닙니다. 비어 있지 않습니다.`);
   e('read',33,'s에 담긴 &s를 읽어 구조체 s를 찾습니다.',{label:'s 읽기',cellId:'q.s'});
   e('read',33,`후위 --의 식 값은 감소 전 s.top ${top}입니다. 이 값이 꺼낼 인덱스입니다.`,{label:`s->top 읽기 (${top})`,cellId:'s.top'});
   const stored=mode==='wrong'&&!full?null:(top<n?VALUES[top]:item);
   e('read',33,stored===null?`s.stack[${top}]${[2,4,5,9].includes(top)?'는':'은'} 한 번도 쓰지 않은 칸입니다. 초기화되지 않은 값을 읽으므로 여기서 멈춥니다. 후위 ++가 한 칸 어긋나게 만든 결과입니다.`:`s.stack[${top}]의 ${J(stored,'을/를')} 반환값으로 정합니다.`,{label:`s->stack[${top}] 읽기`,cellId:slot(top)});
   if(stored===null)return events;
   e('write',33,`s.top을 ${J(top-1,'으로/로')} 내립니다. 원소를 고르는 데는 감소 전 값을 썼고, 감소는 pop이 돌아가기 전에 끝납니다(같은 식 안의 읽기와 감소 순서는 C가 정하지 않습니다). 배열 칸의 ${J(stored,'은/는')} 지우지 않지만 이제 유효 범위 밖입니다.`,{label:`(s->top)-- → ${top-1}`,cellId:'s.top',value:I(top-1)});
   e('return',33,`${J(stored,'을/를')} x에 돌려주고 pop의 매개변수 수명이 끝납니다.`,{label:`pop 반환 → x = ${stored}`,frameId:'q',result:{cellId:'x',value:I(stored)}});
   e('observe',41,full?`push가 포화로 거절되어 x는 원래 맨 위 값 ${stored}입니다. s.top은 ${top-1}입니다.`:`x = ${stored}, s.top = ${top-1}입니다. push한 값을 바로 pop했으므로 유효 원소는 처음 ${n}개와 같습니다.`,{label:'호출 후 확인'});
   return events;
  },
  expected:[{presetId:'default',checks:[{step:'last',cellId:'x',value:I(4)},{step:'last',cellId:'s.top',value:I(1)},{step:'last',cellId:'s.stack[2]',value:I(4)}]},{presetId:'wrong',checks:[{step:'last',cellId:'s.stack[1]',value:I(4)},{step:'last',cellId:'s.top',value:I(2)}],diagnosticCode:'UNINITIALIZED_READ'},{presetId:'empty',checks:[{step:'last',cellId:'x',value:I(4)},{step:'last',cellId:'s.top',value:I(-1)},{step:'last',cellId:'s',value:I(4)}]},{presetId:'empty-wrong',checks:[],diagnosticCode:'OUT_OF_BOUNDS'},{presetId:'full',checks:[{step:'last',cellId:'x',value:I(6)},{step:'last',cellId:'s.top',value:I(3)}]},{presetId:'boundary',checks:[{step:'last',cellId:'s.stack[4]',value:I(-99)},{step:'last',cellId:'x',value:I(-99)},{step:'last',cellId:'s.top',value:I(3)}]}]
 };
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
