import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from assignment_cover import CoverError, render_cover


SAMPLE = {
    "course": "[2027-1] 운영체제",
    "assignment_label": "과제 2",
    "assignment_topic": "Process scheduling",
    "student_id": "123456789",
    "student_name": "홍길동",
}


class RenderCoverTests(unittest.TestCase):
    def test_renders_extractable_a4_landscape_pdf_with_pretendard(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "cover.pdf"
            render_cover(SAMPLE, output)
            reader = PdfReader(output)
            self.assertEqual(len(reader.pages), 1)
            page = reader.pages[0]
            self.assertAlmostEqual(float(page.mediabox.width), 841.89, delta=0.5)
            self.assertAlmostEqual(float(page.mediabox.height), 595.28, delta=0.5)
            content = page.extract_text()
            for value in SAMPLE.values():
                self.assertIn(value, content)
            self.assertNotIn("Banker's algorithm", content)

            fonts = subprocess.check_output(["pdffonts", str(output)], text=True)
            self.assertIn("Pretendard", fonts)
            self.assertNotIn("AppleGothic", fonts)

    def test_missing_identity_creates_no_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "cover.pdf"
            with self.assertRaises(CoverError):
                render_cover({**SAMPLE, "student_name": "미제공"}, output)
            self.assertFalse(output.exists())

    def test_overflow_creates_no_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "cover.pdf"
            with self.assertRaises(CoverError):
                render_cover({**SAMPLE, "assignment_topic": "긴제목" * 100}, output)
            self.assertFalse(output.exists())

    def test_existing_pdf_is_preserved_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "cover.pdf"
            output.write_bytes(b"existing")
            with self.assertRaises(CoverError):
                render_cover(SAMPLE, output)
            self.assertEqual(output.read_bytes(), b"existing")


if __name__ == "__main__":
    unittest.main()
