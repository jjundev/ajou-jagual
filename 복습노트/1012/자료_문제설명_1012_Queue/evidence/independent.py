from pathlib import Path
import json,re,html,subprocess
w=Path(__file__).resolve().parent;r=w.parent;s=json.loads((r/'source.json').read_text());out={}
# Independent token-to-expression reduction, separate from authoring simulator.
def expression(tokens):
 st=[];states=[];pu=po=0
 for t in tokens.split():
  if t.isdigit():st.append((int(t),t));pu+=1
  else:
   b,eb=st.pop();a,ea=st.pop();po+=2
   if t=='+':v=a+b
   elif t=='-':v=a-b
   elif t=='*':v=a*b
   elif t=='/':assert b!=0 and a%b==0;v=a//b
   st.append((v,f'({ea}{t}{eb})'));pu+=1
  states.append([v for v,_ in st])
 assert len(st)==1
 return dict(value=st[0][0],expression=st[0][1],states=states,push=pu,pop=po)
out['p1']=expression('5 6 * 4 2 / + 1 -');assert (out['p1']['value'],out['p1']['push'],out['p1']['pop'])==(31,9,8)
out['p2']={'part1':expression('2 4 + 7 * 6 3 * - 1 +'),'part2':expression('5 6 * 4 2 / + 1 -')};assert out['p2']['part1']['value']==(2+4)*7-6*3+1==25;assert out['p2']['part2']['states']==[[5],[5,6],[30],[30,4],[30,4,2],[30,2],[32],[32,1],[31]]
out['p3']=expression('7 6 2 / - 5 4 * +');assert out['p3']['states']==[[7],[7,6],[7,6,2],[7,3],[4],[4,5],[4,5,4],[4,20],[24]]
out['p4']={'answer':'스택','proof':'proper nesting closes the most recently opened unmatched delimiter; stack exactly implements this invariant, independent of nesting depth'}
out['p5']={'answer':'스택','proof':'postfix binary operators combine the two most recently completed pending operands; replacing them with their result maintains the pending-subexpression invariant'}
out['p7']={'answer':'큐','proof':'rear insertion and front removal preserve arrival order for all customers in the ordinary FIFO model stated by the problem'}
out['p8']={'answer':'X','counterexample':'push A; push B; pop returns B, whereas FIFO would return A'}
p6=next(p for p in s['problems'] if p['id']=='p6');bs=[html.unescape(x) for x in re.findall(r'<pre><code[^>]*>(.*?)</code></pre>',p6['conditions_html'],re.S)];ans=json.loads((w/'blank_answers.json').read_text());c=bs[0]+ans['push']+'\n'+bs[1];c=re.sub(r'else \{\s*\}',lambda m:'else {\n'+ans['pop']+'\n\t}',c);m=re.sub(r'(for \(i = 0; i < len; i\+\+\)\{)\s*\}',lambda q:q[1]+'\n'+ans['loop']+'\n\t}',bs[2]);c+='\n'+m
assert 'int op;' not in c and 'exit(' not in c and '%99s' not in c
(w/'p6_original_blanks.c').write_text(c);exe=w/'p6_original_blanks';cc=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-pedantic',str(w/'p6_original_blanks.c'),'-o',str(exe)],capture_output=True,text=True);(w/'p6_compile.txt').write_text(cc.stdout+cc.stderr);assert cc.returncode==0
cases=[]
for inp,expected in [('23+4*',20),('52*3+',13),('0',0),('99*9+',90)]:
 x=subprocess.run([str(exe)],input=inp,text=True,capture_output=True,check=True);assert x.stdout.endswith(f'result:{expected}');cases.append(dict(input=inp,output=x.stdout,expected=expected))
out['p6']={'cases':cases,'scope':'Only original blanks filled. No added variables, error exit, or scanf width. Defined valid input only; <=99 chars, sufficient operands, capacity<=100, int no overflow. Compiler warns original empty-pop branch has no return.'}
(w/'independent-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2));print('Compiler:',cc.stderr)
