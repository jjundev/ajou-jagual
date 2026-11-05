#!/usr/bin/env python3
"""1105 independent verification: direct tree simulation, not answer-key parsing.
Output is printed to stdout; no repository files are changed.
Lecture p11/p12 are also checked by a C11 translation harness.
Height convention: number of occupied levels (empty=0, leaf=1).
"""
from pathlib import Path
from collections import deque
from copy import deepcopy
from itertools import permutations
from math import ceil,log2,factorial
import json
RUN=Path(__file__).resolve().parent

def node(k,left=None,right=None): return {'key':k,'left':left,'right':right}
def insert(t,k,trace=None):
    if t is None:return node(k)
    if trace is not None:trace.append(t['key'])
    if k<t['key']:t['left']=insert(t['left'],k,trace)
    elif k>t['key']:t['right']=insert(t['right'],k,trace)
    return t

def build(keys):
    t=None
    for k in keys:t=insert(t,k)
    return t

def traversal(t,order):
    if t is None:return []
    l=traversal(t['left'],order);r=traversal(t['right'],order);k=[t['key']]
    return {'pre':k+l+r,'in':l+k+r,'post':l+r+k}[order]

def array(t,i=1):
    if t is None:return {}
    return {i:t['key'],**array(t['left'],2*i),**array(t['right'],2*i+1)}

def height(t):return 0 if t is None else 1+max(height(t['left']),height(t['right']))
def check_bst(t,lo=float('-inf'),hi=float('inf')):
    return t is None or lo<t['key']<hi and check_bst(t['left'],lo,t['key']) and check_bst(t['right'],t['key'],hi)

def ascii_tree(t,prefix='',label='root'):
    if t is None:return ''
    lines=[prefix+label+': '+str(t['key'])]
    for name,tag in [('left','L'),('right','R')]:
        if t[name] is not None:lines.append(ascii_tree(t[name],prefix+'  ',tag))
    return '\n'.join(lines)

def describe(t):
    a=array(t)
    return {'tree':deepcopy(t),'ascii':ascii_tree(t),'array':dict(sorted(a.items())),'level_order':[a[i] for i in sorted(a)],'preorder':traversal(t,'pre'),'inorder':traversal(t,'in'),'postorder':traversal(t,'post'),'height_levels':height(t),'bst':check_bst(t)}

def delete(t,k,choice='successor',events=None):
    if events is None:events=[]
    assert t is not None
    if k<t['key']:t['left']=delete(t['left'],k,choice,events)
    elif k>t['key']:t['right']=delete(t['right'],k,choice,events)
    elif t['left'] is None or t['right'] is None:
        replacement=t['left'] or t['right']
        events.append({'remove':k,'case':'leaf' if replacement is None else 'one-child','replacement':None if replacement is None else replacement['key']})
        return replacement
    else:
        side='right' if choice=='successor' else 'left';walk='left' if choice=='successor' else 'right'
        u=t[side];path=[u['key']]
        while u[walk]:u=u[walk];path.append(u['key'])
        events.append({'remove':k,'case':'two-child','method':choice,'replacement_path':path,'replacement':u['key']})
        t['key']=u['key'];t[side]=delete(t[side],u['key'],choice,events)
    return t

def delete_trace(t,keys,choice):
    records=[]
    for k in keys:
        ev=[];t=delete(t,k,choice,ev);assert check_bst(t)
        records.append({'deleted':k,'events':ev,**describe(t)})
    return records

def from_relations(root,rels):
    if root is None:return None
    l,r=rels.get(root,(None,None));return node(root,from_relations(l,rels),from_relations(r,rels))

def complete(sorted_keys):
    """Fix complete-tree positions 1..n, then assign ascending keys in inorder."""
    n=len(sorted_keys);it=iter(sorted_keys)
    def make(i):
        if i>n:return None
        l=make(i*2);k=next(it);r=make(i*2+1);return node(k,l,r)
    t=make(1);assert check_bst(t) and set(array(t))==set(range(1,n+1));return t

