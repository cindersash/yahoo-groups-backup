#!/usr/bin/env python3
"""
Yahoo Groups Mbox to Static Website Converter

This script converts an mbox file containing Yahoo Groups messages into a static website.
"""

import argparse
import mailbox
import os
import sys
from typing import List

from .generator import SiteGenerator
from .message import Message


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

    # Generate the static website using SiteGenerator
    generator = SiteGenerator(args.output_dir)
    generator.generate_site(messages)

    print(f"\nDone! The static website has been generated in the '{args.output_dir}' directory.")
    print(f"Open '{args.output_dir}/index.html' in your web browser to view the archive.")


if __name__ == '__main__':
    main()
