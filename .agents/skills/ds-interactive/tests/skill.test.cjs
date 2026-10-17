const {test}=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),p=require('node:path'),cp=require('node:child_process');
const skill=p.resolve(__dirname,'..');
test('skill is discoverable with resolvable local references and runnable CLIs',()=>{
 const md=fs.readFileSync(p.join(skill,'SKILL.md'),'utf8');a.match(md,/^---\r?\nname: ds-interactive/);a.match(md,/description: Use when/);
 for(const m of md.matchAll(/\]\(([^)]+)\)/g))if(!m[1].includes('://'))a.ok(fs.existsSync(p.resolve(skill,m[1])),m[1]);
 const r=JSON.parse(cp.execFileSync(process.execPath,[p.join(skill,'scripts/resolve.cjs'),process.cwd(),'0928'],{encoding:'utf8'}));a.equal(r.date,'0928');
 for(const script of ['check','steps','build','review','save','link-notes','relink'])a.ok(fs.existsSync(p.join(skill,'scripts',script+'.cjs')));
});
