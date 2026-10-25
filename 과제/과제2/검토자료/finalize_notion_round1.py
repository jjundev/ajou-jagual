"""Apply the author's four confirmed formatting repairs, with exact readback."""
from pathlib import Path
import copy
import importlib.util
import json
import sys
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[1]
OUT = ROOT / '검토자료/노션_1차수정_적용'
PID = '404b06d2-63bc-81cd-b588-d36e59ca3a77'


def common():
    spec = importlib.util.spec_from_file_location('round1_common', REPO / '.agents/skills/notion-report-sync/scripts/notion_report.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, mod.NotionAPI()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def text(b, field='rich_text'):
    return ''.join(v.get('plain_text', v.get('text', {}).get('content', '')) for v in b.get(b['type'], {}).get(field, []))


def canonical(b):
    kind = b['type']
    value = copy.deepcopy(b[kind])
    if kind == 'image' and value.get('type') == 'file':
        value['file'] = {'path': urlsplit(value['file']['url']).path}
    return {'id': b['id'], 'type': kind, 'value': value,
            'children': [canonical(x) for x in b.get('_children', [])]}


def prepare():
    OUT.mkdir(exist_ok=True)
    assert not (OUT / 'plan.json').exists(), 'An existing plan must be inspected before preparing again.'
    for name in ('before.json', 'before.md'):
        if (OUT / name).exists():
            assert not (OUT / ('initial-' + name)).exists()
            (OUT / name).rename(OUT / ('initial-' + name))
    mod, api = common()
    blocks = api.tree(PID)
    write('before.json', {'page': api.request('GET', 'pages/' + PID), 'blocks': blocks})
    (OUT / 'before.md').write_text(mod.markdown_from_response(api.request('GET', f'pages/{PID}/markdown')))
    toc = [b for b in blocks if b['type'] == 'table_of_contents']
    assert 1 <= len(toc) <= 2
    gray = [b for b in toc if b['table_of_contents']['color'] == 'gray']
    assert len(gray) == 1
    duplicate = [b for b in blocks if b['type'] == 'paragraph' and text(b) == '경계 사례: 정확한 크기와 최소 크기']
    assert len(duplicate) == 1
    edits = []
    for b in blocks:
        if b['type'] != 'image':
            continue
        caption = text(b, 'caption')
        if caption.startswith('Antigravity IDE 내장 터미널'):
            items = copy.deepcopy(b['image']['caption'])
            assert items[0]['type'] == 'text' and items[0]['text']['content'].startswith('Antigravity IDE 내장 ')
            items[0]['text']['content'] = items[0]['text']['content'].removeprefix('Antigravity IDE 내장 ')
            writable = [{k: v for k, v in item.items() if k in {'type', 'text', 'annotations'}} for item in items]
            edits.append({'block_id': b['id'], 'old_text': caption, 'body': {'image': {'caption': writable}}})
    assert len(edits) == 3
    h = next(i for i, b in enumerate(blocks) if b['type'] == 'heading_2' and text(b).startswith('실패 사례: 외부 단편화'))
    input_id = next(b['id'] for b in blocks[h:] if b['type'] == 'code')
    i = next(i for i, b in enumerate(blocks) if b['id'] == input_id)
    assert blocks[i+1]['type'] == 'paragraph' and text(blocks[i+1]) == '실제 출력 (표준 출력 원문)'
    plan = {'page_id': PID, 'status': 'prepared', 'completed': [], 'pending': None,
            'keep_toc': gray[0]['id'], 'archive': [b['id'] for b in toc if b['id'] != gray[0]['id']] + [duplicate[0]['id']],
            'captions': edits, 'insert_after': input_id, 'insert_before': blocks[i+1]['id']}
    write('plan.json', plan)
    print(f"Prepared: archive {len(plan['archive'])-1} extra TOC + 1 duplicate case title; update 3 captions; insert 1 empty block.")


def apply():
    mod, api = common()
    plan = json.loads((OUT / 'plan.json').read_text())
    assert plan['status'] == 'prepared', 'Inspect durable pending/completed records before attempting recovery.'
    before = json.loads((OUT / 'before.json').read_text())['blocks']
    assert [canonical(b) for b in api.tree(PID)] == [canonical(b) for b in before], 'Page changed since preparation.'
    by_id = {b['id']: b for b in before}
    plan['status'] = 'applying'
    write('plan.json', plan)

    def mutate(label, method, path, body):
        plan['pending'] = {'label': label, 'method': method, 'path': path, 'body': body}
        write('plan.json', plan)
        result = api.request(method, path, body)
        write('response-' + label + '.json', result)
        return result

    def completed(label):
        plan['completed'].append(label)
        plan['pending'] = None
        write('plan.json', plan)

    for bid in plan['archive']:
        current = api.request('GET', 'blocks/' + bid)
        assert current['parent'].get('page_id') == PID and canonical(current) == canonical(by_id[bid])
        mutate('archive-' + bid, 'PATCH', 'blocks/' + bid, {'in_trash': True})
        assert api.request('GET', 'blocks/' + bid).get('in_trash')
        completed('archive-' + bid)

    for edit in plan['captions']:
        bid = edit['block_id']
        current = api.request('GET', 'blocks/' + bid)
        assert current['parent'].get('page_id') == PID and text(current, 'caption') == edit['old_text']
        mutate('caption-' + bid, 'PATCH', 'blocks/' + bid, edit['body'])
        assert text(api.request('GET', 'blocks/' + bid), 'caption') == edit['old_text'].removeprefix('Antigravity IDE 내장 ')
        completed('caption-' + bid)

    children = api.children(PID)
    i = next(i for i, b in enumerate(children) if b['id'] == plan['insert_after'])
    assert children[i+1]['id'] == plan['insert_before']
    before_ids = {b['id'] for b in children}
    mutate('insert-gap', 'PATCH', f'blocks/{PID}/children', {
        'children': [{'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': []}}],
        'position': {'type': 'after_block', 'after_block': {'id': plan['insert_after']}}})
    for attempt in range(6):
        after = api.children(PID)
        fresh = [b for b in after if b['id'] not in before_ids]
        if len(fresh) == 1:
            break
        if attempt == 5:
            raise RuntimeError('Inserted block not yet resolved; inspect saved response, do not append again.')
        time.sleep(0.5)
    gap = fresh[0]
    assert gap['type'] == 'paragraph' and text(gap) == ''
    i = next(i for i, b in enumerate(after) if b['id'] == plan['insert_after'])
    assert [x['id'] for x in after[i:i+3]] == [plan['insert_after'], gap['id'], plan['insert_before']]
    plan['inserted_id'] = gap['id']
    completed('insert-gap')

    final = api.tree(PID)
    expected = [copy.deepcopy(b) for b in before if b['id'] not in plan['archive']]
    for edit in plan['captions']:
        target = next(b for b in expected if b['id'] == edit['block_id'])
        target['image']['caption'] = next(b for b in final if b['id'] == edit['block_id'])['image']['caption']
    assert [canonical(b) for b in expected] == [canonical(b) for b in final if b['id'] != gap['id']], 'Unexpected non-target content change.'
    assert [b['id'] for b in final if b['type'] == 'table_of_contents'] == [plan['keep_toc']]
    assert all(text(b, 'caption').startswith('터미널의 실제 실행 화면.') for b in final if b['type'] == 'image')
    assert not any(b['type'] == 'paragraph' and text(b) == '경계 사례: 정확한 크기와 최소 크기' for b in final)
    write('after.json', final)
    plan.update(status='complete', targeted_changes_verified=True, non_target_content_unchanged=True,
                root_blocks=len(final), tables=sum(b['type']=='table' for b in final), images=sum(b['type']=='image' for b in final))
    write('plan.json', plan)
    print('Verified: one gray TOC, uniform captions, removed duplicate title, input/output gap; all non-target content unchanged.')


if __name__ == '__main__':
    {'prepare': prepare, 'apply': apply}[sys.argv[1]]()
