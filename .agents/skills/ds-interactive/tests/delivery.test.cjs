const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),p=require('node:path'),crypto=require('node:crypto');
const tmp=()=>fs.mkdtempSync(p.join(os.tmpdir(),'ds delivery 한글 '));
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const {fixtureReport,fixtureThemeReport}=require('./fixtures/study-report.cjs');
const studyReport='evidence/study.json';
function approve(run, browserEvidence=studyReport){
 const {createReview}=require('../scripts/review.cjs'),review=createReview(run);
 const version=fs.readFileSync(p.join(run,'preview.html'),'utf8').match(/data-ui-version="(\d+)"/);
 if(version) review.ui_version=Number(version[1]);
 else { delete review.ui_version; delete review.theme_version; }
 for(const v of Object.values(review.checks))Object.assign(v,{status:'pass',evidence:'evidence/pass.md',notes:'manually observed fixture'});
 review.checks.browser.evidence=browserEvidence;
 fs.writeFileSync(p.join(run,'review.json'),JSON.stringify(review));
}
function runFixture(base, example='../examples/0928/value-address.cjs', transform=source=>source,uiVersion=require('../scripts/build.cjs').CURRENT_UI_VERSION){
 const run=p.join(base,'run'), scenario=require.resolve(example), {buildPage}=require('../scripts/build.cjs');
 fs.mkdirSync(p.join(run,'evidence'),{recursive:true});
 const sourceText=transform(fs.readFileSync(scenario,'utf8'));
 const {html,traces}=buildPage({scenario:{sourceText},outDir:run,uiVersion,themeVersion:uiVersion ? 1 : 0});
 for(const [name,text] of Object.entries({'scenario.cjs':sourceText,'trace.json':JSON.stringify(traces),'source.json':'[]','brief.md':'reviewed','preview.html':html,'evidence/pass.md':'actual evidence'}))fs.writeFileSync(p.join(run,name),text);
 if(uiVersion) {
  fs.writeFileSync(p.join(run,studyReport),JSON.stringify(fixtureReport(run)));
  fs.writeFileSync(p.join(run,'evidence/theme.json'),JSON.stringify(fixtureThemeReport(html)));
 }
 approve(run,uiVersion?studyReport:'evidence/pass.md');
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
test('archived recursive publication retains the current-node evidence check', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir,'../examples/1105/inorder.cjs',source=>source,0);
 const {checkReady}=require('../scripts/verify-build.cjs'),{save}=require('../scripts/save.cjs');
 const archived=()=>checkReady(run,{archived:true});
 a.throws(()=>save({run,dest:p.join(dir,'notes'),name:'legacy'}),/NEW_UI_REQUIRED/);
 a.throws(archived,/CURRENT_NODE_UNVERIFIED/);
 const file='evidence/browser.json';
 const sha256=hash(fs.readFileSync(p.join(run,'preview.html')));
 const traces=JSON.parse(fs.readFileSync(p.join(run,'trace.json')));
 const checkpoints=Object.values(traces).reduce((total,tr)=>total+tr.lineSteps.length,0);
 const results=[[1440,900],[1024,768],[375,812]].flatMap(viewport=>['light','dark'].map(theme=>({
  viewport,theme,sha256,status:'pass',current_node_checked:checkpoints,
 })));
 const writeReport=()=>{fs.writeFileSync(p.join(run,file),JSON.stringify({status:'pass',results}));approve(run,file);};
 results[0].current_node_checked=0;
 writeReport();
 a.throws(archived,/CURRENT_NODE_UNVERIFIED/);
 results[0].current_node_checked=checkpoints;
 results[0].sha256='stale';
 writeReport();
 a.throws(archived,/CURRENT_NODE_UNVERIFIED/);
 results[0].sha256=sha256;
 writeReport();
 a.doesNotThrow(archived);
});
test('archived graph publication retains the layout and build evidence check', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir,'../examples/0928/value-address.cjs',source=>source.replace('c-memory','c-graph'),0);
 const browser='evidence/browser.json';
 const preview=fs.readFileSync(p.join(run,'preview.html'),'utf8');
 const sha256=hash(preview),build_sha256=hash(require('../scripts/fonts.cjs').withoutFontHref(preview));
 const traces=Object.values(JSON.parse(fs.readFileSync(p.join(run,'trace.json'))));
 const snapshots=traces.reduce((total,trace)=>total+trace.snapshots.length,0);
 const results=[[1440,900],[1280,800],[1279,800],[375,812]].flatMap(viewport=>['light','dark'].map(theme=>({
  viewport,theme,sha256,build_sha256,status:'pass',graph_layout_version:2,graph_view:'traversal',
  presets:traces.length,snapshots_checked:snapshots,
  mobile_first_screen:viewport[0]===375 ? ['initial','middle','last'] : undefined,
 })));
 const {checkReady}=require('../scripts/verify-build.cjs');
 const archived=()=>checkReady(run,{archived:true});
 const writeReport=rows=>{
  fs.writeFileSync(p.join(run,browser),JSON.stringify({status:'pass',results:rows,console_errors:[],external_requests:[]}));
  approve(run,browser);
 };
 a.throws(archived,/GRAPH_LAYOUT_UNVERIFIED/);
 writeReport(results.slice(1));
 a.throws(archived,/GRAPH_LAYOUT_UNVERIFIED/);
 writeReport(results.map(result=>({...result,build_sha256:'stale'})));
 a.throws(archived,/GRAPH_LAYOUT_UNVERIFIED/);
 writeReport(results);
 a.doesNotThrow(archived);
});
for(const [kind,example,transform] of [
 ['c-memory','../examples/0928/value-address.cjs',source=>source],
 ['c-tree','../examples/1105/inorder.cjs',source=>source],
 ['c-graph','../examples/0928/value-address.cjs',source=>source.replace('c-memory','c-graph')],
]){
 test(kind+' publication requires current layout, padding and mobile evidence', t=>{
  const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const run=runFixture(dir,example,transform);
  const {save}=require('../scripts/save.cjs'),{checkReady,checkPublished}=require('../scripts/verify-build.cjs');
  const dest=p.join(dir,'notes');
  const report=fixtureReport(run);
  const rowFor=width=>report.results.find(row=>row.viewport[0]===width);
  const replace=(width,change)=>report.results.map(row=>row===rowFor(width)?{...row,...change}:row);
  const writeReport=(overrides={})=>{
   fs.writeFileSync(p.join(run,studyReport),JSON.stringify({...report,...overrides}));
   approve(run);
  };
  approve(run,'evidence/pass.md');
  a.throws(()=>save({run,dest,name:kind}),/STUDY_UI_UNVERIFIED/);
  a.equal(fs.existsSync(dest),false);
  for(const results of [
   report.results.filter(row=>row.viewport[0]!==320),
   replace(320,{controls_checked:false}),
   replace(375,{layout_checked:false}),
   replace(375,{mobile_first_screen:['initial','middle']}),
   replace(375,{sha256:'stale-preview'}),
   replace(375,{build_sha256:'stale-build'}),
   replace(375,{ui_version:0}),
   replace(375,{preset_label_checked:false}),
   replace(375,{header_selector_checked:false}),
   replace(375,{input_behavior_checked:false}),
   replace(375,{snapshots_checked:0}),
  ]){
   writeReport({results});
   a.throws(()=>checkReady(run),/STUDY_UI_UNVERIFIED/);
  }
  writeReport({console_errors:['render failed']});
  a.throws(()=>checkReady(run),/STUDY_UI_UNVERIFIED/);
  writeReport();
  const published=save({run,dest,name:kind});
  a.doesNotThrow(()=>checkPublished(published.dir,published.html));
  fs.appendFileSync(published.html,'<!-- changed layout -->');
  a.throws(()=>checkPublished(published.dir,published.html),/REBUILD_MISMATCH/);
 });
}
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

