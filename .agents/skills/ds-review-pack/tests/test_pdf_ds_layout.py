import tempfile
from pathlib import Path
from _util import REPO
from pdf_cards import read_pack,to_payload
from pdf_types import PageSlice
from pdf_render import load_template

def payload(date,pid,mode,tmp):
 pack=read_pack(next((REPO/'복습노트'/date).glob('복습문제_*.html')))
 c=next(c for c in pack.cards if c.id==pid)
 return to_payload(pack,mode,(PageSlice(c.id,c.id,1,c.problem,c.solution,True,True),),Path(tmp))['problems'][0]

def test_code_has_own_section_preserving_lines():
 with tempfile.TemporaryDirectory() as tmp:
  p=payload('1005','p4','problems',tmp)
  assert '<pre>' in p['html']['code']
  assert '<pre>' not in p['html']['ask']
  pack=read_pack(next((REPO/'복습노트/1005').glob('복습문제_*.html')))
  assert p['html']['code'] == ''.join(b.html for b in pack.cards[3].problem if b.kind=='code')

def test_fill_tables_use_center_only_on_questions():
 with tempfile.TemporaryDirectory() as tmp:
  for pid in ('p2','p3'):
   q=payload('1012',pid,'problems',tmp);a=payload('1012',pid,'answers',tmp)
   assert '<table>' in q['workspace_html']
   assert '<table>' not in q['html']['ask']
   assert '<table>' in a['html']['ask']
   assert not a['workspace_html']
   assert q['workspace_html'] in a['html']['ask']

def test_extension_before_fit_and_empty_conditions_guard():
 for mode in ('problems','answers'):
  t=load_template(mode)
  assert 'if (p.html.conditions' in t
  assert "block('코드'" in t
  assert 'p.workspace_html' in t if mode=='problems' else True

def test_browser_table_placement_and_condition_visibility():
 from pdf_render import probe
 with tempfile.TemporaryDirectory() as tmp:
  for mode in ('problems','answers'):
   p=payload('1012','p2',mode,tmp)
   data={'meta':{'mode':mode,'title':'Test','chapter':'DS'},'problems':[p]}
   result=probe(data,mode,'video-16x9',Path(tmp)/mode)
   assert not result.errors and not result.overflow
   g=result.geometry['p2'];panel=next(r for r in g['regions'] if r['cls']=='panel')
   table=next(r for r in g['regions'] if r['tag']=='TABLE')
   assert table['x'] > panel['x']+panel['w'] if mode=='problems' else table['x'] < panel['x']+panel['w']
   assert '조건' not in g['labels']
   p['html']['conditions']='<p>n = 3</p>'
   result=probe(data,mode,'video-16x9',Path(tmp)/(mode+'-conditions'))
   assert '조건' in result.geometry['p2']['labels']

def test_layout_extension_hash_gate():
 import pytest
 from pdf_ds_layout import extension_hash,check_extension
 from pdf_types import PdfError
 check_extension({'layout_extension_sha256':extension_hash()})
 with pytest.raises(PdfError,match='extension changed'):
  check_extension({'layout_extension_sha256':'old'})
