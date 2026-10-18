const p=require('node:path'),{checkScenario}=require('../assets/engine/trace.js');
module.exports={checkScenario};
if(require.main===module){try{const r=checkScenario(require(p.resolve(process.argv[2])));console.log(JSON.stringify({ok:r.ok,issues:r.issues,cases:Object.keys(r.traces)},null,2));if(!r.ok)process.exitCode=1;}catch(e){console.error(e);process.exitCode=1;}}
