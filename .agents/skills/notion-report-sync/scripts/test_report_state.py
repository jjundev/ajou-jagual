import json
from pathlib import Path
import tempfile
import unittest

try:
    from report_state import Ledger
except ImportError:
    Ledger = None


class StateTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(Ledger, 'shared freshness ledger is missing')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'screen.png'
        self.source.write_bytes(b'old image')
        self.pdf = self.root / 'candidate.pdf'
        self.pdf.write_bytes(b'pdf')
        self.ledger = Ledger(self.root / 'state.json', 'selected-page')

    def chain(self):
        self.ledger.record('notion', {'image': self.source})
        self.ledger.record('html', {'image': self.source})
        self.ledger.record('print', {'pdf': self.pdf}, values={'margin': 14})
        self.ledger.record('content', {'pdf': self.pdf})
        self.ledger.record('visual', {'pdf': self.pdf}, evidence=['page-1.png'])

    def test_changed_image_invalidates_entire_downstream_chain(self):
        self.chain()
        self.source.write_bytes(b'new image')
        states = self.ledger.refresh()
        self.assertEqual([states[s]['status'] for s in ('notion', 'html', 'print', 'content', 'visual')], ['stale'] * 5)
        self.assertTrue(states['visual']['evidence'])

    def test_changed_pdf_does_not_invalidate_source_stages(self):
        self.chain()
        self.pdf.write_bytes(b'changed pdf')
        states = self.ledger.refresh()
        self.assertEqual(states['notion']['status'], 'verified')
        self.assertEqual(states['html']['status'], 'verified')
        self.assertEqual(states['visual']['status'], 'stale')

    def test_reverified_parent_does_not_revive_old_children(self):
        self.chain()
        self.source.write_bytes(b'new')
        self.ledger.record('notion', {'image': self.source})
        self.assertEqual(self.ledger.refresh()['html']['status'], 'stale')

    def test_missing_file_and_page_mismatch_are_not_current(self):
        self.chain()
        self.source.unlink()
        self.assertEqual(self.ledger.refresh()['notion']['status'], 'stale')
        with self.assertRaises(ValueError):
            Ledger(self.root / 'state.json', 'other-page')

    def test_explicit_empty_dependencies_support_local_checks(self):
        self.ledger.record('print', {'pdf': self.pdf}, depends_on=[])
        self.assertEqual(self.ledger.refresh()['print']['status'], 'verified')
        self.assertEqual(Ledger(self.root / 'state.json').page_id, 'selected-page')

    def test_recorded_configuration_file_changes_invalidate(self):
        config = self.root / 'config.json'
        config.write_text('{"margin":14}')
        self.ledger.record('print', {'config': config, 'pdf': self.pdf})
        config.write_text('{"margin":15}')
        self.assertEqual(self.ledger.refresh()['print']['status'], 'stale')

    def test_two_instances_do_not_lose_each_others_records(self):
        second = Ledger(self.root / 'state.json', 'selected-page')
        self.ledger.record('images', {'image': self.source})
        second.record('notion', {'image': self.source})
        states = Ledger(self.root / 'state.json').refresh()
        self.assertEqual(states['images']['status'], 'verified')
        self.assertEqual(states['notion']['parents']['images'], states['images']['version'])

    def test_expected_inputs_cannot_be_replaced_with_new_hashes(self):
        from report_state import fingerprint
        expected = {'image': fingerprint(self.source)}
        self.source.write_bytes(b'new')
        with self.assertRaisesRegex(ValueError, 'changed'):
            self.ledger.record('images', {'image': self.source}, expected_inputs=expected)


if __name__ == '__main__':
    unittest.main()
