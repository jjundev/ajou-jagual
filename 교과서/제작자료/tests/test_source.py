from pathlib import Path
import unicodedata, pytest, fitz
from source import resolve_local, inspect_sources, prepare_run, file_sha256

def test_unicode_and_escape(tmp_path):
    name=unicodedata.normalize("NFD","한글.txt"); (tmp_path/name).write_text("data")
    assert resolve_local(tmp_path,"한글.txt").name==name
    with pytest.raises(ValueError): resolve_local(tmp_path,"../outside")
    (tmp_path/"link").symlink_to("/tmp")
    with pytest.raises(ValueError): resolve_local(tmp_path,"link/outside")

def test_missing_duplicate(tmp_path):
    with pytest.raises(ValueError): inspect_sources(tmp_path)
    for i in range(1,15):
        doc=fitz.open(); doc.new_page(); doc.save(tmp_path/f"{i:02}_test.pdf")
    assert len(inspect_sources(tmp_path))==14
    (tmp_path/"01_duplicate.pdf").write_bytes((tmp_path/"01_test.pdf").read_bytes())
    with pytest.raises(ValueError): inspect_sources(tmp_path)

def test_prepare_keeps_bytes(tmp_path):
    origin=tmp_path/"origin";origin.mkdir()
    for i in range(1,15):
        doc=fitz.open();doc.new_page();doc.save(origin/f"{i:02}_test.pdf")
    before={p.name:file_sha256(p) for p in origin.iterdir()}
    package=prepare_run(origin,tmp_path/"run")
    assert before=={p.name:file_sha256(p) for p in (package/"origin").iterdir()}
    assert len(list((tmp_path/"run/pages").glob("*.png")))==14

def test_inside_symlink_rejected(tmp_path):
    (tmp_path/'real').write_text('data');(tmp_path/'alias').symlink_to(tmp_path/'real')
    with pytest.raises(ValueError):resolve_local(tmp_path,'alias')

def test_normalized_name_collision(tmp_path,monkeypatch):
    actual_iterdir=Path.iterdir
    def listing(path):
        if path==tmp_path:return iter([tmp_path/'한글.txt',tmp_path/unicodedata.normalize('NFD','한글.txt')])
        return actual_iterdir(path)
    monkeypatch.setattr(Path,'iterdir',listing)
    with pytest.raises(ValueError,match='ambiguous'):resolve_local(tmp_path,'한글.txt')
