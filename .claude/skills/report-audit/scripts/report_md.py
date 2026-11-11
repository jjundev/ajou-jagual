#!/usr/bin/env python3
"""Helpers for auditing one Notion-exported report Markdown file.

Subcommands:
  prose PATH                      numbered prose lines (code and image URLs hidden)
  check PATH --before REF         protected spans unchanged vs. a git revision or file
  code-compare PATH --source FILE report's full-source block vs. a .c file
  warnings PATH                   signed image URLs that expire or carry tokens

Exit codes: 0 ok, 1 difference found, 2 usage or file error.
"""

from __future__ import annotations

import argparse
import itertools
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Notion structural tags. Matched by name so escaped text such as `\<stdio.h\>`
# or `a \< b` is never mistaken for a tag.
_TAG = re.compile(
    r"</?(?:td|tr|table|colgroup|col|br|empty-block|table_of_contents)\b[^>]*?/?>"
)
_FENCE = re.compile(r"^\s*```")
_IMAGE = re.compile(r"(!\[[^\]]*\]\()([^)\s]+)(\))")
_ESCAPE = re.compile(r"\\([\\<>{}\[\]*~|_#`])")
_RUN_SCRIPT = re.compile(
    r"(?:^|\s)(\./run\s+\d+|EXIT_STATUS:\s*\d+|hw\d-(?:author-evidence|report-screenshots)[\w-]*|case-?\d+\.(?:txt|tty))"
)
_PROMPT = re.compile(r"[ㄱ-힣\w\s().~\-]{1,40}입력하세요[^:\n]{0,40}:")
_VOICE = re.compile(
    r"나는|내가|처음에|헷갈|시행착오|고쳤|수정했|생각했|이해했|보았다|느낀|어려|막혔|놓쳤|배운"
)
_OUT_OF_SCOPE = (
    (re.compile(r"O\(\s*[nN1]\s*\)"), "O(n)"),
    (re.compile(r"정의되지\s*않은\s*동작"), "정의되지 않은 동작"),
    (re.compile(r"undefined\s+behavior", re.IGNORECASE), "undefined behavior"),
    (re.compile(r"Best-?Fit|Worst-?Fit"), "Best/Worst-Fit"),
    (re.compile(r"MSVC"), "MSVC"),
    (re.compile(r"ISO\s*C"), "ISO C"),
    (re.compile(r"외부\s*단편화"), "외부 단편화"),
)
CODE_HEADER = "소스코드"
FULL_SOURCE_HEADING = re.compile(r"^#\s*전체 소스코드\s*$")


def _cell_text(line: str) -> str | None:
    match = re.match(r"^\s*<td>(.*)</td>\s*$", line)
    return match.group(1) if match else None


