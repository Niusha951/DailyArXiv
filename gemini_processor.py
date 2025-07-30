import google.generativeai as genai
from typing import List, Dict
import time
from config import Config


class GeminiProcessor:
    """Processor for handling Gemini AI operations with efficient batching."""
    
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
        self.total_tokens_used = 0
    
    def estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count (4 chars per token)."""
        return len(text) // 4
    
    def create_efficient_prompt(self, paper: Dict[str, str], subject: str) -> str:
        """Create an efficient single-paper prompt for minimal token usage."""
        abstract = (
            paper['summary'][:Config.MAX_ABSTRACT_LENGTH]
            if len(paper['summary']) > Config.MAX_ABSTRACT_LENGTH
            else paper['summary']
        )
        
        prompt = f"""Summarize this arXiv paper in 2-3 bullet points:
Title: {paper['title']}
Abstract: {abstract}
Link: {paper['link']}

Focus on key findings and contributions. Be concise."""
        
        return prompt
    
    def process_papers_efficiently(
        self, 
        papers: List[Dict[str, str]], 
        subject: str,
        max_retries: int = 3
    ) -> str:
        if not papers:
            return f"# No papers found for {subject}\n"
        
        print(f"Processing {len(papers)} papers individually for minimal token usage...")
        
        summaries = []
        for i, paper in enumerate(papers, 1):
            print(f"Processing paper {i}/{len(papers)}: {paper['title'][:50]}...")
            prompt = self.create_efficient_prompt(paper, subject)
            summary = self._process_single_paper_with_retry(prompt, paper, max_retries)
            summaries.append(summary)
        
        combined_summary = f"# Latest arXiv Papers for {subject}\n\n"
        combined_summary += "\n\n".join(summaries)
        return combined_summary
    
    def _process_single_paper_with_retry(self, prompt: str, paper: Dict[str, str], max_retries: int) -> str:
        """Process a single paper with retry logic."""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                summary = response.text.strip()
                return f"## [{paper['title']}]({paper['link']})\n{summary}"
            except Exception as e:
                print(f"Paper processing attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return f"## [{paper['title']}]({paper['link']})\nError processing paper."
    
    def _process_papers_individually(self, papers: List[Dict[str, str]], subject: str) -> str:
        """Fallback: process papers one by one."""
        summaries = []
        for paper in papers:
            prompt = self.create_efficient_prompt(paper, subject)
            try:
                response = self.model.generate_content(prompt)
                summary = response.text.strip()
                summaries.append(f"## [{paper['title']}]({paper['link']})\n{summary}")
            except Exception as e:
                print(f"Error processing individual paper: {e}")
                summaries.append(f"## [{paper['title']}]({paper['link']})\nError processing paper.")
        return "\n\n".join(summaries)
    
    def process_multiple_subjects(self, papers_by_subject: Dict[str, List[Dict[str, str]]]) -> str:
        """Process papers from multiple subjects efficiently."""
        all_summaries = []
        for subject, papers in papers_by_subject.items():
            if papers:
                summary = self.process_papers_efficiently(papers, subject)
                all_summaries.append(summary)
        return "\n\n---\n\n".join(all_summaries)
        