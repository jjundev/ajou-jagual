"""Measure rendered note and review scopes using the shared DOM expression."""
from __future__ import annotations

from collections.abc import Sequence
import json
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from playwright.sync_api import Browser

MEASURE = Path(__file__).with_name("measure_layout.js")
CARD_AREAS = ("problem", "original", "hint", "solution")


class ScopeRow(TypedDict):
    id: str
    area: str
    state: str
    overflow_px: float
    svg_text_count: int
    min_svg_text_height_px: float | None
    widget_min_svg_text_height_px: dict[str, float | None]


class CaseLayout(TypedDict):
    rows: list[ScopeRow]
    errors: list[str]


def expected_scopes(manifest: dict, kind: str) -> tuple[tuple[str, str], ...]:
    scopes = [("hero", "body")]
    if kind == "note":
        for section in manifest["sections"]:
            for topic in section["topics"]:
                scopes.append((topic["id"], "body"))
                if topic["layers"]:
                    scopes.append((topic["id"], "summary"))
    elif kind == "review":
        scopes.extend((card["id"], area) for card in manifest["problems"] for area in CARD_AREAS)
    else:
        raise ValueError(f"unknown browser artifact: {kind}")
    return tuple(scopes)


def has_layout_defect(row: ScopeRow) -> bool:
    height = row["min_svg_text_height_px"]
    return row["overflow_px"] > 1 or (height is not None and height < 9)


def needs_visual_check(row: ScopeRow) -> bool:
    height = row["min_svg_text_height_px"]
    return row["state"] == "visual-only" or (height is not None and 9 <= height < 12)


def measure_case(
    browser: Browser, page_path: Path, case: str, scopes: Sequence[tuple[str, str]]
) -> CaseLayout:
    from playwright.sync_api import Error

    _, viewport, theme = case.split("/")
    width, height = map(int, viewport.split("x"))
    expression = MEASURE.read_text(encoding="utf-8")
    result: CaseLayout = {"rows": [], "errors": []}
    errors = result["errors"]
    with browser.new_context(
        viewport={"width": width, "height": height},
        color_scheme=theme,
        reduced_motion="reduce",
        offline=True,
    ) as context:
        page = context.new_page()
        page.set_default_timeout(3000)
        page.on("pageerror", lambda error: errors.append(f"page: {error}"))
        page.on("requestfailed", lambda request: errors.append(f"resource: {request.url} {request.failure}"))
        try:
            page.goto(page_path.resolve().as_uri(), wait_until="load")
            if not page.evaluate("""async () =>
                typeof renderMathInElement === 'function' &&
                (await document.fonts.load('400 16px Pretendard', '한글')).length > 0
            """):
                raise ValueError("bundled KaTeX or Pretendard unavailable")
        except (Error, ValueError) as exc:
            errors.append(str(exc))
            return result

        current = None
        static_hero = list(scopes) == [("hero", "body")] and not page.locator("main article").count()
        hero = "main .hero" if static_hero else "main .hero.is-current"
        toggle = page.locator("#toggle-right")
        for sid, area in scopes:
            in_panel = area not in ("body", "problem")
            try:
                if sid != current:
                    page.evaluate("(id) => { location.hash = id === 'hero' ? '' : id; }", sid)
                    selector = hero if sid == "hero" else (
                        f"main [id={json.dumps(sid, ensure_ascii=False)}].is-current"
                    )
                    screen = page.locator(selector)
                    screen.wait_for(state="visible")
                    current = sid

                if in_panel and toggle.get_attribute("aria-expanded") != "true":
                    toggle.click()
                elif not in_panel and width < 1024 and not static_hero and toggle.get_attribute("aria-expanded") == "true":
                    page.locator("#panel-right .panel-close").click()

                if area == "summary":
                    root = page.locator("#panel-right .sum:not([hidden])")
                elif in_panel:
                    root = page.locator(f"#panel-right .aid:not([hidden]) details.{area}")
                    summary = root.locator(":scope > summary")
                    if root.get_attribute("open") is None:
                        summary.click()
                else:
                    root = screen.locator(":scope > .problem") if area == "problem" else screen
                root.wait_for(state="visible")
                scroller = "#panel-right .panel-inner" if in_panel else ".content"
                checked = root.evaluate(
                    f"""async (root, selector) => {{
                        const images = Array.from(root.querySelectorAll('img')).filter(img => img.getClientRects().length);
                        const broken = (await Promise.all(images.map(async img => {{
                            img.loading = 'eager';
                            try {{
                                await img.decode();
                                return null;
                            }} catch {{
                                return img.currentSrc || img.getAttribute('src') || '(img)';
                            }}
                        }}))).filter(Boolean);
                        await document.fonts.ready;
                        const scroller = document.querySelector(selector);
                        if (!root.clientWidth || !scroller.clientWidth) throw Error("zero-width scope");
                        return {{broken, measurement: ({expression})(root, scroller)}};
                    }}""",
                    scroller,
                )
                errors.extend(f"{sid}/{area}: image decode failed: {url}" for url in checked["broken"])
                result["rows"].append({"id": sid, "area": area, **checked["measurement"]})
            except Error as exc:
                errors.append(f"{sid}/{area}: {str(exc).splitlines()[0]}")
    return result
