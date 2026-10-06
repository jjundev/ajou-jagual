#!/usr/bin/env python3
"""
Context inference and Data Structures & Algorithms glossary extractor for ds-stt.

- Infers class date (MMDD) from audio filename or explicit argument.
- Infers syllabus chapter from 복습노트/<MMDD>/ or recent 복습노트/.
- Extracts key technical terms directly from 자료구조_강의록_2026/Software_<N>_*.pdf.
- Builds domain guidance prompt for STT transcription subagents.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

DATE_PATTERNS = [
    # 20261005, 2026-10-05, 2026.10.05, 2026_1005
    re.compile(r"(?:20\d{2})[-_.]?([01]\d)[-_.]?([0-3]\d)"),
    # 1005 자구알, 1005.m4a, 녹음_1001.wav, 0928
    re.compile(r"(?:^|[^\d])([01]\d)([0-3]\d)(?:[^\d]|$)"),
]

CHAPTER_SLUG_MAP = {
    "Intro_DS_Algorithms": 1,
    "자료구조및알고리즘": 1,
    "Recursion": 2,
    "재귀": 2,
    "ArrayStructureList": 3,
    "배열": 3,
    "구조체": 3,
    "List": 4,
    "리스트": 4,
    "연결리스트": 4,
    "Stack": 5,
    "스택": 5,
    "Queue": 6,
    "큐": 6,
    "Tree": 7,
    "트리": 7,
    "Heap": 8,
    "힙": 8,
    "Sorting": 9,
    "정렬": 9,
    "Graph": 10,
    "그래프": 10,
    "Hash": 11,
    "해시": 11,
    "Search": 12,
    "탐색": 12,
}

COMMON_DS_ERROR_RULES = [
    ("말록/말락", "malloc (동적 메모리 할당)"),
    ("프리", "free (동적 메모리 해제)"),
    ("스트럭트/스트럭쳐", "struct (구조체)"),
    ("타입데프", "typedef (타입 정의)"),
    ("사이즈오브", "sizeof (크기 연산자)"),
    ("널/널값/널포인터", "NULL (널 포인터)"),
    ("인서트 노드/인서트", "insert_node / insert"),
    ("리무브 노드/리무브/딜리트", "remove_node / remove / delete"),
    ("헤드 포인터/헤드", "head pointer (헤드 포인터)"),
    ("테일/테일 포인터", "tail pointer"),
    ("비포/비포 노드", "before (이전 노드 포인터 변수)"),
    ("애프터/애프터 노드", "after (다음 노드 포인터 변수)"),
    ("뉴/뉴노드", "new_node / new (새 노드 포인터 변수)"),
    ("넥스트", "next (다음 노드 링크)"),
    ("링크/링크 필드", "link (링크 필드)"),
    ("가베이지/가비지", "가비지 (garbage)"),
    ("슈도/수도 코드", "의사코드 (pseudo-code)"),
    ("디레퍼런스", "역참조 (dereference)"),
    ("어레이", "array (배열)"),
    ("싱글 링크드 리스트", "단순 연결 리스트 (singly linked list)"),
    ("더블 링크드 리스트", "이중 연결 리스트 (doubly linked list)"),
    ("원형 링크드 리스트", "원형 연결 리스트 (circular linked list)"),
    ("푸쉬/푸시", "push (스택 삽입)"),
    ("팝", "pop (스택 삭제)"),
    ("픽/피크", "peek (스택 조회)"),
    ("인큐", "enqueue (큐 삽입)"),
    ("디큐", "dequeue (큐 삭제)"),
    ("원형 큐", "circular queue"),
    ("덱/디큐", "deque (양방향 큐)"),
    ("재귀/순환", "recursion / 순환 호출"),
    ("피벗", "pivot (퀵정렬 기준 원소)"),
    ("히피파이", "heapify (힙 생성/재구성)"),
    ("빅오", "Big-O (O(n))"),
]


def nfc(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def parse_date(filename_or_path: str, date_override: str | None = None) -> str:
    """Extract MMDD string from filename or override."""
    if date_override:
        clean = date_override.strip()
        m = re.fullmatch(r"(\d{2})(\d{2})", clean)
        if m and (1 <= int(m.group(1)) <= 12) and (1 <= int(m.group(2)) <= 31):
            return m.group(0)
        raise ValueError(f"유효하지 않은 날짜 형식입니다: {date_override!r} (예: 1005)")

    base = nfc(Path(filename_or_path).name)

    for pat in DATE_PATTERNS:
        match = pat.search(base)
        if match:
            mm, dd = match.group(1), match.group(2)
            if (1 <= int(mm) <= 12) and (1 <= int(dd) <= 31):
                return f"{mm}{dd}"

    raise ValueError(
        f"파일명에서 수업 날짜(MMDD)를 찾을 수 없습니다: {base!r}\n"
        f"--date MMDD 옵션으로 날짜를 직접 지정해 주세요. (예: /ds-stt audio.m4a --date 1005)"
    )


def _detect_chapter_from_text_or_slug(name_or_text: str) -> int | None:
    norm = nfc(name_or_text)
    m = re.search(r"Software_(\d+)_", norm)
    if m:
        return int(m.group(1))
    m_slide = re.search(r'class="tag slide">S(\d+)', norm)
    if m_slide:
        return int(m_slide.group(1))

    for slug, ch in CHAPTER_SLUG_MAP.items():
        if slug in norm:
            return ch
    return None


def infer_chapter(repo_root: Path | str, mmdd: str) -> int:
    """Infer lecture chapter number from 복습노트/<MMDD>/ or latest 복습노트/."""
    repo = Path(repo_root)

    # 1순위: 복습노트/<MMDD>/ 안의 파일 검사
    review_target_dir = repo / "복습노트" / mmdd
    if review_target_dir.is_dir():
        for f in review_target_dir.iterdir():
            name = nfc(f.name)
            ch = _detect_chapter_from_text_or_slug(name)
            if ch is not None:
                return ch
            if name.endswith((".md", ".html")):
                try:
                    content = f.read_text(encoding="utf-8")
                    ch_content = _detect_chapter_from_text_or_slug(content)
                    if ch_content is not None:
                        return ch_content
                except Exception:
                    pass

    # 2순위: 복습노트/ 에서 가장 최근 완료된 폴더 조사
    review_root = repo / "복습노트"
    if review_root.is_dir():
        folders = sorted([d.name for d in review_root.iterdir() if d.is_dir() and re.fullmatch(r"\d{4}", d.name)])
        past_folders = [d for d in folders if d <= mmdd]
        target_folder = past_folders[-1] if past_folders else (folders[-1] if folders else None)

        if target_folder:
            f_dir = review_root / target_folder
            for f in f_dir.iterdir():
                name = nfc(f.name)
                ch = _detect_chapter_from_text_or_slug(name)
                if ch is not None:
                    return ch

    # 기본 fallback: 4장 (학기 중반 List 기본값)
    return 4


def get_chapter_title(repo_root: Path | str, chapter: int) -> str:
    """Find chapter title from 자료구조_강의록_2026/ directory."""
    repo = Path(repo_root)
    lec_dir = repo / "자료구조_강의록_2026"
    if lec_dir.is_dir():
        for f in lec_dir.iterdir():
            name = nfc(f.name)
            m = re.match(rf"^Software_{chapter}_(.+?)\.pdf$", name)
            if m:
                return f"Software_{chapter}_{m.group(1).strip()}"
    return f"Software_{chapter}"


def extract_chapter_terms(repo_root: Path | str, chapter: int, max_terms: int = 70) -> list[str]:
    """Extract key technical terms from lecture PDF."""
    repo = Path(repo_root)
    terms: set[str] = set()

    # Curated core Korean DS terms by chapter and general DS
    ds_curated_vocab = [
        # General & C basics (Ch 1~3)
        "자료구조", "알고리즘", "시간 복잡도", "공간 복잡도", "빅오 표기법", "순환 호출", "재귀 호출",
        "기저 조건", "탈출 조건", "팩토리얼", "피보나치 수열", "하노이 탑", "배열", "구조체", "포인터",
        "포인터 연산", "동적 메모리 할당", "동적 메모리 해제", "역참조", "화살표 연산자", "도트 연산자",
        "자가 참조 구조체", "다항식 표현", "희소 행렬", "2차원 배열",
        # List (Ch 4)
        "단순 연결 리스트", "이중 연결 리스트", "원형 연결 리스트", "연결 리스트", "선형 리스트",
        "헤드 포인터", "헤드 노드", "테일 포인터", "노드", "데이터 필드", "링크 필드",
        "삽입 연산", "삭제 연산", "탐색 연산", "방문 연산", "공백 상태", "포화 상태", "가비지",
        # Stack & Queue (Ch 5~6)
        "스택", "스택 상단", "스택 하단", "스택 오버플로우", "스택 언더플로우", "푸시 연산", "팝 연산",
        "피크 연산", "후위 표기법", "전위 표기법", "중위 표기법", "괄호 검사", "미로 탐색",
        "큐", "원형 큐", "선형 큐", "프론트", "리어", "인큐 연산", "디큐 연산", "덱",
        # Tree & Heap (Ch 7~8)
        "트리", "루트 노드", "서브트리", "단말 노드", "리프 노드", "부모 노드", "자식 노드", "형제 노드",
        "이진 트리", "포화 이진 트리", "완전 이진 트리", "경사 이진 트리", "스레드 이진 트리",
        "전위 순회", "중위 순회", "후위 순회", "레벨 순회", "이진 탐색 트리",
        "힙", "최대 힙", "최소 힙", "히피파이", "우선순위 큐",
        # Sorting (Ch 9)
        "선택 정렬", "삽입 정렬", "버블 정렬", "셸 정렬", "합병 정렬", "퀵 정렬", "기수 정렬",
        "힙 정렬", "피벗", "분할 정복", "안정 정렬",
        # Graph (Ch 10)
        "그래프", "정점", "간선", "무방향 그래프", "방향 그래프", "가중치 그래프", "인접 행렬", "인접 리스트",
        "깊이 우선 탐색", "너비 우선 탐색", "신장 트리", "최소 비용 신장 트리", "크루스칼", "프림",
        "최단 경로", "다익스트라", "플로이드", "위상 정렬",
        # Hash & Search (Ch 11~12)
        "해싱", "해시 테이블", "해시 함수", "버킷", "슬롯", "충돌", "오버플로우",
        "선형 조사법", "이차 조사법", "이중 해싱", "체이닝", "이진 탐색", "보간 탐색", "색인 순차 탐색",
        "균형 이진 탐색 트리", "AVL 트리"
    ]

    lec_dir = repo / "자료구조_강의록_2026"
    pdf_path = None
    if lec_dir.is_dir():
        for f in lec_dir.iterdir():
            if re.match(rf"^Software_{chapter}_.+\.pdf$", nfc(f.name)):
                pdf_path = f
                break

    if pdf_path and fitz:
        try:
            doc = fitz.open(pdf_path)
            full_text = "\n".join(page.get_text() for page in doc)

            # (1) C 코드 식별자 및 키워드 (2글자 이상 알파벳/언더스코어로 시작하는 식별자)
            for m in re.finditer(r"\b[A-Za-z_][A-Za-z0-9_]{1,24}\b", full_text):
                word = m.group(0)
                if word.lower() not in {"and", "the", "for", "with", "from", "that", "this", "page", "software", "chap"}:
                    terms.add(word)

            # (2) 슬라이드에 등장하는 엄선된 자료구조 용어 매칭
            for vocab in ds_curated_vocab:
                if vocab in full_text or vocab.replace(" ", "") in full_text:
                    terms.add(vocab)

            # (3) 괄호 안 영문 병기 단어: 예) 단순 연결 리스트(singly linked list)
            for m in re.finditer(r"([가-힣]{2,10})\s*\(([A-Za-z\s]+)\)", full_text):
                terms.add(m.group(1).strip())
                en = m.group(2).strip()
                if len(en) < 25:
                    terms.add(en)
        except Exception:
            pass

    # 핵심 필수 공통 C/자료구조 시드 용어 보강
    common_seed = [
        "malloc", "free", "sizeof", "struct", "typedef", "NULL", "pointer", "포인터",
        "node", "노드", "link", "링크", "head", "tail", "헤드 포인터", "new_node",
        "before", "after", "insert_node", "remove_node", "단순 연결 리스트", "이중 연결 리스트",
        "원형 연결 리스트", "스택", "stack", "push", "pop", "peek", "큐", "queue",
        "enqueue", "dequeue", "circular queue", "deque", "덱", "트리", "tree", "root",
        "leaf node", "binary tree", "이진 트리", "이진 탐색 트리", "BST", "힙", "heap",
        "heapify", "quick sort", "merge sort", "시간 복잡도", "Big-O", "재귀", "recursion"
    ]
    for w in common_seed:
        terms.add(w)

    sorted_terms = sorted(terms, key=lambda x: (-len(x), x))
    return sorted_terms[:max_terms]


def build_stt_prompt(chapter: int, chapter_title: str, terms: list[str]) -> str:
    """Format domain guidance block to inject into the subagent STT prompt."""
    sample_terms = ", ".join(terms[:50])
    homophone_guide = "\n".join(f"  - '{err}'로 들리면 -> '{cor}'" for err, cor in COMMON_DS_ERROR_RULES)

    return f"""[자료구조및알고리즘이해 강의 도메인 가이드 (이정원 교수님, ECE256)]
