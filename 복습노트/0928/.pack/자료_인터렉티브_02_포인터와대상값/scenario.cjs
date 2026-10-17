(function(root){
 'use strict';const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target});
 const cell=(id,value,type='int',owner='main')=>({id,name:id.split('.').at(-1),type,owner,address:`&${id}`,value,lifetime:'live'});
 const source=id=>({id,label:id==='null'?'NULL 역참조 · 진단 예제':'대상 쓰기와 포인터 재대입 · 보충',language:'c',text:`#include <stddef.h>\nvoid change(int *p)\n{\n    *p = {{value}};\n    p = NULL;\n}\nint main(void)\n{\n    int a = {{a}};\n    int *q = ${id==='null'?'NULL':'&a'};\n    change(q);\n    return 0;\n}`,provenance:{path:'자료구조_강의록_2026/Software_3_ArrayStructureList.pdf',page:20,section:'s0-pointer-ops',sha256:'765ff7fae303bdcf83aa116cf8171482d083641617c24314304ca01f6953917a',supplement:true,adjustments:'슬라이드의 & / * 구분을 함수 호출 예제로 확장. NULL 사례는 실행하지 않고 원인 단계에서 중단.'}});
 const scenario={version:1,id:'pointer-target',kind:'c-memory',title:'포인터가 바뀔까, 대상이 바뀔까?',intro:'q의 현재 저장 값을 확인하세요. change(q)는 이 값을 어디로 복사할까요?',takeaway:'p는 주소를 담는 변수, &p는 p 자신의 주소, *p는 그 주소를 따라간 대상의 값입니다.',sources:[source('normal'),source('null')],
 inputs:[{key:'a',label:'a의 초기값',type:'integer',default:10,min:-99,max:99},{key:'value',label:'대상에 쓸 값',type:'integer',default:20,min:-99,max:99},{key:'mode',label:'시작 포인터',type:'enum',default:'normal',options:[{value:'normal',label:'q = &a'},{value:'null',label:'q = NULL · 진단'}]}],presets:[{id:'normal',label:'*p 쓰기 → p 재대입',input:{a:10,value:20,mode:'normal'}},{id:'null',label:'NULL이면 어디서 멈출까?',input:{a:10,value:20,mode:'null'}},{id:'boundary',label:'경계 입력 99 → -99',input:{a:99,value:-99,mode:'normal'}}],
 initialState({a,mode}){return {frames:{main:{id:'main',functionId:'main',cellIds:['main.a','main.q'],lifetime:'live',caller:null}},objects:{},cells:{'main.a':cell('main.a',I(a)),'main.q':cell('main.q',P(mode==='null'?null:'main.a'),'int *')},activeFrame:'main',stdout:[]};},
 generateEvents({value,mode}){const sourceId=mode==='null'?'null':'normal',events=[],e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload}),v=P(mode==='null'?null:'main.a');
 e('call',11,'change를 호출합니다. q와 별개인 매개변수 p를 만듭니다.',{label:'함수 호출',frame:{id:'f',functionId:'change',cellIds:[],lifetime:'live',callSite:{sourceId,line:11}}});
 e('bind',2,'q에 저장된 주소 값을 p에 복사합니다. 두 변수의 자기 주소는 다릅니다.',{label:'q의 값 → p 복사',cell:cell('f.p',v,'int *','f'),value:v,fromCellId:'main.q'});
 e('enter',3,'함수 본문으로 진입합니다.',{label:'change 진입',frameId:'f'});
 e('write',4,mode==='null'?'p가 NULL이므로 *p에는 쓸 수 없습니다. 여기서 중단합니다.':`*p = ${value}은 p가 가리키는 a에 씁니다. q와 p는 계속 같은 a를 가리킵니다.`,{label:'*p · 대상에 쓰기',cellId:'main.a',through:['f.p'],value:I(value)});
 e('write',5,'p = NULL은 함수 안의 p만 바꿉니다. q는 여전히 a를 가리키고 a에 쓴 값도 남아 있습니다.',{label:'p · 주소 값 재대입',cellId:'f.p',value:P(null)});
 e('return',6,'지역 매개변수 p의 수명이 끝납니다. 호출자 q와 대상 a는 살아 있습니다.',{label:'change 반환',frameId:'f'});
 e('observe',12,`q에는 &a가 남아 있고, a의 값은 ${value}입니다. 대상 쓰기와 포인터 재대입의 차이를 확인하세요.`,{label:'호출자 확인'});return events;},
 expected:[{presetId:'default',checks:[{step:'last',cellId:'main.a',value:I(20)},{step:'last',cellId:'main.q',value:P('main.a')}]},{presetId:'null',checks:[],diagnosticCode:'NULL_DEREFERENCE'}]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
