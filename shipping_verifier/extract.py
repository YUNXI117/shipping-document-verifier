"""Extract structured shipment fields from attachment text."""

import re
from collections.abc import Iterator
from dataclasses import dataclass

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


@dataclass(frozen=True, slots=True)
class TextFieldRule:
    name: str
    label: re.Pattern[str]


def label_pattern(label: str) -> re.Pattern[str]:
    """Build a line pattern that accepts optional descriptions and delimiters."""
    return re.compile(
        rf"^\s*(?:{label})(?:\s*\([^)]*\))*\s*(?:(?::|\|)\s*(.*))?$",
        re.IGNORECASE,
    )


TEXT_FIELD_RULES = (
    TextFieldRule("shipper", label_pattern(r"Shipper(?:/Exporter)?")),
    TextFieldRule("consignee", label_pattern(r"Consignee|To the Order of")),
    TextFieldRule(
        "notify_party",
        label_pattern(r"Notify(?: Party(?:/Intermediate Consignee)?)?"),
    ),
    TextFieldRule(
        "port_of_loading",
        label_pattern(r"Port of Loading|Load Port|POL"),
    ),
    TextFieldRule(
        "port_of_discharge",
        label_pattern(r"Port of Discharge|Discharge Port|POD"),
    ),
)

OTHER_FIELD_LABEL = label_pattern(
    r"Container Count|Total Containers|No\.\s*of Containers(?: or Packages)?|"
    r"(?:TOTAL\s+)?Gross\s+(?:Weight(?:毛重)?|Wt)|Ocean Vessel|Vessel|"
    r"Export Carrier|CONTAINER NO\.|Commodity|Description|HS Code|Booking(?: No| Ref)?|"
    r"B/L (?:NO\.|NUMBER)|Bill of Lading No\.|Voy(?:age|\. No)?|OC No\.|Freight"
)

MISSING_VALUE = re.compile(r"^(?:N/?A|TBA|_+|\?+|\s*)$", re.IGNORECASE)


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


def matching_field(line: str) -> Iterator[tuple[TextFieldRule, re.Match[str]]]:
    for rule in TEXT_FIELD_RULES:
        match = rule.label.match(line)
        if match:
            yield rule, match


def starts_known_field(line: str) -> bool:
    return any(matching_field(line)) or OTHER_FIELD_LABEL.match(line) is not None


def clean_text_value(lines: list[str]) -> str | None:
    value = "\n".join(line.strip() for line in lines if line.strip()).strip()
    return None if MISSING_VALUE.fullmatch(value) else value


def extract_text_fields(text: str) -> dict[str, str | None]:
    """Extract multiline party and port values while preserving their content."""
    lines = text.splitlines()
    extracted: dict[str, str | None] = {rule.name: None for rule in TEXT_FIELD_RULES}
    index = 0
    while index < len(lines):
        match_info = next(matching_field(lines[index]), None)
        if match_info is None:
            index += 1
            continue

        rule, match = match_info
        value_lines = [match.group(1) or ""]
        index += 1
        while index < len(lines) and not starts_known_field(lines[index]):
            if lines[index].strip():
                value_lines.append(lines[index])
            index += 1
        extracted[rule.name] = clean_text_value(value_lines)
    return extracted


def extract_fields(text: str) -> ShipmentFields:
    """Extract all currently supported shipment fields from document text."""
    numeric = extract_numeric_fields(text)
    values = extract_text_fields(text)
    return ShipmentFields(
        shipper=values["shipper"],
        consignee=values["consignee"],
        notify_party=values["notify_party"],
        port_of_loading=values["port_of_loading"],
        port_of_discharge=values["port_of_discharge"],
        container_count=numeric.container_count,
        gross_weight_kg=numeric.gross_weight_kg,
    )
