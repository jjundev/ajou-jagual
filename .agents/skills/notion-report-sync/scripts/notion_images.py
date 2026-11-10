"""Prepare, apply, or resume targeted replacement of existing Notion images."""
from __future__ import annotations

import argparse
import copy
import io
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import urllib.request
import uuid

from PIL import Image
from notion_report import NotionAPI, NOTION_VERSION, markdown_from_response
from report_state import Ledger, atomic_json, digest, fingerprint

MAX_BYTES = 20_000_000  # Conservative single-part ceiling; larger files need another workflow.
MIMES = {'PNG': ('image/png', '.png'), 'JPEG': ('image/jpeg', '.jpg'), 'WEBP': ('image/webp', '.webp')}
METADATA = {'created_time', 'created_by', 'last_edited_time', 'last_edited_by'}


def walk(tree):
    for block in tree:
        yield block
        yield from walk(block.get('_children', []))


def writable_caption(block):
    result = []
    for item in block['image'].get('caption', []):
        if item.get('type') not in ('text', 'equation'):
            raise ValueError('Unsupported caption structure; review separately')
        result.append({k: copy.deepcopy(v) for k, v in item.items()
                       if k in ('type', 'text', 'equation', 'annotations')})
    return result


def file_url(block):
    image = block['image']
    kind = image.get('type')
    if kind not in ('file', 'external') or not image.get(kind, {}).get('url'):
        raise ValueError('Expected an attached image, not an empty slot')
    return image[kind]['url']


def stable_url(url):
    parts = urlsplit(url)
    host = parts.hostname or ''
    known = (host == 'secure.notion-static.com' or
             (host.startswith('prod-files-secure.s3.') and host.endswith('.amazonaws.com')) or
             (host.startswith('s3.') and host.endswith('.amazonaws.com') and
              parts.path.startswith('/secure.notion-static.com/')))
    return urlunsplit(parts._replace(query='')) if known else url


def comparable(tree, targets=()):
    result = copy.deepcopy(tree)
    for block in walk(result):
        for key in METADATA:
            block.pop(key, None)
        if block.get('type') != 'image':
            continue
        image = block['image']
        caption = writable_caption(block)
        if block['id'] in targets:
            block['image'] = {'caption': caption}
        else:
            image['caption'] = caption
            if image.get('type') == 'file':
                image['file'].pop('expiry_time', None)
                image['file']['url'] = stable_url(image['file']['url'])
    return result


def download_file(url):
    if urlsplit(url).scheme != 'https':
        raise ValueError('Image download must use HTTPS')
    with urllib.request.urlopen(url, timeout=45) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('Image exceeds supported size')
    return data


def image_info(data):
    if not data or len(data) > MAX_BYTES:
        raise ValueError('Image exceeds supported single-part size or is empty')
    with Image.open(io.BytesIO(data)) as image:
        if image.format not in MIMES or getattr(image, 'is_animated', False):
            raise ValueError('Only static PNG, JPEG, and WebP are supported')
        mime, extension = MIMES[image.format]
        image.load()
        return mime, extension, image.size, image.convert('RGBA').tobytes()


def compare_images(expected, actual):
    a, b = image_info(expected), image_info(actual)
    return expected == actual, a[2:] == b[2:]


def send_upload(api, uid, filename, data, mime):
    boundary = 'NotionImage' + uuid.uuid4().hex
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
            f'Content-Type: {mime}\r\n\r\n').encode() + data + f'\r\n--{boundary}--\r\n'.encode()
    request = urllib.request.Request(f'https://api.notion.com/v1/file_uploads/{uid}/send',
        data=body, headers={**api.headers, 'Content-Type': 'multipart/form-data; boundary=' + boundary},
        method='POST')
    with urllib.request.urlopen(request, timeout=60) as response:
        result = json.load(response)
    if result.get('status') != 'uploaded':
        raise RuntimeError('File send did not reach uploaded status')


