"""Apply only HW2 spacing and heading formatting; preserve report content."""
from pathlib import Path
import importlib.util
import json
import time

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parents[1]
PID = '404b06d2-63bc-81cd-b588-d36e59ca3a77'
OUT = ROOT / '검토자료/notion_api/formatting'


def common():
    path = REPO / '.agents/skills/notion-report-sync/scripts/notion_report.py'
    spec = importlib.util.spec_from_file_location('nr_format', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.NotionAPI()


def text(b):
    return ''.join(x.get('plain_text', x.get('text', {}).get('content', ''))
                   for x in b.get(b['type'], {}).get('rich_text', []))


def rt(value, bold=False):
    return [{'type': 'text', 'text': {'content': value}, 'annotations': {'bold': bold}}] if value else []


def save(value):
    (OUT / 'changes.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def prepare():
    OUT.mkdir(exist_ok=False)
    mod, api = common()
    root = api.tree(PID)
    (OUT / 'before.json').write_text(json.dumps({'page': api.request('GET', 'pages/' + PID), 'blocks': root}, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'before.md').write_text(mod.markdown_from_response(api.request('GET', f'pages/{PID}/markdown')))
    plan = {'page_id': PID, 'status': 'prepared', 'labels': [], 'gaps': [], 'completed': []}
    chapter = None
    first_subsection = True
    for i, b in enumerate(root):
        if b['type'] == 'heading_1':
            if chapter is not None:
                plan['gaps'].append({'after_id': root[i-1]['id'], 'heading_id': b['id'], 'heading': text(b), 'count': 2})
            chapter = text(b)
            first_subsection = True
        elif b['type'] == 'heading_2':
            if not first_subsection:
                plan['gaps'].append({'after_id': root[i-1]['id'], 'heading_id': b['id'], 'heading': text(b), 'count': 1})
            first_subsection = False
        elif b['type'] == 'heading_3':
            assert text(b) in ['입력', '실제 출력 (표준 출력 원문)', '실제 터미널 실행 화면']
            plan['labels'].append({'block_id': b['id'], 'old_type': 'heading_3', 'old_text': text(b), 'new_type': 'paragraph', 'bold': True})
    assert len(plan['labels']) == 18 and sum(g['count'] for g in plan['gaps']) == 23
    save(plan)
    print('Prepared: 18 targeted label conversions, 23 empty blocks; full before-state backed up.')


def apply():
    mod, api = common()
    plan = json.loads((OUT / 'changes.json').read_text())
    assert plan['status'] in ['prepared', 'applying'], 'Inspect final changes before repeating'
    before = json.loads((OUT / 'before.json').read_text())['blocks']
    now = api.children(PID)
    if plan['status'] == 'prepared':
        assert [(b['id'], b['last_edited_time']) for b in now] == [(b['id'], b['last_edited_time']) for b in before]
    plan['status'] = 'applying'; save(plan)
    for edit in plan['labels']:
        if edit.get('replacement_id'):
            current = api.request('GET', 'blocks/' + edit['replacement_id'])
            assert current['type'] == 'paragraph' and text(current) == edit['old_text']
            continue
        current = api.request('GET', 'blocks/' + edit['block_id'])
        assert current['type'] == edit['old_type'] and text(current) == edit['old_text'] and current['parent']['page_id'] == PID
        para = {'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': rt(edit['old_text'], True)}}
        response = api.request('PATCH', f'blocks/{PID}/children', {'children': [para], 'position': {'type': 'after_block', 'after_block': {'id': edit['block_id']}}})
        new = response['results'][0]
        assert new['type'] == 'paragraph' and text(new) == edit['old_text']
        readback = api.request('GET', 'blocks/' + new['id'])
        assert readback['type'] == 'paragraph' and text(readback) == edit['old_text']
        assert all(x['annotations']['bold'] for x in readback['paragraph']['rich_text'])
        # New block verified before recoverably archiving the old heading.
        api.request('PATCH', 'blocks/' + edit['block_id'], {'in_trash': True})
        edit['replacement_id'] = new['id']; plan['completed'].append({'label': edit['block_id'], 'replacement': new['id']}); save(plan)
    for gap in plan['gaps']:
        now = api.children(PID)
        i = next(i for i, b in enumerate(now) if b['id'] == gap['heading_id'])
        existing = []
        k = i - 1
        while k >= 0 and now[k]['type'] == 'paragraph' and not text(now[k]):
            existing.insert(0, now[k]); k -= 1
        assert now[k]['id'] == gap['after_id'], 'Page structure changed during edit'
        if existing:
            # Recovery: prior successful append was not yet visible to its immediate GET.
            assert len(existing) == gap['count']
            ids = [b['id'] for b in existing]
        else:
            paras = [{'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': []}} for _ in range(gap['count'])]
            result = api.request('PATCH', f'blocks/{PID}/children', {'children': paras, 'position': {'type': 'after_block', 'after_block': {'id': gap['after_id']}}})
            (OUT / ('response-' + gap['heading_id'] + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
            before_ids = {b['id'] for b in now}
            for attempt in range(6):
                after = api.children(PID)
                fresh = [b for b in after if b['id'] not in before_ids]
                if len(fresh) == gap['count']:
                    break
                if attempt == 5:
                    raise RuntimeError('Inspect persisted append response before retrying a mutation')
                time.sleep(0.5)
            ids = [b['id'] for b in fresh]
            assert all(b['type'] == 'paragraph' and not text(b) for b in fresh)
        # Record returned IDs before waiting for read consistency. Never append twice.
        gap['inserted_ids'] = ids
        save(plan)
        for attempt in range(6):
            current = api.children(PID)
            i = next(i for i,b in enumerate(current) if b['id'] == gap['heading_id'])
            if [b['id'] for b in current[i-gap['count']:i]] == ids:
                break
            if attempt == 5:
                raise RuntimeError('Inserted block IDs are not visible at expected position yet; inspect saved record')
            time.sleep(0.5)
        assert all(b['type'] == 'paragraph' and not text(b) for b in current[i-gap['count']:i])
        if not any(c.get('gap_before') == gap['heading_id'] for c in plan['completed']):
            plan['completed'].append({'gap_before': gap['heading_id'], 'ids': ids})
        save(plan)
    final = api.tree(PID)
    replaced = {e['block_id']:e['replacement_id'] for e in plan['labels']}
    inserted = {bid for g in plan['gaps'] for bid in g['inserted_ids']}
    assert [b['id'] for b in final if b['id'] not in inserted] == [replaced.get(b['id'], b['id']) for b in before]
    final_by_id = {b['id']: b for b in final}
    for old in before:
        if old['id'] in replaced:
            assert text(final_by_id[replaced[old['id']]]) == text(old)
        else:
            new = final_by_id[old['id']]
            assert new['type'] == old['type']
            if old['type'] == 'image':
                assert new['image']['type'] == old['image']['type'] == 'file'
                assert new['image']['caption'] == old['image']['caption']
                # Signed download URLs/expiry are refreshed by a read, not content edits.
            else:
                assert new.get(new['type']) == old.get(old['type']), old['id']
            assert new.get('_children') == old.get('_children'), old['id']
    assert not any(b['type']=='heading_3' for b in final)
    for g in plan['gaps']:
        i = next(i for i,b in enumerate(final) if b['id'] == g['heading_id'])
        count=0
        for b in reversed(final[:i]):
            if b['type']=='paragraph' and not text(b):count+=1
            else:break
        assert count==g['count']
    (OUT / 'after.json').write_text(json.dumps(final, ensure_ascii=False, indent=2)+'\n')
    plan.update(status='complete', root_blocks=len(final), non_format_content_unchanged=True, source_tables_unchanged=True,
                image_blocks_unchanged=True, heading_3_count=0, inserted_blank_blocks=len(inserted))
    save(plan)
    print('Verified: 18 labels converted, 23 spacing blocks inserted; text, tables, source and images unchanged.')


if __name__ == '__main__':
    import sys
    {'prepare':prepare,'apply':apply}[sys.argv[1]]()
