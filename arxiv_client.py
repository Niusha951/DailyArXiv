import requests
import xml.etree.ElementTree as ET
import re
from typing import List, Dict, Optional
from datetime import datetime
import time
from config import Config


class ArXivClient:
    """Client for fetching papers from arXiv API."""
    
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'arXiv-Paper-Processor/1.0'
        })
    
    def clean_text(self, text: str) -> str:
        """Remove newlines and excessive spaces."""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    def fetch_papers(
        self, 
        subject: str = Config.DEFAULT_SUBJECT,
        min_results: int = Config.DEFAULT_MIN_RESULTS,
        max_results: int = Config.DEFAULT_MAX_RESULTS,
        max_retries: int = 3
    ) -> List[Dict[str, str]]:
        """
        Fetch papers from arXiv by category with retry logic.
        
        Args:
            subject: arXiv category (e.g., 'astro-ph.GA', 'quant-ph')
            min_results: start index
            max_results: number of papers to fetch
            max_retries: maximum number of retry attempts
            
        Returns:
            List of paper dictionaries with title, summary, and link
        """
        url = (
            f"{self.base_url}?"
            f"search_query=cat:{subject}&"
            "sortBy=submittedDate&sortOrder=descending&"
            f"start={min_results}&max_results={max_results}"
        )
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                root = ET.fromstring(response.content)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = []
                
                for entry in root.findall("atom:entry", ns):
                    title_elem = entry.find("atom:title", ns)
                    summary_elem = entry.find("atom:summary", ns)
                    link_elem = entry.find("atom:id", ns)
                    
                    if title_elem is not None and summary_elem is not None and link_elem is not None:
                        raw_title = title_elem.text
                        raw_summary = summary_elem.text
                        link = link_elem.text.strip()
                        
                        # Clean up whitespace
                        title = self.clean_text(raw_title)
                        summary = self.clean_text(raw_summary)
                        
                        entries.append({
                            "title": title, 
                            "summary": summary, 
                            "link": link,
                            "subject": subject
                        })
                
                print(f"Successfully fetched {len(entries)} papers from arXiv")
                return entries
                
            except requests.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print(f"Failed to fetch papers after {max_retries} attempts")
                    return []
    
    def get_recent_papers_by_subject(self, subjects: List[str]) -> Dict[str, List[Dict[str, str]]]:
        """
        Fetch recent papers for multiple subjects.
        
        Args:
            subjects: List of arXiv subjects to fetch
            
        Returns:
            Dictionary mapping subjects to their papers
        """
        results = {}
        for subject in subjects:
            papers = self.fetch_papers(subject=subject)
            if papers:
                results[subject] = papers
        return results 