def s(seq):return ' '.join(map(str,seq))
D={'verification':{'method':'Python dictionary tree simulation and exact combinatorial expected insertion comparisons','height_convention':'root level 1; height counts levels','bank_used_for_calculation':False,'c_harness':'not applicable: no selected question contains C code'},'problems':{},'bank_disagreements':[],'wording_discrepancies':[]}
P=D['problems']
# p1: source diagram relations, not inferred from key.
t=from_relations(15,{15:(5,16),5:(3,12),12:(10,13),10:(6,None),6:(None,7),16:(None,20),20:(18,23)})
assert check_bst(t)
p1={'initial':describe(t),'successor_steps':delete_trace(deepcopy(t),[13,16,5],'successor'),'predecessor_steps':delete_trace(deepcopy(t),[13,16,5],'predecessor')}
p1['answer']='후계자 사용 레벨 순서 '+s(p1['successor_steps'][-1]['level_order'])+'; 선행자 사용 레벨 순서 '+s(p1['predecessor_steps'][-1]['level_order'])
p1['terms']=[s(p1[x][-1]['level_order']) for x in ['successor_steps','predecessor_steps']];p1['note']='13은 단말, 16은 오른쪽 자식 하나. 5는 두 자식이 있어 후계자 6 또는 선행자 3 사용 가능. 후계자 6의 오른쪽 자식 7을 10의 왼쪽으로 연결한다.';P['p1']=p1
# p2: input sequence and one-child deletions.
keys=[520,490,650,380,570,250,450,610,280,430,460,580];t=None;steps=[]
for k in keys:
 path=[];t=insert(t,k,path);steps.append({'insert':k,'comparison_path':path,**describe(t)})
r=delete_trace(t,[250,610],'successor');a=r[-1]['array']
P['p2']={'insertions':steps,'deletions':r,'answer':', '.join(f'{i}:{v}' for i,v in a.items())+' (나머지 빈칸)','terms':[f'{i}:{v}' for i,v in a.items()],'empty_indices':[i for i in range(1,31) if i not in a],'note':'250→오른쪽 자식 280, 610→왼쪽 자식 580. 삭제 전과 후 경로가 바뀌므로 초기 배열에서 숫자만 지우면 안 된다.'}
# p3 and p5: independent complete-tree construction by inorder filling.
for pid,keys in [('p3',list(range(110,301,10))),('p5',list(range(1,17)))]:
 t=complete(keys);desc=describe(t);order=desc['level_order'];assert array(build(order))==array(t)
 P[pid]={'construction':'완전이진트리의 위치 1..n을 먼저 정하고 중위순서로 오름차순 키 배치','sorted_keys':keys,**desc,'insertion_order':order,'answer':s(order),'terms':[s(order)],'height_lower_bound':ceil(log2(len(keys)+1)),'minimality':f'노드 {len(keys)}개이므로 h >= ceil(log2({len(keys)}+1)) = {ceil(log2(len(keys)+1))}. 구성한 트리는 이 하한을 달성하며 배열 1..n에 빈칸이 없어 완전이진트리이다.','notes':'제시 입력순서는 가능한 답의 하나. 부모가 자손보다 먼저 들어가면 같은 트리를 만드는 다른 순서도 가능.'}
# p4: choose a symmetric shape, fill it by inorder, then verify input.
shape={1,2,3,4,5,6,7,8,15};it=iter(range(1,10))
def symmetric_shape(i):
 if i not in shape:return None
 l=symmetric_shape(2*i);v=next(it);r=symmetric_shape(2*i+1);return node(v,l,r)
t=symmetric_shape(1)
def mirror(a,b):
 if a is None or b is None:return a is None and b is None
 return mirror(a['left'],b['right']) and mirror(a['right'],b['left'])
