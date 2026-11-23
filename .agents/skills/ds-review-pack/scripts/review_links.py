"""Inspect note links and keep problem explanation page links aligned."""
import html
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from review_source import nfc

HTML_LINK = re.compile(r"""(\bhref\s*=\s*)(["'])([^"']+)\2""", re.I)
MD_LINK = re.compile(r"(\]\()([^\s)]+)(\))")


HTML_ANCHOR = re.compile(r"""<a\b(?P<attrs>[^>]*)>(?P<label>.*?)</a\s*>""", re.I | re.S)
MD_DESTINATION = re.compile(
    r"(?:\]\(\s*|^ {0,3}\[[^\]\n]+\]:\s*)(?:<([^>\n]+)>|([^\s)]+))",
    re.M,
)
MD_AUTOLINK = re.compile(r"<((?:[a-z][a-z0-9+.-]*:)[^<>\s]+)>", re.I)


def is_pdf_link(value: str) -> bool:
    return unquote(urlsplit(html.unescape(value.strip())).path).lower().endswith(".pdf")


def markdown_link_targets(text: str):
    for match in MD_DESTINATION.finditer(text):
        yield match[1] or match[2]
    yield from MD_AUTOLINK.findall(text)


def is_working_review_link(value: str, source: Path) -> bool:
    url = urlsplit(html.unescape(value))
    return not (url.scheme or url.netloc) and nfc(unquote(url.path)) in {
        nfc(source.name), "./" + nfc(source.name),
    }


def unlink_working_review(text: str, source: Path) -> str:
    """Preserve the label of a link to the temporary HTML discarded at publish."""
    def replace(match):
        href = HTML_LINK.search(match["attrs"])
        if href and is_working_review_link(href[3], source):
            return match["label"]
        return match[0]

    return HTML_ANCHOR.sub(replace, text)


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
