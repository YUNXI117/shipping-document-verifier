"""An explainable email-classification baseline."""

import argparse
import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from models import Category, Classification, EmailRecord, parse_email


@dataclass(frozen=True, slots=True)
class Rule:
    category: Category
    reason: str
    matches: Callable[[EmailRecord], bool]


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    """Return True when at least one term occurs in text."""
    return any(term in text for term in terms)


def normalized(email: EmailRecord) -> EmailRecord:
    """Create an uppercase view used only for case-insensitive matching."""
    return EmailRecord(
        email_id=email["email_id"],
        from_=email["from_"].upper(),
        subject=email["subject"].upper(),
        body=email["body"].upper(),
        attachments=email["attachments"],
    )


RULES: tuple[Rule, ...] = (
    Rule(
        Category.BL_COMPARISON,
        "The subject requests draft BL confirmation or amendment",
        lambda email: contains_any(
            email["subject"],
            ("TO CONFIRM DOCS", "REQUEST BL DRAFT", "DRAFT BL", "AMEND BL"),
        ),
    ),
    Rule(
        Category.BL_COMPARISON,
        "The subject uses the AIE document-checking format",
        lambda email: re.search(r"\bAIE\s*-", email["subject"]) is not None,
    ),
    Rule(
        Category.SI_REQUEST,
        "The subject requests a shipping instruction",
        lambda email: contains_any(
            email["subject"],
            ("REQUEST SI", "SI NEEDED", "CUST SI", "SHIPPING INSTRUCTION"),
        )
        or re.search(r"^(RE[:_ ]+)?SI\s*-", email["subject"]) is not None,
    ),
    Rule(
        Category.INVOICE_QUERY,
        "The subject refers to an invoice or charge",
        lambda email: contains_any(
            email["subject"],
            ("INVOICE", "BILLING", "LOCAL CHARGES", "TOTAL FREIGHT", "D & D CHARGES"),
        ),
    ),
    Rule(
        Category.SPAM,
        "The subject or sender contains a strong spam signal",
        lambda email: contains_any(
            email["subject"],
            ("PRIZE", "WINNER", "PARCEL FEE", "MAILBOX FULL", "WEIRD TRICK"),
        )
        or ("NO-REPLY@" in email["from_"] and "VERIFY YOUR ACCOUNT" in email["body"]),
    ),
    Rule(
        Category.BL_COMPARISON,
        "The body explicitly requests an SI and draft BL check",
        lambda email: all(term in email["body"] for term in ("ATTACHED", "SI", "DRAFT BL")),
    ),
)


def classify(email: EmailRecord) -> Classification:
    """Classify an email using the first matching rule."""
    candidate = normalized(email)
    for rule in RULES:
        if rule.matches(candidate):
            return Classification(rule.category, rule.reason)
    return Classification(
        Category.GENERAL,
        "No rule matched; AI or human review may be needed",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify one hackathon email")
    parser.add_argument("--data", type=Path, default=Path("hac"))
    parser.add_argument("--email", default="email_001")
    args = parser.parse_args()
    if re.fullmatch(r"email_\d+", args.email) is None:
        parser.error("--email must use an ID such as email_001")

    path = args.data / "inbox" / f"{args.email}.json"
    if not path.is_file():
        parser.error(f"Email not found: {path}")

    result = classify(parse_email(json.loads(path.read_text(encoding="utf-8"))))
    print(f"{args.email}: {result.category}\nReason: {result.reason}")


if __name__ == "__main__":
    main()
