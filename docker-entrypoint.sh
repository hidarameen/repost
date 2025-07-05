#!/bin/bash
set -e

# سكريپت دخول Docker لبوت الأنصار الله
# =====================================

echo "🤖 بدء تشغيل بوت الأنصار الله..."

# إنشاء المجلدات المطلوبة
mkdir -p /app/data /app/logs /app/temp

# التحقق من وجود ملف الإعدادات
if [ ! -f "/app/.env" ]; then
    echo "⚠️  ملف .env غير موجود، سيتم إنشاء ملف افتراضي..."
    cp /app/.env.example /app/.env 2>/dev/null || true
fi

# التحقق من متغيرات البيئة المطلوبة
required_vars=("BOT_TOKEN" "CHANNEL_ID" "ADMIN_IDS")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ متغير البيئة المطلوب غير موجود: $var"
        echo "يرجى تعيين المتغيرات المطلوبة في ملف .env"
        exit 1
    fi
done

echo "✅ تم التحقق من متغيرات البيئة بنجاح"

# تنظيف الملفات المؤقتة القديمة
echo "🧹 تنظيف الملفات المؤقتة..."
find /app/temp -type f -mtime +1 -delete 2>/dev/null || true

# التحقق من الاتصال بالإنترنت
echo "🌐 فحص الاتصال بالإنترنت..."
if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "⚠️  تحذير: لا يوجد اتصال بالإنترنت"
else
    echo "✅ الاتصال بالإنترنت متوفر"
fi

# التحقق من الاتصال بـ Telegram API
echo "📞 فحص الاتصال بـ Telegram API..."
if curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getMe" | grep -q '"ok":true'; then
    echo "✅ الاتصال بـ Telegram API ناجح"
else
    echo "❌ فشل في الاتصال بـ Telegram API"
    echo "يرجى التحقق من صحة البوت توكن"
    exit 1
fi

# فحص إمكانية الوصول لموقع الأنصار الله
echo "🌐 فحص إمكانية الوصول لموقع الأنصار الله..."
if curl -s --max-time 10 "https://www.ansarollah.com.ye" >/dev/null; then
    echo "✅ يمكن الوصول لموقع الأنصار الله"
else
    echo "⚠️  تحذير: مشكلة في الوصول لموقع الأنصار الله"
fi

# إعداد قاعدة البيانات
echo "🗄️  إعداد قاعدة البيانات..."
python3 -c "
import sqlite3
import os

db_path = os.getenv('DATABASE_PATH', '/app/data/ansarollah_bot.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# إنشاء قاعدة البيانات إذا لم تكن موجودة
conn = sqlite3.connect(db_path)
conn.close()
print('✅ قاعدة البيانات جاهزة')
"

# إعداد التسجيل
echo "📝 إعداد نظام التسجيل..."
cat > /app/logging_config.py << 'EOF'
import logging
import os
from datetime import datetime

# إعداد نظام التسجيل
log_dir = '/app/logs'
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'bot_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
EOF

echo "✅ نظام التسجيل جاهز"

# إعداد معالج الإشارات للإغلاق الآمن
trap 'echo "🛑 إيقاف البوت..."; kill -TERM $PID; wait $PID' TERM INT

echo "🚀 تشغيل بوت الأنصار الله..."
echo "📊 معلومات البيئة:"
echo "  - Python: $(python3 --version)"
echo "  - مجلد العمل: $(pwd)"
echo "  - مجلد البيانات: /app/data"
echo "  - مجلد السجلات: /app/logs"
echo "  - وقت البدء: $(date)"

# تشغيل البوت
exec "$@" &
PID=$!
wait $PID