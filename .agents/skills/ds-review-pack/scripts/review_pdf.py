#!/usr/bin/env python3
"""Staged PDF export: build/check/publish/backfill, with independent review."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys
import unicodedata
import uuid
from pdf_cards import read_pack,to_payload,digest
from pdf_types import Block,PageSlice,PdfError
from pdf_layout import plan_pages,check_coverage
from pdf_render import render,render_session,ASSETS
from pdf_publish import dump,stage_hashes,publish_stage
from pdf_ds_layout import extension_hash,check_extension


def discover_reviews(repo,target):
    repo=Path(repo).resolve();found=[]
    pattern=re.compile(r'복습문제_(\d{4}(?:-\d{4})?)_(.+)\.html$')
    for path in repo.rglob('*.html'):
        rel=path.relative_to(repo)
        if unicodedata.normalize('NFC',rel.parts[0])!='복습노트':continue
        m=pattern.fullmatch(unicodedata.normalize('NFC',path.name))
        if not m:continue
        if target=='all' or m[1]==target:found.append(path)
    groups={}
    for path in found:groups.setdefault(path.parent,[]).append(path)
    if any(len(v)>1 for v in groups.values()):raise PdfError('자료_PDF report collision: multiple reviews in same folder')
    return tuple(sorted(found,key=lambda p:unicodedata.normalize('NFC',str(p))))


def _pages(value):
    return tuple(PageSlice(v['logical_id'],v['physical_id'],v['continuation'],
              tuple(Block(**b) for b in v['problem']),tuple(Block(**b) for b in v['solution']),v['show_answer'],v['show_hint']) for v in value)


def check_stage(run):
    import fitz
    run=Path(run);r=json.loads((run/'report.json').read_text());errors=[]
    if r['status']=='skipped':return []
    if r.get('failure'):return [r['failure']]
    if not Path(r['source']).is_file() or digest(r['source'])!=r['source_sha256']:errors.append('Source changed')
    if 'layout_extension_sha256' in r:
        try:check_extension(r)
        except PdfError as exc:errors.append(str(exc))
    pack=read_pack(Path(r['source']));pages=_pages(r['page_slices']);errors.extend(check_coverage(pack,pages))
    for name,sha in r['template_hashes'].items():
        if digest(ASSETS/'ec2'/name)!=sha:errors.append('Template changed: '+name)
    for name,sha in r.get('input_assets',{}).items():
        if not Path(name).is_file() or digest(name)!=sha:errors.append('Input asset changed: '+name)
    if r['artifact_hashes']!=stage_hashes(run):errors.append('Stage artifact hashes changed')
    for mode,result in r['probes'].items():
        errors.extend(result['errors']);errors.extend('Overflow: '+pid for pid in result['overflow'])
        pdf=run/'stage'/r['pdfs'][0 if mode=='problems' else 1]
        with fitz.open(pdf) as doc:
            if len(doc)!=len(result['page_ids']):errors.append(mode+': PDF page count differs from DOM')
            for p in doc:
                if abs(p.rect.width-1440)>.5 or abs(p.rect.height-810)>.5:errors.append(mode+': incorrect MediaBox')
                if not p.get_text().strip():errors.append(mode+': empty PDF page')
            # Check source C tokens in final PDF, independently of payload completeness.
            final=''.join(p.get_text() for p in doc);compact=re.sub(r'\s+','',final)
            blocks=[b for p in pages for b in p.problem+(p.solution if mode=='answers' else ()) if b.kind=='code']
            for b in blocks:
                for line in b.text.splitlines():
                    token=re.sub(r'\s+','',line)
                    if token and token not in compact:errors.append(mode+': code line missing: '+line[:100])
    return list(dict.fromkeys(errors))


def failure_status(source):
    source=Path(source)
    return 'stale' if any((source.parent/(source.stem+suffix)).exists()
                          for suffix in ('-문제.pdf','-답안.pdf')) else 'withheld'


def build_pack(review,run):
    run=Path(run).resolve()
    if run.exists() and any(run.iterdir()):raise PdfError('RUN must be fresh/empty')
    run.mkdir(parents=True,exist_ok=True);stage=run/'stage';stage.mkdir()
    source=Path(review).resolve()
    try:
        pack=read_pack(source)
    except (PdfError,OSError,ValueError) as exc:
        report={'version':1,'source':str(source),'dest':str(source.parent),
                'source_sha256':digest(source) if source.is_file() else None,
                'status':failure_status(source),
                'failure':str(exc),'checks':{'status':'fail','errors':[str(exc)]},'artifact_hashes':{}}
        dump(run/'report.json',report);dump(run/'review.json',{'status':'not_run'})
        return run/'report.json'
    report={'version':1,'source':str(pack.source),'source_sha256':pack.source_sha256,
       'dest':str(pack.source.parent),'range':pack.range,'slug':pack.slug,'logical_ids':[c.id for c in pack.cards],
       'template_hashes':{p.name:digest(p) for p in (ASSETS/'ec2').iterdir() if p.is_file()},
       'vendor_hashes':{str(p.relative_to(ASSETS)):digest(p) for p in (ASSETS/'vendor').rglob('*') if p.is_file()},
       'layout_extension_sha256':extension_hash(),
       'browser':{'status':'not_run'},'status':'staged','probes':{},'input_assets':{}}
    if not pack.cards:
        report.update(status='skipped',checks={'status':'pass','errors':[]},pdfs=[],artifact_hashes={})
        dump(run/'report.json',report);return run/'report.json'
    try:
        # Track external local source images, as well as inline figure coverage.
        from html2md import Builder
        from urllib.parse import unquote,urlparse
        builder=Builder();builder.feed(pack.source.read_text())
        for img in builder.root.find_all(lambda n:n.tag=='img'):
            src=img.attrs.get('src','');url=urlparse(src)
            if not url.scheme:
                path=(pack.source.parent/unquote(url.path)).resolve();report['input_assets'][str(path)]=digest(path)
        with render_session():
            pages=plan_pages(pack,run/'layout');report['page_slices']=[asdict(p) for p in pages]
            report['coverage']={'status':'pass','errors':check_coverage(pack,pages)}
            report['pdfs']=[pack.source.stem+'-문제.pdf',pack.source.stem+'-답안.pdf']
            for mode,name in zip(('problems','answers'),report['pdfs']):
                data=to_payload(pack,mode,pages,stage/'assets');dump(stage/f'{mode}.json',data)
                result=render(data,mode,run/mode,stage/name);report['probes'][mode]=asdict(result)
                if result.errors or result.overflow:raise PdfError(mode+': '+str(result.errors or result.overflow))
                import fitz
                with fitz.open(stage/name) as doc:
                    for index,page in enumerate(doc):
                        png=stage/'pages'/mode/f'{index+1:03}.png';png.parent.mkdir(parents=True,exist_ok=True)
                        page.get_pixmap(matrix=fitz.Matrix(2/3,2/3)).save(png)
            report['artifact_hashes']=stage_hashes(run);report['checks']={'status':'not_run','errors':[]};dump(run/'report.json',report)
            errors=check_stage(run);report['checks']={'status':'fail' if errors else 'pass','errors':errors}
            if errors:report['status']=failure_status(pack.source)
    except (PdfError,OSError,ValueError) as exc:
        report.update(status=failure_status(pack.source),failure=str(exc),checks={'status':'fail','errors':[str(exc)]},artifact_hashes=stage_hashes(run))
    dump(run/'report.json',report);dump(run/'review.json',{'status':'not_run','reviewer':'','evidence':'','artifact_hashes':report.get('artifact_hashes',{}),'report_sha256':digest(run/'report.json')})
    return run/'report.json'


def backfill(repo,target,run):
    run=Path(run).resolve()
    if run.exists() and any(run.iterdir()):raise PdfError('RUN must be fresh/empty')
    run.mkdir(parents=True,exist_ok=True);items=[]
    for source in discover_reviews(repo,target):
        folder=run/source.stem
        try:
            report=build_pack(source,folder);value=json.loads(report.read_text())
            item={'source':str(source),'run':str(folder),'status':value['status'],'errors':value.get('checks',{}).get('errors',[])}
        except (PdfError,OSError,ValueError) as exc:item={'source':str(source),'run':str(folder),'status':'withheld','errors':[str(exc)]}
        items.append(item);print(source.parent.name,item['status'], '; '.join(item['errors']),flush=True)
    dump(run/'summary.json',{'packs':items})
    return int(any(p['status'] in ('withheld','stale') for p in items))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);commands=parser.add_subparsers(dest='command',required=True)
    for name in ('build','check','publish','backfill'):
        p=commands.add_parser(name);p.add_argument('--run',type=Path,required=True)
        if name=='build':p.add_argument('--review',type=Path,required=True)
        if name in ('publish','backfill'):p.add_argument('--repo',type=Path,required=True)
        if name=='backfill':p.add_argument('--target',default='all')
    args=parser.parse_args(argv)
    try:
        if args.command=='backfill':return backfill(args.repo,args.target,args.run)
        if args.command=='build':
            report=build_pack(args.review,args.run);value=json.loads(report.read_text());print(report,value['status']);return int(value['status'] in ('withheld','stale'))
        if args.command=='check':
            errors=check_stage(args.run);print('PASS' if not errors else '\n'.join(errors));return int(bool(errors))
        print('backup:',publish_stage(args.run,args.repo));return 0
    except (PdfError,OSError,ValueError,KeyError) as exc:print(str(exc),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
