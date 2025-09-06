#!/usr/bin/env python3
"""
Yahoo Groups Mbox to Static Website Converter

This script converts an mbox file containing Yahoo Groups messages into a static website.
"""

import os
import sys
import re
import json
import email
import mailbox
import argparse
import shutil
from datetime import datetime
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr, parsedate_to_datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup
from dateutil import tz

# Template environment setup
env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    autoescape=select_autoescape(['html', 'xml'])
)

class Message:
    """Represents an email message with its metadata and content."""

    def __init__(self, msg_id: int, msg: email.message.Message):
        self.id = msg_id
        self.subject = self._get_header(msg, 'Subject', '(No subject)')
        self.sender_name, self.sender_email = parseaddr(msg['From'])
        self.date = self._parse_date(msg)
        self.references = self._get_references(msg)
        self.html_content = self._extract_content(msg)
        self.url = f'messages/{self.id}.html'

    @staticmethod
    def _get_header(msg: email.message.Message, header: str, default: str = '') -> str:
        """Safely get a header from the email message."""
        value = msg.get(header, '')
        if not value:
            return default
        return str(value)

    def _parse_date(self, msg: email.message.Message) -> datetime:
        """Parse the date from the email message and ensure it's timezone-aware."""
        date_str = self._get_header(msg, 'Date')
        if not date_str:
            return datetime.now(tz=tz.UTC)
        try:
            dt = parsedate_to_datetime(date_str)
            # If the datetime is naive, make it timezone-aware with UTC
            if dt.tzinfo is None:
                return dt.replace(tzinfo=tz.UTC)
            return dt
        except (TypeError, ValueError):
            return datetime.now(tz=tz.UTC)

    def _get_references(self, msg: email.message.Message) -> List[str]:
        """Extract message references for threading."""
        refs = []
        if 'References' in msg:
            refs.extend(msg['References'].replace('\n', '').split())
        if 'In-Reply-To' in msg:
            refs.append(msg['In-Reply-To'])
        return [ref.strip('<>') for ref in refs if ref.strip()]

    def _extract_content(self, msg: email.message.Message) -> str:
        """Extract and process the message content."""
        # Try to get HTML content first
        html_part = None
        text_part = None

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/html' and not html_part:
                    html_part = part.get_payload(decode=True).decode('utf-8', 'ignore')
                elif content_type == 'text/plain' and not text_part:
                    text_part = part.get_payload(decode=True).decode('utf-8', 'ignore')
        else:
            content_type = msg.get_content_type()
            payload = msg.get_payload(decode=True)
            if payload:
                if content_type == 'text/html':
                    html_part = payload.decode('utf-8', 'ignore')
                elif content_type == 'text/plain':
                    text_part = payload.decode('utf-8', 'ignore')

        # Return HTML if available, otherwise convert text to HTML
        if html_part:
            # Clean up HTML
            soup = BeautifulSoup(html_part, 'lxml')
            # Remove potentially harmful elements
            for element in soup(['script', 'iframe', 'object', 'embed']):
                element.decompose()
            return str(soup)
        elif text_part:
            # Convert plain text to HTML, preserving line breaks
            text_part = text_part.replace('\n', '<br>\n')
            return f'<div class="plaintext-content">{text_part}</div>'
        return '<p>No content available</p>'


def process_mbox(mbox_path: str) -> List[Message]:
    """Process an mbox file and return a list of Message objects."""
    messages = []
    msg_id = 1

    if not os.path.exists(mbox_path):
        print(f"Error: File not found: {mbox_path}")
        sys.exit(1)

    try:
        mbox = mailbox.mbox(mbox_path)
        for msg in mbox:
            try:
                messages.append(Message(msg_id, msg))
                msg_id += 1
            except Exception as e:
                print(f"Error processing message {msg_id}: {str(e)}")
                continue
    except Exception as e:
        print(f"Error reading mbox file: {str(e)}")
        sys.exit(1)

    return messages

