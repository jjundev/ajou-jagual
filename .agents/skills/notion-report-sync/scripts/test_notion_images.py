import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

try:
    import notion_images as tool
except ImportError:
    tool = None


def png(color):
    stream = io.BytesIO()
    Image.new('RGB', (30, 12), color).save(stream, format='PNG')
    return stream.getvalue()


class ImageAPI:
    """Only the external Notion boundary is simulated; files and comparisons are real."""
    def __init__(self):
        self.url_generation = 0
        self.blobs = {'old-a': png('black'), 'old-b': png('white')}
        self.blocks = [self.image('a', 'old-a'), self.image('b', 'old-b'),
                       {'id': 'text', 'type': 'paragraph', 'paragraph': {'rich_text': []}}]
        self.uploads = {}
        self.patches = []
        self.timeout_after = False
        self.fail_second = False

    def image(self, key, resource):
        return {'id': key, 'type': 'image', 'last_edited_time': 'before',
                'image': {'type': 'file', 'file': {'url': self.url(resource), 'expiry_time': 'soon'},
                          'caption': [{'type': 'text', 'text': {'content': key, 'link': {'url': 'https://example.org/?q=1'}},
                                       'plain_text': key, 'annotations': {'bold': True}}]}}

    def url(self, resource):
        return 'https://prod-files-secure.s3.us-west-2.amazonaws.com/' + resource + '?signature=' + str(self.url_generation)

    def tree(self, page_id):
        if page_id != 'page':
            raise ValueError('wrong page')
        return copy.deepcopy(self.blocks)

    def request(self, method, path, body=None):
        if method == 'GET' and path == 'pages/page':
            return {'id': 'page', 'url': 'https://notion.so/page'}
        if method == 'GET' and path == 'pages/page/markdown':
            return {'markdown': 'report'}
        if method == 'GET' and path.startswith('blocks/'):
            block = next(b for b in self.blocks if b['id'] == path.split('/')[1])
            result = copy.deepcopy(block)
            if result['type'] == 'image':
                result['image']['file']['url'] = result['image']['file']['url'].split('?')[0] + '?signature=new'
            return result
        if method == 'POST' and path == 'file_uploads':
            uid = 'upload-' + str(len(self.uploads))
            self.uploads[uid] = {'id': uid, 'status': 'pending'}
            return self.uploads[uid].copy()
        if method == 'GET' and path.startswith('file_uploads/'):
            return self.uploads[path.split('/')[1]].copy()
        if method == 'PATCH' and path.startswith('blocks/'):
            key = path.split('/')[1]
            if self.fail_second and key == 'b':
                raise TimeoutError('before application')
            self.patches.append(copy.deepcopy(body))
            if 'type' in body['image']:
                raise ValueError('image.type must be absent')
            block = next(b for b in self.blocks if b['id'] == key)
            uid = body['image']['file_upload']['id']
            block['image'].update(type='file', file={'url': self.url(uid)}, caption=body['image']['caption'])
            block['last_edited_time'] = 'after'
            if self.timeout_after:
                self.timeout_after = False
                raise TimeoutError('after application')
            return copy.deepcopy(block)
        raise AssertionError((method, path))

    def download(self, url):
        key = url.split('/')[-1].split('?')[0]
        return self.blobs[key]

    def send(self, api, uid, filename, data, mime):
        self.blobs[uid] = data
        self.uploads[uid]['status'] = 'uploaded'


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(tool, 'common image replacement tool is missing')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.a, self.b = self.root / 'a.png', self.root / 'b.png'
        self.a.write_bytes(png('red'))
        self.b.write_bytes(png('blue'))
        self.api = ImageAPI()
        self.evidence = self.root / 'evidence'

    def prepare(self, entries=None):
        return tool.prepare(self.api, 'page', entries or [
            {'block_id': 'a', 'source_path': str(self.a)},
            {'block_id': 'b', 'source_path': str(self.b)}], self.evidence,
            download=self.api.download)

    def apply(self, resume=False):
        return tool.apply(self.api, self.evidence, resume=resume,
                          download=self.api.download, send=self.api.send)

    def test_replaces_only_mapped_attachment_preserving_caption_and_other_image(self):
        self.prepare([{'block_id': 'a', 'source_path': str(self.a)}])
        old_b = copy.deepcopy(self.api.blocks[1])
        self.apply()
        self.assertEqual(self.api.blocks[1], old_b)
        self.assertEqual(len(self.api.patches), 1)
        self.assertNotIn('type', self.api.patches[0]['image'])
        self.assertEqual(self.api.patches[0]['image']['caption'][0]['text']['link'], {'url': 'https://example.org/?q=1'})
        self.assertTrue(json.loads((self.evidence / 'manifest.json').read_text())['images'][0]['exact_bytes'])

    def test_foreign_duplicate_or_nonimage_targets_fail_before_mutation(self):
        for ids in [('foreign',), ('text',), ('a', 'a')]:
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.prepare([{'block_id': key, 'source_path': str(self.a)} for key in ids])
        self.assertEqual(self.api.uploads, {})

    def test_changed_source_rejects_entire_batch_before_upload(self):
        self.prepare()
        self.b.write_bytes(png('green'))
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.apply()
        self.assertEqual(self.api.uploads, {})

    def test_remote_edit_rejects_entire_batch_before_upload(self):
        self.prepare()
        self.api.blocks[1]['image']['caption'][0]['text']['content'] = 'edited'
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.apply()
        self.assertEqual(self.api.uploads, {})

    def test_timeout_after_patch_is_resolved_on_resume_without_second_patch(self):
        self.prepare()
        self.api.timeout_after = True
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            self.apply()
        self.apply(resume=True)
        self.assertEqual(len(self.api.patches), 2)
        self.assertEqual(len(self.api.uploads), 2)

    def test_uncertain_unchanged_write_is_not_repeated(self):
        self.prepare()
        self.api.fail_second = True
        with self.assertRaises(RuntimeError):
            self.apply()
        self.api.fail_second = False
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            self.apply(resume=True)
        self.assertEqual(len(self.api.patches), 1)

    def test_non_target_url_change_is_not_masked(self):
        self.prepare([{'block_id': 'a', 'source_path': str(self.a)}])
        self.api.blocks[1]['image']['file']['url'] = 'https://example.org/different.png?q=2'
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.apply()
        self.assertEqual(self.api.uploads, {})

    def test_signed_url_refresh_is_accepted_but_new_attachment_is_not(self):
        self.prepare()
        for b in self.api.blocks[:2]:
            b['image']['file']['url'] += '&renewed=1'
        self.apply()
        self.assertEqual(len(self.api.patches), 2)

    def test_source_changed_during_upload_stops_before_next_attachment(self):
        self.prepare()
        original_send = self.api.send
        def changed_send(api, uid, filename, data, mime):
            original_send(api, uid, filename, data, mime)
            self.b.write_bytes(png('green'))
        self.api.send = changed_send
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.apply()
        self.assertEqual(len(self.api.patches), 1)

    def test_wrong_page_ledger_is_rejected_before_writes(self):
        self.prepare()
        from report_state import Ledger
        Ledger(self.evidence / 'state.json', 'other-page').record('notion', {'source': self.a})
        with self.assertRaises(ValueError):
            self.apply()
        self.assertEqual(len(self.api.patches), 0)

    def test_creation_response_lost_is_not_repeated(self):
        self.prepare()
        original = self.api.request
        def request(method, path, body=None):
            result = original(method, path, body)
            if method == 'POST':
                raise TimeoutError('creation response lost')
            return result
        self.api.request = request
        with self.assertRaises(RuntimeError):
            self.apply()
        self.api.request = original
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            self.apply(resume=True)
        self.assertEqual(len(self.api.uploads), 1)

    def test_attachment_check_does_not_certify_full_notion_report(self):
        self.prepare()
        self.apply()
        state = json.loads((self.evidence / 'state.json').read_text())['stages']
        self.assertNotIn('notion', state)
        self.assertEqual(state['images']['status'], 'verified')

    def test_changed_original_mapping_is_rejected(self):
        mapping = self.root / 'mapping.json'
        entries = [{'block_id': 'a', 'source_path': str(self.a)}]
        mapping.write_text(json.dumps(entries))
        tool.prepare(self.api, 'page', entries, self.evidence,
                     mapping_path=mapping, download=self.api.download)
        mapping.write_text('[]')
        with self.assertRaisesRegex(ValueError, 'Mapping changed'):
            self.apply()
        self.assertEqual(len(self.api.patches), 0)

    def test_mapping_file_must_match_the_entries_read_for_preparation(self):
        mapping = self.root / 'mapping.json'
        mapping.write_text(json.dumps([{'block_id': 'b', 'source_path': str(self.b)}]))
        with self.assertRaisesRegex(ValueError, 'Mapping changed'):
            tool.prepare(self.api, 'page', [{'block_id': 'a', 'source_path': str(self.a)}],
                         self.evidence, mapping_path=mapping, download=self.api.download)

    def test_send_response_lost_can_resume_if_upload_is_confirmed(self):
        self.prepare()
        original = self.api.send
        def send(api, uid, filename, data, mime):
            original(api, uid, filename, data, mime)
            raise TimeoutError('send response lost')
        self.api.send = send
        with self.assertRaises(RuntimeError):
            self.apply()
        self.api.send = original
        self.apply(resume=True)
        self.assertEqual(len(self.api.uploads), 2)
        self.assertEqual(len(self.api.patches), 2)

    def test_source_change_during_final_readback_cannot_be_certified(self):
        self.prepare([{'block_id': 'a', 'source_path': str(self.a)}])
        original = self.api.request
        def request(method, path, body=None):
            result = original(method, path, body)
            if path == 'pages/page/markdown':
                self.a.write_bytes(png('green'))
            return result
        self.api.request = request
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.apply()
        from report_state import Ledger
        self.assertNotEqual(Ledger(self.evidence / 'state.json').refresh().get('images', {}).get('status'), 'verified')


if __name__ == '__main__':
    unittest.main()
