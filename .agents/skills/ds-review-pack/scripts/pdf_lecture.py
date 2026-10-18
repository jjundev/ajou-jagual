"""Split lecture-code problem prose into PDF conditions and asks."""
import html, re
from pdf_types import Block, PdfError

ASK = re.compile(r'(?:세요|시오|하라|보라)[.)]?$|\?$')
TRAILING_NOTE = re.compile(r'\s*\([^()]*\)(?=[.?!]?$)')
CITATION = re.compile(r'S\d+ p\d+(?: · 추가 근거 p\d+(?:,\d+)*)?')
BADGE = re.compile(r'<span class="badge">.*?</span>')

def text(s: str) -> str:
    return html.unescape(re.sub(r'<[^>]+>', '', s)).strip()

def squash(s: str) -> str:
    return re.sub(r'\s+', '', text(s))

def sentences(inner: str) -> list[str]:
    out, start, depth, math, i = [], 0, 0, False, 0
    while i < len(inner):
        ch = inner[i]
        if ch == '<':
            j = inner.index('>', i)
            tag = inner[i:j + 1]
            if not tag.endswith('/>') and not re.match(r'<(br|img|hr)\b', tag):
                depth += -1 if tag.startswith('</') else 1
            i = j + 1; continue
        if ch == '$': math = not math
        if ch in '.?!' and depth == 0 and not math and i + 1 < len(inner) and inner[i + 1].isspace():
            out.append(inner[start:i + 1].strip()); start = i + 1
        i += 1
    tail = inner[start:].strip()
    return out + ([tail] if tail else [])

def is_ask(sentence: str) -> bool:
    return bool(ASK.search(TRAILING_NOTE.sub('', text(sentence))))

def inner_p(block_html: str) -> str:
    return re.sub(r'</p>\s*$', '', re.sub(r'^\s*<p\b[^>]*>', '', block_html)).strip()

def assert_lossless(source_html: str, out_html: str) -> None:
    if sorted(squash(out_html)) != sorted(squash(source_html)):
        raise PdfError(f'lecture split lost text: {text(source_html)[:40]}')

def is_badge(block: Block) -> bool:
    if 'class="badge"' not in block.html:
        return False
    if not CITATION.fullmatch(text(BADGE.sub('', inner_p(block.html)))):
        raise PdfError(f'badge paragraph has more than a citation: {text(block.html)[:40]}')
    return True

def split_lecture_problem(blocks: tuple[Block, ...]) -> tuple[str, str]:
    kept = [b for b in blocks if not is_badge(b)]
    notes = [b for b in kept if text(b.html).startswith('후속 수업 보충')]
    body = [b for b in kept if b not in notes]
    caption = ''.join(f'<p class="ds-source">{inner_p(b.html)}</p>' for b in notes)
    original = ''.join(b.html for b in body)
    if any(re.match(r'\s*<[ou]l\b', b.html) for b in body):
        return caption, original
    parts = [s for b in body for s in sentences(inner_p(b.html))]
    asks = [s for s in parts if is_ask(s)]
    if not asks:
        return caption, original
    cond = caption + ''.join(f'<p>{s}</p>' for s in parts if not is_ask(s))
    ask = '<ol class="ds-asks">' + ''.join(f'<li>{s}</li>' for s in asks) + '</ol>'
    assert_lossless(''.join(b.html for b in kept), cond + ask)
    return cond, ask
