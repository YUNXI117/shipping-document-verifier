"""Tests for shipment-field extraction."""

import unittest

from extract import extract_numeric_fields


class NumericFieldExtractionTests(unittest.TestCase):
    def test_extracts_standard_labels(self) -> None:
        text = """Container Count: 3 x 40'HC
Gross Weight (KG): 67,311 KG"""

        fields = extract_numeric_fields(text)

        self.assertEqual(fields.container_count, 3)
        self.assertEqual(fields.gross_weight_kg, 67_311)

    def test_extracts_synonym_labels(self) -> None:
        text = """No. of Containers or Packages: 12 x 20'FCL
Gross Wt (kgs): 257,340 KG"""

        fields = extract_numeric_fields(text)

        self.assertEqual(fields.container_count, 12)
        self.assertEqual(fields.gross_weight_kg, 257_340)

    def test_extracts_pipe_delimited_spreadsheet_text(self) -> None:
        text = """Container Count | 6 x 40'HC
GROSS WEIGHT | 131058"""

        fields = extract_numeric_fields(text)

        self.assertEqual(fields.container_count, 6)
        self.assertEqual(fields.gross_weight_kg, 131_058)

    def test_extracts_word_table_labels_with_descriptions(self) -> None:
        text = """Total Containers (description) | 12 x 20'FCL
Gross Wt (kgs) (description) | 243,588"""

        fields = extract_numeric_fields(text)

        self.assertEqual(fields.container_count, 12)
        self.assertEqual(fields.gross_weight_kg, 243_588)

    def test_returns_none_for_missing_values(self) -> None:
        text = """No. of Containers:
Gross Weight (KG): N/A"""

        fields = extract_numeric_fields(text)

        self.assertIsNone(fields.container_count)
        self.assertIsNone(fields.gross_weight_kg)


if __name__ == "__main__":
    unittest.main()
