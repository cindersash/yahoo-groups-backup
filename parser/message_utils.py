"""
Shared utilities for message processing.
"""
import re
from email.header import decode_header

DEFAULT_SUBJECT = "(No subject)"
BRACKET_REGEX = re.compile(r"^\s*\[.*?]\s*")
PREFIXES_TO_STRIP = ["re:", "fwd:", "fw:", "aw:", "vs:", "sv:", "re[\d]*:", "fwd[\d]*:"]


def decode_mime_header(header: str) -> str:
    """Decode MIME-encoded header values."""
    if not header:
        return ""

    try:
        # Decode the header parts
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                # Try to decode with the specified encoding, fall back to utf-8 with replace
                try:
                    decoded_part = part.decode(encoding or "utf-8", errors="replace")
                except (LookupError, UnicodeError):
                    # If the encoding is unknown or invalid, try utf-8 with replace
                    decoded_part = part.decode("utf-8", errors="replace")
                decoded_parts.append(decoded_part)
            else:
                decoded_parts.append(part)

        # Join all parts, normalize whitespace, and remove any leading underscores
        result = " ".join(str(part).strip() for part in decoded_parts if part)
        # Remove any leading underscores that might be left after decoding
        return result.lstrip("_").strip()
    except Exception:
        # If anything goes wrong, return the original string with leading underscores removed
        return str(header).lstrip("_").strip()


def normalize_subject(subject: str) -> str:
    """Normalize thread subject by removing common prefixes and formatting."""
    if not subject:
        return DEFAULT_SUBJECT

    # Extract content from parenthetical references like "... (was Original Subject)"
    match = re.search(r"\(\s * was\s+([^)] * )\)", subject, flags = re.IGNORECASE)
    if match:
        subject = match.group(1).strip()

    # Remove any attachment indicators from the end (e.g., [1 Attachment], [2 Attachments], etc.)
    subject = re.sub(r"\s*\[\s*\d+\s+Attachments?\s*]\s*$", "", subject, flags=re.IGNORECASE)

    # Process prefixes and other normalizations
    stripped = True
    while stripped:
        stripped = False

        # Remove [bracketed] prefixes
        subject = re.sub(BRACKET_REGEX, "", subject)

        # Check for and remove reply/forward prefixes (Re:, Fwd:, etc.)
        lower_subject = subject.lower()
        for p in PREFIXES_TO_STRIP:
            if lower_subject.startswith(p.lower()):
                subject = subject[len(p):].lstrip()  # remove the prefix + leading spaces
                stripped = True
                break  # check prefixes again from the start

        # If we still have [bracketed] content, strip it in the next iteration
        if re.match(BRACKET_REGEX, subject):
            stripped = True

    subject = subject.strip()
    return subject if subject else DEFAULT_SUBJECT
