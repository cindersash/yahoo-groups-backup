from datetime import datetime
from email.message import Message as EmailMessage
from email.utils import parseaddr, parsedate_to_datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from dateutil import tz

from parser.base_message import BaseMessage
from parser.message_utils import (
    decode_mime_header,
    normalize_subject,
    DEFAULT_SUBJECT
)


class MboxMessage(BaseMessage):
    """Represents an email message from an mbox file with its metadata and content."""

    def __init__(self, msg_id: int, msg: EmailMessage):
        self._id = msg_id
        self._subject = self._get_header(msg, "Subject", DEFAULT_SUBJECT)
        self._normalized_subject = self._normalize_subject(self.subject)
        self._sender_name, self._sender_email = parseaddr(msg["From"])
        self._date = self._parse_date(msg)
        self._references = self._get_references(msg)
        self._html_content = self._extract_content(msg)
        self._url = f"messages/{self.id}.html"

    @staticmethod
    def _get_header(msg: EmailMessage, header: str, default: str = "") -> str:
        """Safely get a header from the email message."""
        value = msg.get(header, "")
        if not value:
            return default
        return decode_mime_header(str(value))

    def _parse_date(self, msg: EmailMessage) -> Optional[datetime]:
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
    def _get_references(msg: EmailMessage) -> list[str]:
        """Extract message references for threading."""
        refs = []
        if "References" in msg:
            refs.extend(msg["References"].replace("\n", "").split())
        if "In-Reply-To" in msg:
            refs.append(msg["In-Reply-To"])
        return [ref.strip("<>") for ref in refs if ref.strip()]

    @staticmethod
    def _extract_content(msg: EmailMessage) -> Optional[str]:
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

    # Property implementations from BaseMessage
    @property
    def id(self) -> int:
        return self._id

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def normalized_subject(self) -> str:
        return self._normalized_subject

    @property
    def sender_name(self) -> str:
        return self._sender_name

    @property
    def sender_email(self) -> str:
        return self._sender_email

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def html_content(self) -> str:
        return self._html_content

    @property
    def references(self) -> List[str]:
        return self._references

    @property
    def url(self) -> str:
        """Return the URL of the message."""
        return self._url

    @url.setter
    def url(self, value: str) -> None:
        """Set the URL of the message."""
        self._url = value
