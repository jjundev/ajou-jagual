"""Deterministic, original vector drawings from explicitly transcribed structure."""
import json,math,argparse,re
from pathlib import Path
import xml.etree.ElementTree as ET
from source import file_sha256
NS='http://www.w3.org/2000/svg'
TAGS={'svg','g','title','desc','rect','circle','ellipse','line','path','polyline','polygon','text','tspan'}
ATTRS={'xmlns','viewBox','width','height','id','role','aria-label','x','y','x1','x2','y1','y2','cx','cy','r','rx','ry','d','points','fill','stroke','stroke-width','stroke-dasharray','font-family','font-size','font-weight','text-anchor','dominant-baseline','transform'}
def validate_svg(text):
    errors=[]
    if '<!DOCTYPE' in text or '<!ENTITY' in text: return ['XML declarations forbidden']
    try:root=ET.fromstring(text)
    except ET.ParseError as e:return [str(e)]
    if root.tag!='{'+NS+'}svg':errors.append('SVG namespace required')
    ids=[]
    for e in root.iter():
        if e.tag.split('}')[-1] not in TAGS:errors.append('forbidden tag '+e.tag)
        for k,v in e.attrib.items():
            if k not in ATTRS or '\\' in v or any(t in v.lower() for t in ('url(','javascript:','data:','http:','https:')):errors.append('forbidden attribute '+k)
        if 'id' in e.attrib:ids.append(e.attrib['id'])
        for k in ('fill','stroke'):
            if k in e.attrib and not re.fullmatch(r'(?:none|#[a-fA-F0-9]{3,8}|[a-zA-Z]+)',e.attrib[k]):errors.append('unsafe paint value')
    if len(ids)!=len(set(ids)):errors.append('duplicate SVG IDs')
    return errors

def validate_model(model):
    d=model['data'];kind=model['kind'];errors=[]
    try:
        if kind in ('tree','graph'):
            ids=[n['id'] for n in d['nodes']];assert len(ids)==len(set(ids)) and ids
            if kind=='tree':
                assert d['root'] in ids;parents=[];seen=set();nodes={n['id']:n for n in d['nodes']}
                def visit(n):
                    assert n not in seen;seen.add(n)
                    for side in ('left','right'):
                        child=nodes[n][side]
                        if child is not None:assert child in nodes;parents.append(child);visit(child)
                visit(d['root']);assert seen==set(ids) and len(parents)==len(set(parents))
            else:
                eids=[]
                for e in d['edges']:assert e['from'] in ids and e['to'] in ids and isinstance(e['directed'],bool);eids.append(e['id'])
                assert len(eids)==len(set(eids)) and not set(ids)&set(eids)
        elif kind=='array':
            ids=[c['index'] for c in d['cells']];assert len(ids)==len(set(ids)) and ids
            assert all(p['index'] in ids for p in d['pointers'])
        elif kind=='table':
            coverage=set()
            for c in d['cells']:
                assert c['rowspan']>0 and c['colspan']>0
                for r in range(c['row'],c['row']+c['rowspan']):
                    for col in range(c['col'],c['col']+c['colspan']):
                        assert 0<=r<d['rows'] and 0<=col<d['cols'] and (r,col) not in coverage;coverage.add((r,col))
            assert len(coverage)==d['rows']*d['cols']
        elif kind=='vector':
            assert all(p['tag'] in TAGS-{'svg','title','desc'} for p in d['primitives'])
        else:assert False
    except (AssertionError,KeyError,TypeError):errors.append('invalid '+kind+' structure')
    return errors

def svg_payload_text(text):
    return [e.text for e in ET.fromstring(text).iter() if e.tag.split('}')[-1] in ('text','tspan') and e.text]

