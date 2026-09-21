"""Tests for SI-to-BL normalization and comparison."""

import unittest

from compare import compare_fields, normalize_text
from models import ComparisonStatus, ReviewReason, ShipmentFields


def complete_fields(
    *,
    shipper: str | None = "Example Paper Pte. Ltd.\n1 Harbour Road",
    port_of_loading: str | None = "SINGAPORE (SGSIN)",
    port_of_discharge: str | None = "CALLAO, PERU (PECLL)",
    container_count: int | None = 3,
    gross_weight_kg: int | None = 67_311,
) -> ShipmentFields:
    return ShipmentFields(
        shipper=shipper,
        consignee="Buyer Ltd",
        notify_party="Agent Ltd",
        port_of_loading=port_of_loading,
        port_of_discharge=port_of_discharge,
        container_count=container_count,
        gross_weight_kg=gross_weight_kg,
    )


class NormalizationTests(unittest.TestCase):
    def test_normalizes_case_punctuation_and_layout(self) -> None:
        left = "Example Paper Pte. Ltd.\n1 Harbour Road"
        right = "EXAMPLE PAPER PTE LTD | 1 HARBOUR ROAD"
        self.assertEqual(normalize_text(left), normalize_text(right))


class ComparisonTests(unittest.TestCase):
    def test_equivalent_formatting_is_ok(self) -> None:
        si = complete_fields()
        bl = complete_fields(
            shipper="EXAMPLE PAPER PTE LTD | 1 HARBOUR ROAD",
            port_of_loading="Singapore",
        )
        self.assertEqual(compare_fields(si, bl).status, ComparisonStatus.OK)

    def test_reports_only_changed_fields(self) -> None:
        result = compare_fields(
            complete_fields(),
            complete_fields(container_count=4, gross_weight_kg=68_000),
        )
        self.assertEqual(result.status, ComparisonStatus.MISMATCH)
        self.assertEqual(
            [mismatch.field for mismatch in result.mismatches],
            ["container_count", "gross_weight_kg"],
        )

    def test_preserves_original_values_in_mismatch(self) -> None:
        result = compare_fields(
            complete_fields(port_of_discharge="CALLAO, PERU (PECLL)"),
            complete_fields(port_of_discharge="BUSAN, SOUTH KOREA (KRPUS)"),
        )
        mismatch = result.mismatches[0]
        self.assertEqual(mismatch.si_value, "CALLAO, PERU (PECLL)")
        self.assertEqual(mismatch.bl_value, "BUSAN, SOUTH KOREA (KRPUS)")

    def test_missing_value_requires_review(self) -> None:
        result = compare_fields(complete_fields(shipper=None), complete_fields())
        self.assertEqual(result.status, ComparisonStatus.NEEDS_REVIEW)
        self.assertEqual(result.review_reason, ReviewReason.MISSING_VALUE)
        self.assertEqual(result.mismatches, ())


if __name__ == "__main__":
    unittest.main()
