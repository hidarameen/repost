#!/usr/bin/env python3
"""
Website Monitoring and Telegram Publishing Bot
===============================================

This bot monitors websites for new articles and publishes them to Telegram channels
with support for Telegraph pages, admin approval, and multiple publishing modes.

Features:
- Monitor multiple website sections
- Extract article content automatically
- Publish to Telegram with images
- Create Telegraph pages for long articles
- Admin approval system
- Text shortening mode
- Custom headers and footers
- Content filtering
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import List, Dict
import schedule
import time
from concurrent.futures import ThreadPoolExecutor
import threading

from config import Config
from database import Database, Article, Section
from website_monitor import WebsiteMonitor
from telegraph_manager import TelegraphManager
from telegram_publisher import TelegramPublisher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class NewsBot:
    """Main bot class that orchestrates all components"""
    
    def __init__(self):
        self.running = False
        self.monitor_task = None
        self.bot_task = None
        self.schedule_thread = None
        self.shutdown_event = None
        self._loop = None
        
        # Initialize components
        self.db = Database()
        self.telegraph_manager = TelegraphManager()
        self.website_monitor = WebsiteMonitor(self.db)
        self.telegram_publisher = TelegramPublisher(self.db, self.telegraph_manager)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Bot initialized successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        # Set the shutdown event instead of creating a task
        if self.shutdown_event and not self.shutdown_event.is_set():
            self.shutdown_event.set()
    
    async def start(self):
        """Start the bot"""
        logger.info("Starting News Bot...")
        
        # Store the event loop for thread-safe task scheduling
        self._loop = asyncio.get_event_loop()
        
        # Create shutdown event in the proper event loop context
        self.shutdown_event = asyncio.Event()
        
        # Print configuration for debugging
        Config.print_config()
        
        # Validate configuration
        if not Config.validate():
            logger.error("Configuration validation failed")
            return False
        
        # Initialize database
        self.db.init_database()
        
        # Setup initial sections if configured
        await self.setup_initial_sections()
        
        # Start monitoring
        self.running = True
        
        # Start background tasks
        self.monitor_task = asyncio.create_task(self.monitoring_loop())
        self.bot_task = asyncio.create_task(self.telegram_publisher.run_bot())
        
        # Start scheduler in separate thread
        self.schedule_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.schedule_thread.start()
        
        logger.info("Bot started successfully")
        
        # Wait for shutdown signal or task completion
        try:
            done, pending = await asyncio.wait(
                [self.monitor_task, self.bot_task, asyncio.create_task(self.shutdown_event.wait())],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks gracefully
            for task in pending:
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=5.0)
                    except asyncio.CancelledError:
                        logger.debug(f"Task {task} was cancelled successfully")
                    except asyncio.TimeoutError:
                        logger.warning(f"Task {task} did not respond to cancellation within timeout")
                    except Exception as e:
                        logger.warning(f"Error while cancelling task {task}: {e}")
            
            # Stop the bot properly
            await self.stop()
            
        except Exception as e:
            logger.error(f"Error during bot execution: {e}")
            await self.stop()
        
        return True
    
    async def stop(self):
        """Stop the bot"""
        if not self.running:
            return
            
        logger.info("Stopping News Bot...")
        
        self.running = False
        
        # Cancel monitor task with timeout
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            try:
                await asyncio.wait_for(self.monitor_task, timeout=3.0)
            except asyncio.CancelledError:
                logger.debug("Monitor task cancelled successfully")
            except asyncio.TimeoutError:
                logger.warning("Monitor task did not stop within timeout")
            except Exception as e:
                logger.warning(f"Error stopping monitor task: {e}")
        
        # Stop telegram bot
        if self.telegram_publisher:
            try:
                await self.telegram_publisher.stop_bot()
            except Exception as e:
                logger.warning(f"Error stopping telegram bot: {e}")
        
        logger.info("Bot stopped successfully")
    
    async def setup_initial_sections(self):
        """Setup initial sections from configuration"""
        try:
            for section_name in Config.WEBSITE_SECTIONS:
                # Check if section already exists
                existing_sections = self.db.get_active_sections()
                if any(s.name == section_name for s in existing_sections):
                    continue
                
                # Create section URL (this would need to be configured per website)
                section_url = f"{Config.WEBSITE_URL.rstrip('/')}/{section_name.lower()}/"
                
                # Add section
                section_id = self.website_monitor.add_section(
                    name=section_name,
                    url=section_url,
                    selector="article a, .post-title a, .entry-title a"  # Common selectors
                )
                
                if section_id > 0:
                    logger.info(f"Added section: {section_name}")
                
        except Exception as e:
            logger.error(f"Error setting up initial sections: {e}")
    
    async def monitoring_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitoring loop...")
        
        while self.running:
            try:
                # Monitor all sections
                new_articles = await self.website_monitor.monitor_all_sections()
                
                if new_articles:
                    logger.info(f"Found {len(new_articles)} new articles")
                    
                    # Process each article
                    for article in new_articles:
                        await self.process_new_article(article)
                
                # Wait for next check
                await asyncio.sleep(Config.CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def process_new_article(self, article: Article):
        """Process a new article"""
        try:
            logger.info(f"Processing article: {article.title}")
            
            if Config.AUTO_PUBLISH:
                # Publish immediately
                success = await self.telegram_publisher.publish_article(article)
                
                if success:
                    logger.info(f"Published article: {article.title}")
                else:
                    logger.error(f"Failed to publish article: {article.title}")
            else:
                # Send to admins for approval
                await self.send_for_approval(article)
                logger.info(f"Sent article for approval: {article.title}")
                
        except Exception as e:
            logger.error(f"Error processing article {article.title}: {e}")
    
    async def send_for_approval(self, article: Article):
        """Send article to admins for approval"""
        try:
            for admin_id in Config.ADMIN_IDS:
                try:
                    await self.telegram_publisher.send_article_for_approval(admin_id, article)
                except Exception as e:
                    logger.error(f"Error sending article to admin {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error sending article for approval: {e}")
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        # Schedule periodic tasks
        schedule.every(5).minutes.do(self.cleanup_old_data)
        schedule.every().hour.do(self.update_statistics)
        schedule.every().day.at("00:00").do(self.daily_report)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)
    
    def cleanup_old_data(self):
        """Clean up old data"""
        try:
            logger.info("Running cleanup task...")
            # Implement cleanup logic here
            # For example, remove old published articles from database
            pass
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    def update_statistics(self):
        """Update statistics"""
        try:
            logger.info("Updating statistics...")
            # Update section statistics
            sections = self.db.get_active_sections()
            for section in sections:
                # Update article count for section
                # This would require additional database queries
                pass
        except Exception as e:
            logger.error(f"Error updating statistics: {e}")
    
    def daily_report(self):
        """Send daily report to admins"""
        try:
            logger.info("Generating daily report...")
            
            # Get statistics
            sections = self.db.get_active_sections()
            pending_articles = self.db.get_articles_pending_approval()
            unpublished_articles = self.db.get_unpublished_articles()
            
            report = f"""
