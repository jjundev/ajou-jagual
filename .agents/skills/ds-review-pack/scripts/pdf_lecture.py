"""Split lecture-code problem prose into PDF conditions and asks."""
import html, re
from pdf_types import Block, PdfError

ASK = re.compile(r'(?:세요|시오|하라|보라)[.)]?$|\?$')
TRAILING_NOTE = re.compile(r'\s*\([^()]*\)(?=[.?!]?$)')

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

def split_lecture_problem(blocks: tuple[Block, ...]) -> tuple[str, str]:
    kept = [b for b in blocks if 'class="badge"' not in b.html]
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
    if squash(''.join(parts)) != squash(original) or squash(cond + ask) != squash(caption) + ''.join(
            squash(s) for s in parts if not is_ask(s)) + ''.join(squash(s) for s in asks):
        raise PdfError(f'lecture split lost text: {text(original)[:40]}')
    return cond, ask
