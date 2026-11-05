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

 def test_direct_build_rejects_report_collision(self):
  from review_pdf import build_pack
  import json
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);p=folder/'복습문제_0907_A.html';p.write_text('')
   (folder/'복습문제_0914_B.html').write_text('')
   r=json.loads(build_pack(p,folder/'run').read_text());self.assertEqual(r['status'],'withheld');self.assertIn('collision',r['failure'])
 def test_missing_image_with_previous_pdf_is_reported_stale(self):
  from review_pdf import build_pack
  import json
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);p=folder/'복습문제_0907_Test.html';p.write_text('<article class="card" id="p1"><div class="problem"><img src="missing.png"></div><details class="solution"><p class="answer">A</p></details></article>')
   p.with_name(p.stem+'-문제.pdf').write_bytes(b'old')
   report=json.loads(build_pack(p,folder/'run').read_text());self.assertEqual(report['status'],'stale');self.assertIn('missing.png',report['failure'])
 def test_final_check_failure_with_previous_pdf_is_stale(self):
  from review_pdf import build_pack
  from unittest.mock import patch
  import json
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);p=folder/'복습문제_0907_Test.html';p.write_text('<article class="card" id="p1"><div class="problem">Q</div><details class="solution"><p class="answer">A</p></details></article>')
   p.with_name(p.stem+'-문제.pdf').write_bytes(b'old')
   with patch('review_pdf.check_stage',return_value=['final check failed']):report=json.loads(build_pack(p,folder/'run').read_text())
   self.assertEqual(report['status'],'stale');self.assertEqual(p.with_name(p.stem+'-문제.pdf').read_bytes(),b'old')

class PerModePageTests(unittest.TestCase):
 def test_long_solution_does_not_add_blank_question_sheets(self):
  from review_pdf import pages_for_mode
  from pdf_types import Block,PageSlice
  q=Block('prose','<p>키 5를 삭제한 트리를 그리세요.</p>','키 5를 삭제한 트리를 그리세요.')
  s1=Block('prose','<p>첫 삭제 단계</p>','첫 삭제 단계')
  s2=Block('prose','<p>남은 자식의 재연결</p>','남은 자식의 재연결')
  pages=(PageSlice('p1','p1',1,(q,),(s1,),False,True),PageSlice('p1','p1-c2',2,(),(s2,),True,False))
  question_pages=pages_for_mode(pages,'problems')
  self.assertEqual([p.physical_id for p in question_pages],['p1'])
  self.assertEqual(tuple(b for p in question_pages for b in p.problem),(q,))
  answer_pages=pages_for_mode(pages,'answers')
  self.assertEqual(tuple(b for p in answer_pages for b in p.solution),(s1,s2))
  self.assertTrue(answer_pages[-1].show_answer)

 def test_question_continuation_is_preserved(self):
  from review_pdf import pages_for_mode
  from pdf_types import Block,PageSlice
  code=Block('code','<pre><code>return 5;</code></pre>','return 5;')
  page=PageSlice('p1','p1-c2',2,(code,),(),True,False)
  self.assertEqual(pages_for_mode((page,),'problems'),(page,))