📊 التقرير اليومي - {datetime.now().strftime('%Y-%m-%d')}

📰 الأقسام النشطة: {len(sections)}
📝 المقالات المعلقة: {len(pending_articles)}
📋 المقالات غير المنشورة: {len(unpublished_articles)}

🔄 حالة البوت: {'🟢 يعمل' if self.running else '🔴 متوقف'}
            """
            
            # Use asyncio.run_coroutine_threadsafe to safely schedule the task
            if self.running and hasattr(self, '_loop') and self._loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    self.telegram_publisher.notify_admins(report), 
                    self._loop
                )
                # Don't wait for the result to avoid blocking the scheduler thread
            else:
                logger.info(f"Daily report ready: {report}")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
    
    # Management commands
    async def add_section(self, name: str, url: str, selector: str = ""):
        """Add a new section"""
        try:
            section_id = self.website_monitor.add_section(name, url, selector)
            if section_id > 0:
                logger.info(f"Added section: {name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding section: {e}")
            return False
    
    async def test_section(self, url: str, selector: str = ""):
        """Test section monitoring"""
        try:
            article_urls = await self.website_monitor.test_section(url, selector)
            return article_urls
        except Exception as e:
            logger.error(f"Error testing section: {e}")
            return []
    
    async def get_bot_status(self) -> Dict:
        """Get bot status"""
        try:
            sections = self.db.get_active_sections()
            pending_articles = self.db.get_articles_pending_approval()
            unpublished_articles = self.db.get_unpublished_articles()
            
            return {
                'running': self.running,
                'sections_count': len(sections),
                'pending_articles': len(pending_articles),
                'unpublished_articles': len(unpublished_articles),
                'auto_publish': Config.AUTO_PUBLISH,
                'text_shortening': Config.ENABLE_TEXT_SHORTENING,
                'check_interval': Config.CHECK_INTERVAL,
                'telegraph_connected': self.telegraph_manager.account_info is not None
            }
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return {}
    
    async def manual_check(self):
        """Manually trigger a check"""
        try:
            logger.info("Manual check triggered")
            new_articles = await self.website_monitor.monitor_all_sections()
            
            if new_articles:
                for article in new_articles:
                    await self.process_new_article(article)
            
            return len(new_articles)
        except Exception as e:
            logger.error(f"Error in manual check: {e}")
            return 0

def main():
    """Main function"""
    logger.info("Starting News Bot...")
    
    # Create bot instance
    bot = NewsBot()
    
    try:
        # Run the bot
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()