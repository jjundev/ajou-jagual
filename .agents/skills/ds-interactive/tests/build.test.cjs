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
