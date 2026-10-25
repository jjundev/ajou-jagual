"""Create a new HW2 native Notion report; never replace another report page."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import re
import runpy
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[1]
EVIDENCE = ROOT / '검토자료/notion_api'
PARENT = '3e2b06d2-63bc-803a-bbc0-fb62531e78e0'
TITLE = 'HW2: 프로세스 메모리 관리 보고서'


def load_api():
    path = REPO / '.agents/skills/notion-report-sync/scripts/notion_report.py'
    spec = importlib.util.spec_from_file_location('notion_report_common', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.NotionAPI()


def rt(text):
    return [{'type': 'text', 'text': {'content': text[i:i+1900]}} for i in range(0, len(text), 1900)]


def block(kind, text):
    return {'object': 'block', 'type': kind, kind: {'rich_text': rt(text)}}


def code(text, language='plain text'):
    return {'object': 'block', 'type': 'code', 'code': {'rich_text': rt(text), 'language': language}}


def table(headers, rows):
    return {'object': 'block', 'type': 'table', 'table': {
        'table_width': len(headers), 'has_column_header': True, 'has_row_header': False,
        'children': [{'object': 'block', 'type': 'table_row',
                      'table_row': {'cells': [rt(str(cell)) for cell in row]}}
                     for row in [headers, *rows]]}}


def indent(text):
    return re.sub(r'(?m)^ +', lambda m: '\u00a0' * len(m[0]), text)


def save(manifest):
    (EVIDENCE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def upload_image(api, path, filename):
    data = path.read_bytes()
    assert len(data) < 20 * 1024 * 1024
    result = api.request('POST', 'file_uploads', {'mode': 'single_part', 'filename': filename, 'content_type': 'image/png'})
    uid = result['id']
    boundary = 'NotionHW2' + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: image/png\r\n\r\n'.encode()
            + data + f'\r\n--{boundary}--\r\n'.encode())
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
        assert got['type'] == kind, (kind, got['type'])
        if kind in ['paragraph', 'heading_1', 'heading_2', 'heading_3', 'code']:
            assert plain(wanted[kind]['rich_text']) == plain(got[kind]['rich_text']), (kind, got['id'])
        elif kind == 'table':
            assert got[kind]['table_width'] == wanted[kind]['table_width']
            compare(wanted[kind]['children'], got['_children'])
        elif kind == 'table_row':
            assert [plain(x) for x in wanted[kind]['cells']] == [plain(x) for x in got[kind]['cells']], got['id']
            assert all(not item.get('annotations', {}).get('code') for cell in got[kind]['cells'] for item in cell)
        elif kind == 'image':
            assert got[kind]['type'] == 'file' and got[kind]['file']['url']
            assert plain(wanted[kind]['caption']) == plain(got[kind]['caption'])


def main():
    EVIDENCE.mkdir(exist_ok=True)
    manifest_path = EVIDENCE / 'manifest.json'
    if manifest_path.exists():
        raise RuntimeError('Upload record already exists. Inspect it before resuming; do not recreate page or duplicate blocks.')
    common, api = load_api()
    parent = api.request('GET', 'pages/' + PARENT)
    old_children = api.children(PARENT)
    assert not any(b['type'] == 'child_page' and b['child_page']['title'] == TITLE for b in old_children), 'HW2 page already exists'
    (EVIDENCE / 'parent-before.json').write_text(json.dumps({'page': parent, 'children': old_children}, ensure_ascii=False, indent=2) + '\n')
    report = runpy.run_path(str(ROOT / '검토자료/build_report.py'))
    tree = ast.parse((ROOT / '검토자료/build_report.py').read_text())
    intro = {node.targets[0].id: ast.literal_eval(node.value) for node in ast.walk(tree)
             if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
             and node.targets[0].id in ['purpose', 'notice']}
    blocks = [{'object': 'block', 'type': 'table_of_contents', 'table_of_contents': {'color': 'default'}},
              block('paragraph', ''), block('paragraph', intro['notice']), block('heading_1', '구현 목적'), block('paragraph', intro['purpose'])]
    manifest = {'status': 'prepared', 'parent_id': PARENT, 'title': TITLE,
                'report_sha256': hashlib.sha256((ROOT / '보고서_초안.md').read_bytes()).hexdigest(),
                'source_sha256': hashlib.sha256((ROOT / 'HW2.c').read_bytes()).hexdigest(),
                'uploads': [], 'new_ids': [], 'notion_pdf_exported': False}
    save(manifest)
    source_tables = []
    for part in report['BLOCKS']:
        kind = part[0]
        if kind == 'heading':
            blocks.append(block('heading_' + str(part[1]), part[2]))
        elif kind == 'paragraph':
            blocks.append(block('paragraph', part[1]))
        elif kind == 'source':
            rows = []
            for source, label, paragraphs in part[1]:
                rows.append([indent(source), label + '\n\n' + '\n\n'.join(paragraphs)])
            source_tables.append(len(blocks))
            blocks.append(table(['소스코드', '기능 명세와 분석'], rows))
        elif kind == 'table':
            blocks.append(table(part[1], part[2]))
        elif kind == 'execution':
            case = part[1]
            blocks += [block('heading_3', '입력'), code(case['stdin']), block('heading_3', '실제 출력 (표준 출력 원문)'), code(case['stdout'])]
        elif kind == 'screenshot':
            title, capture = part[1:]
            image = upload_image(api, Path(capture['screenshot']), f"hw2-case-{capture['case_number']}.png")
            manifest['uploads'].append(image)
            save(manifest)
            blocks += [block('heading_3', '실제 터미널 실행 화면'), block('paragraph', title),
                       {'object': 'block', 'type': 'image', 'image': {'type': 'file_upload', 'file_upload': {'id': image['id']},
                        'caption': rt('Antigravity IDE 내장 터미널의 실제 실행 화면. 입력·출력·메모리 지도 및 EXIT_STATUS: 0을 확인했다. 원본 화면에서 창 장식과 빈 여백만 잘랐다.')}}]
            print('Image uploaded:', capture['case_number'], flush=True)
        elif kind == 'appendix':
            blocks.append(code(part[1], 'c'))
        else:
            raise ValueError(kind)
    (EVIDENCE / 'upload-plan.json').write_text(json.dumps(blocks, ensure_ascii=False, indent=2) + '\n')
    manifest['planned_root_blocks'] = len(blocks)
    manifest['source_table_indices'] = source_tables
    manifest['status'] = 'creating_page'
    save(manifest)
    page = api.request('POST', 'pages', {'parent': {'type': 'page_id', 'page_id': PARENT},
                       'properties': {'title': {'type': 'title', 'title': rt(TITLE)}}})
    pid = page['id']
    manifest.update(page_id=pid, url=page['url'], status='uploading_blocks')
    save(manifest)
    assert api.children(pid) == []
    for first in range(0, len(blocks), 30):
        batch = blocks[first:first+30]
        assert len(json.dumps({'children': batch}, ensure_ascii=False).encode()) < 500_000
        result = api.request('PATCH', f'blocks/{pid}/children', {'children': batch})
        assert len(result['results']) == len(batch)
        manifest['new_ids'] += [b['id'] for b in result['results']]
        save(manifest)
        print('Blocks uploaded:', len(manifest['new_ids']), '/', len(blocks), flush=True)
    remote = api.tree(pid)
    compare(blocks, remote)
    assert [b['id'] for b in remote] == manifest['new_ids']
    source = []
    for index in source_tables:
        for row in remote[index]['_children'][1:]:
            cell = row['table_row']['cells'][0]
            source.append(plain(cell).replace('\u00a0', ' '))
    assert source == report['SOURCE_PARTS']
    assert plain(remote[-1]['code']['rich_text']) == (ROOT / 'HW2.c').read_text()
    assert len([b for b in remote if b['type'] == 'image']) == 6
    (EVIDENCE / 'remote-blocks.json').write_text(json.dumps(remote, ensure_ascii=False, indent=2) + '\n')
    markdown = common.markdown_from_response(api.request('GET', f'pages/{pid}/markdown'))
    common.save_pulled_markdown(markdown, ROOT / '보고서_노션.md')
    manifest.update(status='complete', root_block_count=len(remote), source_tables_verified=len(source_tables),
                    source_rows_verified=len(source), images_verified=6, full_source_appendix_verified=True,
                    native_text_and_tables_verified=True, markdown_download_complete=True)
    save(manifest)
    print('Completed:', page['url'], flush=True)


if __name__ == '__main__':
    main()
