#!/usr/bin/env python3
"""자구알 기출 문제은행(문제은행.json) 검사·선별 도구 (표준 라이브러리만 사용).

CLI:
  bank.py validate BANK                                              # 스키마 검사 → OK
  bank.py select BANK --range-ch 2,3 --taught 1-3 [--used-dir DIR]   # 후보를 우선순위 순으로 출력
  bank.py check-manifest BANK MANIFEST                               # manifest 문항 출처가 쓸 수 있는 은행 문항인지
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
NUMBER_RE = re.compile(r"\d+")
EXAMS = {"중간", "기말", "모의", "미상"}
TRANSCRIBED_FROM = {"text", "scan", "photo", "hwp", "txt"}
TYPES = {"ox", "blank", "trace", "code-read", "code-write", "short", "essay"}
ANSWER_ORIGINS = {"key", "verified", "unverified"}
PROFESSOR_RANK = {"이정원": 0, "미상": 1}  # 그 밖의 교수는 2
TYPE_RANK = {"trace": 0, "code-read": 0, "blank": 1, "short": 1, "code-write": 1, "essay": 2, "ox": 3}
MAX_OX = 2
SOURCE_ATTR_RE = re.compile(r'data-source="([^"]+)"')
REVIEW_NAME_RE = re.compile(r"복습문제_\d{4}(?:-\d{4})?_[A-Za-z0-9_]+\.html")


class BankError(Exception):
    pass


def _is(value, typ) -> bool:
    if typ is int:
        return isinstance(value, int) and not isinstance(value, bool)
    return isinstance(value, typ)


def _need(obj: dict, key: str, typ: type, where: str, errors: list[str], nullable: bool = False) -> bool:
    if key not in obj:
        errors.append(f"{where}.{key}: 없음")
        return False
    if nullable and obj[key] is None:
        return True
    if not _is(obj[key], typ):
        errors.append(f"{where}.{key}: {typ.__name__}{' 또는 null' if nullable else ''}이어야 함")
        return False
    return True


def _check_source(s: dict, where: str, ids: set[str], errors: list[str]) -> None:
    fields = (("id", str, False), ("file", str, False), ("year", int, True), ("exam", str, False),
              ("professor", str, False), ("has_key", bool, False), ("transcribed_from", str, False),
              ("reviewed", bool, False))
    if not all([_need(s, key, typ, where, errors, nullable) for key, typ, nullable in fields]):
        return
    if not ID_RE.fullmatch(s["id"]):
        errors.append(f"{where}.id: 소문자·숫자·하이픈만: {s['id']!r}")
    elif s["id"] in ids:
        errors.append(f"{where}.id: 중복: {s['id']}")
    ids.add(s["id"])
    if s["exam"] not in EXAMS:
        errors.append(f"{where}.exam: {sorted(EXAMS)} 중 하나여야 함: {s['exam']!r}")
    if s["transcribed_from"] not in TRANSCRIBED_FROM:
        errors.append(f"{where}.transcribed_from: {sorted(TRANSCRIBED_FROM)} 중 하나여야 함: {s['transcribed_from']!r}")
    if not s["professor"].strip():
        errors.append(f"{where}.professor: 비어 있음")


def _check_problem(q: dict, where: str, source_ids: set[str], ids: set[str], errors: list[str]) -> None:
    fields = (("id", str, False), ("source", str, False), ("number", str, False), ("chapters", list, False),
              ("type", str, False), ("points", int, True), ("text", str, False), ("figure", str, True),
              ("answer", str, False), ("answer_origin", str, False), ("duplicate_of", str, True))
    if not all([_need(q, key, typ, where, errors, nullable) for key, typ, nullable in fields]):
        return
    if q["source"] not in source_ids:
        errors.append(f"{where}.source: 없는 원본: {q['source']}")
    if not NUMBER_RE.fullmatch(q["number"]):
        errors.append(f"{where}.number: 숫자 문자열이어야 함: {q['number']!r}")
    elif q["id"] != f"{q['source']}-q{q['number']}":
        errors.append(f"{where}.id: '<source>-q<number>' 꼴이어야 함: {q['id']!r}")
    if q["id"] in ids:
        errors.append(f"{where}.id: 중복: {q['id']}")
    ids.add(q["id"])
    ch = q["chapters"]
    if not (ch and all(_is(c, int) and 1 <= c <= 12 for c in ch) and len(set(ch)) == len(ch)):
        errors.append(f"{where}.chapters: 1~12 정수, 중복 없이 하나 이상이어야 함: {ch!r}")
    if q["type"] not in TYPES:
        errors.append(f"{where}.type: {sorted(TYPES)} 중 하나여야 함: {q['type']!r}")
    if q["answer_origin"] not in ANSWER_ORIGINS:
        errors.append(f"{where}.answer_origin: {sorted(ANSWER_ORIGINS)} 중 하나여야 함: {q['answer_origin']!r}")
    for key in ("text", "answer"):
        if not q[key].strip():
            errors.append(f"{where}.{key}: 비어 있음")


def _check_duplicates(problems: list, errors: list[str]) -> None:
    by_id = {q["id"]: q for q in problems if isinstance(q, dict) and isinstance(q.get("id"), str)}
    for i, q in enumerate(problems):
        dup = q.get("duplicate_of") if isinstance(q, dict) else None
        if not isinstance(dup, str):
            continue
        where = f"problems[{i}].duplicate_of"
        target = by_id.get(dup)
        if target is None:
            errors.append(f"{where}: 없는 문항: {dup}")
        elif dup == q.get("id"):
            errors.append(f"{where}: 자기 자신을 가리킴")
        elif target.get("duplicate_of") is not None:
            errors.append(f"{where}: 원 문항 {dup}도 중복 문항임")


def validate(bank: dict) -> list[str]:
    if not isinstance(bank, dict):
        return ["최상위: 객체여야 함"]
    errors: list[str] = []
    if bank.get("version") != 1:
        errors.append("version: 1이어야 함")
    sources, problems = bank.get("sources"), bank.get("problems")
    if not isinstance(sources, list) or not isinstance(problems, list):
        return errors + ["sources, problems: 목록이어야 함"]
    source_ids: set[str] = set()
    problem_ids: set[str] = set()
    for i, s in enumerate(sources):
        if isinstance(s, dict):
            _check_source(s, f"sources[{i}]", source_ids, errors)
        else:
            errors.append(f"sources[{i}]: 객체여야 함")
    for i, q in enumerate(problems):
        if isinstance(q, dict):
            _check_problem(q, f"problems[{i}]", source_ids, problem_ids, errors)
        else:
            errors.append(f"problems[{i}]: 객체여야 함")
    _check_duplicates(problems, errors)
    return errors


def load(path: Path | str) -> dict:
    try:
        bank = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise BankError(f"{path}: JSON 형식 오류: {e}") from e
    except (OSError, UnicodeDecodeError) as e:
        raise BankError(f"{path}: 파일을 읽을 수 없음: {e}") from e
    errors = validate(bank)
    if errors:
        raise BankError("\n".join(errors))
    return bank


def parse_chapters(spec: str) -> set[int]:
    """'1-3,5' → {1, 2, 3, 5}. 챕터는 강의록 Software_<N> 번호(1~12)."""
    out: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not m:
            raise BankError(f"챕터 표기 오류: {part!r}")
        a, b = int(m.group(1)), int(m.group(2) or m.group(1))
        if not 1 <= a <= b <= 12:
            raise BankError(f"챕터는 1~12, 앞이 작아야 함: {part!r}")
        out.update(range(a, b + 1))
    return out


def used_sources(notes_dir: Path | str) -> set[str]:
    """이전 복습팩 복습문제 페이지(NFC·NFD 이름 모두)의 data-source 값."""
    used: set[str] = set()
    for dirpath, _, files in os.walk(notes_dir):
        for name in files:
            if REVIEW_NAME_RE.fullmatch(unicodedata.normalize("NFC", name)):
                used.update(SOURCE_ATTR_RE.findall(Path(dirpath, name).read_text(encoding="utf-8")))
    return used


def select(bank: dict, range_ch: set[int], taught: set[int], used=frozenset()) -> list[dict]:
    """쓸 수 있는 문항을 우선순위 순으로. OX는 MAX_OX개까지."""
    sources = {s["id"]: s for s in bank["sources"]}

    def eligible(q: dict) -> bool:
        ch = set(q["chapters"])
        return (sources[q["source"]]["reviewed"] and q["duplicate_of"] is None
                and ch <= taught and bool(ch & range_ch) and q["id"] not in used)

    def rank(q: dict) -> tuple:
        s = sources[q["source"]]
        return (PROFESSOR_RANK.get(s["professor"], 2), TYPE_RANK[q["type"]], -(s["year"] or 0), q["id"])

    out, ox = [], 0
    for q in sorted(filter(eligible, bank["problems"]), key=rank):
        if q["type"] == "ox":
            if ox >= MAX_OX:
                continue
            ox += 1
        out.append(q)
    return out


def check_manifest(bank: dict, manifest: dict) -> list[str]:
    """manifest problems의 source가 쓸 수 있는 은행 문항인지. 변형(variant)은 같은 문항을 다시 써도 된다."""
    items = manifest.get("problems") if isinstance(manifest, dict) else None
    if not isinstance(items, list):
        return ["manifest.problems: 목록이어야 함"]
    problems = {q["id"]: q for q in bank["problems"]}
    sources = {s["id"]: s for s in bank["sources"]}
    errors: list[str] = []
    originals: set[str] = set()
    for i, p in enumerate(items):
        where = f"problems[{i}].source"
        src = p.get("source") if isinstance(p, dict) else None
        q = problems.get(src)
        if q is None:
            errors.append(f"{where}: 은행에 없는 문항: {src!r}")
            continue
        if q["duplicate_of"] is not None:
            errors.append(f"{where}: 중복 문항이므로 원 문항 {q['duplicate_of']}을 써야 함")
        if not sources[q["source"]]["reviewed"]:
            errors.append(f"{where}: 검수 전 원본의 문항: {src}")
        if not p.get("variant"):
            if src in originals:
                errors.append(f"{where}: 같은 문항이 두 번: {src}")
            originals.add(src)
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="자구알 기출 문제은행 검사·선별")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("validate").add_argument("bank")
    sp = sub.add_parser("select")
    sp.add_argument("bank")
    sp.add_argument("--range-ch", required=True, help="이번 범위 챕터, 예: 2,3")
    sp.add_argument("--taught", required=True, help="지금까지 배운 챕터, 예: 1-3")
    sp.add_argument("--used-dir", help="이전 팩 폴더(복습노트). 주면 이미 쓴 문항을 뺀다")
    cp = sub.add_parser("check-manifest")
    cp.add_argument("bank")
    cp.add_argument("manifest")
    a = ap.parse_args(argv)
    try:
        bank = load(a.bank)
        if a.cmd == "validate":
            print(f"OK: 원본 {len(bank['sources'])}개, 문항 {len(bank['problems'])}개")
            return 0
        if a.cmd == "select":
            used = used_sources(a.used_dir) if a.used_dir else set()
            rows = select(bank, parse_chapters(a.range_ch), parse_chapters(a.taught), used)
            sources = {s["id"]: s for s in bank["sources"]}
            print("id\t출제자\t유형\t챕터\t정답출처")
            for q in rows:
                print("\t".join([q["id"], sources[q["source"]]["professor"], q["type"],
                                 ",".join(map(str, q["chapters"])), q["answer_origin"]]))
            print(f"후보 {len(rows)}개", file=sys.stderr)
            return 0
        manifest = json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        errors = check_manifest(bank, manifest)
    except (BankError, OSError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        return 1
    if errors:
        print("\n".join(errors))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
