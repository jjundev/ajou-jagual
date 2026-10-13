#!/usr/bin/env python3
"""복습노트/<range>/ 폴더 배치: 루트에는 HTML·PDF와 .pack/ 만, 나머지는 전부 .pack/ 안.

.pack/ 안의 이름(figures_<range>/, 자료_PDF/, 자료_복습팩/, 자료_문제설명_*/, *.md)은 옛 루트 이름 그대로다.
그래서 과거 검증 기록 속 상대 경로는 .pack/ 기준으로 그대로 맞는다.

  python3 pack_layout.py check --repo REPO            # 모든 팩 배치 검사(오류면 종료 코드 1)
  python3 pack_layout.py migrate --repo REPO          # 옛 배치 팩 이전 계획만 출력(dry-run)
  python3 pack_layout.py migrate --repo REPO --apply  # 실제로 옮기고 링크를 고친다
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path
from urllib.parse import unquote

PACK_DIR = ".pack"
RANGE_RE = re.compile(r"\d{4}(?:-\d{4})?")
ROOT_SUFFIXES = (".html", ".pdf")
IGNORED = {".DS_Store"}
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
MD_LINK_RE = re.compile(r"(\]\()([^)\s]+)(\))")
MD_ATTR_RE = re.compile(r'((?:href|src)=")([^"]+)(")')
HTML_ATTR_RE = re.compile(r'((?:href|src)=")((?:자료_문제설명_|figures_문제설명_)[^"]*)(")')


def nfc(s) -> str:
    return unicodedata.normalize("NFC", str(s))


def pack_dir(root) -> Path:
    """팩 루트(날짜 폴더) → .pack/ 경로."""
    return Path(root) / PACK_DIR


def pdf_report_path(root) -> Path:
    return pack_dir(root) / "자료_PDF" / "pdf-validation.json"


def pack_folders(repo) -> list[Path]:
    notes = Path(repo) / "복습노트"
    if not notes.is_dir():
        return []
    return sorted((d for d in notes.iterdir() if d.is_dir() and RANGE_RE.fullmatch(nfc(d.name))),
                  key=lambda d: nfc(d.name))


def misplaced(root) -> list[str]:
    """루트에 있으면 안 되는 항목 이름(NFC). .pack/ 이 파일이면 그것도 오류다."""
    root = Path(root)
    bad = []
    for entry in sorted(root.iterdir(), key=lambda p: nfc(p.name)):
        name = nfc(entry.name)
        if name in IGNORED:
            continue
        if name == PACK_DIR:
            if not entry.is_dir():
                bad.append(name)
            continue
        if entry.is_file() and name.endswith(ROOT_SUFFIXES):
            continue
        bad.append(name)
    return bad


def check_layout(root) -> list[str]:
    root = Path(root)
    return [f"{nfc(root.name)}: 루트에 남은 항목(→ {PACK_DIR}/): {name}" for name in misplaced(root)]


def _pack_root(path: Path) -> Path | None:
    for a in (path, *path.parents):
        if nfc(a.parent.name) == "복습노트" and RANGE_RE.fullmatch(nfc(a.name)):
            return a
    return None


def current_path(path) -> Path:
    """이전 전 경로(복습노트/<range>/X)를 지금 위치로. 루트에 없으면 .pack/X 를 본다."""
    path = Path(path)
    if path.exists():
        return path
    root = _pack_root(path)
    if root is not None and path != root:
        moved = root / PACK_DIR / path.relative_to(root)
        if moved.exists():
            return moved
    return path


def current_digest(path, digest: str) -> str:
    """이전 전 경로의 해시를, 이전 때 링크만 고친 파일이면 고친 뒤 해시로 바꿔 준다(migration-*.json)."""
    path = Path(path)
    root = _pack_root(path)
    if root is None or path == root:
        return digest
    rel = nfc(path.relative_to(root).as_posix())
    for record in sorted((root / PACK_DIR).glob("migration-*.json")):
        rewritten = json.loads(record.read_text(encoding="utf-8")).get("rewritten", {})
        for key in (rel, f"{PACK_DIR}/{rel}"):
            entry = rewritten.get(key)
            if entry and entry.get("before") == digest:
                digest = entry["after"]
    return digest


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fix_md_target(target: str, data: Path) -> str:
    """.pack/ 로 옮긴 md 의 상대 링크: .pack/ 안에 있는 대상은 그대로, 아니면 ../ 를 붙인다."""
    path, _, _ = target.partition("#")
    if not path or SCHEME_RE.match(path) or path.startswith("/"):
        return target
    if (data / unquote(path)).exists() or (data / nfc(unquote(path))).exists():
        return target
    return "../" + target


def rewrite_md(text: str, data: Path) -> str:
    fix = lambda m: m.group(1) + _fix_md_target(m.group(2), data) + m.group(3)
    return MD_ATTR_RE.sub(fix, MD_LINK_RE.sub(fix, text))


def rewrite_explain_html(text: str) -> str:
    """문제설명 HTML 이 참조하는 설명 소유 자원(vendor·그림)을 .pack/ 아래로."""
    return HTML_ATTR_RE.sub(lambda m: m.group(1) + PACK_DIR + "/" + m.group(2) + m.group(3), text)


def migrate_pack(root, apply: bool) -> dict:
    """한 팩을 옮긴다. 충돌이 있으면 아무것도 옮기지 않고 errors 로 돌려준다."""
    root = Path(root)
    data = pack_dir(root)
    names = {nfc(p.name): p for p in root.iterdir()}
    moving = [n for n in misplaced(root) if n != PACK_DIR]
    result = {"pack": nfc(root.name), "move": moving, "rewrite": [], "errors": []}
    if data.exists() and not data.is_dir():
        result["errors"].append(f"{PACK_DIR} 이 파일임")
    for n in moving:
        if (data / n).exists():
            result["errors"].append(f"{PACK_DIR}/{n} 이미 있음")
    explain = [n for n, p in names.items() if p.is_file() and n.startswith("문제설명_") and n.endswith(".html")]
    result["rewrite"] = sorted(explain) + sorted(n for n in moving if n.endswith(".md"))
    if not moving or result["errors"] or not apply:
        return result
    record = {"date": time.strftime("%Y-%m-%d"), "moved": moving, "rewritten": {}}
    data.mkdir(exist_ok=True)
    for n in moving:
        shutil.move(str(names[n]), str(data / names[n].name))
    for n in sorted(explain):
        path = names[n]
        before = _sha(path)
        path.write_text(rewrite_explain_html(path.read_text(encoding="utf-8")), encoding="utf-8")
        record["rewritten"][n] = {"before": before, "after": _sha(path)}
    for n in sorted(x for x in moving if x.endswith(".md")):
        path = data / names[n].name
        before = _sha(path)
        path.write_text(rewrite_md(path.read_text(encoding="utf-8"), data), encoding="utf-8")
        record["rewritten"][f"{PACK_DIR}/{n}"] = {"before": before, "after": _sha(path)}
    out = data / f"migration-{record['date']}.json"
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("check", "migrate"))
    ap.add_argument("--repo", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    folders = pack_folders(a.repo)
    if a.command == "check":
        problems = [p for d in folders for p in check_layout(d)]
        for p in problems:
            print(p)
        print("OK" if not problems else f"FAIL ({len(problems)})")
        return int(bool(problems))
    failed = False
    for d in folders:
        r = migrate_pack(d, a.apply)
        if not r["move"]:
            continue
        failed |= bool(r["errors"])
        tag = "중단" if r["errors"] else ("이전" if a.apply else "계획")
        print(f"[{tag}] {r['pack']}: 옮김 {len(r['move'])}개, 링크 수정 {len(r['rewrite'])}개", *r["errors"], sep="\n  ")
    if not a.apply:
        print("dry-run: --apply 로 실행하면 옮긴다")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
