(function(root){
 'use strict';
 const I=value=>({kind:'int',value}),U={kind:'uninitialized'};
 const J=(n,p)=>{const a=Math.abs(n),d=a%10,b=a===0||d===0||[1,3,6,7,8].includes(d),l=a!==0&&d!==0&&[1,7,8].includes(d);const [x,y]=p.split('/');return `${n}${p==='으로/로'?(b&&!l?x:y):(b?x:y)}`;};
 const pt=(n,p)=>J(n,p).slice(String(n).length);
 const cell=(id,name,type,owner,address,value)=>({id,name,type,owner,address,value,lifetime:'live'});
 const MAX=6;
 const CASES={
  note:{label:'5차 + 3차',A:[5,[10,0,0,0,6,3]],B:[3,[10,3,0,'k']]},
  same:{label:'3차 + 3차',A:[3,[8,0,7,1]],B:[3,[10,3,0,'k']]},
  bigb:{label:'1차 + 3차',A:[1,[6,3]],B:[3,[10,3,0,'k']]},
  cancel:{label:'최고차 상쇄',A:[2,[3,0,1]],B:[2,[-3,5,'k']]},
  constant:{label:'상수항만',A:[0,[7]],B:[0,['k']]}
 };
 const term=(c,e)=>e===0?String(c):`${c===1?'':c===-1?'-':c}x${e===1?'':['','','²','³','⁴','⁵'][e]}`;
 const show=([d,cs])=>cs.map((c,i)=>[c,d-i]).filter(([c])=>c!==0).map(([c,e],i)=>(i&&c>0?'+':'')+term(c,e)).join('')||'0';
 const init=([d,cs])=>`{ ${d}, {${cs.map(x=>x==='k'?'{{k}}':x).join(', ')}} }`;
 const withK=([d,cs],k)=>[d,cs.map(x=>x==='k'?k:x)];
 const body=`    polynomial C;\n    int Apos=0, Bpos=0, Cpos=0;\n    int degree_a=A.degree, degree_b=B.degree;\n    C.degree = (A.degree > B.degree) ? A.degree : B.degree;\n    while( Apos<=A.degree && Bpos<=B.degree ){\n        if( degree_a > degree_b ){ // A항 > B항\n            C.coef[Cpos++]= A.coef[Apos++];\n            degree_a--;\n        }\n        else if( degree_a == degree_b ){ // A항 == B항\n            C.coef[Cpos++]=A.coef[Apos++]+B.coef[Bpos++];\n            degree_a--; degree_b--;\n        }\n        else {                 // B항 > A항\n            C.coef[Cpos++]= B.coef[Bpos++];\n            degree_b--;\n        }\n    }\n    /* 후처리: 남은 항을 C 끝으로 (보충) */\n    while( Apos<=A.degree )\n        C.coef[Cpos++]= A.coef[Apos++];\n    while( Bpos<=B.degree )\n        C.coef[Cpos++]= B.coef[Bpos++];\n    return 0;\n}`;
 const head=`#include <stdio.h>\n#define MAX_DEGREE ${MAX}\ntypedef struct {\n    int degree;\n    int coef[MAX_DEGREE];   /* 강의는 float */\n} polynomial;\nint main(void)\n{\n`;
 const sources=Object.entries(CASES).map(([id,c])=>({id,label:c.label,language:'c',
  text:head+`    polynomial A = ${init(c.A)};\n    polynomial B = ${init(c.B)};\n`+body,
  provenance:{path:'자료구조_강의록_2026/Software_3_ArrayStructureList.pdf',page:8,section:'s2-poly-add1',sha256:'765ff7fae303bdcf83aa116cf8171482d083641617c24314304ca01f6953917a',supplement:id!=='note'&&id!=='same',
   note:'강의 p8 while 루프 원문 · p7 구조체(coef는 float→int), 선언·초기값(B의 상수항 k)·C.degree·후처리는 보충입니다.',
   adjustments:'p8 프로그램 3.2 while 루프 본문 보존. p7 polynomial 구조체의 float coef를 정수 예제에 맞춰 int로, MAX_DEGREE를 6으로 단순화. main, 변수 선언, C.degree 계산, 후처리 while 두 개(정리노트 보충)는 보충.'}}));
 const L={decl:12,deg:13,cdeg:14,loop:15,gt:16,gtBody:17,gtDec:18,eq:20,eqBody:21,eqDec:22,ltBody:25,ltDec:26,postA:30,postABody:31,postB:32,postBBody:33,ret:34};
 const scenario={version:1,id:'poly-add-index',kind:'c-memory',title:'다항식 덧셈: 세 위치 Apos·Bpos·Cpos',
  intro:'9–11줄까지 실행해 A, B를 초기화하고 C를 선언한 상태입니다. 초기값 목록이 짧으면 나머지 coef 칸은 0으로 채워집니다. C는 아직 아무 값도 없습니다.',
  takeaway:'방법 #1은 계수를 차수 순서대로 모두 저장하므로, 두 차수 카운터를 비교해 큰 쪽 계수를 C에 옮기거나 같으면 더하면 됩니다. 두 카운터가 같아진 뒤에는 함께 줄어 두 다항식이 상수항에서 같이 끝나므로, 후처리 while은 한 번도 돌지 않습니다.',
  sources,
  inputs:[{key:'case',label:'더할 두 다항식',type:'enum',default:'note',options:Object.entries(CASES).map(([value,c])=>({value,label:c.label}))},{key:'k',label:'B의 상수항 k',type:'integer',default:1,min:-99,max:99}],
  presets:[{id:'note',label:'정리노트 예: 차수 5와 3',input:{case:'note',k:1}},{id:'same',label:'정리노트 예: 최고 차수가 같을 때',input:{case:'same',k:1}},{id:'bigb',label:'B의 차수가 더 클 때',input:{case:'bigb',k:1}},{id:'cancel',label:'최고차항이 지워질 때',input:{case:'cancel',k:1}},{id:'zero-const',label:'상수항 합이 0일 때 (k = -3)',input:{case:'note',k:-3}},{id:'constant',label:'상수항만 있을 때 (차수 0)',input:{case:'constant',k:-2}},{id:'boundary',label:'경계 k = 99',input:{case:'constant',k:99}}],
  initialState({case:id,k}){
   const c={A:CASES[id].A,B:withK(CASES[id].B,k)},cells={},objects={},frameCells=[];
   const poly=(name,val)=>{const ids=[`${name}.degree`,...[...Array(MAX).keys()].map(i=>`${name}.coef[${i}]`)];objects[`main.${name}`]={id:`main.${name}`,type:'polynomial',storage:'automatic',cellIds:ids,lifetime:'live'};
    ids.forEach((id,i)=>{cells[id]=cell(id,id,'int',`main.${name}`,i?`&${id}`:`&${id} (= &${name})`,!val?U:i===0?I(val[0]):I(val[1][i-1]??0));frameCells.push(id);});};
   poly('A',c.A);poly('B',c.B);poly('C',null);
   for(const v of ['Apos','Bpos','Cpos','degree_a','degree_b']){cells[v]=cell(v,v,'int','main',`&${v}`,U);frameCells.push(v);}
   return {frames:{main:{id:'main',functionId:'main',cellIds:frameCells,lifetime:'live',caller:null}},objects,cells,activeFrame:'main',stdout:[]};
  },
  generateEvents({case:id,k}){
   const c={A:CASES[id].A,B:withK(CASES[id].B,k)},sourceId=id,events=[],e=(kind,line,explanation,payload={})=>events.push({kind,at:{sourceId,line},explanation,...payload});
   const v={Adeg:c.A[0],Bdeg:c.B[0],A:[...Array(MAX).keys()].map(i=>c.A[1][i]??0),B:[...Array(MAX).keys()].map(i=>c.B[1][i]??0),C:[],Apos:0,Bpos:0,Cpos:0,da:0,db:0};
   const rd=(line,id,label,text)=>e('read',line,text,{label,cellId:id});
   const wr=(line,id,val,label,text)=>e('write',line,text,{label,cellId:id,value:I(val)});
   // 12–14줄: 위치와 차수 카운터 준비
   wr(L.decl,'Apos',0,'Apos = 0','A에서 다음에 읽을 계수의 인덱스 Apos를 0으로 시작합니다.');
   wr(L.decl,'Bpos',0,'Bpos = 0','B에서 다음에 읽을 계수의 인덱스 Bpos를 0으로 시작합니다.');
   wr(L.decl,'Cpos',0,'Cpos = 0','C에 다음으로 쓸 인덱스 Cpos를 0으로 시작합니다.');
   rd(L.deg,'A.degree','A.degree 읽기',`A의 최고 차수 ${J(v.Adeg,'을/를')} 읽습니다.`);
   wr(L.deg,'degree_a',v.Adeg,`degree_a = ${v.Adeg}`,'A.degree를 degree_a에 복사합니다. degree_a는 지금 Apos 자리 계수의 차수입니다.');v.da=v.Adeg;
   rd(L.deg,'B.degree','B.degree 읽기',`B의 최고 차수 ${J(v.Bdeg,'을/를')} 읽습니다.`);
   wr(L.deg,'degree_b',v.Bdeg,`degree_b = ${v.Bdeg}`,'B.degree를 degree_b에 복사합니다. 복사본만 줄여 가므로 A.degree, B.degree는 그대로 남습니다.');v.db=v.Bdeg;
   rd(L.cdeg,'A.degree','A.degree 읽기','결과 차수를 정하려고 A.degree를 읽습니다.');
   rd(L.cdeg,'B.degree','B.degree 읽기',`B.degree도 읽어 비교합니다. ${v.Adeg} > ${v.Bdeg}${pt(v.Bdeg,'이/가')}${v.Adeg>v.Bdeg?' 참이므로 A.degree를 고릅니다.':' 거짓이므로 B.degree를 고릅니다.'}`);
   const cd=Math.max(v.Adeg,v.Bdeg);rd(L.cdeg,v.Adeg>v.Bdeg?'A.degree':'B.degree','고른 차수 읽기',`고른 쪽의 차수 ${J(cd,'을/를')} 다시 읽습니다.`);
   wr(L.cdeg,'C.degree',cd,`C.degree = ${cd}`,`C의 최고 차수는 두 차수 중 큰 값 ${cd}입니다.`);
   const cond=(which)=>{
    const pos=which==='A'?'Apos':'Bpos',p=v[pos],d=which==='A'?v.Adeg:v.Bdeg;
    rd(L.loop,pos,`${pos} 읽기`,`조건 ${pos}<=${which}.degree를 계산하려고 ${pos}(${p})${pt(p,'을/를')} 읽습니다.`);
    rd(L.loop,`${which}.degree`,`${which}.degree 읽기`,`${p} <= ${d}${pt(d,'이/가')}${p<=d?' 참입니다.':` 거짓입니다. ${which}의 계수를 모두 썼습니다.`}`);return p<=d;
   };
   let iter=0;
   while(true){
    const okA=cond('A');
    if(!okA){e('observe',L.loop,'&&의 왼쪽이 거짓이므로 오른쪽 Bpos<=B.degree는 계산하지 않고 while을 빠져나옵니다.',{label:'while 종료'});break;}
    const okB=cond('B');
    if(!okB){e('observe',L.loop,'두 조건 중 하나가 거짓이므로 while을 빠져나옵니다.',{label:'while 종료'});break;}
    iter++;
    rd(L.gt,'degree_a','degree_a 읽기',`${iter}번째 반복입니다. A의 현재 항 차수 degree_a(${v.da})${pt(v.da,'을/를')} 읽습니다.`);
    rd(L.gt,'degree_b','degree_b 읽기',`B의 현재 항 차수 degree_b(${v.db})${pt(v.db,'을/를')} 읽습니다. ${v.da} > ${v.db}${pt(v.db,'이/가')}${v.da>v.db?' 참입니다.':' 거짓입니다.'}`);
    const sym=v.da>v.db?'gt':v.da===v.db?'eq':'lt';
    if(sym!=='gt'){
     rd(L.eq,'degree_a','degree_a 읽기','else if로 넘어와 degree_a를 다시 읽습니다.');
     rd(L.eq,'degree_b','degree_b 읽기',`${v.da} == ${v.db}${pt(v.db,'이/가')}${sym==='eq'?' 참입니다. 같은 차수끼리 더합니다.':' 거짓입니다. else로 가서 B의 항을 옮깁니다.'}`);
    }
    const line=sym==='gt'?L.gtBody:sym==='eq'?L.eqBody:L.ltBody,cp=v.Cpos;
    rd(line,'Cpos','Cpos 읽기',`Cpos++는 증가 전 값 ${J(cp,'을/를')} 내놓으므로 C.coef[${cp}]에 씁니다.`);
    let val,parts=[];
    if(sym!=='lt'){const ap=v.Apos;rd(line,'Apos','Apos 읽기',`Apos++도 증가 전 값 ${J(ap,'을/를')} 내놓으므로 A.coef[${ap}]${pt(ap,'을/를')} 읽습니다.`);rd(line,`A.coef[${ap}]`,`A.coef[${ap}] 읽기`,`A.coef[${ap}] = ${v.A[ap]} (차수 ${v.da})`);parts.push(v.A[ap]);}
    if(sym!=='gt'){const bp=v.Bpos;rd(line,'Bpos','Bpos 읽기',`Bpos++${sym==='eq'?'도':'는'} 증가 전 값 ${J(bp,'을/를')} 내놓으므로 B.coef[${bp}]${pt(bp,'을/를')} 읽습니다.`);rd(line,`B.coef[${bp}]`,`B.coef[${bp}] 읽기`,`B.coef[${bp}] = ${v.B[bp]} (차수 ${v.db})`);parts.push(v.B[bp]);}
    val=parts.reduce((a,b)=>a+b,0);v.C[cp]=val;
    wr(line,`C.coef[${cp}]`,val,`C.coef[${cp}] = ${val}`,sym==='eq'?`${parts[0]} + ${parts[1]<0?`(${parts[1]})`:parts[1]} = ${J(val,'을/를')} C.coef[${cp}]에 씁니다.${val===0?' 합이 0이어도 방법 #1은 자리를 그대로 차지합니다.':''}`:`${sym==='gt'?'A':'B'}의 계수 ${J(val,'을/를')} 그대로 C.coef[${cp}]에 복사합니다.`);
    const inc=(id,old)=>wr(line,id,old+1,`${id} = ${old+1}`,`같은 문장 안의 ${id}++가 ${id}를 ${J(old+1,'으로/로')} 올립니다. 이 증가와 배열 쓰기의 상대 순서는 C가 정하지 않지만, 쓰는 자리는 증가 전 값 ${old}입니다.`);
    inc('Cpos',v.Cpos);v.Cpos++;
    if(sym!=='lt'){inc('Apos',v.Apos);v.Apos++;}
    if(sym!=='gt'){inc('Bpos',v.Bpos);v.Bpos++;}
    const dec=(id,key)=>{const dl=sym==='gt'?L.gtDec:sym==='eq'?L.eqDec:L.ltDec;rd(dl,id,`${id} 읽기`,`${id}(${v[key]})${pt(v[key],'을/를')} 읽습니다.`);wr(dl,id,v[key]-1,`${id} = ${v[key]-1}`,v[key]-1<0?`${id}--로 ${J(v[key]-1,'이/가')} 됩니다. 상수항까지 다 처리해 더 내려갈 차수가 없습니다.`:`${id}--로 다음 항의 차수 ${J(v[key]-1,'으로/로')} 내려갑니다.`);v[key]--;};
    if(sym!=='lt')dec('degree_a','da');
    if(sym!=='gt')dec('degree_b','db');
   }
   const post=(which,line,bodyLine)=>{
    const pos=which==='A'?'Apos':'Bpos',d=which==='A'?v.Adeg:v.Bdeg;
    while(true){
     rd(line,pos,`${pos} 읽기`,`후처리: ${which}에 남은 항이 있는지 ${pos}(${v[pos]})${pt(v[pos],'을/를')} 읽습니다.`);
     const ok=v[pos]<=d;rd(line,`${which}.degree`,`${which}.degree 읽기`,`${v[pos]} <= ${d}${pt(d,'이/가')}${ok?` 참입니다. ${which}의 남은 계수를 C 끝에 옮깁니다.`:` 거짓입니다. ${which}에 남은 항이 없어 이 while은 한 번도 돌지 않습니다.`}`);
     if(!ok)break;
     const cp=v.Cpos,p=v[pos];rd(bodyLine,'Cpos','Cpos 읽기',`C.coef[${cp}]에 씁니다.`);rd(bodyLine,pos,`${pos} 읽기`,`${which}.coef[${p}]${pt(p,'을/를')} 읽습니다.`);rd(bodyLine,`${which}.coef[${p}]`,`${which}.coef[${p}] 읽기`,`${which}.coef[${p}] = ${v[which][p]}`);
     v.C[cp]=v[which][p];wr(bodyLine,`C.coef[${cp}]`,v[which][p],`C.coef[${cp}] = ${v[which][p]}`,'남은 계수를 C 끝에 복사합니다.');
     wr(bodyLine,'Cpos',cp+1,`Cpos = ${cp+1}`,'Cpos를 하나 올립니다.');v.Cpos++;wr(bodyLine,pos,p+1,`${pos} = ${p+1}`,`${pos}를 하나 올립니다.`);v[pos]++;
    }
   };
   post('A',L.postA,L.postABody);post('B',L.postB,L.postBBody);
   const coefs=v.C.slice(0,cd+1);
   e('observe',L.ret,`C = { ${cd}, {${coefs.join(', ')}} } → ${show([cd,coefs])}.${coefs[0]===0?` C.degree는 ${cd}이지만 최고차 계수가 0입니다. 방법 #1은 0인 계수도 자리를 차지하고, 이 코드는 차수를 줄이지 않습니다.`:''} 반복 ${iter}번, Apos=${v.Apos}, Bpos=${v.Bpos}, Cpos=${v.Cpos}.`,{label:'결과 확인'});
   return events;
  },
  expected:[
   {presetId:'default',checks:[{step:'last',cellId:'C.degree',value:I(5)},...[10,0,10,3,6,4].map((x,i)=>({step:'last',cellId:`C.coef[${i}]`,value:I(x)}))]},
   {presetId:'note',checks:[...[10,0,10,3,6,4].map((x,i)=>({step:'last',cellId:`C.coef[${i}]`,value:I(x)})),{step:'last',cellId:'Cpos',value:I(6)}]},
   {presetId:'same',checks:[{step:'last',cellId:'C.degree',value:I(3)},...[18,3,7,2].map((x,i)=>({step:'last',cellId:`C.coef[${i}]`,value:I(x)})),{step:'last',cellId:'C.coef[4]',value:U}]},
   {presetId:'bigb',checks:[{step:'last',cellId:'C.degree',value:I(3)},...[10,3,6,4].map((x,i)=>({step:'last',cellId:`C.coef[${i}]`,value:I(x)}))]},
   {presetId:'cancel',checks:[{step:'last',cellId:'C.degree',value:I(2)},...[0,5,2].map((x,i)=>({step:'last',cellId:`C.coef[${i}]`,value:I(x)}))]},
   {presetId:'zero-const',checks:[...[10,0,10,3,6,0].map((x,i)=>({step:'last',cellId:`C.coef[${i}]`,value:I(x)}))]},
   {presetId:'boundary',checks:[{step:'last',cellId:'C.coef[0]',value:I(106)}]},
   {presetId:'constant',checks:[{step:'last',cellId:'C.degree',value:I(0)},{step:'last',cellId:'C.coef[0]',value:I(5)},{step:'last',cellId:'Apos',value:I(1)},{step:'last',cellId:'Bpos',value:I(1)}]}
  ]};
 if(typeof module!=='undefined'&&module.exports)module.exports=scenario;else root.DSInteractive.scenario=scenario;
})(globalThis);
