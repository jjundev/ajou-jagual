"""Rendered 1119 failure patterns, using the actual note and card templates."""
import json
import shutil

import pytest
from playwright.sync_api import sync_playwright

from _util import MINI_RUN
import assemble
from browser_layout import expected_scopes, has_layout_defect, measure_case, needs_visual_check


@pytest.fixture(scope="module")
def chrome():
    with sync_playwright() as playwright:
        with playwright.chromium.launch(channel="chrome") as browser:
            yield browser


def assembled(tmp_path, *, note_extra="", solutions=()):
    run = tmp_path / "run"
    shutil.copytree(MINI_RUN, run)
    path = run / "manifest.json"
    manifest = json.loads(path.read_text())
    section = run / "sections/s1.html"
    text = section.read_text().replace('</h3>', '</h3>' + note_extra, 1)
    section.write_text(text)
    card = run / "cards/p1.html"
    template = card.read_text()
    for number, content in solutions:
        pid = f"p{number}"
        if number != 1:
            manifest["problems"].append({**manifest["problems"][0], "id": pid})
        body = template.replace('id="p1"', f'id="{pid}"')
        if content is None:
            body = body.split('        <details class="solution">')[0] + "</article>"
        else:
            body = body.replace("</ol>", "</ol>" + content)
        (card.parent / f"{pid}.html").write_text(body)
    path.write_text(json.dumps(manifest))
    note, review = assemble.assemble(run, tmp_path)
    return manifest, note, review


def measured(browser, manifest, path, case):
    result = measure_case(browser, path, case, expected_scopes(manifest, case.split("/")[0]))
    assert result["errors"] == []
    return {(row["id"], row["area"]): row for row in result["rows"]}


def tree_grid(columns, view_width):
    labels = []
    for i in range(4):
        x = 10 + i % columns * view_width / columns
        y = 28 + i // columns * 55
        labels.append(f'<text x="{x}" y="{y}" font-size="17">A—B—C</text>')
    return f'<svg width="100%" viewBox="0 0 {view_width} 120">{"".join(labels)}</svg>'


@pytest.mark.parametrize("viewport", ["375x812", "1280x900"])
def test_measures_active_solution_in_both_widths(tmp_path, chrome, viewport):
    results = []
    for name, grid in (("wide", tree_grid(4, 1000)), ("stacked", tree_grid(2, 270))):
        case_dir = tmp_path / name
        case_dir.mkdir()
        m, _, page = assembled(case_dir, solutions=[(1, tree_grid(4, 1600)), (9, grid)])
        rows = measured(chrome, m, page, f"review/{viewport}/light")
        assert rows["p1", "solution"]["min_svg_text_height_px"] < rows["p9", "solution"]["min_svg_text_height_px"]
        results.append(rows["p9", "solution"])
    bad, fixed = results
    assert bad["id"] == "p9" and bad["area"] == "solution"
    assert 0 < bad["min_svg_text_height_px"] < 9
    assert fixed["min_svg_text_height_px"] >= 12
    assert not has_layout_defect(fixed)


def test_local_scroll_is_allowed_but_panel_overflow_fails(tmp_path, chrome):
    content = '<div class="figure-scroll" style="overflow:auto"><div style="width:800px">Tree</div></div>'
    m, _, review = assembled(tmp_path, solutions=[(1, content), (9, content + '<p style="width:800px">Outside</p>')])
    rows = measured(chrome, m, review, "review/375x812/light")
    assert rows["p1", "solution"]["overflow_px"] <= 1
    assert rows["p9", "solution"]["overflow_px"] > 1


def test_inline_math_overflow_and_split_formula(tmp_path, chrome):
    edges = [f"(v_{{{i}}},v_{{{i+1}}})" for i in range(7)]
    overflows = []
    for name, equation in (("single", "$" + r",\;".join(edges) + "$"),
                           ("split", " ".join(f"${edge}$" for edge in edges))):
        case_dir = tmp_path / name
        case_dir.mkdir()
        m, note, _ = assembled(case_dir, note_extra=f"<p>{equation}</p>")
        rows = measured(chrome, m, note, "note/375x812/light")
        overflows.append(rows["s1-mean", "body"]["overflow_px"])
    assert overflows[0] > 1 and overflows[1] <= 1


