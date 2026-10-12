import copy,json,sys,tempfile,unittest,os,shutil,subprocess
from pathlib import Path
from _util import SCRIPTS,REPO,find_nfc
from test_bank import mini_bank,EXPECTED
import bank
try:
 import textbook
except ImportError:
 textbook=None
class TextbookTests(unittest.TestCase):
 def setUp(self): self.assertIsNotNone(textbook,'textbook adapter missing')
 def catalog(self):
  q={'id':'ch04-q03','chapter_id':'ch04','number':'03','kind':'choice','content':[{'type':'text','text':'x'}],'options':[], 'answer':None,'issues':[], 'review':{'status':'verified'}}
  return textbook.TextbookCatalog(Path('.'),{q['id']:q},{'ch04':{'number':4}}, {},{})
 def test_full_mapping(self):
  self.assertEqual([textbook.course_chapters(i) for i in range(1,15)],[{1},{2},{3},{5},{6},{4},{4},{7},{8},{10},{10},{9},{12},{11}])
 def test_null_answer_and_kind_stay_intact(self):
  rows=textbook.textbook_candidates(self.catalog(),{5},{1,5},set());self.assertEqual(rows[0]['id'],'textbook-ch04-q03');self.assertIsNone(rows[0]['answer']);self.assertEqual(rows[0]['type'],'choice')
 def test_pending_blocking_external_context_excluded(self):
  for change in ({'review':{'status':'pending'}},{'issues':[{'kind':'external-context','blocking':False}]},{'issues':[{'kind':'source-error','blocking':True}]}):
   cat=self.catalog();cat.questions['ch04-q03'].update(change);self.assertEqual(textbook.textbook_candidates(cat,{5},{5},set()),[])
 def test_used_and_scope(self):
  cat=self.catalog();self.assertEqual(textbook.textbook_candidates(cat,{5},{5},{'textbook-ch04-q03'}),[]);self.assertEqual(textbook.textbook_candidates(cat,{4},{4},set()),[])
 def test_legacy_and_source_kind_mismatch(self):
  self.assertEqual([q['id'] for q in bank.select(mini_bank(),{2},{1,2})],EXPECTED)
  m={'problems':[{'source':'textbook-ch04-q03','source_kind':'textbook','variant':False}]}
  self.assertEqual(bank.check_manifest(mini_bank(),m,textbook=self.catalog()),[])
  m['problems'][0]['source_kind']='past-exam';self.assertTrue(bank.check_manifest(mini_bank(),m,textbook=self.catalog()))
 def test_validator_failure_has_no_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'제작자료/scripts').mkdir(parents=True);(p/'제작자료/scripts/validate.py').write_text('raise SystemExit(1)')
   with self.assertRaises(bank.BankError):textbook.load_textbook(p,python=sys.executable)
 def test_cli_catalog_error_is_actionable_without_traceback(self):
  with tempfile.TemporaryDirectory() as d:
   file=Path(d)/'bank.json';file.write_text(json.dumps(mini_bank()))
   result=subprocess.run([sys.executable,str(SCRIPTS/'bank.py'),'select',str(file),'--range-ch','5','--taught','1-5','--textbook-dir','/nonexistent'],capture_output=True,text=True)
   self.assertEqual(result.returncode,1);self.assertNotIn('Traceback',result.stderr);self.assertIn('교과서',result.stderr)
 def test_missing_package_fails(self):
  with self.assertRaises(bank.BankError):textbook.load_textbook(Path('/nonexistent'),python=sys.executable)

class RealCatalogTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.python=os.environ.get('DS_TEXTBOOK_PYTHON',sys.executable)
  if subprocess.run([cls.python,'-c','import fitz,jsonschema'],capture_output=True).returncode:
   raise unittest.SkipTest('set DS_TEXTBOOK_PYTHON to Python with PyMuPDF/jsonschema')
 def test_nfd_package_null_answers(self):
  catalog=textbook.load_textbook(find_nfc(REPO,'교과서'),python=self.python)
  self.assertEqual(len(catalog.questions),213);self.assertIsNone(catalog.questions['ch04-q03']['answer'])
 def test_stale_asset_fails_without_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'교과서';shutil.copytree(find_nfc(REPO,'교과서'),target)
   asset=next((target/'assets').glob('*.svg'));asset.write_text(asset.read_text()+'<!-- tampered -->')
   with self.assertRaises(bank.BankError):textbook.load_textbook(target,python=self.python)
 def test_stale_source_fails_without_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'교과서';shutil.copytree(find_nfc(REPO,'교과서'),target)
   source=next((target/'origin').glob('*.pdf'));source.write_bytes(source.read_bytes()+b'changed')
   with self.assertRaises(bank.BankError):textbook.load_textbook(target,python=self.python)
 def test_validator_module_isolation(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d);scripts=target/'제작자료/scripts';scripts.mkdir(parents=True)
   (scripts/'bank.py').write_text('SENTINEL=123')
   (scripts/'validate.py').write_text('import bank; assert bank.SENTINEL==123')
   catalog=textbook.load_textbook(target,python=self.python)
   self.assertEqual(catalog.questions,{});self.assertFalse(hasattr(bank,'SENTINEL'))
