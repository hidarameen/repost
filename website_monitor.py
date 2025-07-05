import requests
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from newspaper import Article as NewsArticle
from readability import Document
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import html2text
import re
import logging
from urllib.parse import urljoin, urlparse
from config import Config
from database import Database, Article, Section

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteMonitor:
    """Website monitoring and content extraction"""
    
    def __init__(self, db: Database):
        self.db = db
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    async def monitor_all_sections(self) -> List[Article]:
        """Monitor all active sections for new content"""
        sections = self.db.get_active_sections()
        new_articles = []
        
        for section in sections:
            logger.info(f"Checking section: {section.name}")
            try:
                articles = await self.check_section(section)
                new_articles.extend(articles)
                self.db.update_section_last_check(section.id)
            except Exception as e:
                logger.error(f"Error checking section {section.name}: {e}")
        
        return new_articles
    
    async def check_section(self, section: Section) -> List[Article]:
        """Check a specific section for new articles"""
        try:
            # Get the section page
            response = self.session.get(section.url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find articles using the section selector
            article_elements = soup.select(section.selector) if section.selector else soup.find_all('a', href=True)
            
            new_articles = []
            
            for element in article_elements:
                try:
                    # Extract article URL
                    article_url = self._extract_article_url(element, section.url)
                    
                    if not article_url or not self._is_valid_article_url(article_url):
                        continue
                    
                    # Check if article already exists
                    existing_article = self.db.get_article_by_url(article_url)
                    if existing_article:
                        continue
                    
                    # Extract and process article
                    article = await self.extract_article(article_url, section.name)
                    if article:
                        # Apply section-specific settings
                        article = self._apply_section_settings(article, section)
                        
                        # Apply filters
                        if self._should_include_article(article):
                            article_id = self.db.add_article(article)
                            if article_id > 0:
                                article.id = article_id
                                new_articles.append(article)
                                logger.info(f"Added new article: {article.title}")
                        
                except Exception as e:
                    logger.error(f"Error processing article element: {e}")
            
            return new_articles
            
        except Exception as e:
            logger.error(f"Error checking section {section.name}: {e}")
            return []
    
    async def extract_article(self, url: str, section: str) -> Optional[Article]:
        """Extract article content from URL"""
        try:
            # Use newspaper3k for content extraction
            news_article = NewsArticle(url)
            news_article.download()
            news_article.parse()
            
            # Fallback to manual extraction if newspaper3k fails
            if not news_article.text:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Use readability for content extraction
                doc = Document(response.text)
                content = doc.summary()
                
                soup = BeautifulSoup(content, 'html.parser')
                text_content = soup.get_text(strip=True)
                
                # Convert HTML to markdown
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = False
                markdown_content = h.handle(content)
                
            else:
                text_content = news_article.text
                markdown_content = self._convert_to_markdown(text_content)
            
            # Extract additional information
            title = news_article.title or self._extract_title_from_url(url)
            author = news_article.authors[0] if news_article.authors else ""
            publish_date = news_article.publish_date or datetime.now()
            
            # Extract main image
            image_url = ""
            if news_article.top_image:
                image_url = news_article.top_image
            else:
                image_url = self._extract_main_image(url)
            
            # Create summary
            summary = self._create_summary(text_content)
            
            # Extract tags/keywords
            tags = list(news_article.keywords) if news_article.keywords else []
            
            # Create article object
            article = Article(
                url=url,
                title=title,
                content=markdown_content,
                summary=summary,
                author=author,
                publish_date=publish_date,
                section=section,
                image_url=image_url,
                tags=tags,
                needs_approval=not Config.AUTO_PUBLISH
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error extracting article from {url}: {e}")
            return None
    
    def _extract_article_url(self, element, base_url: str) -> str:
        """Extract article URL from element"""
        if element.name == 'a':
            href = element.get('href')
        else:
            link_element = element.find('a', href=True)
            href = link_element.get('href') if link_element else None
        
        if href:
            return urljoin(base_url, href)
        return ""
    
    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL is a valid article URL"""
        if not url:
            return False
        
        # Skip external URLs
        if not url.startswith(Config.WEBSITE_URL):
            return False
        
        # Skip common non-article URLs
        skip_patterns = [
            '/category/', '/tag/', '/author/', '/page/', '/search/',
            '.pdf', '.doc', '.zip', '.jpg', '.png', '.gif',
            '/wp-admin/', '/wp-content/', '/feed/', '/rss/'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract title from URL as fallback"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different title selectors
            title_selectors = ['h1', 'title', '.entry-title', '.post-title', '.article-title']
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    return element.get_text(strip=True)
            
            # Fallback to URL path
            return url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            
        except Exception:
            return url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
    
    def _extract_main_image(self, url: str) -> str:
        """Extract main image from article"""
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different image selectors
            image_selectors = [
                'meta[property="og:image"]',
                'meta[name="twitter:image"]',
                '.featured-image img',
                '.post-thumbnail img',
                '.entry-content img:first-child',
                'img[src*="featured"]'
            ]
            
            for selector in image_selectors:
                element = soup.select_one(selector)
                if element:
                    if element.name == 'meta':
                        image_url = element.get('content')
                    else:
                        image_url = element.get('src')
                    
                    if image_url:
                        return urljoin(url, image_url)
            
            return ""
            
        except Exception:
            return ""
    
    def _create_summary(self, content: str, max_length: int = None) -> str:
        """Create a summary from content"""
        if max_length is None:
            max_length = Config.SHORT_DESCRIPTION_LENGTH
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        if len(content) <= max_length:
            return content
        
        # Find the last complete sentence within the limit
        truncated = content[:max_length]
        last_sentence_end = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_sentence_end > max_length * 0.7:  # If we have at least 70% of the content
            return content[:last_sentence_end + 1]
        else:
            return content[:max_length] + "..."
    
    def _convert_to_markdown(self, text: str) -> str:
        """Convert plain text to markdown format"""
        # Simple markdown conversion
        lines = text.split('\n')
        markdown_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append("")
                continue
            
            # Add paragraph formatting
            if not line.startswith('#') and not line.startswith('-') and not line.startswith('*'):
                markdown_lines.append(line)
            else:
                markdown_lines.append(line)
        
        return '\n\n'.join(markdown_lines)
    
    def _apply_section_settings(self, article: Article, section: Section) -> Article:
        """Apply section-specific settings to article"""
        settings = section.custom_settings
        
        # Apply custom formatting
        if settings.get('custom_header'):
            article.content = settings['custom_header'] + '\n\n' + article.content
        
        if settings.get('custom_footer'):
            article.content = article.content + '\n\n' + settings['custom_footer']
        
        # Apply custom tags
        if settings.get('default_tags'):
            article.tags.extend(settings['default_tags'])
        
        return article
    
    def _should_include_article(self, article: Article) -> bool:
        """Check if article should be included based on filters"""
        # Check exclude keywords
        if Config.EXCLUDE_KEYWORDS:
            text_to_check = f"{article.title} {article.content}".lower()
            for keyword in Config.EXCLUDE_KEYWORDS:
                if keyword.lower() in text_to_check:
                    return False
        
        # Check include keywords (if specified, at least one must match)
        if Config.INCLUDE_KEYWORDS:
            text_to_check = f"{article.title} {article.content}".lower()
            for keyword in Config.INCLUDE_KEYWORDS:
                if keyword.lower() in text_to_check:
                    return True
            return False  # None of the include keywords matched
        
        return True
    
    def add_section(self, name: str, url: str, selector: str = "", custom_settings: Dict = None) -> int:
        """Add a new section to monitor"""
        section = Section(
            name=name,
            url=url,
            selector=selector,
            custom_settings=custom_settings or {}
        )
        
        return self.db.add_section(section)
    
    def get_sections(self) -> List[Section]:
        """Get all active sections"""
        return self.db.get_active_sections()
    
    async def test_section(self, url: str, selector: str = "") -> List[str]:
        """Test section monitoring and return found article URLs"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find articles using the selector
            article_elements = soup.select(selector) if selector else soup.find_all('a', href=True)
            
            article_urls = []
            for element in article_elements:
                article_url = self._extract_article_url(element, url)
                if article_url and self._is_valid_article_url(article_url):
                    article_urls.append(article_url)
            
            return article_urls[:10]  # Return first 10 for testing
            
        except Exception as e:
            logger.error(f"Error testing section {url}: {e}")
            return []