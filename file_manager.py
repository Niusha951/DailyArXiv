import os
from datetime import datetime
from typing import Optional
from config import Config


class FileManager:
    """Manager for saving and organizing arXiv paper summaries."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Ensure output directory exists."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"Created output directory: {self.output_dir}")
    
    def save_markdown(
        self, 
        content: str, 
        subject: str = "arxiv_papers",
        include_timestamp: bool = True
    ) -> str:
        """
        Save markdown content to a file.
        
        Args:
            content: Markdown content to save
            subject: Subject name for filename
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to saved file
        """
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{subject}_{timestamp}.md"
        else:
            filename = f"{subject}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Markdown file saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving file {filepath}: {e}")
            return ""
    
    def save_json(
        self, 
        data: dict, 
        subject: str = "arxiv_papers",
        include_timestamp: bool = True
    ) -> str:
        """
        Save data as JSON file.
        
        Args:
            data: Data to save as JSON
            subject: Subject name for filename
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to saved file
        """
        import json
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{subject}_{timestamp}.json"
        else:
            filename = f"{subject}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"JSON file saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving JSON file {filepath}: {e}")
            return ""
    
    def get_latest_file(self, subject: str = "arxiv_papers", extension: str = ".md") -> Optional[str]:
        """
        Get the most recent file for a subject.
        
        Args:
            subject: Subject name to search for
            extension: File extension to search for
            
        Returns:
            Path to latest file or None if not found
        """
        try:
            files = [f for f in os.listdir(self.output_dir) 
                    if f.startswith(subject) and f.endswith(extension)]
            
            if not files:
                return None
            
            # Sort by modification time (newest first)
            files_with_time = [(f, os.path.getmtime(os.path.join(self.output_dir, f))) 
                              for f in files]
            files_with_time.sort(key=lambda x: x[1], reverse=True)
            
            return os.path.join(self.output_dir, files_with_time[0][0])
        except Exception as e:
            print(f"Error finding latest file: {e}")
            return None
    
    def cleanup_old_files(self, days_to_keep: int = 30):
        """
        Clean up old files to prevent disk space issues.
        
        Args:
            days_to_keep: Number of days to keep files
        """
        import time
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        try:
            for filename in os.listdir(self.output_dir):
                filepath = os.path.join(self.output_dir, filename)
                if os.path.isfile(filepath):
                    if os.path.getmtime(filepath) < cutoff_time:
                        os.remove(filepath)
                        print(f"Removed old file: {filename}")
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def get_file_stats(self) -> dict:
        """
        Get statistics about saved files.
        
        Returns:
            Dictionary with file statistics
        """
        try:
            files = os.listdir(self.output_dir)
            stats = {
                "total_files": len(files),
                "markdown_files": len([f for f in files if f.endswith('.md')]),
                "json_files": len([f for f in files if f.endswith('.json')]),
                "total_size_mb": sum(os.path.getsize(os.path.join(self.output_dir, f)) 
                                   for f in files) / (1024 * 1024)
            }
            return stats
        except Exception as e:
            print(f"Error getting file stats: {e}")
            return {} 