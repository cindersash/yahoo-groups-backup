"""
Base message interface for all message types in the Yahoo Groups backup system.

This module defines the abstract base class that all message types must implement.
"""
import re
from abc import ABC, abstractmethod
from datetime import datetime
from email.header import decode_header
from typing import List

from parser.constants import PREFIXES_TO_STRIP
from parser.message_utils import BRACKET_REGEX, DEFAULT_SUBJECT


class BaseMessage(ABC):
    """Abstract base class for all message types in the system.
    
    This class defines the interface that all message implementations must follow.
    """

    @staticmethod
    def _decode_mime_header(header: str) -> str:
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

    @staticmethod
    def _normalize_subject(subject: str) -> str:
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
        subject = BaseMessage._decode_mime_header(subject)

        # Extract content from parenthetical references like "... (was Original Subject)"
        match = re.search(r"\(\s*was\s+([^)]*)\)", subject, flags=re.IGNORECASE)
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
    
    @property
    @abstractmethod
    def id(self) -> int:
        """Return the unique identifier for this message."""
        pass
    
    @property
    @abstractmethod
    def subject(self) -> str:
        """Return the message subject."""
        pass
    
    @property
    @abstractmethod
    def normalized_subject(self) -> str:
        """Return the normalized subject (with common reply prefixes removed)."""
        pass
    
    @property
    @abstractmethod
    def sender_name(self) -> str:
        """Return the name of the message sender."""
        pass
    
    @property
    @abstractmethod
    def sender_email(self) -> str:
        """Return the email of the message sender."""
        pass
    
    @property
    @abstractmethod
    def date(self) -> datetime:
        """Return the message date as a timezone-aware datetime object."""
        pass
    
    @property
    @abstractmethod
    def html_content(self) -> str:
        """Return the HTML content of the message."""
        pass
    
    @property
    @abstractmethod
    def references(self) -> List[str]:
        """Return a list of message IDs that this message references."""
        pass
    
    @property
    @abstractmethod
    def url(self) -> str:
        """Return the relative URL to this message's page."""
        pass
        
    @url.setter
    @abstractmethod
    def url(self, value: str) -> None:
        """Set the relative URL to this message's page."""
        pass
