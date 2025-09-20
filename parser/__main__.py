#!/usr/bin/env python3
"""
Yahoo Groups to Static Website Converter

This script converts Yahoo Groups messages (from mbox or JSON) into a static website.
"""

import argparse
import mailbox
import os
import sys
import time
from typing import List, Dict

from .base_message import BaseMessage
from .generator import SiteGenerator
from .json_processor import process_json_directory
from .message import MboxMessage


def process_mbox(mbox_path: str) -> Dict[str, List[BaseMessage]]:
    """
    Process mbox file and return a dictionary where keys are thread names
    and values are lists of Message objects in that thread, sorted by date.
    """
    threads: Dict[str, List[BaseMessage]] = {}
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

        for message in mbox:
            try:
                msg = MboxMessage(msg_id, message)
                if _is_valid_message(msg):
                    if msg.normalized_subject not in threads:
                        threads[msg.normalized_subject] = []
                    threads[msg.normalized_subject].append(msg)
                    processed_count += 1
                else:
                    invalid_messages += 1

                msg_id += 1

                processed_count += 1

                # Show progress every 100 messages
                if processed_count % 100 == 0 or processed_count == total_messages:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    print(
                        f"  Processed {processed_count}/{total_messages} messages "
                        f"({processed_count / total_messages:.1%}) - {rate:.1f} msg/sec"
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
    parser = argparse.ArgumentParser(description='Convert Yahoo Groups data to static website')

    # Create a mutually exclusive group for input types
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--mbox', help='Path to the mbox file')
    input_group.add_argument('--json-dir', help='Path to directory containing JSON files')

    parser.add_argument('-o', '--output', default='output',
                        help='Output directory (default: output)')
    parser.add_argument("--forum-name", required=True, help="Name of the forum (used in page titles)")
    args = parser.parse_args()

    # Process the input based on type
    if args.mbox:
        threads = process_mbox(args.mbox)
    elif args.json_dir:
        threads = process_json_directory(args.json_dir)
    else:
        parser.error('Either --mbox or --json-dir must be specified')

    # Generate the static website using SiteGenerator
    generator = SiteGenerator(args.output, args.forum_name)
    generator.generate_site(threads)

    print(f"\nDone! The static website has been generated in the '{args.output}' directory.")
    print(f"Open '{args.output}/index.html' in your web browser to view the archive.")


if __name__ == "__main__":
    main()
