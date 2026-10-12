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
