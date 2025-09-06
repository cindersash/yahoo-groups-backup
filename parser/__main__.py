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


def process_mbox(mbox_path: str) -> (List[Message], List[List[Message]]):
    """Process mbox file and return a list of Message objects grouped by thread."""
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
        
        # First pass: collect all valid messages
        all_messages = []
        for msg in mbox:
            try:
                message = Message(msg_id, msg)

                if _is_valid_message(message):
                    all_messages.append(message)
                    msg_id += 1

                processed_count += 1
                
                # Show progress every 100 messages
                if processed_count % 100 == 0 or processed_count == total_messages:
                    elapsed = time.time() - start_time
                    rate = processed_count / elapsed if elapsed > 0 else 0
                    print(f"  Processed {processed_count}/{total_messages} messages "
                          f"({processed_count/total_messages:.1%}) - {rate:.1f} msg/sec")
                        
            except Exception as e:
                print(f"Error processing message {msg_id}: {str(e)}")
                continue
        
        # Group messages by thread (normalized subject)
        threads = {}
        for message in all_messages:
            thread_key = message.normalized_subject or '(No subject)'
            if thread_key not in threads:
                threads[thread_key] = []
            threads[thread_key].append(message)
        
        # Sort messages within each thread by date
        for thread_messages in threads.values():
            thread_messages.sort(key=lambda x: x.date)
        
        # Flatten the threads back into a single list for compatibility
        # The SiteGenerator will handle the grouping
        messages = [msg for thread in threads.values() for msg in thread]
                
    except Exception as e:
        print(f"Error processing mbox file: {str(e)}")
        sys.exit(1)
        
    print(f"\nSuccessfully processed {len(messages)} valid messages out of {total_messages}")
    print(f"Grouped into {len(threads)} threads")
    return messages, list(threads.values())


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Convert Yahoo Groups mbox to static website')
    parser.add_argument('mbox_file', help='Path to the mbox file')
    parser.add_argument('-o', '--output', default='output', help='Output directory (default: output)')
    
    args = parser.parse_args()
    
    # Process mbox file
    messages, threads = process_mbox(args.mbox_file)
    
    if not messages:
        print("No messages found in the mbox file.")
        sys.exit(1)

    print(f"Processed {len(messages)} messages in {len(threads)} threads.")
    print(f"Generating static website in: {args.output}")

    # Generate the static website using SiteGenerator
    generator = SiteGenerator(args.output)
    generator.generate_site(messages, threads)
    
    print(f"\nDone! The static website has been generated in the '{args.output}' directory.")
    print(f"Open '{args.output}/index.html' in your web browser to view the archive.")


if __name__ == '__main__':
    main()
