(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target});
 const cell=(id,value,type='int',owner='main')=>({id,name:id.split('.').at(-1),type,owner,address:`&${id}`,value,lifetime:'live'});
 const source=(id,label,pointer,call,supplement)=>({id,label,language:'c',text:`#include <stddef.h>\nvoid swap(${pointer?'int *px, int *py':'int px, int py'})\n{\n    int tmp;\n    tmp = ${pointer?'*px':'px'};\n    ${pointer?'*px = *py':'px = py'};\n    ${pointer?'*py':'py'} = tmp;\n}\nint main(void)\n{\n    int a = {{a}}, b = {{b}};\n    ${call};\n    return 0;\n}`,provenance:{path:'자료구조_강의록_2026/Software_3_ArrayStructureList.pdf',page:22,section:'s1-swap / s1-call-by-value',supplement,sha256:'765ff7fae303bdcf83aa116cf8171482d083641617c24314304ca01f6953917a',adjustments:'원본 swap 함수 보존. #include와 int main(void), 입력값·비교 모드 호출자는 보충. 원본 printf는 생략.'}});
 const scenario={version:1,id:'value-address',kind:'c-memory',title:'값과 주소는 어떻게 전달될까?',intro:'main의 a와 b를 확인하세요. 함수에 넘기면 무엇이 복사될까요?',takeaway:'C는 항상 값을 전달합니다. 포인터 인자도 주소 값의 복사이고, 그 주소를 따라가면 원본에 쓸 수 있습니다.',
  sources:[source('address','주소 값 복사 · 강의 swap',true,'swap(&a, &b)',false),source('value','정수 값 복사 · 비교 예제',false,'swap(a, b)',true),source('alias','같은 대상 두 번 · 보충',true,'swap(&a, &a)',true)],
  inputs:[{key:'a',label:'a',type:'integer',default:1,min:-99,max:99},{key:'b',label:'b',type:'integer',default:2,min:-99,max:99},{key:'mode',label:'전달 방식',type:'enum',default:'address',options:[{value:'address',label:'주소 값 복사'},{value:'value',label:'정수 값 복사'},{value:'alias',label:'같은 주소 두 번'}]}],
  presets:[{id:'value',label:'값만 복사하면?',input:{a:1,b:2,mode:'value'}},{id:'address',label:'주소를 복사하면?',input:{a:1,b:2,mode:'address'}},{id:'alias',label:'swap(&a, &a)',input:{a:1,b:2,mode:'alias'}},{id:'boundary',label:'경계 입력 -99와 99',input:{a:-99,b:99,mode:'address'}}],
  initialState({a,b}){return {frames:{main:{id:'main',functionId:'main',cellIds:['main.a','main.b'],lifetime:'live',caller:null}},objects:{},cells:{'main.a':cell('main.a',I(a)),'main.b':cell('main.b',I(b))},activeFrame:'main',stdout:[]};},
  generateEvents({a,b,mode}){
   const ptr=mode!=='value',alias=mode==='alias',sourceId=mode==='address'?'address':mode==='value'?'value':'alias',events=[];
   const e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload});
   const left=ptr?'main.a':'f.px',right=ptr?(alias?'main.a':'main.b'):'f.py',vRight=alias?a:b;
   e('call',12,'swap 호출을 준비합니다. 호출자의 a, b는 그대로 있고, 별도의 함수 저장 공간을 만듭니다.',{label:'호출 준비',frame:{id:'f',functionId:'swap',cellIds:[],lifetime:'live',callSite:{sourceId,line:12}}});
   const vx=ptr?P('main.a'):I(a),vy=ptr?P(alias?'main.a':'main.b'):I(b);
   e('bind',2,ptr?'&a라는 주소 값을 새 매개변수 px에 복사합니다. a 객체가 복제되지는 않습니다.':'a의 정수 값을 별도 변수 px에 복사합니다. px의 주소는 a와 다릅니다.',{label:'첫 인자 → px 복사',cell:cell('f.px',vx,ptr?'int *':'int','f'),value:vx,...(!ptr?{fromCellId:'main.a'}:{})});
   e('bind',2,ptr?(alias?'py도 &a를 받습니다. px와 py는 서로 다른 변수이지만 같은 a를 가리킵니다.':'&b라는 주소 값을 새 매개변수 py에 복사합니다.'):'b의 정수 값을 별도 변수 py에 복사합니다.',{label:'둘째 인자 → py 복사',cell:cell('f.py',vy,ptr?'int *':'int','f'),value:vy,...(!ptr?{fromCellId:'main.b'}:{})});
   e('enter',3,'복사가 끝나 swap 함수 본문으로 진입합니다.',{label:'함수 진입',frameId:'f'});
   e('declare',4,'임시 변수 tmp의 저장 공간을 만듭니다. 아직 값을 읽어서는 안 됩니다.',{label:'tmp 선언',cell:cell('f.tmp',{kind:'uninitialized'},'int','f')});
   e('read',5,ptr?'px에 담긴 주소를 따라가 a의 현재 값을 읽습니다.':'px에 복사된 정수를 읽습니다.',{label:'교환 전 값 읽기',cellId:left,...(ptr?{through:['f.px']}:{})});
   e('write',5,`${a}을 tmp에 보관합니다. 나중에 첫 값을 잃지 않기 위해서입니다.`,{label:'tmp에 첫 값 보관',cellId:'f.tmp',value:I(a)});
   e('read',6,ptr?'py에 담긴 주소를 따라가 둘째 값을 읽습니다.':'py의 정수 값을 읽습니다.',{label:'둘째 값 읽기',cellId:right,...(ptr?{through:['f.py']}:{})});
   e('write',6,ptr?(alias?'두 주소 모두 a를 가리키므로 a에 자신의 값을 씁니다.':'*px에 쓰면 main의 a가 바뀝니다. px에 담긴 주소 자체는 그대로입니다.'):'px만 바뀝니다. main의 a는 바뀌지 않습니다.',{label:ptr?'첫 대상에 쓰기':'px 복사본에 쓰기',cellId:left,value:I(vRight),...(ptr?{through:['f.px']}:{})});
   e('read',7,'보관해 둔 tmp의 첫 값을 읽습니다.',{label:'tmp 읽기',cellId:'f.tmp'});
   e('write',7,ptr?'py를 따라간 대상에 tmp를 씁니다. 주소를 복사했기 때문에 호출자의 객체를 바꿀 수 있습니다.':'py 복사본에 tmp를 씁니다. 호출자의 a와 b는 그대로입니다.',{label:ptr?'둘째 대상에 쓰기':'py 복사본에 쓰기',cellId:right,value:I(a),...(ptr?{through:['f.py']}:{})});
   e('return',8,'swap의 매개변수와 지역 변수 수명이 끝납니다. main의 변수는 살아 있습니다.',{label:'swap 반환',frameId:'f'});
   e('observe',13,ptr?(alias?'a 하나를 두 번 전달했으므로 a 값은 그대로입니다. 매개변수는 두 개여도 대상은 하나였습니다.':`main으로 돌아오면 a=${b}, b=${a}입니다. 주소 값은 복사했지만 그 주소로 원본에 썼습니다.`):`main의 a=${a}, b=${b}는 그대로입니다. 함수 안에서 바뀐 것은 복사본이었습니다.`,{label:'호출자 결과 확인'});return events;
  },expected:[{presetId:'default',checks:[{step:'last',cellId:'main.a',value:I(2)},{step:'last',cellId:'main.b',value:I(1)}]},{presetId:'value',checks:[{step:'last',cellId:'main.a',value:I(1)},{step:'last',cellId:'main.b',value:I(2)}]},{presetId:'alias',checks:[{step:'last',cellId:'main.a',value:I(1)}]}]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
