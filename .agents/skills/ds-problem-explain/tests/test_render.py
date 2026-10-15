from dataclasses import replace
import json, re, base64, hashlib
from pathlib import Path
from urllib.parse import quote
import pytest
from helpers import fragment, source_file
from mpe_source import load_source, sha256
from mpe_shared import parse
from mpe_types import ExplainError
from mpe_render import build_explanation, check_artifacts
from test_skill_files import undo_overrides

def make(tmp_path):
    source=source_file(tmp_path/'repo');pack=load_source(source,tmp_path/'repo')
    p=pack.problems[0]
    return pack,{p.id:fragment(p)}

def test_legacy_statement_rendered_once(tmp_path):
    pack,fragments=make(tmp_path)
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    text=result.html.read_text();md=result.md.read_text()
    assert text.count('printf("$%d", n);')==1
    assert '구할 것</h4>' not in text
    assert 'printf("$%d", n);' in md
    assert 'ds-problem-explain-review-0917-Recursion' in text
    assert '자료구조및알고리즘이해' in text
    assert result.html.name=='문제설명_0917_Recursion.html'
    assert '이 문제를 봤을 때 떠올릴 개념과 공식' in md
    details=list(parse(text).find_all(lambda n:n.tag=='details'))
    assert len(details)==1 and 'original' in details[0].classes
    assert '왼쪽 목차로 문항을 고르고, 오른쪽 문제를 보며 해설을 따라가요.' in text
    assert md.index('printf') < md.index('이 문제를 봤을 때')
    assert 'https://cdn.' not in text

def test_problem_pane_wraps_statement_and_original(tmp_path):
    pack,fragments=make(tmp_path);result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    doc=parse(result.html.read_text())
    panes=list(doc.find_all(lambda n:'problem-pane' in n.classes))
    assert [n.attrs['data-problem-for'] for n in panes]==['p1']
    assert len(list(panes[0].find_all(lambda n:n.attrs.get('data-source-problem')=='p1')))==1
    original=[n for n in panes[0].find_all(lambda n:n.tag=='details')]
    assert len(original)==1 and 'original' in original[0].classes and '기출 원문 보기' in original[0].text()
    assert '주어진 조건</h4>' not in result.html.read_text()

def test_choice_model_is_empty(tmp_path):
    pack,fragments=make(tmp_path);text=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo').html.read_text()
    assert re.search(r'id="explain-choice-model">\{\}</script>',text)

def test_statement_and_original_sharing_svg_ids_stay_unique(tmp_path):
    pack,fragments=make(tmp_path)
    svg='<svg viewBox="0 0 10 10"><defs><marker id="m"></marker></defs><path marker-end="url(#m)" d="M0 0L5 5"></path></svg>'
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+svg,original_html=pack.problems[0].original_html+svg)
    pack=replace(pack,problems=(p,))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]

def test_problem_without_original_has_no_details(tmp_path):
    pack,fragments=make(tmp_path)
    pack=replace(pack,problems=(replace(pack.problems[0],original_html=''),))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    assert not list(parse(result.html.read_text()).find_all(lambda n:n.tag=='details'))

def test_template_bytes_match_pinned_ml():
    template=Path(__file__).resolve().parents[1]/'assets/note-template.html'
    provenance=json.loads((template.parent/'port-provenance.json').read_text())
    chain=[o for o in provenance.get('local_overrides',[]) if o['destination']=='assets/note-template.html']
    assert hashlib.sha256(template.read_bytes()).hexdigest()==chain[-1]['current_sha256']
    original=undo_overrides(template.read_bytes(),chain)
    assert hashlib.sha256(original).hexdigest()=='d0fe664a773920cf017ccf69fc9e7b69ef9a7c6b0b066601da36aaf1f338ba50'

