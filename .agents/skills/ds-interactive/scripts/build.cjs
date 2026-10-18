const fs=require('node:fs'),p=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),{checkScenario}=require('../assets/engine/trace.js');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function buildPage({scenario,inputs,title}){
 const {definition:s,sourceText}=scenario;if(/\brequire\s*\(|\bimport\s*(?:\(|[\s{*])/m.test(sourceText))throw Error('External require/import is not supported');
 const ctx={module:{exports:{}},structuredClone};vm.runInNewContext(sourceText,ctx,{timeout:2000});if(ctx.module.exports.id!==s.id)throw Error('Scenario id mismatch');
 const result=checkScenario(s);if(!result.ok)throw Error(JSON.stringify(result.issues));if(s.kind!=='c-memory')throw Error(`Renderer missing: ${s.kind}`);
 const assets=p.join(__dirname,'../assets'),read=f=>fs.readFileSync(p.join(assets,f),'utf8');
 const faces=[['Regular',400],['Medium',500],['SemiBold',600],['Bold',700]].map(([name,weight])=>{
  const data=fs.readFileSync(p.join(assets,`vendor/pretendard/Pretendard-${name}.woff2`)).toString('base64');
  return `@font-face{font-family:Pretendard;src:url(data:font/woff2;base64,${data}) format('woff2');font-style:normal;font-weight:${weight};font-display:swap}`;
 }).join('\n');
 let html=read('shell.html').replace('/*FONT*/',`/* ${read('vendor/pretendard/LICENSE')} */\n${faces}`).replace('/*CSS*/',read('player.css'));
 const list=['engine/contract.js','engine/memory.js','engine/trace.js','memory-svg.js','shell.js','player.js'].map(read);
 // Browser must take the browser branch; the Node source remains byte-equivalent inside the script.
 list.push(sourceText);list.push("DSInteractive.player=DSInteractive.mountPlayer(document.querySelector('#app'),DSInteractive.scenario);");
 html=html.replace('<!--SCRIPTS-->',list.map(js=>`<script>${js.replace(/<\/script/gi,'<\\/script')}</script>`).join('\n'));
 return {html,traces:result.traces,hashes:{scenario:sha(sourceText),trace:sha(JSON.stringify(result.traces,null,2)),preview:sha(html)}};
}
module.exports={buildPage,sha};
if(require.main===module){const file=p.resolve(process.argv[2]),r=buildPage({scenario:{definition:require(file),sourceText:fs.readFileSync(file,'utf8')}});fs.writeFileSync(process.argv[3],r.html);console.log(JSON.stringify({file:process.argv[3],hashes:r.hashes}));}
