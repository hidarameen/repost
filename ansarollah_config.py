"""
إعداد خاص لموقع الأنصار الله اليمني
==============================

هذا الملف يحتوي على إعدادات خاصة لموقع www.ansarollah.com.ye
"""

from typing import Dict, List

class AnsarallahConfig:
    """إعدادات موقع الأنصار الله"""
    
    # إعدادات الموقع الأساسية
    WEBSITE_URL = "https://www.ansarollah.com.ye"
    WEBSITE_NAME = "الأنصار الله"
    
    # أقسام الموقع
    SECTIONS = {
        "أخبار": {
            "url": "https://www.ansarollah.com.ye/archives/category/news",
            "selector": "article .entry-title a, .post-title a",
            "description": "الأخبار العامة"
        },
        "أخبار محلية": {
            "url": "https://www.ansarollah.com.ye/archives/category/local-news",
            "selector": "article .entry-title a, .post-title a",
            "description": "الأخبار المحلية"
        },
        "أخبار عربية": {
            "url": "https://www.ansarollah.com.ye/archives/category/arab-news",
            "selector": "article .entry-title a, .post-title a",
            "description": "الأخبار العربية"
        },
        "أخبار دولية": {
            "url": "https://www.ansarollah.com.ye/archives/category/international-news",
            "selector": "article .entry-title a, .post-title a",
            "description": "الأخبار الدولية"
        },
        "بيانات": {
            "url": "https://www.ansarollah.com.ye/archives/category/statements",
            "selector": "article .entry-title a, .post-title a",
            "description": "البيانات الرسمية"
        },
        "مقالات": {
            "url": "https://www.ansarollah.com.ye/archives/category/articles",
            "selector": "article .entry-title a, .post-title a",
            "description": "المقالات والتحليلات"
        }
    }
    
    # محددات استخراج المحتوى
    CONTENT_SELECTORS = {
        "title": [
            "h1.entry-title",
            "h1.post-title", 
            ".entry-header h1",
            "h1"
        ],
        "content": [
            ".entry-content",
            ".post-content",
            ".content",
            "article .entry-content",
            ".single-post-content"
        ],
        "date": [
            ".entry-date",
            ".post-date",
            "time.entry-date",
            ".date"
        ],
        "author": [
            ".entry-author",
            ".post-author",
            ".author-name",
            ".by-author"
        ],
        "image": [
            ".entry-thumbnail img",
            ".post-thumbnail img",
            ".featured-image img",
            ".wp-post-image"
        ],
        "category": [
            ".entry-category",
            ".post-category",
            ".category"
        ]
    }
    
    # إعدادات خاصة بالأقسام
    SECTION_SETTINGS = {
        "أخبار": {
            "custom_header": "📰 أخبار الأنصار الله",
            "default_tags": ["أخبار", "اليمن"],
            "emoji": "📰"
        },
        "أخبار محلية": {
            "custom_header": "🏠 أخبار محلية",
            "default_tags": ["أخبار محلية", "اليمن"],
            "emoji": "🏠"
        },
        "أخبار عربية": {
            "custom_header": "🌍 أخبار عربية",
            "default_tags": ["أخبار عربية", "العالم العربي"],
            "emoji": "🌍"
        },
        "أخبار دولية": {
            "custom_header": "🌐 أخبار دولية",
            "default_tags": ["أخبار دولية", "العالم"],
            "emoji": "🌐"
        },
        "بيانات": {
            "custom_header": "📋 بيانات رسمية",
            "default_tags": ["بيانات", "رسمي"],
            "emoji": "📋"
        },
        "مقالات": {
            "custom_header": "✍️ مقالات وتحليلات",
            "default_tags": ["مقالات", "تحليلات"],
            "emoji": "✍️"
        }
    }
    
    # كلمات مفتاحية مهمة
    IMPORTANT_KEYWORDS = [
        "عاجل", "بيان", "تصريح", "قرار", "إعلان",
        "العدوان", "المقاومة", "الصمود", "النصر",
        "فلسطين", "غزة", "الأقصى", "القدس",
        "أمريكا", "إسرائيل", "السعودية", "الإمارات"
    ]
    
    # كلمات للاستبعاد
    EXCLUDE_KEYWORDS = [
        "إعلان", "إعلانات", "رعاية", "تسويق"
    ]
    
    # إعدادات التنسيق
    FORMATTING = {
        "use_emoji": True,
        "add_source": True,
        "add_date": True,
        "add_category": True,
        "max_title_length": 100,
        "max_summary_length": 300
    }
    
    # إعدادات Telegraph
    TELEGRAPH_CONFIG = {
        "author": "قناة الأنصار الله",
        "author_url": "https://t.me/ansarollah_channel",
        "add_metadata": True,
        "add_source_link": True
    }
    
    @classmethod
    def get_section_config(cls, section_name: str) -> Dict:
        """الحصول على إعدادات قسم معين"""
        return cls.SECTIONS.get(section_name, {})
    
    @classmethod
    def get_section_settings(cls, section_name: str) -> Dict:
        """الحصول على إعدادات التنسيق لقسم معين"""
        return cls.SECTION_SETTINGS.get(section_name, {})
    
    @classmethod
    def get_all_sections(cls) -> List[str]:
        """الحصول على جميع أسماء الأقسام"""
        return list(cls.SECTIONS.keys())
    
    @classmethod
    def is_important_article(cls, title: str, content: str) -> bool:
        """تحديد ما إذا كان المقال مهماً"""
        text = f"{title} {content}".lower()
        return any(keyword in text for keyword in cls.IMPORTANT_KEYWORDS)
    
    @classmethod
    def should_exclude_article(cls, title: str, content: str) -> bool:
        """تحديد ما إذا كان يجب استبعاد المقال"""
        text = f"{title} {content}".lower()
        return any(keyword in text for keyword in cls.EXCLUDE_KEYWORDS)
    
    @classmethod
    def format_message(cls, article_data: Dict) -> str:
        """تنسيق رسالة المقال"""
        section = article_data.get("section", "")
        settings = cls.get_section_settings(section)
        
        message = ""
        
        # إضافة الرمز التعبيري
        if settings.get("emoji"):
            message += f"{settings['emoji']} "
        
        # إضافة العنوان
        message += f"**{article_data['title']}**\n\n"
        
        # إضافة الملخص
        if article_data.get("summary"):
            message += f"{article_data['summary']}\n\n"
        
        # إضافة التاريخ
        if article_data.get("date") and cls.FORMATTING["add_date"]:
            message += f"📅 {article_data['date']}\n"
        
        # إضافة القسم
        if section and cls.FORMATTING["add_category"]:
            message += f"📂 {section}\n"
        
        # إضافة المصدر
        if cls.FORMATTING["add_source"]:
            message += f"🔗 المصدر: {cls.WEBSITE_NAME}\n"
        
        return message