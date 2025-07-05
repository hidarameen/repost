#!/bin/bash

# إعداد سريع لبوت موقع الأنصار الله اليمني
# =====================================

clear
echo "🤖 إعداد بوت موقع الأنصار الله اليمني"
echo "======================================="
echo ""

# التحقق من Python
if ! command -v python3 &> /dev/null; then
    echo "❌ خطأ: Python 3 غير مثبت"
    echo "يرجى تثبيت Python 3 أولاً"
    exit 1
fi

echo "✅ تم العثور على Python 3"

# إنشاء ملف الإعدادات للأنصار الله
echo "📝 إنشاء ملف الإعدادات..."
cp .env.ansarollah .env

# تثبيت المتطلبات
echo "📦 تثبيت المتطلبات..."
pip3 install -r requirements.txt --quiet

# إعطاء صلاحيات التشغيل
chmod +x run.sh

echo ""
echo "🎯 تم الإعداد الأولي بنجاح!"
echo "==============================="
echo ""

# طلب بيانات البوت
echo "يرجى إدخال بيانات البوت التلقرام:"
echo ""

read -p "📞 توكن البوت (Bot Token): " BOT_TOKEN
read -p "📢 معرف القناة (Channel ID): " CHANNEL_ID
read -p "👤 معرف المشرف (Admin ID): " ADMIN_ID

# تحديث ملف الإعدادات
echo "📝 تحديث الإعدادات..."

# إنشاء ملف env مؤقت
cat > temp_env << EOF
# إعدادات بوت موقع الأنصار الله اليمني
BOT_TOKEN=$BOT_TOKEN
CHANNEL_ID=$CHANNEL_ID
ADMIN_IDS=["$ADMIN_ID"]

# إعدادات موقع الأنصار الله
WEBSITE_URL=https://www.ansarollah.com.ye
WEBSITE_SECTIONS=["أخبار", "أخبار محلية", "أخبار عربية", "أخبار دولية", "بيانات", "مقالات"]
CHECK_INTERVAL=120

# إعدادات Telegraph
TELEGRAPH_TOKEN=
TELEGRAPH_AUTHOR=قناة الأنصار الله
TELEGRAPH_AUTHOR_URL=https://t.me/ansarollah_channel

# إعدادات النشر
AUTO_PUBLISH=false
ENABLE_TEXT_SHORTENING=true
MAX_MESSAGE_LENGTH=4000
SHORT_DESCRIPTION_LENGTH=250

# إعدادات التخصيص
CUSTOM_HEADER=📰 أحدث أخبار الأنصار الله
CUSTOM_FOOTER=🔗 تابعونا للمزيد من الأخبار العاجلة

# قاعدة البيانات
DATABASE_PATH=ansarollah_bot.db

# إعدادات استخراج المحتوى
EXTRACT_IMAGES=true
DOWNLOAD_IMAGES=true

# فلاتر المحتوى
EXCLUDE_KEYWORDS=["إعلان", "إعلانات", "رعاية"]
INCLUDE_KEYWORDS=["عاجل", "بيان", "تصريح", "قرار", "العدوان", "المقاومة", "فلسطين", "غزة"]
EOF

# نقل الملف المؤقت
mv temp_env .env

echo "✅ تم تحديث الإعدادات"
echo ""

# اختبار الإعدادات
echo "🔍 اختبار الإعدادات..."
if python3 test_config.py > /dev/null 2>&1; then
    echo "✅ الإعدادات صحيحة"
else
    echo "⚠️  تحذير: قد تحتاج لمراجعة الإعدادات"
fi

# اختبار موقع الأنصار الله
echo "🌐 اختبار موقع الأنصار الله..."
if python3 test_ansarollah.py > /dev/null 2>&1; then
    echo "✅ يمكن الوصول للموقع واستخراج المحتوى"
else
    echo "⚠️  تحذير: مشكلة في الوصول للموقع"
fi

echo ""
echo "🎉 تم الإعداد بنجاح!"
echo "=================="
echo ""
echo "الخطوات التالية:"
echo "1. تأكد من إضافة البوت كمشرف في القناة"
echo "2. امنح البوت صلاحيات النشر"
echo "3. شغل البوت بالأمر: ./run.sh"
echo ""
echo "للاختبار اليدوي:"
echo "- python3 test_config.py"
echo "- python3 test_ansarollah.py"
echo "- python3 main.py"
echo ""

# خيار التشغيل الفوري
echo -n "هل تريد تشغيل البوت الآن؟ (y/n): "
read -r answer
if [[ $answer == "y" || $answer == "Y" || $answer == "نعم" ]]; then
    echo ""
    echo "🚀 تشغيل البوت..."
    echo "استخدم Ctrl+C للإيقاف"
    echo ""
    sleep 2
    ./run.sh
else
    echo ""
    echo "📋 يمكنك تشغيل البوت لاحقاً بالأمر: ./run.sh"
    echo "📖 راجع ملف 'دليل_الإعداد_لموقع_الأنصار_الله.md' للمزيد من التفاصيل"
fi

echo ""
echo "✨ شكراً لاستخدام بوت موقع الأنصار الله!"