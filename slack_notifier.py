from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Optional, List
import re
from config import Config


class SlackNotifier:
    """Slack notifier for sending arXiv paper summaries."""
    
    def __init__(self):
        self.client = WebClient(token=Config.SLACK_BOT_TOKEN)
        self.channel_id = Config.SLACK_CHANNEL_ID
    
    def format_message_for_slack(self, markdown_content: str) -> str:
        """
        Convert markdown content to Slack-compatible format.
        
        Args:
            markdown_content: Raw markdown content
            
        Returns:
            Slack-formatted message
        """
        # Remove markdown headers and convert to Slack format
        content = markdown_content
        
        # Convert markdown headers to bold text
        content = re.sub(r'^# (.+)$', r'*:newspaper: \1*', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'*:page_facing_up: \1*', content, flags=re.MULTILINE)
        
        # Convert markdown links to Slack format
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<\2|\1>', content)
        
        # Convert bullet points
        content = re.sub(r'^\s*[-*]\s+', '• ', content, flags=re.MULTILINE)
        
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def split_long_message(self, message: str, max_length: int = Config.SLACK_MESSAGE_LENGTH_LIMIT) -> List[str]:
        """
        Split long messages into chunks that fit Slack's limits.
        
        Args:
            message: The message to split
            max_length: Maximum length per chunk
            
        Returns:
            List of message chunks
        """
        if len(message) <= max_length:
            return [message]
        
        chunks = []
        current_chunk = ""
        
        # Split by sections (headers)
        sections = re.split(r'(?=^:newspaper:|^:page_facing_up:)', message, flags=re.MULTILINE)
        
        for section in sections:
            if not section.strip():
                continue
                
            # If adding this section would exceed limit, start new chunk
            if len(current_chunk) + len(section) > max_length and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = section
            else:
                current_chunk += section
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def send_summary(self, markdown_content: str, subject: str = "arXiv Papers") -> bool:
        """
        Send formatted summary to Slack.
        
        Args:
            markdown_content: Raw markdown content
            subject: Subject line for the message
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Format for Slack
            slack_message = self.format_message_for_slack(markdown_content)
            
            # Add timestamp and subject
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f":rocket: *{subject} Summary* - {timestamp}\n\n"
            
            full_message = header + slack_message
            
            # Split if too long
            message_chunks = self.split_long_message(full_message)
            
            success = True
            for i, chunk in enumerate(message_chunks):
                try:
                    response = self.client.chat_postMessage(
                        channel=self.channel_id,
                        text=chunk,
                        unfurl_links=False  # Don't expand links to avoid clutter
                    )
                    print(f"Sent message chunk {i+1}/{len(message_chunks)} to Slack")
                    
                except SlackApiError as e:
                    print(f"Error sending Slack message: {e.response['error']}")
                    success = False
                    break
            
            return success
            
        except Exception as e:
            print(f"Error formatting or sending Slack message: {e}")
            return False
    
    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification to Slack.
        
        Args:
            error_message: Error message to send
            
        Returns:
            True if successful, False otherwise
        """
        try:
            message = f":warning: *arXiv Paper Processor Error*\n{error_message}"
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
            return True
        except SlackApiError as e:
            print(f"Error sending error notification to Slack: {e.response['error']}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test Slack connection and permissions.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.auth_test()
            print(f"Connected to Slack as: {response['user']}")
            return True
        except SlackApiError as e:
            print(f"Slack connection test failed: {e.response['error']}")
            return False 