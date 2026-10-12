import unittest,tempfile,unicodedata
from pathlib import Path
from _util import SKILL
from pdf_types import PdfError
try:
 from review_pdf import discover_reviews
except ImportError:discover_reviews=None
class CliTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(discover_reviews,'CLI missing')
 def test_nfd_discovery_and_report_collision(self):
  with tempfile.TemporaryDirectory() as tmp:
   repo=Path(tmp);folder=repo/unicodedata.normalize('NFD','복습노트')/'0907';folder.mkdir(parents=True)
   p=folder/unicodedata.normalize('NFD','복습문제_0907_Test.html');p.write_text('')
   self.assertEqual(discover_reviews(repo,'all'),(p.resolve(),));self.assertEqual(discover_reviews(repo,'0907'),(p.resolve(),))
   (folder/'복습문제_0907_Other.html').write_text('')
   with self.assertRaisesRegex(PdfError,'collision'):discover_reviews(repo,'all')

 def test_zero_cards_and_partial_failure(self):
  from review_pdf import backfill
  import json
  with tempfile.TemporaryDirectory() as tmp:
   repo=Path(tmp)/'repo';run=Path(tmp)/'run'
   for date,text in [('0907',''),('0914','<article class="card" id="p1"><div class="problem">Q</div></article>')]:
    p=repo/'복습노트'/date/f'복습문제_{date}_Test.html';p.parent.mkdir(parents=True);p.write_text(text)
   self.assertEqual(backfill(repo,'all',run),1)
   self.assertEqual([p['status'] for p in json.loads((run/'summary.json').read_text())['packs']],['skipped','withheld'])

 def test_failed_rebuild_marks_previous_stale(self):
  from review_pdf import build_pack
  import json
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'복습문제_0907_Test.html';p.write_text('<article class="card" id="p1"><div class="problem">Q</div></article>')
   p.with_name(p.stem+'-문제.pdf').write_bytes(b'old')
   report=build_pack(p,Path(tmp)/'run')
   self.assertEqual(json.loads(report.read_text())['status'],'stale')

 def test_browser_failure_withheld_and_other_pack_continues(self):
  from review_pdf import backfill
  from playwright.sync_api import Error
  from unittest.mock import patch
  import json
  with tempfile.TemporaryDirectory() as tmp:
   repo=Path(tmp)/'repo';run=Path(tmp)/'run'
   for date in ['0907','0914']:
    p=repo/'복습노트'/date/f'복습문제_{date}_Test.html';p.parent.mkdir(parents=True);p.write_text('<article class="card" id="p1"><h3>P1. Test</h3><div class="problem"><p>Q</p></div><details class="solution"><ol class="steps"><li>S</li></ol><p class="answer">A</p></details></article>')
   with patch('pdf_layout.probe',side_effect=Error('Chrome disconnected')):
    self.assertEqual(backfill(repo,'all',run),1)
   self.assertEqual([p['status'] for p in json.loads((run/'summary.json').read_text())['packs']],['withheld','withheld'])
