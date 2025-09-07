import email
import re
from datetime import datetime
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime
from typing import Optional, Tuple, List, Union

from bs4 import BeautifulSoup
from dateutil import tz

from parser.constants import PREFIXES_TO_STRIP

DEFAULT_SUBJECT = "(No subject)"
BRACKET_REGEX = re.compile(r"^\s*\[.*?]\s*")


class Message:
    """Represents an email message with its metadata and content."""

    def __init__(self, msg_id: int, msg: email.message.Message):
        self.id = msg_id
        self.subject = self._get_header(msg, "Subject", DEFAULT_SUBJECT)
        self.normalized_subject = self._normalize_subject(self.subject)
        self.sender_name, self.sender_email = parseaddr(msg["From"])
        self.date = self._parse_date(msg)
        self.references = self._get_references(msg)
        self.html_content = self._extract_content(msg)
        self.url = f"messages/{self.id}.html"

    @classmethod
    def _decode_mime_header(cls, header: str) -> str:
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
        except Exception as e:
            # If anything goes wrong, return the original string with leading underscores removed
            return str(header).lstrip("_").strip()

    @classmethod
    def _normalize_subject(cls, subject: str) -> str:
        """Normalize thread subject by:
        1. Decoding MIME-encoded parts
        2. Extracting original subject from parenthetical references (e.g., '... (was Re: [group] Re: Original Subject)')
        3. Removing 'Re:', 'Fwd:', etc. prefixes
        4. Removing [text] prefixes
        5. Removing [X Attachment(s)] suffixes
        6. Normalizing whitespace
        """
        if not subject:
            return ""

        # First decode any MIME-encoded parts
        subject = cls._decode_mime_header(subject)

        # Extract original subject from parenthetical references like "... (was [group] Original Subject)"
        was_pattern = r"\(\s*was\s+(?:re:\s*)?\[.*?\]\s*(?:re:\s*)?(.*?)\)$"
        match = re.search(was_pattern, subject, flags=re.IGNORECASE)
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
                    subject = subject[len(p) :].lstrip()  # remove the prefix + leading spaces
                    stripped = True
                    break  # check prefixes again from the start

            # If we still have [bracketed] content, strip it in the next iteration
            if re.match(BRACKET_REGEX, subject):
                stripped = True

        subject = subject.strip()

        return subject if subject else DEFAULT_SUBJECT

    @staticmethod
    def _get_header(msg: email.message.Message, header: str, default: str = "") -> str:
        """Safely get a header from the email message."""
        value = msg.get(header, "")
        if not value:
            return default
        return str(value)

    def _parse_date(self, msg: email.message.Message) -> Optional[datetime]:
        """Parse the date from the email message and ensure it's timezone-aware."""
        date_str = self._get_header(msg, "Date")
        if not date_str:
            return None

        try:
            dt = parsedate_to_datetime(date_str)
            # If the datetime is naive, make it timezone-aware with UTC
            if dt.tzinfo is None:
                return dt.replace(tzinfo=tz.UTC)
            return dt
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_references(msg: email.message.Message) -> list[str]:
        """Extract message references for threading."""
        refs = []
        if "References" in msg:
            refs.extend(msg["References"].replace("\n", "").split())
        if "In-Reply-To" in msg:
            refs.append(msg["In-Reply-To"])
        return [ref.strip("<>") for ref in refs if ref.strip()]

    @staticmethod
    def _extract_content(msg: email.message.Message) -> Optional[str]:
        """Extract and process the message content."""
        # Try to get HTML content first
        html_part = None
        text_part = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/html" and not html_part:
                    html_part = part.get_payload(decode=True).decode("utf-8", "ignore")
                elif content_type == "text/plain" and not text_part:
                    text_part = part.get_payload(decode=True).decode("utf-8", "ignore")
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                if content_type == "text/html":
                    html_part = payload.decode("utf-8", "ignore")
                elif content_type == "text/plain":
                    text_part = payload.decode("utf-8", "ignore")

        # Return HTML if available, otherwise convert text to HTML
        if html_part:
            # Clean up HTML
            soup = BeautifulSoup(html_part, "lxml")
            # Remove potentially harmful elements
            for element in soup(["script", "iframe", "object", "embed"]):
                element.decompose()
            return str(soup)
        elif text_part:
            # Convert plain text to HTML, preserving line breaks
            text_part = text_part.replace("\n", "<br>\n")
            return f'<div class="plaintext-content">{text_part}</div>'

        return None
