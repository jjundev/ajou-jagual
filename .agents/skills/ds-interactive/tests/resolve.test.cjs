const {test}=require('node:test');
const a=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),p=require('node:path');
test('resolve actual course and keep .pack authoring note',()=>{
 const {resolveTarget}=require('../scripts/resolve.cjs');const t=resolveTarget({repo:process.cwd(),arg:'0928'});
 a.equal(t.date,'0928');a.match(t.noteHtml,/ArrayStructureList.html$/);a.ok(t.notes.some(x=>x.includes('.pack')));
});
test('missing explicit file, ambiguous range, topic fallback and Unicode paths',()=>{
 const {resolveTarget}=require('../scripts/resolve.cjs');const repo=fs.mkdtempSync(p.join(os.tmpdir(),'ds-한글 é '));
 try {for(const d of ['0928','0928-1001'])fs.mkdirSync(p.join(repo,'복습노트',d),{recursive:true});
 a.throws(()=>resolveTarget({repo,arg:'0928'}),{code:'AMBIGUOUS_TARGET'});
 a.throws(()=>resolveTarget({repo,arg:'missing.c'}),{code:'SOURCE_MISSING'});
 a.equal(resolveTarget({repo,arg:'트리'}).kind,'topic');
 fs.writeFileSync(p.join(repo,'코 드.c'),'int a;');a.equal(resolveTarget({repo,arg:'코 드.c'}).kind,'code');
 }finally{fs.rmSync(repo,{recursive:true,force:true});}
});
test('input rejects nonintegers, missing fields, invalid enum and out of range',()=>{
 const {validateInput}=require('../assets/engine/contract.js');const defs=[{key:'a',type:'integer',min:-99,max:99},{key:'mode',type:'enum',options:[{value:'x'}]}];
 for(const n of [-99,99])a.deepEqual(validateInput(defs,{a:n,mode:'x'}),[]);
 for(const n of [-100,100,NaN,'',1.5,undefined])a.ok(validateInput(defs,{a:n,mode:'x'}).length);
 a.ok(validateInput(defs,{a:1,mode:'wrong'}).length);
});
test('NFD Korean note names are classified while their actual paths are preserved',()=>{
 const {resolveTarget}=require('../scripts/resolve.cjs'),repo=fs.mkdtempSync(p.join(os.tmpdir(),'ds-nfd-'));
 try{const folder=p.join(repo,'복습노트','0928');fs.mkdirSync(p.join(folder,'.pack'),{recursive:true});const base='정리노트_0928_포인터'.normalize('NFD'),html=p.join(folder,base+'.html'),md=p.join(folder,'.pack',base+'.md');fs.writeFileSync(html,'note');fs.writeFileSync(md,'note');fs.writeFileSync(p.join(folder,base+'.md'),'root duplicate');const t=resolveTarget({repo,arg:'0928'});a.equal(t.noteHtml,html);a.deepEqual(t.notes.sort(),[html,md].sort());}finally{fs.rmSync(repo,{force:true,recursive:true});}
});
