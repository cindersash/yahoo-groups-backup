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
from .base_message import BaseMessage
from .utils import slugify


class SiteGenerator:
    """Handles the generation of static website files from message data."""

    def __init__(self, output_dir: str, forum_name: str):
        """Initialize the SiteGenerator with output directory and template environment.

        Args:
            output_dir: Base directory where the forum archive will be created
            forum_name: Name of the forum (used in page titles and subdirectory name)
        """
        # Create a filesystem-safe version of the forum name for the subdirectory
        safe_forum_name = slugify(forum_name)

        # Set up directory structure with forum subdirectory
        self.output_dir = Path(output_dir) / safe_forum_name
        self.forum_name = forum_name
        self.messages_dir = self.output_dir / "messages"
        self.static_dir = self.output_dir / "static"
        self.search_dir = self.output_dir / "search"

        # Store the base output dir for reference
        self.base_output_dir = Path(output_dir)

        # Create output directories
        for directory in [self.output_dir, self.messages_dir, self.static_dir, self.search_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Set up template environment
        self.env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"), autoescape=select_autoescape(["html", "xml"])
        )

    def generate_site(self, threads: dict[str, List[BaseMessage]]) -> None:
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
                print(
                    f"  Processed {i}/{len(threads)} threads "
                    f"({processed_messages}/{total_messages} messages) - {rate:.1f} msg/sec"
                )

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
        with open(self.static_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(constants.CSS_STYLES)

        # Write JavaScript file
        with open(self.static_dir / "script.js", "w", encoding="utf-8") as f:
            f.write(constants.JAVASCRIPT_CODE)

    @staticmethod
    def _clean_html_content(html: str) -> str:
        """Clean up HTML content to ensure consistent styling."""
        if not html:
            return ""
            
        # Parse the HTML with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove any inline styles and classes
        for tag in soup.find_all(True):
            # Remove style attributes
            if 'style' in tag.attrs:
                del tag.attrs['style']
                
            # Remove class attributes from most elements (keep our utility classes)
            if 'class' in tag.attrs and tag.name not in ['div', 'span']:
                del tag.attrs['class']
                
            # Remove font tags
            if tag.name == 'font':
                tag.unwrap()
                
        # Convert back to string
        return str(soup)

    def _generate_thread_page(self, thread: List[BaseMessage], thread_id: int) -> None:
        """Generate an HTML page for a single thread."""
        if not thread:
            return

        # Sort messages in thread by date (oldest first)
        thread.sort(key=lambda x: x.date)

        # Generate HTML for each message in the thread
        messages_html = ""
        for i, message in enumerate(thread, 1):
            # Get the already cleaned HTML content
            cleaned_content = message.html_content
            
            # Format the message date
            message_date = message.date.strftime('%Y-%m-%d %H:%M:%S %Z') if message.date else 'Unknown date'
            
            # Format the sender info
            sender_str = self._get_sender_str(message)
            
            messages_html += f"""
            <div class="message {'first-message' if i == 1 else 'reply-message'}">
                <div class="message-header">
                    <h3 class="message-subject">{self._escape_html(message.subject)}</h3>
                    <div class="message-meta">
                        From: <strong>{sender_str}</strong> | 
                        Date: {message_date}
                    </div>
                </div>
                <div class="message-content">
                    {cleaned_content}
                </div>
            </div>
            """

        # Create the complete HTML
        thread_subject = thread[0].normalized_subject or "No subject"
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self._escape_html(thread_subject)} - Thread - {self.forum_name} Archive</title>
            <link rel="stylesheet" href="../static/style.css">
        </head>
        <body>
            <header>
                <h1>{self.forum_name} - Yahoo Groups Archive</h1>
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
        safe_subject = "".join(c if c.isalnum() or c in " -_" else "_" for c in thread_subject)
        safe_subject = safe_subject[:50]  # Limit length
        filename = f"thread_{thread_id}_{safe_subject}.html"

        # Write to file
        output_file = self.messages_dir / filename
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        # Update the URL for all messages in this thread
        for msg in thread:
            msg.url = f"messages/{filename}"

    @staticmethod
    def _get_sender_str(message: BaseMessage) -> str:
        sender_str = ""

        if message.sender_name.strip():
            sender_str += message.sender_name.strip()
        if message.sender_email.strip():
            sender_str += " (" + message.sender_email.strip() + ")"

        if not sender_str:
            sender_str = "Unknown"

        return sender_str

    def _generate_index_page(
        self, threads: dict[str, List[BaseMessage]], page: int = 1, threads_per_page: int = 25
    ) -> None:
        """
        Generate the main index page with paginated threads.

        Args:
            threads: Dictionary where keys are thread names and values are lists of messages
            page: Current page number (1-based)
            threads_per_page: Number of threads to display per page
        """
        # Convert threads to a list and sort by most recent message date
        sorted_threads = sorted(
            threads.items(), key=lambda x: x[1][-1].date if x[1] and x[1][-1].date else datetime.min, reverse=True
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

            month_year = last_message.date.strftime("%B %Y")
            if month_year not in threads_by_month:
                threads_by_month[month_year] = []
            threads_by_month[month_year].append((thread_name, messages))

        # Generate HTML for each month
        months_html = ""
        for month_year, month_threads in threads_by_month.items():
            months_html += f"<h2>{month_year}</h2>\n"
            for thread_name, messages in month_threads:
                if not messages:
                    continue

                first_msg = messages[0]
                last_msg = messages[-1]
                started_by_str = self._get_sender_str(first_msg)

                months_html += f"""
                <div class="thread-preview">
                    <h3><a href="{first_msg.url}">{self._escape_html(thread_name)}</a></h3>
                    <div class="thread-meta">
                        Started by <strong>{started_by_str}</strong> | 
                        {len(messages)} message{'s' if len(messages) != 1 else ''} | 
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
            <title>{self.forum_name} Archive - Page {page}</title>
            <link rel="stylesheet" href="static/style.css">
        </head>
        <body>
            <header>
                <h1>{self.forum_name} - Yahoo Groups Archive</h1>
                <div class="search-container">
                    <form action="search/" method="get" class="search-form">
                        <input type="text" name="q" id="search-input" placeholder="Search messages..." required>
                        <button type="submit" id="search-button">Search</button>
                    </form>
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
            output_file = self.output_dir / "index.html"
        else:
            output_file = self.output_dir / f"index{page}.html"

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

    def _generate_search_index(self, threads: dict[str, List[BaseMessage]]) -> None:
        """
        Generate a search index JSON file and search page.

        Args:
            threads: Dictionary where keys are thread names and values are lists of messages
        """
        search_data = []

        # Add thread information to search index
        for thread_idx, (thread_name, messages) in enumerate(threads.items()):
            if not messages:
                continue

            first_msg = messages[0]

            # Get unique authors in the thread
            authors = list({msg.sender_name for msg in messages if msg.sender_name})

            # Add simplified thread information with dates
            # Make URL relative to the search directory
            search_data.append(
                {
                    "id": thread_idx,
                    "url": f"../{first_msg.url}",  # Add ../ to go up from search/ to root
                    "title": thread_name,
                    "authors": authors,
                    "message_count": len(messages),
                    "start_date": messages[0].date.isoformat() if messages[0].date else "",
                    "last_date": messages[-1].date.isoformat() if messages[-1].date else "",
                }
            )

        # Ensure search directory exists
        self.search_dir.mkdir(parents=True, exist_ok=True)

        # Write search index to file
        search_file = self.search_dir / "search_index.json"
        with open(search_file, "w", encoding="utf-8") as f:
            json.dump(search_data, f, ensure_ascii=False, indent=2)

        # Write search page
        search_page = self.search_dir / "index.html"
        with open(search_page, "w", encoding="utf-8") as f:
            f.write(constants.SEARCH_PAGE_TEMPLATE)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        if not text:
            return ""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    @staticmethod
    def _generate_pagination_html(current_page: int, total_pages: int) -> str:
        """
        Generate HTML for pagination controls.

        Args:
            current_page: Current page number (1-based)
            total_pages: Total number of pages

        Returns:
            HTML string with pagination controls
        """
        if total_pages <= 1:
            return ""

        pagination = ['<div class="pagination-controls">']

        # Previous button
        if current_page > 1:
            prev_page = "index.html" if current_page == 2 else f"index{current_page - 1}.html"
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
                page_url = f"index{p}.html" if p > 1 else "index.html"
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

        pagination.append("</div>")
        return "\n".join(pagination)

    @staticmethod
    def _get_snippet(html: str, max_length: int = 200) -> str:
        """Get a text snippet from HTML content."""
        if not html:
            return ""

        # Remove HTML tags and decode HTML entities
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text()

        # Truncate and add ellipsis if needed
        if len(text) > max_length:
            return text[:max_length].rsplit(" ", 1)[0] + "..."
        return text
