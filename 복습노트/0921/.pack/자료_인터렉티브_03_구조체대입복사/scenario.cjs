(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),P=target=>({kind:'pointer',target}),U={kind:'uninitialized'};
 const J=(n,p)=>{const a=Math.abs(n),d=a%10,b=a===0||d===0||[1,3,6,7,8].includes(d),l=a!==0&&d!==0&&[1,7,8].includes(d);const [x,y]=p.split('/');return `${n}${p==='으로/로'?(b&&!l?x:y):(b?x:y)}`;};
 const cell=(id,name,type,owner,address,value)=>({id,name,type,owner,address,value,lifetime:'live'});
 const pdf={path:'자료구조_강의록_2026/Software_3_ArrayStructureList.pdf',sha256:'765ff7fae303bdcf83aa116cf8171482d083641617c24314304ca01f6953917a'};
 const person=`#include <stdio.h>\ntypedef struct person {\n    int age;            // 나이를 나타내는 정수값\n    int height;         // 키(cm) · 강의는 float\n} person;\n`;
 const sources=[
  {id:'copy',label:'b = a · 강의 대입',language:'c',text:person+`int main(void)\n{\n    person a = { {{x}}, {{y}} }, b;\n    b = a;                  // 가능\n    a.age = a.age + 1;      // a만 바꾸면?\n    if( a.age > b.age )     // 필드를 골라 비교\n        printf("a가 b보다 나이가 많음");\n    return 0;\n}`,
   provenance:{...pdf,page:17,section:'s4-struct-assign',supplement:false,note:'강의 p17 대입·비교 · name[10]을 빼고 height를 int로 줄인 단순화, 초기값과 a.age 변경은 보충입니다.',adjustments:'p17 person 구조체에서 char name[10]을 빼고 float height를 int로 바꿔 정수 필드 두 개로 단순화. b = a; 원문 보존. 초기값, a.age 변경, 필드 비교 a.age > b.age(정리노트 보충)와 int main(void)는 보충.'}},
  {id:'uninit',label:'a를 초기화하지 않으면 · 강의 main',language:'c',text:person+`int main(void)\n{\n    person a, b;\n    b = a;                  // 가능\n    return 0;\n}`,
   provenance:{...pdf,page:17,section:'s4-struct-assign',supplement:false,note:'강의 p17 main 그대로 a를 초기화하지 않고 대입합니다 · 구조체 필드는 단순화했습니다.',adjustments:'p17 main 원문 그대로(main()→int main(void)) a를 초기화하지 않고 b = a; 실행. 복사할 값이 정해지지 않으므로 첫 필드 읽기에서 중단. person 필드 단순화는 copy와 같음.'}},
  {id:'link',label:'포인터 필드 복사 · 보충',language:'c',text:`#include <stddef.h>\ntypedef struct ListNode {\n    int data;               // 강의는 char data[10]\n    struct ListNode *link;\n} ListNode;\nint main(void)\n{\n    ListNode n2 = { {{y}}, NULL };\n    ListNode n1 = { {{x}}, &n2 };\n    ListNode c;\n    c = n1;                 // 필드별 복사\n    c.data = c.data + 1;    // c만 바뀜\n    c.link->data = 0;       // n2를 바꿈\n    int seen = n1.link->data;   // n1에서 보면?\n    return 0;\n}`,
   provenance:{...pdf,page:18,section:'s4-self-ref',supplement:true,note:'강의 p18 ListNode(data는 int로 단순화)로 대입이 포인터 필드를 어떻게 복사하는지 보는 보충 예제입니다.',adjustments:'p18 ListNode의 char data[10]을 int data로 단순화. main 전체(n1→n2 연결, c = n1, 필드 변경)는 p17 대입 규칙을 자체 참조 구조체에 적용한 보충.'}}
 ];
 const scenario={version:1,id:'struct-assign-copy',kind:'c-memory',title:'구조체 대입 b = a: 필드마다 값 복사',
  intro:'같은 타입의 두 구조체 변수는 필드 구성이 같습니다. 대입이 무엇을 복사하는지, 복사한 뒤 한쪽을 바꾸면 다른 쪽도 바뀌는지 보세요.',
  takeaway:'같은 타입 구조체의 대입은 모든 필드를 하나씩 값으로 복사합니다. 복사가 끝나면 두 변수는 따로 바뀝니다. 포인터 필드는 주소 값만 복사하므로 가리키는 대상은 함께 씁니다. 구조체 전체 비교(a > b)는 없고 a.age > b.age처럼 필드를 골라 비교합니다.',
  sources,
  inputs:[{key:'x',label:'첫 값 (a.age · n1.data)',type:'integer',default:20,min:-999,max:999},{key:'y',label:'둘째 값 (a.height · n2.data)',type:'integer',default:170,min:-999,max:999},{key:'mode',label:'예제',type:'enum',default:'copy',options:[{value:'copy',label:'b = a (강의)'},{value:'uninit',label:'a 미초기화 (강의 main)'},{value:'link',label:'포인터 필드 (보충)'}]}],
  presets:[{id:'copy',label:'a = {20, 170}을 b에 대입',input:{x:20,y:170,mode:'copy'}},{id:'same',label:'두 필드 값이 같을 때',input:{x:7,y:7,mode:'copy'}},{id:'min',label:'경계 입력 -999',input:{x:-999,y:-999,mode:'copy'}},{id:'max',label:'경계 입력 999',input:{x:999,y:999,mode:'copy'}},{id:'uninit',label:'강의 main처럼 a를 초기화하지 않으면?',input:{x:20,y:170,mode:'uninit'}},{id:'link',label:'포인터 필드 link를 복사하면?',input:{x:10,y:20,mode:'link'}}],
  initialState({mode}){
   const cells={},objects={},ids=[];
   const obj=(name,type,fields)=>{const cs=fields.map(([f,t])=>`${name}.${f}`);objects[`main.${name}`]={id:`main.${name}`,type,storage:'automatic',cellIds:cs,lifetime:'live'};
    fields.forEach(([f,t],i)=>{const id=`${name}.${f}`;cells[id]=cell(id,id,t,`main.${name}`,i?`&${id}`:`&${id} (= &${name})`,U);ids.push(id);});};
   if(mode==='link'){for(const n of ['n2','n1','c'])obj(n,'ListNode',[['data','int'],['link','struct ListNode *']]);cells.seen=cell('seen','seen','int','main','&seen',U);ids.push('seen');}
   else for(const n of ['a','b'])obj(n,'person',[['age','int'],['height','int']]);
   return {frames:{main:{id:'main',functionId:'main',cellIds:ids,lifetime:'live',caller:null}},objects,cells,activeFrame:'main',stdout:[]};
  },
  generateEvents({x,y,mode}){
   const sourceId=mode,events=[],e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload});
   if(mode==='uninit'){
    e('observe',8,'person a, b;는 두 구조체의 저장 공간만 만듭니다. 초기값이 없으므로 a의 필드에는 정해진 값이 없습니다.',{label:'a, b 선언'});
    e('read',9,'b = a는 a의 필드를 하나씩 읽어 b에 복사하려 합니다. 그런데 a.age에는 아직 아무 값도 쓴 적이 없어, 무엇을 복사할지 정해지지 않습니다. 강의 코드는 대입 문법이 가능하다는 것만 보여 주므로, 실제로 쓸 때는 a에 먼저 값을 넣어야 합니다.',{label:'a.age 읽기',cellId:'a.age'});
    return events;
   }
   if(mode==='link'){
    e('write',8,`n2를 초기화합니다. n2.data에 ${J(y,'을/를')} 씁니다.`,{label:`n2.data = ${y}`,cellId:'n2.data',value:I(y)});
    e('write',8,'n2.link에 NULL을 씁니다. n2 다음 노드는 없습니다.',{label:'n2.link = NULL',cellId:'n2.link',value:P(null)});
    e('write',9,`n1.data에 ${J(x,'을/를')} 씁니다.`,{label:`n1.data = ${x}`,cellId:'n1.data',value:I(x)});
    e('write',9,'n1.link에 &n2를 씁니다. link는 자기와 같은 ListNode만 가리킬 수 있습니다.',{label:'n1.link = &n2',cellId:'n1.link',value:P('n2.data')});
    e('observe',10,'ListNode c;는 c의 저장 공간만 만듭니다. 아직 값이 없습니다.',{label:'c 선언'});
    e('read',11,'c = n1은 필드 순서대로 복사합니다. 먼저 n1.data를 읽습니다.',{label:'n1.data 읽기',cellId:'n1.data'});
    e('write',11,`읽은 ${J(x,'을/를')} c.data에 씁니다.`,{label:`c.data = ${x}`,cellId:'c.data',value:I(x)});
    e('read',11,'다음 필드 n1.link를 읽습니다. 담긴 값은 n2의 주소입니다.',{label:'n1.link 읽기',cellId:'n1.link'});
    e('write',11,'주소 값 &n2를 c.link에 복사합니다. n2 노드 자체는 복제되지 않아, n1.link와 c.link가 같은 n2를 가리킵니다.',{label:'c.link = &n2',cellId:'c.link',value:P('n2.data')});
    e('read',12,`c.data(${x})를 읽습니다.`.replace(`(${x})를`,`(${x})${J(x,'을/를').slice(String(x).length)}`),{label:'c.data 읽기',cellId:'c.data'});
    e('write',12,`c.data에 ${J(x+1,'을/를')} 씁니다. c는 n1과 다른 저장 공간이라 n1.data는 ${J(x,'으로/로')} 그대로입니다.`,{label:`c.data = ${x+1}`,cellId:'c.data',value:I(x+1)});
    e('write',13,`c.link를 따라가 n2.data에 0을 씁니다. n1.link도 같은 n2를 가리키므로 n1에서 따라가도 0이 보입니다.`,{label:'c.link->data = 0',cellId:'n2.data',value:I(0),through:['c.link']});
    e('read',14,'n1.link를 따라가 n2.data를 읽습니다. c.link로 바꾼 값이 그대로 보입니다.',{label:'n1.link->data 읽기',cellId:'n2.data',through:['n1.link']});
    e('write',14,'읽은 0을 seen에 씁니다. n1과 c는 따로 있지만 같은 n2를 가리킵니다.',{label:'seen = 0',cellId:'seen',value:I(0)});
    e('observe',15,`n1 = {${x}, &n2}, c = {${x+1}, &n2}, n2.data = 0. 정수 필드는 따로 바뀌었고, 포인터 필드는 주소만 복사해 n2를 함께 씁니다.`,{label:'결과 확인'});
    return events;
   }
   e('write',8,`a.age에 ${J(x,'을/를')} 씁니다.`,{label:`a.age = ${x}`,cellId:'a.age',value:I(x)});
   e('write',8,`a.height에 ${J(y,'을/를')} 씁니다. b는 초기값 없이 선언만 했습니다.`,{label:`a.height = ${y}`,cellId:'a.height',value:I(y)});
   e('read',9,'b = a는 필드를 하나씩 복사합니다. 먼저 a.age를 읽습니다.',{label:'a.age 읽기',cellId:'a.age'});
   e('write',9,`읽은 ${J(x,'을/를')} b.age에 씁니다.`,{label:`b.age = ${x}`,cellId:'b.age',value:I(x)});
   e('read',9,'다음 필드 a.height를 읽습니다.',{label:'a.height 읽기',cellId:'a.height'});
   e('write',9,`읽은 ${J(y,'을/를')} b.height에 씁니다. 같은 타입이라 필드가 모자라거나 남지 않습니다.`,{label:`b.height = ${y}`,cellId:'b.height',value:I(y)});
   e('read',10,`a.age(${x})${J(x,'을/를').slice(String(x).length)} 읽습니다.`,{label:'a.age 읽기',cellId:'a.age'});
   e('write',10,`a.age에 ${J(x+1,'을/를')} 씁니다. b는 a와 다른 저장 공간이라 b.age는 ${J(x,'으로/로')} 그대로입니다.`,{label:`a.age = ${x+1}`,cellId:'a.age',value:I(x+1)});
   e('read',11,'if( a > b )처럼 구조체 전체는 비교할 수 없어 필드를 고릅니다. a.age를 읽습니다.',{label:'a.age 읽기',cellId:'a.age'});
   e('read',11,`b.age를 읽습니다. ${x+1} > ${J(x,'이/가')} 참입니다.`,{label:'b.age 읽기',cellId:'b.age'});
   e('observe',12,`조건이 참이라 "a가 b보다 나이가 많음"을 출력합니다. a = {${x+1}, ${y}}, b = {${x}, ${y}}.`,{label:'결과 확인'});
   return events;
  },
  expected:[
   {presetId:'default',checks:[{step:'last',cellId:'a.age',value:I(21)},{step:'last',cellId:'b.age',value:I(20)},{step:'last',cellId:'b.height',value:I(170)}]},
   {presetId:'copy',checks:[{step:'last',cellId:'a.age',value:I(21)},{step:'last',cellId:'b.age',value:I(20)},{step:'last',cellId:'b.height',value:I(170)}]},
   {presetId:'same',checks:[{step:'last',cellId:'a.age',value:I(8)},{step:'last',cellId:'b.age',value:I(7)},{step:'last',cellId:'b.height',value:I(7)}]},
   {presetId:'min',checks:[{step:'last',cellId:'a.age',value:I(-998)},{step:'last',cellId:'b.age',value:I(-999)}]},
   {presetId:'max',checks:[{step:'last',cellId:'a.age',value:I(1000)},{step:'last',cellId:'b.age',value:I(999)}]},
   {presetId:'uninit',diagnosticCode:'UNINITIALIZED_READ',checks:[{step:'last',cellId:'b.age',value:U}]},
   {presetId:'link',checks:[{step:'last',cellId:'n1.data',value:I(10)},{step:'last',cellId:'c.data',value:I(11)},{step:'last',cellId:'c.link',value:P('n2.data')},{step:'last',cellId:'n1.link',value:P('n2.data')},{step:'last',cellId:'n2.data',value:I(0)},{step:'last',cellId:'seen',value:I(0)}]}
  ]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
