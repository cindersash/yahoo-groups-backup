"""
HTML generation utilities for the Yahoo Groups Mbox to Static Website Converter.
"""

import json
import time
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import constants
from .message import Message


class SiteGenerator:
    """Handles the generation of static website files from message data."""

    def __init__(self, output_dir: str):
        """Initialize the SiteGenerator with output directory and template environment."""
        self.output_dir = Path(output_dir)
        self.messages_dir = self.output_dir / 'messages'
        self.static_dir = self.output_dir / 'static'
        self.search_dir = self.output_dir / 'search'
        
        # Create output directories
        for directory in [self.output_dir, self.messages_dir, self.static_dir, self.search_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set up template environment
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_site(self, messages: List[Message]) -> None:
        """Generate the complete static website."""
        print("\nGenerating static website...")
        start_time = time.time()
        total_messages = len(messages)
        
        # Copy static files
        print("Copying static files...")
        self._copy_static_files()
        
        # Generate individual message pages
        print(f"Generating {total_messages} message pages...")
        generated_count = 0
        for i, message in enumerate(messages, 1):
            self._generate_message_page(message, messages)
            if message.html_content and message.html_content.strip() != '<p>No content available</p>':
                generated_count += 1
            
            # Show progress every 100 messages
            if i % 100 == 0 or i == total_messages:
                elapsed = time.time() - start_time
                rate = i / elapsed if elapsed > 0 else 0
                print(f"  Processed {i}/{total_messages} messages ({i/total_messages:.1%}), "
                      f"generated {generated_count} pages - {rate:.1f} msg/sec")
        
        # Generate index page
        print("\nGenerating index page...")
        self._generate_index_page(messages)
        
        # Generate search index
        print("Generating search index...")
        self._generate_search_index(messages)
        
        elapsed = time.time() - start_time
        print(f"\nWebsite generation completed in {elapsed:.1f} seconds")
        print(f"Total pages generated: {generated_count} message pages + index + search")

    def _copy_static_files(self) -> None:
        """Copy static files (CSS, JS) to the output directory."""
        # Write CSS file
        with open(self.static_dir / 'style.css', 'w', encoding='utf-8') as f:
            f.write(constants.CSS_STYLES)

        # Write JavaScript file
        with open(self.static_dir / 'script.js', 'w', encoding='utf-8') as f:
            f.write(constants.JAVASCRIPT_CODE)

    def _generate_message_page(self, message: Message, all_messages: List[Message]) -> None:
        """Generate an HTML page for a single message."""
        # Skip if message has no content
        if not message.html_content or message.html_content.strip() == '<p>No content available</p>':
            return
            
        # Find replies to this message
        replies = [m for m in all_messages if message.id in [int(ref) for ref in m.references if ref.isdigit()]]

        # Find parent message if this is a reply
        parent = None
        if message.references:
            for ref in message.references:
                if ref.isdigit() and int(ref) < message.id:
                    parent = next((m for m in all_messages if m.id == int(ref)), None)
                    if parent:
                        break

        # Create HTML
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{message.subject} - Yahoo Groups Archive</title>
            <link rel="stylesheet" href="../static/style.css">
        </head>
        <body>
            <header>
                <h1>Yahoo Groups Archive</h1>
                <nav>
                    <a href="../index.html">Back to Index</a>
                </nav>
            </header>
            
            <main>
                {parent_html}
                
                <article class="message">
                    <div class="message-header">
                        <h2 class="message-subject">{subject}</h2>
                        <div class="message-meta">
                            From: <strong>{sender_name}</strong> &lt;{sender_email}&gt; | 
                            Date: {date}
                        </div>
                    </div>
                    
                    <div class="message-content">
                        {content}
                    </div>
                </article>
                
                {replies_html}
            </main>
            
            <footer>
                <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
            </footer>
            
            <script src="../static/script.js"></script>
        </body>
        </html>
        """.format(
            message=message,
            subject=self._escape_html(message.subject),
            sender_name=self._escape_html(message.sender_name),
            sender_email=self._escape_html(message.sender_email),
            date=message.date.strftime('%Y-%m-%d %H:%M:%S %Z'),
            content=message.html_content,
            parent_html=self._generate_parent_html(parent) if parent else '',
            replies_html=self._generate_replies_html(replies) if replies else ''
        )

        # Write to file
        output_file = self.messages_dir / f"{message.id}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_parent_html(self, parent: Message) -> str:
        """Generate HTML for a parent message link."""
        return f"""
        <div class="parent-message">
            <p>In reply to: <a href="{parent.url}">{self._escape_html(parent.subject)}</a> from {self._escape_html(parent.sender_name)}</p>
        </div>
        """

    def _generate_replies_html(self, replies: List[Message]) -> str:
        """Generate HTML for replies to a message."""
        if not replies:
            return ''

        html = '<div class="replies">\n'
        html += '<h3>Replies ({})</h3>\n'.format(len(replies))
        html += '<ul class="reply-list">\n'
        for reply in sorted(replies, key=lambda x: x.date):
            html += f'<li><a href="{reply.url}">{self._escape_html(reply.subject)}</a> - {self._escape_html(reply.sender_name)}</li>\n'
        html += '</ul>\n</div>\n'
        return html

    def _generate_index_page(self, messages: List[Message]) -> None:
        """Generate the main index page with all messages."""
        # Sort messages by date, newest first
        messages_sorted = sorted(messages, key=lambda x: x.date, reverse=True)

        # Group messages by month for better organization
        messages_by_month = {}
        for msg in messages_sorted:
            month_year = msg.date.strftime('%B %Y')
            if month_year not in messages_by_month:
                messages_by_month[month_year] = []
            messages_by_month[month_year].append(msg)

        # Generate HTML for each month
        months_html = ''
        for month_year, month_messages in messages_by_month.items():
            months_html += f'<h2>{month_year}</h2>\n'
            for msg in month_messages:
                months_html += f"""
                <div class="message-preview">
                    <h3><a href="{msg.url}">{self._escape_html(msg.subject)}</a></h3>
                    <div class="message-meta">
                        From: <strong>{self._escape_html(msg.sender_name)}</strong> | 
                        Date: {msg.date.strftime('%Y-%m-%d %H:%M:%S %Z')}
                    </div>
                    <div class="message-snippet">
                        {self._get_snippet(msg.html_content, 200)}
                    </div>
                </div>
                """

        # Create the complete HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Yahoo Groups Archive</title>
            <link rel="stylesheet" href="static/style.css">
        </head>
        <body>
            <header>
                <h1>Yahoo Groups Archive</h1>
                <div class="search-container">
                    <input type="text" id="search-input" placeholder="Search messages...">
                    <div id="search-results" style="display: none;"></div>
                </div>
            </header>
            
            <main>
                <p>Total messages: {len(messages)}</p>
                
                {months_html}
                
                <div class="pagination">
                    <!-- Add pagination if needed -->
                </div>
            </main>
            
            <footer>
                <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
            </footer>
            
            <script src="static/script.js"></script>
        </body>
        </html>
        """

        # Write to file
        with open(self.output_dir / 'index.html', 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_search_index(self, messages: List[Message]) -> None:
        """Generate a search index JSON file for client-side searching."""
        search_data = {
            'messages': []
        }

        for msg in messages:
            # Extract text content from HTML for searching
            soup = BeautifulSoup(msg.html_content, 'lxml')
            text_content = soup.get_text()

            search_data['messages'].append({
                'id': msg.id,
                'subject': msg.subject,
                'sender_name': msg.sender_name,
                'sender_email': msg.sender_email,
                'date': msg.date.isoformat(),
                'url': f'messages/{msg.id}.html',
                'content': text_content
            })

        # Write search index
        with open(self.search_dir / 'search_index.json', 'w', encoding='utf-8') as f:
            json.dump(search_data, f, indent=2)

        # Write search results page
        with open(self.search_dir / 'search.html', 'w', encoding='utf-8') as f:
            f.write(constants.SEARCH_HTML_TEMPLATE)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ''
        return (
            str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;')
        )

    @staticmethod
    def _get_snippet(html: str, max_length: int = 200) -> str:
        """Get a text snippet from HTML content."""
        if not html:
            return ''

        # Remove HTML tags and decode HTML entities
        soup = BeautifulSoup(html, 'lxml')
        text = soup.get_text()

        # Truncate and add ellipsis if needed
        if len(text) > max_length:
            return text[:max_length].rsplit(' ', 1)[0] + '...'
        return text
