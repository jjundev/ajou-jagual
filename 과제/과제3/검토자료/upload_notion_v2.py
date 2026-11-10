"""Create a NEW HW3 Notion page whose content matches 보고서_노션.md (commit 7e86b16).

The block structure (TOC, headings, empty paragraphs, bold labels, NBSP-indented code
cells, code blocks) is cloned from the existing HW3 page snapshot, then 19 exact text
replacements bring it to the local manuscript: 16 wording fixes plus 3 reverts of
edits made directly in Notion after the last sync. The old page is never modified.

Usage: python3 upload_notion_v2.py --dry-run | --upload | --verify
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
import time
import urllib.parse
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parent.parent          # 과제/과제3
REPO = ROOT.parents[1]
EVIDENCE = ROOT / '검토자료/notion_api_v2'
SNAPSHOT = EVIDENCE / 'old-page-tree.json'
MANIFEST = EVIDENCE / 'manifest.json'
PLAN = EVIDENCE / 'upload-plan.json'
REPORT = ROOT / '보고서_노션.md'
SHOTS = ROOT / '터미널_스크린샷'
OLD_PAGE = '408b06d2-63bc-8184-8464-e0f3a3bbd8e5'
PARENT = '3e2b06d2-63bc-803a-bbc0-fb62531e78e0'
TITLE = 'HW3: CPU 및 인터럽트 스케줄러 보고서'

# (old text in the Notion snapshot, new text in 보고서_노션.md); each must match exactly once.
REPLACEMENTS = [
    ('0으로 초기화한 Context가 IDLE_CONTEXT와 같은 셈이다.', '0으로 초기화한 Context가 IDLE_CONTEXT와 같다.'),
    ('차례가 다시 오는 셈이다.', '차례가 다시 온다.'),
    ('구조체이다. ready는 준비 큐, suspended는 중단 문맥 스택, current는 지금 CPU에서 돌고 있는 문맥이며, '
     'tick은 지금까지 흐른 tick 수이자 현재 시각을 의미한다.',
     '구조체다. ready는 준비 큐, suspended는 중단 문맥 스택, current는 지금 CPU에서 돌고 있는 문맥이다. '
     'tick은 지금까지 흐른 tick 수이자 현재 시각이다.'),
    ('뒤의 세 개는 구현할 함수의 원형이다. ',
     '뒤의 세 개는 구현할 함수의 원형이다. 원형이 위에 있어 정의 순서와 상관없이 서로 부를 수 있다. '
     '과제 조건대로 함수 형식·매크로·구조체는 손대지 않았고 함수도 새로 만들지 않았다.'),
    ('front == rear를 비었다고 보는 꼴이다.', 'front와 rear가 같으면 꺼낼 원소가 없으므로 1을 돌려준다.'),
    ('top = -1이 빈 스택인 꼴이다.', 'top을 -1로 두어 빈 스택을 만든다.'),
    ('top이 15면 가득이다.', 'top이 마지막 인덱스 15에 닿으면 1을 돌려준다.'),
    ('스택에 push한다(문맥 전환, context switch의 저장 측면이다).',
     '스택에 push한다. 문맥 전환(context switch)에서 저장에 해당하는 단계다.'),
    ('프로세스가 다 돈 경우.', 'current가 프로세스인 경우.'),
    ('(실행 사례 2·3)', '(추가 사례 1·2)'),
    ('다음 tick에도 같은 프로세스가 이어서 실행되는 셈이다.', '다음 tick에도 같은 프로세스가 이어서 실행된다.'),
    ('select_process가 맡는 셈이다.', 'select_process의 몫이다.'),
    ('(실행 사례 5)', '(추가 사례 4)'),
    ('(실행 사례 4)', '(추가 사례 3)'),
    ('퀀텀 2를 새로 받기 때문이다.', '퀀텀 2를 새로 받은 결과다.'),
    ('T2에 I2가 I1을 끊고, T6·T7에서 I1 → P1 순서로 스택이 풀린다.',
     'T3에서 I2가 I1을 끊고, T4·T5에 I1 → P1 순서로 스택이 풀린다.'),
    ('T8·T9·T11의 pop 세 번이 보인다.',
     'T4·T6·T8이 끝날 때마다 pop이 일어나 T5·T7·T9에 I2·I1·P1이 이어서 실행된다.'),
    ('I1이 끝난 T5에서 스택이 비어 CPU가 IDLE로 떨어진다.',
     'I1이 끝난 T3에서 스택이 비어 CPU가 비고, T4부터 큐의 P2가 실행된다.'),
    ('아직 끝나지 않은 I1 때문에 반복이 이어지는 구간이다.', '아직 도착하지 않은 I1 때문에 반복이 이어지는 구간.'),
]
# The prototype cell must be exactly this before the revert (guards replacement 4).
PROTOTYPE_CELL = '앞의 다섯 개는 제공 함수 가운데 큐·스택 조작 함수와 1 tick 실행 함수, 뒤의 세 개는 구현할 함수의 원형이다. '


def load_api():
    path = REPO / '.claude/skills/notion-report-sync/scripts/notion_report.py'
    spec = importlib.util.spec_from_file_location('notion_report_common', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    api = module.NotionAPI()
    raw = api.request

    def request(method, path, body=None):
        # Retry only reads on dropped connections; never repeat a write blindly.
        for attempt in range(4):
            try:
                return raw(method, path, body)
            except (ConnectionError, OSError) as error:
                if method != 'GET' or attempt == 3:
                    raise
                time.sleep(2 * (attempt + 1))
    api.request = request
    return module, api


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def text_lists(block):
    """Every rich-text list of a block (cells, rich_text, captions), for replacement and checks."""
    kind = block['type']
    data = block[kind]
    if kind == 'table_row':
        yield from data['cells']
    if 'rich_text' in data:
        yield data['rich_text']
    if 'caption' in data:
        yield data['caption']


def writable(items):
    # Notion GET may return one merged item longer than the 2000-character write limit; split it
    # without changing the concatenated text.
    return [{'type': 'text', 'text': {'content': item['text']['content'][i:i + 1900],
                                      'link': item['text'].get('link')},
             'annotations': copy.deepcopy(item['annotations'])}
            for item in items for i in range(0, max(len(item['text']['content']), 1), 1900)]


def image_file(block):
    name = urllib.parse.unquote(block['image']['file']['url'].split('?')[0].rsplit('/', 1)[-1])
    path = SHOTS / name
    assert path.is_file(), path
    return path


def to_payload(block, image_ids):
    kind = block['type']
    data = block[kind]
    if kind == 'table_of_contents':
        body = {'color': data['color']}
    elif kind in ('paragraph', 'heading_1', 'heading_2', 'heading_3'):
        body = {'rich_text': writable(data['rich_text']), 'color': data['color']}
        if kind.startswith('heading'):
            body['is_toggleable'] = data['is_toggleable']
    elif kind == 'code':
        body = {'rich_text': writable(data['rich_text']), 'language': data['language'],
                'caption': writable(data.get('caption', []))}
    elif kind == 'table':
        body = {'table_width': data['table_width'], 'has_column_header': data['has_column_header'],
                'has_row_header': data['has_row_header'],
                'children': [to_payload(row, image_ids) for row in block['_children']]}
    elif kind == 'table_row':
        body = {'cells': [writable(cell) for cell in data['cells']]}
    elif kind == 'image':
        body = {'type': 'file_upload', 'file_upload': {'id': image_ids[block['id']]},
                'caption': writable(data['caption'])}
    else:
        raise ValueError(f'Unsupported block type {kind}')
    return {'object': 'block', 'type': kind, kind: body}


def apply_replacements(tree):
    tree = copy.deepcopy(tree)
    flat = [b for top in tree for b in [top, *top.get('_children', [])]]
    proto = [items for b in flat for items in text_lists(b)
             if ''.join(i['text']['content'] for i in items) == PROTOTYPE_CELL]
    assert len(proto) == 1, 'prototype cell changed in Notion; re-check revert 4'
    for old, new in REPLACEMENTS:
        hits = [(items, i) for b in flat for items in text_lists(b)
                for i, item in enumerate(items) if old in item['text']['content']]
        assert len(hits) == 1 and hits[0][0][hits[0][1]]['text']['content'].count(old) == 1, (old, len(hits))
        items, i = hits[0]
        items[i]['text']['content'] = items[i]['text']['content'].replace(old, new)
        assert len(items[i]['text']['content']) <= 2000
    return tree


def plain(items):
    return ''.join(x.get('plain_text', x.get('text', {}).get('content', '')) for x in items)


def compare(expected, actual):
    assert len(expected) == len(actual), (len(expected), len(actual))
    for wanted, got in zip(expected, actual):
        kind = wanted['type']
        assert got['type'] == kind, (kind, got['type'], got['id'])
        w, g = wanted[kind], got[kind]
        if kind in ('paragraph', 'heading_1', 'heading_2', 'heading_3', 'code'):
            assert plain(w['rich_text']) == plain(g['rich_text']), (kind, got['id'])
            bold = lambda items: [(plain([x]), x['annotations']['bold']) for x in items if plain([x])]
            # Notion may merge adjacent equal-annotation items; compare the bold text spans.
            assert ''.join(t for t, b in bold(w['rich_text']) if b) == ''.join(t for t, b in bold(g['rich_text']) if b), got['id']
            if kind == 'code':
                assert w['language'] == g['language'], got['id']
        elif kind == 'table_of_contents':
            assert g['color'] == w['color'] == 'gray'
        elif kind == 'table':
            assert (g['table_width'], g['has_column_header'], g['has_row_header']) == \
                   (w['table_width'], w['has_column_header'], w['has_row_header']), got['id']
            compare(w['children'], got['_children'])
        elif kind == 'table_row':
            assert [plain(c) for c in w['cells']] == [plain(c) for c in g['cells']], got['id']
            assert not any(i['annotations'].get('code') for c in g['cells'] for i in c), got['id']
        elif kind == 'image':
            assert g['type'] == 'file' and g['file']['url'], got['id']
            assert plain(w['caption']) == plain(g['caption']), got['id']


def upload_image(api, path):
    data = path.read_bytes()
    assert len(data) < 20 * 1024 * 1024
    filename = f'hw3-case-{path.name[:2]}.png'   # ASCII name; the local Korean name stays in the manifest
    result = api.request('POST', 'file_uploads', {'mode': 'single_part', 'filename': filename,
                                                  'content_type': 'image/png'})
    uid = result['id']
    boundary = 'NotionHW3v2' + uuid.uuid4().hex
    disposition = f'form-data; name="file"; filename="{filename}"'
    body = (f'--{boundary}\r\nContent-Disposition: {disposition}\r\n'
            f'Content-Type: image/png\r\n\r\n').encode() + data + f'\r\n--{boundary}--\r\n'.encode()
    headers = {**api.headers, 'Content-Type': 'multipart/form-data; boundary=' + boundary}
    req = urllib.request.Request(f'https://api.notion.com/v1/file_uploads/{uid}/send', data=body,
                                 headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=60) as response:
        sent = json.load(response)
    assert sent['status'] == 'uploaded', sent['status']
    return {'id': uid, 'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'status': sent['status']}


def build_plan(image_ids):
    snapshot = json.loads(SNAPSHOT.read_text())
    assert snapshot['page']['id'] == OLD_PAGE
    tree = apply_replacements(snapshot['tree'])
    return [to_payload(b, image_ids) for b in tree], [b for b in tree if b['type'] == 'image']


def dry_run():
    snapshot = json.loads(SNAPSHOT.read_text())
    images = [b for b in snapshot['tree'] if b['type'] == 'image']
    plan, _ = build_plan({b['id']: 'DRY-RUN' for b in images})
    print('root blocks', len(plan), 'tables', sum(b['type'] == 'table' for b in plan),
          'images', [image_file(b).name for b in images])
    print('replacements applied:', len(REPLACEMENTS))


def verify(api, manifest, plan):
    pid = manifest['page_id']
    remote = api.tree(pid)
    save(EVIDENCE / 'remote-blocks.json', remote)
    compare(plan, remote)
    assert [b['id'] for b in remote] == manifest['new_ids']
    old = {b['id']: b for b in api.tree(OLD_PAGE)}
    assert len(old) == 142, 'old page changed size'
    images = [b for b in remote if b['type'] == 'image']
    checks = []
    for block, upload in zip(images, manifest['uploads']):
        with urllib.request.urlopen(block['image']['file']['url'], timeout=60) as response:
            data = response.read()
        checks.append({'block_id': block['id'], 'file': upload['path'],
                       'bytes_equal': hashlib.sha256(data).hexdigest() == upload['sha256'],
                       'caption': plain(block['image']['caption'])})
    manifest.update(status='blocks_verified', root_block_count=len(remote), image_checks=checks,
                    native_text_and_tables_verified=True)
    save(MANIFEST, manifest)
    print('Verified blocks:', manifest['url'])
    print(json.dumps(checks, ensure_ascii=False, indent=1))


def upload():
    if MANIFEST.exists():
        raise RuntimeError('Upload record exists; inspect it before resuming. Do not recreate the page.')
    _, api = load_api()
    siblings = api.children(PARENT)
    save(EVIDENCE / 'parent-before.json', siblings)
    snapshot = json.loads(SNAPSHOT.read_text())
    manifest = {'status': 'prepared', 'parent_id': PARENT, 'title': TITLE, 'old_page_id': OLD_PAGE,
                'report_sha256': hashlib.sha256(REPORT.read_bytes()).hexdigest(),
                'uploads': [], 'new_ids': []}
    save(MANIFEST, manifest)
    image_ids = {}
    for block in [b for b in snapshot['tree'] if b['type'] == 'image']:
        result = upload_image(api, image_file(block))
        manifest['uploads'].append(result)
        image_ids[block['id']] = result['id']
        save(MANIFEST, manifest)
    plan, _ = build_plan(image_ids)
    save(PLAN, plan)
    manifest.update(status='creating_page', planned_root_blocks=len(plan))
    save(MANIFEST, manifest)
    page = api.request('POST', 'pages', {'parent': {'type': 'page_id', 'page_id': PARENT},
                                         'properties': {'title': {'type': 'title', 'title': [
                                             {'type': 'text', 'text': {'content': TITLE}}]}}})
    manifest.update(page_id=page['id'], url=page['url'], status='uploading_blocks')
    save(MANIFEST, manifest)
    print('Page created:', page['url'], flush=True)
    assert api.children(page['id']) == []
    for first in range(0, len(plan), 30):
        batch = plan[first:first + 30]
        assert len(json.dumps({'children': batch}, ensure_ascii=False).encode()) < 500_000
        manifest['pending'] = f'append root blocks {first}..{first + len(batch) - 1}'
        save(MANIFEST, manifest)
        result = api.request('PATCH', f"blocks/{page['id']}/children", {'children': batch})
        manifest['new_ids'] += [b['id'] for b in result['results']][:len(batch)]
        manifest.pop('pending')
        save(MANIFEST, manifest)
        print('Blocks uploaded:', len(manifest['new_ids']), '/', len(plan), flush=True)
    verify(api, manifest, plan)


def verify_only():
    _, api = load_api()
    manifest = json.loads(MANIFEST.read_text())
    verify(api, manifest, json.loads(PLAN.read_text()))


if __name__ == '__main__':
    {'--dry-run': dry_run, '--upload': upload, '--verify': verify_only}[sys.argv[1]]()
