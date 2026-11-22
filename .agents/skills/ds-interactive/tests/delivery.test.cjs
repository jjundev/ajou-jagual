const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),p=require('node:path'),crypto=require('node:crypto');
const tmp=()=>fs.mkdtempSync(p.join(os.tmpdir(),'ds delivery 한글 '));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
function approve(run, browserEvidence='evidence/pass.md'){
 const {createReview}=require('../scripts/review.cjs'),review=createReview(run);
 for(const v of Object.values(review.checks))Object.assign(v,{status:'pass',evidence:'evidence/pass.md',notes:'manually observed fixture'});
 review.checks.browser.evidence=browserEvidence;
 fs.writeFileSync(p.join(run,'review.json'),JSON.stringify(review));
}
function runFixture(base, example='../examples/0928/value-address.cjs'){
 const run=p.join(base,'run'), scenario=require.resolve(example), {buildPage}=require('../scripts/build.cjs');
 fs.mkdirSync(p.join(run,'evidence'),{recursive:true});
 const sourceText=fs.readFileSync(scenario,'utf8');
 const {html,traces}=buildPage({scenario:{definition:require(scenario),sourceText},outDir:run});
 for(const [name,text] of Object.entries({'scenario.cjs':sourceText,'trace.json':JSON.stringify(traces),'source.json':'[]','brief.md':'reviewed','preview.html':html,'evidence/pass.md':'actual evidence'}))fs.writeFileSync(p.join(run,name),text);
 approve(run);
 return run;
}
test('publication rejects a reviewed preview from a different scenario build', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir),dest=p.join(dir,'notes');
 fs.appendFileSync(p.join(run,'scenario.cjs'),'\n// edited after building HTML\n');
 approve(run);
 const {save}=require('../scripts/save.cjs');
 a.throws(()=>save({run,dest,name:'stale'}),/REBUILD_MISMATCH/);
 a.equal(fs.existsSync(dest),false);
});
test('save rolls back when the approved scenario changes during the copy', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir),dest=p.join(dir,'notes'),{save}=require('../scripts/save.cjs');
 const mkdir=fs.mkdirSync;
 let edited=false;
 fs.mkdirSync=function(file,...args){
  if(!edited&&String(file).endsWith('자료_인터렉티브_01_stale')){
   edited=true;
   fs.appendFileSync(p.join(run,'scenario.cjs'),'\n// edited during save\n');
   approve(run);
  }
  return mkdir.call(fs,file,...args);
 };
 try{
  a.throws(()=>save({run,dest,name:'stale'}),/REBUILD_MISMATCH/);
  a.equal(edited,true);
  a.deepEqual(fs.readdirSync(dest),['.pack']);
  a.deepEqual(fs.readdirSync(p.join(dest,'.pack')),[]);
 }finally{fs.mkdirSync=mkdir;}
});
test('published HTML is checked against a fresh build in its own directory', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir),{save}=require('../scripts/save.cjs');
 const published=save({run,dest:p.join(dir,'notes'),name:'verified'});
 const {checkPublished}=require('../scripts/verify-build.cjs');
 a.doesNotThrow(()=>checkPublished(published.dir,published.html));
 fs.appendFileSync(published.html,'<!-- changed public HTML -->');
 a.throws(()=>checkPublished(published.dir,published.html),/REBUILD_MISMATCH/);
});
test('recursive publication requires current-node browser results for the reviewed HTML', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir,'../examples/1105/inorder.cjs'),dest=p.join(dir,'notes');
 const {save}=require('../scripts/save.cjs');
 a.throws(()=>save({run,dest,name:'unchecked'}),/CURRENT_NODE_UNVERIFIED/);
 const file='evidence/browser.json';
 const sha256=hash(fs.readFileSync(p.join(run,'preview.html')));
 const traces=JSON.parse(fs.readFileSync(p.join(run,'trace.json')));
 const checkpoints=Object.values(traces).reduce((total,t)=>total+t.lineSteps.length,0);
 const results=[[1440,900],[1024,768],[375,812]].flatMap(viewport=>['light','dark'].map(theme=>({
  viewport,theme,sha256,status:'pass',current_node_checked:checkpoints,
 })));
 const writeReport=()=>{fs.writeFileSync(p.join(run,file),JSON.stringify({status:'pass',results}));approve(run,file);};
 results[0].current_node_checked=0;
 writeReport();
 a.throws(()=>save({run,dest,name:'missing'}),/CURRENT_NODE_UNVERIFIED/);
 results[0].current_node_checked=checkpoints;
 results[0].sha256='stale';
 writeReport();
 a.throws(()=>save({run,dest,name:'wrong-build'}),/CURRENT_NODE_UNVERIFIED/);
 results[0].sha256=sha256;
 writeReport();
 const published=save({run,dest,name:'complete'});
 const {checkPublished}=require('../scripts/verify-build.cjs');
 a.doesNotThrow(()=>checkPublished(published.dir,published.html));
});
test('save requires real completed reviews, current hashes and exclusive numbering',()=>{
 const dir=tmp();try{const {save}=require('../scripts/save.cjs'),{verifyReview}=require('../scripts/review.cjs'),run=runFixture(dir),dest=p.join(dir,'0928');fs.mkdirSync(dest);fs.writeFileSync(p.join(dest,'인터렉티브_01_existing.html'),'keep');fs.mkdirSync(p.join(dest,'.pack','자료_인터렉티브_02_reserved'),{recursive:true});const result=save({run,dest,name:'값과 주소'});a.equal(result.nn,3);a.match(fs.readFileSync(result.html,'utf8'),/data-ds-interactive-font/);a.deepEqual(verifyReview(result.dir),[]);
  fs.appendFileSync(p.join(run,'scenario.cjs'),'changed');a.throws(()=>save({run,dest,name:'x'}),/HASH/);a.equal(fs.readFileSync(p.join(dest,'인터렉티브_01_existing.html'),'utf8'),'keep');
  a.throws(()=>save({run,dest,name:'../escape'}),/NAME/);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('not_run, fail, disputed, missing evidence and outside evidence block save',()=>{
 const dir=tmp();try{const run=runFixture(dir),{save}=require('../scripts/save.cjs');const r=JSON.parse(fs.readFileSync(p.join(run,'review.json')));for(const status of ['not_run','fail','disputed']){r.checks.content.status=status;fs.writeFileSync(p.join(run,'review.json'),JSON.stringify(r));a.throws(()=>save({run,dest:p.join(dir,'out'),name:'x'}),/REVIEW/);}r.checks.content.status='pass';for(const evidence of ['missing','../outside.md']){r.checks.content.evidence=evidence;fs.writeFileSync(p.join(run,'review.json'),JSON.stringify(r));a.throws(()=>save({run,dest:p.join(dir,'out'),name:'x'}),/EVIDENCE/);}
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('contextual links are encoded, same-tab, section-local, idempotent and backed up',()=>{
 const dir=tmp();try{const {linkNotes}=require('../scripts/link-notes.cjs'),note=p.join(dir,'정리 노트.html'),html=p.join(dir,'자료 한글.html');fs.writeFileSync(html,'page');const original='<!-- <article id="x">fake</article> --><script>"<article id=\"x\">"</script><article id="x"><div class="layer formal"><p>original</p></div></article><article id="y"><p>keep</p></article>';
 fs.writeFileSync(note,original);const links=[{sectionId:'x',html,label:'확인',before:'주소를 ',after:' 보세요.'},{sectionId:'y',html,label:'한번 더',before:'값을 ',after:' 확인.'}];
 a.equal(linkNotes({note,links,dryRun:true}).changed,true);a.equal(fs.readFileSync(note,'utf8'),original);
 const r=linkNotes({note,links,backupDir:p.join(dir,'backup')});a.equal(r.changed,true);const text=fs.readFileSync(note,'utf8');a.ok(text.includes('target="_self"'));a.ok(text.includes(encodeURIComponent('자료 한글.html')));a.equal((text.match(/data-ds-interactive/g)||[]).length,2);a.equal(linkNotes({note,links}).changed,false);a.equal(fs.readFileSync(r.backup,'utf8'),original);
 fs.writeFileSync(note,'<article id="x"></article><article id="x"></article>');a.equal(linkNotes({note,links:[links[0]]}).results[0].status,'skipped');
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('numbering beyond 99 and relative relink after folder relocation',()=>{
 const dir=tmp();try{const {save}=require('../scripts/save.cjs'),{relink}=require('../scripts/relink.cjs'),run=runFixture(dir),dest=p.join(dir,'course');fs.mkdirSync(dest);fs.writeFileSync(p.join(dest,'인터렉티브_99_old.html'),'old');fs.writeFileSync(p.join(run,'note-links.json'),JSON.stringify({notes:[{note:'../../정리.html',links:[{sectionId:'x',html:'../../$HTML',label:'열기',before:'관찰 ',after:'.'}]}]}));const r=save({run,dest,name:'백'});a.equal(r.nn,100);fs.writeFileSync(p.join(dest,'정리.html'),'<article id="x"><p>원본</p></article>');const relocated=p.join(dir,'moved');fs.renameSync(dest,relocated);const report=relink({repo:dir,target:relocated});a.equal(report.changed,true);a.equal(relink({repo:dir,target:relocated}).changed,false);
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
test('interleaved saves with different names reserve distinct numbers',()=>{
 const dir=tmp();const real=fs.mkdirSync;try{const run=runFixture(dir),{save}=require('../scripts/save.cjs'),dest=p.join(dir,'out');let other,interleaved=false;
  fs.mkdirSync=function(file,...args){if(!interleaved&&/자료_인터렉티브_\d+_A$/.test(String(file))){interleaved=true;other=save({run,dest,name:'B'});}return real.call(fs,file,...args);};
  const own=save({run,dest,name:'A'});a.notEqual(own.nn,other.nn);a.deepEqual([own.nn,other.nn].sort(),[1,2]);a.equal(fs.readFileSync(own.html,'utf8'),fs.readFileSync(other.html,'utf8'));
 }finally{fs.mkdirSync=real;fs.rmSync(dir,{recursive:true,force:true});}
});
