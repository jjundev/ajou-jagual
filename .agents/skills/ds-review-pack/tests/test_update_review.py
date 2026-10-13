import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from _util import SCRIPTS
try:import update_review
except ImportError:update_review=None
import html2md
BEFORE='<html><head><title>old</title></head><body><nav class="toc"></nav><main><div class="hero"><h1>old</h1><p>intro</p></div><section id="partB"><article class="card" id="p1" data-source="old"><h3>old</h3></article></section></main><footer>old</footer><script>localStorage.getItem("old-key")</script></body></html>'
CARD='<article class="card" id="p2" data-source="textbook-ch01-q01" data-source-kind="textbook"><h3>new</h3></article>'
class UpdateTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(update_review,'preserving updater missing')
 def test_preservation_and_rerun(self):
  new=update_review.build_update(BEFORE,[CARD],title='new',intro='new intro',footer='new footer');self.assertEqual(update_review.check_preserved(BEFORE,new),[]);self.assertEqual(update_review.extract_cards(new)[0]['raw'],update_review.extract_cards(BEFORE)[0]['raw']);self.assertIn('"old-key"',new);self.assertEqual(update_review.build_update(new,[CARD],title='new',intro='new intro',footer='new footer'),new)
 def test_metadata_updates_and_nested_footer_preserved(self):
  before=BEFORE.replace('<title>old</title>','<title>old</title><meta name="description" content="old description">').replace('<h3>old</h3>','<h3>old</h3><footer>old source</footer>')
  updated=update_review.build_update(before,[CARD],title='new title',intro='intro',footer='new footer')
  self.assertIn('content="new title"',updated)
  self.assertEqual(update_review.check_preserved(before,updated),[])
 def test_svg_title_rerun_is_idempotent(self):
  card=CARD.replace('<h3>new</h3>','<h3>new</h3><svg><title>original figure</title></svg>')
  first=update_review.build_update(BEFORE,[card],title='n',intro='i',footer='f')
  self.assertEqual(update_review.build_update(first,[card],title='n',intro='i',footer='f'),first)
 def test_existing_eight_cards_append_from_p9(self):
  old=update_review.extract_cards(BEFORE)[0]['raw']
  eight=''.join(old.replace('id="p1"',f'id="p{i}"').replace('data-source="old"',f'data-source="old-{i}"') for i in range(1,9))
  before=BEFORE.replace(old,eight)
  updated=update_review.build_update(before,[CARD.replace('p2','p9')],title='n',intro='i',footer='f')
  self.assertEqual(update_review.extract_cards(updated)[:8],update_review.extract_cards(before))
  self.assertEqual(update_review.extract_cards(updated)[8]['id'],'p9')
 def test_empty_pack_p1(self):
  before=BEFORE.replace(update_review.extract_cards(BEFORE)[0]['raw'],'');new=update_review.build_update(before,[CARD.replace('p2','p1')],title='n',intro='i',footer='f');self.assertEqual(update_review.extract_cards(new)[0]['id'],'p1')
 def test_duplicate_and_reassigned_source_rejected(self):
  with self.assertRaises(ValueError):update_review.build_update(BEFORE,[CARD.replace('p2','p1')],title='n',intro='i',footer='f')
  first=update_review.build_update(BEFORE,[CARD],title='n',intro='i',footer='f')
  with self.assertRaises(ValueError):update_review.build_update(first,[CARD.replace('ch01-q01','ch01-q02')],title='n',intro='i',footer='f')
 def test_second_replace_failure_rolls_back(self):
  with tempfile.TemporaryDirectory() as d:
   a=Path(d)/'a';b=Path(d)/'b';a.write_bytes(b'old-a');b.write_bytes(b'old-b');real=update_review.os.replace;calls=0
   def fail(src,dst):
    nonlocal calls
    calls+=1
    if calls==2:raise OSError('injected failure')
    return real(src,dst)
   with patch.object(update_review.os,'replace',side_effect=fail):
    with self.assertRaises(OSError):update_review.publish_update({a:b'new-a',b:b'new-b'},backup=Path(d)/'backup')
   self.assertEqual(a.read_bytes(),b'old-a');self.assertEqual(b.read_bytes(),b'old-b')
 def test_review_only_keeps_figures(self):
  self.assertTrue(hasattr(html2md,'convert_review'))
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);review=root/'복습문제_0101_Test.html';review.write_text(BEFORE)
   (root/'.pack').mkdir();note=root/'.pack/정리노트_0101_Test.md';note.write_bytes(b'keep-note')
   figures=root/'.pack/figures_0101';figures.mkdir();(figures/'old.svg').write_bytes(b'keep-figure')
   html2md.convert_review(review)
   self.assertEqual(note.read_bytes(),b'keep-note');self.assertEqual((figures/'old.svg').read_bytes(),b'keep-figure')
 def test_review_only_figure_collision_fails(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);review=root/'복습문제_0101_Test.html';review.write_text(BEFORE.replace('<h3>old</h3>','<h3>old</h3><svg id="shared" viewBox="0 0 10 10"><path d="M0 0L1 1"/></svg>'))
   html2md.convert_review(review);existing=root/'.pack/figures_0101/shared.svg';existing.write_bytes(b'preserve this')
   with self.assertRaises(ValueError):html2md.convert_review(review)
   self.assertEqual(existing.read_bytes(),b'preserve this')