def prepare(api, page_id, mapping, evidence, *, report=None, state_path=None,
            mapping_path=None, download=download_file):
    evidence = Path(evidence).resolve()
    if evidence.exists():
        raise ValueError('Use a new evidence directory; existing plans must be resumed')
    ledger = Ledger(Path(state_path).resolve() if state_path else evidence / 'state.json', page_id)
    if ledger.path.exists():
        ledger.refresh()
    mapping_source = Path(mapping_path).resolve() if mapping_path else None
    mapping_data = mapping_source.read_bytes() if mapping_source else None
    if mapping_data is not None:
        actual = json.loads(mapping_data)
        resolved = [{'block_id': item['block_id'],
                     'source_path': str((mapping_source.parent / item['source_path']).resolve())}
                    for item in actual]
        supplied = [{'block_id': item['block_id'],
                     'source_path': str(Path(item['source_path']).resolve())} for item in mapping]
        if resolved != supplied:
            raise ValueError('Mapping changed between reading and preparation')
    ids = [item['block_id'] for item in mapping]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError('Mapping must contain distinct block IDs')
    page = api.request('GET', f'pages/{page_id}')
    if page.get('id', '').replace('-', '') != page_id.replace('-', ''):
        raise ValueError('Page identity differs')
    tree = api.tree(page_id)
    blocks = {b['id']: b for b in walk(tree)}
    staged = []
    order = [b['id'] for b in walk(tree) if b['id'] in ids]
    for item in mapping:
        key = item['block_id']
        if key not in blocks or blocks[key]['type'] != 'image':
            raise ValueError('Target is not an image on the selected page: ' + key)
        source = Path(item['source_path']).resolve()
        data = source.read_bytes()
        mime, extension, _, _ = image_info(data)
        caption = writable_caption(blocks[key])
        old = download(file_url(blocks[key]))
        image_info(old)
        staged.append((item, source, data, old, mime, extension, caption))
    markdown = markdown_from_response(api.request('GET', f'pages/{page_id}/markdown'))
    if report is not None:
        Path(report).read_bytes()
    evidence.mkdir(parents=True)
    for name in ('sources', 'previous', 'attached'):
        (evidence / name).mkdir()
    atomic_json(evidence / 'before.json', {'page': page, 'tree': tree})
    if mapping_data is not None:
        (evidence / 'mapping-original.json').write_bytes(mapping_data)
    (evidence / 'before.md').write_text(markdown)
    images = []
    # Execution order follows the page, never directory enumeration or title matching.
    staged.sort(key=lambda record: order.index(record[0]['block_id']))
    for index, (item, source, data, old, mime, ext, caption) in enumerate(staged):
        filename = f'image-{index + 1:03}{ext}'
        snapshot = evidence / 'sources' / filename
        previous = evidence / 'previous' / filename
        snapshot.write_bytes(data)
        previous.write_bytes(old)
        images.append({'block_id': item['block_id'], 'source_path': str(source),
                       'snapshot': str(snapshot), 'previous': str(previous), 'filename': filename,
                       'sha256': digest(data), 'previous_sha256': digest(old), 'mime': mime,
                       'caption': caption, 'state': 'prepared'})
    manifest = {'schema_version': 1, 'api_version': NOTION_VERSION, 'page_id': page_id,
                'images': images, 'state_path': str(Path(state_path).resolve()) if state_path else str(evidence / 'state.json'),
                'report': str(Path(report).resolve()) if report else None,
                'mapping_path': str(mapping_source) if mapping_source else None,
                'mapping_sha256': digest(mapping_data) if mapping_data is not None else None,
                'report_sha256': digest(Path(report).read_bytes()) if report else None}
    atomic_json(evidence / 'manifest.json', manifest)
    return manifest


