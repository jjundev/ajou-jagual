const {test}=require('node:test'),a=require('node:assert/strict'),vm=require('node:vm');
const text=`(function(){const s={version:1,id:'escape',title:'<img onerror=x>',kind:'c-memory',sources:[{id:'c',text:'// </script> & <img>',language:'c'}],inputs:[],presets:[],initialState:()=>({frames:{},objects:{},cells:{},activeFrame:null,stdout:[]}),generateEvents:()=>[],expected:[]};if(typeof module!=='undefined')module.exports=s;else DSInteractive.scenario=s;})();`;
function definition(src){const ctx={module:{exports:{}},structuredClone};vm.runInNewContext(src,ctx);return ctx.module.exports;}
test('builder links the shared font, embeds the engine and safely serializes closing script',()=>{
 const {buildPage}=require('../scripts/build.cjs');const r=buildPage({scenario:{definition:definition(text),sourceText:text}});
 a.match(r.html, /<link rel="stylesheet" data-ds-interactive-font href="[^"]+\/pretendard\/pretendard\.css">/);
 a.doesNotMatch(r.html, /data:font\/|<script[^>]+src=|@import|fetch\(/i);
 a.ok(!r.html.includes('// </script> & <img>'));
 const scripts=[...r.html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);const ctx={structuredClone,module:undefined};for(const src of scripts.slice(0,-1))vm.runInNewContext(src,ctx);
 a.equal(ctx.DSInteractive.scenario.sources[0].text,'// </script> & <img>');a.equal(ctx.DSInteractive.compileScenario(ctx.DSInteractive.scenario,{}).snapshots.length,1);
});
test('build rejects source mismatch, imports and invalid source line',()=>{
 const {buildPage}=require('../scripts/build.cjs');a.throws(()=>buildPage({scenario:{definition:{...definition(text),id:'wrong'},sourceText:text}}),/mismatch/);
 a.throws(()=>buildPage({scenario:{definition:definition(text),sourceText:text+'\nrequire("fs")'}}),/import|require/);
 const bad=definition(text);bad.generateEvents=()=>[{kind:'observe',at:{sourceId:'c',line:99},explanation:'bad'}];a.throws(()=>buildPage({scenario:{definition:bad,sourceText:text}}),/LOCATION_INVALID/);
});
test('inorder build embeds the tree renderer and compiles offline',()=>{
 const {buildPage}=require('../scripts/build.cjs');
 const path=require.resolve('../examples/1105/inorder.cjs');
 const sourceText=require('node:fs').readFileSync(path,'utf8');
 const {html}=buildPage({scenario:{definition:require(path),sourceText}});
 a.doesNotMatch(html,/<script[^>]+src=|@import|fetch\(/i);
 const ctx={structuredClone};
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
 for(const script of scripts.slice(0,-1))vm.runInNewContext(script,ctx);
 const api=ctx.DSInteractive, trace=api.compileScenario(api.scenario,{treeCase:'lecture'});
 a.equal(trace.lineSteps.at(-1).state.stdout.join(''),'3 7 12 18 26 27 31 ');
 a.equal(typeof api.renderers.get('c-tree')?.render,'function');
});
test('graph build embeds the graph player and keeps the graph layout in the scenario',()=>{
 const {buildPage}=require('../scripts/build.cjs');
 const graphText=text.replace("kind:'c-memory'","kind:'c-graph',graph:{positions:[[40,40],[100,100]]}");
 const {html,traces}=buildPage({scenario:{sourceText:graphText}});
 a.doesNotMatch(html,/<script[^>]+src=|@import|fetch\(/i);
 a.equal(traces.default.kind,'c-graph');
 const ctx={structuredClone};
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x=>x[1]);
 for(const script of scripts.slice(0,-1))vm.runInNewContext(script,ctx);
 a.equal(typeof ctx.DSInteractive.mountGraphPlayer,'function');
 a.equal(JSON.stringify(ctx.DSInteractive.scenario.graph),JSON.stringify({positions:[[40,40],[100,100]]}));
});

test('a new build uses the versioned common UI by default',()=>{
 const {buildPage}=require('../scripts/build.cjs');
 const sourceText=require('node:fs').readFileSync(require.resolve('../examples/0928/value-address.cjs'),'utf8');
 const build=buildPage({scenario:{sourceText}});
 a.equal(build.uiVersion,1);
 a.match(build.html,/data-ui-version="1"/);
 const legacy=buildPage({scenario:{sourceText},uiVersion:0});
 a.doesNotMatch(legacy.html,/data-ui-version="1"/);
 a.equal(legacy.hashes.trace,build.hashes.trace);
});
