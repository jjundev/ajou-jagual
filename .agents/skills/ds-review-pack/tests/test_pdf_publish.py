import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
from _util import SKILL
from pdf_types import PdfError
try:
 import pdf_publish
except ImportError:pdf_publish=None
class PublishTests(unittest.TestCase):
 def setUp(self):
  self.assertIsNotNone(pdf_publish,'publication missing')
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.repo=self.root/'repo';self.repo.mkdir();self.run=self.root/'run';self.run.mkdir()
 def stage(self):
  import fitz
  from pdf_cards import digest
  src=self.repo/'복습노트/0907/복습문제_0907_Test.html';src.parent.mkdir(parents=True);src.write_text('source')
  stage=self.run/'stage';stage.mkdir()
  for name in ['복습문제_0907_Test-문제.pdf','복습문제_0907_Test-답안.pdf']:
   doc=fitz.open();p=doc.new_page(width=1440,height=810);p.insert_text((50,50),'fixture');doc.save(stage/name)
  report={'source':str(src),'source_sha256':digest(src),'dest':str(src.parent),'status':'staged','pdfs':[p.name for p in stage.glob('*.pdf')],'checks':{'status':'pass','errors':[]},'artifact_hashes':{p.name:digest(p) for p in stage.glob('*.pdf')},'browser':{'status':'not_run'}}
  pdf_publish.dump(self.run/'report.json',report)
  return src,report
 def approve(self):
  from pdf_cards import digest
  report=json.loads((self.run/'report.json').read_text());pdf_publish.dump(self.run/'review.json',{'status':'pass','reviewer':'real fixture test','evidence':'controlled fixture pages','artifact_hashes':report['artifact_hashes'],'report_sha256':digest(self.run/'report.json')})
 def test_unreviewed_stage_rejected(self):
  src,_=self.stage()
  with self.assertRaises(PdfError):pdf_publish.publish_stage(self.run,self.repo)
  self.assertEqual(list(src.parent.glob('*.pdf')),[])
 def test_source_change_blocks_publish(self):
  src,_=self.stage();self.approve();src.write_text('changed')
  with self.assertRaises(PdfError):pdf_publish.publish_stage(self.run,self.repo)
  self.assertEqual(list(src.parent.glob('*.pdf')),[])
 def test_second_replace_rolls_back(self):
  src,r=self.stage();self.approve()
  for name in r['pdfs']:(src.parent/name).write_bytes(b'old')
  real=pdf_publish.os.replace;calls=0
  def fail(a,b):
   nonlocal calls
   if str(b).endswith('.pdf'):
    calls+=1
    if calls==2:raise OSError('injected second replace')
   return real(a,b)
  with patch.object(pdf_publish.os,'replace',fail):
   with self.assertRaises(OSError):pdf_publish.publish_stage(self.run,self.repo)
  for name in r['pdfs']:self.assertEqual((src.parent/name).read_bytes(),b'old')
 def test_approved_publish_and_hash_mutation(self):
  src,r=self.stage();self.approve();pdf_publish.publish_stage(self.run,self.repo)
  self.assertTrue((src.parent/'.pack/자료_PDF/pdf-validation.json').exists())
  (self.run/'stage'/r['pdfs'][0]).write_bytes(b'changed')
  with self.assertRaises(PdfError):pdf_publish.publish_stage(self.run,self.repo)

 def test_lock_contention(self):
  import fcntl,hashlib
  src,_=self.stage();self.approve()
  lock=Path(tempfile.gettempdir())/'ds-pdf-locks'/(hashlib.sha256(str(src.parent.resolve()).encode()).hexdigest()+'.lock');lock.parent.mkdir(exist_ok=True)
  with lock.open('a') as handle:
   fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
   with self.assertRaisesRegex(PdfError,'lock busy'):pdf_publish.publish_stage(self.run,self.repo)

 def test_direct_publish_rejects_peer_review(self):
  src,_=self.stage();self.approve();(src.parent/'복습문제_0907_Other.html').write_text('peer')
  with self.assertRaisesRegex(PdfError,'collision'):pdf_publish.publish_stage(self.run,self.repo)
  self.assertEqual(list(src.parent.glob('*.pdf')),[])
 def test_published_report_owned_by_other_source_rejected(self):
  src,r=self.stage();self.approve();pdf_publish.dump(src.parent/'.pack/자료_PDF/pdf-validation.json',{'source':str(src.parent/'복습문제_0907_Other.html')})
  with self.assertRaisesRegex(PdfError,'collision'):pdf_publish.publish_stage(self.run,self.repo)
  self.assertEqual(list(src.parent.glob('*.pdf')),[])
