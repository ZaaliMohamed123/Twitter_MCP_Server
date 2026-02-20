"""
TrendToThread Configuration
Loads environment variables from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load .env file from project root
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)


class TwitterConfig:
    """Twitter API configuration loaded from environment variables."""
    
    API_KEY: str = os.getenv("TWITTER_API_KEY", "")
    API_SECRET: str = os.getenv("TWITTER_API_SECRET", "")
    ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN", "")
    ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
    
    @classmethod
    def validate(cls) -> bool:
        """Check if all required credentials are set."""
        required = [cls.API_KEY, cls.API_SECRET, cls.ACCESS_TOKEN, cls.ACCESS_TOKEN_SECRET]
        return all(required) and all(v != "" for v in required)
    
    @classmethod
    def get_missing(cls) -> list[str]:
        """Return list of missing credential names."""
        missing = []
        if not cls.API_KEY:
            missing.append("TWITTER_API_KEY")
        if not cls.API_SECRET:
            missing.append("TWITTER_API_SECRET")
        if not cls.ACCESS_TOKEN:
            missing.append("TWITTER_ACCESS_TOKEN")
        if not cls.ACCESS_TOKEN_SECRET:
            missing.append("TWITTER_ACCESS_TOKEN_SECRET")
        return missing


class NgrokConfig:
    """Ngrok configuration loaded from environment variables."""
    
    AUTH_TOKEN: str = os.getenv("NGROK_AUTH_TOKEN", "")
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if ngrok auth token is set."""
        return bool(cls.AUTH_TOKEN)


# Server configuration
SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
