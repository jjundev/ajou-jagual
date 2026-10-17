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
  from dataclasses import replace
  pack=read_pack(next((REPO/'복습노트/1012').glob('복습문제_*.html')))
  original=next(c for c in pack.cards if c.source=='2018-mid-c024-q9')
  for source in ('2018-mid-c024-q9','2017-mid-c050-q6'):
   c=replace(original,id='p99',source=source)
   reordered=replace(pack,cards=(c,))
   page=(PageSlice(c.id,c.id,1,c.problem,c.solution,True,True),)
   q=to_payload(reordered,'problems',page,Path(tmp))['problems'][0]
   a=to_payload(reordered,'answers',page,Path(tmp))['problems'][0]
   assert '<table>' in q['workspace_html'] and '<table>' not in q['html']['ask']
   assert '<table>' in a['html']['ask'] and not a['workspace_html']
  c=replace(original,id='p2',source='unrelated-source')
  unrelated=replace(pack,cards=(c,))
  q=to_payload(unrelated,'problems',(PageSlice(c.id,c.id,1,c.problem,c.solution,True,True),),Path(tmp))['problems'][0]
  assert not q['workspace_html'] and '<table>' in q['html']['ask']


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
