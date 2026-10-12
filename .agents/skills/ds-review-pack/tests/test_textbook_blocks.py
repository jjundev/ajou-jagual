import tempfile,unittest
from pathlib import Path
from _util import SCRIPTS
from test_textbook import TextbookTests
import manifest
from test_manifest import mini
try:import textbook_blocks
except ImportError:textbook_blocks=None
class BlocksTests(unittest.TestCase):
 def setUp(self):self.assertIsNotNone(textbook_blocks,'structured renderer missing')
 def test_choice_recursive_and_c_literals(self):
  cat=TextbookTests().catalog();q=cat.questions['ch04-q03'];q['content']=[{'type':'code','text':'a < b && x; printf("\\n");'},{'type':'subquestions','items':[{'label':'a','content':[{'type':'text','text':'sub'}]}]}];q['options']=[{'label':'1','content':[{'type':'text','text':'one'}]}];q['observations']=[{'text':'handwriting'}]
  s=textbook_blocks.render_question(cat,q['id'],prefix='p1-original');self.assertIn('a &lt; b &amp;&amp; x;',s);self.assertIn('(a)',s);self.assertIn('(1)',s);self.assertNotIn('handwriting',s)
 def test_svg_ids_references_and_alt(self):
  with tempfile.TemporaryDirectory() as d:
   cat=TextbookTests().catalog();cat.package=Path(d);(cat.package/'a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><defs><marker id="arrow"/></defs><path marker-end="url(#arrow)"/></svg>');cat.assets={'a':{'path':'a.svg','alt':'original','review':{'status':'verified'}}}
   blocks=[{'type':'figure','asset_id':'a'}];s=textbook_blocks.render_blocks(blocks,cat,prefix='p1');t=textbook_blocks.render_blocks(blocks,cat,prefix='p2');self.assertIn('p1-0-a-arrow',s);self.assertIn('url(#p1-0-a-arrow)',s);self.assertNotIn('p1-0-a-arrow',t);self.assertIn('original',s);self.assertIn('white',s)
 def test_unsafe_asset_path(self):
  cat=TextbookTests().catalog();cat.assets={'a':{'path':'../secret','alt':'a','review':{'status':'verified'}}}
  with self.assertRaises(ValueError):textbook_blocks.render_blocks([{'type':'figure','asset_id':'a'}],cat,prefix='p1')
 def test_wrong_kind_prefix_fails(self):
  m=mini();m['problems'][0]['source_kind']='textbook';self.assertTrue(manifest.validate(m))
