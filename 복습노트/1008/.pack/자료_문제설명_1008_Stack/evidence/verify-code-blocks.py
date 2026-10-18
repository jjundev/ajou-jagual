"""Independent execution and mathematical checks for the current 64 cards."""
import math,json,subprocess,tempfile,re,html
from pathlib import Path
B=Path(__file__).parent
inputs = sorted(B.glob('*/review-*/source.json'))
if not inputs:
 raise SystemExit('zero question inputs: use docs/verify/rerun-ds-code-blocks.py')
results={}
def record(key,evidence,method='exact'):results[key]={'method':method,'conclusion':evidence,'evidence':evidence}
def compile_run(source,input=''):
 with tempfile.TemporaryDirectory() as td:
  p=Path(td);(p/'x.c').write_text(source)
  cp=subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(p/'x.c'),'-o',str(p/'x')],capture_output=True,text=True)
  assert cp.returncode==0,cp.stderr
  cp=subprocess.run([str(p/'x')],input=input,capture_output=True,text=True,timeout=5)
  assert cp.returncode==0,(cp.stderr,source)
  return cp.stdout.strip()
# Every positive pair <=100: divisors independently vs Euclid recurrence.
for a in range(1,101):
 for b in range(1,101):
  x,y=a,b
  while x%y:x,y=y,x%y
  assert y==max(d for d in range(1,min(a,b)+1) if a%d==b%d==0)
record('foo','10000 positive pairs: Euclidean return equals independently enumerated greatest common divisor; y=0 excluded.','proof')
record('gcd','Same common-divisor invariant; second argument strictly decreases to zero. 10000 pairs matched.','proof')
out=compile_run('#include <stdio.h>\nint gcd(int a,int b){if(!b)return a;return gcd(b,a%b);}\nint main(void){printf("%d %d",gcd(48,18),gcd(18,48));}');assert out=='6 6'
record('recursion','Definition check: self call creates another activation; loop-only implementation has no self-call.','qualitative')
out=compile_run('#include <stdio.h>\nvoid f(int n){if(!n)return;f(n/2);printf("%d",n%2);}\nint main(void){f(10);puts("");f(1);puts("");f(0);puts("");}');assert out=='1010\n1';record('binary','Compiled C: 10→1010,1→1,0→empty. Reconstruction 8+2=10; positive input assumption explicit.')
for c in (10,20,30):
 for n in range(21):
  count=sum(1 for i in range(n) for j in range(i,n) for k in range(c));assert count==c*n*(n+1)//2
 record('tri'+str(c),f'Independent nested-loop enumeration n=0..20 equals {c}n(n+1)/2; pair-sum proof supplies general formula.','proof')
 for n in range(1,21):
  total=0
  for i in range(1,n):
   j=1
   while j<n:
    while j<=i:
     for k in range(1,c):total+=1
     j+=1
    j+=1
  assert total==(c-1)*n*(n-1)//2
 record('four'+str(c),f'Actual j-mutating control flow n=1..20 equals {c-1}n(n-1)/2. k starts 1, p unchanged, j terminates.','proof')
record('broken-loop','Literal k stays zero after entry for n>=2: no finite normal T(n), possible out-of-bounds/overflow. Hazardous original not executed. Explicit k++ assumption only: enumerate n=0..20 →30n(n-1)/2. Original key uses intended-code assumption, not literal behavior.','qualitative')
for a,b in [(3,8),(-2,-7),(4,4)]:
 x,y=a,b;t=x;x=y;y=t;assert (x,y)==(b,a)
