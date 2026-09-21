"""Read attachment content through one format-independent interface."""

from pathlib import Path


class AttachmentError(Exception):
    """Base exception for attachment-reading failures."""


class UnsupportedAttachmentType(AttachmentError):
    """Raised when no reader is available for a file extension."""


def resolve_attachment(data_dir: Path, attachment: str) -> Path:
    """Resolve an attachment path and prevent access outside the dataset."""
    root = data_dir.resolve()
    path = (root / attachment).resolve()
    if not path.is_relative_to(root):
        raise AttachmentError(f"Attachment is outside the dataset: {attachment}")
    if not path.is_file():
        raise AttachmentError(f"Attachment does not exist: {attachment}")
    return path


def read_attachment(data_dir: Path, attachment: str) -> str:
    """Extract text from a supported attachment."""
    path = resolve_attachment(data_dir, attachment)
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    raise UnsupportedAttachmentType(
        f"Unsupported attachment type: {path.suffix.lower() or '<none>'}"
    )