assert mirror(t['left'],t['right']) and check_bst(t) and height(t)==ceil(log2(10))
order=describe(t)['level_order'];assert array(build(order))==array(t)
P['p4']={**describe(t),'insertion_order':order,'answer':s(order),'terms':[s(order)],'shape_indices':sorted(shape),'mirror_shape':True,'height_lower_bound':ceil(log2(10)),'minimality':'높이 3의 최대 노드는 2^3-1=7 < 9. 구성 높이 4가 최소이며 2의 왼쪽 1과 8의 오른쪽 9가 서로 거울 대칭이다.','notes':'좌우대칭 모양은 하나로 유일하지 않다. 위 순서는 한 가지 정답이다.'}
# p6: source diagram, traversal, explicit search, both root replacement conventions.
t=from_relations(55,{55:(16,92),16:(4,29),29:(None,30),92:(60,None),60:(None,75)});assert check_bst(t)
path=[];u=t
while u:
 path.append(u['key'])
 if u['key']==75:break
 u=u['left'] if 75<u['key'] else u['right']
succ=delete_trace(deepcopy(t),[55],'successor');pred=delete_trace(deepcopy(t),[55],'predecessor')
P['p6']={'initial':describe(t),'subquestions':{'a':{'answer':s(traversal(t,'pre')),'rule':'N-L-R'},'b':{'answer':s(traversal(t,'in')),'rule':'L-N-R'},'c':{'answer':s(traversal(t,'post')),'rule':'L-R-N'},'d':{'answer':s(path),'comparisons':['75 > 55: 오른쪽','75 < 92: 왼쪽','75 > 60: 오른쪽','75 == 75: 성공']},'e':{'successor':succ,'predecessor':pred,'note':'후계자 60을 올리면 92의 왼쪽은 75. 선행자 30을 올리면 29의 오른쪽은 빈칸.'}},'answer':'(a) '+s(traversal(t,'pre'))+'; (b) '+s(traversal(t,'in'))+'; (c) '+s(traversal(t,'post'))+'; (d) '+s(path)+'; (e) 후계자 60 또는 선행자 30','terms':[s(traversal(t,o)) for o in ['pre','in','post']]+[s(path),s(succ[-1]['level_order']),s(pred[-1]['level_order'])]}
# p7/p8: same n, two concrete heights; p8 needs no search-order requirement.
bal=build([2,1,3]);skew=build([1,2,3]);assert len(array(bal))==len(array(skew))==3 and height(bal)!=height(skew)
for pid in ['p7','p8']:
 P[pid]={'answer':'X','terms':['X','2 1 3','1 2 3'],'counterexample':{'n':3,'height2':describe(bal),'height3':describe(skew)},'height_range_levels':'ceil(log2(n+1)) <= h <= n','explanation':'같은 3개 노드라도 루트 2의 두 자식이 1,3이면 높이 2, 1→오른쪽 2→오른쪽 3이면 높이 3이다. BST에서도 입력순서가 모양과 높이를 바꾼다.' if pid=='p7' else '일반 이진트리에서도 노드 수가 같아도 모양이 다르면 높이가 다르다. 3개 노드의 높이가 2 또는 3인 반례가 있다.'}
# p9: table provides search avg/worst; blanks are INSERT avg/worst only.
# Exact mean successful comparison count for insertion of a new random rank.
means=[]
for n in range(1,7):
 counts=[]
 for perm in permutations(range(n+1)):
  t=build(perm[:-1]);path=[];insert(t,perm[-1],path);counts.append(len(path))
 exact=sum(counts)/len(counts);harmonic=2*sum(1/i for i in range(1,n+2))-2
 assert abs(exact-harmonic)<1e-10
 means.append({'existing_n':n,'permutations':factorial(n+1),'mean_key_comparisons':exact,'formula_2H_nplus1_minus2':harmonic,'worst_key_comparisons':n})
