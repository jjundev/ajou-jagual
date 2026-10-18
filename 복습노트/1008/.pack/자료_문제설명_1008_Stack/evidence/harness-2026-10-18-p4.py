def run(position):
    link={'A':'B','B':'C','C':None}; st={'head':'A','length':3}
    def get_node_at(pos):
        if pos<0: return None
        t=st['head']
        for _ in range(pos): t=link[t]
        return t
    def insert_node(p,new):
        if st['head'] is None: link[new]=None; st['head']=new
        elif p is None: link[new]=st['head']; st['head']=new
        else: link[new]=link[p]; link[p]=new
    p=get_node_at(position-1); insert_node(p,'N'); st['length']+=1
    out=[];t=st['head']
    while t: out.append(t); t=link[t]
    return p,out,st['length']
print('pos2',run(2)); print('pos0',run(0)); print('bug pos2 uses get_node_at(2)->C so after C')
