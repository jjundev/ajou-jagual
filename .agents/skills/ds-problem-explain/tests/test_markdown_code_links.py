"""Code examples are not Markdown links; prose links still require real targets."""
from mpe_shared import check_md


def test_inline_code_state_is_not_a_link_but_real_missing_link_is_checked(tmp_path):
    html = tmp_path / '문제설명_0101_Test.html'
    md = tmp_path / '.pack' / '문제설명_0101_Test.md'
    md.parent.mkdir()
    html.write_text('<html><body><main><p><code>[A](1) → [A,B](2)</code></p></main></body></html>')
    md.write_text('`[A](1) → [A,B](2)`\n')
    assert check_md(str(html), str(md)) == []

    # Same-line prose links must remain visible to the checker.
    md.write_text('`[A](1) → [A,B](2)` and [missing](missing.md)\n')
    assert check_md(str(html), str(md)) == ['링크 파일 없음: missing.md']

    # A real relative link is accepted only once its target exists.
    (md.parent / 'missing.md').write_text('A real target.\n')
    assert check_md(str(html), str(md)) == []
