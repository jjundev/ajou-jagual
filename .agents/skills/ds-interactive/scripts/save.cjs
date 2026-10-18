const fs=require('node:fs'),p=require('node:path'),{verifyReview,hash}=require('./review.cjs');
function save({run,dest,name}){
 if(!name||/[<>:"/\\|?*\x00-\x1f]/.test(name)||/[. ]$/.test(name)||/^(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\.|$)/i.test(name)||name.length>80)throw Error('NAME_INVALID');
 const issues=verifyReview(run);if(issues.length)throw Error(JSON.stringify(issues));
 dest=p.resolve(dest);run=p.resolve(run);if(dest===run||dest.startsWith(run+p.sep))throw Error('DEST_INVALID');fs.mkdirSync(p.join(dest,'.pack'),{recursive:true});
 const entries=[...fs.readdirSync(dest),...fs.readdirSync(p.join(dest,'.pack'))];let nn=Math.max(0,...entries.map(n=>Number(n.match(/인터렉티브_(\d+)_/)?.[1]||0)))+1;
 while(nn<100000){const base=`인터렉티브_${String(nn).padStart(2,'0')}_${name}`,html=p.join(dest,base+'.html'),dir=p.join(dest,'.pack','자료_'+base),lock=p.join(dest,'.pack',`.ds-interactive-number-${nn}.lock`);let ownDir=false,ownHtml=false,ownLock=false,fd,lockfd;
  try{lockfd=fs.openSync(lock,'wx');ownLock=true;
   // Recheck while holding the number lock: another writer may have published after our initial scan.
   const used=[...fs.readdirSync(dest),...fs.readdirSync(p.join(dest,'.pack'))].some(n=>Number(n.match(/인터렉티브_(\d+)_/)?.[1])===nn);
   if(used){nn++;continue;}
   fs.mkdirSync(dir);ownDir=true;fd=fs.openSync(html,'wx');ownHtml=true;
   for(const e of fs.readdirSync(run))fs.cpSync(p.join(run,e),p.join(dir,e),{recursive:true,errorOnExist:true,force:false});
   const links=p.join(dir,'note-links.json');if(fs.existsSync(links))fs.writeFileSync(links,fs.readFileSync(links,'utf8').replaceAll('$HTML',base+'.html'));
   const second=verifyReview(dir);if(second.length)throw Error(JSON.stringify(second));const bytes=fs.readFileSync(p.join(dir,'preview.html'));fs.writeFileSync(fd,bytes);fs.closeSync(fd);fd=undefined;
   if(hash(fs.readFileSync(html))!==hash(bytes))throw Error('COPY_HASH_MISMATCH');return {nn,html,dir};
  }catch(e){if(fd!==undefined)fs.closeSync(fd);if(ownHtml)fs.unlinkSync(html);if(ownDir)fs.rmSync(dir,{recursive:true,force:true});if(e.code==='EEXIST'){nn++;continue;}throw e;}
  finally{if(lockfd!==undefined)fs.closeSync(lockfd);if(ownLock)fs.unlinkSync(lock);}
 }throw Error('NUMBER_EXHAUSTED');
}
module.exports={save};
if(require.main===module){try{const [run,dest,name]=process.argv.slice(2);console.log(JSON.stringify(save({run,dest,name}),null,2));}catch(e){console.error(e.message);process.exitCode=1;}}
