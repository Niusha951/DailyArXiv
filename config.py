import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for arXiv paper processor."""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID", "")
    
    # arXiv Settings
    DEFAULT_SUBJECT = "astro-ph.GA"
    DEFAULT_MIN_RESULTS = 0
    DEFAULT_MAX_RESULTS = 10
    
    # Processing Settings
    MAX_ABSTRACT_LENGTH = 200  # Truncate abstracts to save tokens
    MAX_RETRIES = 3  # Maximum retry attempts for API calls
    
    # Slack Settings
    SLACK_MESSAGE_LENGTH_LIMIT = 3000  # Slack message character limit
    
    # Model Settings
    GEMINI_MODEL = "models/gemini-1.5-flash"
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.GEMINI_API_KEY:
            print("Warning: GEMINI_API_KEY not set")
            return False
        if not cls.SLACK_BOT_TOKEN:
            print("Warning: SLACK_BOT_TOKEN not set")
            return False
        if not cls.SLACK_CHANNEL_ID:
            print("Warning: SLACK_CHANNEL_ID not set")
            return False
        return True 