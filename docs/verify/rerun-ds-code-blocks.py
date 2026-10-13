"""Replay published verification without historical RUNs; never overwrite approvals.

uv run --with playwright python docs/verify/rerun-ds-code-blocks.py --kind all --output /tmp/ds-code-blocks-replay
The output directory must be empty. Independent mode needs Python and a C compiler;
browser/all additionally needs Playwright and its installed Chromium runtime.
"""
import argparse
import functools
import hashlib
import http.server
import json
from pathlib import Path
import shutil
import subprocess
import sys
import threading
from types import SimpleNamespace

# Records name pre-.pack locations; the pack-layout migration resolves them to today's files.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'.agents/skills/ds-review-pack/scripts'))
from pack_layout import current_path, current_digest


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError('input outside repository: ' + name)
    return current_path(path)


def load_inputs(root):
    report = json.loads((root / 'docs/verify/2026-10-13-ds-code-blocks.json').read_text())
    records = report['packs']
    if not records:
        raise ValueError('zero question inputs')
    if {p['html'] for p in records} != {p.relative_to(root).as_posix() for p in (root/'복습노트').glob('*/문제설명_*.html')}:
        raise ValueError('published pack set differs')
    sys.path.insert(0, str(root/'.agents/skills/ds-problem-explain/scripts'))
    from mpe_source import load_source
    from mpe_cli import serialized
    inputs = []
    for record in records:
        manifest_path = within(root, record['manifest'])
        manifest = json.loads(manifest_path.read_text())
        source = within(root, record['source'])
        if sha(source) != current_digest(source, record['source_sha256']) or sha(source) != current_digest(source, manifest['source_sha256']):
            raise ValueError('source hash differs')
        for name, digest in manifest['files'].items():
            if sha(within(source.parent, name)) != current_digest((source.parent / name).resolve(), digest):
                raise ValueError('artifact hash differs: ' + name)
        pack = load_source(source, root)
        ids = [p.id for p in pack.problems]
        if not ids or ids != record['problem_ids'] or ids != [p['id'] for p in manifest['problems']]:
            raise ValueError('zero or missing question inputs')
        inputs.append((record, serialized(pack)))
    return inputs


def independent_checks(root, inputs, output):
    replay = output/'independent'
    replay.mkdir()
    first = within(root, inputs[0][0]['manifest']).parent/'evidence'
    for name in ('verify-code-blocks.py', 'verification_key.py', 'author.py'):
        shutil.copy2(first/name, replay/name)
    folders = []
    for record, source in inputs:
        folder = replay/record['date']/f"review-{record['date']}-{record['slug']}"
        folder.mkdir(parents=True)
        (folder/'source.json').write_text(json.dumps(source, ensure_ascii=False))
        data = within(root, record['manifest']).parent
        shutil.copytree(data/'fragments', folder/'explanations')
        (folder/'evidence').mkdir()
        folders.append((record, folder, data/'evidence/independent-results.json'))
    run = subprocess.run([sys.executable, str(replay/'verify-code-blocks.py')], text=True, capture_output=True)
    (output/'independent-run.txt').write_text(run.stdout + run.stderr)
    if run.returncode:
        raise RuntimeError('independent checks failed; see independent-run.txt')
    count = 0
    for record, folder, prior_results in folders:
        actual = json.loads((folder/'evidence/independent-results.json').read_text())
        if set(actual) != set(record['problem_ids']):
            raise ValueError('missing verified question')
        if actual != json.loads(prior_results.read_text()):
            raise ValueError('fresh independent result differs: ' + record['date'])
        count += len(actual)
    return count


