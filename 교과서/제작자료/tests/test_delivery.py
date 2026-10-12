import html,json,copy,shutil
from pathlib import Path
import pytest
from preview import render_preview
from publish import publish_package,package_fingerprint

def test_html_escapes_and_code_preserved():
    package=Path(__file__).parents[1].parent;b=__import__('publish').load_bank(package);m=json.loads((package/'제작자료/asset-models.json').read_text())
    b['questions'][0]['content']=[{'type':'code','language':'c','text':'printf("%d\\n", n); if (n < 1 && p != NULL) return 0; <script>'}]
    doc=render_preview(b,m);assert '<script>' not in doc;assert 'if (n < 1 && p != NULL)' in html.unescape(doc);assert '../assets/' in doc and '../origin/' in doc

def test_publish_rejects_incomplete_and_existing(tmp_path):
    p=tmp_path/'package';p.mkdir();(p/'제작자료').mkdir();d=tmp_path/'dest';d.mkdir()
    with pytest.raises(ValueError):publish_package(p,d)
    assert not list(d.glob('[0-9][0-9]_*_연습문제.json'))

def test_fingerprint_changes(tmp_path):
    (tmp_path/'제작자료').mkdir();(tmp_path/'assets').mkdir();(tmp_path/'01_test_연습문제.json').write_text('{}')
    for f in ['inventory.json','asset-models.json','preview.html']:(tmp_path/'제작자료'/f).write_text('{}')
    before=package_fingerprint(tmp_path);(tmp_path/'제작자료/preview.html').write_text('changed');assert package_fingerprint(tmp_path)!=before
from test_validation import candidate
from publish import verify_package

def write_chapters(package,bank):
    for chapter in bank['chapters']:
        sids=set(chapter['source_ids'])
        part={**bank,'chapters':[chapter],'sources':[s for s in bank['sources'] if s['id'] in sids],'questions':[q for q in bank['questions'] if q['chapter_id']==chapter['id']],'assets':[a for a in bank['assets'] if any(r['source_id'] in sids for r in a['source_refs'])]}
        (package/f"{chapter['number']:02d}_{chapter['title']}_연습문제.json").write_text(json.dumps(part,ensure_ascii=False))

def sealed_package(candidate):
    b,i,m,p=candidate;s=p/'제작자료';s.mkdir();write_chapters(p,b);(s/'inventory.json').write_text(json.dumps(i,ensure_ascii=False));(s/'asset-models.json').write_text(json.dumps(m,ensure_ascii=False));(s/'preview.html').write_text('test preview')
    manifest={'schema_version':1,'package_sha256':package_fingerprint(p),'origin_sha256':{s['id']:s['sha256'] for s in b['sources']},'content_review':{'status':'verified','notes':['synthetic test']},'asset_reviews':[{'id':a['id'],'sha256':a['sha256'],'status':'verified','notes':['synthetic test']} for a in b['assets']],'browser_reviews':[{'viewport':v,'theme':t,'status':'verified','notes':['synthetic test']} for v in ['1280x900','375x812'] for t in ['light','dark']],'counts':{'chapters':14,'sources':14,'pages':44,'questions':213,'assets':46,'options':sum(len(q['options']) for q in b['questions']),'subquestions':sum(len(b['items']) for q in b['questions'] for b in __import__('model').question_blocks(q) if b['type']=='subquestions'),'figures':sum(m['kind']!='table' for m in m['models']),'tables':sum(m['kind']=='table' for m in m['models'])},'unresolved':[]};(s/'verification.json').write_text(json.dumps(manifest));return p

def destination_with_origins(package,tmp_path):
    d=tmp_path/'destination';d.mkdir();shutil.copytree(package/'origin',d/'origin');return d

def test_manifest_counts_must_match(candidate):
    p=sealed_package(candidate);f=p/'제작자료/verification.json';m=json.loads(f.read_text());m['counts']['questions']=0;f.write_text(json.dumps(m))
    with pytest.raises(ValueError):verify_package(p)

def test_copy_time_mutation_rejected(candidate,tmp_path,monkeypatch):
    import publish
    p=sealed_package(candidate);d=destination_with_origins(p,tmp_path);real=publish.shutil.copy2;changed=False
    def copy(src,dst,*args,**kwargs):
        nonlocal changed
        if not changed and str(src).endswith('.svg'):
            changed=True;Path(src).write_text(Path(src).read_text()+'<!-- changed after validation -->')
        return real(src,dst,*args,**kwargs)
    monkeypatch.setattr(publish.shutil,'copy2',copy)
    with pytest.raises(ValueError):publish_package(p,d)
    assert not list(d.glob('[0-9][0-9]_*_연습문제.json'))

def test_rollback_preserves_foreign_replacement(candidate,tmp_path,monkeypatch):
    import publish
    p=sealed_package(candidate);d=destination_with_origins(p,tmp_path);real=publish.os.link;first=None;count=0
    def link(src,dst):
        nonlocal count,first
        count+=1
        if count==2:raise OSError('injected failure')
        real(src,dst);first=Path(dst);first.unlink();first.write_text('foreign replacement')
    monkeypatch.setattr(publish.os,'link',link)
    with pytest.raises(OSError):publish_package(p,d)
    assert first.exists() and first.read_text()=='foreign replacement'

def test_success_json_last_and_no_overwrite(candidate,tmp_path,monkeypatch):
    import publish
    p=sealed_package(candidate);d=destination_with_origins(p,tmp_path);linked=[];real=publish.os.link
    def link(src,dst):linked.append(Path(dst));return real(src,dst)
    monkeypatch.setattr(publish.os,'link',link);publish_package(p,d)
    assert linked[-1].name=='14_해싱_연습문제.json';assert (d/linked[-1].name).read_bytes()==(p/linked[-1].name).read_bytes()
    before={f:f.read_bytes() for f in linked}
    with pytest.raises(ValueError,match='conflict'):publish_package(p,d)
    assert all(f.read_bytes()==content for f,content in before.items())


def test_final_chapter_package_verifies():
    package=Path(__file__).parents[1].parent
    bank=verify_package(package)
    assert len(bank['chapters'])==14
    assert len(bank['questions'])==213

def test_publish_chapter_files_last(candidate,tmp_path,monkeypatch):
    import publish
    p=sealed_package(candidate);d=destination_with_origins(p,tmp_path);linked=[];real=publish.os.link
    def link(src,dst):linked.append(Path(dst));return real(src,dst)
    monkeypatch.setattr(publish.os,'link',link);publish_package(p,d)
    chapters=sorted(p.glob('[0-9][0-9]_*_연습문제.json'))
    assert len(chapters)==14
    assert [f.name for f in linked[-14:]]==[f.name for f in chapters]
    assert all((d/f.name).read_bytes()==f.read_bytes() for f in chapters)
