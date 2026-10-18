const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),p=require('node:path'),crypto=require('node:crypto');
const tmp=()=>fs.mkdtempSync(p.join(os.tmpdir(),'ds delivery 한글 '));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
function runFixture(base){const run=p.join(base,'run');fs.mkdirSync(p.join(run,'evidence'),{recursive:true});for(const [name,text]of Object.entries({'scenario.cjs':'module.exports={id:"x"}','trace.json':'{}','source.json':'[]','brief.md':'reviewed','preview.html':'<!doctype html>reviewed bytes'}))fs.writeFileSync(p.join(run,name),text);fs.writeFileSync(p.join(run,'evidence/pass.md'),'actual evidence');const {createReview}=require('../scripts/review.cjs'),r=createReview(run);for(const v of Object.values(r.checks))Object.assign(v,{status:'pass',evidence:'evidence/pass.md',notes:'manually observed fixture'});fs.writeFileSync(p.join(run,'review.json'),JSON.stringify(r));return run;}
test('save requires real completed reviews, current hashes and exclusive numbering',()=>{
 const dir=tmp();try{const {save}=require('../scripts/save.cjs'),{verifyReview}=require('../scripts/review.cjs'),run=runFixture(dir),dest=p.join(dir,'0928');fs.mkdirSync(dest);fs.writeFileSync(p.join(dest,'인터렉티브_01_existing.html'),'keep');fs.mkdirSync(p.join(dest,'.pack','자료_인터렉티브_02_reserved'),{recursive:true});const result=save({run,dest,name:'값과 주소'});a.equal(result.nn,3);a.equal(fs.readFileSync(result.html,'utf8'),'<!doctype html>reviewed bytes');a.deepEqual(verifyReview(result.dir),[]);
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
  const own=save({run,dest,name:'A'});a.notEqual(own.nn,other.nn);a.deepEqual([own.nn,other.nn].sort(),[1,2]);a.equal(fs.readFileSync(own.html,'utf8'),'<!doctype html>reviewed bytes');a.equal(fs.readFileSync(other.html,'utf8'),'<!doctype html>reviewed bytes');
 }finally{fs.mkdirSync=real;fs.rmSync(dir,{recursive:true,force:true});}
});
