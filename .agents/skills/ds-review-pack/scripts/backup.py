"""이번 range의 기존 팩을 RUN/previous-<시각>-<임의>/에 백업한다.

python3 backup.py --range 0921 --repo REPO --run RUN
대상: 복습노트/<range>/(와 예전 형식인 복습노트/ 바로 아래)의 정리노트_<range>_*, 복습문제_<range>_*, figures_<range>/.
파일명은 NFC로 비교하므로 NFD 이름도 잡힌다. range 형식이 틀리거나 복사된 파일 수가 다르면 종료 코드 1.
"""

import argparse
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata as u


def listdir_nfc(d):  # NFD 폴더명도 찾는다
    return {u.normalize("NFC", n): os.path.join(d, n) for n in os.listdir(d)} if os.path.isdir(d) else {}


def count(p):
    return sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", required=True)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    r, run = a.range, a.run
    notes = os.path.join(a.repo, "복습노트")
    if not re.fullmatch(r"\d{4}(-\d{4})?", r) or not os.path.isdir(run):
        sys.exit(f"백업 중단: RANGE={r!r} 또는 RUN={run!r} 잘못됨")

    def want(n):
        n = u.normalize("NFC", n)
        return n.startswith((f"정리노트_{r}_", f"복습문제_{r}_")) or n == f"figures_{r}"

    srcs = [listdir_nfc(notes).get(r), notes]  # 날짜 폴더, 예전 형식(바로 아래)
    hits = sorted({n: p for d in srcs if d and os.path.isdir(d) for n, p in listdir_nfc(d).items() if want(n)}.items())
    if not hits:
        print("백업할 기존 팩 없음")
        return
    dst = tempfile.mkdtemp(prefix=time.strftime("previous-%Y%m%d-%H%M%S-"), dir=run)  # 항상 새 폴더
    for n, src in hits:
        b = os.path.join(dst, n)
        shutil.copytree(src, b) if os.path.isdir(src) else shutil.copy2(src, b)
    want_n, got_n = sum(count(p) for _, p in hits), count(dst)
    if got_n != want_n:
        sys.exit(f"백업 실패: 파일 {want_n}개 중 {got_n}개만 복사됨 → {dst}")
    print(f"백업 {len(hits)}항목(파일 {got_n}개): {dst}", *(p for _, p in hits), sep="\n")


if __name__ == "__main__":
    main()
