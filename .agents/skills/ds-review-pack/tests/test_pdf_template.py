import unittest, tempfile, sys, types, importlib.util
from pathlib import Path
from _util import SKILL
try:
 import pdf_render
except ImportError: pdf_render=None
class TemplateTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(pdf_render,'frozen renderer missing')
 def test_pinned_template_hashes(self):
  from pdf_cards import digest
  expected={'problem.html':'1ddb009d96f3a844778bd8f4378126d0fd52d037296dff89223adb69bc38bdc7','answer.html':'557b30b2918b4b41ff37763c80869ce28ce6b55f81c42e1ce34bfa30af3c1b06','video-16x9.css':'d56658538e1b67df08a7eea0282e733afd999c6255e58ecc13cd4c72d13ad870','render.py':'120a843102b480f5afff38ffcee0fbad817d2a17a4bf709c388c1491f3481577'}
  for name,sha in expected.items():self.assertEqual(digest(pdf_render.TEMPLATES/name),sha)
 def test_injected_layout_matches_ec2(self):
  fake=types.ModuleType('paths');fake.TEMPLATES=pdf_render.TEMPLATES
  from unittest.mock import patch
  with patch.dict(sys.modules,paths=fake):
   spec=importlib.util.spec_from_file_location('ec2_frozen',pdf_render.TEMPLATES/'render.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
  for mode in ('problems','answers'):
   for layout in ('a4','video-16x9'):
    self.assertEqual(pdf_render.inject(pdf_render.load_template(mode,layout),self.data()),ref.inject(ref.load_template(mode,layout),self.data()))
 @staticmethod
 def data():
  return {'meta':{'title':'Test','chapter':'DS','mode':'answers'},'problems':[{'id':'p1','kind':'장말문제','number':'1','title':'검증','section':'test','difficulty':0,'html':{'conditions':'','original':'','ask':'<p>포인터 $x=1$</p>'},'figures':[],'hints':[],'solution':{'steps':[{'html':'<pre><code>p-&gt;link = NULL;</code></pre>','label':''}],'answer':'1'}}]}
 def test_offline_ready_and_geometry(self):
  import fitz
  with tempfile.TemporaryDirectory() as tmp:
   run=Path(tmp);result=pdf_render.render(self.data(),'answers',run,run/'test.pdf')
   self.assertEqual(result.errors,());self.assertEqual(result.overflow,())
   with fitz.open(run/'test.pdf') as doc:self.assertAlmostEqual(doc[0].rect.width,1440,delta=.5);self.assertAlmostEqual(doc[0].rect.height,810,delta=.5)
 def test_missing_font_or_math_fails(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as tmp, patch.object(pdf_render,'VENDOR',Path(tmp)/'missing'):
   result=pdf_render.probe(self.data(),'answers','a4',Path(tmp))
   self.assertTrue(result.errors)
