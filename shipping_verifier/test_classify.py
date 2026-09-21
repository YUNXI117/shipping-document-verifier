"""Focused tests for the classification baseline."""

import unittest

from classify import classify
from models import Category, EmailRecord


def email(subject: str, body: str = "", sender: str = "sender@example.com") -> EmailRecord:
    return EmailRecord(
        email_id="email_001",
        from_=sender,
        subject=subject,
        body=body,
        attachments=[],
    )


class ClassifyTests(unittest.TestCase):
    def test_bl_comparison_subject(self) -> None:
        self.assertEqual(
            classify(email("RE: TO CONFIRM DOCS 123")).category,
            Category.BL_COMPARISON,
        )

    def test_si_request_subject(self) -> None:
        self.assertEqual(classify(email("SI - booking 123")).category, Category.SI_REQUEST)

    def test_invoice_subject(self) -> None:
        self.assertEqual(
            classify(email("Local charges for shipment" )).category,
            Category.INVOICE_QUERY,
        )

    def test_spam_subject(self) -> None:
        self.assertEqual(classify(email("You are a prize winner")).category, Category.SPAM)

    def test_unmatched_email(self) -> None:
        self.assertEqual(classify(email("Weekly operations update")).category, Category.GENERAL)

if __name__ == "__main__":
    unittest.main()
