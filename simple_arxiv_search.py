#!/usr/bin/env python3
"""
Simple ArXiv Keyword Search Tool

This script searches arXiv for papers matching keywords, summarizes the first 3 recent papers,
and sends results to Slack. Optimized for minimal token usage with Gemini 1.5 Flash.
"""

import requests
import xml.etree.ElementTree as ET
import re
import os
import sys
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")

# Gemini configuration
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

# Slack configuration
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

def clean_text(text: str) -> str:
    """Remove newlines and excessive spaces."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def search_arxiv_papers(keywords: str, subject: str = "astro-ph.GA", max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search arXiv for papers matching keywords.
    
    Args:
        keywords: Search keywords (e.g., "dwarf galaxies", "Milky Way satellites")
        max_results: Number of papers to fetch
        
    Returns:
        List of paper dictionaries with title, summary, and link
    """
    # Clean and format keywords for search
#    search_query = keywords.replace(" ", "+")
    
    keyword_query = "+AND+".join([f"all:{kw}" for kw in keywords.strip().split()])
    search_query = f"cat:{subject}+AND+{keyword_query}"


    url = (
        "http://export.arxiv.org/api/query?"
        f"search_query={search_query}&"
        "sortBy=submittedDate&sortOrder=descending&"
        f"start=0&max_results={max_results}"
    )
    
    try:
        response = requests.get(url, timeout=30)
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
                title = clean_text(raw_title)
                summary = clean_text(raw_summary)
                
                entries.append({
                    "title": title, 
                    "summary": summary, 
                    "link": link
                })
        
        print(f"Found {len(entries)} papers for keywords: '{keywords}'")
        return entries
        
    except Exception as e:
        print(f"Error searching arXiv: {e}")
        return []

def create_efficient_prompt(paper: Dict[str, str]) -> str:
    """Create an efficient prompt for minimal token usage."""
    # Truncate abstract to save tokens
    abstract = paper['summary'][:150] if len(paper['summary']) > 150 else paper['summary']
    
    prompt = f"""Summarize this arXiv paper in 2-3 bullet points:
Title: {paper['title']}
Abstract: {abstract}

Focus on key findings. Be concise."""
    
    return prompt

def summarize_paper(paper: Dict[str, str]) -> str:
    """Summarize a single paper using Gemini."""
    try:
        prompt = create_efficient_prompt(paper)
        
        # Use the newer API format
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        summary = response.text.strip()
        return f"## [{paper['title']}]({paper['link']})\n{summary}"
        
    except Exception as e:
        print(f"Error summarizing paper: {e}")
        return f"## [{paper['title']}]({paper['link']})\nError processing paper."

def format_for_slack(markdown_content: str, keywords: str) -> str:
    """Convert markdown to Slack-compatible format."""
    # Convert markdown headers to bold text
    content = re.sub(r'^# (.+)$', r'*:newspaper: \1*', markdown_content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'*:page_facing_up: \1*', content, flags=re.MULTILINE)
    
    # Convert markdown links to Slack format
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', content)
    
    # Convert bullet points
    content = re.sub(r'^\s*[-*]\s+', '• ', content, flags=re.MULTILINE)
    
    # Remove excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Add header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f":mag: *ArXiv Search Results for '{keywords}'* - {timestamp}\n\n"
    
    return header + content.strip()

def send_to_slack(message: str) -> bool:
    """Send message to Slack."""
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        response = client.chat_postMessage(
            channel=SLACK_CHANNEL_ID,
            text=message,
            unfurl_links=False
        )
        print("✅ Message sent to Slack successfully!")
        return True
    except SlackApiError as e:
        print(f"❌ Error sending to Slack: {e.response['error']}")
        return False
    except Exception as e:
        print(f"❌ Error sending to Slack: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python simple_arxiv_search.py 'your keywords'")
        print("Example: python simple_arxiv_search.py 'dwarf galaxies'")
        sys.exit(1)
    
    keywords = sys.argv[1]
    
    # Check API keys
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set in .env file")
        sys.exit(1)
    
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        print("❌ SLACK_BOT_TOKEN or SLACK_CHANNEL_ID not set in .env file")
        sys.exit(1)
    
    print(f"🔍 Searching arXiv for: '{keywords}'")
    print("=" * 50)
    
    # Search for papers
    papers = search_arxiv_papers(keywords, max_results=3)
    
    if not papers:
        print("❌ No papers found for the given keywords")
        sys.exit(1)
    
    # Summarize each paper
    print(f"📝 Summarizing {len(papers)} papers...")
    summaries = []
    
    for i, paper in enumerate(papers, 1):
        print(f"Processing paper {i}/{len(papers)}: {paper['title'][:50]}...")
        summary = summarize_paper(paper)
        summaries.append(summary)
    
    # Combine summaries
    markdown_content = f"# ArXiv Papers for '{keywords}'\n\n"
    markdown_content += "\n\n".join(summaries)
    
    # Format for Slack and send
    slack_message = format_for_slack(markdown_content, keywords)
    
    print("\n📤 Sending to Slack...")
    success = send_to_slack(slack_message)
    
    if success:
        print("✅ Search completed successfully!")
    else:
        print("❌ Failed to send to Slack")
        # Save to file as backup
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"arxiv_search_{keywords.replace(' ', '_')}_{timestamp}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"📄 Saved to file: {filename}")

if __name__ == "__main__":
    main() 
