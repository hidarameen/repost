#!/usr/bin/env python3
"""
اختبار أوامر البوت
"""

import asyncio
from telegram import Bot
from config import Config

async def test_bot_commands():
    """اختبار أوامر البوت"""
    
    print("🧪 اختبار أوامر بوت الأنصار الله")
    print("=" * 50)
    
    # إنشاء البوت
    bot = Bot(token=Config.BOT_TOKEN)
    
    try:
        # 1. اختبار معلومات البوت
        print("1. فحص معلومات البوت...")
        bot_info = await bot.get_me()
        print(f"✅ البوت: @{bot_info.username}")
        print(f"   الاسم: {bot_info.first_name}")
        print(f"   ID: {bot_info.id}")
        
        # 2. اختبار القناة
        print("\n2. فحص القناة...")
        chat_info = await bot.get_chat(Config.CHAT_ID)
        print(f"✅ القناة: {chat_info.title}")
        print(f"   النوع: {chat_info.type}")
        print(f"   ID: {chat_info.id}")
        
        # 3. اختبار إرسال رسالة اختبار للمشرف
        print("\n3. إرسال رسالة اختبار للمشرف...")
        
        test_message = """
🤖 اختبار أوامر البوت

الأوامر المتاحة:
• /start - بدء التشغيل
• /help - المساعدة
• /status - حالة البوت
• /pending - المقالات المعلقة
• /settings - الإعدادات
• /sections - الأقسام
• /test - اختبار

جرب الأوامر أعلاه! ✨
        """
        
        message = await bot.send_message(
            chat_id=Config.ADMIN_IDS[0],
            text=test_message
        )
        
        print(f"✅ تم إرسال رسالة اختبار للمشرف")
        print(f"   معرف الرسالة: {message.message_id}")
        
        # 4. فحص صلاحيات البوت في القناة
        print("\n4. فحص صلاحيات البوت في القناة...")
        try:
            member = await bot.get_chat_member(Config.CHAT_ID, bot_info.id)
            print(f"✅ البوت عضو في القناة")
            print(f"   الحالة: {member.status}")
            
            if member.status == 'administrator':
                print("✅ البوت مشرف في القناة")
            else:
                print("⚠️ البوت ليس مشرف في القناة")
                
        except Exception as e:
            print(f"❌ خطأ في فحص صلاحيات البوت: {e}")
        
        print("\n🎉 انتهى اختبار أوامر البوت!")
        print("=" * 50)
        print("\nالآن يمكنك اختبار الأوامر التالية في Telegram:")
        print("1. أرسل /start للبوت")
        print("2. أرسل /help لعرض المساعدة")
        print("3. أرسل /status لعرض حالة البوت")
        print("4. أرسل /test لاختبار نظام الموافقة")
        
    except Exception as e:
        print(f"❌ خطأ في اختبار البوت: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot_commands())