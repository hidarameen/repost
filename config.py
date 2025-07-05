import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import json

load_dotenv()

class Config:
    """Configuration class for the website monitoring bot"""
    
    # Bot Settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    ADMIN_IDS: List[int] = json.loads(os.getenv("ADMIN_IDS", "[]"))
    
    # Website Settings
    WEBSITE_URL: str = os.getenv("WEBSITE_URL", "")
    WEBSITE_SECTIONS: List[str] = json.loads(os.getenv("WEBSITE_SECTIONS", "[]"))
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", "60"))  # seconds
    
    # Telegraph Settings
    TELEGRAPH_TOKEN: str = os.getenv("TELEGRAPH_TOKEN", "")
    TELEGRAPH_AUTHOR: str = os.getenv("TELEGRAPH_AUTHOR", "News Bot")
    TELEGRAPH_AUTHOR_URL: str = os.getenv("TELEGRAPH_AUTHOR_URL", "")
    
    # Publishing Settings
    AUTO_PUBLISH: bool = os.getenv("AUTO_PUBLISH", "false").lower() == "true"
    ENABLE_TEXT_SHORTENING: bool = os.getenv("ENABLE_TEXT_SHORTENING", "false").lower() == "true"
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
    SHORT_DESCRIPTION_LENGTH: int = int(os.getenv("SHORT_DESCRIPTION_LENGTH", "200"))
    
    # Content Settings
    CUSTOM_HEADER: str = os.getenv("CUSTOM_HEADER", "")
    CUSTOM_FOOTER: str = os.getenv("CUSTOM_FOOTER", "")
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "bot_data.db")
    
    # Content Extraction
    EXTRACT_IMAGES: bool = os.getenv("EXTRACT_IMAGES", "true").lower() == "true"
    DOWNLOAD_IMAGES: bool = os.getenv("DOWNLOAD_IMAGES", "true").lower() == "true"
    
    # Filters
    EXCLUDE_KEYWORDS: List[str] = json.loads(os.getenv("EXCLUDE_KEYWORDS", "[]"))
    INCLUDE_KEYWORDS: List[str] = json.loads(os.getenv("INCLUDE_KEYWORDS", "[]"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = ['BOT_TOKEN', 'CHANNEL_ID', 'WEBSITE_URL']
        missing_fields = []
        
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        return True
    
    @classmethod
    def get_section_settings(cls, section: str) -> Dict:
        """Get settings for a specific section"""
        section_settings = json.loads(os.getenv(f"SECTION_{section.upper()}_SETTINGS", "{}"))
        return section_settings