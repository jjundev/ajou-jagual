"""Immutable source and shared page contracts for PDF export."""
from dataclasses import dataclass
from pathlib import Path

class PdfError(ValueError):
    pass

@dataclass(frozen=True)
class Block:
    kind: str
    html: str
    text: str

@dataclass(frozen=True)
class Card:
    id: str
    source: str
    kind: str
    title: str
    problem: tuple[Block, ...]
    solution: tuple[Block, ...]
    answer_html: str
    hint_html: str

@dataclass(frozen=True)
class Pack:
    source: Path
    source_sha256: str
    range: str
    slug: str
    cards: tuple[Card, ...]

@dataclass(frozen=True)
class PageSlice:
    logical_id: str
    physical_id: str
    continuation: int
    problem: tuple[Block, ...]
    solution: tuple[Block, ...]
    show_answer: bool
    show_hint: bool

@dataclass(frozen=True)
class Probe:
    page_ids: tuple[str, ...]
    overflow: tuple[str, ...]
    errors: tuple[str, ...]
    geometry: dict
    typography: dict
