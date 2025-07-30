#!/usr/bin/env python3
"""
Example usage of the ArXiv Paper Processor

This script demonstrates how to use the modular arXiv processor
programmatically for different use cases.
"""

import os
from arxiv_processor import ArXivProcessor
from config import Config


def example_single_subject():
    """Example: Process a single subject."""
    print("=== Single Subject Processing ===")
    
    processor = ArXivProcessor()
    
    # Process astrophysics papers
    results = processor.process_single_subject(
        subject="astro-ph.GA",
        max_results=5,
        save_to_file=True,
        send_to_slack=False  # Set to True if you have Slack configured
    )
    
    print(f"Success: {results['success']}")
    print(f"Papers fetched: {results['papers_fetched']}")
    print(f"Processing time: {results['processing_time']:.2f} seconds")
    if results.get('file_path'):
        print(f"File saved: {results['file_path']}")


def example_multiple_subjects():
    """Example: Process multiple subjects efficiently."""
    print("\n=== Multiple Subjects Processing ===")
    
    processor = ArXivProcessor()
    
    # Process multiple physics categories
    subjects = ["quant-ph", "cond-mat.mtrl-sci", "physics.optics"]
    
    results = processor.process_multiple_subjects(
        subjects=subjects,
        max_results=3,  # 3 papers per subject
        save_to_file=True,
        send_to_slack=False
    )
    
    print(f"Success: {results['success']}")
    print(f"Total papers fetched: {results['total_papers_fetched']}")
    print(f"Processing time: {results['processing_time']:.2f} seconds")
    if results.get('file_path'):
        print(f"File saved: {results['file_path']}")


def example_connection_testing():
    """Example: Test all external connections."""
    print("\n=== Connection Testing ===")
    
    processor = ArXivProcessor()
    results = processor.test_connections()
    
    for service, status in results.items():
        print(f"{service.capitalize()}: {'✓' if status else '✗'}")


def example_statistics():
    """Example: Get processing statistics."""
    print("\n=== Statistics ===")
    
    processor = ArXivProcessor()
    stats = processor.get_stats()
    
    print("File Statistics:")
    for key, value in stats['file_stats'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    print("\nConfiguration:")
    for key, value in stats['config'].items():
        print(f"  {key}: {value}")


def example_custom_configuration():
    """Example: Custom configuration usage."""
    print("\n=== Custom Configuration ===")
    
    # You can modify Config values programmatically
    Config.BATCH_SIZE = 3  # Smaller batches for testing
    Config.MAX_TOKENS_PER_BATCH = 2000  # Lower token limit
    
    processor = ArXivProcessor()
    
    # Process with custom settings
    results = processor.process_single_subject(
        subject="cs.AI",  # Computer Science - Artificial Intelligence
        max_results=2,
        save_to_file=True,
        send_to_slack=False
    )
    
    print(f"Success: {results['success']}")
    print(f"Papers fetched: {results['papers_fetched']}")


def main():
    """Run all examples."""
    print("ArXiv Paper Processor - Example Usage")
    print("=" * 50)
    
    # Check if API key is set
    if not Config.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Some examples may fail.")
        print("Set it with: export GEMINI_API_KEY='your-api-key'")
    
    try:
        # Run examples
        example_connection_testing()
        example_statistics()
        example_single_subject()
        example_multiple_subjects()
        example_custom_configuration()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set up the required API keys.")


if __name__ == "__main__":
    main() 