def browser_checks(root, records, output):
    from playwright.sync_api import sync_playwright
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin=f'http://127.0.0.1:{server.server_port}/'
    total = 0
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            for record in records:
                dest=output/'browser'/record['date'];dest.mkdir(parents=True)
                results=[]
                for width,height in [(1280,900),(375,812)]:
                    for theme in ['light','dark']:
                        page=browser.new_page(viewport={'width':width,'height':height},color_scheme=theme)
                        logs=[];failed=[];external=[]
                        page.on('pageerror',lambda e:logs.append(str(e)))
                        page.on('console',lambda e:logs.append(e.text) if e.type=='error' else None)
                        page.on('requestfailed',lambda r:failed.append(r.url))
                        page.on('response',lambda r:failed.append(str(r.status)+' '+r.url) if r.status>=400 else None)
                        page.on('request',lambda r:external.append(r.url) if not r.url.startswith(origin) else None)
                        page.goto(origin+record['html'],wait_until='networkidle')
                        for i,pid in enumerate(record['problem_ids']):
                            page.locator('#pager-next').click();page.wait_for_timeout(40)
                            assert page.locator('#'+pid).is_visible(),pid
                            assert page.locator('#'+pid+' [data-explanation]').count()==7
                            assert page.locator('.katex-error').count()==0
                            assert page.locator('#'+pid+' img').evaluate_all('(es)=>es.every(e=>e.complete&&e.naturalWidth>0)')
                            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(record['date'],pid,width,theme,'overflow')
                            metrics=page.locator('#'+pid+' pre').evaluate_all('''es=>es.map(e=>{let s=getComputedStyle(e);return {client:e.clientWidth,scroll:e.scrollWidth,padding:s.padding,border:s.borderTopWidth,size:s.fontSize,whiteSpace:s.whiteSpace,background:s.backgroundColor,color:s.color,codePadding:getComputedStyle(e.querySelector('code')).padding}})''')
                            assert all(m['padding']=='16px' and m['border']=='1px' and m['size']=='14px' and m['whiteSpace']=='pre' and m['codePadding']=='0px' for m in metrics),(pid,metrics)
                            if i==0:
                                page.screenshot(path=str(dest/f'{width}-{theme}-{pid}.png'))
                            results.append({'problem':pid,'viewport':[width,height],'theme':theme,'document_overflow':False,'code_blocks':metrics})
                        page.locator('#pager-prev').click();assert page.locator('#'+record['problem_ids'][-2]).is_visible()
                        page.locator('#pager-next').click();assert page.locator('#'+record['problem_ids'][-1]).is_visible()
                        if width<800 or not page.locator('#panel-right').is_visible():page.locator('#toggle-right').click()
                        page.wait_for_timeout(250);assert page.locator('#panel-right').is_visible()
                        if width<800:page.locator('#panel-right [data-panel-close]').click()
                        page.locator('#toggle-left').click();page.wait_for_timeout(250)
                        if width>=800:page.locator('#toggle-left').click()
                        page.locator('#panel-left a[href="#'+record['problem_ids'][0]+'"]').click();page.wait_for_timeout(150)
                        assert page.locator('#'+record['problem_ids'][0]).is_visible()
                        page.locator('#theme-toggle').click();page.locator('#theme-toggle').click()
                        assert not logs and not failed and not external,(logs,failed,external)
                        page.close()
                (dest/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
                total += len(results)
                print(record['date'],len(results),'browser combinations verified',flush=True)
            browser.close()
    finally:
        server.shutdown()
    return total


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--kind',choices=('independent','browser','all'),default='all')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    root=args.repo.resolve();output=args.output.resolve()
    inputs=load_inputs(root)
    # Keep outputs away from the delivered study files and approvals.
    if output.is_relative_to(root/'복습노트') or output==root or (output.exists() and (not output.is_dir() or any(output.iterdir()))):
        raise ValueError('output must be an empty scratch directory outside delivered notes')
    output.mkdir(parents=True,exist_ok=True)
    summary={'pack_count':len(inputs),'question_count':sum(len(p['problem_ids']) for p,_ in inputs),'input_location':'published sources and fragments','kind':args.kind}
    if args.kind in ('independent','all'):
        summary['independent_question_count']=independent_checks(root,inputs,output)
    if args.kind in ('browser','all'):
        summary['browser_combination_count']=browser_checks(root,[p for p,_ in inputs],output)
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    main()