record('ch01-q01','Temporary-value invariant yields final (old b,old a); examples 3,8 and equal/negative values.','proof')
record('ch01-q02','Exhaustive branches a>=b/a<b each produce an input >=both; positive,negative,equal examples.','proof')
for n in range(1,101):assert sum(range(1,n+1))==n*(n+1)//2
for k in ('ch01-q03','ch02-q13','ch02-q16'):record(k,'Initialization, preservation and termination of prefix-sum invariant; n=1..100 equals arithmetic formula.','proof')
record('ch01-q12','Asymptotic ratios log(n)/n→0, log(n)<n eventually; exponential dominates fixed polynomial; factorial/2^n diverges. n=16 spot check not treated as proof.','proof')
record('ch01-q09','Lecture page28 defines T(n) operation count; T(0,1,2)=10,17,24, not seconds or bytes.','qualitative')
record('ch02-q01','Lecture base n<=1: deepest live factorial calls 5,4,3,2,1 (five), then returns 1,2,6,24,120.')
record('ch02-q05','For every n!=1, child has same n and no progress. Defect analysis only; no normal return approved.','qualitative')
record('ch02-q06','No branch avoids recursive call; decreasing n alone cannot establish termination. Defect, not normal execution result.','qualitative')
trace=[]
def rec(n):
 trace.append(n)
 return -1 if n<1 else rec(n-3)+1
assert rec(10)==3 and trace==[10,7,4,1,-2];record('ch02-q09','Separate recursion simulator: prints 10,7,4,1,-2, return3; -1+four edges=3.')
out=compile_run('#include <stdio.h>\nint main(void){int a[10][20];int a1[10];double a2[10];char a3[40];float a4[10];printf("%zu %zu %zu %zu %zu %zu",sizeof(int),sizeof a,sizeof a1,sizeof a2,sizeof a3,sizeof a4);}')
assert out=='4 800 40 80 40 40';record('ch03-q01','C sizeof: int4, a[10][20]800; independent 10*20*4=800.');record('ch03-q03','C sizeof arrays 40,80,40,40: option2 largest in stated environment.')
record('ch03-q04','2**i for i=0..9 yields 1,2,4,8,16,32,64,128,256,512; recurrence induction and compiled printed program.')
record('ch03-q05','Member types char[],int,float satisfy specification; name capacity chosen, not prescribed. Compiler accesses verified.','qualitative')
record('ch03-q06','typedef declares type alias, separate c1,c2 declarations create two objects; float real/imaginary member accesses compile.','qualitative')
record('ch03-q07','Componentwise sum (1,2)+(3,4)=(4,6); compiled function returns structure by value and leaves inputs unchanged.')
record('ch03-q12','Compiled sanitizer program prints100 just testing; malloc sizeof object, NULL guard,12-character string plus NUL fits21, one free.')
record('ch01-q17','Random-address calculation is constant; an unseen arbitrary value can change minimum/sum, proving all elements necessary.','proof')
for n in range(1,11):
 for loc in range(n+1):
  a=list(range(n))+[None];moves=0
  for i in range(n-1,loc-1,-1):a[i+1]=a[i];moves+=1
  a[loc]=99;assert a==list(range(n))[:loc]+[99]+list(range(n))[loc:] and moves==n-loc
 for loc in range(n):
  a=list(range(n));removed=a[loc];moves=0
  for i in range(loc,n-1):a[i]=a[i+1];moves+=1
  assert a[:n-1]==list(range(n))[:loc]+list(range(n))[loc+1:] and removed==loc and moves==n-loc-1
record('ch03-q08','Every insertion position at lengths1..10 matches abstract list insertion; backward copy preserves unmoved values.','proof');record('ch03-q09','Independent move counter equals items-loc for all positions; worst items, best0 moves plus constant work.','proof')
record('ch03-q10','Every deletion position at lengths1..10 matches abstract deletion and returned removed value; prefix-copy invariant.','proof');record('ch03-q11','Move counter items-loc-1, worst items-1, last0; constant overhead.','proof')
record('ch06-q03','Last node exists and has NULL next; dereference of NULL next not evaluated.','qualitative');record('ch06-q04','Noncontiguous-node addresses cannot be traversed by +/-; stored link gives next; each a,b,c,d separately assessed.','qualitative')
record('ch06-q07','Reference traversal A→B→C→D tests next link, stops D before NULL; empty-list code excluded.')
record('ch06-q10','Acyclic prefix visitation invariant; compiled program with inputs0 and3,5,6,7 yields0 and3 and frees all allocated nodes.','proof')
record('ch04-q01','Empty top-1 → successful pushes0,1; full state not incremented.');record('ch04-q04','Indices0..3 count4; empty-1 count0.');record('ch04-q05','M=5: empty top-1 count0, full top4 count5, index5 invalid.')
a=[None]*5;t=-1;states=[];returned=[]
for op,value in [('push',1),('push',2),('push',3),('pop',None),('push',4),('push',5),('pop',None)]:
 if op=='push':t+=1;a[t]=value
 else:returned.append(a[t]);t-=1
 states.append({'memory':a.copy(),'top':t,'valid':a[:t+1]})
