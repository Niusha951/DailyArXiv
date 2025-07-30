#!/usr/bin/env python3
"""
Test script for ArXiv Paper Processor components

This script tests individual components to ensure they work correctly.
"""

import os
import sys
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from arxiv_client import ArXivClient
from gemini_processor import GeminiProcessor
from slack_notifier import SlackNotifier
from file_manager import FileManager


def test_config():
    """Test configuration module."""
    print("Testing Config module...")
    
    # Test default values
    assert Config.DEFAULT_SUBJECT == "astro-ph.GA"
    assert Config.BATCH_SIZE == 5
    assert Config.MAX_TOKENS_PER_BATCH == 4000
    
    # Test validation (should return False without API keys)
    assert not Config.validate_config()
    
    print("✓ Config module working correctly")


def test_arxiv_client():
    """Test ArXiv client module."""
    print("Testing ArXivClient module...")
    
    client = ArXivClient()
    
    # Test text cleaning
    test_text = "  This   is   a   test   "
    cleaned = client.clean_text(test_text)
    assert cleaned == "This is a test"
    
    # Test with empty text
    assert client.clean_text("") == ""
    assert client.clean_text(None) == ""
    
    print("✓ ArXivClient module working correctly")


def test_file_manager():
    """Test file manager module."""
    print("Testing FileManager module...")
    
    # Create temporary file manager
    file_manager = FileManager(output_dir="test_output")
    
    # Test markdown saving
    test_content = "# Test Content\n\nThis is a test."
    file_path = file_manager.save_markdown(test_content, "test_subject", include_timestamp=False)
    
    # Check file was created
    assert os.path.exists(file_path)
    
    # Test JSON saving
    test_data = {"test": "data", "number": 42}
    json_path = file_manager.save_json(test_data, "test_subject", include_timestamp=False)
    
    # Check file was created
    assert os.path.exists(json_path)
    
    # Test file stats
    stats = file_manager.get_file_stats()
    assert "total_files" in stats
    
    # Clean up test files
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(json_path):
        os.remove(json_path)
    if os.path.exists("test_output"):
        os.rmdir("test_output")
    
    print("✓ FileManager module working correctly")


def test_slack_notifier():
    """Test Slack notifier module."""
    print("Testing SlackNotifier module...")
    
    notifier = SlackNotifier()
    
    # Test message formatting
    test_markdown = "# Header\n## Subheader\n- Bullet point\n[Link](http://example.com)"
    formatted = notifier.format_message_for_slack(test_markdown)
    
    # Check that formatting occurred
    assert "Header" in formatted
    assert "Bullet point" in formatted
    
    # Test message splitting
    long_message = "A" * 5000  # Create a long message
    chunks = notifier.split_long_message(long_message, max_length=1000)
    
    # Should have multiple chunks
    assert len(chunks) > 1
    
    print("✓ SlackNotifier module working correctly")


def test_gemini_processor():
    """Test Gemini processor module."""
    print("Testing GeminiProcessor module...")
    
    # Mock the Gemini model to avoid API calls
    with patch('google.generativeai.GenerativeModel') as mock_model:
        mock_instance = Mock()
        mock_model.return_value = mock_instance
        
        processor = GeminiProcessor()
        
        # Test token estimation
        test_text = "This is a test text for token estimation."
        estimated_tokens = processor.estimate_tokens(test_text)
        assert estimated_tokens > 0
        
        # Test batch prompt creation
        test_papers = [
            {"title": "Test Paper 1", "summary": "Test summary 1", "link": "http://example.com/1"},
            {"title": "Test Paper 2", "summary": "Test summary 2", "link": "http://example.com/2"}
        ]
        
        prompt = processor.create_batch_prompt(test_papers, "test-subject")
        assert "Test Paper 1" in prompt
        assert "Test Paper 2" in prompt
        assert "test-subject" in prompt
        
        print("✓ GeminiProcessor module working correctly")


def test_integration():
    """Test basic integration between components."""
    print("Testing component integration...")
    
    # Test that components can be instantiated together
    try:
        from arxiv_processor import ArXivProcessor
        processor = ArXivProcessor()
        print("✓ Components can be instantiated together")
    except Exception as e:
        print(f"✗ Component integration failed: {e}")


def main():
    """Run all tests."""
    print("ArXiv Paper Processor - Component Tests")
    print("=" * 50)
    
    tests = [
        test_config,
        test_arxiv_client,
        test_file_manager,
        test_slack_notifier,
        test_gemini_processor,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 