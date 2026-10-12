"""Code blocks keep code bytes and distinguish standalone snippets from prose."""
import html
import re
from helpers import fragment, source_file
from mpe_source import load_source
from mpe_shared import parse
from mpe_render import build_explanation


def render(tmp_path, extra='', no_source_code=False):
    repo = tmp_path / 'repo'
    source = source_file(repo)
    if no_source_code:
        source.write_text(source.read_text().replace('<pre><code>printf("$%d", n);</code></pre>', ''))
    pack = load_source(source, repo)
    return build_explanation(pack, {'p1': fragment(pack.problems[0]) + extra}, tmp_path / 'stage', repo)


def test_code_block_style_uses_theme_tokens(tmp_path):
    art = render(tmp_path)
    css = art.html.read_text()
    pre = re.search(r'pre \{([^}]+)\}', css).group(1)
    for rule in ('background: var(--surface)', 'color: var(--ink)', 'border: 1px solid var(--line)',
                 'padding: var(--s4)', 'border-radius: var(--radius)', 'margin: var(--s4) 0',
                 'box-sizing: border-box', 'min-width: 0', 'max-width: 100%', 'overflow-x: auto',
                 'white-space: pre', 'tab-size: 4', 'font-size: 14px', 'line-height: 1.6',
                 'font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'):
        assert rule in pre
    code = re.search(r'pre > code \{([^}]+)\}', css).group(1)
    for rule in ('font: inherit', 'color: inherit', 'background: none', 'border: 0', 'margin: 0', 'padding: 0'):
        assert rule in code


def test_code_and_output_whitespace_preserved(tmp_path):
    code = 'if (a < b && p) {\n\tprintf("$%d", n);\n\n}\n'
    output = '$1\n$2\n'
    art = render(tmp_path, ''.join('<pre><code>' + html.escape(s) + '</code></pre>' for s in (code, output)))
    blocks = [n.text() for n in parse(art.html.read_text()).find_all(lambda n: n.tag == 'pre')]
    for value in (code, output):
        assert value in blocks
        assert value in art.md.read_text()


def test_pack_without_code_has_no_empty_pre(tmp_path):
    art = render(tmp_path, no_source_code=True)
    assert not list(parse(art.html.read_text()).find_all(lambda n: n.tag == 'pre'))
