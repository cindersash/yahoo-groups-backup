"""
HTML generation utilities for the Yahoo Groups Mbox to Static Website Converter.
"""
import json
import time
from datetime import datetime
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

    def generate_site(self, threads: dict[str, List[Message]]) -> None:
        """
        Generate the complete static website with thread-based pages.
        
        Args:
            threads: Dictionary where keys are thread names and values are lists of messages
        """
        print("\nGenerating static website...")
        start_time = time.time()

        # Flatten messages list for compatibility with existing code
        all_messages = [msg for thread_msgs in threads.values() for msg in thread_msgs]
        total_messages = len(all_messages)

        # Copy static files
        print("Copying static files...")
        self._copy_static_files()

        # Generate thread pages
        print(f"Generating {len(threads)} thread pages...")
        generated_count = 0
        processed_messages = 0

        for i, (thread_name, messages) in enumerate(threads.items(), 1):
            self._generate_thread_page(messages, i)
            processed_messages += len(messages)
            generated_count += 1

            # Show progress every 10 threads
            if i % 10 == 0 or i == len(threads):
                elapsed = time.time() - start_time
                rate = processed_messages / elapsed if elapsed > 0 else 0
                print(f"  Processed {i}/{len(threads)} threads "
                      f"({processed_messages}/{total_messages} messages) - {rate:.1f} msg/sec")

        # Generate paginated index pages
        print("\nGenerating index pages...")
        total_threads = len(threads)
        threads_per_page = 25
        total_pages = (total_threads + threads_per_page - 1) // threads_per_page

        for page in range(1, total_pages + 1):
            self._generate_index_page(threads, page, threads_per_page)
            if page == 1:
                print(f"  Generated index.html (page 1 of {total_pages})")
            else:
                print(f"  Generated index{page}.html (page {page} of {total_pages})")

        # Generate search index
        print("Generating search index...")
        self._generate_search_index(threads)

        elapsed = time.time() - start_time
        print(f"\nWebsite generation completed in {elapsed:.1f} seconds")
        print(f"Total pages generated: {generated_count} thread pages + index + search")

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

    def _generate_thread_page(self, thread: List[Message], thread_id: int) -> None:
        """Generate an HTML page for a single thread."""
        if not thread:
            return

        # Sort messages in thread by date (oldest first)
        thread.sort(key=lambda x: x.date)

        # Generate HTML for each message in the thread
        messages_html = ''
        for i, message in enumerate(thread, 1):
            messages_html += f"""
            <div class="message {'first-message' if i == 1 else 'reply-message'}">
                <div class="message-header">
                    <h3 class="message-subject">{self._escape_html(message.subject)}</h3>
                    <div class="message-meta">
                        From: <strong>{self._escape_html(message.sender_name)}</strong> &lt;{self._escape_html(message.sender_email)}&gt; | 
                        Date: {message.date.strftime('%Y-%m-%d %H:%M:%S %Z')}
                    </div>
                </div>
                <div class="message-content">
                    {message.html_content}
                </div>
            </div>
            """

        # Create the complete HTML
        thread_subject = thread[0].normalized_subject or 'No subject'
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self._escape_html(thread_subject)} - Thread - Yahoo Groups Archive</title>
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
                <h1 class="thread-title">{self._escape_html(thread_subject)}</h1>
                <div class="thread-meta">
                    {len(thread)} messages in this thread | 
                    Started on {thread[0].date.strftime('%Y-%m-%d')}
                </div>
                
                <div class="thread-messages">
                    {messages_html}
                </div>
            </main>
            
            <footer>
                <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
            </footer>
            
            <script src="../static/script.js"></script>
        </body>
        </html>
        """

        # Create a URL-friendly filename for the thread
        safe_subject = ''.join(c if c.isalnum() or c in ' -_' else '_' for c in thread_subject)
        safe_subject = safe_subject[:50]  # Limit length
        filename = f"thread_{thread_id}_{safe_subject}.html"

        # Write to file
        output_file = self.messages_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        # Update the URL for all messages in this thread
        for msg in thread:
            msg.url = f'messages/{filename}'

    def _generate_index_page(self, threads: dict[str, List[Message]], page: int = 1,
                             threads_per_page: int = 25) -> None:
        """
        Generate the main index page with paginated threads.
        
        Args:
            threads: Dictionary where keys are thread names and values are lists of messages
            page: Current page number (1-based)
            threads_per_page: Number of threads to display per page
        """
        # Convert threads to a list and sort by most recent message date
        sorted_threads = sorted(
            threads.items(),
            key=lambda x: x[1][-1].date if x[1] and x[1][-1].date else datetime.min,
            reverse=True
        )

        # Calculate pagination
        total_threads = len(sorted_threads)
        total_pages = (total_threads + threads_per_page - 1) // threads_per_page
        page = max(1, min(page, total_pages))  # Ensure page is within valid range
        start_idx = (page - 1) * threads_per_page
        end_idx = min(start_idx + threads_per_page, total_threads)

        # Get threads for current page
        page_threads = sorted_threads[start_idx:end_idx]

        # Group threads by month for better organization
        threads_by_month = {}
        for thread_name, messages in page_threads:
            if not messages:
                continue

            # Get the most recent message date for sorting
            last_message = messages[-1]
            if not last_message.date:
                continue

            month_year = last_message.date.strftime('%B %Y')
            if month_year not in threads_by_month:
                threads_by_month[month_year] = []
            threads_by_month[month_year].append((thread_name, messages))

        # Generate HTML for each month
        months_html = ''
        for month_year, month_threads in threads_by_month.items():
            months_html += f'<h2>{month_year}</h2>\n'
            for thread_name, messages in month_threads:
                if not messages:
                    continue

                first_msg = messages[0]
                last_msg = messages[-1]
                reply_count = len(messages) - 1

                months_html += f"""
                <div class="thread-preview">
                    <h3><a href="{first_msg.url}">{self._escape_html(thread_name)}</a></h3>
                    <div class="thread-meta">
                        Started by <strong>{self._escape_html(first_msg.sender_name or first_msg.sender_email or 'Unknown')}</strong> | 
                        {len(messages)} message{'s' if len(messages) != 1 else ''} | 
                        {reply_count} repl{'y' if reply_count == 1 else 'ies' if reply_count > 1 else 'ies'} |
                        Last reply: {last_msg.date.strftime('%Y-%m-%d') if last_msg.date else 'Unknown date'}
                    </div>
                    <div class="message-snippet">
                        {self._get_snippet(first_msg.html_content, 200) if first_msg.html_content else ''}
                    </div>
                </div>
                """

        total_messages = sum(len(lst) for lst in threads.values())

        # Generate pagination HTML
        pagination_html = self._generate_pagination_html(page, total_pages)

        # Create the complete HTML
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Yahoo Groups Archive - Page {page}</title>
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
                <p>Total messages: {total_messages} in {total_threads} threads (page {page} of {total_pages})</p>
                
                {months_html}
                
                <div class="pagination">
                    {pagination_html}
                </div>
            </main>
            
            <footer>
                <p>Generated by Yahoo Groups Mbox to Static Website Converter</p>
            </footer>
            
            <script src="static/script.js"></script>
        </body>
        </html>
        """

        # Determine the output filename
        if page == 1:
            output_file = self.output_dir / 'index.html'
        else:
            output_file = self.output_dir / f'index{page}.html'

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

    def _generate_search_index(self, threads: dict[str, List[Message]]) -> None:
        """
        Generate a search index JSON file.
        
        Args:
            threads: Dictionary where keys are thread names and values are lists of messages
        """
        search_data = {
            'messages': [],
            'threads': []
        }

        # Add messages and threads to search index
        for thread_idx, (thread_name, messages) in enumerate(threads.items()):
            if not messages:
                continue

            first_msg = messages[0]
            last_msg = messages[-1]

            # Add thread information
            search_data['threads'].append({
                'id': thread_idx,
                'url': first_msg.url,
                'title': thread_name,
                'message_count': len(messages),
                'start_date': first_msg.date.isoformat() if first_msg.date else '',
                'last_activity': last_msg.date.isoformat() if last_msg.date else '',
                'authors': list({msg.sender_name for msg in messages if msg.sender_name})
            })

            # Add messages in this thread
            for msg in messages:
                if not msg.html_content:
                    continue

                # Extract text from HTML content for search
                soup = BeautifulSoup(msg.html_content, 'html.parser')
                text_content = soup.get_text(' ', strip=True)

                search_data['messages'].append({
                    'id': str(msg.id),
                    'thread_id': thread_idx,
                    'url': f"{msg.url}#msg-{msg.id}",
                    'title': thread_name,
                    'content': text_content,
                    'author': msg.sender_name or 'Unknown',
                    'date': msg.date.isoformat() if msg.date else '',
                    'is_thread_start': msg == first_msg
                })

        # Write search index to file
        search_file = self.search_dir / 'search_index.json'
        with open(search_file, 'w', encoding='utf-8') as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)

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

    def _generate_pagination_html(self, current_page: int, total_pages: int) -> str:
        """
        Generate HTML for pagination controls.
        
        Args:
            current_page: Current page number (1-based)
            total_pages: Total number of pages
            
        Returns:
            HTML string with pagination controls
        """
        if total_pages <= 1:
            return ''

        pagination = ['<div class="pagination-controls">']

        # Previous button
        if current_page > 1:
            prev_page = 'index.html' if current_page == 2 else f'index{current_page - 1}.html'
            pagination.append(f'<a href="{prev_page}" class="page-link">&laquo; Previous</a>')
        else:
            pagination.append('<span class="page-link disabled">&laquo; Previous</span>')

        # Page numbers
        max_pages_to_show = 5
        half_window = max_pages_to_show // 2

        start_page = max(1, current_page - half_window)
        end_page = min(total_pages, start_page + max_pages_to_show - 1)

        # Adjust if we're near the end
        if end_page - start_page + 1 < max_pages_to_show:
            start_page = max(1, end_page - max_pages_to_show + 1)

        # First page and ellipsis if needed
        if start_page > 1:
            pagination.append('<a href="index.html" class="page-link">1</a>')
            if start_page > 2:
                pagination.append('<span class="ellipsis">...</span>')

        # Page numbers in current window
        for p in range(start_page, end_page + 1):
            if p == current_page:
                pagination.append(f'<span class="page-link current">{p}</span>')
            else:
                page_url = f'index{p}.html' if p > 1 else 'index.html'
                pagination.append(f'<a href="{page_url}" class="page-link">{p}</a>')

        # Last page and ellipsis if needed
        if end_page < total_pages:
            if end_page < total_pages - 1:
                pagination.append('<span class="ellipsis">...</span>')
            pagination.append(f'<a href="index{total_pages}.html" class="page-link">{total_pages}</a>')

        # Next button
        if current_page < total_pages:
            pagination.append(f'<a href="index{current_page + 1}.html" class="page-link">Next &raquo;</a>')
        else:
            pagination.append('<span class="page-link disabled">Next &raquo;</span>')

        pagination.append('</div>')
        return '\n'.join(pagination)

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