test('new publication requires theme evidence for the preview being saved', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir);
 const evidence=p.join(run,'evidence/theme.json');
 const report=JSON.parse(fs.readFileSync(evidence,'utf8'));
 const {checkReady}=require('../scripts/verify-build.cjs');
 for(const invalid of [{...report,build_sha256:'old'}, {...report,storage:false}]){
  fs.writeFileSync(evidence,JSON.stringify(invalid));
  approve(run);
  a.throws(()=>checkReady(run),/THEME_UNVERIFIED/);
 }
 fs.writeFileSync(evidence,JSON.stringify(report));
 approve(run);
 a.doesNotThrow(()=>checkReady(run));
});

test('theme-only updates preserve the archived HTML and cannot be used for new publication', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir);
 const preview=p.join(run,'preview.html'), reviewPath=p.join(run,'review.json');
 const evidence=p.join(run,studyReport), themeEvidence=p.join(run,'evidence/theme.json');
 const {addTheme,removeTheme}=require('../scripts/theme.cjs');
 const {currentHashes}=require('../scripts/review.cjs');
 const {checkReady}=require('../scripts/verify-build.cjs');
 const base=removeTheme(fs.readFileSync(preview,'utf8')).replace('<title>', '<!-- archived layout --><title>');
 fs.writeFileSync(preview,base);
 fs.writeFileSync(evidence,JSON.stringify(fixtureReport(run)));
 const update=(html)=>{
  fs.writeFileSync(preview,html);
  fs.writeFileSync(themeEvidence,JSON.stringify(fixtureThemeReport(html)));
  const review=JSON.parse(fs.readFileSync(reviewPath,'utf8'));
  fs.writeFileSync(reviewPath,JSON.stringify({...review,theme_base_sha256:hash(base),hashes:currentHashes(run)}));
 };
 update(addTheme(base));
 a.throws(()=>checkReady(run),/THEME_BASE_NOT_ARCHIVED/);
 a.equal(checkReady(run,{archived:true}),addTheme(base));
 update(addTheme(base).replace('archived layout','unreviewed layout'));
 a.throws(()=>checkReady(run,{archived:true}),/REBUILD_MISMATCH/);
});

