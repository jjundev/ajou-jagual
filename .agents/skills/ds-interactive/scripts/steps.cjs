const p=require('node:path'),{checkScenario}=require('../assets/engine/trace.js');
if(require.main===module){const r=checkScenario(require(p.resolve(process.argv[2])));console.log(JSON.stringify(r.traces,null,2));if(!r.ok)process.exitCode=1;}
