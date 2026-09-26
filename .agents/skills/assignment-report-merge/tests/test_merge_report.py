import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path

from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from merge_report import MergeError, merge_report


def make_pdf(path: Path, widths: tuple[int, ...]) -> None:
    writer = PdfWriter()
    for width in widths:
        writer.add_blank_page(width=width, height=500)
    with path.open("wb") as stream:
        writer.write(stream)


class MergeReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.assignment_dir = self.root / "과제" / "과제2"
        self.assignment_dir.mkdir(parents=True)
        self.cover = self.assignment_dir / "표지.pdf"
        self.report = self.root / "Downloads" / "report.pdf"
        self.report.parent.mkdir()
        make_pdf(self.cover, (800,))
        make_pdf(self.report, (600, 700))

    def merge(self, *, replace: bool = False) -> Path:
        return merge_report(
            report=self.report,
            cover=self.cover,
            assignment_dir=self.assignment_dir,
            assignment_number=2,
            student_id="202220953",
            student_name="신현준",
            replace=replace,
        )

    def test_creates_named_submission_with_cover_first(self) -> None:
        output = self.merge()
        self.assertEqual(output, self.assignment_dir / "제출용" / "HW2_202220953_신현준.pdf")
        widths = [int(page.mediabox.width) for page in PdfReader(output).pages]
        self.assertEqual(widths, [800, 600, 700])

    def test_accepts_decomposed_korean_assignment_folder(self) -> None:
        decomposed = self.root / "과제" / unicodedata.normalize("NFD", "과제2")
        output = merge_report(
            report=self.report,
            cover=self.cover,
            assignment_dir=decomposed,
            assignment_number=2,
            student_id="202220953",
            student_name="신현준",
        )
        self.assertEqual(output.parent, decomposed / "제출용")

    def test_existing_submission_is_preserved_without_replace(self) -> None:
        output = self.merge()
        original = output.read_bytes()
        make_pdf(self.report, (300,))
        with self.assertRaises(MergeError):
            self.merge()
        self.assertEqual(output.read_bytes(), original)

    def test_invalid_cover_does_not_create_submission(self) -> None:
        make_pdf(self.cover, (800, 900))
        with self.assertRaises(MergeError):
            self.merge()
        self.assertFalse((self.assignment_dir / "제출용" / "HW2_202220953_신현준.pdf").exists())

    def test_failed_replacement_preserves_existing_submission(self) -> None:
        output = self.merge()
        original = output.read_bytes()
        make_pdf(self.report, ())
        with self.assertRaises(MergeError):
            self.merge(replace=True)
        self.assertEqual(output.read_bytes(), original)

    def test_rejects_path_separators_in_filename_fields(self) -> None:
        with self.assertRaises(MergeError):
            merge_report(
                report=self.report,
                cover=self.cover,
                assignment_dir=self.assignment_dir,
                assignment_number=2,
                student_id="2022/20953",
                student_name="신현준",
            )


if __name__ == "__main__":
    unittest.main()
