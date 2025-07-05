#!/bin/bash
# نقطة دخول بوت الأنصار الله اليمني
# Docker Entry Point for Ansarollah News Bot

set -e

echo "🐳 مرحباً بك في بوت الأنصار الله اليمني"
echo "🇾🇪 بدء تشغيل البوت..."
echo "================================================="

# فحص وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ خطأ: Python غير متوفر"
    exit 1
fi

echo "✅ Python متوفر: $(python3 --version)"

# فحص وجود ملف .env
if [ ! -f /app/.env ]; then
    echo "⚠️  تحذير: ملف .env غير موجود"
    if [ -f /app/.env.example ]; then
        echo "📋 نسخ .env.example إلى .env..."
        cp /app/.env.example /app/.env
        echo "✅ تم إنشاء ملف .env افتراضي"
        echo "⚠️  يرجى تعديل متغيرات البيئة في Docker Compose"
    else
        echo "❌ خطأ: لا يوجد ملف .env أو .env.example"
        exit 1
    fi
fi

# فحص متغيرات البيئة الأساسية
echo "🔍 فحص متغيرات البيئة..."

if [ -z "$BOT_TOKEN" ] && ! grep -q "BOT_TOKEN=" /app/.env; then
    echo "❌ خطأ: BOT_TOKEN غير محدد"
    exit 1
fi

if [ -z "$CHAT_ID" ] && ! grep -q "CHAT_ID=" /app/.env; then
    echo "❌ خطأ: CHAT_ID غير محدد"
    exit 1
fi

echo "✅ متغيرات البيئة محددة"

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات المطلوبة..."
mkdir -p /app/data /app/logs /app/temp
echo "✅ المجلدات جاهزة"

# فحص الاتصال بالإنترنت
echo "🌐 فحص الاتصال بالإنترنت..."
if curl -s --connect-timeout 10 https://google.com > /dev/null; then
    echo "✅ الاتصال بالإنترنت متاح"
else
    echo "❌ تحذير: مشكلة في الاتصال بالإنترنت"
fi

# فحص الاتصال بـ Telegram API
echo "� فحص الاتصال بـ Telegram API..."
if curl -s --connect-timeout 10 https://api.telegram.org/ > /dev/null; then
    echo "✅ Telegram API متاح"
else
    echo "❌ تحذير: مشكلة في الاتصال بـ Telegram API"
fi

# فحص الاتصال بموقع الأنصار الله
echo "🇾� فحص الاتصال بموقع الأنصار الله..."
if curl -s --connect-timeout 10 https://www.ansarollah.com.ye > /dev/null; then
    echo "✅ موقع الأنصار الله متاح"
else
    echo "❌ تحذير: مشكلة في الاتصال بموقع الأنصار الله"
fi

# تحديد مجلد العمل
cd /app

# فحص وجود الملفات المطلوبة
echo "📋 فحص الملفات المطلوبة..."
required_files=("main.py" "config.py" "database.py" "website_monitor.py" "telegram_publisher.py")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ خطأ: الملف $file غير موجود"
        exit 1
    fi
done

echo "✅ جميع الملفات المطلوبة موجودة"

# فحص صحة Python syntax
echo "🐍 فحص صحة الكود..."
if python3 -m py_compile main.py; then
    echo "✅ الكود صحيح"
else
    echo "❌ خطأ: مشكلة في الكود"
    exit 1
fi

# إعداد قاعدة البيانات
echo "🗄️  إعداد قاعدة البيانات..."
python3 -c "
import sqlite3
import os
db_path = '/app/data/ansarollah_bot.db'
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)
conn.close()
print('✅ قاعدة البيانات جاهزة')
"

# إعداد نظام السجلات
echo "📝 إعداد نظام السجلات..."
log_file="/app/logs/bot_$(date +%Y%m%d).log"
touch "$log_file"
echo "✅ نظام السجلات جاهز: $log_file"

# بدء تشغيل البوت
echo ""
echo "🚀 بدء تشغيل بوت الأنصار الله اليمني..."
echo "================================================="
echo "📅 التاريخ: $(date)"
echo "🕒 الوقت: $(date +%H:%M:%S)"
echo "🌍 المنطقة الزمنية: $(date +%Z)"
echo "📍 مجلد العمل: $(pwd)"
echo "👤 المستخدم: $(whoami)"
echo "================================================="

# تشغيل البوت مع إعادة التوجيه للسجلات
exec python3 main.py 2>&1 | tee -a "$log_file"