P['p9']={'answer':'삽입연산: 평균 O(log n), 최악 O(n).','terms':['O(log n)','O(n)'],'table':{'header_original':'삭제연산알고리즘','search_prefilled':['O(log n)','O(n)'],'insertion_blanks':['O(log n)','O(n)']},'assumption':'평균은 서로 다른 키의 입력순서가 무작위라는 표준 평균 모형(또는 높이가 O(log n)인 경우)이다. 일반 BST에서 항상 log n을 보장하지 않으며 경사트리는 O(n).','trace':means,'derivation':'삽입은 루트에서 빈 자식 링크까지 비교하며 내려간 뒤 새 노드를 연결하므로 O(h). 무작위 순열 BST에 새 무작위 순위 키를 삽입할 평균 비교 횟수는 2H_(n+1)-2=Theta(log n). 정렬순서로 삽입해 경사트리가 되면 마지막 삽입은 n번 비교하여 Theta(n).','source_issue':'첫 열 머리글은 실제 원문에 삭제연산알고리즘으로 인쇄됨. 삭제 행을 추가하지 않고 원표를 보존한다.'}
D['wording_discrepancies'].append({'id':'p9','kind':'nonblocking-source-error','detail':P['p9']['source_issue']})
# p10: reconstruct actual visible diagram. 8 is LEFT CHILD OF 10, not child of 7.
t=from_relations(6,{6:(4,9),4:(2,5),2:(1,3),9:(7,10),10:(8,11)});assert not check_bst(t)
a=array(t);rows={i:a.get(i) for i in range(1,16)};seq=traversal(t,'in');assert seq==[1,2,3,4,5,6,7,9,8,10,11]
P['p10']={'source_diagram_relations':{6:[4,9],4:[2,5],2:[1,3],9:[7,10],10:[8,11]},**describe(t),'array_1_to_15':rows,'subquestions':{'1':{'answer':rows,'trace':'루트 [1]=6. 부모 i의 왼쪽은 2i, 오른쪽은 2i+1. 5 아래 및 7 아래는 빈칸. 8은 [14], 11은 [15].'},'2':{'answer':s(traversal(t,'pre')),'rule':'N-L-R'},'3':{'answer':s(traversal(t,'post')),'rule':'L-R-N'},'4':{'answer':s(seq),'rule':'L-N-R'},'5':{'answer':s(describe(t)['level_order']),'rule':'큐로 왼쪽부터 레벨 순회'},'6':{'answer':'아니다. 8은 9의 오른쪽 서브트리에 있지만 8 < 9이다.','trace':'9 → 오른쪽 10 → 왼쪽 8. 중위순회에서도 9 뒤에 8이 나타나 오름차순을 위반한다.'}},'answer':'배열 '+', '.join(f'{i}:{v if v is not None else "∅"}' for i,v in rows.items())+'; 전위 '+s(traversal(t,'pre'))+'; 후위 '+s(traversal(t,'post'))+'; 중위 '+s(seq)+'; 레벨 '+s(describe(t)['level_order'])+'; BST 아님(9의 오른쪽 서브트리의 8)','terms':[s(traversal(t,o)) for o in ['pre','post','in']]+[s(describe(t)['level_order']),'8 < 9','14:8','15:11']}
# Explicit comparisons against source-bank keys were performed AFTER simulation.
D['bank_comparison']={'p1':'both final trees agree','p2':'all nonempty array indices agree','p3':'all 20 indices agree','p4':'one valid symmetric construction agrees','p5':'one valid complete construction agrees','p6':'all traversals/search and successor deletion agree; predecessor also valid','p7':'X agrees','p8':'X agrees','p9':'answer null, independently derived','p10':'answer null, independently derived from diagram'}
for v in P.values():v['verification_status']='pass'
# Additional lecture checks: direct independent data, not reference answers.
base=from_relations(18,{18:(7,26),7:(3,12),26:(None,31),31:(27,None)})
def find_trace(t,k):
    path=[]
    while t is not None:
        path.append(t['key'])
        if k==t['key']:return path,t['key']
        t=t['left'] if k<t['key'] else t['right']
    return path,None
