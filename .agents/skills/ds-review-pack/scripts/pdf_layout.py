"""Measure common question/answer slices; never shrink the frozen CSS."""
import copy
import html
from pathlib import Path
from pdf_types import Block, PageSlice, PdfError
from pdf_cards import to_payload
from pdf_render import probe, render_session


def units(blocks):
    out=[]
    for index,b in enumerate(blocks):
        if b.kind=='code':
            lines=b.text.splitlines(keepends=True) or ['']
            out.extend((index,Block('code','<pre><code>'+html.escape(line)+'</code></pre>',line)) for line in lines)
        else:out.append((index,b))
    return out


def regroup(items):
    out=[];last=None
    for origin,b in items:
        if b.kind=='code' and last==origin and out and out[-1].kind=='code':
            text=out[-1].text+b.text;out[-1]=Block('code','<pre><code>'+html.escape(text)+'</code></pre>',text)
        else:out.append(b)
        last=origin
    return tuple(out)


def check_coverage(pack,pages):
    errors=[]
    ids=[p.logical_id for p in pages]
    if list(dict.fromkeys(ids))!=[c.id for c in pack.cards]:errors.append('Logical order/coverage mismatch')
    if len({p.physical_id for p in pages})!=len(pages):errors.append('Duplicate physical ID')
    for c in pack.cards:
        parts=[p for p in pages if p.logical_id==c.id]
        if not parts:errors.append(c.id+': missing');continue
        for name in ('problem','solution'):
            expected=units(getattr(c,name));actual=units(tuple(b for p in parts for b in getattr(p,name)))
            # Line-exact text and HTML for every non-code block, including SVG/table.
            e=[(b.kind,b.text,b.html if b.kind!='code' else '') for _,b in expected]
            a=[(b.kind,b.text,b.html if b.kind!='code' else '') for _,b in actual]
            if e!=a:errors.append(f'{c.id}: {name} blocks/lines changed')
        if [p.continuation for p in parts]!=list(range(1,len(parts)+1)):errors.append(c.id+': continuation order')
        if [p.show_answer for p in parts]!=[False]*(len(parts)-1)+[True]:errors.append(c.id+': answer placement')
        if [p.show_hint for p in parts]!=[True]+[False]*(len(parts)-1):errors.append(c.id+': hint placement')
    return errors


def plan_pages(pack,run: Path):
    run=Path(run);run.mkdir(parents=True,exist_ok=True);pages=[]
    with render_session():
        for c in pack.cards:
            questions=units(c.problem);solutions=units(c.solution);qi=si=0;continuation=1
            cache={}
            def make(qn,sn,last=True):
                pid=c.id if continuation==1 else f'{c.id}-c{continuation}'
                return PageSlice(c.id,pid,continuation,regroup(questions[qi:qi+qn]),regroup(solutions[si:si+sn]),last,continuation==1)
            def fits(qn,sn):
                key=(qi,si,qn,sn,continuation)
                if key in cache:return cache[key]
                p=make(qn,sn)
                for mode in ('problems','answers'):
                    data=to_payload(pack,mode,(p,),run/'assets')
                    a4=probe(data,mode,'a4',run/'probe-a4')
                    if a4.errors:raise PdfError(c.id+': '+ '; '.join(a4.errors))
                    video=copy.deepcopy(data);video['meta']['typography']=a4.typography
                    result=probe(video,mode,'video-16x9',run/'probe-video')
                    if result.errors:raise PdfError(c.id+': '+ '; '.join(result.errors))
                    if result.overflow:cache[key]=False;return False
                cache[key]=True;return True
            while qi<len(questions) or si<len(solutions):
                if continuation>128:raise PdfError(c.id+': pagination exceeded 128 pages')
                qleft=len(questions)-qi;sleft=len(solutions)-si
                if fits(qleft,sleft):qn,sn=qleft,sleft
                else:
                    def longest(limit,check):
                        low=0;high=limit
                        while low<high:
                            mid=(low+high+1)//2
                            if check(mid):low=mid
                            else:high=mid-1
                        return low
                    qn=longest(qleft,lambda n:fits(n,0))
                    sn=longest(sleft,lambda n:fits(qn,n))
                    if qn+sn==0:
                        raise PdfError(c.id+': unbreakable problem/solution line, table, figure or hint overflow')
                last=qi+qn==len(questions) and si+sn==len(solutions)
                pages.append(make(qn,sn,last));qi+=qn;si+=sn;continuation+=1
    errors=check_coverage(pack,tuple(pages))
    if errors:raise PdfError('; '.join(errors))
    return tuple(pages)