def apply(api, evidence, *, resume=False, download=download_file, send=send_upload):
    evidence = Path(evidence).resolve()
    manifest_path = evidence / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('schema_version') != 1 or manifest['api_version'] != NOTION_VERSION:
        raise ValueError('Unsupported manifest or API version')
    page_id, records = manifest['page_id'], manifest['images']
    ledger = Ledger(Path(manifest['state_path']), page_id)
    ledger.refresh()
    baseline = json.loads((evidence / 'before.json').read_text())['tree']
    saved = {b['id']: b for b in walk(baseline)}
    tree = api.tree(page_id)
    live = {b['id']: b for b in walk(tree)}
    targets = {r['block_id'] for r in records}
    if comparable(tree, targets) != comparable(baseline, targets):
        raise ValueError('Page content or non-target attachment changed')
    def check_sources(selected):
        try:
            if manifest.get('mapping_path') and digest(Path(manifest['mapping_path']).read_bytes()) != manifest['mapping_sha256']:
                raise ValueError('Mapping changed since preparation')
            if manifest.get('report') and digest(Path(manifest['report']).read_bytes()) != manifest['report_sha256']:
                raise ValueError('Report changed since preparation')
            for entry in selected:
                if any(digest(Path(entry[k]).read_bytes()) != entry['sha256'] for k in ('source_path', 'snapshot')):
                    raise ValueError('Source image changed: ' + entry['block_id'])
        except OSError as error:
            raise ValueError('Source changed or is missing') from error
    check_sources(records)
    # Check the entire batch before the first upload, including verified resume entries.
    for r in records:
        if digest(Path(r['previous']).read_bytes()) != r['previous_sha256']:
            raise ValueError('Previous image backup changed')
        current = live[r['block_id']]
        if r['state'] in ('verified', 'attaching') and resume:
            if not any(compare_images(Path(r['snapshot']).read_bytes(), download(file_url(current)))):
                raise RuntimeError('Attachment uncertain or diverged; inspect before retry: ' + r['block_id'])
            continue
        if r['state'] != 'prepared' and not resume:
            raise RuntimeError('Partial operation: use resume after inspection')
        if (current.get('last_edited_time') != saved[r['block_id']].get('last_edited_time') or
                comparable([current]) != comparable([saved[r['block_id']]])):
            raise ValueError('Target changed since preparation: ' + r['block_id'])
        if digest(download(file_url(current))) != r['previous_sha256']:
            raise ValueError('Target attachment changed since preparation')

    def persist(r, state):
        r['state'] = state
        atomic_json(manifest_path, manifest)

    for r in records:
        check_sources([r])
        key = r['block_id']
        data = Path(r['snapshot']).read_bytes()
        current = api.request('GET', f'blocks/{key}')
        if writable_caption(current) != r['caption']:
            raise ValueError('Target caption changed before mutation')
        if r['state'] in ('verified', 'attaching'):
            attached = download(file_url(current))
            exact, pixels = compare_images(data, attached)
            if not (exact or pixels):
                raise RuntimeError('Attachment uncertain or diverged; inspect before retry: ' + key)
        else:
            if (current.get('last_edited_time') != saved[key].get('last_edited_time') or
                    comparable([current]) != comparable([saved[key]])):
                raise ValueError('Target changed immediately before mutation: ' + key)
            if r['state'] == 'creating':
                raise RuntimeError('Upload creation uncertain without ID; inspect before retry')
            if 'upload_id' not in r:
                persist(r, 'creating')
                try:
                    result = api.request('POST', 'file_uploads', {'mode': 'single_part',
                                         'filename': r['filename'], 'content_type': r['mime']})
                except Exception as error:
                    raise RuntimeError('Upload creation uncertain; inspect before retry') from error
                r['upload_id'] = result['id']
                persist(r, 'created')
            uid = r['upload_id']
            upload = api.request('GET', f'file_uploads/{uid}')
            if upload.get('status') != 'uploaded':
                if r['state'] == 'sending':
                    raise RuntimeError('File send uncertain; inspect before retry')
                if upload.get('status') != 'pending' or r['state'] != 'created':
                    raise RuntimeError('Upload expired, failed or unrecognized; prepare a reviewed replacement plan')
                persist(r, 'sending')
                try:
                    send(api, uid, r['filename'], data, r['mime'])
                except Exception as error:
                    raise RuntimeError('File send uncertain; inspect before retry') from error
                if api.request('GET', f'file_uploads/{uid}').get('status') != 'uploaded':
                    raise RuntimeError('File send uncertain; uploaded status not confirmed')
            persist(r, 'uploaded')
            # A user can edit while the multipart send is in flight.
            current = api.request('GET', f'blocks/{key}')
            if (current.get('last_edited_time') != saved[key].get('last_edited_time') or
                    comparable([current]) != comparable([saved[key]])):
                raise ValueError('Target changed during upload: ' + key)
            persist(r, 'attaching')
            try:
                api.request('PATCH', f'blocks/{key}',
                            {'image': {'file_upload': {'id': uid}, 'caption': r['caption']}})
                current = api.request('GET', f'blocks/{key}')
                attached = download(file_url(current))
                exact, pixels = compare_images(data, attached)
                if writable_caption(current) != r['caption'] or not (exact or pixels):
                    raise ValueError('Readback mismatch')
            except Exception as error:
                raise RuntimeError('Image attachment uncertain; completed IDs are in manifest; inspect or resume: ' + key) from error
        (evidence / 'attached' / r['filename']).write_bytes(attached)
        r.update(exact_bytes=exact, identical_pixels=pixels, attached_sha256=digest(attached))
        persist(r, 'verified')

    after = api.tree(page_id)
    if comparable(after, targets) != comparable(baseline, targets):
        raise RuntimeError('Unexpected changes outside targeted attachments; verification failed')
    latest = {b['id']: b for b in walk(after)}
    for r in records:
        if not any(compare_images(Path(r['snapshot']).read_bytes(), download(file_url(latest[r['block_id']])))):
            raise RuntimeError('Attachment changed before final verification: ' + r['block_id'])
    check_sources(records)
    atomic_json(evidence / 'after.json', {'tree': after})
    markdown = markdown_from_response(api.request('GET', f'pages/{page_id}/markdown'))
    (evidence / 'after.md').write_text(markdown)
    check_sources(records)
    result = {'page_id': page_id, 'image_blocks': [r['block_id'] for r in records],
              'attachments_verified': True, 'captions_order_and_other_content_preserved': True}
    atomic_json(evidence / 'verification.json', result)
    inputs = {'plan': manifest_path}
    for i, r in enumerate(records):
        inputs.update({f'source-{i}': Path(r['source_path']), f'snapshot-{i}': Path(r['snapshot']),
                       f'attached-{i}': evidence / 'attached' / r['filename']})
    if manifest.get('report'):
        inputs['report'] = Path(manifest['report'])
    if manifest.get('mapping_path'):
        inputs['mapping'] = Path(manifest['mapping_path'])
    expected = {k: fingerprint(v) for k, v in inputs.items()}
    for i, r in enumerate(records):
        expected[f'source-{i}']['sha256'] = r['sha256']
        expected[f'snapshot-{i}']['sha256'] = r['sha256']
        expected[f'attached-{i}']['sha256'] = r['attached_sha256']
    if manifest.get('report'):
        expected['report']['sha256'] = manifest['report_sha256']
    if manifest.get('mapping_path'):
        expected['mapping']['sha256'] = manifest['mapping_sha256']
    ledger.record('images', inputs,
        values={'scope': 'targeted image replacement; other page settings not reverified'},
        evidence=[str(evidence / 'verification.json')], expected_inputs=expected)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare')
    prep.add_argument('--page-id', required=True)
    prep.add_argument('--mapping', type=Path, required=True, help='JSON array of block_id/source_path objects')
    prep.add_argument('--report', type=Path)
    prep.add_argument('--state', type=Path)
    prep.add_argument('--evidence', type=Path, required=True)
    for command in ('apply', 'resume'):
        commands.add_parser(command).add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    api = NotionAPI()
    if args.command == 'prepare':
        mapping = json.loads(args.mapping.read_text())
        for item in mapping:
            item['source_path'] = str((args.mapping.parent / item['source_path']).resolve())
        result = prepare(api, args.page_id, mapping, args.evidence, report=args.report,
                         state_path=args.state, mapping_path=args.mapping)
        print('Prepared image plan:', args.evidence / 'manifest.json', 'targets:', len(result['images']))
    else:
        print(json.dumps(apply(api, args.evidence, resume=args.command == 'resume'), ensure_ascii=False))


if __name__ == '__main__':
    main()
