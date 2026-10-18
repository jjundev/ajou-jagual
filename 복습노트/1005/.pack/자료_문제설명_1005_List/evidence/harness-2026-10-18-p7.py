link={'A':'B','B':'A'}; head='B'
def insert_last(node, update=True):
    global head
    if head is None: head=node; link[node]=node
    else:
        link[node]=link[head]; link[head]=node
        if update: head=node
insert_last('N'); print('head',head,'first',link[head],link)
link={'A':'B','B':'A'}; head='B'; insert_last('N',False); print('no-update head',head,'first',link[head],link)
