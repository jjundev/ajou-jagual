"""Create the HW3 native Notion report page; never replace another report page."""
from pathlib import Path
import hashlib
import importlib.util
import json
import re
import sys
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[1]
EVIDENCE = ROOT / '검토자료/notion_api'
PARENT = '3e2b06d2-63bc-803a-bbc0-fb62531e78e0'
TITLE = 'HW3: CPU 및 인터럽트 스케줄러 보고서'

sys.path.insert(0, str(ROOT / '검토자료'))
import build_report as report  # noqa: E402


def load_api():
    path = REPO / '.agents/skills/notion-report-sync/scripts/notion_report.py'
    spec = importlib.util.spec_from_file_location('notion_report_common', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.NotionAPI()


def rt(text, bold=False):
    return [{'type': 'text', 'text': {'content': text[i:i + 1900]}, 'annotations': {'bold': bold}}
            for i in range(0, len(text), 1900)]


def block(kind, text='', bold=False):
    return {'object': 'block', 'type': kind, kind: {'rich_text': rt(text, bold)}}


def empty(n=1):
    return [block('paragraph') for _ in range(n)]


def code(text, language='plain text'):
    return {'object': 'block', 'type': 'code', 'code': {'rich_text': rt(text), 'language': language}}


def table(headers, rows):
    return {'object': 'block', 'type': 'table', 'table': {
        'table_width': len(headers), 'has_column_header': True, 'has_row_header': False,
        'children': [{'object': 'block', 'type': 'table_row', 'table_row': {'cells': [rt(str(c)) for c in row]}}
                     for row in [headers, *rows]]}}


def indent(text):
    return re.sub(r'(?m)^ +', lambda m: ' ' * len(m[0]), text)


def explanation(text):
    return '\n\n'.join(p.strip() for p in text.strip().split('\n\n'))


def code_table(rows):
    return table(['소스코드', '기능 명세와 분석'], [[indent(src.rstrip('\n')), explanation(txt)] for src, txt in rows])


def save(manifest):
    (EVIDENCE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def upload_image(api, path, filename):
    data = path.read_bytes()
    assert len(data) < 20 * 1024 * 1024
    result = api.request('POST', 'file_uploads', {'mode': 'single_part', 'filename': filename, 'content_type': 'image/png'})
    uid = result['id']
    boundary = 'NotionHW3' + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f'Content-Type: image/png\r\n\r\n').encode() + data + f'\r\n--{boundary}--\r\n'.encode()
    headers = {**api.headers, 'Content-Type': 'multipart/form-data; boundary=' + boundary}
    req = urllib.request.Request(f'https://api.notion.com/v1/file_uploads/{uid}/send', data=body, headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=60) as response:
        sent = json.load(response)
    assert sent['status'] == 'uploaded', sent['status']
    return {'id': uid, 'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'status': sent['status']}


def plain(items):
    return ''.join(x.get('plain_text', x.get('text', {}).get('content', '')) for x in items)


def compare(expected, actual):
    assert len(expected) == len(actual), (len(expected), len(actual))
    for wanted, got in zip(expected, actual):
        kind = wanted['type']
        assert got['type'] == kind, (kind, got['type'], got['id'])
        if kind in ['paragraph', 'heading_1', 'heading_2', 'code']:
            assert plain(wanted[kind]['rich_text']) == plain(got[kind]['rich_text']), (kind, got['id'])
            # Notion merges adjacent rich-text items with equal annotations, so compare the bold set.
            assert {x['annotations']['bold'] for x in got[kind]['rich_text']} == \
                   {x['annotations']['bold'] for x in wanted[kind]['rich_text']}, got['id']
        elif kind == 'table_of_contents':
            assert got[kind]['color'] == 'gray'
        elif kind == 'table':
            assert got[kind]['table_width'] == wanted[kind]['table_width']
            compare(wanted[kind]['children'], got['_children'])
        elif kind == 'table_row':
            assert [plain(x) for x in wanted[kind]['cells']] == [plain(x) for x in got[kind]['cells']], got['id']
            assert all(not item.get('annotations', {}).get('code') for cell in got[kind]['cells'] for item in cell)
        elif kind == 'image':
            assert got[kind]['type'] == 'file' and got[kind]['file']['url']
            assert plain(wanted[kind]['caption']) == plain(got[kind]['caption'])


def plan_blocks(api, manifest):
    """Mirror 보고서_초안.md as native blocks; images are uploaded while planning."""
    report.run_cases()
    md_intro = report.OUT.read_text(encoding='utf-8').split('\n')
    purpose = md_intro[md_intro.index('# 구현 목적') + 1].replace('\\', '')
    analysis_intro = md_intro[md_intro.index('# 소스코드 분석') + 1].replace('\\', '')
    run_intro = md_intro[md_intro.index('# 실행결과 및 분석') + 1].replace('\\', '')
    blocks = [{'object': 'block', 'type': 'table_of_contents', 'table_of_contents': {'color': 'gray'}}, *empty(),
              block('heading_1', '구현 목적'), block('paragraph', purpose), *empty(2),
              block('heading_1', '소스코드 분석'), block('paragraph', analysis_intro),
              block('heading_2', '헤더·매크로·구조체·함수 원형'), code_table(report.DECLS)]
    sources = [src for src, _ in report.DECLS]
    for name, label, rows in report.FUNCS:
        blocks += [*empty(), block('heading_2', name), block('paragraph', label), code_table(rows)]
        sources += [src for src, _ in rows]
    blocks += [*empty(2), block('heading_1', '실행결과 및 분석'), block('paragraph', run_intro), *empty()]
    for i, case in enumerate(report.CASES, 1):
        if i > 1:
            blocks += empty()
        blocks.append(block('heading_2', case['title']))
        if case.get('purpose'):
            blocks.append(block('paragraph', case['purpose']))
        blocks += [block('paragraph', '입력', bold=True), code(case['input'].rstrip('\n')), *empty(),
                   block('paragraph', '실제 출력', bold=True), code(case['output'].rstrip('\n')),
                   table(['시각', '실행', '상태 변화의 이유'], case['table']),
                   block('paragraph', '결과 분석: ' + case['analysis']), *empty(),
                   block('paragraph', '실제 터미널 실행 화면', bold=True)]
        image = upload_image(api, ROOT / case['image'], f'hw3-case-0{i}.png')
        manifest['uploads'].append(image)
        save(manifest)
        n = case['input'].count('\n')
        blocks.append({'object': 'block', 'type': 'image', 'image': {
            'type': 'file_upload', 'file_upload': {'id': image['id']},
            'caption': rt(f'터미널의 실제 실행 화면. 입력 {n}줄, tick별 출력과 FINISHED 요약, 종료 상태 0을 보여 준다.')}})
        print('Image uploaded:', i, flush=True)
    blocks += [*empty(2), block('heading_1', '전체 소스코드'), code(report.SOURCE.read_text(encoding='utf-8').rstrip('\n'), 'c')]
    return blocks, sources


def main():
    EVIDENCE.mkdir(exist_ok=True)
    if (EVIDENCE / 'manifest.json').exists():
        raise RuntimeError('Upload record already exists. Inspect it before resuming; do not recreate page or duplicate blocks.')
    common, api = load_api()
    parent = api.request('GET', 'pages/' + PARENT)
    old_children = api.children(PARENT)
    assert not any(b['type'] == 'child_page' and b['child_page']['title'] == TITLE for b in old_children), 'HW3 page already exists'
    (EVIDENCE / 'parent-before.json').write_text(json.dumps({'page': parent, 'children': old_children}, ensure_ascii=False, indent=2) + '\n')
    manifest = {'status': 'prepared', 'parent_id': PARENT, 'title': TITLE,
                'report_sha256': hashlib.sha256(report.OUT.read_bytes()).hexdigest(),
                'source_sha256': hashlib.sha256(report.SOURCE.read_bytes()).hexdigest(),
                'uploads': [], 'new_ids': [], 'notion_pdf_exported': False}
    save(manifest)
    blocks, sources = plan_blocks(api, manifest)
    (EVIDENCE / 'upload-plan.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2) + '\n')
    manifest.update(planned_root_blocks=len(blocks), status='creating_page')
    save(manifest)
    page = api.request('POST', 'pages', {'parent': {'type': 'page_id', 'page_id': PARENT},
                                         'properties': {'title': {'type': 'title', 'title': rt(TITLE)}}})
    pid = page['id']
    manifest.update(page_id=pid, url=page['url'], status='uploading_blocks')
    save(manifest)
    assert api.children(pid) == []
    for first in range(0, len(blocks), 30):
        batch = blocks[first:first + 30]
        assert len(json.dumps({'children': batch}, ensure_ascii=False).encode()) < 500_000
        manifest['pending'] = f'append blocks {first}..{first + len(batch) - 1}'
        save(manifest)
        result = api.request('PATCH', f'blocks/{pid}/children', {'children': batch})
        manifest['new_ids'] += [b['id'] for b in result['results']][:len(batch)]
        manifest.pop('pending')
        save(manifest)
        print('Blocks uploaded:', len(manifest['new_ids']), '/', len(blocks), flush=True)
    verify(api, manifest, blocks, sources)


def verify(api, manifest, blocks, sources):
    """Read the whole page back and compare it with the saved plan; never mutates the page."""
    pid = manifest['page_id']
    remote = api.tree(pid)
    (EVIDENCE / 'remote-blocks.json').write_text(json.dumps(remote, ensure_ascii=False, indent=2) + '\n')
    compare(blocks, remote)
    assert [b['id'] for b in remote] == manifest['new_ids']
    got_sources = [plain(row['table_row']['cells'][0]).replace(' ', ' ')
                   for b in remote if b['type'] == 'table' and plain(b['_children'][0]['table_row']['cells'][0]) == '소스코드'
                   for row in b['_children'][1:]]
    assert got_sources == [s.rstrip('\n') for s in sources]
    assert plain(remote[-1]['code']['rich_text']) == report.SOURCE.read_text(encoding='utf-8').rstrip('\n')
    images = [b for b in remote if b['type'] == 'image']
    assert len(images) == len(report.CASES)
    manifest.update(status='blocks_verified', root_block_count=len(remote), source_rows_verified=len(got_sources),
                    image_block_ids=[b['id'] for b in images], full_source_appendix_verified=True,
                    native_text_and_tables_verified=True)
    save(manifest)
    print('Verified:', manifest['url'], flush=True)


def verify_only():
    _, api = load_api()
    manifest = json.loads((EVIDENCE / 'manifest.json').read_text())
    blocks = json.loads((EVIDENCE / 'upload-plan.json').read_text())
    sources = [src for src, _ in report.DECLS] + [src for _, _, rows in report.FUNCS for src, _ in rows]
    assert manifest['source_sha256'] == hashlib.sha256(report.SOURCE.read_bytes()).hexdigest()
    verify(api, manifest, blocks, sources)


if __name__ == '__main__':
    verify_only() if sys.argv[1:] == ['--verify'] else main()
