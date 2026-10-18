"""Independent table oracle: no JS engine imports or expectations read from Scenario.expected."""
import json,subprocess,sys,shutil
from pathlib import Path

def integer(v):return {'kind':'int','value':v}
def pointer(v):return {'kind':'pointer','target':v}
def oracle(topic,x):
 a,b=x.get('a'),x.get('b');mode=x['mode'];rows=[]
 def put(cell,v):rows.append([cell,v])
 if topic=='value-address':
  ptr=mode!='value';right=a if mode=='alias' else b
  put('f.px',pointer('main.a') if ptr else integer(a));put('f.py',pointer('main.a' if mode=='alias' else 'main.b') if ptr else integer(b));put('f.tmp',{'kind':'uninitialized'})
  put('f.tmp',integer(a));put('main.a' if ptr else 'f.px',integer(right));put(('main.a' if mode=='alias' else 'main.b') if ptr else 'f.py',integer(a))
 elif topic=='pointer-target':
  put('f.p',pointer(None if mode=='null' else 'main.a'))
  if mode!='null':put('main.a',integer(x['value']));put('f.p',pointer(None))
 else:
  double=mode!='single';put('f.pp' if double else 'f.p',pointer(None if mode=='null' else 'main.q' if double else 'main.a'));put('f.next',pointer('main.b'))
  if mode!='null':put('main.q' if double else 'f.p',pointer('main.b'))
 return rows

def verify(trace):
 topic=trace['id'];actual=[[w['cellId'],w['after']] for s in trace['snapshots'] for w in s['writes']]
 expected=oracle(topic,trace['inputs']);assert actual==expected,(topic,trace['inputs'],actual,expected)
 diag=trace['snapshots'][-1]['diagnostic'];assert (diag['code'] if diag else None)==('NULL_DEREFERENCE' if trace['inputs']['mode']=='null' else None)
 return {'topic':topic,'input':trace['inputs'],'writes_checked':len(actual),'diagnostic':diag['code'] if diag else None,'status':'pass'}

if __name__=='__main__':
 skill=Path(__file__).resolve().parents[1];out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True);reports=[]
 for scenario in sorted((skill/'examples/0928').glob('*.cjs')):
  traces=json.loads(subprocess.check_output(['node',str(skill/'scripts/steps.cjs'),str(scenario)],encoding='utf8'))
  for trace in traces.values():reports.append(verify(trace))
  # Boundary and equal inputs in every supported mode, compiled by real public CLI API.
  js="const s=require(process.argv[1]),e=require(process.argv[2]);const out=[];for(const m of s.inputs.find(x=>x.key==='mode').options)for(const n of [-99,0,99]){const x=Object.fromEntries(s.inputs.map(d=>[d.key,d.type==='integer'?n:m.value]));out.push(e.compileScenario(s,x));}console.log(JSON.stringify(out));"
  traces=json.loads(subprocess.check_output(['node','-e',js,str(scenario),str(skill/'assets/engine/trace.js')],encoding='utf8'))
  reports.extend(verify(t) for t in traces)
 result={'method':'independent Python write/bind table','compiler_unavailable':not any(shutil.which(c) for c in ['gcc','clang','cl']),'cases':reports,'total':len(reports),'status':'pass'}
 (out/'independent.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':'pass','cases':len(reports),'writes':sum(r['writes_checked'] for r in reports),'compiler_unavailable':result['compiler_unavailable']}))
