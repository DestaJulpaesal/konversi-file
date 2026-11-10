import unittest

from exe_to_pdf.core import ExtractionError, extract_pdf


PDF = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF"


class ExtractionTests(unittest.TestCase):
    def test_extracts_embedded_pdf(self):
        result = extract_pdf(b"MZ" + b"\x00" * 10 + PDF + b"\x00", "report.exe")
        self.assertEqual(result.pdf, PDF)
        self.assertEqual(result.source_name, "report.exe")
        self.assertEqual(len(result.pdf_sha256), 64)

    def test_rejects_regular_exe(self):
        with self.assertRaises(ExtractionError):
            extract_pdf(b"MZ" + b"\x00" * 100, "program.exe")

    def test_rejects_empty_file(self):
        with self.assertRaises(ExtractionError):
            extract_pdf(b"")
