const fs=require('node:fs'),p=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),{checkScenario}=require('../assets/engine/trace.js');
const {fontHref}=require('./fonts.cjs');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function buildPage({scenario,outDir=process.cwd()}){
 const {definition:s,sourceText}=scenario;if(/\brequire\s*\(|\bimport\s*(?:\(|[\s{*])/m.test(sourceText))throw Error('External require/import is not supported');
 const ctx={module:{exports:{}},structuredClone};vm.runInNewContext(sourceText,ctx,{timeout:2000});if(ctx.module.exports.id!==s.id)throw Error('Scenario id mismatch');
 const result=checkScenario(s);if(!result.ok)throw Error(JSON.stringify(result.issues));if(!['c-memory','c-tree'].includes(s.kind))throw Error(`Renderer missing: ${s.kind}`);
 const assets=p.join(__dirname,'../assets'),read=f=>fs.readFileSync(p.join(assets,f),'utf8');
 let html=read('shell.html').replace('/*FONT_HREF*/',fontHref(outDir)).replace('/*CSS*/',read('player.css'));
 const tree=s.kind==='c-tree';
 const list=['engine/contract.js','engine/memory.js',...(tree?['engine/line-steps.js','engine/tree.js']:[]),
  'engine/trace.js','memory-svg.js',...(tree?['tree-svg.js']:[]),'shell.js','player.js'].map(read);
 // Browser must take the browser branch; the Node source remains byte-equivalent inside the script.
 list.push(sourceText);list.push("DSInteractive.player=DSInteractive.mountPlayer(document.querySelector('#app'),DSInteractive.scenario);");
 html=html.replace('<!--SCRIPTS-->',list.map(js=>`<script>${js.replace(/<\/script/gi,'<\\/script')}</script>`).join('\n'));
 return {html,traces:result.traces,hashes:{scenario:sha(sourceText),trace:sha(JSON.stringify(result.traces,null,2)),preview:sha(html)}};
}
module.exports={buildPage,sha};
if(require.main===module){const file=p.resolve(process.argv[2]),r=buildPage({outDir:p.dirname(p.resolve(process.argv[3])),scenario:{definition:require(file),sourceText:fs.readFileSync(file,'utf8')}});fs.writeFileSync(process.argv[3],r.html);console.log(JSON.stringify({file:process.argv[3],hashes:r.hashes}));}
