"""DS-only structural extension; frozen EC2 assets remain unchanged."""
from pdf_types import PdfError

PANEL = "panel.append(block('조건', p.html.conditions, 'conditions'), block('구할 것', p.html.ask, 'ask-box'));"
REPLACEMENT = """if (p.html.conditions && p.html.conditions.replace(/<[^>]*>/g, '').replace(/&nbsp;|&#160;/g, ' ').trim()) panel.append(block('조건', p.html.conditions, 'conditions'));
  if (p.html.ask) panel.append(block('구할 것', p.html.ask, 'ask-box'));
  if (p.html.code) panel.append(block('코드', p.html.code, 'code-box'));"""


def extend(template, mode, layout="a4"):
    template=template.replace('function renderMath(root) {', """function dsDecorateCode(root) {
  for (const pre of root.querySelectorAll('pre')) {
    const code=pre.querySelector('code') || pre;
    if (code.dataset.dsWrapped) continue;
    const text=code.textContent;
    code.replaceChildren();
    for (const line of text.match(/[^\\n]*\\n|[^\\n]+$/g) || []) {
      const span=document.createElement('span'); span.className='ds-code-line';
      span.textContent=line; code.append(span);
    }
    code.dataset.dsWrapped='true';
    if (code.textContent!==text) throw new Error('Code decoration changed source');
  }
}
function renderMath(root) { dsDecorateCode(root);""")
    if template.count(PANEL) != 1:
        raise PdfError('Frozen EC2 panel extension anchor changed')
    template = template.replace(PANEL, REPLACEMENT)
    if mode == 'problems':
        anchor = "center.append(el('div', 'work'));"
        if template.count(anchor) != 1:
            raise PdfError('Frozen EC2 workspace extension anchor changed')
        template = template.replace(anchor, """const work = el('div', 'work');
  if (p.workspace_html) work.append(el('div', 'prose ds-worksheet', p.workspace_html));
  center.append(work);""")
    from pdf_code import code_css
    template=template.replace('</head>', '<style>'+code_css(layout)+'</style></head>')
    return template.replace('</head>', '<style>.ds-worksheet { padding: 5mm; background: var(--paper); } .ds-worksheet table, .panel table { width: 100%; border-collapse: collapse; } .ds-worksheet th, .ds-worksheet td, .panel th, .panel td { border: 1px solid #888; padding: 2mm; height: 6mm; } .code-box pre { white-space: pre; background: var(--paper); padding: 2mm; border-radius: 1mm; margin: 0; } .code-box pre + pre { margin-top: 2mm; }</style></head>')


def extension_hash():
    import hashlib
    from pathlib import Path
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def check_extension(report):
    if report.get('layout_extension_sha256') != extension_hash():
        raise PdfError('DS layout extension changed since build')
