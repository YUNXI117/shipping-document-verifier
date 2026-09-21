"""Shared domain types for the shipping-document pipeline."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TypedDict


class EmailRecord(TypedDict):
    email_id: str
    from_: str
    subject: str
    body: str
    attachments: list[str]


class Category(StrEnum):
    BL_COMPARISON = "BL_COMPARISON"
    SI_REQUEST = "SI_REQUEST"
    INVOICE_QUERY = "INVOICE_QUERY"
    GENERAL = "GENERAL"
    SPAM = "SPAM"


class ComparisonStatus(StrEnum):
    OK = "OK"
    MISMATCH = "MISMATCH"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class ReviewReason(StrEnum):
    WRONG_DOC_TYPE = "wrong_doc_type"
    MISSING_ATTACHMENT = "missing_attachment"
    UNREADABLE = "unreadable"
    MISSING_VALUE = "missing_value"


@dataclass(frozen=True, slots=True)
class Classification:
    category: Category
    reason: str


@dataclass(frozen=True, slots=True)
class ShipmentFields:
    """The seven values compared between an SI and a draft BL."""

    shipper: str | None = None
    consignee: str | None = None
    notify_party: str | None = None
    port_of_loading: str | None = None
    port_of_discharge: str | None = None
    container_count: int | None = None
    gross_weight_kg: int | None = None


@dataclass(frozen=True, slots=True)
class FieldMismatch:
    field: str
    si_value: str | int
    bl_value: str | int


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    status: ComparisonStatus
    mismatches: tuple[FieldMismatch, ...] = ()
    review_reason: ReviewReason | None = None


def parse_email(raw: object) -> EmailRecord:
    """Validate untrusted JSON and convert its `from` key to `from_`."""
    if not isinstance(raw, dict):
        raise ValueError("Email JSON must be an object")

    required_strings = ("email_id", "from", "subject", "body")
    for field in required_strings:
        if not isinstance(raw.get(field), str):
            raise ValueError(f"Email field '{field}' must be a string")

    attachments = raw.get("attachments")
    if not isinstance(attachments, list) or not all(
        isinstance(item, str) for item in attachments
    ):
        raise ValueError("Email field 'attachments' must be a list of strings")

    return EmailRecord(
        email_id=raw["email_id"],
        from_=raw["from"],
        subject=raw["subject"],
        body=raw["body"],
        attachments=attachments,
    )
