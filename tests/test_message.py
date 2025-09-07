from email.message import Message as EmailMessage

import pytest

from parser.message import Message, DEFAULT_SUBJECT


class TestMessage:
    @pytest.fixture
    def mock_email_message(self):
        """Create a mock email message with a subject."""

    @pytest.mark.parametrize(
        "input_subject, expected_output",
        [
            # Test basic subject
            ("Hello World", "Hello World"),
            # Test with [text] prefix
            ("[Test] Hello World", "Hello World"),
            ("[Test] [Important] Hello World", "Hello World"),
            ("  [Test]  [Important]  Hello World  ", "Hello World"),
            # Test with Re: and Fwd: prefixes
            ("Re: Hello World", "Hello World"),
            ("Fwd: Hello World", "Hello World"),
            ("Re: Fwd: Hello World", "Hello World"),
            # Test with mixed prefixes
            ("[Test] Re: Hello World", "Hello World"),
            ("Re: [Test] Hello World", "Hello World"),
            # Test with empty or whitespace subjects
            ("", DEFAULT_SUBJECT),
            ("   ", DEFAULT_SUBJECT),
            # Test with only prefixes
            ("[Test]", DEFAULT_SUBJECT),
            ("Re: ", DEFAULT_SUBJECT),
        ],
    )
    def test_normalize_subject(self, input_subject: str, expected_output: str):
        email_message = EmailMessage()
        email_message["From"] = "sender@example.com"
        email_message["Subject"] = input_subject

        message = Message(msg_id=1, msg=email_message)

        # The normalized subject should be stored in the normalized_subject attribute
        assert message.normalized_subject == expected_output
