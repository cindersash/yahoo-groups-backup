"""Utility functions for the Yahoo Groups Mbox to Static Website Converter."""

import re


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
