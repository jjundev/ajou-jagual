import copy
import json
from pathlib import Path
from unittest.mock import patch
import pytest
import fitz
from _util import SKILL
import pdf_render
from pdf_types import PdfError

TEXT='int main(void) { // 스택 초기화\n    return 0;\n}\n'

def data(mode, scale=1, text=TEXT):
    code='<pre><code>'+__import__('html').escape(text)+'</code></pre>'
    return {'meta':{'title':'Test','chapter':'DS','mode':mode,'typography':{'p1':{'panel':scale,'solution':scale,'math':[],'hints':[]}}},'problems':[{'id':'p1','kind':'장말문제','number':'1','title':'검증','section':'test','difficulty':0,'html':{'conditions':'','original':'','ask':'<p>inline <code>x = 1</code></p>','code':code},'figures':[],'hints':[],'solution':{'steps':[{'html':code,'label':''}],'answer':'1'}}]}

def spans(pdf):
    with fitz.open(pdf) as doc:
        return [s for p in doc for b in p.get_text('dict')['blocks'] if 'lines' in b for l in b['lines'] for s in l['spans']]

@pytest.mark.parametrize('mode',['problems','answers'])
def test_offline_font_loaded_and_used(tmp_path,mode):
    pdf=tmp_path/'out.pdf'
    p=pdf_render._run(data(mode),mode,'video-16x9',tmp_path,pdf)
    assert not p.errors and not p.overflow
    assert p.geometry['p1']['code']
    ss=spans(pdf)
    assert any('JetBrainsMono' in s['font'] and 'int main' in s['text'] for s in ss)
    assert any('Pretendard' in s['font'] and '스택' in s['text'] for s in ss)

@pytest.mark.parametrize('mode',['problems','answers'])
@pytest.mark.parametrize('scale',[.8,1])
def test_code_fixed_size_ignores_parent_scale(tmp_path,mode,scale):
    pdf=tmp_path/'out.pdf'
    p=pdf_render._run(data(mode,scale),mode,'video-16x9',tmp_path,pdf)
    assert not p.errors
    ss=spans(pdf)
    code=[s for s in ss if 'int main' in s['text'] or 'return 0' in s['text']]
    assert code and all(abs(s['size']-12)<=.05 for s in code)
    assert all(abs(c['effective_pdf_pt']-12)<=.05 for c in p.geometry['p1']['code'])
    assert 'font-variant-ligatures: none' in pdf_render.load_template(mode,'video-16x9')
    assert any('x = 1' in s['text'] and abs(s['size']-12)>.05 for s in ss)

def test_missing_or_changed_font_rejected(tmp_path):
    import pdf_code
    pdf_code.check_font_assets()
    with patch.object(pdf_code,'FONT_DIR',tmp_path):
        with pytest.raises(PdfError):pdf_code.check_font_assets()
    import shutil
    shutil.copytree(pdf_code.FONT_DIR,tmp_path/'font')
    (tmp_path/'font/JetBrainsMono-Regular.ttf').write_bytes(b'changed')
    with patch.object(pdf_code,'FONT_DIR',tmp_path/'font'):
        with pytest.raises(PdfError):pdf_code.check_font_assets()

def test_long_line_wrap_preserves_text_and_indent(tmp_path):
    text='\t  '+('value += array[index];  '*20)+'// 한글 주석\n\n  done();\n'
    p=pdf_render.probe(data('answers',text=text),'answers','video-16x9',tmp_path)
    assert not p.errors and not p.overflow
    for c in p.geometry['p1']['code']:
        assert c['text']==text
        assert c['hanging_indent_ch']==2
        assert c['displayed_lines']
        assert len(c['displayed_lines'])>3
        assert all(r['x']+r['w']<=c['rect']['x']+c['rect']['w']+1 for r in c['displayed_lines'])

def test_long_code_paginates_at_fixed_size(tmp_path):
    import html
    from pdf_types import Block,Card,Pack
    from pdf_layout import plan_pages,check_coverage
    from pdf_cards import to_payload
    text=''.join(f'  value += {i}; // 주석\n' for i in range(65))
    block=Block('code','<pre><code>'+html.escape(text)+'</code></pre>',text)
    c=Card('p1','fixture','장말문제','Long code',(block,),(block,),'<p>42</p>','')
    pack=Pack(Path('/tmp/복습문제_0907_Fixture.html'),'fixture','0907','Fixture',(c,))
    with pdf_render.render_session():
        pages=plan_pages(pack,tmp_path/'layout')
        assert len(pages)>1 and check_coverage(pack,pages)==[]
        for name in ('problem','solution'):
            assert ''.join(b.text for p in pages for b in getattr(p,name))==text
        for mode in ('problems','answers'):
            payload=to_payload(pack,mode,pages,tmp_path/'assets')
            p=pdf_render.render(payload,mode,tmp_path/mode,tmp_path/(mode+'.pdf'))
            assert not p.errors and not p.overflow
            for g in p.geometry.values():
                assert all(abs(c['effective_pdf_pt']-12)<=.05 for c in g['code'])

def test_code_free_pages_keep_existing_layout(tmp_path):
    from test_pdf_ds_layout import test_browser_table_placement_and_condition_visibility
    test_browser_table_placement_and_condition_visibility()
    d=data('problems');d['problems'][0]['html']['code']=''
    p=pdf_render.probe(d,'problems','video-16x9',tmp_path)
    assert not p.geometry['p1']['code'] and '코드' not in p.geometry['p1']['labels']
