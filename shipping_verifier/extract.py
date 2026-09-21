"""Extract structured shipment fields from attachment text."""

import re

from models import ShipmentFields


CONTAINER_PATTERN = re.compile(
    r"^(?:Container Count|Total Containers|No\.\s*of Containers(?: or Packages)?)"
    r"[^:|\r\n]*(?::|\|)\s*(\d+)",
    re.IGNORECASE | re.MULTILINE,
)

WEIGHT_PATTERN = re.compile(
    r"^(?:TOTAL\s+)?Gross\s+(?:Weight(?:毛重)?|Wt)"
    r"[^:|\r\n]*(?::|\|)\s*([\d,]+)(?:\.\d+)?\s*(?:KG|KGS)?",
    re.IGNORECASE | re.MULTILINE,
)


def parse_integer(raw_value: str) -> int:
    """Convert a display value such as `21,577` to an integer."""
    return int(raw_value.replace(",", ""))


def first_integer(pattern: re.Pattern[str], text: str) -> int | None:
    match = pattern.search(text)
    return parse_integer(match.group(1)) if match else None


def extract_numeric_fields(text: str) -> ShipmentFields:
    """Extract the two numeric comparison fields from document text."""
    return ShipmentFields(
        container_count=first_integer(CONTAINER_PATTERN, text),
        gross_weight_kg=first_integer(WEIGHT_PATTERN, text),
    )
