import importlib.util
import sys
import zipfile
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/export_standalone_note.py'
spec = importlib.util.spec_from_file_location('export_standalone_note', SCRIPT)
sn = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = sn
spec.loader.exec_module(sn)


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / 'repo'
    (repo / 'STT').mkdir(parents=True)
    (repo / '자료구조_강의록_2026').mkdir()
    for day in ('1008', '1015'):
        pack = repo / '복습노트' / day
        pack.mkdir(parents=True)
        (pack / '.pack').mkdir()
        (pack / '.pack/a.css').write_text('body{background:url("a.svg")}')
        (pack / '.pack/a.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (pack / '.pack/a.js').write_text('window.ready=1;//</script>')
        for kind in sn.KINDS:
            (pack / f'{kind}_{day}_Queue.html').write_text(
                '<!doctype html><html><head><meta charset="utf-8">'
                '<link href=".pack/a.css" rel="stylesheet">'
                '<script defer src=".pack/a.js" onload="window.loaded=1"></script>'
                '</head><body><h1 id="p1">큐</h1>'
                '<img src=".pack/a.svg"><a href="#p1">목차</a>'
                f'<a class="jump" href="복습문제_{day}_Queue.html#p1">문제</a>'
                '<a href="../1008/정리노트_1008_Queue.html#p1">이전</a>'
                '<a href="../../자료구조_강의록_2026/a.pdf">강의록</a>'
                '<a href="https://example.org">웹</a></body></html>', encoding='utf-8')
        for kind in ('문제', '답안'):
            (pack / f'복습문제_{day}_Queue-{kind}.pdf').write_bytes(b'%PDF-1.4\n' + kind.encode())
    return repo


def run(repo, tmp_path, *args):
    out = tmp_path / 'out'
    result = sn.export(repo, list(args), out)
    return result, out


def test_default_bundles_three_html_and_identical_pdfs(repo, tmp_path):
    result, out = run(repo, tmp_path, '1015')
    assert result.path.name == '자구알_복습노트_1015.zip'
    with zipfile.ZipFile(result.path) as z:
        assert len(z.namelist()) == 5
        for name in z.namelist():
            assert z.getinfo(name).flag_bits & 0x800
            if name.endswith('.pdf'):
                assert z.read(name) == (repo / '복습노트' / name).read_bytes()
        html = z.read('1015/문제설명_1015_Queue.html').decode()
        assert 'data:image/svg+xml;base64,' in html
        assert 'window.ready=1' in html and 'window.loaded=1' in html
        assert html.index('window.ready=1') > html.index('<h1')
        assert '<a href="#p1">' in html
        assert 'href="https://example.org"' in html
        assert '>강의록</span>' in html
    assert result.excluded


def test_kind_produces_one_html_without_pdfs(repo, tmp_path):
    result = sn.export(repo, ['1015'], tmp_path / 'out', kind='문제설명')
    assert result.path.suffix == '.html'
    assert result.path.name == '문제설명_1015_Queue.html'
    assert '<span class="jump">문제</span>' in result.path.read_text(encoding='utf-8')


def test_range_cross_date_links_and_fragments(repo, tmp_path):
    result, _ = run(repo, tmp_path, '1008-1015')
    with zipfile.ZipFile(result.path) as z:
        assert len(z.namelist()) == 10
        html = z.read('1015/문제설명_1015_Queue.html').decode()
        assert '../1008/' in html
        assert sn.check_bundle({n: z.read(n) for n in z.namelist()}) == []


def test_direct_html_path(repo, tmp_path):
    source = repo / '복습노트/1015/문제설명_1015_Queue.html'
    result, _ = run(repo, tmp_path, str(source))
    assert result.path.name == source.name


@pytest.mark.parametrize('names', [['1016'], ['1015-1008'], ['../'], []])
def test_invalid_selection_fails(repo, tmp_path, names):
    with pytest.raises(sn.ExportError):
        sn.export(repo, names, tmp_path / 'out')


def test_missing_specific_kind_and_duplicate_fail(repo, tmp_path):
    p = repo / '복습노트/1015/문제설명_1015_Queue.html'
    p.unlink()
    with pytest.raises(sn.ExportError):
        sn.export(repo, ['1015'], tmp_path / 'out', kind='문제설명')
    result, _ = run(repo, tmp_path, '1015')
    assert result.skipped
    p = repo / '복습노트/1015/정리노트_1015_Other.html'
    p.write_text('<html></html>')
    with pytest.raises(sn.ExportError):
        sn.export(repo, ['1015'], tmp_path / 'out')


def test_missing_asset_preserves_previous_output(repo, tmp_path):
    result, _ = run(repo, tmp_path, '1015')
    before = result.path.read_bytes()
    (repo / '복습노트/1015/.pack/a.svg').unlink()
    with pytest.raises(sn.ExportError):
        run(repo, tmp_path, '1015')
    assert result.path.read_bytes() == before


def test_original_output_collision_fails(repo):
    with pytest.raises(sn.ExportError):
        sn.export(repo, ['1015'], repo / '복습노트/1015', kind='정리노트')


def test_no_pdf_option(repo, tmp_path):
    result = sn.export(repo, ['all'], tmp_path / 'out', include_pdf=False)
    with zipfile.ZipFile(result.path) as z:
        assert len(z.namelist()) == 6


def test_unknown_remote_asset_fails(repo, tmp_path):
    p = repo / '복습노트/1015/정리노트_1015_Queue.html'
    p.write_text('<html><body><img src="https://unknown.example/a.png"></body></html>')
    with pytest.raises(sn.ExportError, match='외부'):
        run(repo, tmp_path, '1015')


def test_fragment_validation():
    data = {'a.html': b'<meta charset="utf-8"><a href="b.html#gone">x</a>',
            'b.html': b'<meta charset="utf-8"><h1 id="here">x</h1>'}
    assert sn.check_bundle(data)


def test_known_cdn_katex_is_inlined_without_confusing_parser_fetch(repo, tmp_path):
    p = repo / '복습노트/1015/정리노트_1015_Queue.html'
    p.write_text('<html><head><meta charset="utf-8">'
                 '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>'
                 '</head><body>수식</body></html>', encoding='utf-8')
    result = sn.export(repo, ['1015'], tmp_path / 'out', kind='정리노트')
    assert 'katex' in result.path.read_text(encoding='utf-8')


def test_window_fetch_is_rejected(repo, tmp_path):
    p = repo / '복습노트/1015/정리노트_1015_Queue.html'
    p.write_text('<meta charset="utf-8"><body><script>window.fetch("missing.json")</script></body>')
    with pytest.raises(sn.ExportError, match='동적'):
        sn.export(repo, ['1015'], tmp_path / 'out', kind='정리노트')


def test_file_uri_to_excluded_document_becomes_span(repo, tmp_path):
    p = repo / '복습노트/1015/정리노트_1015_Queue.html'
    p.write_text('<meta charset="utf-8"><body><a href="file:///C:/missing.pdf">자료</a></body>', encoding='utf-8')
    result = sn.export(repo, ['1015'], tmp_path / 'out', kind='정리노트')
    assert '<span>자료</span>' in result.path.read_text(encoding='utf-8')
    assert result.excluded


def test_svg_fragment_is_preserved(repo):
    asset = sn.Assets(repo)
    base = repo / '복습노트/1015/.pack'
    assert asset.uri('a.svg#blur', base).endswith('#blur')


@pytest.mark.parametrize('element', [
    '<script onload="fetch(\'missing.json\')">window.ready=1</script>',
    '<button onclick="fetch(\'missing.json\')">조회</button>',
])
def test_event_handler_dynamic_loading_is_rejected(repo, tmp_path, element):
    p = repo / '복습노트/1015/정리노트_1015_Queue.html'
    p.write_text('<meta charset="utf-8"><body>' + element + '</body>', encoding='utf-8')
    with pytest.raises(sn.ExportError, match='동적'):
        sn.export(repo, ['1015'], tmp_path / 'out', kind='정리노트')