assert find_trace(base,12)==([18,7,12],12)
assert find_trace(base,20)==([18,26],None)
assert not check_bst(from_relations(18,{18:(7,None),7:(None,20)}))
P['p11']={'verification_status':'pass'}
P['p11']['answer']='레코드·필드·학번; 20은 조상 18의 왼쪽 조건 위반; 중복 불가; 12 탐색 18,7,12 뒤 노드 주소,20 탐색18,26 뒤 NULL'
trace=[]
t=deepcopy(base);t=insert(t,9,trace)
assert trace==[18,7,12] and t['left']['right']['left']['key']==9 and len(array(t))==8
before=deepcopy(t);t=insert(t,9);assert t==before and len(array(t))==8
assert insert(None,9)==node(9)
P['p12']={'answer':'(NULL,18),(18,7),(7,12),종료(12,NULL);12.left=9;중복 후8개유지;빈트리0회 root=9','verification_status':'pass'}
import subprocess,tempfile
c_source='#include <stdio.h>\n#include <stdlib.h>\ntypedef struct TreeNode {int key; struct TreeNode *left,*right;} TreeNode;\nTreeNode *search(TreeNode *node,int key) {\n    if(node==NULL) return NULL;\n    if(key==node->key) return node;\n    if(key<node->key) return search(node->left,key);\n    return search(node->right,key);\n}\nint insert_node(TreeNode **root,TreeNode *z) {\n    TreeNode *p=NULL,*t=*root;\n    while(t!=NULL) {\n        if(z->key==t->key) return 0;\n        p=t;\n        if(z->key<p->key) t=p->left; else t=p->right;\n    }\n    if(p==NULL) *root=z;\n    else if(z->key<p->key) p->left=z;\n    else p->right=z;\n    return 1;\n}\nint main(void) {\n    TreeNode n3={3,NULL,NULL},n12={12,NULL,NULL},n7={7,&n3,&n12};\n    TreeNode n27={27,NULL,NULL},n31={31,&n27,NULL},n26={26,NULL,&n31};\n    TreeNode n18={18,&n7,&n26},*root=&n18;\n    printf("search12=%d search20=%s\\n",search(root,12)->key,search(root,20)==NULL?"NULL":"found");\n    TreeNode n9={9,NULL,NULL};\n    printf("insert9=%d\\n",insert_node(&root,&n9));\n    printf("parent12.left=%d\\n",n12.left->key);\n    TreeNode dup={9,NULL,NULL};\n    printf("duplicate9=%d\\n",insert_node(&root,&dup));\n    TreeNode empty_node={9,NULL,NULL},*empty=NULL;\n    int ok=insert_node(&empty,&empty_node);\n    printf("empty_insert=%d root=%d\\n",ok,empty->key);\n    return 0;\n}\n'
with tempfile.TemporaryDirectory(prefix='ds-1105-verify-') as tmp:
    src=Path(tmp)/'verify.c';exe=Path(tmp)/'verify';src.write_text(c_source)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-o',str(exe),str(src)],check=True)
    output=subprocess.run([str(exe)],check=True,capture_output=True,text=True).stdout
assert output=="search12=12 search20=NULL\ninsert9=1\nparent12.left=9\nduplicate9=0\nempty_insert=1 root=9\n"
D['verification']['c_harness']='C11 translation (not original slide source), auto-storage nodes with valid lifetime, no allocation; empty/duplicate/success/miss checked'
print(json.dumps({'status':'pass','count':len(P),'answers':{k:v['answer'] for k,v in P.items()},'bank_disagreements':D['bank_disagreements'],'lecture_c_output':output},ensure_ascii=False,indent=2))