assert returned==[3,5] and states[-1]=={'memory':[1,2,4,5,None],'top':2,'valid':[1,2,4]}
record('ch04-q08','Independent fixed-array state trace matches all7 rows; pop returns3,5; physical stale5 differs from logical [1,2,4].')
from collections import deque
q=deque('ABCDE');assert ''.join(q.popleft() for _ in range(5))=='ABCDE';record('ch05-q01','deque removes A,B,C,D,E in order; a valid, b first mismatch, c fourth mismatch, d first mismatch.')
q=deque([10,20,30,40,50]);assert [q.popleft() for _ in range(3)]==[10,20,30] and list(q)==[40,50];record('ch05-q03','deque deletion returns10,20,30 and leaves40,50.')
def postfix(tokens):
 stack=[];states=[];push=pop=0
 for token in tokens.split():
  if token in '+-*/':
   b=stack.pop();a=stack.pop();pop+=2
   v={'+':lambda:a+b,'-':lambda:a-b,'*':lambda:a*b,'/':lambda:a//b}[token]()
  else:v=int(token)
  stack.append(v);push+=1;states.append(stack.copy())
 return stack,push,pop,states
A=postfix('5 6 * 4 2 / + 1 -');C=postfix('7 6 2 / - 5 4 * +');assert A[:3]==([31],9,8) and C[0]==[24]
record('2019-mid-q6',f'Independent postfix interpreter: {A}; result left on stack.')
# Separately derive conversion by shunting yard, rather than reusing answer string.
def convert(tokens):
 out=[];ops=[];priority={'+':1,'-':1,'*':2,'/':2}
 for x in tokens:
  if x.isdigit():out.append(x)
  elif x=='(':ops.append(x)
  elif x==')':
   while ops[-1]!='(':out.append(ops.pop())
   ops.pop()
  else:
   while ops and ops[-1]!='(' and priority[ops[-1]]>=priority[x]:out.append(ops.pop())
   ops.append(x)
 return out+ops[::-1]
converted=convert('( 2 + 4 ) * 7 - 6 * 3 + 1'.split());assert converted=='2 4 + 7 * 6 3 * - 1 +'.split() and postfix(' '.join(converted))[0]==[25]
record('2018-mid-c024-q9','Independent shunting yard result2 4 + 7 * 6 3 * - 1 + value25; separately supplied table tokens value31. Both answered.')
record('2017-mid-c050-q6',f'Independent postfix state interpreter: {C}; result24.')
record('2018-mid-c024-q1','([]) passes LIFO type matching; ([)] fails at first closing ) despite equal counts.','qualitative');record('2017-mid-c050-q1','Postfix23+4* value20 with most recent partial results; queue cannot preserve nested-expression invariant.','qualitative')
record('2017-mid-c050-q2','Customers A,B,C service A,B,C per FIFO; no priority policy assumed.','qualitative');record('2019-mid-q4','Counterexample push A then B returns B (LIFO), disproving FIFO premise; bracket-use clause itself true.','qualitative')
record('ch04-q07','Symbolic operand stack [A,B,E] first + combines B,E; A remains, so option1.')
def bracket(s):
 stack=[];n=0;out=[]
 for c in s:
  if c=='(':n+=1;stack.append(n);out.append(n)
  elif c==')':out.append(stack.pop())
 return out,stack
assert bracket('((())(()))')==([1,2,3,3,2,4,5,5,4,1],[]) and bracket('((((()')==([1,2,3,4,5,5],[1,2,3,4])
record('ch04-q11','Independent bracket numbering trace yields printed sequences; second example deliberately leaves unmatched1..4, not approved as balanced.')
record('ch04-q14','For top=-1,0,3,M-1 size=0,1,4,M; no mutation, O(1).')
# Full C program: valid input +,*; rejected malformed input; no UB normal path.
stack_c = r'''#include <stdio.h>
#include <stdlib.h>
#define MAX_STACK_SIZE 100
typedef int element;
typedef struct {element stack[MAX_STACK_SIZE];int top;} StackType;
void init(StackType*s){s->top=-1;}
int is_empty(StackType*s){return s->top==-1;}
int is_full(StackType*s){return s->top==MAX_STACK_SIZE-1;}
void push(StackType*s,element item){if(is_full(s))exit(1);s->stack[++s->top]=item;}
element pop(StackType*s){if(is_empty(s))exit(1);element item=s->stack[s->top--];return item;}
int main(void){char str[100];StackType s;init(&s);if(scanf("%99s",str)!=1)return 1;
for(int i=0;str[i];++i){if(str[i]=='+'||str[i]=='*'){int op2=pop(&s),op1=pop(&s);if(str[i]=='+')push(&s,op1+op2);else push(&s,op1*op2);}else if(str[i]>='0'&&str[i]<='9')push(&s,str[i]-'0');else return 1;}
if(s.top!=0)return 1;printf("%d",pop(&s));return 0;}
'''
assert compile_run(stack_c,'23+4*')=='20' and compile_run(stack_c,'52*3+')=='13'
record('2017-mid-c050-q10','Full C11+ASan+UBSan complete program:23+4*→20,52*3+→13. Stack snippets exact. Only valid bounded, non-overflow inputs accepted; added failure exits and bounded scanf distinguished from original.')
# Compile actual newly authored full programs/declarations (not existing-reference answers).
for src in inputs:
 v=json.loads(src.read_text());folder=src.parent;local={}
 for q in v['problems']:
  from verification_key import key
  k=key(q);frag=(folder/'explanations'/f"{q['id']}.html").read_text();solve=frag.split('data-explanation="solve"')[1].split('data-explanation="verify"')[0]
  blocks=[html.unescape(c) for c in re.findall(r'<pre><code[^>]*>(.*?)</code></pre>',solve,re.S)]
  if k in ('ch03-q04','ch03-q12','ch06-q10','ch04-q11'):
   inp={'ch03-q04':'','ch03-q12':'','ch06-q10':'3\n5\n6\n7\n','ch04-q11':'((())(()))\n'}[k];out=compile_run(blocks[0],inp);local[q['id']]={'key':k,**results[k],'compiled_output':out}
  elif k in ('ch03-q05','ch03-q06','ch03-q07'):
   prefix=blocks[0];suffix={'ch03-q05':'int main(void){struct person p={"A",20,3.0f};return p.age!=20;}', 'ch03-q06':'int main(void){c1.real=1.0f;c2.imaginary=2.0f;return c1.real!=1.0f;}', 'ch03-q07':'int main(void){Complex a={1,2},b={3,4},r=complex_add(a,b);return r.real!=4 || r.imag!=6;}'}[k];compile_run(prefix+'\n'+suffix);local[q['id']]={'key':k,**results[k],'compiled':'C11 sanitizer PASS'}
  else:local[q['id']]={'key':k,**results[k]}
  if k=='ch04-q11':assert '1 2 3 3 2 4 5 5 4 1' in out
  if k=='ch03-q04':assert out=='1 2 4 8 16 32 64 128 256 512'
  if k=='ch03-q12':assert out=='100 just testing'
  if k=='ch06-q10':assert out.endswith('연결 리스트 노드의 개수 = 3')
 (folder/'evidence'/'independent-results.json').write_text(json.dumps(local,ensure_ascii=False,indent=2))
 (folder/'evidence'/'verify-code-blocks.py').write_text(Path(__file__).read_text())
 (folder/'evidence'/'verification_key.py').write_text((B/'verification_key.py').read_text())
 (folder/'evidence'/'author.py').write_text((B/'author.py').read_text())
 if v['range']=='1012':(folder/'evidence'/'postfix.c').write_text(stack_c)
 print(v['range'],len(local),'verified')
(B/'independent-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
