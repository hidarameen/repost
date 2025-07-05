import sqlite3
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from config import Config

@dataclass
class Article:
    """Article data structure"""
    id: Optional[int] = None
    url: str = ""
    title: str = ""
    content: str = ""
    summary: str = ""
    author: str = ""
    publish_date: Optional[datetime] = None
    section: str = ""
    image_url: str = ""
    tags: List[str] = None
    hash: str = ""
    telegram_message_id: Optional[int] = None
    telegraph_url: str = ""
    is_published: bool = False
    needs_approval: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if not self.hash:
            self.hash = self.generate_hash()
    
    def generate_hash(self) -> str:
        """Generate a unique hash for the article"""
        content = f"{self.url}{self.title}{self.content}"
        return hashlib.md5(content.encode()).hexdigest()

@dataclass
class Section:
    """Website section data structure"""
    id: Optional[int] = None
    name: str = ""
    url: str = ""
    selector: str = ""
    is_active: bool = True
    last_check: Optional[datetime] = None
    articles_count: int = 0
    custom_settings: Dict = None
    
    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}

class Database:
    """Database manager for the bot"""
    
    def __init__(self, db_path: str = Config.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                summary TEXT,
                author TEXT,
                publish_date DATETIME,
                section TEXT,
                image_url TEXT,
                tags TEXT,
                hash TEXT UNIQUE,
                telegram_message_id INTEGER,
                telegraph_url TEXT,
                is_published BOOLEAN DEFAULT 0,
                needs_approval BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                selector TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_check DATETIME,
                articles_count INTEGER DEFAULT 0,
                custom_settings TEXT
            )
        ''')
        
        # Bot settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Published messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS published_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER,
                message_id INTEGER,
                chat_id TEXT,
                message_type TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_article(self, article: Article) -> int:
        """Add a new article to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO articles (url, title, content, summary, author, publish_date, 
                                    section, image_url, tags, hash, telegram_message_id, 
                                    telegraph_url, is_published, needs_approval)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.url, article.title, article.content, article.summary,
                article.author, article.publish_date, article.section, article.image_url,
                json.dumps(article.tags), article.hash, article.telegram_message_id,
                article.telegraph_url, article.is_published, article.needs_approval
            ))
            
            article_id = cursor.lastrowid
            conn.commit()
            return article_id
            
        except sqlite3.IntegrityError:
            return 0  # Article already exists
        finally:
            conn.close()
    
    def get_article_by_url(self, url: str) -> Optional[Article]:
        """Get article by URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles WHERE url = ?', (url,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_article(row)
        return None
    
    def get_article_by_hash(self, hash: str) -> Optional[Article]:
        """Get article by hash"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles WHERE hash = ?', (hash,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_article(row)
        return None
    
    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """Get article by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_article(row)
        return None
    
    def get_unpublished_articles(self, limit: int = 50) -> List[Article]:
        """Get unpublished articles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            WHERE is_published = 0 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_article(row) for row in rows]
    
    def get_articles_pending_approval(self, limit: int = 50) -> List[Article]:
        """Get articles pending admin approval"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM articles 
            WHERE needs_approval = 1 AND is_published = 0 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_article(row) for row in rows]
    
    def update_article(self, article: Article) -> bool:
        """Update an existing article"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE articles SET 
                title = ?, content = ?, summary = ?, author = ?, 
                publish_date = ?, section = ?, image_url = ?, tags = ?, 
                telegram_message_id = ?, telegraph_url = ?, is_published = ?, 
                needs_approval = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            article.title, article.content, article.summary, article.author,
            article.publish_date, article.section, article.image_url,
            json.dumps(article.tags), article.telegram_message_id,
            article.telegraph_url, article.is_published, article.needs_approval,
            article.id
        ))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def add_section(self, section: Section) -> int:
        """Add a new section"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO sections (name, url, selector, is_active, custom_settings)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                section.name, section.url, section.selector, section.is_active,
                json.dumps(section.custom_settings)
            ))
            
            section_id = cursor.lastrowid
            conn.commit()
            return section_id
            
        except sqlite3.IntegrityError:
            return 0  # Section already exists
        finally:
            conn.close()
    
    def get_active_sections(self) -> List[Section]:
        """Get all active sections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sections WHERE is_active = 1')
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_section(row) for row in rows]
    
    def update_section_last_check(self, section_id: int):
        """Update the last check time for a section"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE sections SET last_check = CURRENT_TIMESTAMP WHERE id = ?
        ''', (section_id,))
        
        conn.commit()
        conn.close()
    
    def get_bot_setting(self, key: str) -> Optional[str]:
        """Get a bot setting value"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM bot_settings WHERE key = ?', (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
    
    def set_bot_setting(self, key: str, value: str, description: str = ""):
        """Set a bot setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO bot_settings (key, value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (key, value, description))
        
        conn.commit()
        conn.close()
    
    def add_published_message(self, article_id: int, message_id: int, chat_id: str, message_type: str):
        """Record a published message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO published_messages (article_id, message_id, chat_id, message_type)
            VALUES (?, ?, ?, ?)
        ''', (article_id, message_id, chat_id, message_type))
        
        conn.commit()
        conn.close()
    
    def _row_to_article(self, row) -> Article:
        """Convert database row to Article object"""
        return Article(
            id=row[0],
            url=row[1],
            title=row[2],
            content=row[3],
            summary=row[4],
            author=row[5],
            publish_date=datetime.fromisoformat(row[6]) if row[6] else None,
            section=row[7],
            image_url=row[8],
            tags=json.loads(row[9]) if row[9] else [],
            hash=row[10],
            telegram_message_id=row[11],
            telegraph_url=row[12],
            is_published=bool(row[13]),
            needs_approval=bool(row[14]),
            created_at=datetime.fromisoformat(row[15]) if row[15] else None,
            updated_at=datetime.fromisoformat(row[16]) if row[16] else None
        )
    
    def _row_to_section(self, row) -> Section:
        """Convert database row to Section object"""
        return Section(
            id=row[0],
            name=row[1],
            url=row[2],
            selector=row[3],
            is_active=bool(row[4]),
            last_check=datetime.fromisoformat(row[5]) if row[5] else None,
            articles_count=row[6],
            custom_settings=json.loads(row[7]) if row[7] else {}
        )