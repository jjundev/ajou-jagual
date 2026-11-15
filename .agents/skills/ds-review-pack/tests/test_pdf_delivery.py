import unittest,json,hashlib,os
from pathlib import Path
from _util import REPO
from pdf_cards import digest,read_pack
from review_pdf import discover_reviews
from review_source import problem_pdf_pages, source_file
from pack_layout import current_path,current_digest
class DeliveryTests(unittest.TestCase):
 def test_existing_pack_pdf_coverage(self):
  import fitz
  sources=discover_reviews(REPO, 'all')
  self.assertGreaterEqual(len(sources),15)
  for source in sources:
   rpath=source.parent/'.pack/자료_PDF/pdf-validation.json';self.assertTrue(rpath.exists(),str(rpath))
   r=json.loads(rpath.read_text());self.assertEqual(r['status'],'published');self.assertFalse(source.exists());self.assertEqual(source_file(source).suffix, '.json')
   self.assertEqual(r['logical_ids'],[c.id for c in read_pack(source).cards]);self.assertEqual(set(problem_pdf_pages(source)),set(r['logical_ids']));self.assertEqual(r['checks']['status'],'pass');self.assertEqual(r['browser']['status'],'pass')
   for name in r['pdfs']:
    self.assertEqual(digest(source.parent/name),r['artifact_hashes'][name])
    with fitz.open(source.parent/name) as doc:
     self.assertEqual(len(doc),len(r['probes']['problems' if name.endswith('-문제.pdf') else 'answers']['page_ids']))
     for p in doc:self.assertAlmostEqual(p.rect.width,1440,delta=.5);self.assertAlmostEqual(p.rect.height,810,delta=.5)
 def test_original_reviews_notes_and_figures_unchanged(self):
  latest=REPO/'docs/verify/2026-10-17-exam-restore.json'
  path=latest if latest.exists() else REPO/'docs/verify/2026-10-17-review-question-overhaul.json';self.assertTrue(path.exists())
  report=json.loads(path.read_text())
  for name,sha in report['protected_files'].items():self.assertEqual(digest(current_path(REPO/name)),current_digest(REPO/name,sha),name)
