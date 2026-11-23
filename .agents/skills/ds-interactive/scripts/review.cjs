const fs=require('node:fs'),p=require('node:path'),crypto=require('node:crypto');
const {CURRENT_UI_VERSION}=require('./build.cjs');
const {CURRENT_THEME_VERSION}=require('./theme.cjs');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function currentHashes(dir){const out={};function scan(folder,prefix=''){for(const e of fs.readdirSync(folder,{withFileTypes:true})){const rel=prefix+e.name;if(e.isSymbolicLink())throw Error('SYMLINK_NOT_SUPPORTED: '+rel);if(e.isDirectory()){if(prefix||e.name==='evidence')scan(p.join(folder,e.name),rel+'/');}else if(prefix||['scenario.cjs','trace.json','preview.html','source.json','brief.md','source.c'].includes(e.name))out[rel]=hash(fs.readFileSync(p.join(folder,e.name)));}}scan(dir);return out;}
function createReview(dir){return {version:1,ui_version:CURRENT_UI_VERSION,theme_version:CURRENT_THEME_VERSION,hashes:currentHashes(dir),checks:Object.fromEntries(['schema','content','independent','browser'].map(k=>[k,{status:'not_run',evidence:'',notes:''}]))};}
const readReview=dir=>JSON.parse(fs.readFileSync(p.join(dir,'review.json'),'utf8'));
function verifyReview(dir){const issues=[],add=(code,message)=>issues.push({code,message});let review,now;try{review=readReview(dir);now=currentHashes(dir);}catch(e){return [{code:'REVIEW_MISSING',message:e.message}];}
 if(review.version!==1)add('REVIEW_VERSION','version 1 required');
 for(const f of ['scenario.cjs','trace.json','preview.html','source.json','brief.md'])if(!now[f])add('HASH_MISSING',f);
 if(JSON.stringify(Object.entries(now).sort())!==JSON.stringify(Object.entries(review.hashes||{}).sort()))add('HASH_CHANGED','검토 후 파일이 바뀌었습니다.');
 for(const name of ['schema','content','independent','browser']){const c=review.checks?.[name];if(c?.status!=='pass')add('REVIEW_NOT_PASS',name);const rel=c?.evidence;const full=typeof rel==='string'?p.resolve(dir,rel):'';if(!rel||p.isAbsolute(rel)||!full.startsWith(p.resolve(dir)+p.sep)||!fs.existsSync(full)||!fs.statSync(full).isFile()||fs.statSync(full).size===0||!now[rel.replaceAll('\\','/')])add('EVIDENCE_INVALID',name);if(!c?.notes?.trim())add('REVIEW_NOTES_MISSING',name);}
 return issues;
}
module.exports={createReview,readReview,verifyReview,currentHashes,hash};
if(require.main===module){try{const [mode,dir]=process.argv.slice(2);if(mode==='init')fs.writeFileSync(p.join(dir,'review.json'),JSON.stringify(createReview(dir),null,2),{flag:'wx'});else {const issues=verifyReview(dir);console.log(JSON.stringify({ok:!issues.length,issues},null,2));if(issues.length)process.exitCode=1;}}catch(e){console.error(e.message);process.exitCode=1;}}
