(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const cell=(id,name,type,owner,value)=>({id,name,type,owner,address:`&${id}`,value,lifetime:'live'});
 // Number + particle: pick the Korean particle by how the number is read aloud.
 const josa=s=>s.replace(/(\d+)(을|를|이|가|은|는|으로|로|과|와)(?=[\s.,)!?]|$)/g,(m,num,p)=>{const v=Number(num),d=v%10,bat=v===0||d===0||[1,3,6,7,8].includes(d),rieul=d!==0&&[1,7,8].includes(d);const pick={'을':bat?'을':'를','를':bat?'을':'를','이':bat?'이':'가','가':bat?'이':'가','은':bat?'은':'는','는':bat?'은':'는','과':bat?'과':'와','와':bat?'과':'와','으로':bat&&!rieul?'으로':'로','로':bat&&!rieul?'으로':'로'}[p];return num+pick;});
 const MAX=5,VALUES=[10,20,30,40,50];
 const PUSH='    else s->stack[++(s->top)] = item;';
 const WRONG='    else s->stack[(s->top)++] = item;  // 보충 비교: 저장 후 증가';
 const body=(store,call)=>[
  '#include <stdio.h>',
  '#include <stdlib.h>',
  '#define MAX_STACK_SIZE 5',
  'typedef int element;',
  'typedef struct {',
  '    element stack[MAX_STACK_SIZE];',
  '    int top;',
  '} StackType;',
  '// 공백 상태 검출 함수',
  'int is_empty(StackType *s)',
  '{',
  '    return (s->top == -1);',
  '}',
  '// 포화 상태 검출 함수',
  'int is_full(StackType *s)',
  '{',
  '    return (s->top == (MAX_STACK_SIZE-1));',
  '}',
  '// 삽입함수',
  'void push(StackType *s, element item)',
  '{',
  '    if( is_full(s) ) {',
  '        fprintf(stderr,"스택 포화 에러\\n");',
  '        return;',
  '    }',
  store,
  '}',
  '// 삭제함수',
  'element pop(StackType *s)',
  '{',
  '    if( is_empty(s) ) {',
  '        fprintf(stderr, "스택 공백 에러\\n");',
  '        exit(1);',
  '    }',
  '    else return s->stack[(s->top)--];',
  '}',
  'int main(void)',
  '{',
  '    StackType s;  /* 보충: init(&s) 후 {{n}}개를 push한 상태 (10, 20, 30, 40, 50 순) */',
  call,
  '    return 0;',
  '}'
 ].join('\n');
 const lines=body(PUSH,'    push(&s, {{x}});').split('\n');
 function L(needle,nth=1){let seen=0;for(let i=0;i<lines.length;i++)if(lines[i].includes(needle)&&++seen===nth)return i+1;throw Error('line not found: '+needle);}
 const CALL=L('    push(&s,'),STORE=L(PUSH);
 const prov=(supplement,adjustments,note)=>({note,path:'자료구조_강의록_2026/Software_5_Stack.pdf',page:14,section:'s2-pushpop',supplement,sha256:'235bf69c42564fed2de833ae99701b849802d10093a028caa2bdfba1bc254e90',adjustments});
 const common='StackType·is_empty·is_full은 S5 p13, push·pop 본문과 주석은 S5 p14 원문(줄 앞 공백만 정리). 1008 수업은 같은 순서를 p10–12 의사코드로 설명했고 p13–14 C 구현은 다음 시간 예고 범위다. #include, MAX_STACK_SIZE 값 5, main과 준비된 s는 보충.';
 const ORIG_NOTE='S5 p13–14 C 원문 · 1008 수업은 같은 순서를 p10–12 의사코드로 다뤘고, 헤더·main과 준비된 s는 보충했습니다.';
 const scenario={version:1,id:'array-stack',kind:'c-memory',title:'배열 스택에서 top을 먼저 옮기는 이유',
  intro:'main의 s를 확인하세요. top은 맨 위 요소의 인덱스이고, top보다 위의 칸은 아직 유효한 요소가 아닙니다.',
  takeaway:'push는 포화 검사 후 top을 먼저 1 올리고 그 칸에 저장합니다. pop은 공백 검사 후 stack[top]을 읽고 top을 1 내립니다. 저장 후 증가로 바꾸면 기존 맨 위 값을 덮어쓰거나, 빈 스택에서 stack[-1]에 접근합니다.',
  sources:[
   {id:'push',label:'push · S5 p14',language:'c',text:body(PUSH,'    push(&s, {{x}});'),provenance:prov(false,common,ORIG_NOTE)},
   {id:'pop',label:'pop · S5 p14',language:'c',text:body(PUSH,'    element e = pop(&s);'),provenance:prov(false,common,ORIG_NOTE)},
   {id:'wrong',label:'보충 비교 · 저장 후 증가',language:'c',text:body(WRONG,'    push(&s, {{x}});'),provenance:prov(true,common+' 저장 후 증가 한 줄은 노트의 덮어쓰기 경고를 확인하기 위한 보충 오답 예제이며 강의 코드가 아니다.','보충 오답 · 저장 후 증가로 바꾼 한 줄은 강의 코드가 아닙니다.')}
  ],
  inputs:[{key:'x',label:'push할 값',type:'integer',default:5,min:-99,max:99},{key:'n',label:'처음 요소 수',type:'integer',default:2,min:0,max:5},{key:'op',label:'연산',type:'enum',default:'push',options:[{value:'push',label:'push(&s, x)'},{value:'pop',label:'pop(&s)'},{value:'wrong',label:'보충 · 저장 후 증가'}]}],
  presets:[
   {id:'push-empty',label:'빈 스택에 push',input:{n:0,x:5,op:'push'}},
   {id:'push-fill',label:'마지막 칸 채우기 · 경계값 -99',input:{n:4,x:-99,op:'push'}},
   {id:'overflow',label:'가득 찬 스택에 push',input:{n:5,x:99,op:'push'}},
   {id:'pop',label:'요소 3개에서 pop',input:{n:3,x:5,op:'pop'}},
   {id:'underflow',label:'빈 스택에서 pop',input:{n:0,x:5,op:'pop'}},
   {id:'wrong',label:'저장 후 증가 · 덮어쓰기',input:{n:2,x:5,op:'wrong'}},
   {id:'wrong-empty',label:'저장 후 증가 · 빈 스택',input:{n:0,x:5,op:'wrong'}}
  ],
  initialState({n}){
   const ids=[...Array(MAX).keys()].map(i=>`s.stack[${i}]`).concat('s.top'),cells={};
   for(let i=0;i<MAX;i++)cells[`s.stack[${i}]`]=cell(`s.stack[${i}]`,`stack[${i}]`,'element','s',i<n?I(VALUES[i]):U);
   cells['s.top']=cell('s.top','top','int','s',I(n-1));
   return {frames:{main:{id:'main',functionId:'main',cellIds:[...ids],lifetime:'live',caller:null}},objects:{s:{id:'s',type:'StackType s',storage:'automatic',cellIds:ids,lifetime:'live'}},cells,activeFrame:'main',stdout:[]};
  },
  *generateEvents({n,x,op}){
   const sourceId=op,t=n-1,fn=op==='pop'?'pop':'push';
   const e=(kind,line,label,explanation,payload={})=>({kind,at:{sourceId,line},label:josa(label),explanation:josa(explanation),...payload});
   const SIG=L(op==='pop'?'element pop(':'void push(');
   if(op==='pop')yield e('declare',CALL,'e 선언','pop의 반환값을 받을 main의 변수 e를 만듭니다.',{cell:cell('main.e','e','element','main',U)});
   yield e('call',CALL,`${fn} 호출 준비`,op==='pop'?'pop(&s)를 호출합니다. pop만의 저장 공간을 만듭니다.':`push(&s, ${x})를 호출합니다. push만의 저장 공간을 만듭니다.`,{frame:{id:fn,functionId:fn,cellIds:[],lifetime:'live',callSite:{sourceId,line:CALL}}});
   yield e('bind',SIG,'s ← &s 복사','&s라는 주소 값을 매개변수 s에 복사합니다. 배열을 통째로 복사하지 않습니다. s의 시작 주소는 첫 칸 stack[0]의 주소와 같아서 &s.stack[0]으로 표시합니다.',{cell:cell(`${fn}.s`,'s','StackType *',fn,P('s.stack[0]')),value:P('s.stack[0]')});
   if(op!=='pop')yield e('bind',SIG,'item 복사',`정수 ${x}를 item에 복사합니다.`,{cell:cell('push.item','item','element','push',I(x)),value:I(x)});
   yield e('enter',SIG+1,`${fn} 진입`,`${fn} 본문으로 들어갑니다.`,{frameId:fn});
   const check=op==='pop'?'is_empty':'is_full',cid=op==='pop'?'emp':'full',hit=op==='pop'?n===0:n===MAX;
   const CHECK=L(op==='pop'?'    if( is_empty(s) )':'    if( is_full(s) )'),CSIG=L(`int ${check}(`);
   yield e('call',CHECK,`${check} 호출 준비`,op==='pop'?'꺼내기 전에 비어 있는지 먼저 검사합니다.':'넣기 전에 가득 찼는지 먼저 검사합니다.',{frame:{id:cid,functionId:check,cellIds:[],lifetime:'live',callSite:{sourceId,line:CHECK}}});
   yield e('bind',CSIG,'s 주소 값 복사',`${fn}의 s에 있던 주소 값을 ${check}의 s에 복사합니다.`,{cell:cell(`${cid}.s`,'s','StackType *',cid,P('s.stack[0]')),value:P('s.stack[0]'),fromCellId:`${fn}.s`});
   yield e('enter',CSIG+1,`${check} 진입`,`${check} 본문으로 들어갑니다.`,{frameId:cid});
   yield e('read',CSIG+2,'s->top 읽기',op==='pop'?`top은 ${t}입니다. ${t} == -1은 ${hit?'참':'거짓'}입니다.`:`top은 ${t}입니다. ${t} == MAX_STACK_SIZE-1(4)은 ${hit?'참':'거짓'}입니다.`,{cellId:'s.top'});
   yield e('return',CSIG+2,`${check} 반환 ${hit?1:0}`,`${hit?1:0}을 돌려줍니다. ${check}의 s는 수명이 끝납니다.`,{frameId:cid});
   if(op!=='pop'&&hit){
    yield e('observe',L('스택 포화 에러'),'overflow 메시지','가득 찼으므로 stderr에 "스택 포화 에러"를 출력합니다. 배열과 top은 바뀌지 않습니다.');
    yield e('return',L('        return;'),'push 반환','저장하지 않고 push가 끝납니다.',{frameId:'push'});
    yield e('observe',L('    return 0;'),'호출자 결과 확인',`top=${t}, stack[4]=${VALUES[4]} 그대로입니다. 넘치는 값은 저장되지 않았습니다.`);
    return;
   }
   if(op==='pop'&&hit){
    yield e('observe',L('스택 공백 에러'),'underflow 메시지','비어 있으므로 stderr에 "스택 공백 에러"를 출력합니다.');
    yield e('diagnostic',L('        exit(1);'),'exit(1)로 종료','exit(1): 빈 스택에서 꺼낼 요소가 없어 프로그램이 종료됩니다. main의 e는 값을 받지 못합니다.',{code:'PROGRAM_EXIT',message:'exit(1): 스택 공백 에러로 프로그램이 종료됩니다. main으로 돌아가지 않습니다.'});
    return;
   }
   if(op==='push'){
    yield e('read',STORE,'s->top 읽기',t>=0?`top은 ${t}입니다. stack[${t}]에 현재 맨 위 요소 ${VALUES[t]}가 있습니다.`:'top은 -1입니다. 아직 저장된 요소가 없습니다.',{cellId:'s.top'});
    yield e('write',STORE,'++(s->top)',`top을 먼저 ${t+1}로 올립니다. ++의 결과 ${t+1}이 저장할 인덱스입니다.`,{cellId:'s.top',value:I(t+1)});
    yield e('read',STORE,'item 읽기',`저장할 값 ${x}를 읽습니다.`,{cellId:'push.item'});
    yield e('write',STORE,`stack[${t+1}] = item`,`비어 있던 stack[${t+1}]에 ${x}를 저장합니다. 기존 맨 위 요소는 그대로입니다.`,{cellId:`s.stack[${t+1}]`,value:I(x)});
    yield e('return',STORE+1,'push 반환','push의 s와 item 수명이 끝납니다. main의 s에는 변경이 남습니다.',{frameId:'push'});
    yield e('observe',L('    return 0;'),'호출자 결과 확인',`top=${t+1}, 맨 위는 stack[${t+1}]=${x}입니다.${t+1===MAX-1?' 이제 가득 찬 상태라 다음 push는 overflow입니다.':''}`);
    return;
   }
   if(op==='wrong'){
    yield e('read',STORE,'s->top 읽기',`top은 ${t}입니다. 후위 ++는 증가 전 값 ${t}을 인덱스로 씁니다.`,{cellId:'s.top'});
    yield e('read',STORE,'item 읽기',`저장할 값 ${x}를 읽습니다.`,{cellId:'push.item'});
    yield e('write',STORE,`stack[${t}] = item`,t>=0?`증가 전 인덱스 ${t}에 저장해 현재 맨 위 요소 ${VALUES[t]}를 덮어씁니다.`:'증가 전 인덱스 -1에 저장하려 합니다. 배열 범위 밖이라 이 단계에서 멈춥니다.',{cellId:`s.stack[${t}]`,value:I(x)});
    yield e('write',STORE,'top 증가',`top을 ${t+1}로 올립니다. 이 줄의 저장과 증가의 순서는 C가 정하지 않지만 결과는 같습니다.`,{cellId:'s.top',value:I(t+1)});
    yield e('return',STORE+1,'push 반환','push의 s와 item 수명이 끝납니다.',{frameId:'push'});
    yield e('observe',L('    return 0;'),'호출자 결과 확인',`top=${t+1}이 가리키는 stack[${t+1}]은 아직 미초기화입니다. 원래 맨 위 값 ${VALUES[t]}는 사라졌고 새 값은 한 칸 아래에 있습니다.`);
    return;
   }
   const POP=L('    else return s->stack[(s->top)--];');
   yield e('read',POP,'s->top 읽기',`top은 ${t}입니다. 후위 --는 감소 전 값 ${t}을 인덱스로 씁니다.`,{cellId:'s.top'});
   yield e('read',POP,`stack[${t}] 읽기`,`맨 위 요소 ${VALUES[t]}를 읽습니다. 반환할 값입니다.`,{cellId:`s.stack[${t}]`});
   yield e('write',POP,'(s->top)--',`top을 ${t-1}로 내립니다.`,{cellId:'s.top',value:I(t-1)});
   yield e('return',POP,`${VALUES[t]} 반환`,`${VALUES[t]}를 main의 e에 저장하고 pop의 s 수명이 끝납니다.`,{frameId:'pop',result:{cellId:'main.e',value:I(VALUES[t])}});
   yield e('observe',L('    return 0;'),'호출자 결과 확인',`e=${VALUES[t]}, top=${t-1}입니다. stack[${t}]에 ${VALUES[t]}가 남아 있어도 top보다 위라 유효한 요소가 아닙니다.`);
  },
  expected:[
   {presetId:'default',checks:[{step:'last',cellId:'s.top',value:I(2)},{step:'last',cellId:'s.stack[2]',value:I(5)},{step:'last',cellId:'s.stack[1]',value:I(20)}]},
   {presetId:'push-empty',checks:[{step:'last',cellId:'s.top',value:I(0)},{step:'last',cellId:'s.stack[0]',value:I(5)}]},
   {presetId:'push-fill',checks:[{step:'last',cellId:'s.top',value:I(4)},{step:'last',cellId:'s.stack[4]',value:I(-99)}]},
   {presetId:'overflow',checks:[{step:'last',cellId:'s.top',value:I(4)},{step:'last',cellId:'s.stack[4]',value:I(50)}]},
   {presetId:'pop',checks:[{step:'last',cellId:'main.e',value:I(30)},{step:'last',cellId:'s.top',value:I(1)},{step:'last',cellId:'s.stack[2]',value:I(30)}]},
   {presetId:'underflow',diagnosticCode:'PROGRAM_EXIT',checks:[{step:'last',cellId:'s.top',value:I(-1)}]},
   {presetId:'wrong',checks:[{step:'last',cellId:'s.stack[1]',value:I(5)},{step:'last',cellId:'s.top',value:I(2)},{step:'last',cellId:'s.stack[2]',value:U}]},
   {presetId:'wrong-empty',diagnosticCode:'OUT_OF_BOUNDS',checks:[{step:'last',cellId:'s.top',value:I(-1)}]}
  ]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
