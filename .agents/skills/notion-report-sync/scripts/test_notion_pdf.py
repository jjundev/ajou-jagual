import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image

try:
    import notion_pdf as tool
except ImportError:
    tool = None


class PDFTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(tool, 'common HTML print and PDF verifier is missing')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'export').mkdir()
        self.source = self.root / 'export' / 'export.html'
        Image.new('RGB', (100, 30), 'navy').save(self.source.parent / 'screen.png')
        self.source.write_text('''<!doctype html><html><head><meta charset="utf-8">
          <style>body{font-family:Arial}pre{font-family:monospace;white-space:pre-wrap}
          table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:5px}</style></head>
          <body><article class="page"><h1 class="page-title">Fresh report</h1><div class="page-body">
          <h1>Chapter</h1><p>Repeated paragraph.</p><p>Repeated paragraph.</p><p> \n </p>
          <table><thead><tr><th>Source code</th><th>Analysis</th></tr></thead><tbody>
          <tr><td>int value = 1;<br>  value++;</td><td>Value becomes two.</td></tr></tbody></table>
          <p><strong>Output</strong></p><pre>Result: 2\nEXIT: 0</pre>
          <p><strong>Screen</strong></p><figure class="image"><img src="screen.png"><figcaption>First capture</figcaption></figure>
          <p><strong>Screen</strong></p><figure class="image"><img src="screen.png"><figcaption>Repeated capture</figcaption></figure>
          <h2>Appendix</h2><pre data-notion-code-syntax="c">int main() {\n  return 0;\n}</pre>
          <p><a href="https://example.org/?x=1">Reference</a></p></div></article></body></html>''')
        self.output = self.root / 'candidate.pdf'
        self.evidence = self.root / 'checks'

    def render(self, config=None):
        return tool.print_html(self.source, self.output, self.evidence, config=config)

    def test_print_preserves_sources_and_verifies_repeated_text_and_image_occurrences(self):
        original = self.source.read_bytes()
        receipt = self.render()
        result = tool.verify(self.evidence)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(result['image_occurrences'], 2)
        self.assertEqual(result['paired_rows'], 1)
        self.assertEqual(result['visual_review'], 'not verified')
        self.assertTrue(list((self.evidence / 'pages').glob('page-*.png')))
        copy = (self.evidence / 'print.html').read_text()
        self.assertIn('print-image-group', copy)
        self.assertIn('print-empty', copy)
        self.assertEqual(receipt['settings']['landscape'], True)

    def test_changed_asset_rejects_old_receipt(self):
        self.render()
        Image.new('RGB', (100, 30), 'red').save(self.source.parent / 'screen.png')
        with self.assertRaisesRegex(ValueError, 'changed'):
            tool.verify(self.evidence)

    def test_changed_pdf_rejects_old_receipt(self):
        self.render()
        with self.output.open('ab') as f:
            f.write(b'\n% changed\n')
        with self.assertRaisesRegex(ValueError, 'changed'):
            tool.verify(self.evidence)

    def test_candidate_and_evidence_are_never_silently_overwritten(self):
        self.output.write_bytes(b'previous deliverable')
        with self.assertRaises(FileExistsError):
            self.render()
        self.assertEqual(self.output.read_bytes(), b'previous deliverable')

    def test_tall_paired_row_is_rejected(self):
        self.source.write_text(self.source.read_text().replace('Value becomes two.', '<br>'.join(['analysis'] * 90)))
        with self.assertRaisesRegex(ValueError, 'row'):
            self.render()

    def test_heading_and_table_label_stay_with_first_row(self):
        self.source.write_text('''<html><body><article class="page"><div class="page-body">
          <p style="height:510px">Opening content</p><h2>FunctionAlpha</h2><p>Implementation</p>
          <table><thead><tr><th>Code</th><th>Explanation</th></tr></thead>
          <tbody><tr style="height:180px"><td>unique_row_content</td><td>Details</td></tr></tbody></table>
          </div></article></body></html>''')
        self.render()
        import fitz
        with fitz.open(self.output) as pdf:
            heading_pages = [i for i, p in enumerate(pdf) if 'FunctionAlpha' in p.get_text()]
            row_pages = [i for i, p in enumerate(pdf) if 'unique_row_content' in p.get_text()]
        self.assertEqual(heading_pages, row_pages)

    def test_row_that_fits_alone_but_not_with_heading_is_unverified(self):
        self.source.write_text('''<html><body><h2>Large section</h2><p>Implementation</p>
          <table><thead><tr><th>Code</th><th>Explanation</th></tr></thead>
          <tbody><tr style="height:630px"><td>code</td><td>Details</td></tr></tbody></table>
          </body></html>''')
        with self.assertRaisesRegex(ValueError, 'row'):
            self.render()

    def test_large_first_table_does_not_leave_chapter_intro_on_its_own_page(self):
        self.source.write_text('''<html><body><div class="page-body"><h1>ChapterAlpha</h1><p>Introduction</p>
          <h2>SectionAlpha</h2><table><thead><tr><th>Code</th><th>Analysis</th></tr></thead>
          <tbody><tr style="height:350px"><td>first_unique_row</td><td>First analysis</td></tr>
          <tr style="height:350px"><td>second_unique_row</td><td>Second analysis</td></tr></tbody></table>
          </div></body></html>''')
        self.render()
        import fitz
        with fitz.open(self.output) as pdf:
            chapter_pages = [i for i, p in enumerate(pdf) if 'ChapterAlpha' in p.get_text()]
            first_pages = [i for i, p in enumerate(pdf) if 'first_unique_row' in p.get_text()]
        self.assertEqual(chapter_pages, first_pages)

    def test_output_inside_export_bundle_is_rejected(self):
        self.output = self.source.parent / 'candidate.pdf'
        with self.assertRaises(ValueError):
            self.render()

    def test_native_cdn_styles_are_cached_without_changing_export(self):
        self.source.write_text(self.source.read_text().replace('</head>',
            '<link rel="stylesheet" href="https://assets.invalid/export.css"></head>'))
        original = self.source.read_bytes()
        receipt = tool.print_html(self.source, self.output, self.evidence,
            remote_loader=lambda url: (b'body { color: #223344; }', 'text/css'))
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual(len(receipt['remote_resources']), 1)
        cached = Path(receipt['remote_resources'][0]['cache']['path'])
        self.assertEqual(cached.read_bytes(), b'body { color: #223344; }')
        cached.write_bytes(b'changed CSS')
        with self.assertRaisesRegex(ValueError, 'changed'):
            tool.verify(self.evidence)

    def test_missing_local_stylesheet_cannot_silently_change_appearance(self):
        self.source.write_text(self.source.read_text().replace('</head>',
            '<link rel="stylesheet" href="missing.css"></head>'))
        with self.assertRaisesRegex(ValueError, 'assets'):
            self.render()

    def test_changed_print_copy_invalidates_the_receipt(self):
        self.render()
        (self.evidence / 'print.html').write_text('different print copy')
        with self.assertRaisesRegex(ValueError, 'changed'):
            tool.verify(self.evidence)

    def test_long_code_can_flow_independent_of_language(self):
        code = '\n'.join(f'  statement_{i:03}();' for i in range(100))
        self.source.write_text(self.source.read_text().replace('int main() {\n  return 0;\n}', code))
        self.render()
        result = tool.verify(self.evidence)
        self.assertGreater(result['pages'], 1)

    def test_text_order_and_repetition_loss_are_detected(self):
        units = [{'text': 'same'}, {'text': 'middle'}, {'text': 'same'}]
        with self.assertRaises(ValueError):
            tool.check_text(units, ['same middle'])
        with self.assertRaises(ValueError):
            tool.check_text([{'text': 'first'}, {'text': 'second'}], ['second first'])

    def test_blockquote_hidden_by_print_css_is_not_silently_lost(self):
        self.source.write_text(self.source.read_text().replace('</style>',
            '@media print{blockquote{display:none}}</style>').replace('</article>',
            '<blockquote>Required missing quotation</blockquote></article>'))
        self.render()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            tool.verify(self.evidence)

    def test_fragmented_toc_paint_order_does_not_override_geometric_reading_order(self):
        # Native PDF painting may draw fragmented navigation after body text.
        units = [{'text': 'Navigation'}, {'text': 'Body'}]
        geometry = [(1, 80, 10)] * len('Body') + [(1, 10, 10)] * len('Navigation')
        tool.check_text(units, ['Body Navigation'], geometry=geometry)

    def test_indentation_loss_is_detected_separately(self):
        with self.assertRaisesRegex(ValueError, 'indent'):
            tool.check_indentation(['int x;\n  x++;'], 'int x;\nx++;\n')
        tool.check_indentation(['int x;\n  x++;'], 'int x;\n  x++;\n')

    def test_code_indentation_survives_fragmented_pdf_paint_order(self):
        tool.check_indentation(['int x;\n  x++;'], 'int x;\nCaption from preceding figure\n  x++;\n')

    def test_visual_review_requires_all_current_rendered_pages_and_notes(self):
        self.render()
        result = tool.verify(self.evidence)
        with self.assertRaises(ValueError):
            tool.record_review(self.evidence, [], 'checked')
        tool.record_review(self.evidence, list(range(1, result['pages'] + 1)), 'All pages inspected; no issues.')
        state = json.loads((self.evidence / 'state.json').read_text())
        self.assertEqual(state['stages']['visual']['status'], 'verified')
        first = self.evidence / 'pages' / 'page-001.png'
        first.write_bytes(b'changed render')
        from report_state import Ledger
        self.assertEqual(Ledger(self.evidence / 'state.json').refresh()['visual']['status'], 'stale')

    def test_shared_ledger_cannot_mix_two_pdf_candidates(self):
        shared = self.root / 'workflow.json'
        tool.print_html(self.source, self.output, self.evidence, state_path=shared)
        tool.verify(self.evidence)
        other = self.root / 'other-checks'
        tool.print_html(self.source, self.root / 'other.pdf', other,
                        config={'body_pt': 11}, state_path=shared)
        tool.verify(other)
        with self.assertRaisesRegex(ValueError, 'candidate'):
            tool.record_review(self.evidence, [1], 'Reviewed the older candidate.')
        with self.assertRaisesRegex(ValueError, 'candidate'):
            tool.verify(self.evidence)


if __name__ == '__main__':
    unittest.main()
