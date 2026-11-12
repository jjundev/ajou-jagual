import shutil

import pytest

import concept_util
from concept_util import copy_fixture, nfd_path
import build
import interaction


def test_build_writes_root_html(tmp_path):
    root = copy_fixture(tmp_path)
    out = build.build(root / ".pack/자료_확인문제_9999_Mini")
    assert out == root / "확인문제_9999_Mini.html"
    page = out.read_text(encoding="utf-8")
    assert "확인문제 9999" in page and page.count('class="card"') == 3
    assert interaction.build_model(page, "x")["errors"] == []


def test_build_finds_nfd_pack_dir(tmp_path):
    root = copy_fixture(tmp_path, nfd=True)
    assert build.build(nfd_path(root, ".pack/자료_확인문제_9999_Mini")).exists()


def test_build_missing_pack_message(tmp_path):
    root = copy_fixture(tmp_path)
    shutil.rmtree(root / ".pack/자료_복습팩")
    with pytest.raises(build.BuildError, match="팩이 없어 근거가 없습니다"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_build_unknown_objective(tmp_path):
    root = copy_fixture(tmp_path)
    p = root / ".pack/자료_확인문제_9999_Mini/items.json"
    p.write_text(p.read_text(encoding="utf-8").replace('"o2"', '"o9"', 1), encoding="utf-8")
    with pytest.raises(build.BuildError, match="o9"):
        build.build(root / ".pack/자료_확인문제_9999_Mini")


def test_cli_missing_pack_exits_1(tmp_path, capsys):
    root = copy_fixture(tmp_path)
    shutil.rmtree(root / ".pack/자료_복습팩")
    assert build.main(["build.py", str(root / ".pack/자료_확인문제_9999_Mini")]) == 1
    assert "팩이 없어 근거가 없습니다" in capsys.readouterr().err
