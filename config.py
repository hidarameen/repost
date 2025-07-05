import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import json

load_dotenv()

class Config:
    """Configuration class for the website monitoring bot"""
    
    # Bot Settings
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHAT_ID: str = os.getenv("CHAT_ID", os.getenv("CHANNEL_ID", ""))  # Support both names
    
    # Admin IDs - support both single ADMIN_ID and list ADMIN_IDS
    _admin_id = os.getenv("ADMIN_ID", "")
    _admin_ids = os.getenv("ADMIN_IDS", "[]")
    
    if _admin_id:
        # If single ADMIN_ID is provided, use it
        ADMIN_IDS: List[int] = [int(_admin_id)]
    else:
        # Try to parse ADMIN_IDS as JSON
        try:
            ADMIN_IDS: List[int] = json.loads(_admin_ids)
        except:
            ADMIN_IDS: List[int] = []
    
    # Website Settings
    WEBSITE_URL: str = os.getenv("WEBSITE_URL", "https://www.ansarollah.com.ye")
    WEBSITE_SECTIONS: List[str] = json.loads(os.getenv("WEBSITE_SECTIONS", '["news", "statements", "articles"]'))
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", os.getenv("MONITORING_INTERVAL", "120")))  # seconds
    
    # Telegraph Settings
    TELEGRAPH_TOKEN: str = os.getenv("TELEGRAPH_TOKEN", "")
    TELEGRAPH_AUTHOR: str = os.getenv("TELEGRAPH_AUTHOR", os.getenv("TELEGRAPH_AUTHOR_NAME", "الأنصار الله"))
    TELEGRAPH_AUTHOR_URL: str = os.getenv("TELEGRAPH_AUTHOR_URL", "https://www.ansarollah.com.ye")
    
    # Publishing Settings
    AUTO_PUBLISH: bool = os.getenv("AUTO_PUBLISH", "true").lower() == "true"
    ENABLE_TEXT_SHORTENING: bool = os.getenv("ENABLE_TEXT_SHORTENING", "true").lower() == "true"
    MAX_MESSAGE_LENGTH: int = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
    SHORT_DESCRIPTION_LENGTH: int = int(os.getenv("SHORT_DESCRIPTION_LENGTH", "200"))
    
    # Content Settings
    CUSTOM_HEADER: str = os.getenv("CUSTOM_HEADER", "📰 موقع الأنصار الله")
    CUSTOM_FOOTER: str = os.getenv("CUSTOM_FOOTER", "🔗 تابعونا للمزيد من الأخبار")
    
    # Database
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", os.getenv("DATABASE_FILE", "data/ansarollah_bot.db"))
    
    # Content Extraction
    EXTRACT_IMAGES: bool = os.getenv("EXTRACT_IMAGES", "true").lower() == "true"
    DOWNLOAD_IMAGES: bool = os.getenv("DOWNLOAD_IMAGES", "true").lower() == "true"
    
    # Filters
    EXCLUDE_KEYWORDS: List[str] = json.loads(os.getenv("EXCLUDE_KEYWORDS", '["إعلان", "ads", "advertisement"]'))
    INCLUDE_KEYWORDS: List[str] = json.loads(os.getenv("INCLUDE_KEYWORDS", "[]"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_fields = ['BOT_TOKEN', 'CHAT_ID', 'WEBSITE_URL']
        missing_fields = []
        
        for field in required_fields:
            value = getattr(cls, field)
            if not value or value == "":
                missing_fields.append(field)
        
        if missing_fields:
            print(f"Missing required configuration: {', '.join(missing_fields)}")
            return False
        
        # Check if at least one admin is configured
        if not cls.ADMIN_IDS:
            print("Warning: No admin IDs configured")
        
        return True
    
    @classmethod
    def get_section_settings(cls, section: str) -> Dict:
        """Get settings for a specific section"""
        section_settings = json.loads(os.getenv(f"SECTION_{section.upper()}_SETTINGS", "{}"))
        return section_settings
    
    @classmethod
    def print_config(cls):
        """Print current configuration (for debugging)"""
        print("Current Configuration:")
        print(f"  BOT_TOKEN: {'✅ Set' if cls.BOT_TOKEN else '❌ Missing'}")
        print(f"  CHAT_ID: {'✅ Set' if cls.CHAT_ID else '❌ Missing'} ({cls.CHAT_ID})")
        print(f"  ADMIN_IDS: {'✅ Set' if cls.ADMIN_IDS else '❌ Missing'} ({cls.ADMIN_IDS})")
        print(f"  WEBSITE_URL: {cls.WEBSITE_URL}")
        print(f"  AUTO_PUBLISH: {cls.AUTO_PUBLISH}")
        print(f"  CHECK_INTERVAL: {cls.CHECK_INTERVAL}")
        print(f"  DATABASE_PATH: {cls.DATABASE_PATH}")