def _walk(text: str):
    """Yield (lineno, kind, payload) for every line.

    kind is one of: fence (inside a fenced block, including the fences),
    code_cell, prose_cell, struct (pure Notion structure), prose.
    """
    in_fence = False
    in_table = False
    row = -1
    cell = 0
    code_col: int | None = None
    for number, line in enumerate(text.splitlines(), start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            yield number, "fence", line
            continue
        if in_fence:
            yield number, "fence", line
            continue
        stripped = line.strip()
        if stripped.startswith("<table") and not stripped.startswith("<table_of_contents"):
            in_table, row, code_col = True, -1, None
            yield number, "struct", line
            continue
        if stripped == "</table>":
            in_table = False
            yield number, "struct", line
            continue
        if in_table and stripped == "<tr>":
            row += 1
            cell = 0
            yield number, "struct", line
            continue
        content = _cell_text(line) if in_table else None
        if content is not None:
            if row == 0 and content.strip() == CODE_HEADER:
                code_col = cell
            kind = "code_cell" if (row > 0 and cell == code_col) else "prose_cell"
            cell += 1
            yield number, kind, content
            continue
        if not _TAG.sub("", line).strip():
            yield number, "struct", line
            continue
        yield number, "prose", line


def _clean(raw: str) -> str:
    text = _IMAGE.sub(lambda m: m.group(1) + "URL" + m.group(3), raw)
    # Keep in-cell paragraph breaks visible: a short segment alone between
    # ¶ marks is a subheading that the 문장 category must see.
    text = re.sub(r"(?:<br\s*/?>){2,}", " ¶ ", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = _TAG.sub("", text)
    text = _ESCAPE.sub(r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def prose_lines(text: str) -> list[tuple[int, str]]:
    out = []
    for number, kind, payload in _walk(text):
        if kind in ("prose", "prose_cell"):
            cleaned = _clean(payload)
            if cleaned:
                out.append((number, cleaned))
    return out


def protected_spans(text: str) -> dict[str, list[str]]:
    blocks: list[str] = []
    current: list[str] | None = None
    code_cells: list[str] = []
    headings: list[str] = []
    for number, kind, payload in _walk(text):
        if kind == "fence":
            if current is None:
                current = [payload]
            else:
                current.append(payload)
                if _FENCE.match(payload) and len(current) > 1:
                    blocks.append("\n".join(current))
                    current = None
        elif kind == "code_cell":
            code_cells.append(payload)
        elif kind == "prose" and payload.lstrip().startswith("#"):
            headings.append(payload.strip())
    lines = text.splitlines()
    structure = [
        f"<table: {sum(l.strip().startswith('<table ') or l.strip() == '<table>' for l in lines)}",
        f"<tr>: {sum(l.strip() == '<tr>' for l in lines)}",
        f"<td>: {sum(_cell_text(l) is not None for l in lines)}",
    ]
    urls = [m.group(2) for m in _IMAGE.finditer(text)]
    return {
        "code blocks": blocks,
        "code cells": code_cells,
        "table structure": structure,
        "headings": headings,
        "image URLs": urls,
    }


def _first_difference(old: list[str], new: list[str]) -> str:
    if len(old) != len(new):
        return f"count {len(old)} -> {len(new)}"
    for index, (a, b) in enumerate(zip(old, new), start=1):
        if a != b:
            return f"item {index}: {a[:80]!r} -> {b[:80]!r}"
    return "order changed"


def compare_protected(before: str, after: str) -> list[tuple[str, str]]:
    old, new = protected_spans(before), protected_spans(after)
    return [
        (area, _first_difference(old[area], new[area]))
        for area in old
        if old[area] != new[area]
    ]


def read_before(ref: str, path: Path) -> str:
    candidate = Path(ref)
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    path = path.resolve()
    top = subprocess.run(
        ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    if top.returncode != 0:
        raise ValueError(f"{path.parent} is not in a git repository; pass a file path to --before")
    root = Path(top.stdout.strip()).resolve()
    relative = path.relative_to(root).as_posix()
    shown = subprocess.run(
        ["git", "-C", str(root), "show", f"{ref}:{relative}"],
        capture_output=True,
    )
    if shown.returncode != 0:
        raise ValueError(shown.stderr.decode("utf-8", "replace").strip())
    return shown.stdout.decode("utf-8")


def _full_source(md: str) -> str:
    lines = md.splitlines()
    start = None
    for index, line in enumerate(lines):
        if FULL_SOURCE_HEADING.match(line):
            start = index
    search_from = start if start is not None else 0
    fences = [i for i in range(search_from, len(lines)) if _FENCE.match(lines[i])]
    if start is None:
        # Fall back to the last fenced block in the file.
        fences = [i for i, l in enumerate(lines) if _FENCE.match(l)][-2:]
    if len(fences) < 2:
        raise ValueError("no fenced full-source code block found")
    return "\n".join(lines[fences[0] + 1:fences[1]])


def _tokens(code: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", code)


def _nonblank(code: str) -> list[str]:
    return [line.rstrip() for line in code.splitlines() if line.strip()]


def _style(code: str) -> str:
    indents = [len(l) - len(l.lstrip(" ")) for l in code.splitlines() if l.startswith(" ")]
    step = min((i for i in indents if i), default=0)
    own_line = sum(l.strip() == "{" for l in code.splitlines())
    same_line = sum(l.rstrip().endswith("{") and l.strip() != "{" for l in code.splitlines())
    brace = "next line" if own_line > same_line else "same line"
    return f"indent {step}, brace {brace}"


def code_compare(md: str, source: str) -> dict:
    report = _full_source(md)
    a, b = _tokens(report), _tokens(source)
    first = None
    if a != b:
        index = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        first = f"token {index}: {' '.join(a[index:index + 6])!r} vs {' '.join(b[index:index + 6])!r}"
    return {
        "tokens_equal": a == b,
        "format_differs": _nonblank(report) != _nonblank(source),
        "first_token_diff": first,
        "report_style": _style(report),
        "source_style": _style(source),
    }


def url_warnings(text: str) -> list[str]:
    out = []
    for index, match in enumerate(_IMAGE.finditer(text), start=1):
        query = parse_qs(urlparse(match.group(2)).query)
        if "X-Amz-Date" in query or "X-Amz-Security-Token" in query:
            date = query.get("X-Amz-Date", ["?"])[0]
            expires = query.get("X-Amz-Expires", ["?"])[0]
            token = "with security token" if "X-Amz-Security-Token" in query else "no token"
            out.append(f"image {index}: signed URL issued {date}, expires after {expires}s, {token}")
    return out


def _read(path: str) -> str:
    file = Path(path)
    if not file.is_file():
        raise FileNotFoundError(path)
    return file.read_text(encoding="utf-8")


def _signal_run_script_trace(text: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    for match in _RUN_SCRIPT.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        evidence = match.group(1)[:60]
        out.append(("run-script-trace", f"line {line_no}", evidence))
    return out


def _signal_output_block_smushed_prompts(text: str) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        matches = list(_PROMPT.finditer(line))
        if len(matches) < 2:
            continue
        smushed = False
        for a, b in zip(matches, matches[1:]):
            gap = line[a.end():b.start()]
            if not re.search(r"\d", gap):
                smushed = True
                break
        if smushed:
            evidence = f"{len(matches)} prompts: " + line.strip()[:60]
            out.append(("output-block-smushed-prompts", f"line {number}", evidence[:60]))
    return out


def _trigrams(s: str) -> set[str]:
    s = re.sub(r"\s+", " ", s).strip()
    return {s[i:i + 3] for i in range(max(0, len(s) - 2))}


def _signal_caption_duplication(text: str) -> list[tuple[str, str, str]]:
    captions: list[tuple[int, str]] = []
    for index, match in enumerate(_IMAGE.finditer(text), start=1):
        head = match.group(1)  # "![caption]("
        caption = head[2:-2]
        captions.append((index, caption))
    if len(captions) < 3:
        return []
    grams = [(i, _trigrams(c)) for i, c in captions]
    out: list[tuple[str, str, str]] = []
    for (i1, g1), (i2, g2) in itertools.combinations(grams, 2):
        if not g1 or not g2:
            continue
        jaccard = len(g1 & g2) / min(len(g1), len(g2))
        if jaccard >= 0.6:
            out.append(("caption-duplication", f"image {i1},{i2}", f"jaccard={jaccard:.2f}"))
    return out


def _signal_cell_prefix_repetition(text: str) -> list[tuple[str, str, str]]:
    cells: list[str] = []
    for _, kind, payload in _walk(text):
        if kind == "prose_cell":
            cleaned = _clean(payload)
            if cleaned:
                cells.append(cleaned)
    prefixes = [c[:8] for c in cells if len(c) >= 8]
    if len(prefixes) < 4:
        return []
    counts: dict[str, int] = {}
    for p in prefixes:
        counts[p] = counts.get(p, 0) + 1
    prefix, shared = max(counts.items(), key=lambda kv: kv[1])
    if shared / len(prefixes) >= 0.8:
        return [(
            "cell-prefix-repetition",
            "prose cells",
            f"{shared}/{len(prefixes)} start with {prefix!r}",
        )]
    return []


def _signal_out_of_scope_vocabulary(text: str) -> list[tuple[str, str, str]]:
    total = 0
    labels: list[str] = []
    for pattern, label in _OUT_OF_SCOPE:
        hits = pattern.findall(text)
        if hits:
            total += len(hits)
            labels.append(label)
    if total < 3:
        return []
    return [("out-of-scope-vocabulary", "whole text", f"count={total}; " + "/".join(labels))]


def _signal_no_personal_voice(text: str) -> list[tuple[str, str, str]]:
    prose = " ".join(t for _, t in prose_lines(text))
    if len(prose) < 200:
        return []
    if _VOICE.search(prose):
        return []
    return [("no-personal-voice", "whole prose", f"prose_chars={len(prose)}, markers=0")]


def style_signals(text: str, source: str | None = None) -> list[tuple[str, str, str]]:
    out: list[tuple[str, str, str]] = []
    out.extend(_signal_run_script_trace(text))
    out.extend(_signal_output_block_smushed_prompts(text))
    out.extend(_signal_caption_duplication(text))
    out.extend(_signal_cell_prefix_repetition(text))
    out.extend(_signal_out_of_scope_vocabulary(text))
    out.extend(_signal_no_personal_voice(text))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("prose").add_argument("path")
    check = sub.add_parser("check")
    check.add_argument("path")
    check.add_argument("--before", required=True, help="git revision (e.g. HEAD) or file path")
    compare = sub.add_parser("code-compare")
    compare.add_argument("path")
    compare.add_argument("--source", required=True)
    sub.add_parser("warnings").add_argument("path")
    signals = sub.add_parser("signals")
    signals.add_argument("path")
    signals.add_argument("--source", default=None)
    args = parser.parse_args(argv)
    try:
        text = _read(args.path)
        if args.command == "prose":
            for number, line in prose_lines(text):
                print(f"{number}\t{line}")
            return 0
        if args.command == "check":
            differences = compare_protected(read_before(args.before, Path(args.path)), text)
            if not differences:
                print("protected spans identical")
                return 0
            for area, detail in differences:
                print(f"CHANGED {area}: {detail}")
            return 1
        if args.command == "code-compare":
            result = code_compare(text, _read(args.source))
            for key, value in result.items():
                print(f"{key}: {value}")
            return 0 if result["tokens_equal"] and not result["format_differs"] else 1
        if args.command == "signals":
            found = style_signals(text, args.source)
            for name, loc, evidence in found:
                print(f"{name}\t{loc}\t{evidence}")
            graded = [row for row in found if row[1] != "skipped"]
            return 1 if graded else 0
        warnings = url_warnings(text)
        for line in warnings:
            print(line)
        return 1 if warnings else 0
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
