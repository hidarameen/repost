import asyncio
import aiohttp
import requests
from telegraph import Telegraph
from typing import Dict, List, Optional, Any
import json
import re
from datetime import datetime
from PIL import Image
import io
import logging
from urllib.parse import urljoin, urlparse
from config import Config
from database import Article

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegraphManager:
    """Telegraph page creation and management"""
    
    def __init__(self):
        self.telegraph = Telegraph()
        self.account_info = None
        self.init_account()
    
    def init_account(self):
        """Initialize Telegraph account"""
        try:
            if Config.TELEGRAPH_TOKEN:
                # Use existing token
                self.telegraph.create_account(
                    short_name=Config.TELEGRAPH_AUTHOR,
                    author_name=Config.TELEGRAPH_AUTHOR,
                    author_url=Config.TELEGRAPH_AUTHOR_URL
                )
                self.account_info = self.telegraph.get_account_info()
            else:
                # Create new account
                self.account_info = self.telegraph.create_account(
                    short_name=Config.TELEGRAPH_AUTHOR,
                    author_name=Config.TELEGRAPH_AUTHOR,
                    author_url=Config.TELEGRAPH_AUTHOR_URL
                )
                logger.info(f"Created new Telegraph account: {self.account_info}")
            
        except Exception as e:
            logger.error(f"Error initializing Telegraph account: {e}")
            self.account_info = None
    
    async def create_article_page(self, article: Article) -> Optional[str]:
        """Create a Telegraph page for an article"""
        try:
            if not self.account_info:
                logger.error("Telegraph account not initialized")
                return None
            
            # Prepare content for Telegraph
            content = await self._prepare_telegraph_content(article)
            
            # Create the page
            response = self.telegraph.create_page(
                title=article.title,
                content=content,
                author_name=article.author or Config.TELEGRAPH_AUTHOR,
                author_url=Config.TELEGRAPH_AUTHOR_URL,
                return_content=True
            )
            
            if response and 'url' in response:
                telegraph_url = response['url']
                logger.info(f"Created Telegraph page: {telegraph_url}")
                return telegraph_url
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating Telegraph page: {e}")
            return None
    
    async def _prepare_telegraph_content(self, article: Article) -> List[Dict]:
        """Prepare article content for Telegraph format"""
        content = []
        
        # Add custom header if configured
        if Config.CUSTOM_HEADER:
            content.append({
                'tag': 'p',
                'children': [Config.CUSTOM_HEADER]
            })
        
        # Add article metadata
        metadata = self._create_metadata_section(article)
        content.extend(metadata)
        
        # Add main image if available
        if article.image_url:
            image_element = await self._create_image_element(article.image_url)
            if image_element:
                content.append(image_element)
        
        # Convert markdown content to Telegraph format
        article_content = self._convert_markdown_to_telegraph(article.content)
        content.extend(article_content)
        
        # Add custom footer if configured
        if Config.CUSTOM_FOOTER:
            content.append({
                'tag': 'p',
                'children': [Config.CUSTOM_FOOTER]
            })
        
        # Add source and sharing links
        footer_links = self._create_footer_links(article)
        content.extend(footer_links)
        
        return content
    
    def _create_metadata_section(self, article: Article) -> List[Dict]:
        """Create metadata section for the article"""
        metadata = []
        
        # Website and section info
        if article.section:
            metadata.append({
                'tag': 'p',
                'children': [
                    {
                        'tag': 'strong',
                        'children': [f'القسم: {article.section}']
                    }
                ]
            })
        
        # Author and date
        info_parts = []
        if article.author:
            info_parts.append(f'الكاتب: {article.author}')
        
        if article.publish_date:
            date_str = article.publish_date.strftime('%Y-%m-%d %H:%M')
            info_parts.append(f'التاريخ: {date_str}')
        
        if info_parts:
            metadata.append({
                'tag': 'p',
                'children': [
                    {
                        'tag': 'em',
                        'children': [' | '.join(info_parts)]
                    }
                ]
            })
        
        # Tags if available
        if article.tags:
            metadata.append({
                'tag': 'p',
                'children': [
                    {
                        'tag': 'small',
                        'children': [f'العلامات: {", ".join(article.tags)}']
                    }
                ]
            })
        
        # Add separator
        if metadata:
            metadata.append({
                'tag': 'hr'
            })
        
        return metadata
    
    async def _create_image_element(self, image_url: str) -> Optional[Dict]:
        """Create image element for Telegraph"""
        try:
            # Download and upload image to Telegraph
            uploaded_url = await self._upload_image_to_telegraph(image_url)
            
            if uploaded_url:
                return {
                    'tag': 'img',
                    'attrs': {
                        'src': uploaded_url
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating image element: {e}")
            return None
    
    async def _upload_image_to_telegraph(self, image_url: str) -> Optional[str]:
        """Upload image to Telegraph"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Resize image if too large
                        image_data = self._resize_image_if_needed(image_data)
                        
                        # Upload to Telegraph
                        files = {'file': ('image.jpg', image_data, 'image/jpeg')}
                        upload_response = requests.post(
                            'https://telegra.ph/upload',
                            files=files
                        )
                        
                        if upload_response.status_code == 200:
                            result = upload_response.json()
                            if result and len(result) > 0:
                                return 'https://telegra.ph' + result[0]['src']
            
            return None
            
        except Exception as e:
            logger.error(f"Error uploading image to Telegraph: {e}")
            return None
    
    def _resize_image_if_needed(self, image_data: bytes, max_size: int = 5 * 1024 * 1024) -> bytes:
        """Resize image if it's too large"""
        try:
            if len(image_data) <= max_size:
                return image_data
            
            # Open image and resize
            image = Image.open(io.BytesIO(image_data))
            
            # Calculate new size while maintaining aspect ratio
            ratio = (max_size / len(image_data)) ** 0.5
            new_width = int(image.width * ratio)
            new_height = int(image.height * ratio)
            
            # Resize image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            resized_image.save(output, format='JPEG', quality=85)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image_data
    
    def _convert_markdown_to_telegraph(self, markdown_text: str) -> List[Dict]:
        """Convert markdown text to Telegraph format"""
        content = []
        
        # Split text into paragraphs
        paragraphs = markdown_text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Handle different markdown elements
            if paragraph.startswith('# '):
                # H1 heading
                content.append({
                    'tag': 'h3',
                    'children': [paragraph[2:]]
                })
            elif paragraph.startswith('## '):
                # H2 heading
                content.append({
                    'tag': 'h4',
                    'children': [paragraph[3:]]
                })
            elif paragraph.startswith('### '):
                # H3 heading
                content.append({
                    'tag': 'h4',
                    'children': [paragraph[4:]]
                })
            elif paragraph.startswith('- ') or paragraph.startswith('* '):
                # Lists
                list_items = paragraph.split('\n')
                list_content = []
                for item in list_items:
                    item = item.strip()
                    if item.startswith('- ') or item.startswith('* '):
                        list_content.append({
                            'tag': 'li',
                            'children': [item[2:]]
                        })
                
                if list_content:
                    content.append({
                        'tag': 'ul',
                        'children': list_content
                    })
            else:
                # Regular paragraph - process inline formatting
                formatted_paragraph = self._process_inline_formatting(paragraph)
                content.append({
                    'tag': 'p',
                    'children': formatted_paragraph
                })
        
        return content
    
    def _process_inline_formatting(self, text: str) -> List[Any]:
        """Process inline markdown formatting"""
        # This is a simplified version - you might want to use a proper markdown parser
        result = []
        
        # Handle bold text
        parts = re.split(r'\*\*(.*?)\*\*', text)
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                if part:
                    result.append(part)
            else:
                # Bold text
                result.append({
                    'tag': 'strong',
                    'children': [part]
                })
        
        # Handle italic text (simplified)
        # Handle links (simplified)
        
        return result if result else [text]
    
    def _create_footer_links(self, article: Article) -> List[Dict]:
        """Create footer with original source and sharing links"""
        footer = []
        
        # Add separator
        footer.append({
            'tag': 'hr'
        })
        
        # Original source link
        footer.append({
            'tag': 'p',
            'children': [
                {
                    'tag': 'strong',
                    'children': ['المصدر الأصلي: ']
                },
                {
                    'tag': 'a',
                    'attrs': {
                        'href': article.url,
                        'target': '_blank'
                    },
                    'children': [article.title]
                }
            ]
        })
        
        # Website info
        try:
            website_name = urlparse(article.url).netloc
            footer.append({
                'tag': 'p',
                'children': [
                    {
                        'tag': 'small',
                        'children': [f'الموقع: {website_name}']
                    }
                ]
            })
        except Exception:
            pass
        
        return footer
    
    def get_page_views(self, page_path: str) -> int:
        """Get page views for a Telegraph page"""
        try:
            page_info = self.telegraph.get_page(page_path, return_content=False)
            return page_info.get('views', 0)
        except Exception:
            return 0
    
    def update_page(self, page_path: str, title: str, content: List[Dict]) -> Optional[str]:
        """Update an existing Telegraph page"""
        try:
            response = self.telegraph.edit_page(
                path=page_path,
                title=title,
                content=content
            )
            
            if response and 'url' in response:
                return response['url']
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating Telegraph page: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """Get Telegraph account information"""
        return self.account_info
    
    def get_page_list(self, offset: int = 0, limit: int = 50) -> List[Dict]:
        """Get list of pages created by the account"""
        try:
            response = self.telegraph.get_page_list(offset=offset, limit=limit)
            return response.get('pages', [])
        except Exception as e:
            logger.error(f"Error getting page list: {e}")
            return []