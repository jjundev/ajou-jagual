import xml.etree.ElementTree as ET
import pytest
from assets import validate_model,render_svg,validate_svg,svg_payload_text

def model(kind,data,layout=None):return {'id':'test','kind':kind,'data':data,'layout':layout or {}}

def test_right_child_and_xml_escape():
    m=model('tree',{'root':'A','nodes':[{'id':'A','label':'A<&','left':None,'right':'B'},{'id':'B','label':'B','left':None,'right':None}]})
    assert validate_model(m)==[];s=render_svg(m,'alt');assert validate_svg(s)==[]
    root=ET.fromstring(s);nodes={n.attrib['id']:n for n in root.findall('.//{*}g') if 'id' in n.attrib}
    assert float(nodes['B'].find('{*}circle').attrib['cx'])>float(nodes['A'].find('{*}circle').attrib['cx'])
    assert 'A<&' in svg_payload_text(s)

def test_graph_directed_parallel_loop():
    m=model('graph',{'nodes':[{'id':'a','label':'A'},{'id':'b','label':'B'}],'edges':[{'id':'e1','from':'a','to':'b','directed':True,'label':'','weight':None},{'id':'e2','from':'a','to':'b','directed':False,'label':'2','weight':None},{'id':'e3','from':'a','to':'a','directed':True,'label':'','weight':None}]})
    assert not validate_model(m);s=render_svg(m,'alt');assert 'e3' in s and 'polygon' in s
    m['data']['edges'][0]['to']='missing';assert validate_model(m)

def test_array_empty_and_pointer():
    m=model('array',{'cells':[{'index':0,'value':''},{'index':1,'value':'B'}],'pointers':[{'label':'front','index':0}]})
    assert not validate_model(m);s=render_svg(m,'alt');assert 'cell-0' in s and 'front' in s
    m['data']['pointers'][0]['index']=3;assert validate_model(m)

def test_table_merged_coverage():
    m=model('table',{'rows':2,'cols':2,'cells':[{'row':0,'col':0,'text':'head','rowspan':1,'colspan':2,'header':True},{'row':1,'col':0,'text':'','rowspan':1,'colspan':1,'header':False},{'row':1,'col':1,'text':'<&','rowspan':1,'colspan':1,'header':False}]})
    assert not validate_model(m);s=render_svg(m,'alt');assert svg_payload_text(s)==['head','<&']
    m['data']['cells'].pop();assert validate_model(m)

@pytest.mark.parametrize('tag',['script','image','foreignObject'])
def test_unsafe_svg(tag):assert validate_svg(f'<svg xmlns="http://www.w3.org/2000/svg"><{tag}/></svg>')

def test_vector_image_rejected():
    m=model('vector',{'entities':[],'primitives':[{'tag':'image','attrs':{'href':'x'}}]});assert validate_model(m)

def test_array_without_printed_indices():
    m=model('array',{'cells':[{'index':0,'value':'7'},{'index':1,'value':'4'}],'pointers':[]},{'show_indices':False})
    assert svg_payload_text(render_svg(m,'alt'))==['7','4']

def test_wide_table_fits_viewbox():
    m=model('table',{'rows':1,'cols':10,'cells':[{'row':0,'col':i,'text':'2','rowspan':1,'colspan':1,'header':False} for i in range(10)]},{'width':700,'height':100})
    root=ET.fromstring(render_svg(m,'alt'))
    assert all(float(e.attrib['x'])+float(e.attrib['width'])<=700 for e in root.findall('.//{*}rect'))

def test_explicit_edge_label_positions():
    m=model('graph',{'nodes':[{'id':'a','label':'0'},{'id':'b','label':'3'}],'edges':[{'id':'ab','from':'a','to':'b','directed':True,'label':'','weight':'10'},{'id':'ba','from':'b','to':'a','directed':True,'label':'','weight':'20'}]},{'width':300,'height':300,'positions':{'a':[150,70],'b':[150,230]},'curves':{'ab':25,'ba':25},'label_positions':{'ab':[90,150],'ba':[210,150]}})
    root=ET.fromstring(render_svg(m,'alt'));positions={e.text:(float(e.attrib['x']),float(e.attrib['y'])) for e in root.findall('.//{*}text')}
    assert positions[' 10']==(90,150) and positions[' 20']==(210,150)

def test_weighted_loop_renders():
    m=model('graph',{'nodes':[{'id':'a','label':'A'}],'edges':[{'id':'loop','from':'a','to':'a','directed':True,'label':'','weight':'3'}]},{'positions':{'a':[200,200]}})
    assert ' 3' in svg_payload_text(render_svg(m,'alt'))

def test_css_escaped_external_url_rejected():
    assert validate_svg('<svg xmlns="http://www.w3.org/2000/svg"><rect fill="u\\72l(//example.org/x)"/></svg>')
