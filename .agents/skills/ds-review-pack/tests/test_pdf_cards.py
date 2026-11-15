import unittest, tempfile, json
from pathlib import Path
from _util import REPO
from review_source import review_paths, read_review
from review_pdf import discover_reviews
from html2md import Builder, Node
try:
 from pdf_cards import read_pack, to_payload
 from pdf_types import PageSlice, PdfError
except ImportError:
 read_pack = None
class CardsTests(unittest.TestCase):
 def setUp(self): self.assertIsNotNone(read_pack, 'PDF adapter missing')
 def test_solution_extra_code_preserved(self):
  source=review_paths(REPO/'복습노트/1005')[0]; pack=read_pack(source)
  b=Builder();b.feed(read_review(source));article=next(n for n in b.root.find_all(lambda n:n.attrs.get('data-source')=='textbook-ch06-q10'))
  sol=next(article.find_all(lambda n:'solution' in n.classes));pre=next(sol.find_all(lambda n:n.tag=='pre'))
  self.assertIn(pre.text(),[x.text for x in next(c for c in pack.cards if c.source=='textbook-ch06-q10').solution if x.kind=='code'])
 def test_problem_payload_has_no_solution(self):
  pack=read_pack(review_paths(REPO/'복습노트/1005')[0])
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
  sources=discover_reviews(REPO, 'all')
  self.assertEqual([len(read_pack(p).cards) for p in sources],[len(json.loads((p.parent/'.pack/자료_복습팩/manifest.json').read_text(encoding='utf-8'))['problems']) for p in sources])

 def test_solution_steps_retain_inline_markup(self):
  source=review_paths(REPO/'복습노트/0914')[0];pack=read_pack(source)
  b=Builder();b.feed(read_review(source));article=next(b.root.find_all(lambda n:n.attrs.get('id')=='p1'));sol=next(article.find_all(lambda n:'solution' in n.classes));steps=next(sol.find_all(lambda n:n.tag=='ol' and 'steps' in n.classes))
  count=len([n for n in steps.children if isinstance(n,Node) and n.tag=='li'])
  self.assertEqual(len(pack.cards[0].solution),count)

 def test_past_source_is_not_labeled_chapter_problem(self):
  pack=read_pack(review_paths(REPO/'복습노트/0914')[0])
  self.assertEqual(pack.cards[0].source,'2018-mid-c024-q8');self.assertEqual(pack.cards[0].kind,'기출')

 def test_images_frozen_in_solution_answer_hint(self):
  from PIL import Image
  with tempfile.TemporaryDirectory() as tmp:
   folder=Path(tmp);Image.new('RGB',(80,40),'blue').save(folder/'diagram.png')
   p=folder/'복습문제_0907_Test.html';p.write_text('<article class="card" id="p1"><h3>P1. Diagram</h3><div class="problem"><p>Q</p></div><details class="hint"><summary>H</summary><img src="diagram.png"></details><details class="solution"><summary>S</summary><img src="diagram.png"><svg viewBox="0 0 80 40"><path class="fig-accent" d="M0 0 L80 40"/></svg><p class="answer"><img src="diagram.png">A</p></details></article>')
   pack=read_pack(p);c=pack.cards[0];pages=(PageSlice(c.id,c.id,1,c.problem,c.solution,True,True),)
   data=to_payload(pack,'answers',pages,folder/'assets');raw=json.dumps(data,ensure_ascii=False)
   self.assertNotIn('src=\\"diagram.png',raw);self.assertNotIn('src="diagram.png',raw)
   self.assertIn('data:image/png;base64',raw);self.assertIn('fig-accent',raw);self.assertIn('<style>',raw)
   p.with_name('diagram.png').unlink()
   from pdf_render import render
   result=render(data,'answers',folder/'render',folder/'out.pdf');self.assertEqual(result.errors,());self.assertEqual(result.overflow,())

 def test_blocks_without_images_keep_original_markup(self):
  from pdf_cards import freeze_inline_html
  raw='<pre><code>printf(&quot;hello\\n&quot;);</code></pre>'
  with tempfile.TemporaryDirectory() as tmp:
   self.assertEqual(freeze_inline_html(raw,Path(tmp)/'source.html',Path(tmp)/'assets'),raw)
