"""Inspect participant input data without reading any answer files."""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect one email and its attachments")
    parser.add_argument("--data", type=Path, default=Path("hac"))
    parser.add_argument("--email", default="email_001")
    args = parser.parse_args()

    if not args.email.startswith("email_") or not args.email[6:].isdigit():
        parser.error("--email must use an ID such as email_001")

    data_dir = args.data.resolve()
    email_path = data_dir / "inbox" / f"{args.email}.json"
    if not email_path.is_file():
        parser.error(f"Email not found: {email_path}")

    email = json.loads(email_path.read_text(encoding="utf-8"))
    print(f"ID: {email['email_id']}")
    print(f"From: {email['from']}")
    print(f"Subject: {email['subject']}")
    print(f"Body:\n{email['body']}\n")

    for attachment in email.get("attachments", []):
        path = (data_dir / attachment).resolve()
        if not path.is_relative_to(data_dir) or not path.is_file():
            print(f"Attachment unavailable: {attachment}")
            continue
        print(f"Attachment: {attachment}")
        if path.suffix.lower() == ".txt":
            print(path.read_text(encoding="utf-8", errors="replace")[:1200])
        else:
            print(f"  Binary file ({path.suffix.lower()}); support will be added later")
        print()


if __name__ == "__main__":
    main()
