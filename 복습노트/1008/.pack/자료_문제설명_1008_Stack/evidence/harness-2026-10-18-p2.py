# length-1 list [A], pos=0, wrapper with removed=(p!=NULL)?p->link:NULL
link={'A':None}; head='A'; freed=[]; length=1
def get_node_at(pos):
    if pos<0: return None
    t=head
    for _ in range(pos): t=link[t]
    return t
def remove_node(p, removed):
    global head
    if p is None: head=link[head]
    else: link[p]=link[removed]
    freed.append(removed)
p=get_node_at(-1); remove_node(p, link[p] if p else None); length-=1
print('orig: head',head,'length',length,'freed',freed,'leaked A' if 'A' not in freed else 'ok')
link={'A':None}; head='A'; freed=[]; length=1
p=get_node_at(-1); remove_node(p, link[p] if p else head); length-=1
print('fixed: head',head,'length',length,'freed',freed)
