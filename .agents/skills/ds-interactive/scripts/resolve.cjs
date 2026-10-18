const fs=require('node:fs'),p=require('node:path');
const fail=(code,message)=>{throw Object.assign(new Error(message),{code});};
function files(dir){if(!fs.existsSync(dir))return [];return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?(e.name==='.pack'?files(p.join(dir,e.name)):[]):[p.join(dir,e.name)]);}
function resolveTarget({repo,arg,source}) {
 repo=p.resolve(repo);arg=String(arg||'').trim();const base=p.join(repo,'복습노트');let kind='topic',folder=p.join(base,'주제별'),date=null;
 const explicit=source||(/\.c$/i.test(arg)?arg:null);let code=null;
 if(explicit){code=p.resolve(repo,explicit);if(!fs.existsSync(code)||!fs.statSync(code).isFile())fail('SOURCE_MISSING',code);kind='code';}
 else if(/^\d{4}(?:-\d{4})?$/.test(arg)){
  const [lo,hi=lo]=arg.split('-').map(Number);
  const candidates=(fs.existsSync(base)?fs.readdirSync(base,{withFileTypes:true}):[]).filter(e=>e.isDirectory()&&/^\d{4}(?:-\d{4})?$/.test(e.name)).filter(e=>{const [a,b=a]=e.name.split('-').map(Number);return a<=hi&&b>=lo;});
  if(candidates.length>1)fail('AMBIGUOUS_TARGET',candidates.map(e=>e.name).join(', '));
  if(!candidates.length)fail('TARGET_MISSING',arg);date=candidates[0].name;folder=p.join(base,date);kind='date';
 }
 const all=files(folder),notes=all.filter(f=>/정리노트.*\.(md|html)$/i.test(p.basename(f).normalize('NFC'))).filter(f=>p.extname(f)!=='.md'||p.basename(p.dirname(f))==='.pack'||!all.some(other=>p.basename(p.dirname(other))==='.pack'&&p.basename(other).normalize('NFC')===p.basename(f).normalize('NFC')));
 const existing=all.filter(f=>/^인터렉티브_\d+_.*\.html$/.test(p.basename(f)));
 const nums=[...existing,...(fs.existsSync(p.join(folder,'.pack'))?fs.readdirSync(p.join(folder,'.pack')):[])].map(f=>Number(p.basename(f).match(/인터렉티브_(\d+)_/)?.[1]||0));
 return {kind,folder,date,notes,noteHtml:notes.find(f=>f.endsWith('.html'))||null,stt:date?files(p.join(repo,'STT')).filter(f=>p.basename(f).startsWith(date)):[],source:code,existing,next:Math.max(0,...nums)+1};
}
module.exports={resolveTarget};
if(require.main===module){try{console.log(JSON.stringify(resolveTarget({repo:process.argv[2],arg:process.argv[3]}),null,2));}catch(e){console.error(e.code,e.message);process.exitCode=1;}}
