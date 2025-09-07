from email.message import Message as EmailMessage
from email.header import Header

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
            # Test with attachment indicators
            ("Throckmorton letterbox [1 Attachment]", "Throckmorton letterbox"),
            ("Meeting notes [2 Attachments]", "Meeting notes"),
            ("Project Update [3 Attachments]", "Project Update"),
            ("[IMPORTANT] Report [1 Attachment]", "Report"),
            ("Re: Project Status [2 Attachments] ", "Project Status"),
            # Test with empty or whitespace subjects
            ("", DEFAULT_SUBJECT),
            ("   ", DEFAULT_SUBJECT),
            # Test with parenthetical references
            (
                "Northeast Texas Fires (was Re: [letterboxingtexas] Re: Balloon Festival)",
                "Balloon Festival",
            ),
            ("Meeting (was Re: [group] Re: Project Update)", "Project Update"),
            ("Meeting ( was Re: [group] Re: Project Update)", "Project Update"),
            ("(was Re: [test] Re: Original Subject)", "Original Subject"),
            (
                "Snake Phenomena (was [letterboxingtexas] Spring must be close...)",
                "Spring must be close...",
            ),
            ("(was [test] Original Subject)", "Original Subject"),
            (
                "More on LBNA (was Re: [letterboxingtexas] Re: Search Discrepancy - Follow Up & Thanks)",
                "Search Discrepancy - Follow Up & Thanks",
            ),
            # Test with only prefixes
            ("[Test]", DEFAULT_SUBJECT),
            ("Re: ", DEFAULT_SUBJECT),
            ("[1 Attachment]", DEFAULT_SUBJECT),
        ],
    )
    def test_normalize_subject(self, input_subject: str, expected_output: str):
        email_message = EmailMessage()
        email_message["From"] = "sender@example.com"
        email_message["Subject"] = input_subject

        message = Message(msg_id=1, msg=email_message)

        # The normalized subject should be stored in the normalized_subject attribute
        assert message.normalized_subject == expected_output

    @pytest.mark.parametrize(
        "input_subject, expected_output",
        [
            # Test MIME-encoded subject with UTF-8 and emoji
            (
                "_=?UTF-8?Q?[LETTERBOXINGTEXAS]_A?= =?UTF-8?Q?_Old_Bum_&_A_Tall_Cookie_=F0=9F=98=82?=",
                "A Old Bum & A Tall Cookie 😂",
            ),
            # Test MIME-encoded with different charsets
            ("=?ISO-8859-1?Q?This=20is=20some=20text?=", "This is some text"),
            # Test with multiple encoded parts
            ("=?utf-8?q?Hello_=F0=9F=98=80?= =?utf-8?q?_World?=", "Hello 😀 World"),
            # Test with mixed encoded and plain text
            ("Important: =?utf-8?q?Meeting_=F0=9F=93=85?= tomorrow", "Important: Meeting 📅 tomorrow"),
            # Test with MIME-encoded Re: prefix
            ("=?utf-8?q?Re=3A_=F0=9F=93=9D_Project_Update?=", "📝 Project Update"),
            # Test with invalid encoding (should be handled gracefully)
            ("=?invalid-charset?q?test?=", "test"),
        ],
    )
    def test_mime_encoded_subjects(self, input_subject: str, expected_output: str):
        """Test that MIME-encoded subjects are properly decoded and normalized."""
        email_message = EmailMessage()
        email_message["From"] = "sender@example.com"
        email_message["Subject"] = input_subject

        message = Message(msg_id=1, msg=email_message)

        # The normalized subject should have the MIME encoding properly decoded
        assert message.normalized_subject == expected_output

    def test_mime_encoded_header_directly(self):
        """Test the _decode_mime_header method with various edge cases."""
        # Test with None input
        assert Message._decode_mime_header(None) == ""

        # Test with empty string
        assert Message._decode_mime_header("") == ""

        # Test with non-string input
        assert Message._decode_mime_header(123) == "123"

        # Test with already decoded string
        assert Message._decode_mime_header("Hello World") == "Hello World"
