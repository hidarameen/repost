#!/usr/bin/env python3
"""
اختبار سريع لإصلاح مشاكل الإعدادات
"""

import os
import sys
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

print("🔧 اختبار إصلاح مشاكل الإعدادات")
print("=" * 50)

# فحص متغيرات البيئة
print("1. فحص متغيرات البيئة:")
required_vars = ['BOT_TOKEN', 'CHAT_ID', 'ADMIN_ID']

for var in required_vars:
    value = os.getenv(var)
    if value:
        if var == 'BOT_TOKEN':
            print(f"✅ {var}: {'*' * 10}{value[-10:]}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: غير موجود")

print()

# اختبار استيراد الإعدادات
print("2. اختبار استيراد الإعدادات:")
try:
    from config import Config
    print("✅ تم استيراد Config بنجاح")
    
    # طباعة الإعدادات
    Config.print_config()
    
    # فحص التحقق
    print("\n3. فحص التحقق من الإعدادات:")
    if Config.validate():
        print("✅ جميع الإعدادات صحيحة")
    else:
        print("❌ هناك مشاكل في الإعدادات")
        
except Exception as e:
    print(f"❌ خطأ في استيراد الإعدادات: {e}")

print()

# اختبار قاعدة البيانات
print("4. اختبار قاعدة البيانات:")
try:
    from database import Database
    db = Database()
    db.init_database()
    print("✅ قاعدة البيانات تعمل بشكل صحيح")
except Exception as e:
    print(f"❌ خطأ في قاعدة البيانات: {e}")

print()

# اختبار التلقرام
print("5. اختبار اتصال التلقرام:")
try:
    import asyncio
    from telegram import Bot
    
    async def test_telegram():
        bot = Bot(token=Config.BOT_TOKEN)
        
        # اختبار البوت
        try:
            bot_info = await bot.get_me()
            print(f"✅ البوت متصل: @{bot_info.username}")
        except Exception as e:
            print(f"❌ خطأ في اتصال البوت: {e}")
            return
        
        # اختبار القناة
        try:
            chat_info = await bot.get_chat(Config.CHAT_ID)
            print(f"✅ القناة متاحة: {chat_info.title}")
        except Exception as e:
            print(f"❌ خطأ في الوصول للقناة: {e}")
    
    asyncio.run(test_telegram())
    
except Exception as e:
    print(f"❌ خطأ في اختبار التلقرام: {e}")

print()

# اختبار موقع الأنصار الله
print("6. اختبار موقع الأنصار الله:")
try:
    import requests
    
    response = requests.get(Config.WEBSITE_URL, timeout=10)
    if response.status_code == 200:
        print(f"✅ الموقع متاح: {Config.WEBSITE_URL}")
    else:
        print(f"⚠️ الموقع يرد بكود: {response.status_code}")
        
except Exception as e:
    print(f"❌ خطأ في الوصول للموقع: {e}")

print()
print("🎉 انتهى الاختبار!")
print("=" * 50)

# إرشادات الإصلاح
print("\n📋 إرشادات الإصلاح:")
print("1. تأكد من صحة ملف .env")
print("2. تحقق من صحة توكن البوت")
print("3. تأكد من إضافة البوت للقناة كمشرف")
print("4. تحقق من الاتصال بالإنترنت")
print("5. جرب تشغيل البوت: python3 main.py")