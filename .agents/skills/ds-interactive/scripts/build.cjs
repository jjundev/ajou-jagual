const fs=require('node:fs'),p=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),{checkScenario}=require('../assets/engine/trace.js');
const {fontHref}=require('./fonts.cjs');
const {CURRENT_THEME_VERSION,addTheme}=require('./theme.cjs');
const {addLegacyPresetLabel}=require('./preset-label.cjs');
const UI_VERSIONS=[0,1,2];
const CURRENT_UI_VERSION=UI_VERSIONS.at(-1);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
// Graphs reuse the tree panel policy. Legacy tree and pointer bundles keep their original bytes.
function graphPanelShell(source) {
 const profile = "const tree=app.dataset.kind==='c-tree';";
 const storage = "const treeWidthKey='ds-interactive:tree-panel-widths';";
 if (!source.includes(profile) || !source.includes(storage)) throw Error('Graph panel profile could not be applied');
 return source.replace(profile, "const tree=app.dataset.kind==='c-graph';")
  .replace(storage, "const treeWidthKey='ds-interactive:graph-panel-widths';");
}
function buildPage({scenario,outDir=process.cwd(),uiVersion=CURRENT_UI_VERSION,themeVersion=CURRENT_THEME_VERSION}){
 if(![0,CURRENT_THEME_VERSION].includes(themeVersion))throw Error('THEME_VERSION_UNSUPPORTED: '+themeVersion);
 if(!UI_VERSIONS.includes(uiVersion))throw Error('UI_VERSION_UNSUPPORTED: '+uiVersion);
 const {definition,sourceText}=scenario;if(/\brequire\s*\(|\bimport\s*(?:\(|[\s{*])/m.test(sourceText))throw Error('External require/import is not supported');
 const ctx={module:{exports:{}},structuredClone};vm.runInNewContext(sourceText,ctx,{timeout:2000});const s=definition??ctx.module.exports;if(ctx.module.exports.id!==s.id)throw Error('Scenario id mismatch');
 const result=checkScenario(s);if(!result.ok)throw Error(JSON.stringify(result.issues));if(!['c-memory','c-tree','c-graph'].includes(s.kind))throw Error(`Renderer missing: ${s.kind}`);
 const assets=p.join(__dirname,'../assets'),read=f=>fs.readFileSync(p.join(assets,f),'utf8');
 const tree=s.kind==='c-tree',graph=s.kind==='c-graph';
 const inspection=graph&&['bridges','degree'].includes(s.graph?.view);
 const decisions=graph&&['mst','topo'].includes(s.graph?.view);
 if(decisions&&uiVersion===0)throw Error('UI_VERSION_UNSUPPORTED: '+uiVersion+' for '+s.graph.view);
 const graphAsset=decisions?'graph-decisions':inspection?'graph-inspection':'graph';
 const common=uiVersion!==0, ui='ui/v1/';
 const legacyPresetLabel=uiVersion<2;
 const css=['player.css',...(common?[ui+'study.css']:graph?['graph-shell.css']:[]),
  ...(graph?[graphAsset+'.css']:[])].map(file=>{
  const stylesheet=read(file);
  return !legacyPresetLabel&&file===ui+'study.css'
   ?stylesheet.replaceAll('[data-ui-version="1"]','[data-ui-version="'+uiVersion+'"]')
   :stylesheet;
 }).join('\n');
 let html=read('shell.html').replace('/*FONT_HREF*/',fontHref(outDir)).replace('/*CSS*/',css);
 if(common)html=html.replace('id="app"','id="app" data-ui-version="'+uiVersion+'"');
 // Preserve the original markup when reproducing old reviews.
 if(legacyPresetLabel)html=addLegacyPresetLabel(html);
 const runtime=common?[ui+'shell.js',ui+'study.js',ui+'adapters.js',ui+'player.js']:
  [...(tree?['tree-ui.js']:[]),'shell.js','player.js',...(graph?['graph-shell.js']:[])];
 const list=['engine/contract.js','engine/memory.js',...(tree?['engine/line-steps.js','engine/tree.js']:[]),
  'engine/trace.js','memory-svg.js',...(tree?['tree-svg.js']:[]),...runtime,...(graph?[graphAsset+'.js']:[])]
  .map(file=>!common&&graph&&file==='shell.js'?graphPanelShell(read(file)):read(file));
 // Browser must take the browser branch; the Node source remains byte-equivalent inside the script.
 list.push(sourceText);list.push(`DSInteractive.player=DSInteractive.${graph?'mountGraphPlayer':'mountPlayer'}(document.querySelector('#app'),DSInteractive.scenario);`);
 html=html.replace('<!--SCRIPTS-->',list.map(js=>`<script>${js.replace(/<\/script/gi,'<\\/script')}</script>`).join('\n'));
 if(themeVersion)html=addTheme(html);
 return {html,uiVersion,themeVersion,kind:s.kind,traces:result.traces,graphView:graph?(decisions||inspection?s.graph.view:'traversal'):null,hashes:{scenario:sha(sourceText),trace:sha(JSON.stringify(result.traces,null,2)),preview:sha(html)}};
}
module.exports={buildPage,sha,CURRENT_UI_VERSION};
if(require.main===module){const file=p.resolve(process.argv[2]),r=buildPage({outDir:p.dirname(p.resolve(process.argv[3])),scenario:{sourceText:fs.readFileSync(file,'utf8')}});fs.writeFileSync(process.argv[3],r.html);console.log(JSON.stringify({file:process.argv[3],ui_version:r.uiVersion,hashes:r.hashes}));}
