"""Blind independent logical traces for the eight old 1005 questions."""
import json

def emit(name,value): print(name+': '+json.dumps(value,ensure_ascii=False))
def walk(links,head):
    out=[]
    while head is not None:
        assert head not in out, 'unexpected cycle'
        out.append(head); head=links[head]
    return out

links={'A':'B','B':'C','C':'D','D':None}; p='A'; visited=[p]
while links[p] is not None: p=links[p]; visited.append(p)
assert p=='D'; emit('p1',{'visited':visited,'p':p})
for n in [0,1,3,10]:
    links={i:i+1 if i+1<n else None for i in range(n)}
    count=0; p=0 if n else None
    while p is not None: count+=1; p=links[p]
    assert count==n
emit('p2',{'5_6_7_count':3,'tested_lengths':[0,1,3,10]})

links={'A':'B','B':None,'C':'D','D':None}; p='A'
while links[p] is not None:p=links[p]
links[p]='C'
assert walk(links,'A')==['A','B','C','D']; emit('p3',{'return':'A','links':links})

links={'A':'B','B':'C','C':None}; p='A'; q=None; trace=[]
while p is not None:
    r=q; q=p; p=links[p]; links[q]=r
    trace.append({'p':p,'q':q,'r':r,'reversed':walk(links,q)})
assert trace==[{'p':'B','q':'A','r':None,'reversed':['A']},{'p':'C','q':'B','r':'A','reversed':['B','A']},{'p':None,'q':'C','r':'B','reversed':['C','B','A']}]
emit('p4',trace)

def insert(head,p,links):
    links=links.copy()
    if head is None:links['N']=None; head='N'
    elif p is None:links['N']=head; head='N'
    else: links['N']=links[p]; links[p]='N'
    return head,links
cases=[]
for h,p,l,expected in [(None,None,{},['N']),('A',None,{'A':'B','B':None},['N','A','B']),('A','A',{'A':'B','B':None},['A','N','B'])]:
    h,l=insert(h,p,l); assert walk(l,h)==expected; cases.append({'head':h,'order':walk(l,h)})
emit('p5',cases)

cases=[]
for head,prev,removed,links,expected in [('A','A','B',{'A':'B','B':'C','C':None},['A','C']),('A',None,'A',{'A':'B','B':'C','C':None},['B','C']),('A',None,'A',{'A':None},[])]:
    if prev is None:head=links[head]
    else:links[prev]=links[removed]
    del links[removed]
    assert walk(links,head)==expected; cases.append({'head':head,'order':expected})
emit('p6',cases)

links={'A':'B','B':'A'}; head='B'
links['N']=links[head]; links[head]='N'; head='N'
assert links=={'A':'B','B':'N','N':'A'} and links[head]=='A'
emit('p7',{'head':head,'first':links[head],'links':links,'omit_tail_update_first':'N','omit_tail_update_order':['N','A','B']})

left={'A':'B','B':'A'}; right={'A':'B','B':'A'}; before='A'
left['N']=before;right['N']=right[before];left[right[before]]='N';right[before]='N'
assert left['N']=='A' and right['N']=='B' and left['B']=='N' and right['A']=='N'
emit('p8_insert',{'left':left.copy(),'right':right.copy()})
right[left['N']]=right['N'];left[right['N']]=left['N']
assert right['A']=='B' and left['B']=='A'
bad_left={'A':'B','B':'A'};bad_right={'A':'B','B':'A'}
bad_left['N']='A';bad_right['N']=bad_right['A'];bad_right['A']='N';bad_left[bad_right['A']]='N'
assert bad_left['N']=='N' and bad_left['B']=='A'
emit('p8_reverse_last_two',{'left':bad_left,'right':bad_right})
print('ALL 8 INDEPENDENT EXISTING-1005 LOGICAL CHECKS PASSED')
