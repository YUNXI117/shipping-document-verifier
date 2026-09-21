"""Tests for safe attachment reading."""

import unittest
from pathlib import Path

from attachments import AttachmentError, UnsupportedAttachmentType, read_attachment


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
            read_attachment(self.data_dir, "attachments/sample.pdf")


if __name__ == "__main__":
    unittest.main()
