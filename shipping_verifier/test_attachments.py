"""Tests for safe attachment reading."""

import unittest
from pathlib import Path

from attachments import AttachmentError, UnsupportedAttachmentType, read_attachment

PARTICIPANT_DATA = Path(__file__).parent.parent / "hac"


class AttachmentReaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data_dir = Path(__file__).parent / "test_data"

    def test_reads_utf8_text_attachment(self) -> None:
        text = read_attachment(self.data_dir, "attachments/sample.txt")

        self.assertEqual(text, "SHIPPER: Example Ltd\n")

    def test_rejects_path_outside_dataset(self) -> None:
        with self.assertRaises(AttachmentError):
            read_attachment(self.data_dir, "../secret.txt")

    def test_reports_unsupported_file_type(self) -> None:
        with self.assertRaises(UnsupportedAttachmentType):
            read_attachment(self.data_dir, "attachments/sample.bin")

    @unittest.skipUnless(PARTICIPANT_DATA.is_dir(), "participant dataset is unavailable")
    def test_reads_pdf_attachment(self) -> None:
        text = read_attachment(PARTICIPANT_DATA, "attachments/email_059_SI.pdf")
        self.assertIn("BILL OF LADING INSTRUCTION", text)
        self.assertIn("No. of Containers", text)

    @unittest.skipUnless(PARTICIPANT_DATA.is_dir(), "participant dataset is unavailable")
    def test_reads_docx_attachment(self) -> None:
        text = read_attachment(PARTICIPANT_DATA, "attachments/email_055_BL.docx")
        self.assertIn("BILL OF LADING", text)

    @unittest.skipUnless(PARTICIPANT_DATA.is_dir(), "participant dataset is unavailable")
    def test_reads_xlsx_attachment(self) -> None:
        text = read_attachment(PARTICIPANT_DATA, "attachments/email_055_SI.xlsx")
        self.assertIn("BL INSTRUCTION", text)
        self.assertIn("Container Count", text)


if __name__ == "__main__":
    unittest.main()
