#!/usr/bin/env python3
"""
ArXiv Paper Processor - Modular Design

This script processes recent arXiv papers using efficient batching and sends
summaries to Slack. It's designed for cost and speed optimization.
"""

import os
import sys
from typing import List
import argparse

from arxiv_processor import ArXivProcessor
from config import Config


def setup_environment():
    """Set up environment variables if not already set."""
    missing_keys = []
    
    if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_gemini_api_key_here":
        missing_keys.append("GEMINI_API_KEY")
    
    if not Config.SLACK_BOT_TOKEN or Config.SLACK_BOT_TOKEN == "xoxb-your_slack_bot_token_here":
        missing_keys.append("SLACK_BOT_TOKEN")
    
    if not Config.SLACK_CHANNEL_ID or Config.SLACK_CHANNEL_ID == "C1234567890":
        missing_keys.append("SLACK_CHANNEL_ID")
    
    if missing_keys:
        print("❌ Missing or invalid API keys!")
        print("Please set the following environment variables:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\nOption 1: Edit the .env file:")
        print("  cp .env.example .env")
        print("  # Then edit .env with your actual API keys")
        print("\nOption 2: Set environment variables:")
        print("  export GEMINI_API_KEY='your-api-key'")
        print("  export SLACK_BOT_TOKEN='your-slack-token'")
        print("  export SLACK_CHANNEL_ID='your-channel-id'")
        return False
    
    return True


def main():
    """Main function to run the arXiv paper processor."""
    parser = argparse.ArgumentParser(description="Process arXiv papers and send to Slack")
    parser.add_argument(
        "--subjects", 
        nargs="+", 
        default=[Config.DEFAULT_SUBJECT],
        help="arXiv subjects to process (e.g., astro-ph.GA quant-ph)"
    )
    parser.add_argument(
        "--max-results", 
        type=int, 
        default=Config.DEFAULT_MAX_RESULTS,
        help="Maximum number of papers per subject"
    )
    parser.add_argument(
        "--min-results", 
        type=int, 
        default=Config.DEFAULT_MIN_RESULTS,
        help="Starting index for results"
    )
    parser.add_argument(
        "--no-slack", 
        action="store_true",
        help="Don't send results to Slack"
    )
    parser.add_argument(
        "--no-file", 
        action="store_true",
        help="Don't save results to file"
    )
    parser.add_argument(
        "--test-connections", 
        action="store_true",
        help="Test all external connections"
    )
    parser.add_argument(
        "--stats", 
        action="store_true",
        help="Show processing statistics"
    )
    
    args = parser.parse_args()
    
    # Check environment setup
    if not setup_environment():
        sys.exit(1)
    
    # Initialize processor
    processor = ArXivProcessor()
    
    # Test connections if requested
    if args.test_connections:
        print("Testing connections...")
        connection_results = processor.test_connections()
        for service, status in connection_results.items():
            print(f"{service.capitalize()}: {'✓' if status else '✗'}")
        return
    
    # Show stats if requested
    if args.stats:
        print("Processing Statistics:")
        stats = processor.get_stats()
        print(f"  Files: {stats['file_stats']['total_files']}")
        print(f"  Markdown files: {stats['file_stats']['markdown_files']}")
        print(f"  Total size: {stats['file_stats']['total_size_mb']:.2f} MB")
        print(f"  Batch size: {stats['config']['batch_size']}")
        print(f"  Max tokens per batch: {stats['config']['max_tokens_per_batch']}")
        return
    
    # Process papers
    print(f"Starting arXiv paper processing...")
    print(f"Subjects: {', '.join(args.subjects)}")
    print(f"Max results per subject: {args.max_results}")
    print(f"Send to Slack: {not args.no_slack}")
    print(f"Save to file: {not args.no_file}")
    print("-" * 50)
    
    if len(args.subjects) == 1:
        # Single subject processing
        results = processor.process_single_subject(
            subject=args.subjects[0],
            min_results=args.min_results,
            max_results=args.max_results,
            save_to_file=not args.no_file,
            send_to_slack=not args.no_slack
        )
    else:
        # Multiple subjects processing
        results = processor.process_multiple_subjects(
            subjects=args.subjects,
            min_results=args.min_results,
            max_results=args.max_results,
            save_to_file=not args.no_file,
            send_to_slack=not args.no_slack
        )
    
    # Print results
    print("-" * 50)
    print("Processing Results:")
    if results["success"]:
        if "papers_fetched" in results:
            print(f"  Papers fetched: {results['papers_fetched']}")
        else:
            print(f"  Total papers fetched: {results['total_papers_fetched']}")
        print(f"  Processing time: {results['processing_time']:.2f} seconds")
        if results.get("file_path"):
            print(f"  File saved: {results['file_path']}")
        print(f"  Slack sent: {'✓' if results['slack_sent'] else '✗'}")
    else:
        print(f"  Error: {results['error']}")
    
    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())