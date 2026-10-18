"""Independent logical models, not execution of submitted/lecture C implementations.
Qualitative proofs are recorded separately in independent.json reasoning fields.
"""
import json

def emit(name, result):
    print(name + ': ' + json.dumps(result, ensure_ascii=False))

def merge(a, b):
    i=j=0; out=[]; trace=[]
    while i<len(a) and j<len(b):
        ca,ea=a[i]; cb,eb=b[j]
        if ea>eb: term=a[i]; moved='p'; i+=1
        elif ea<eb: term=b[j]; moved='q'; j+=1
        else: term=(ca+cb,ea); moved='p,q'; i+=1; j+=1
        if term[0]: out.append(term)
        trace.append({'term':term if term[0] else None, 'moved':moved, 'i':i, 'j':j})
    out.extend(a[i:]); out.extend(b[j:])
    return out,trace

A=[None]*6; A[2]=7
assert len(A)==6 and A[2]==7
emit('array_adt', {'length':len(A),'retrieve_2':A[2]})
address=1000+(2*4+1)*4
assert address==1036 and 0<=2<3 and 0<=1<4
emit('row_major_address', address)

dense=[a+b for a,b in zip([8,0,7,1],[10,3,0,1])]
sparse,trace=merge([(8,3),(7,1),(1,0)],[(10,3),(3,2),(1,0)])
assert dense==[18,3,7,2] and sparse==[(18,3),(3,2),(7,1),(2,0)]
assert merge([(2,3)],[(-2,3)])[0]==[]
emit('polynomial_dense_sparse', {'dense':dense,'sparse':sparse,'trace':trace})

a=[10,20,30]; p=0; pp='p'; pointer_trace=[]
x=a[p]; p+=1; pointer_trace.append({'p_index':p,'a':a.copy(),'x':x})
y=a[p]; a[p]+=1; pointer_trace.append({'p_index':p,'a':a.copy(),'y':y})
assert pp=='p'; a[p]=40; pointer_trace.append({'p_index':p,'a':a.copy()})
assert (x,y,a,p)==(10,20,[10,40,30],1)
emit('double_pointer_logical_model',pointer_trace)

lst=[]; states=[]
lst.append('A'); states.append(lst.copy())
lst.append('B'); states.append(lst.copy())
lst.insert(2,'C'); states.append(lst.copy())
lst.insert(1,'D'); states.append(lst.copy())
del lst[2]; states.append(lst.copy())
lst[1]='E'; states.append(lst.copy())
assert states==[['A'],['A','B'],['A','B','C'],['A','D','B','C'],['A','D','C'],['A','E','C']]
assert lst[1]=='E' and len(lst)==3
emit('list_adt', [{'list':s,'length':len(s)} for s in states])

raw=[7,8,9]; length=0
assert raw==[7,8,9] and raw[:length]==[] and (length==0,length==3)==(True,False)
emit('array_list_initialization', {'raw':raw,'logical':raw[:length],'length':length,'empty':int(length==0),'full':int(length==3)})

links={300:100,100:500,500:None}; values={300:10,100:20,500:30}
cur=300; order=[]
while cur is not None: order.append(values[cur]); cur=links[cur]
assert order==[10,20,30]
emit('linked_address_order', order)
def splice(correct):
    links={'A':'C','C':None,'N':None}
    if correct: links['N']=links['A']; links['A']='N'
    else: links['A']='N'; links['N']=links['A']
    return links
assert splice(True)=={'A':'N','C':None,'N':'C'}
assert splice(False)=={'A':'N','C':None,'N':'N'}
emit('splice_order', {'correct':splice(True),'reversed_same_statements':splice(False)})

out,trace=merge([(3,12),(2,8),(1,0)],[(8,12),(-3,10),(10,6)])
assert out==[(11,12),(-3,10),(2,8),(10,6),(1,0)]
emit('linked_polynomial',{'out':out,'trace':trace,'remaining_A':[(1,0)]})

def adapter(position):
    nodes=['A','B','C']; prev=None if position==0 else nodes[position-1]
    nodes.insert(position,'N')
    return {'predecessor':prev,'args':['&(list->head)',prev,'node(N)'],'result':nodes,'length':len(nodes)}
assert adapter(2)['predecessor']=='B' and adapter(2)['result']==['A','B','N','C']
assert adapter(0)['predecessor'] is None and adapter(0)['result']==['N','A','B','C']
emit('position_adapter',{'pos2':adapter(2),'pos0':adapter(0)})

frames=['main(i=3)','sub1(a=3,j=5)','sub2(b=5)']; popped=[]; return_to=[]
while len(frames)>1:
    popped.append(frames.pop()); return_to.append(frames[-1].split('(')[0])
assert return_to==['sub1','main']
emit('activation_record_order',{'popped':popped,'return_to':return_to})

def guarded_push(storage,top,value):
    if top==len(storage)-1: return top,False
    top+=1; storage[top]=value
    return top,True
def guarded_pop(storage,top):
    if top==-1: return top,False,None
    value=storage[top]; top-=1
    return top,True,value
full=['A','B','C']; before=full.copy()
full_top,accepted=guarded_push(full,2,'N')
assert (full_top,accepted,full)==(2,False,before)
empty=[7,8,9]; before_empty=empty.copy()
empty_top,accepted,value=guarded_pop(empty,-1)
assert (empty_top,accepted,value,empty)==(-1,False,None,before_empty)
emit('stack_guards_before_mutation',{'full_push':{'top':full_top,'storage':full,'accepted':False},'empty_pop':{'top':empty_top,'storage':empty,'accepted':False}})
print('ALL INDEPENDENT LOGICAL ASSERTIONS PASSED')
