#!/usr/bin/env python3
"""
أداة اختبار token البوت
تتحقق من صحة token البوت قبل تشغيل البوت الرئيسي
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

async def test_bot_token(token: str = None) -> bool:
    """Test if bot token is valid"""
    if not token:
        token = BOT_TOKEN
    
    if not token:
        print("❌ لم يتم العثور على BOT_TOKEN!")
        print("📋 الرجاء تحديث ملف .env")
        return False
    
    # Check token format
    if not token.count(':') == 1:
        print("❌ صيغة البوت Token غير صحيحة!")
        print("📋 الصيغة الصحيحة: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False
    
    parts = token.split(':')
    if not parts[0].isdigit() or len(parts[1]) < 35:
        print("❌ صيغة البوت Token غير صحيحة!")
        print("📋 الصيغة الصحيحة: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz")
        return False
    
    # Test token with Telegram API
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    bot_info = data['result']
                    print(f"✅ البوت Token صحيح!")
                    print(f"📋 اسم البوت: {bot_info.get('first_name', 'Unknown')}")
                    print(f"📋 معرف البوت: @{bot_info.get('username', 'Unknown')}")
                    print(f"📋 ID البوت: {bot_info.get('id', 'Unknown')}")
                    return True
                elif response.status == 401:
                    print("❌ البوت Token غير صحيح أو منتهي الصلاحية!")
                    print("📋 الرجاء:")
                    print("   1. إنشاء بوت جديد من @BotFather")
                    print("   2. تحديث BOT_TOKEN في ملف .env")
                    print("   3. إعادة تشغيل البوت")
                    return False
                else:
                    print(f"❌ خطأ في الاتصال بـ Telegram API: {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

async def get_bot_info(token: str = None) -> dict:
    """Get bot information from Telegram API"""
    if not token:
        token = BOT_TOKEN
    
    url = f"https://api.telegram.org/bot{token}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['result']
                else:
                    return {}
    except Exception:
        return {}

async def main():
    """Main function to test the bot token"""
    print("🔍 اختبار صحة البوت Token...")
    print("=" * 50)
    
    is_valid = await test_bot_token()
    
    if is_valid:
        print("\n✅ البوت جاهز للعمل!")
        print("🚀 يمكنك تشغيل البوت الآن بأمان")
    else:
        print("\n❌ البوت Token غير صحيح!")
        print("📋 اتبع الخطوات في ملف BOT_TOKEN_FIX_GUIDE.md")

if __name__ == "__main__":
    asyncio.run(main())