"""
Yahoo Groups JSON to Static Website Converter

This module processes JSON files containing Yahoo Groups messages and converts them
into a static website.
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple

from .base_message import BaseMessage
from .json_message import JSONMessage
from .utils import _is_valid_message


class ProgressTracker:
    """Helper class to track and display processing progress."""
    
    def __init__(self, total_files: int, threads: Dict[str, List[BaseMessage]]):
        """Initialize with the total number of files to process and threads dict."""
        self.total_files = total_files
        self.threads = threads
        self.processed_files = 0
        self.processed_messages = 0
        self.valid_messages = 0
        self.start_time = time.time()
        self.last_update = 0
        
    def update_file_started(self, filename: str) -> None:
        """Called when starting to process a new file."""
        self.processed_files += 1
        self._print_status(f"Processing {filename}...")
        
    def update_messages_processed(self, count: int, valid: int) -> None:
        """Update the count of processed and valid messages."""
        self.processed_messages += count
        self.valid_messages += valid
        self._print_status()
        
    def _print_status(self, message: str = None) -> None:
        """Print the current status, but not too frequently."""
        current_time = time.time()
        if current_time - self.last_update < 1.0 and not message:
            return
            
        self.last_update = current_time
        elapsed = current_time - self.start_time
        rate = self.processed_messages / elapsed if elapsed > 0 else 0
        
        status_lines = []
        if message:
            status_lines.append(message)
            
        status_lines.extend([
            f"Files: {self.processed_files}/{self.total_files} "
            f"({self.processed_files/self.total_files:.1%})",
            f"Messages: {self.processed_messages} processed, "
            f"{self.valid_messages} valid ({rate:.1f} msg/sec)",
            f"Elapsed: {self._format_duration(elapsed)}"
        ])
        
        # Clear previous status if this isn't the first update
        if self.processed_files > 1 or self.processed_messages > 0:
            sys.stdout.write('\r' + '\n'.join([' ' * 80] * len(status_lines)) + '\r')
            
        sys.stdout.write('\n'.join(status_lines) + '\r')
        sys.stdout.flush()
    
    def final_report(self) -> Tuple[int, int, float]:
        """Print final report and return statistics."""
        elapsed = time.time() - self.start_time
        rate = self.processed_messages / elapsed if elapsed > 0 else 0
        thread_count = len(self.threads)
        
        print("\n" + "=" * 80)
        print(f"Processing complete!")
        print(f"- Processed {self.processed_files} files")
        print(f"- Processed {self.processed_messages} total messages")
        print(f"- Found {self.valid_messages} valid messages in {thread_count} threads")
        print(f"- Average speed: {rate:.1f} messages/second")
        print(f"- Total time: {self._format_duration(elapsed)}")
        print("=" * 80)
        
        return self.valid_messages, thread_count, elapsed
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds as a human-readable string."""
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"


def process_json_directory(json_dir: str) -> Dict[str, List[BaseMessage]]:
    """
    Process a directory containing JSON files and return a dictionary where keys are 
    thread names and values are lists of BaseMessage objects in that thread, sorted by date.
    Only processes files matching the pattern <integer>.json (e.g., 12345.json).
    
    Args:
        json_dir: Path to the directory containing JSON files
        
    Returns:
        Dictionary mapping thread names to lists of BaseMessage objects
    """
    threads: Dict[str, List[BaseMessage]] = {}

    if not os.path.isdir(json_dir):
        raise FileNotFoundError(f"Directory not found: {json_dir}")

    # Get list of JSON files to process
    json_files = [f for f in os.listdir(json_dir) 
                 if f.endswith('.json') and f[:-5].isdigit()]
    
    if not json_files:
        print(f"No valid JSON files found in {json_dir}")
        return threads
        
    print(f"Found {len(json_files)} JSON files to process in {json_dir}...")
    progress = ProgressTracker(len(json_files), threads)

    # Process each JSON file in the directory that matches <integer>.json pattern
    for filename in sorted(json_files, key=lambda x: int(x[:-5])):
        file_path = os.path.join(json_dir, filename)
        progress.update_file_started(filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            messages = data.get('messages', [])
            valid_count = 0
            
            # Process each message in the topic
            for msg_data in messages:
                try:
                    msg_id = int(msg_data.get('msgId', '0'))
                    if not msg_id:
                        print(f"\nWarning: Missing or invalid msgId in {filename}")
                        continue

                    msg = JSONMessage(msg_id, msg_data)

                    if not _is_valid_message(msg):
                        continue
                        
                    valid_count += 1

                    # Group by normalized subject (thread)
                    if msg.normalized_subject not in threads:
                        threads[msg.normalized_subject] = []

                    threads[msg.normalized_subject].append(msg)
                    
                except (KeyError, ValueError) as e:
                    print(f"\nError processing message in {filename}: {e}")
                    continue
                    
            progress.update_messages_processed(len(messages), valid_count)

        except (json.JSONDecodeError, OSError) as e:
            print(f"\nError reading {filename}: {e}")
            continue

    # Sort messages in each thread by date
    for thread_msgs in threads.values():
        thread_msgs.sort(key=lambda x: x.date if x.date else datetime.min)

    # Print final report
    total_messages = sum(len(msgs) for msgs in threads.values())
    progress.final_report()
    print(f"Grouped into {len(threads)} threads")
    return threads