def test_height_thresholds_and_external_image(tmp_path, chrome):
    def row(height):
        return {"state": "measured", "overflow_px": 0, "min_svg_text_height_px": height}

    assert [has_layout_defect(row(h)) for h in (8.99, 9.0, 12.0)] == [True, False, False]
    assert [needs_visual_check(row(h)) for h in (9.0, 11.99, 12.0)] == [True, True, False]
    image = '<img src="external.svg" width="30" height="30">'
    textless = '<svg viewBox="0 0 10 10" width="30"><circle cx="5" cy="5" r="4"/></svg>'
    widget = f'<div class="widget" id="tree-demo">{tree_grid(2, 270)}</div>'
    (tmp_path / "external.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    m, note, review = assembled(tmp_path, note_extra=widget, solutions=[(1, image), (9, textless)])
    assert measured(chrome, m, note, "note/375x812/light")["s1-mean", "body"]["widget_min_svg_text_height_px"]["tree-demo"] >= 12
    rows = measured(chrome, m, review, "review/375x812/light")
    assert rows["p1", "solution"]["state"] == "visual-only"
    textless_svg = rows["p9", "solution"]
    assert textless_svg["state"] == "measured" and textless_svg["svg_text_count"] == 0
    assert textless_svg["min_svg_text_height_px"] is None


def test_missing_required_panel_is_error(tmp_path, chrome):
    m, _, review = assembled(tmp_path, solutions=[(9, None)])
    report = measure_case(chrome, review, "review/375x812/light", expected_scopes(m, "review"))
    assert any("p9/solution" in error for error in report["errors"])
    assert not any(row["id"] == "p9" and row["area"] == "solution" for row in report["rows"])


def test_desktop_body_measured_with_default_open_panel(tmp_path, chrome):
    fragment = '<div style="width:800px">내용을 읽는 기본 화면에서 넘치는 블록</div>'
    m, note, _ = assembled(tmp_path, note_extra=fragment)
    rows = measured(chrome, m, note, "note/1280x900/light")
    assert rows["s1-mean", "body"]["overflow_px"] > 1


def test_sighted_svg_labels_inside_aria_hidden_diagram_are_measured(tmp_path, chrome):
    diagram = '<svg aria-hidden="true" width="100" viewBox="0 0 200 60"><text y="20" font-size="8">A → B</text></svg>'
    m, _, review = assembled(tmp_path, solutions=[(9, diagram)])
    row = measured(chrome, m, review, "review/375x812/light")["p9", "solution"]
    assert row["state"] == "measured" and row["svg_text_count"] == 1
    assert has_layout_defect(row)


def test_corrupt_local_image_is_a_resource_error(tmp_path, chrome):
    (tmp_path / "invalid.png").write_bytes(b"this is not a PNG")
    m, _, review = assembled(tmp_path, solutions=[(9, '<img src="invalid.png" width="100" height="60">')])
    report = measure_case(chrome, review, "review/375x812/light", expected_scopes(m, "review"))
    assert any("p9/solution" in error and "invalid.png" in error for error in report["errors"])


def test_multiline_svg_checks_each_rendered_line(tmp_path, chrome):
    diagram = (
        '<svg width="200" viewBox="0 0 200 60"><text font-size="5">'
        '<tspan x="5" y="12">vertex A</tspan><tspan x="5" y="32">vertex B</tspan></text></svg>'
    )
    m, _, review = assembled(tmp_path, solutions=[(9, diagram)])
    row = measured(chrome, m, review, "review/375x812/light")["p9", "solution"]
    assert 0 < row["min_svg_text_height_px"] < 9
    assert has_layout_defect(row)
