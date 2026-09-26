"""Build and verify a cover-first submission PDF."""

import argparse
import os
import tempfile
import unicodedata
from pathlib import Path

from pypdf import PdfReader, PdfWriter


class MergeError(ValueError):
    """An input or output cannot safely produce the requested submission."""


def _filename_part(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MergeError(f"{label} 값이 필요합니다.")
    value = unicodedata.normalize("NFC", value.strip())
    if value in {".", ".."} or any(
        character in '/\\:<>"|?*' or ord(character) < 32 for character in value
    ):
        raise MergeError(f"{label}에 파일명으로 사용할 수 없는 문자가 있습니다.")
    return value


def _read_pdf(path: Path, label: str) -> PdfReader:
    if not path.is_file():
        raise MergeError(f"{label} PDF를 찾지 못했습니다: {path}")
    try:
        reader = PdfReader(path)
        if not reader.pages:
            raise MergeError(f"{label} PDF에 페이지가 없습니다: {path}")
        return reader
    except MergeError:
        raise
    except Exception as error:
        raise MergeError(f"{label} PDF를 읽을 수 없습니다: {path}: {error}") from error


def merge_report(
    *,
    report: Path,
    cover: Path,
    assignment_dir: Path,
    assignment_number: int,
    student_id: str,
    student_name: str,
    replace: bool = False,
) -> Path:
    report = Path(report)
    cover = Path(cover)
    assignment_dir = Path(assignment_dir)
    if isinstance(assignment_number, bool) or not isinstance(assignment_number, int) or assignment_number < 1:
        raise MergeError("과제 번호는 1 이상의 정수여야 합니다.")
    if unicodedata.normalize("NFC", assignment_dir.name) != f"과제{assignment_number}" or not assignment_dir.is_dir():
        raise MergeError(f"과제 폴더는 존재하는 과제{assignment_number}이어야 합니다: {assignment_dir}")
    student_id = _filename_part(student_id, "학번")
    student_name = _filename_part(student_name, "이름")
    output = assignment_dir / "제출용" / f"HW{assignment_number}_{student_id}_{student_name}.pdf"
    if output.exists() and not replace:
        raise MergeError(f"제출용 PDF가 이미 있습니다. 교체하려면 --replace를 지정하세요: {output}")
    if report.resolve() == cover.resolve() or output.resolve() in {report.resolve(), cover.resolve()}:
        raise MergeError("보고서, 표지, 제출용 PDF는 서로 다른 파일이어야 합니다.")

    cover_pdf = _read_pdf(cover, "표지")
    report_pdf = _read_pdf(report, "보고서")
    if len(cover_pdf.pages) != 1:
        raise MergeError(f"표지는 정확히 1쪽이어야 합니다: {cover}")

    writer = PdfWriter()
    sources = [cover_pdf.pages[0], *report_pdf.pages]
    try:
        for page in sources:
            writer.add_page(page)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            prefix=".merge-", suffix=".pdf", dir=output.parent, delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
        try:
            with temporary_path.open("wb") as stream:
                writer.write(stream)
            merged = PdfReader(temporary_path)
            if len(merged.pages) != len(sources):
                raise MergeError("병합 후 페이지 수가 원본과 다릅니다.")
            for number, (source, actual) in enumerate(zip(sources, merged.pages), 1):
                if source.mediabox != actual.mediabox or source.extract_text() != actual.extract_text():
                    raise MergeError(f"병합 결과 {number}쪽이 원본과 다릅니다.")
            if replace:
                os.replace(temporary_path, output)
            else:
                try:
                    os.link(temporary_path, output)
                except FileExistsError as error:
                    raise MergeError(f"제출용 PDF가 이미 있습니다: {output}") from error
        finally:
            temporary_path.unlink(missing_ok=True)
    except MergeError:
        raise
    except Exception as error:
        raise MergeError(f"병합 또는 검증에 실패했습니다: {error}") from error
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--assignment-dir", required=True, type=Path)
    parser.add_argument("--assignment-number", required=True, type=int)
    parser.add_argument("--student-id", required=True)
    parser.add_argument("--student-name", required=True)
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    try:
        print(merge_report(**vars(args)))
    except MergeError as error:
        parser.exit(1, f"오류: {error}\n")


if __name__ == "__main__":
    main()
