"""관련 챕터 강의록 텍스트를 쪽 번호와 함께 RUN/slides.txt에 쓴다.

python3 extract_slides.py --repo REPO --run RUN --ch 3 4
"""

import argparse
import os
import re

import fitz


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--ch", type=int, nargs="+", required=True)
    a = ap.parse_args()
    want = set(a.ch)
    d = os.path.join(a.repo, "자료구조_강의록_2026")
    with open(os.path.join(a.run, "slides.txt"), "w", encoding="utf-8") as f:
        for name in sorted(os.listdir(d)):
            m = re.match(r"Software_(\d+)_", name)
            if not m or int(m.group(1)) not in want:
                continue
            for i, page in enumerate(fitz.open(os.path.join(d, name)), 1):
                f.write(f"=== S{m.group(1)} p{i} ===\n{page.get_text()}\n")
    print("slides.txt:", sorted(want))


if __name__ == "__main__":
    main()