def test_repeated_svg_ids_scoped(tmp_path):
    pack,fragments=make(tmp_path)
    second=replace(pack.problems[0],id='p2',number=2)
    pack=replace(pack,problems=(*pack.problems,second))
    svg='<svg viewBox="0 0 10 10"><defs><clipPath id="clip"><rect width="5" height="5"/></clipPath></defs><rect clip-path="url(#clip)" width="10" height="10"/></svg>'
    fragments={p.id:fragment(p)+svg for p in pack.problems}
    # Original-card anchors must exist in source too.
    pack.path.write_text(pack.path.read_text().replace('</section>','<article id="p2"></article></section>'))
    pack=replace(pack,sha256=sha256(pack.path))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    text=result.html.read_text();assert 'url(#p1-explain-clip)' in text and 'url(#p2-explain-clip)' in text

def test_nfd_image_link_and_missing_anchor(tmp_path):
    pack,fragments=make(tmp_path)
    image=pack.path.parent/'그림.png'
    image.write_bytes(base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jJ1sAAAAASUVORK5CYII='))
    fragments['p1']+='<figure><img src="%EA%B7%B8%EB%A6%BC.png" alt="그림"><figcaption>상태</figcaption></figure>'
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    assert re.search(r'!\[그림\]\(figures_[^)]+\.png\)',result.md.read_text())
    assert re.search(r'<img src="\.pack/figures_[^"]+\.png"',result.html.read_text())
    assert result.md.parent.name=='.pack'
    assert re.search(r'\]\(\.\./'+re.escape(quote(pack.path.name,safe=''))+r'#p1\)',result.md.read_text())
    with pytest.raises(ExplainError,match='앵커'):
        build_explanation(pack,{'p1':fragments['p1']+'<a href="'+pack.path.name+'#missing">x</a>'},tmp_path/'bad',tmp_path/'repo')

def test_missing_images_and_duplicate_svg_ids_refused(tmp_path):
    pack,fragments=make(tmp_path)
    for extra,match in [('<img src="missing.png">','경로|그림'),('<svg><g id="a"></g><g id="a"></g></svg>','중복.*ID')]:
        with pytest.raises(ExplainError,match=match):build_explanation(pack,{'p1':fragments['p1']+extra},tmp_path/match.replace('|',''),tmp_path/'repo')

def test_tampered_output_detected(tmp_path):
    pack,fragments=make(tmp_path);result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    result.html.write_text(result.html.read_text()+'changed')
    assert check_artifacts(pack,result)

def test_vendor_files_and_hashes_present():
    vendor=Path(__file__).resolve().parents[1]/'assets/vendor'
    manifest=json.loads((vendor/'provenance.json').read_text())
    for name,digest in manifest['files'].items(): assert sha256(vendor/name)==digest
    for css in vendor.rglob('*.css'):
        for href in re.findall(r"url\(['\"]?([^)'\"\s]+)",css.read_text()):assert (css.parent/href).is_file()

def test_original_c_comparison_is_preserved(tmp_path):
    path=source_file(tmp_path/'repo')
    path.write_text(path.read_text().replace('원래 질문','<pre><code>for(i=0; i&lt;n &amp;&amp; p!=NULL; i++){}</code></pre>'))
    pack=load_source(path,tmp_path/'repo');p=pack.problems[0]
    result=build_explanation(pack,{'p1':fragment(p)},tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    original=next(parse(result.html.read_text()).find_all(lambda n:n.attrs.get('data-original-problem')=='p1'))
    assert next(original.find_all(lambda n:n.tag=='code')).text()=='for(i=0; i<n && p!=NULL; i++){}'

def test_source_and_explanation_svg_ids_do_not_collide(tmp_path):
    path=source_file(tmp_path/'repo')
    svg='<svg viewBox="0 0 10 10"><defs><clipPath id="clip"><rect width="5" height="5"/></clipPath></defs><rect clip-path="url(#clip)" width="10" height="10"/></svg>'
    path.write_text(path.read_text().replace('</div>',''+svg+'</div>',1))
    pack=load_source(path,tmp_path/'repo');p=pack.problems[0]
    result=build_explanation(pack,{'p1':fragment(p)+svg},tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    ids=[n.attrs['id'] for n in parse(result.html.read_text()).find_all(lambda n:'id' in n.attrs)]
    assert len(ids)==len(set(ids))

def test_existing_source_figure_presentation_preserved(tmp_path):
    pack,fragments=make(tmp_path)
    figure='<figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white"><svg viewBox="0 0 1000 200" style="background:white;width:1000px;max-width:none;height:auto"><text x="1" y="20">A B C D</text></svg></div></figure>'
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+figure)
    pack=replace(pack,problems=(p,))
    art=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,art)==[]
    assert figure in art.html.read_text()

@pytest.mark.parametrize('style',['background:url(https://example.com/x)','width:expression(alert(1))','position:fixed','color:red'])
def test_source_style_allowance_is_narrow(tmp_path,style):
    pack,fragments=make(tmp_path)
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+f'<figure style="{style}">x</figure>')
    with pytest.raises(ExplainError,match='마크업'):
        build_explanation(replace(pack,problems=(p,)),fragments,tmp_path/'stage',tmp_path/'repo')

