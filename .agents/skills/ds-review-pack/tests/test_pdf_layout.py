import unittest,tempfile
from pathlib import Path
from _util import REPO
from pdf_types import Block,Card,Pack,PdfError
try:
 from pdf_layout import plan_pages,check_coverage
except ImportError:plan_pages=None
class LayoutTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(plan_pages,'pagination missing')
 def pack(self,text):
  import html
  c=Card('p1','fixture','장말문제','Long code',(Block('prose','<p>Trace code</p>','Trace code'),),(Block('code','<pre><code>'+html.escape(text)+'</code></pre>',text),),'<p>42</p>','')
  return Pack(Path('/tmp/복습문제_0907_Fixture.html'),'fixture','0907','Fixture',(c,))
 def test_long_code_reconstructed_exactly(self):
  text=''.join(f'  x += {i}; // iteration\n' for i in range(200));pack=self.pack(text)
  with tempfile.TemporaryDirectory() as tmp:
   pages=plan_pages(pack,Path(tmp));self.assertGreater(len(pages),1)
   self.assertEqual(''.join(b.text for p in pages for b in p.solution if b.kind=='code'),text)
   self.assertEqual(check_coverage(pack,pages),[])
   self.assertEqual(sum(p.show_answer for p in pages),1);self.assertTrue(pages[-1].show_answer)
 def test_wide_line_withheld(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(PdfError,'p1'):plan_pages(self.pack('W'*1000),Path(tmp))
 def test_coverage_detects_missing_code(self):
  from pdf_types import PageSlice
  pack=self.pack('x=1;\n')
  pages=(PageSlice('p1','p1',1,pack.cards[0].problem,(),True,True),)
  self.assertTrue(check_coverage(pack,pages))

 def test_no_progress_guard(self):
  from unittest.mock import patch
  from pdf_types import Probe
  with tempfile.TemporaryDirectory() as tmp, patch('pdf_layout.probe',return_value=Probe(('p1',),('p1',),(),{},{})):
   with self.assertRaisesRegex(PdfError,'p1'):plan_pages(self.pack('x=1;\n'),Path(tmp))
