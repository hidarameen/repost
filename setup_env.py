#!/usr/bin/env python3
"""
أداة إعداد ملف .env للبوت
تساعد في إنشاء ملف .env بالإعدادات الصحيحة
"""

import os
import asyncio
import aiohttp

def create_env_file():
    """إنشاء ملف .env بالإعدادات الصحيحة"""
    
    print("🔧 إعداد ملف .env للبوت")
    print("=" * 50)
    
    # جمع البيانات من المستخدم
    print("\n📋 الرجاء إدخال البيانات التالية:")
    print("💡 يمكنك الضغط على Enter لاستخدام القيم الافتراضية")
    
    # البوت Token
    print("\n1️⃣ البوت Token:")
    print("   احصل عليه من @BotFather بعد إنشاء بوت جديد")
    bot_token = input("BOT_TOKEN: ").strip()
    
    if not bot_token:
        print("❌ البوت Token مطلوب!")
        return False
    
    # Chat ID
    print("\n2️⃣ Chat ID:")
    print("   للنشر في محادثة شخصية: رقم موجب")
    print("   للنشر في قناة: رقم سالب (مثل: -1001234567890)")
    chat_id = input("CHAT_ID: ").strip()
    
    if not chat_id:
        print("❌ Chat ID مطلوب!")
        return False
    
    # Admin IDs
    print("\n3️⃣ Admin IDs:")
    print("   ID المدير (يمكن إضافة أكثر من واحد بفصل بالفاصلة)")
    admin_ids_input = input("ADMIN_IDS: ").strip()
    
    if not admin_ids_input:
        print("❌ Admin ID مطلوب!")
        return False
    
    # تحويل Admin IDs إلى قائمة
    admin_ids = []
    for admin_id in admin_ids_input.split(','):
        admin_id = admin_id.strip()
        if admin_id.isdigit():
            admin_ids.append(int(admin_id))
    
    if not admin_ids:
        print("❌ Admin IDs غير صحيحة!")
        return False
    
    # إعدادات اختيارية
    print("\n4️⃣ إعدادات اختيارية (اضغط Enter للافتراضي):")
    
    website_url = input("WEBSITE_URL [https://www.ansarollah.com.ye]: ").strip()
    if not website_url:
        website_url = "https://www.ansarollah.com.ye"
    
    auto_publish = input("AUTO_PUBLISH [true]: ").strip()
    if not auto_publish:
        auto_publish = "true"
    
    check_interval = input("CHECK_INTERVAL [120]: ").strip()
    if not check_interval:
        check_interval = "120"
    
    # إنشاء محتوى ملف .env
    env_content = f"""# إعدادات البوت
BOT_TOKEN={bot_token}
CHAT_ID={chat_id}
ADMIN_IDS={admin_ids}

# إعدادات الموقع
WEBSITE_URL={website_url}
AUTO_PUBLISH={auto_publish}
CHECK_INTERVAL={check_interval}

# إعدادات قاعدة البيانات
DATABASE_PATH=data/ansarollah_bot.db

# إعدادات Telegraph
TELEGRAPH_AUTHOR=الأنصار الله
TELEGRAPH_AUTHOR_URL={website_url}

# إعدادات المحتوى
ENABLE_TEXT_SHORTENING=true
MAX_MESSAGE_LENGTH=4096
SHORT_DESCRIPTION_LENGTH=200

# إعدادات مخصصة
CUSTOM_HEADER=📰 موقع الأنصار الله
CUSTOM_FOOTER=🔗 تابعونا للمزيد من الأخبار

# إعدادات الصور
EXTRACT_IMAGES=true
DOWNLOAD_IMAGES=true
"""
    
    # حفظ ملف .env
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("\n✅ تم إنشاء ملف .env بنجاح!")
        print("📋 محتوى الملف:")
        print("-" * 30)
        print(env_content)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في حفظ ملف .env: {e}")
        return False

async def test_settings():
    """اختبار الإعدادات الجديدة"""
    
    print("\n🔍 اختبار الإعدادات الجديدة...")
    
    # تحميل الإعدادات
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN", "")
    chat_id = os.getenv("CHAT_ID", "")
    
    if not bot_token or not chat_id:
        print("❌ لم يتم العثور على الإعدادات!")
        return False
    
    # اختبار البوت Token
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    bot_info = data['result']
                    print(f"✅ البوت Token صحيح!")
                    print(f"📋 اسم البوت: {bot_info.get('first_name', 'Unknown')}")
                    print(f"📋 معرف البوت: @{bot_info.get('username', 'Unknown')}")
                    return True
                else:
                    print(f"❌ البوت Token غير صحيح: {response.status}")
                    return False
    
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    
    print("🚀 أداة إعداد البوت")
    print("=" * 50)
    
    # التحقق من وجود ملف .env
    if os.path.exists('.env'):
        print("⚠️  يوجد ملف .env بالفعل!")
        overwrite = input("هل تريد استبداله؟ (y/n): ").strip().lower()
        if overwrite not in ['y', 'yes', 'نعم']:
            print("❌ تم إلغاء العملية")
            return
    
    # إنشاء ملف .env
    if create_env_file():
        # اختبار الإعدادات
        print("\n🔧 اختبار الإعدادات...")
        try:
            is_valid = asyncio.run(test_settings())
            if is_valid:
                print("\n🎉 الإعداد مكتمل بنجاح!")
                print("🚀 يمكنك الآن تشغيل البوت:")
                print("   python3 main.py")
            else:
                print("\n❌ يوجد مشكلة في الإعدادات!")
                print("📋 تحقق من البيانات وأعد المحاولة")
        except Exception as e:
            print(f"❌ خطأ في اختبار الإعدادات: {e}")
    else:
        print("❌ فشل في إنشاء ملف .env")

if __name__ == "__main__":
    main()