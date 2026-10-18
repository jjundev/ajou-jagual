(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),U={kind:'uninitialized'};
 const J=(n,p)=>{const a=Math.abs(n),d=a%10,b=a===0||d===0||[1,3,6,7,8].includes(d),l=a!==0&&d!==0&&[1,7,8].includes(d);const [x,y]=p.split('/');return `${n}${p==='으로/로'?(b&&!l?x:y):(b?x:y)}`;};
 const pt=(n,p)=>J(n,p).slice(String(n).length);
 const cell=(id,name,type,owner,address,value)=>({id,name,type,owner,address,value,lifetime:'live'});
 const INT_MAX=2147483647,INT_MIN=-2147483648,DEPTH_GUARD=80;
 const main=`int main(void)\n{\n    int r = factorial({{n}});\n    printf("%d\\n", r);\n    return 0;\n}`;
 const pdf={path:'자료구조_강의록_2026/Software_2_Recursion.pdf',page:6,section:'s0-recursion-rules',sha256:'e686ae970c836fbdd84eb967c22efb44473bb2258c9914715c96b7ff48cf4efe'};
 const sources=[
  {id:'lecture',label:'바닥 조건 있음 · 강의 factorial',language:'c',text:`#include <stdio.h>\nint factorial(int n)\n{\n    if( n <= 1 )  return 1;\n    else return n * factorial(n-1);\n}\n`+main,
   provenance:{...pdf,supplement:false,note:'강의 p6 factorial · 슬라이드에서 빠진 return 1 뒤 ;와 #include, main 호출자는 보충입니다.',adjustments:'p6 factorial 본문 보존. 슬라이드의 `return 1` 뒤에 빠진 세미콜론을 보충(그대로는 컴파일되지 않음). #include, int main(void) 호출자와 printf는 보충.'}},
  {id:'nobase',label:'바닥 조건 없음 · 보충',language:'c',text:`#include <stdio.h>\nint factorial(int n)\n{\n    /* 순환을 멈추는 부분을 지웠다 */\n    return n * factorial(n-1);\n}\n`+main,
   provenance:{...pdf,supplement:true,note:'p6의 질문 “멈추는 부분이 없다면?”을 확인하려고 if 줄을 지운 보충 예제입니다.',adjustments:'강의 factorial에서 순환을 멈추는 if 줄을 지운 비교용 보충. 실제 실행은 스택이 넘칠 때까지 호출하므로 실행하지 않고 호출 깊이 한도에서 멈춘다.'}}
 ];
 const scenario={version:1,id:'factorial-frames',kind:'c-memory',title:'factorial: 호출마다 생기는 n과 돌아오는 값',
  intro:'main이 factorial을 부르기 직전입니다. 호출할 때마다 새 n이 생기고, 바닥에 닿으면 값이 한 칸씩 위로 돌아옵니다.',
  takeaway:'순환 호출마다 별도의 n이 생깁니다. 바닥 조건(n <= 1)에서 1을 바로 돌려주면, 기다리던 호출이 그 값에 자기 n을 곱해 차례로 돌려줍니다. 바닥 조건이 없으면 호출이 끝없이 쌓입니다.',
  sources,
  inputs:[{key:'n',label:'factorial에 넘길 n',type:'integer',default:4,min:-99,max:99},{key:'mode',label:'바닥 조건',type:'enum',default:'lecture',options:[{value:'lecture',label:'바닥 조건 있음 (강의)'},{value:'nobase',label:'바닥 조건 없음 (보충)'}]}],
  presets:[{id:'four',label:'factorial(4)',input:{n:4,mode:'lecture'}},{id:'one',label:'n = 1: 바로 바닥',input:{n:1,mode:'lecture'}},{id:'zero',label:'n = 0',input:{n:0,mode:'lecture'}},{id:'negative',label:'음수 n = -3',input:{n:-3,mode:'lecture'}},{id:'twelve',label:'12!: int 안의 가장 큰 결과',input:{n:12,mode:'lecture'}},{id:'overflow',label:'13!: int 범위를 넘으면?',input:{n:13,mode:'lecture'}},{id:'nobase',label:'바닥 조건이 없다면?',input:{n:4,mode:'nobase'}}],
  initialState(){return {frames:{main:{id:'main',functionId:'main',cellIds:['r'],lifetime:'live',caller:null}},objects:{},cells:{r:cell('r','r','int','main','&r',U)},activeFrame:'main',stdout:[]};},
  *generateEvents({n,mode}){
   const sourceId=mode,base=mode==='lecture',ev=(kind,line,explanation,payload={})=>({kind,at:{sourceId,line},explanation,...payload});
   const ids=[],ns=[];let k=0,cur=n;
   // 내려가기: 각 호출의 n을 만들고 바닥 조건을 검사한다.
   while(true){
    k++;const id=`f${k}`,caller=k===1?'main':`f${k-1}`;ids.push(id);ns.push(cur);
    if(k>DEPTH_GUARD){yield ev('diagnostic',5,'호출 깊이 한도에 도달했습니다.',{label:'한도',code:'LIMIT_REACHED',message:'호출 깊이 한도에 도달했습니다.'});return;}
    if(k===1){
     yield ev('call',9,`main이 factorial(${n})${pt(n,'을/를')} 부릅니다. factorial 호출 하나를 위한 저장 공간을 새로 만듭니다.`,{label:`factorial(${n}) 호출`,frame:{id,functionId:'factorial',cellIds:[],lifetime:'live',callSite:{sourceId,line:9}}});
     yield ev('bind',2,`인자 ${J(n,'을/를')} 이 호출의 매개변수 n에 복사합니다.`,{label:`${n} → n 복사`,cell:cell(`${id}.n`,'n','int',id,`&${id}.n`,I(n)),value:I(n)});
    }else{
     yield ev('read',5,`인자 n-1을 계산하려고 지금 호출의 n(${ns[k-2]})${pt(ns[k-2],'을/를')} 읽습니다.`,{label:'n-1 계산',cellId:`${caller}.n`});
     yield ev('call',5,base&&k===64?`factorial(${cur})${pt(cur,'을/를')} 부르면 main까지 합친 호출이 64개를 넘습니다. 이 화면은 호출 깊이 64까지만 따라갑니다. 실제 C에서는 ${n}개의 호출이 모두 쌓였다가 돌아오면서 13!부터 int 범위를 넘어 정의되지 않은 동작이 됩니다.`:!base&&k===64?`멈추는 부분이 없어 factorial(${cur})${pt(cur,'을/를')} 또 부릅니다. 호출이 이미 63개 쌓였습니다. 실제 프로그램은 스택 공간이 바닥날 때까지 부르다가 비정상 종료(시스템 오류)되고, 이 화면은 호출 깊이 64에서 멈춥니다.`:`factorial(${cur})${pt(cur,'을/를')} 부릅니다. 이름은 같아도 새 호출이라 저장 공간을 하나 더 만듭니다. 부른 쪽 호출은 끝나지 않고 기다립니다.`,{label:`factorial(${cur}) 호출`,frame:{id,functionId:'factorial',cellIds:[],lifetime:'live',callSite:{sourceId,line:5}}});
     yield ev('bind',2,`n-1의 값 ${J(cur,'을/를')} 새 매개변수 n에 복사합니다. 부른 쪽의 n(${ns[k-2]})${pt(ns[k-2],'과/와')}는 다른 변수입니다.`,{label:`${cur} → 새 n 복사`,cell:cell(`${id}.n`,'n','int',id,`&${id}.n`,I(cur)),value:I(cur)});
    }
    yield ev('enter',3,`factorial(${cur}) 본문으로 들어갑니다. 지금 실행 중인 호출은 ${k}번째 factorial입니다.`,{label:'함수 진입',frameId:id});
    if(base){
     yield ev('read',4,cur<=1?`n은 ${cur}이고 n <= 1이 참입니다. 순환을 멈추는 부분입니다.${cur<0?' 수학의 팩토리얼은 음수에 정의되지 않지만, 이 코드는 n <= 1이면 모두 1을 돌려줍니다.':''}`:`n은 ${cur}이고 n <= 1이 거짓입니다. else로 가서 더 작은 문제를 맡깁니다.`,{label:cur<=1?'n <= 1 참':'n <= 1 거짓',cellId:`${id}.n`});
     if(cur<=1)break;
    }
    yield ev('declare',5,`factorial(${cur-1})${pt(cur-1,'이/가')} 돌려줄 값을 받을 자리입니다. C에서는 이름 없는 값이지만, 돌아오는 값을 보려고 화면에만 칸을 그립니다.`,{label:'반환값 받을 자리',cell:cell(`${id}.ret`,`factorial(${cur-1})`,'int',id,'이름 없는 값 · 주소 없음',U)});
    cur=cur-1;
   }
   // 올라가기: 바닥에서 1을 돌려주고, 기다리던 호출이 n을 곱해 돌려준다.
   const target=i=>i===0?'r':`${ids[i-1]}.ret`;
   let i=ids.length-1,value=1;
   yield ev('return',4,`바닥에서는 더 부르지 않고 1을 바로 돌려줍니다. ${i===0?'main의 r':`기다리던 factorial(${ns[i-1]})${pt(ns[i-1],'이/가')}`}${i===0?'이':''} 1을 받고, 이 호출의 n은 수명이 끝납니다.`,{label:'1 반환',frameId:ids[i],result:{cellId:target(i),value:I(1)}});
   for(i=i-1;i>=0;i--){
    const id=ids[i],m=ns[i];
    yield ev('read',5,`돌아온 factorial(${m-1})의 값 ${J(value,'을/를')} 읽습니다.`,{label:'돌아온 값 읽기',cellId:`${id}.ret`});
    yield ev('read',5,`곱할 자기 n(${m})${pt(m,'을/를')} 읽습니다. 곱셈의 두 피연산자를 읽는 순서는 C가 정하지 않지만 결과는 같습니다.`,{label:'자기 n 읽기',cellId:`${id}.n`});
    const product=m*value;
    if(product>INT_MAX||product<INT_MIN){yield ev('diagnostic',5,`${m} × ${value} = ${J(product,'은/는')} int가 32비트일 때(강의 기준) 범위 ${INT_MIN} ~ ${J(INT_MAX,'을/를')} 넘습니다. 부호 있는 정수 오버플로는 정의되지 않은 동작이라 여기서 멈춥니다.`,{label:'int 범위 초과',code:'SIGNED_OVERFLOW',message:`${m} × ${value}는 int 범위를 넘습니다(정의되지 않은 동작).`});return;}
    const prev=value;value=product;
    yield ev('return',5,`${m} × ${prev} = ${J(value,'을/를')} 돌려줍니다. ${i===0?'main의 r':`factorial(${ns[i-1]})${pt(ns[i-1],'이/가')}`}${i===0?'이':''} 이 값을 받고, 이 호출의 저장 공간은 수명이 끝납니다.`,{label:`${value} 반환`,frameId:id,result:{cellId:target(i),value:I(value)}});
   }
   yield ev('read',10,`main으로 돌아왔습니다. r에 담긴 ${J(value,'을/를')} 읽어 출력합니다.`,{label:'r 출력',cellId:'r'});
   yield ev('observe',11,`factorial(${n}) = ${value}. ${ids.length===1?'호출 1개가 바로 바닥에서 끝났습니다.':`호출 ${ids.length}개가 차례로 쌓였다가 거꾸로 하나씩 끝났습니다.`}`,{label:'결과 확인'});
  },
  expected:[
   {presetId:'default',checks:[{step:'last',cellId:'r',value:I(24)}]},
   {presetId:'four',checks:[{step:'last',cellId:'r',value:I(24)}]},
   {presetId:'one',checks:[{step:'last',cellId:'r',value:I(1)}]},
   {presetId:'zero',checks:[{step:'last',cellId:'r',value:I(1)}]},
   {presetId:'negative',checks:[{step:'last',cellId:'r',value:I(1)}]},
   {presetId:'twelve',checks:[{step:'last',cellId:'r',value:I(479001600)}]},
   {presetId:'overflow',diagnosticCode:'SIGNED_OVERFLOW',checks:[{step:'last',cellId:'r',value:U}]},
   {presetId:'nobase',diagnosticCode:'LIMIT_REACHED',checks:[{step:'last',cellId:'r',value:U}]}
  ]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