test('archived preset label updates preserve the selector and require browser evidence', t=>{
 const dir=tmp();t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
 const run=runFixture(dir,'../examples/0928/value-address.cjs',source=>source,1);
 const preview=p.join(run,'preview.html'), reviewPath=p.join(run,'review.json');
 const themeEvidence=p.join(run,'evidence/theme.json');
 const {removeTheme}=require('../scripts/theme.cjs');
 const {addLegacyPresetLabel,removeLegacyPresetLabel}=require('../scripts/preset-label.cjs');
 const {currentHashes}=require('../scripts/review.cjs');
 const {checkReady}=require('../scripts/verify-build.cjs');
 const old=fs.readFileSync(preview,'utf8'), html=removeLegacyPresetLabel(old);
 const base=removeTheme(old);
 a.notEqual(html,old);
 a.match(html,/<label> <select data-action="preset" aria-label="사례">/);
 a.equal(addLegacyPresetLabel(html),old);
 fs.writeFileSync(preview,base);
 fs.writeFileSync(p.join(run,studyReport),JSON.stringify(fixtureReport(run)));
 fs.writeFileSync(preview,html);
 const review=JSON.parse(fs.readFileSync(reviewPath,'utf8'));
 const writeReview=(checked)=>{
  fs.writeFileSync(themeEvidence,JSON.stringify({...fixtureThemeReport(html),preset_label_checked:checked}));
  fs.writeFileSync(reviewPath,JSON.stringify({...review,reviewed_preview_sha256:hash(base),
   theme_base_sha256:hash(base),preset_label_removed:true,hashes:currentHashes(run)}));
 };
 writeReview(false);
 a.throws(()=>checkReady(run,{archived:true}),/THEME_UNVERIFIED/);
 writeReview(true);
 a.equal(checkReady(run,{archived:true}),html);
});