def render_svg(model,alt):
    errors=validate_model(model)
    if errors:raise ValueError(errors)
    d=model['data'];layout=model['layout'];kind=model['kind'];W=layout.get('width',800);H=layout.get('height',420)
    root=ET.Element('svg',{'xmlns':NS,'viewBox':f'0 0 {W} {H}','role':'img','aria-label':alt});ET.SubElement(root,'title').text=alt
    def add(tag,attrs,parent=root,text=None):
        e=ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()});e.text=text;return e
    def label(x,y,text,parent=root,size=22):
        if text!='':add('text',{'x':x,'y':y,'text-anchor':'middle','dominant-baseline':'middle','font-family':'sans-serif','font-size':size,'fill':'#17212b'},parent,text)
    def edge(a,b,eid,arrow=False,curve=0,labeltext=''):
        group=add('g',{'id':eid});x1,y1=a;x2,y2=b
        if a==b:
            add('path',{'d':f'M {x1-15} {y1-20} C {x1-95} {y1-130}, {x1+95} {y1-130}, {x1+15} {y1-20}','fill':'none','stroke':'#26394a','stroke-width':2},group);tx,ty=x1+15,y1-20;angle=math.pi*.8;mx,my=x1,y1-90
        elif curve:
            mx=(x1+x2)/2;my=(y1+y2)/2;dx=x2-x1;dy=y2-y1;dist=max(1,math.hypot(dx,dy));cx=mx-dy/dist*curve;cy=my+dx/dist*curve
            add('path',{'d':f'M {x1} {y1} Q {cx} {cy} {x2} {y2}','fill':'none','stroke':'#26394a','stroke-width':2},group);angle=math.atan2(y2-cy,x2-cx);tx,ty=x2,y2;mx=(mx+cx)/2;my=(my+cy)/2
        else:
            add('line',{'x1':x1,'y1':y1,'x2':x2,'y2':y2,'stroke':'#26394a','stroke-width':2},group);angle=math.atan2(y2-y1,x2-x1);tx,ty=x2,y2;mx=(x1+x2)/2;my=(y1+y2)/2
        if arrow:
            tx-=28*math.cos(angle);ty-=28*math.sin(angle)
            pts=[(tx,ty),(tx-13*math.cos(angle-.45),ty-13*math.sin(angle-.45)),(tx-13*math.cos(angle+.45),ty-13*math.sin(angle+.45))]
            add('polygon',{'points':' '.join(f'{x},{y}' for x,y in pts),'fill':'#26394a'},group)
        if labeltext:
            lx,ly=layout.get('label_positions',{}).get(eid,[mx,my-12]);label(lx,ly,labeltext,group,19)
    if kind in ('tree','graph'):
        positions=layout.get('positions',{})
        if kind=='tree' and not positions:
            nodes={n['id']:n for n in d['nodes']}
            def place(n,x,y,gap):
                positions[n]=[x,y]
                for side,sign in [('left',-1),('right',1)]:
                    if nodes[n][side] is not None:place(nodes[n][side],x+gap*sign,y+85,gap/2)
            place(d['root'],W/2,45,W/4)
        elif not positions:
            for i,n in enumerate(d['nodes']):
                angle=2*math.pi*i/len(d['nodes'])-math.pi/2;positions[n['id']]=[W/2+min(W,H)*.35*math.cos(angle),H/2+min(W,H)*.35*math.sin(angle)]
        if kind=='tree':
            for n in d['nodes']:
                for side in ('left','right'):
                    if n[side] is not None:edge(positions[n['id']],positions[n[side]],'edge-'+n['id']+'-'+side)
        else:
            pair_counts={}
            for e in d['edges']:
                pair=tuple(sorted([e['from'],e['to']]));k=pair_counts.get(pair,0);pair_counts[pair]=k+1
                curve=layout.get('curves',{}).get(e['id'],k*65)
                text=e['label']+((' '+e['weight']) if e['weight'] is not None else '')
                edge(positions[e['from']],positions[e['to']],e['id'],e['directed'],curve,text)
        for n in d['nodes']:
            x,y=positions[n['id']];group=add('g',{'id':n['id']});add('circle',{'cx':x,'cy':y,'r':22,'fill':'#fff','stroke':'#26394a','stroke-width':2},group);label(x,y,n['label'],group)
    elif kind=='array':
        cells=d['cells'];cw=min(100,(W-80)/len(cells));x0=40;y=100
        for i,c in enumerate(cells):
            x=x0+i*cw;g=add('g',{'id':f"cell-{c['index']}"});add('rect',{'x':x,'y':y,'width':cw,'height':60,'fill':'#fff','stroke':'#26394a'},g);label(x+cw/2,y+30,c['value'],g)
            if layout.get('show_indices',True):label(x+cw/2,y-25,str(c['index']),g,18)
        for i,p in enumerate(d['pointers']):
            j=next(i for i,c in enumerate(cells) if c['index']==p['index']);x=x0+(j+.5)*cw;py=y+110+i*40
            add('line',{'x1':x,'y1':py-18,'x2':x,'y2':y+64,'stroke':'#26394a'});add('polygon',{'points':f'{x},{y+60} {x-6},{y+73} {x+6},{y+73}','fill':'#26394a'});label(x,py,p['label'],size=19)
    elif kind=='table':
        cw=layout.get('cell_width',(W-40)/d['cols']);ch=layout.get('cell_height',52)
        for c in d['cells']:
            x=20+c['col']*cw;y=20+c['row']*ch;w=cw*c['colspan'];h=ch*c['rowspan'];g=add('g',{'id':f"cell-{c['row']}-{c['col']}"});add('rect',{'x':x,'y':y,'width':w,'height':h,'fill':'#e8eef2' if c['header'] else '#fff','stroke':'#526575'},g)
            for i,line in enumerate(c['text'].split('\n')):label(x+w/2,y+h/2+(i-(len(c['text'].split('\n'))-1)/2)*24,line,g,layout.get('font_size',18))
    else:
        for p in d['primitives']:add(p['tag'],p['attrs'],text=p.get('text'))
    result=ET.tostring(root,encoding='unicode')+'\n'
    if validate_svg(result):raise ValueError(validate_svg(result))
    return result

def main(argv=None):
    from bank import bank_files,load_bank
    parser=argparse.ArgumentParser();parser.add_argument('--models',type=Path,required=True);parser.add_argument('--bank',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args(argv)
    models={m['id']:m for m in json.loads(args.models.read_text())['models']};bank=load_bank(args.bank);args.output.mkdir(exist_ok=True)
    for a in bank['assets']:
        if a['review']['status']=='verified':raise ValueError('cannot overwrite reviewed SVG')
        p=args.output/Path(a['path']).name;p.write_text(render_svg(models[a['model_id']],a['alt']));a['sha256']=file_sha256(p)
    updates={a['id']:a for a in bank['assets']}
    for path in bank_files(args.bank):
        part=json.loads(path.read_text());part['assets']=[updates[a['id']] for a in part['assets']]
        path.write_text(json.dumps(part,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
