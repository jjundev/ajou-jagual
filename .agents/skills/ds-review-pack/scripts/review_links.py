"""Point a published page's review links at its corresponding worksheet."""
import html
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

from review_source import NAME, nfc

HTML_LINK = re.compile(r"""(\bhref\s*=\s*)(["'])([^"']+)\2""", re.I)
MD_LINK = re.compile(r"(\]\()([^\s)]+)(\))")


def rewrite(text: str, source: Path, pages: dict[str, int], *, markdown: bool = False) -> str:
    def pdf_target(value: str) -> str:
        url = urlsplit(html.unescape(value))
        if url.scheme or url.netloc or not url.path:
            return value
        path = Path(unquote(url.path))
        if not NAME.fullmatch(nfc(path.name)) or nfc(path.name) != nfc(source.name):
            return value
        target = quote(path.with_name(nfc(path.stem) + "-문제.pdf").as_posix(), safe="/")
        page = pages.get(unquote(url.fragment))
        return f"{target}#page={page}" if page else target

    return _rewrite_links(text, pdf_target, markdown)


def refresh_pages(text: str, source: Path, prior: dict[str, int], current: dict[str, int], *, markdown: bool = False) -> str:
    """Move links from a verified old PDF page to the same question's new page."""
    previous = {number: pid for pid, number in prior.items()}
    pdf_name = nfc(source.stem) + "-문제.pdf"

    def find_page(value: str) -> str:
        url = urlsplit(html.unescape(value))
        match = re.fullmatch(r"page=([1-9]\d*)", url.fragment)
        if url.scheme or url.netloc or not match or nfc(Path(unquote(url.path)).name) != pdf_name:
            return value
        new_page = current.get(previous.get(int(match[1]), ""))
        target = value.partition("#")[0]
        return f"{target}#page={new_page}" if new_page else target

    return _rewrite_links(text, find_page, markdown)


def _rewrite_links(text, replace, markdown: bool) -> str:
    text = HTML_LINK.sub(lambda m: m[1] + m[2] + replace(m[3]) + m[2], text)
    if markdown:
        text = MD_LINK.sub(lambda m: m[1] + replace(m[2]) + m[3], text)
    return text


def add_pdf_links(text: str, source: Path, *, markdown: bool = False) -> str:
    problem, answer = (quote(nfc(source.stem) + tail, safe="") for tail in ("-문제.pdf", "-답안.pdf"))
    if markdown:
        block = f"\n[문제지 PDF](../{problem}) · [답안지 PDF](../{answer})\n"
        if f"](../{answer})" not in text and f"]({answer})" not in text:
            return text.rstrip() + "\n" + block
        return text
    if f'href="{answer}"' in text or f'href="{source.stem}-답안.pdf"' in text:
        return text
    block = f'<p class="review-pdfs"><a href="{problem}">문제지 PDF</a> · <a href="{answer}">답안지 PDF</a></p>'
    at = text.find("</article>", text.find('id="s3-links"'))
    if at < 0:
        at = text.rfind("</main>")
    if at < 0:
        raise ValueError("정리노트 PDF 링크 위치가 없어요")
    return text[:at] + block + "\n" + text[at:]
