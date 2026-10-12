import unittest, tempfile, json
from pathlib import Path
from _util import REPO
from html2md import Builder, Node
try:
 from pdf_cards import read_pack, to_payload
 from pdf_types import PageSlice, PdfError
except ImportError:
 read_pack = None
class CardsTests(unittest.TestCase):
 def setUp(self): self.assertIsNotNone(read_pack, 'PDF adapter missing')
 def test_solution_extra_code_preserved(self):
  source=next((REPO/'복습노트/1005').glob('복습문제_*.html')); pack=read_pack(source)
  b=Builder();b.feed(source.read_text());article=next(n for n in b.root.find_all(lambda n:n.attrs.get('id')=='p4'))
  sol=next(article.find_all(lambda n:'solution' in n.classes));pre=next(sol.find_all(lambda n:n.tag=='pre'))
  self.assertIn(pre.text(),[x.text for x in pack.cards[3].solution if x.kind=='code'])
 def test_problem_payload_has_no_solution(self):
  pack=read_pack(next((REPO/'복습노트/1005').glob('복습문제_*.html')))
  pages=tuple(PageSlice(c.id,c.id,1,c.problem,c.solution,True,True) for c in pack.cards)
  with tempfile.TemporaryDirectory() as tmp:
   data=to_payload(pack,'problems',pages,Path(tmp))
   self.assertTrue(all('solution' not in p for p in data['problems']))
   self.assertIn('p->link', ''.join(x.text for c in pack.cards for x in c.problem))
 def test_invalid_card_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'복습문제_0907_Test.html';p.write_text('<article class="card" id="p1"><div class="problem">Q</div></article>')
   with self.assertRaises(PdfError): read_pack(p)
   p.write_text('');self.assertEqual(read_pack(p).cards,())
 def test_all_counts(self):
  sources=sorted((REPO/'복습노트').glob('*/복습문제_*.html'))
  self.assertEqual([len(read_pack(p).cards) for p in sources],[4,12,12,8,4,4,4,4,12])

 def test_solution_steps_retain_inline_markup(self):
  source=next((REPO/'복습노트/0914').glob('복습문제_*.html'));pack=read_pack(source)
  b=Builder();b.feed(source.read_text());article=next(b.root.find_all(lambda n:n.attrs.get('id')=='p1'));sol=next(article.find_all(lambda n:'solution' in n.classes));steps=next(sol.find_all(lambda n:n.tag=='ol' and 'steps' in n.classes))
  count=len([n for n in steps.children if isinstance(n,Node) and n.tag=='li'])
  self.assertEqual(len(pack.cards[0].solution),count)

 def test_past_source_is_not_labeled_chapter_problem(self):
  pack=read_pack(next((REPO/'복습노트/0914').glob('복습문제_*.html')))
  self.assertEqual(pack.cards[0].source,'2019-mid-q8');self.assertEqual(pack.cards[0].kind,'기출')
