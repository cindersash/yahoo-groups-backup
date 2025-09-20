"""
JSON Message class for Yahoo Groups JSON data.

This module provides the JSONMessage class which implements the BaseMessage interface
to handle message data from Yahoo Groups JSON exports.
"""
import html
from datetime import datetime
from typing import Dict, Any, List

from bs4 import BeautifulSoup
from dateutil import tz

from .base_message import BaseMessage
from .message_utils import decode_mime_header, normalize_subject, DEFAULT_SUBJECT


class JSONMessage(BaseMessage):
    """Implements BaseMessage for JSON-formatted messages from Yahoo Groups."""

    def __init__(self, msg_id: int, msg_data: Dict[str, Any]):
        """Initialize a message from JSON data.
        
        Args:
            msg_id: The unique identifier for the message
            msg_data: The message data from the JSON file
        """
        self._id = msg_id
        self._msg_data = msg_data
        self._subject = html.unescape(decode_mime_header(msg_data.get('subject', DEFAULT_SUBJECT)))
        self._normalized_subj = normalize_subject(self._subject)
        self._sender_name = msg_data.get('authorName') or msg_data.get('profile')
        self._sender_name = html.unescape(self._sender_name)
        # For some reason, the email is not saved in the JSON data
        self._date = self._parse_date()
        self._topic_id = msg_data.get('topicId')
        self._html_content = self._clean_html_content(msg_data.get('messageBody', ''))
        self._url = f"messages/{self._id}.html"
        
    @property
    def topic_id(self) -> str:
        """Return the topic ID for this message, if available."""
        return self._topic_id
        
    @property
    def is_first_in_thread(self) -> bool:
        """Return True if this is the first message in its thread."""
        return str(self._id) == str(self._topic_id)

    @property
    def id(self) -> int:
        return self._id
        
    @property
    def subject(self) -> str:
        return self._subject
        
    @property
    def normalized_subject(self) -> str:
        return self._normalized_subj
        
    @property
    def sender_name(self) -> str:
        return self._sender_name
        
    @property
    def sender_email(self) -> str:
        return ""
        
    @property
    def date(self) -> datetime:
        return self._date
        
    @property
    def html_content(self) -> str:
        return self._html_content
        
    @property
    def references(self) -> List[str]:
        """Return a list of message IDs that this message references.
        
        For JSON messages, we use the topicId to establish threading.
        If this is not the first message in the thread, we return the topicId as a reference.
        """
        if not self.is_first_in_thread and self._topic_id:
            return [str(self._topic_id)]
        return []
        
    @property
    def url(self) -> str:
        return self._url
        
    @url.setter
    def url(self, value: str) -> None:
        self._url = value

    def _parse_date(self) -> datetime:
        """Parse the post date from the message data."""
        timestamp = int(self._msg_data.get('postDate', 0))
        return datetime.fromtimestamp(timestamp, tz=tz.tzutc())

    @staticmethod
    def _clean_html_content(content: str) -> str:
        """Clean and sanitize HTML content."""
        if not content:
            return ""

        # Use BeautifulSoup to clean the HTML
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script and style elements
        for element in soup(["script", "style"]):
            element.decompose()

        return str(soup)
