"""Render the bundled HTML assignment cover as a one-page PDF."""

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Mapping

from playwright.sync_api import sync_playwright
from pypdf import PdfReader


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATE = SKILL_DIR / "assets" / "cover.html"
FIELDS = ("course", "assignment_label", "assignment_topic", "student_id", "student_name")


class CoverError(ValueError):
    """The requested cover cannot be rendered without changing its content."""


def _validated_data(data: Mapping[str, str]) -> dict[str, str]:
    if not isinstance(data, dict):
        raise CoverError("입력은 JSON 객체여야 합니다.")
    result = {}
    for field in FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip() or value.strip() == "미제공":
            raise CoverError(f"{field}에 확인된 문자열 값이 필요합니다.")
        value = value.strip()
        if any(character in value for character in "\r\n\t"):
            raise CoverError(f"{field}에는 한 줄 텍스트만 넣을 수 있습니다.")
        result[field] = value
    return result


def render_cover(data: Mapping[str, str], output_path: Path, *, overwrite: bool = False) -> Path:
    values = _validated_data(data)
    output_path = Path(output_path)
    if output_path.exists() and not overwrite:
        raise CoverError(f"출력 파일이 이미 있습니다: {output_path}")
    if not TEMPLATE.is_file():
        raise CoverError(f"HTML 템플릿을 찾지 못했습니다: {TEMPLATE}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=".cover-", suffix=".pdf", dir=output_path.parent, delete=False) as temporary:
        temporary_path = Path(temporary.name)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={"width": 1123, "height": 794}, device_scale_factor=1)
                page.goto(TEMPLATE.as_uri(), wait_until="load")
                page.evaluate(
                    """values => {
                      for (const [field, value] of Object.entries(values)) {
                        document.querySelector(`[data-field="${field}"]`).textContent = value;
                      }
                    }""",
                    values,
                )
                fonts_ready = page.evaluate(
                    """async () => {
                      await document.fonts.ready;
                      return document.fonts.check('16pt Pretendard') &&
                             document.fonts.check('600 42pt Pretendard');
                    }"""
                )
                if not fonts_ready:
                    raise CoverError("Pretendard 폰트를 로드하지 못했습니다.")
                overflow = page.evaluate(
                    """() => [...document.querySelectorAll('[data-check-overflow]')]
                      .filter(element => element.scrollWidth > element.clientWidth + 1)
                      .map(element => element.dataset.checkOverflow)"""
                )
                if overflow:
                    raise CoverError(f"표지 영역을 넘는 텍스트: {', '.join(overflow)}")
                page.pdf(path=str(temporary_path), prefer_css_page_size=True, print_background=True)
            finally:
                browser.close()

        reader = PdfReader(temporary_path)
        if len(reader.pages) != 1:
            raise CoverError("PDF가 한 페이지가 아닙니다.")
        page = reader.pages[0]
        if abs(float(page.mediabox.width) - 841.89) > 0.5 or abs(float(page.mediabox.height) - 595.28) > 0.5:
            raise CoverError("PDF가 A4 가로 크기가 아닙니다.")
        content = page.extract_text()
        if any(value not in content for value in values.values()):
            raise CoverError("PDF에서 입력 텍스트를 추출하지 못했습니다.")
        os.replace(temporary_path, output_path)
        return output_path
    finally:
        temporary_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="HTML 템플릿으로 과제 표지 PDF를 만듭니다.")
    parser.add_argument("--data", type=Path, required=True, help="UTF-8 JSON 입력 파일")
    parser.add_argument("--output", type=Path, required=True, help="출력할 PDF 경로")
    parser.add_argument("--force", action="store_true", help="기존 PDF를 교체")
    arguments = parser.parse_args()
    try:
        data = json.loads(arguments.data.read_text(encoding="utf-8"))
        result = render_cover(data, arguments.output, overwrite=arguments.force)
    except (OSError, json.JSONDecodeError, CoverError) as error:
        parser.error(str(error))
    print(result)


if __name__ == "__main__":
    main()
