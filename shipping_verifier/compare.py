"""Normalize and compare SI fields against draft BL fields."""

import re
import unicodedata

from models import (
    ComparisonResult,
    ComparisonStatus,
    FieldMismatch,
    ReviewReason,
    ShipmentFields,
)


FIELD_NAMES = (
    "shipper",
    "consignee",
    "notify_party",
    "port_of_loading",
    "port_of_discharge",
    "container_count",
    "gross_weight_kg",
)

PORT_FIELDS = {"port_of_loading", "port_of_discharge"}
PORT_CODE = re.compile(r"\([A-Z]{5}\)", re.IGNORECASE)


def normalize_text(value: str, *, remove_port_code: bool = False) -> str:
    """Normalize formatting without changing the underlying words or numbers."""
    normalized = unicodedata.normalize("NFKC", value).upper()
    if remove_port_code:
        normalized = PORT_CODE.sub(" ", normalized)
    normalized = re.sub(r"[^\w]+", " ", normalized)
    return " ".join(normalized.split())


def comparable_value(field: str, value: str | int) -> str | int:
    if isinstance(value, int):
        return value
    return normalize_text(value, remove_port_code=field in PORT_FIELDS)


def compare_fields(si: ShipmentFields, bl: ShipmentFields) -> ComparisonResult:
    """Compare SI (the reference) with BL, escalating when a value is missing."""
    missing_fields = [
        field
        for field in FIELD_NAMES
        if getattr(si, field) is None or getattr(bl, field) is None
    ]
    if missing_fields:
        return ComparisonResult(
            status=ComparisonStatus.NEEDS_REVIEW,
            review_reason=ReviewReason.MISSING_VALUE,
        )

    mismatches: list[FieldMismatch] = []
    for field in FIELD_NAMES:
        si_value = getattr(si, field)
        bl_value = getattr(bl, field)
        if comparable_value(field, si_value) != comparable_value(field, bl_value):
            mismatches.append(FieldMismatch(field, si_value, bl_value))

    if mismatches:
        return ComparisonResult(
            status=ComparisonStatus.MISMATCH,
            mismatches=tuple(mismatches),
        )
    return ComparisonResult(status=ComparisonStatus.OK)
