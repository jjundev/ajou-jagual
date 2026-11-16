import json
import subprocess

import _util
import pytest


def setup(tmp_path):
    repo, run = tmp_path / "repo", tmp_path / "explain"
    pack = repo / "복습노트/1116"
    data = pack / ".pack/자료_복습팩"
    data.mkdir(parents=True)
    review = data / "복습문제_1116_Test.json"
    review.write_text('{"version":1}')
    explain = pack / "문제설명_1116_Test.html"
    explain.write_text("prior")
    return repo, run, review, explain


def stage(run, repo, review):
    target = "review-1116-Test"
    folder = run / target
    folder.mkdir(parents=True)
    (run / "run.json").write_text(json.dumps({"version": 1, "repo": str(repo), "targets": [target]}))
    logical = review.parents[2] / review.with_suffix(".html").name
    (folder / "source.json").write_text(json.dumps({"path": str(logical)}))
    return folder


@pytest.mark.parametrize("fault", ["archive", "new-owner", "wrong-repo", "wrong-source", "more-targets", "symlink"])
def test_guard_does_not_call_publisher_on_drift(tmp_path, fault):
    from followup_explain import prepare, publish

    repo, run, review, explain = setup(tmp_path)
    prepare(repo, review, run)
    folder = stage(run, repo, review)
    if fault == "archive":
        review.write_text("changed")
    if fault == "new-owner":
        explain.write_text("a more recent publication")
    if fault == "wrong-repo":
        (run / "run.json").write_text(json.dumps({"version": 1, "repo": str(tmp_path), "targets": [folder.name]}))
    if fault == "wrong-source":
        (folder / "source.json").write_text(json.dumps({"path": str(review.with_suffix(".html"))}))
    if fault == "more-targets":
        (run / "run.json").write_text(json.dumps({"version": 1, "repo": str(repo), "targets": [folder.name, "other"]}))
    if fault == "symlink":
        folder.rename(run / "other")
        folder.symlink_to(run / "other", target_is_directory=True)
    before = explain.read_bytes()
    with pytest.raises(ValueError):
        publish(repo, review, run)
    assert explain.read_bytes() == before


def test_guard_uses_base_pack_lock_and_exact_run(tmp_path, monkeypatch):
    from followup_explain import prepare, publish
    from pdf_publish import lock_handle
    from release_review import publication_lock

    repo, run, review, explain = setup(tmp_path)
    prepare(repo, review, run)
    stage(run, repo, review)
    calls = []

    def call(argv):
        calls.append(argv)
        with publication_lock(explain.parent).open("a+") as handle:
            with pytest.raises(BlockingIOError):
                lock_handle(handle)
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(subprocess, "run", call)
    assert publish(repo, review, run) == 0
    assert len(calls) == 1 and calls[0][-3:] == ["publish", "--run", str(run)]


def test_prepare_accepts_path_through_system_root_alias(tmp_path):
    from followup_explain import prepare

    repo, run, review, _ = setup(tmp_path)
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path, target_is_directory=True)
    receipt = prepare(alias / "repo", alias / "repo" / review.relative_to(repo), run)
    assert json.loads(receipt.read_text())["review"] == str(review)