- 본 오디오는 아주대학교 전자공학부 자료구조및알고리즘이해 강의 녹음입니다.
- 단원 범위: {chapter}장 ({chapter_title})
- 주요 C언어 및 자료구조 고유명사:
  {sample_terms}

- 필수 전사 및 발음 교정 규칙:
  1. C언어/자료구조 표준 용어 최우선: 교수님의 발음이 뭉개지거나 일상 단어로 들릴 경우, C 언어 및 자료구조 표준 용어로 정확히 전사하세요.
{homophone_guide}
  2. 표기 원칙: 자연스러운 한국어 구어체 음차를 기본으로 하되, C 핵심 식별자 및 키워드(malloc, free, sizeof, struct, typedef, NULL, head, link, node, p->link 등)는 정확한 영문 표기를 유지하세요.
  3. 철저한 축어성(Verbatim): 요약이나 어미 생략 없이 실제 발화된 내용을 있는 그대로 기록하세요.
"""


def main():
    parser = argparse.ArgumentParser(description="Infer data structures context and terms for ds-stt")
    parser.add_argument("audio", help="Path to audio file (or filename)")
    parser.add_argument("--repo", default=".", help="Repository root path")
    parser.add_argument("--date", help="Class date override (MMDD)")
    parser.add_argument("--chapter", type=int, help="Chapter override (e.g. 4)")
    parser.add_argument("--json", action="store_true", help="Output JSON structure")
    parser.add_argument("--prompt-only", action="store_true", help="Print prompt injection text only")

    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    date = parse_date(args.audio, args.date)
    chapter = args.chapter if args.chapter else infer_chapter(repo, date)
    chapter_title = get_chapter_title(repo, chapter)
    terms = extract_chapter_terms(repo, chapter)
    prompt_guide = build_stt_prompt(chapter, chapter_title, terms)

    if args.prompt_only:
        print(prompt_guide)
        return

    result = {
        "audio": args.audio,
        "date": date,
        "chapter": chapter,
        "chapter_title": chapter_title,
        "output_filename": f"{date} 자구알.md",
        "output_path": str(repo / "STT" / f"{date} 자구알.md"),
        "terms_count": len(terms),
        "terms": terms,
        "prompt_guide": prompt_guide,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"수업 날짜: {date} (파일명에서 추출)")
        print(f"진도 단원: {chapter}장 ({chapter_title})")
        print(f"추출 용어: {len(terms)}개")
        print(f"최종 저장: STT/{date} 자구알.md")


if __name__ == "__main__":
    main()
