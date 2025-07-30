from typing import List, Dict, Optional
from datetime import datetime
import time

from config import Config
from arxiv_client import ArXivClient
from gemini_processor import GeminiProcessor
from slack_notifier import SlackNotifier
from file_manager import FileManager


class ArXivProcessor:
    """Main processor class that orchestrates arXiv paper processing."""
    
    def __init__(self):
        self.arxiv_client = ArXivClient()
        self.gemini_processor = GeminiProcessor()
        self.slack_notifier = SlackNotifier()
        self.file_manager = FileManager()
        
        # Validate configuration
        if not Config.validate_config():
            print("Warning: Some configuration values are missing. Some features may not work.")
    
    def process_single_subject(
        self, 
        subject: str = Config.DEFAULT_SUBJECT,
        min_results: int = Config.DEFAULT_MIN_RESULTS,
        max_results: int = Config.DEFAULT_MAX_RESULTS,
        save_to_file: bool = True,
        send_to_slack: bool = True
    ) -> Dict[str, any]:
        """
        Process papers for a single subject.
        """
        start_time = time.time()
        results = {
            "subject": subject,
            "success": False,
            "papers_fetched": 0,
            "processing_time": 0,
            "file_path": None,
            "slack_sent": False,
            "error": None
        }
        
        try:
            print(f"Processing {subject} papers...")
            
            # Fetch papers
            papers = self.arxiv_client.fetch_papers(
                subject=subject,
                min_results=min_results,
                max_results=max_results
            )
            
            if not papers:
                results["error"] = "No papers found"
                return results
            
            results["papers_fetched"] = len(papers)
            print(f"Fetched {len(papers)} papers")
            
            # Process with Gemini
            markdown_content = self.gemini_processor.process_papers_efficiently(papers, subject)
            
            # Save to file if requested
            if save_to_file:
                file_path = self.file_manager.save_markdown(
                    markdown_content, 
                    subject=subject.replace(".", "_")
                )
                results["file_path"] = file_path
            
            # Send to Slack if requested
            if send_to_slack:
                slack_success = self.slack_notifier.send_summary(
                    markdown_content, 
                    subject=f"arXiv {subject}"
                )
                results["slack_sent"] = slack_success
            
            results["success"] = True
            results["processing_time"] = time.time() - start_time
            print(f"Processing completed in {results['processing_time']:.2f} seconds")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"Error processing {subject}: {e}")
            
            if send_to_slack:
                self.slack_notifier.send_error_notification(f"Error processing {subject}: {e}")
        
        return results
    
    def process_multiple_subjects(
        self, 
        subjects: List[str],
        min_results: int = Config.DEFAULT_MIN_RESULTS,
        max_results: int = Config.DEFAULT_MAX_RESULTS,
        save_to_file: bool = True,
        send_to_slack: bool = True
    ) -> Dict[str, any]:
        """
        Process papers for multiple subjects efficiently.
        """
        start_time = time.time()
        results = {
            "subjects": subjects,
            "success": False,
            "total_papers_fetched": 0,
            "processing_time": 0,
            "file_path": None,
            "slack_sent": False,
            "subject_results": [],
            "error": None
        }
        
        try:
            print(f"Processing {len(subjects)} subjects: {', '.join(subjects)}")
            
            # Fetch papers
            papers_by_subject = self.arxiv_client.get_recent_papers_by_subject(subjects)
            
            if not papers_by_subject:
                results["error"] = "No papers found for any subject"
                return results
            
            # Process all subjects
            markdown_content = self.gemini_processor.process_multiple_subjects(papers_by_subject)
            
            total_papers = sum(len(papers) for papers in papers_by_subject.values())
            results["total_papers_fetched"] = total_papers
            
            if save_to_file:
                file_path = self.file_manager.save_markdown(
                    markdown_content, 
                    subject="multi_subject_arxiv"
                )
                results["file_path"] = file_path
            
            if send_to_slack:
                slack_success = self.slack_notifier.send_summary(
                    markdown_content, 
                    subject=f"arXiv Papers ({len(subjects)} subjects)"
                )
                results["slack_sent"] = slack_success
            
            results["success"] = True
            results["processing_time"] = time.time() - start_time
            print(f"Multi-subject processing completed in {results['processing_time']:.2f} seconds")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"Error processing multiple subjects: {e}")
            
            if send_to_slack:
                self.slack_notifier.send_error_notification(f"Error processing multiple subjects: {e}")
        
        return results
    
    def test_connections(self) -> Dict[str, bool]:
        """
        Test external connections: Slack, Gemini, arXiv.
        """
        results = {
            "slack": False,
            "gemini": False,
            "arxiv": False
        }
        
        # Test Slack
        try:
            results["slack"] = self.slack_notifier.test_connection()
        except Exception as e:
            print(f"Slack connection test failed: {e}")
        
        # Test Gemini (use new API)
        try:
            test_response = self.gemini_processor.model.generate_content("Hello")
            if test_response and test_response.text:
                results["gemini"] = True
        except Exception as e:
            print(f"Gemini connection test failed: {e}")
        
        # Test arXiv
        try:
            test_papers = self.arxiv_client.fetch_papers(max_results=1)
            results["arxiv"] = len(test_papers) > 0
        except Exception as e:
            print(f"arXiv connection test failed: {e}")
        
        return results
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get processing statistics.
        """
        file_stats = self.file_manager.get_file_stats()
        
        return {
            "file_stats": file_stats,
            "config": {
                "batch_size": Config.BATCH_SIZE,
                "max_tokens_per_batch": Config.MAX_TOKENS_PER_BATCH,
                "default_subject": Config.DEFAULT_SUBJECT
            }
        }
        