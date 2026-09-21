"""Tests for shipment-field extraction."""

import unittest

from extract import extract_fields, extract_numeric_fields


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


class TextFieldExtractionTests(unittest.TestCase):
    def test_extracts_multiline_parties_and_label_synonyms(self) -> None:
        text = """Shipper/Exporter: Example Paper Ltd
  1 Harbour Road; Singapore
Consignee (Non-Negotiable): Buyer Ltd
  2 Market Street; London
Notify Party/Intermediate Consignee: Agent Ltd
Load Port: SINGAPORE (SGSIN)
POD: CALLAO, PERU (PECLL)
Container Count: 2 x 40'HC
Gross Wt (kgs): 42,000 KG"""

        fields = extract_fields(text)

        self.assertEqual(fields.shipper, "Example Paper Ltd\n1 Harbour Road; Singapore")
        self.assertEqual(fields.consignee, "Buyer Ltd\n2 Market Street; London")
        self.assertEqual(fields.notify_party, "Agent Ltd")
        self.assertEqual(fields.port_of_loading, "SINGAPORE (SGSIN)")
        self.assertEqual(fields.port_of_discharge, "CALLAO, PERU (PECLL)")

    def test_extracts_label_only_pdf_layout(self) -> None:
        text = """Shipper
Example Paper Ltd
1 Harbour Road
Consignee
Buyer Ltd
Notify Party
Agent Ltd
POL
SINGAPORE
Port of Discharge (POD)
CALLAO, PERU
Ocean Vessel
TEST VESSEL"""

        fields = extract_fields(text)

        self.assertEqual(fields.shipper, "Example Paper Ltd\n1 Harbour Road")
        self.assertEqual(fields.port_of_loading, "SINGAPORE")
        self.assertEqual(fields.port_of_discharge, "CALLAO, PERU")

    def test_preserves_pipe_delimited_spreadsheet_value(self) -> None:
        fields = extract_fields("Shipper/Exporter | Example Ltd | 1 Harbour Road")
        self.assertEqual(fields.shipper, "Example Ltd | 1 Harbour Road")

    def test_treats_to_the_order_of_as_consignee(self) -> None:
        fields = extract_fields("To the Order of: Example Buyer Ltd")
        self.assertEqual(fields.consignee, "Example Buyer Ltd")

    def test_returns_none_for_missing_text_value(self) -> None:
        fields = extract_fields("""Shipper: ____
Consignee: Buyer Ltd
Port of Loading: TBA
POD: ???""")

        self.assertIsNone(fields.shipper)
        self.assertIsNone(fields.port_of_loading)
        self.assertIsNone(fields.port_of_discharge)


if __name__ == "__main__":
    unittest.main()
