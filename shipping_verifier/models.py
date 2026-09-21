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


@dataclass(frozen=True, slots=True)
class Classification:
    category: Category
    reason: str


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
