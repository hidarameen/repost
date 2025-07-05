import asyncio
import logging
from typing import List, Dict, Optional, Tuple
import re
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError
import io
import requests
from PIL import Image
from config import Config
from database import Database, Article
from telegraph_manager import TelegraphManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramPublisher:
    """Telegram bot for publishing articles"""
    
    def __init__(self, db: Database, telegraph_manager: TelegraphManager):
        self.db = db
        self.telegraph_manager = telegraph_manager
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.application = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup bot handlers"""
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("pending", self.pending_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("sections", self.sections_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
        
        # Callback handlers
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        if user_id not in Config.ADMIN_IDS:
            await update.message.reply_text("عذراً، هذا البوت مخصص للإدارة فقط.")
            return
        
        welcome_message = """
🤖 مرحباً بك في بوت مراقبة المواقع والنشر التلقائي!

الأوامر المتاحة:
/help - عرض المساعدة
/status - حالة البوت
/pending - المقالات المعلقة
/settings - إعدادات البوت
/sections - إدارة الأقسام
/test - اختبار النظام

البوت يعمل على مراقبة المواقع المحددة وينشر المقالات الجديدة تلقائياً.
        """
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        help_text = """
📖 دليل استخدام البوت:

🔧 الأوامر الأساسية:
/start - بدء التشغيل
/help - هذه المساعدة
/status - حالة البوت والإحصائيات
/pending - عرض المقالات المعلقة للموافقة
/settings - تعديل إعدادات البوت
/sections - إدارة أقسام الموقع
/test - اختبار النظام

🎛️ الميزات:
• مراقبة المواقع كل دقيقة
• النشر التلقائي أو اليدوي
• إنشاء صفحات Telegraph للمقالات الطويلة
• تقسيم النصوص الطويلة على عدة رسائل
• إدارة الأقسام والفلاتر
• نظام الموافقة من الإدارة

📝 وضع النشر:
• النشر الكامل: ينشر المقال كاملاً في القناة
• النشر المختصر: ينشر ملخص + رابط Telegraph للمقال الكامل
        """
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        # Get statistics
        sections = self.db.get_active_sections()
        pending_articles = self.db.get_articles_pending_approval()
        unpublished_articles = self.db.get_unpublished_articles()
        
        status_text = f"""
📊 حالة البوت:

🔄 النشر التلقائي: {'🟢 مفعل' if Config.AUTO_PUBLISH else '🔴 معطل'}
✂️ اختصار النصوص: {'🟢 مفعل' if Config.ENABLE_TEXT_SHORTENING else '🔴 معطل'}
⏰ فترة المراقبة: {Config.CHECK_INTERVAL} ثانية

📰 الأقسام النشطة: {len(sections)}
📝 المقالات المعلقة: {len(pending_articles)}
📋 المقالات غير المنشورة: {len(unpublished_articles)}

