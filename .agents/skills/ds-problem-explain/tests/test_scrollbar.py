import re
from pathlib import Path

def test_explain_template_scrollbar():
    t=(Path(__file__).resolve().parents[1]/'assets/note-template.html').read_text(encoding='utf-8')
    assert len(re.findall(r'--scroll: #[0-9a-f]{6}; --scroll-hover: #[0-9a-f]{6};',t))==3
    assert t.count('--scroll: #c9d0db; --scroll-hover: #9aa3b2;')==1
    assert t.count('--scroll: #3f414b; --scroll-hover: #5b5e6a;')==2
    assert '::-webkit-scrollbar-thumb:hover { background: var(--scroll-hover); }' in t
    assert 'pre::-webkit-scrollbar-thumb { background: var(--scroll); border-radius: 8px; border: 2px solid var(--surface); }' in t
    assert 'scrollbar-color: var(--scroll) transparent;' in t
    assert '--scrollbar: 16px;' in t
    assert t.count('.katex-display, table)')==5
