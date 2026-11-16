#!/usr/bin/env python3
"""Guard delegated problem-explanation publication with the base pack lock."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from pack_layout import nfc, normalized_child
from pdf_cards import digest
from pdf_publish import lock_handle
from release_review import publication_lock
from review_source import NAME, review_path, source_file


def checked_path(root, relative):
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"범위를 벗어난 경로: {relative}")
    for part in relative.parts:
        root = normalized_child(root, part)
        if root.is_symlink():
            raise ValueError(f"심볼릭 링크를 사용할 수 없어요: {root}")
    return root


def followup_paths(repo, review, run):
    given_repo = repo.absolute()
    repo = repo.resolve(strict=True)
    root = given_repo if review.is_relative_to(given_repo) else repo
    if not review.is_absolute() or not review.is_relative_to(root):
        raise ValueError("저장소 안의 문제 원고 절대 경로가 필요해요")
    run_path = run.resolve()
    if run.is_symlink() or run_path.is_relative_to(repo) or repo.is_relative_to(run_path):
        raise ValueError("문제설명에는 저장소 밖의 별도 RUN이 필요해요")
    review = checked_path(repo, review.relative_to(root))
    if review.suffix != ".json" or not review.is_file():
        raise ValueError(f"발행된 문제 원고가 없어요: {review}")
    logical = review_path(review)
    match = NAME.fullmatch(nfc(logical.name))
    if match is None:
        raise ValueError(f"복습문제 이름 오류: {logical}")
    range_, slug = match.groups()
    expected_pack = checked_path(repo, Path("복습노트") / range_)
    checked_path(expected_pack, Path(logical.name))
    if logical.parent != expected_pack or source_file(logical) != review:
        raise ValueError("지정한 팩의 유효 JSON 원고와 일치해야 해요")
    receipt = checked_path(run_path.parent, Path(run_path.name + ".publish.json"))
    return repo, review, logical, run_path, receipt, range_, slug


def explanation_snapshot(pack, range_, slug):
    stem = f"문제설명_{range_}_{slug}"
    rels = (Path(stem + ".html"), Path(".pack") / (stem + ".md"),
            Path(".pack") / ("figures_" + stem), Path(".pack") / ("자료_" + stem))
    result = {}
    for rel in rels:
        path = checked_path(pack, rel)
        files = [path]
        if path.is_dir():
            files.extend(checked_path(pack, p.relative_to(pack)) for p in path.rglob("*"))
        for file in files:
            result[file.relative_to(pack).as_posix()] = digest(file) if file.is_file() else None
    return result


def snapshot(repo, review, logical, run, range_, slug):
    return {"version": 1, "repo": str(repo), "run": str(run), "review": str(review),
            "source_sha256": digest(review), "owned_before": explanation_snapshot(logical.parent, range_, slug)}


def prepare(repo: Path, review: Path, run: Path) -> Path:
    repo, review, logical, run, receipt, range_, slug = followup_paths(repo, review, run)
    run.parent.mkdir(parents=True, exist_ok=True)
    if run.exists() and (not run.is_dir() or any(run.iterdir())):
        raise ValueError("비어 있는 문제설명 RUN이 필요해요")
    with publication_lock(logical.parent).open("a+") as lock:
        lock_handle(lock)
        data = snapshot(repo, review, logical, run, range_, slug)
        with receipt.open("x", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")
    return receipt


def publish(repo: Path, review: Path, run: Path) -> int:
    repo, review, logical, run, receipt, range_, slug = followup_paths(repo, review, run)
    with publication_lock(logical.parent).open("a+") as lock:
        lock_handle(lock)
        before = json.loads(receipt.read_text(encoding="utf-8"))
        if snapshot(repo, review, logical, run, range_, slug) != before:
            raise ValueError("문제 원고 또는 기존 설명이 준비 이후 바뀌었어요")
        target = f"review-{range_}-{slug}"
        index = json.loads(checked_path(run, Path("run.json")).read_text(encoding="utf-8"))
        if index != {"version": 1, "repo": str(repo), "targets": [target]}:
            raise ValueError("지정한 저장소와 대상 하나에 맞는 문제설명 RUN이 필요해요")
        src = json.loads(checked_path(run, Path(target) / "source.json").read_text(encoding="utf-8"))
        recorded = Path(src["path"])
        if recorded != logical or source_file(recorded) != review:
            raise ValueError("문제설명 RUN이 지정한 유효 원고와 달라요")
        cli = Path(__file__).resolve().parents[2] / "ds-problem-explain/scripts/mpe_cli.py"
        return subprocess.run([sys.executable, "-B", str(cli), "publish", "--run", str(run)]).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "publish"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "publish":
            return publish(args.repo, args.review, args.run)
        print(prepare(args.repo, args.review, args.run))
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