🔗 Telegraph: {'🟢 متصل' if self.telegraph_manager.account_info else '🔴 غير متصل'}
        """
        
        keyboard = [
            [InlineKeyboardButton("تحديث الحالة", callback_data="status_refresh")],
            [InlineKeyboardButton("إعدادات البوت", callback_data="settings_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(status_text, reply_markup=reply_markup)
    
    async def pending_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        pending_articles = self.db.get_articles_pending_approval(limit=10)
        
        if not pending_articles:
            await update.message.reply_text("لا توجد مقالات معلقة للموافقة.")
            return
        
        for article in pending_articles:
            await self.send_article_for_approval(update.message.chat_id, article)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        keyboard = [
            [InlineKeyboardButton("النشر التلقائي", callback_data="setting_auto_publish")],
            [InlineKeyboardButton("اختصار النصوص", callback_data="setting_text_shortening")],
            [InlineKeyboardButton("فترة المراقبة", callback_data="setting_check_interval")],
            [InlineKeyboardButton("إدارة الأقسام", callback_data="sections_manage")],
            [InlineKeyboardButton("الفلاتر", callback_data="setting_filters")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚙️ إعدادات البوت:", reply_markup=reply_markup)
    
    async def sections_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /sections command"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        sections = self.db.get_active_sections()
        
        if not sections:
            await update.message.reply_text("لا توجد أقسام مضافة.")
            return
        
        sections_text = "📂 الأقسام النشطة:\n\n"
        for section in sections:
            last_check = section.last_check.strftime("%Y-%m-%d %H:%M") if section.last_check else "لم يتم فحصه"
            sections_text += f"• {section.name}\n"
            sections_text += f"  📄 المقالات: {section.articles_count}\n"
            sections_text += f"  🕐 آخر فحص: {last_check}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("إضافة قسم", callback_data="section_add")],
            [InlineKeyboardButton("إدارة الأقسام", callback_data="sections_manage")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(sections_text, reply_markup=reply_markup)
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /test command"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        # Create test article
        test_article = Article(
            title="مقال تجريبي",
            content="هذا مقال تجريبي لاختبار النظام.",
            summary="ملخص تجريبي",
            section="اختبار",
            url="https://example.com/test",
            author="البوت"
        )
        
        await self.send_article_for_approval(update.message.chat_id, test_article)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        if query.data.startswith("approve_"):
            article_id = int(query.data.split("_")[1])
            await self.approve_article(query, article_id)
        
        elif query.data.startswith("reject_"):
            article_id = int(query.data.split("_")[1])
            await self.reject_article(query, article_id)
        
        elif query.data.startswith("edit_"):
            article_id = int(query.data.split("_")[1])
            await self.edit_article(query, article_id)
        
        elif query.data == "status_refresh":
            await self.status_command(update, context)
        
        elif query.data.startswith("setting_"):
            await self.handle_setting_callback(query, context)
        
        elif query.data.startswith("section_"):
            await self.handle_section_callback(query, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if update.effective_user.id not in Config.ADMIN_IDS:
            return
        
        # Handle contextual responses based on conversation state
        # This would be implemented based on your specific needs
        pass
    
    async def publish_article(self, article: Article) -> bool:
        """Publish article to Telegram channel"""
        try:
            if Config.ENABLE_TEXT_SHORTENING:
                # Publish shortened version with Telegraph link
                return await self.publish_shortened_article(article)
            else:
                # Publish full article
                return await self.publish_full_article(article)
        
        except Exception as e:
            logger.error(f"Error publishing article: {e}")
            return False
    
    async def publish_shortened_article(self, article: Article) -> bool:
        """Publish shortened article with Telegraph link"""
        try:
            # Create Telegraph page
            telegraph_url = await self.telegraph_manager.create_article_page(article)
            
            if not telegraph_url:
                logger.error("Failed to create Telegraph page")
                return False
            
            # Update article with Telegraph URL
            article.telegraph_url = telegraph_url
            self.db.update_article(article)
            
            # Prepare message
            message_text = f"📰 {article.title}\n\n"
            
            if article.summary:
                message_text += f"{article.summary}\n\n"
            
            message_text += "...تكملة المقال 👈"
            
            # Add footer
            if Config.CUSTOM_FOOTER:
                message_text += f"\n\n{Config.CUSTOM_FOOTER}"
            
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("📖 تكملة المقال", url=telegraph_url)],
                [InlineKeyboardButton("🔗 المصدر الأصلي", url=article.url)]
            ]
            
            if article.tags:
                share_text = f"{article.title}\n\n{article.summary}\n\n{article.url}"
                share_url = f"https://t.me/share/url?url={article.url}&text={share_text}"
                keyboard.append([InlineKeyboardButton("📤 مشاركة", url=share_url)])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send image if available
            if article.image_url:
                try:
                    message = await self.bot.send_photo(
                        chat_id=Config.CHAT_ID,
                        photo=article.image_url,
                        caption=message_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
                    # Record published message
                    self.db.add_published_message(
                        article.id, message.message_id, Config.CHAT_ID, "photo"
                    )
                    
                except Exception as e:
                    logger.error(f"Error sending photo: {e}")
                    # Fallback to text message
                    message = await self.bot.send_message(
                        chat_id=Config.CHAT_ID,
                        text=message_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                message = await self.bot.send_message(
                    chat_id=Config.CHAT_ID,
                    text=message_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            
            # Update article status
            article.telegram_message_id = message.message_id
            article.is_published = True
            self.db.update_article(article)
            
            logger.info(f"Published shortened article: {article.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing shortened article: {e}")
            return False
    
    async def publish_full_article(self, article: Article) -> bool:
        """Publish full article to Telegram"""
        try:
            # Prepare content
            content = article.content
            
            # Add header
            if Config.CUSTOM_HEADER:
                content = f"{Config.CUSTOM_HEADER}\n\n{content}"
            
            # Add footer
            if Config.CUSTOM_FOOTER:
                content = f"{content}\n\n{Config.CUSTOM_FOOTER}"
            
            # Add source link
            content += f"\n\n🔗 المصدر: {article.url}"
            
            # Split content if too long
            message_parts = self.split_long_message(content)
            
            message_ids = []
            
            for i, part in enumerate(message_parts):
                if i == 0 and article.image_url:
                    # Send first part with image
                    try:
                        message = await self.bot.send_photo(
                            chat_id=Config.CHAT_ID,
                            photo=article.image_url,
                            caption=part,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        message_ids.append(message.message_id)
                    except Exception as e:
                        logger.error(f"Error sending photo: {e}")
                        message = await self.bot.send_message(
                            chat_id=Config.CHAT_ID,
                            text=part,
                            parse_mode=ParseMode.MARKDOWN
                        )
                        message_ids.append(message.message_id)
                else:
                    # Send text parts
                    message = await self.bot.send_message(
                        chat_id=Config.CHAT_ID,
                        text=part,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_to_message_id=message_ids[0] if message_ids else None
                    )
                    message_ids.append(message.message_id)
            
            # Update article status
            article.telegram_message_id = message_ids[0] if message_ids else None
            article.is_published = True
            self.db.update_article(article)
            
            # Record all published messages
            for msg_id in message_ids:
                self.db.add_published_message(
                    article.id, msg_id, Config.CHAT_ID, "text"
                )
            
            logger.info(f"Published full article: {article.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error publishing full article: {e}")
            return False
    
    def split_long_message(self, text: str, max_length: int = None) -> List[str]:
        """Split long message into parts"""
        if max_length is None:
            max_length = Config.MAX_MESSAGE_LENGTH
        
        if len(text) <= max_length:
            return [text]
        
        parts = []
        current_part = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_part) + len(paragraph) + 2 <= max_length:
                if current_part:
                    current_part += '\n\n'
                current_part += paragraph
            else:
                if current_part:
                    parts.append(current_part)
                    current_part = paragraph
                else:
                    # Paragraph is too long, split by sentences
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        if len(current_part) + len(sentence) + 2 <= max_length:
                            if current_part:
                                current_part += '. '
                            current_part += sentence
                        else:
                            if current_part:
                                parts.append(current_part)
                            current_part = sentence
        
        if current_part:
            parts.append(current_part)
        
        return parts
    
    async def send_article_for_approval(self, chat_id: int, article: Article):
        """Send article to admin for approval"""
        try:
            # Prepare preview
            preview_text = f"📰 {article.title}\n\n"
            preview_text += f"📂 القسم: {article.section}\n"
            preview_text += f"🔗 الرابط: {article.url}\n\n"
            
            if article.summary:
                preview_text += f"📝 الملخص:\n{article.summary}\n\n"
            
            # Truncate content preview
            content_preview = article.content[:500] + "..." if len(article.content) > 500 else article.content
            preview_text += f"📄 المحتوى:\n{content_preview}"
            
            # Create approval keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ موافقة", callback_data=f"approve_{article.id}"),
                    InlineKeyboardButton("❌ رفض", callback_data=f"reject_{article.id}")
                ],
                [InlineKeyboardButton("✏️ تعديل", callback_data=f"edit_{article.id}")]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send with image if available
            if article.image_url:
                try:
                    await self.bot.send_photo(
                        chat_id=chat_id,
                        photo=article.image_url,
                        caption=preview_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception:
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=preview_text,
                        reply_markup=reply_markup,
                        parse_mode=ParseMode.MARKDOWN
                    )
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=preview_text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN
                )
            
        except Exception as e:
            logger.error(f"Error sending article for approval: {e}")
    
    async def approve_article(self, query, article_id: int):
        """Approve article for publishing"""
        try:
            # Get article from database
            article = self.db.get_article_by_id(article_id)
            
            if not article:
                await query.edit_message_text("المقال غير موجود.")
                return
            
            # Publish article
            success = await self.publish_article(article)
            
            if success:
                await query.edit_message_text(f"✅ تم نشر المقال بنجاح: {article.title}")
            else:
                await query.edit_message_text(f"❌ فشل في نشر المقال: {article.title}")
                
        except Exception as e:
            logger.error(f"Error approving article: {e}")
            await query.edit_message_text("حدث خطأ أثناء الموافقة على المقال.")
    
    async def reject_article(self, query, article_id: int):
        """Reject article"""
        try:
            # Mark article as rejected (you can implement this in the database)
            await query.edit_message_text("❌ تم رفض المقال.")
            
        except Exception as e:
            logger.error(f"Error rejecting article: {e}")
            await query.edit_message_text("حدث خطأ أثناء رفض المقال.")
    
    async def edit_article(self, query, article_id: int):
        """Edit article"""
        try:
            # This would open an editing interface
            await query.edit_message_text("✏️ ميزة التعديل قيد التطوير.")
            
        except Exception as e:
            logger.error(f"Error editing article: {e}")
            await query.edit_message_text("حدث خطأ أثناء فتح محرر المقال.")
    
    async def handle_setting_callback(self, query, context):
        """Handle settings callbacks"""
        # Implementation for settings management
        await query.edit_message_text("⚙️ إعدادات البوت قيد التطوير.")
    
    async def handle_section_callback(self, query, context):
        """Handle section callbacks"""
        # Implementation for section management
        await query.edit_message_text("📂 إدارة الأقسام قيد التطوير.")
    
    async def notify_admins(self, message: str):
        """Notify all admins"""
        for admin_id in Config.ADMIN_IDS:
            try:
                await self.bot.send_message(chat_id=admin_id, text=message)
            except Exception as e:
                logger.error(f"Error notifying admin {admin_id}: {e}")
    
    async def run_bot(self):
        """Run the bot"""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            logger.info("Bot started successfully")
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
        finally:
            await self.application.stop()
    
    async def stop_bot(self):
        """Stop the bot"""
        if self.application:
            await self.application.stop()