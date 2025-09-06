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
from typing import List

from .generator import SiteGenerator
from .message import Message


def _is_valid_message(message: Message) -> bool:
    return message.html_content and message.date


def process_mbox(mbox_path: str) -> List[Message]:
    """Process mbox file and return a list of Message objects."""
    messages = []
    msg_id = 1
    processed_count = 0
    start_time = time.time()

    if not os.path.exists(mbox_path):
        print(f"Error: File not found: {mbox_path}")
        sys.exit(1)

    print("Processing mbox file (this may take a while)...")
    
    try:
        mbox = mailbox.mbox(mbox_path)
        total_messages = len(mbox)
        print(f"Found {total_messages} messages to process")
        
        for msg in mbox:
            try:
                message = Message(msg_id, msg)

                if _is_valid_message(message):
                    messages.append(message)
                    msg_id += 1

                processed_count += 1
                
                # Show progress every 100 messages
                if processed_count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    print(f"Processed {processed_count}/{total_messages} messages ({processed_count/total_messages:.1%}) - {rate:.1f} msg/sec")
                    
            except Exception as e:
                print(f"\nError processing message {msg_id}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"\nError reading mbox file: {str(e)}")
        sys.exit(1)

    elapsed = time.time() - start_time
    print(f"\nFinished processing {processed_count} messages in {elapsed:.1f} seconds")
    if elapsed > 0:
        print(f"Average processing rate: {processed_count/elapsed:.1f} messages/second")
        
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