def generate_site(messages: List[Message], output_dir: str):
    """Generate the static website from the processed messages."""
    # Create output directories
    output_path = Path(output_dir)
    messages_dir = output_path / 'messages'
    static_dir = output_path / 'static'

    for directory in [output_path, messages_dir, static_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    # Copy static files
    copy_static_files(static_dir)

    # Generate individual message pages
    for message in messages:
        generate_message_page(message, messages_dir, messages)

    # Generate index page
    generate_index_page(messages, output_path)

    # Generate search index
    generate_search_index(messages, output_path)

def copy_static_files(static_dir: Path):
    """Copy static files (CSS, JS) to the output directory."""
    # Create CSS file
    css_content = """
    /* Basic styling for the archive */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 1000px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .message {
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 16px;
        margin-bottom: 16px;
        background-color: #fff;
    }
    
    .message-header {
        border-bottom: 1px solid #e1e4e8;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }
    
    .message-subject {
        font-size: 1.2em;
        font-weight: 600;
        margin: 0 0 8px 0;
    }
    
    .message-meta {
        color: #6a737d;
        font-size: 0.9em;
    }
    
    .message-content {
        line-height: 1.6;
    }
    
    .message-content img {
        max-width: 100%;
        height: auto;
    }
    
    .plaintext-content {
        white-space: pre-wrap;
        font-family: monospace;
    }
    
    a {
        color: #0366d6;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    /* Navigation */
    .pagination {
        margin: 20px 0;
        text-align: center;
    }
    
    .pagination a, .pagination span {
        padding: 8px 16px;
        margin: 0 4px;
        border: 1px solid #e1e4e8;
        border-radius: 3px;
        display: inline-block;
    }
    
    .pagination a:hover {
        background-color: #f6f8fa;
    }
    
    /* Search */
    .search-container {
        margin: 20px 0;
        text-align: center;
    }
    
    #search-input {
        padding: 8px 12px;
        width: 300px;
        max-width: 100%;
        border: 1px solid #e1e4e8;
        border-radius: 4px;
        font-size: 16px;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        body {
            padding: 10px;
        }
        
        .message {
            padding: 12px;
        }
    }
    """

    with open(static_dir / 'style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)

    # Create JavaScript file for search functionality
    js_content = """
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('search-input');
        const searchResults = document.getElementById('search-results');
        
        if (searchInput && searchResults) {
            searchInput.addEventListener('input', function() {
                const query = this.value.toLowerCase();
                if (query.length < 2) {
                    searchResults.style.display = 'none';
                    return;
                }
                
                fetch(`search/search_index.json`)
                    .then(response => response.json())
                    .then(data => {
                        const results = data.messages.filter(message => 
                            message.subject.toLowerCase().includes(query) ||
                            message.sender_name.toLowerCase().includes(query) ||
                            message.content.toLowerCase().includes(query)
                        );
                        
                        displayResults(results);
                    })
                    .catch(error => {
                        console.error('Error loading search index:', error);
                    });
            });
        }
        
        function displayResults(results) {
            const searchResults = document.getElementById('search-results');
            
            if (results.length === 0) {
                searchResults.innerHTML = '<p>No results found.</p>';
                searchResults.style.display = 'block';
                return;
            }
            
            let html = '<div class="search-results">';
            html += `<p>Found ${results.length} result${results.length === 1 ? '' : 's'}:</p>`;
            
            results.forEach(result => {
                const date = new Date(result.date).toLocaleDateString();
                const excerpt = result.content.substring(0, 200) + 
                    (result.content.length > 200 ? '...' : '');
                
                html += `
                <div class="search-result">
                    <h3><a href="${result.url}">${result.subject}</a></h3>
                    <div class="search-meta">
                        From: ${result.sender_name} | Date: ${date}
                    </div>
                    <div class="search-excerpt">${excerpt}</div>
                </div>
                `;
            });
            
            html += '</div>';
            searchResults.innerHTML = html;
            searchResults.style.display = 'block';
        }
    });
    """

    with open(static_dir / 'script.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

def generate_message_page(message: Message, output_dir: Path, all_messages: List[Message]):
    """Generate an HTML page for a single message."""
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
    html = f"""
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
            {generate_parent_html(parent) if parent else ''}
            
            <article class="message">
                <div class="message-header">
                    <h2 class="message-subject">{escape_html(message.subject)}</h2>
                    <div class="message-meta">
                        From: <strong>{escape_html(message.sender_name)}</strong> &lt;{escape_html(message.sender_email)}&gt; | 
                        Date: {message.date.strftime('%Y-%m-%d %H:%M:%S %Z')}
                    </div>
                </div>
                
                <div class="message-content">
                    {message.html_content}
                </div>
            </article>
            
            {generate_replies_html(replies) if replies else ''}
        </main>
        
        <footer>
            <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
        </footer>
        
        <script src="../static/script.js"></script>
    </body>
    </html>
    """

    # Write to file
    output_file = output_dir / f"{message.id}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_parent_html(parent: 'Message') -> str:
    """Generate HTML for a parent message link."""
    return f"""
    <div class="parent-message">
        <p>In reply to: <a href="{parent.url}">{escape_html(parent.subject)}</a> from {escape_html(parent.sender_name)}</p>
    </div>
    """

def generate_replies_html(replies: List[Message]) -> str:
    """Generate HTML for replies to a message."""
    if not replies:
        return ''

    html = '<div class="replies">\n'
    html += '<h3>Replies ({})</h3>\n'.format(len(replies))
    html += '<ul class="reply-list">\n'
    for reply in sorted(replies, key=lambda x: x.date):
        html += f'<li><a href="{reply.url}">{escape_html(reply.subject)}</a> - {escape_html(reply.sender_name)}</li>\n'
    html += '</ul>\n</div>\n'
    return html

def generate_index_page(messages: List[Message], output_dir: Path):
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
                <h3><a href="{msg.url}">{escape_html(msg.subject)}</a></h3>
                <div class="message-meta">
                    From: <strong>{escape_html(msg.sender_name)}</strong> | 
                    Date: {msg.date.strftime('%Y-%m-%d %H:%M:%S %Z')}
                </div>
                <div class="message-snippet">
                    {get_snippet(msg.html_content, 200)}
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
        <title>{messages[0].subject} - Yahoo Groups Archive</title>
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
    with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)

def generate_search_index(messages: List[Message], output_dir: Path):
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

    # Create search directory if it doesn't exist
    search_dir = output_dir / 'search'
    search_dir.mkdir(exist_ok=True)

    # Write search index
    with open(search_dir / 'search_index.json', 'w', encoding='utf-8') as f:
        json.dump(search_data, f, indent=2)

    # Create search results page
    search_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results - Yahoo Groups Archive</title>
        <link rel="stylesheet" href="../static/style.css">
    </head>
    <body>
        <header>
            <h1>Search Results</h1>
            <nav>
                <a href="../index.html">Back to Archive</a>
            </nav>
        </header>
        
        <main>
            <div class="search-container">
                <input type="text" id="search-input" placeholder="Search messages...">
                <div id="search-results"></div>
            </div>
        </main>
        
        <footer>
            <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
        </footer>
        
        <script src="../static/script.js"></script>
    </body>
    </html>
    """

    with open(search_dir / 'search.html', 'w', encoding='utf-8') as f:
        f.write(search_html)

def escape_html(text: str) -> str:
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

def get_snippet(html: str, max_length: int = 200) -> str:
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

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert an mbox file to a static website.')
    parser.add_argument('mbox_file', help='Path to the mbox file to process')
    parser.add_argument('output_dir', nargs='?', default='output',
                       help='Output directory for the generated website (default: output)')

    args = parser.parse_args()

    print(f"Processing mbox file: {args.mbox_file}")
    print("This may take a while for large files...")

    # Process the mbox file
    messages = process_mbox(args.mbox_file)

    if not messages:
        print("No messages found in the mbox file.")
        sys.exit(1)

    print(f"Processed {len(messages)} messages.")
    print(f"Generating static website in: {args.output_dir}")

    # Generate the static website
    generate_site(messages, args.output_dir)

    print(f"\nDone! The static website has been generated in the '{args.output_dir}' directory.")
    print(f"Open '{args.output_dir}/index.html' in your web browser to view the archive.")

if __name__ == '__main__':
    main()
