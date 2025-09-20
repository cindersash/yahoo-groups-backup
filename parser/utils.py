"""Utility functions for the Yahoo Groups Mbox to Static Website Converter."""

import re
from datetime import datetime

from parser.base_message import BaseMessage


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe string.

    Converts to lowercase, removes special characters, and replaces spaces with hyphens.

    Args:
        text: The text to convert to a slug

    Returns:
        A filesystem-safe string with no spaces or special characters
    """
    if not text:
        return ""

    # Convert to lowercase
    text = str(text).lower()
    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)
    # Remove all non-word characters except hyphens
    text = re.sub(r"[^\w-]", "", text)
    # Replace multiple hyphens with a single hyphen
    text = re.sub(r"-+", "-", text)
    # Remove leading and trailing hyphens
    return text.strip("-")

def _is_valid_message(message: BaseMessage) -> bool:
    # The first messages should be from 1998. Anything earlier is probably corrupted.
    if message.date:
        # Make the comparison timezone-aware by localizing the cutoff date to the message timezone
        cutoff_date = datetime(1998, 1, 1, tzinfo=message.date.tzinfo)
        if message.date < cutoff_date:
            return False

    return bool(message.html_content and message.date)