def test_authored_style_still_refused(tmp_path):
    pack,fragments=make(tmp_path)
    with pytest.raises(ExplainError,match='style'):
        build_explanation(pack,{'p1':fragments['p1']+'<figure style="margin:16px 0">x</figure>'},tmp_path/'stage',tmp_path/'repo')

def test_source_scroll_table_preserves_cells_and_static_width(tmp_path):
    pack,fragments=make(tmp_path)
    table='<div class="table-wrap" style="overflow-x:auto"><table style="min-width:500px"><tr><th>front</th><td>3</td><th>rear</th><td>5</td></tr></table></div>'
    p=replace(pack.problems[0],conditions_html=pack.problems[0].conditions_html+table,original_html=pack.problems[0].original_html+table)
    pack=replace(pack,problems=(p,))
    result=build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')
    assert check_artifacts(pack,result)==[]
    assert result.html.read_text().count('min-width:500px')==2

@pytest.mark.parametrize('style',['min-width:500px;position:fixed','min-width:500px;background:url(https://example.com/x)','min-width:0px'])
def test_source_scroll_table_does_not_allow_extra_style(tmp_path,style):
    pack,fragments=make(tmp_path)
    p=replace(pack.problems[0],conditions_html=f'<table style="{style}"><tr><td>x</td></tr></table>')
    pack=replace(pack,problems=(p,))
    with pytest.raises(ExplainError,match='style'):
        build_explanation(pack,fragments,tmp_path/'stage',tmp_path/'repo')

def test_problem_panel_left_of_content():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    bar=t[t.index('<header class="topbar">'):t.index('</header>')]
    assert bar.index('id="toggle-left"')<bar.index('id="toggle-prob"')<bar.index('class="brand"')<bar.index('id="toggle-right"')
    assert t.index('id="panel-left"')<t.index('id="panel-prob"')<t.index('<div class="content">')<t.index('id="panel-right"')
    right=t[t.index('id="panel-right"'):]
    assert 'id="tab-problem"' not in right and 'id="tab-summary"' not in t
    prob=t[t.index('id="panel-prob"'):t.index('<div class="content">')]
    assert 'id="tab-original"' in prob and 'data-side="prob"' in prob
    assert "'od-panels:' + kind + ':v2'" in t or "od-panels:explain:v2" in t

def test_problem_panel_dock_controls():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    assert '<div class="layout" data-left="open" data-prob="open" data-right="closed" data-prob-dock="left">' in t
    prob=t[t.index('id="panel-prob"'):t.index('<div class="content">')]
    group=prob[prob.index('class="prob-dock"'):]
    assert 'role="radiogroup"' in group and 'aria-label="문제 패널 위치"' in group and group.count('role="radio"')==3
    assert [d for d in ('left','right','float') if f'data-dock="{d}"' in group]==['left','right','float']
    assert group.index('data-dock="left"')<group.index('data-dock="right"')<group.index('data-dock="float"')
    assert 'class="float-move"' in prob and 'class="float-resize"' in prob and 'aria-label="문제 창 이동. 화살표로 이동"' in prob
    assert 'class="dock-preview"' in t and "PREF + ':prob'" in t

def test_template_is_ds_branded():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text()
    assert 'bio-' not in t and "const TAB = 'ds-problem-explain-tab';" in t
    assert '.verdict-card {' in t  # 판정 카드 코드는 비활성 상태로 남는다
