#!/usr/bin/env python3
"""
Yahoo Groups Mbox to Static Website Converter

This script converts mbox file containing Yahoo Groups messages into a static website.
"""

import argparse
import mailbox
import os
import sys
import time
from datetime import datetime
from typing import List

from .generator import SiteGenerator
from .message import Message


def _is_valid_message(message: Message) -> bool:
    # The first messages should be from 1998. Anything earlier is probably corrupted.
    if message.date:
        # Make the comparison timezone-aware by localizing the cutoff date to the message timezone
        cutoff_date = datetime(1998, 1, 1, tzinfo=message.date.tzinfo)
        if message.date < cutoff_date:
            return False

    return bool(message.html_content and message.date)


def process_mbox(mbox_path: str) -> dict[str, List[Message]]:
    """
    Process mbox file and return a dictionary where keys are thread names
    and values are lists of Message objects in that thread, sorted by date.
    """
    threads = {}
    msg_id = 1
    processed_count = 0
    start_time = time.time()

    if not os.path.exists(mbox_path):
        print(f"Error: File not found: {mbox_path}")
        sys.exit(1)

    print("Processing mbox file (this may take a while)...")

    try:
        # Open the mbox file in binary mode and handle encoding at the message level
        mbox = mailbox.mbox(mbox_path, create=False)

        # Set the default encoding for the mailbox
        mbox._factory = lambda f, msg=None: mailbox.mboxMessage(f) if msg is None else mailbox.mboxMessage(msg)

        invalid_messages = 0
        total_messages = len(mbox)
        print(f"Found {total_messages} messages to process")

        for msg in mbox:
            try:
                message = Message(msg_id, msg)

                if _is_valid_message(message):
                    thread_key = message.normalized_subject or "(No subject)"
                    if thread_key not in threads:
                        threads[thread_key] = []
                    threads[thread_key].append(message)

                    msg_id += 1
                else:
                    invalid_messages += 1

                processed_count += 1

                # Show progress every 100 messages
                if processed_count % 100 == 0 or processed_count == total_messages:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    print(
                        f"  Processed {processed_count}/{total_messages} messages "
                        f"({processed_count/total_messages:.1%}) - {rate:.1f} msg/sec"
                    )

            except Exception as e:
                print(f"Error processing message {msg_id}: {str(e)}")
                continue

        # Remove empty threads (if any)
        threads = {k: v for k, v in threads.items() if v}

    except Exception as e:
        print(f"Error processing mbox file: {str(e)}")
        sys.exit(1)

    total_messages = sum(len(msgs) for msgs in threads.values())
    print(f"\nSuccessfully processed {total_messages} valid messages in {len(threads)} threads")
    print(f"Skipped {invalid_messages} invalid messages")
    return threads


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Convert Yahoo Groups mbox to static website.")
    parser.add_argument("mbox_file", help="Path to the mbox file")
    parser.add_argument("--forum-name", required=True, help="Name of the forum (used in page titles)")
    parser.add_argument("-o", "--output", default="output", help="Output directory (default: output)")

    args = parser.parse_args()

    # Process mbox file
    threads = process_mbox(args.mbox_file)

    if not threads:
        print("No valid messages found in the mbox file.")
        sys.exit(1)

    total_messages = sum(len(messages) for messages in threads.values())
    print(f"Processed {total_messages} messages in {len(threads)} threads.")
    print(f"Generating static website in: {args.output}")

    # Generate the static website using SiteGenerator
    generator = SiteGenerator(args.output, args.forum_name)
    generator.generate_site(threads)

    print(f"\nDone! The static website has been generated in the '{args.output}' directory.")
    print(f"Open '{args.output}/index.html' in your web browser to view the archive.")


if __name__ == "__main__":
    main()
