import json
import pytest
from _util import SCRIPTS
from review_inventory import collect_reviews

def make_pack(repo, date, source='exam-one'):
    root=repo/'복습노트'/date
    data=root/'.pack'/'자료_복습팩'
    data.mkdir(parents=True)
    (data/'manifest.json').write_text(json.dumps({'range':date,'problems':[{'id':'p1','source':source}]}))
    review=root/f'복습문제_{date}_Test.html'
    review.write_text(f'<article class="card" id="p1" data-source="{source}"><div class="question">Q<pre>x=1;</pre></div><details class="original">original</details></article>')
    return review

def test_root_reviews_only_nfd_and_overlay(tmp_path):
    make_pack(tmp_path,'0914')
    make_pack(tmp_path,'0917','other')
    (tmp_path/'복습노트'/'0914'/'.pack'/'복습문제_backup.html').write_text('bad')
    stage=tmp_path/'stage'
    overlay=make_pack(stage,'0917','replacement')
    rows=collect_reviews(tmp_path,overlays={'0917':overlay})
    assert [r['range'] for r in rows]==['0914','0917']
    assert rows[1]['review_path']==str(overlay.resolve())
    assert 'original' not in rows[0]['cards'][0]['statement_html']

@pytest.mark.parametrize('change',['source','missing','extra'])
def test_manifest_card_mismatch_fails(tmp_path,change):
    path=make_pack(tmp_path,'0914')
    text=path.read_text()
    if change=='source': text=text.replace('exam-one','different')
    elif change=='missing': text=''
    else: text+=text.replace('p1','p2')
    path.write_text(text)
    with pytest.raises(ValueError,match='manifest'):
        collect_reviews(tmp_path)

def test_question_image_bytes_bind_content_hash(tmp_path):
    path=make_pack(tmp_path,'0914')
    path.write_text(path.read_text().replace('Q<pre>','<img src="figure.svg">Q<pre>'))
    picture=path.parent/'figure.svg';picture.write_text('<svg>one</svg>')
    before=collect_reviews(tmp_path)[0]['cards'][0]['content_sha256']
    picture.write_text('<svg>two</svg>')
    after=collect_reviews(tmp_path)[0]['cards'][0]['content_sha256']
    assert before!=after
