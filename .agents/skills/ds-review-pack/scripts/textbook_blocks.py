"""Render verified source blocks without inferred answers or observations."""
from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ET.register_namespace('', 'http://www.w3.org/2000/svg')

def _svg(catalog, asset_id, prefix):
    asset=catalog.assets[asset_id]
    if asset.get('review',{}).get('status')!='verified':
        raise ValueError(f'검수 전 asset: {asset_id}')
    path=(catalog.package/asset['path']).resolve()
    if not path.is_relative_to(catalog.package.resolve()):
        raise ValueError('unsafe asset path')
    root=ET.fromstring(path.read_text(encoding='utf8'))
    ids={node.attrib['id']:f'{prefix}-{asset_id}-{node.attrib["id"]}' for node in root.iter() if 'id' in node.attrib}
    for node in root.iter():
        if node.tag.split('}')[-1] in {'script','foreignObject','image'}:
            raise ValueError('unsafe SVG element')
        for key,value in list(node.attrib.items()):
            if key.lower().startswith('on'):
                raise ValueError('unsafe SVG handler')
            if key=='id':node.set(key,ids[value]);continue
            if key.split('}')[-1]=='href':
                if not value.startswith('#') or value[1:] not in ids:raise ValueError('broken SVG href')
                value='#'+ids[value[1:]]
            def ref(match):
                name=match.group(1)
                if name not in ids:raise ValueError('broken SVG reference')
                return 'url(#'+ids[name]+')'
            node.set(key,re.sub(r'url\(#([^)]*)\)',ref,value))
    width = float(root.attrib['viewBox'].replace(',', ' ').split()[2])
    root.set('role','img');root.set('aria-label',asset['alt']);root.set('style',f'background:white;width:{width:g}px;max-width:none;height:auto')
    return ET.tostring(root,encoding='unicode')

def render_blocks(blocks, catalog, *, prefix):
    out=[]
    for index,b in enumerate(blocks):
        kind=b['type']
        if kind=='text':out.append('<p>'+escape(b['text'])+'</p>')
        elif kind=='code':out.append('<pre><code>'+escape(b['text'])+'</code></pre>')
        elif kind in {'figure','table'}:
            a=catalog.assets[b['asset_id']]
            out.append('<figure style="margin:16px 0"><div class="figure-scroll" style="max-width:100%;overflow-x:auto;background:white">'+_svg(catalog,b['asset_id'],f'{prefix}-{index}')+'</div><figcaption>'+escape(a['alt'])+' · 넓은 그림은 옆으로 스크롤해 보세요.</figcaption></figure>')
        elif kind=='subquestions':
            out.append('<div class="subquestions">'+''.join('<div><p>('+escape(i['label'])+')</p>'+render_blocks(i['content'],catalog,prefix=f'{prefix}-{index}-{j}')+'</div>' for j,i in enumerate(b['items']))+'</div>')
        else:raise ValueError(f'unknown block: {kind}')
    return ''.join(out)

def render_question(catalog, question_id, *, prefix):
    q=catalog.questions[question_id]
    return render_blocks(q['content'],catalog,prefix=prefix)+'<div class="options">'+''.join('<div class="option"><p>('+escape(o['label'])+')</p>'+render_blocks(o['content'],catalog,prefix=f'{prefix}-option-{i}')+'</div>' for i,o in enumerate(q['options']))+'</div>'
