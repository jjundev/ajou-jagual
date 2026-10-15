"""A code block inside a solution step must still paginate line by line."""
import unittest
from _util import REPO
from html2md import Builder
from pdf_cards import blocks
from pdf_layout import units, regroup

class NestedSolutionCodeTests(unittest.TestCase):
 def test_step_code_is_split_without_changing_order_or_whitespace(self):
  source='<details class="solution"><ol class="steps"><li><p>먼저</p><pre><code>int x = 1;\n\n    x += 2;\n</code></pre><p>다음</p></li><li>끝</li></ol></details>'
  parser=Builder();parser.feed(source)
  solution=next(parser.root.find_all(lambda n:'solution' in n.classes))
  extracted=blocks(solution)
  self.assertEqual([b.kind for b in extracted],['prose','code','prose','prose'])
  self.assertEqual(extracted[1].text,'int x = 1;\n\n    x += 2;\n')
  self.assertEqual([b.text for _,b in units((extracted[1],))],['int x = 1;\n','\n','    x += 2;\n'])
  self.assertEqual(regroup(units((extracted[1],)))[0].text,extracted[1].text)
  self.assertEqual([b.text for b in extracted if b.kind=='prose'],['먼저','다음','끝'])

if __name__=='__main__':unittest.main()
