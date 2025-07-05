#!/bin/bash
# تشغيل سريع لبوت الأنصار الله عبر Docker

echo "🐳 مرحباً بك في سكريبت تشغيل بوت الأنصار الله عبر Docker"
echo "================================================="

# فحص وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ خطأ: Docker غير مثبت"
    echo "يرجى تثبيت Docker أولاً من: https://docs.docker.com/get-docker/"
    exit 1
fi

# فحص وجود Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ خطأ: Docker Compose غير مثبت"
    echo "يرجى تثبيت Docker Compose من: https://docs.docker.com/compose/install/"
    exit 1
fi

# فحص وجود ملف .env
if [ ! -f .env ]; then
    echo "⚠️  تحذير: ملف .env غير موجود"
    if [ -f .env.example ]; then
        echo "📋 نسخ .env.example إلى .env..."
        cp .env.example .env
        echo "✅ تم إنشاء ملف .env"
        echo "⚠️  يرجى تعديل ملف .env بالبيانات الصحيحة:"
        echo "   - BOT_TOKEN: توكن البوت"
        echo "   - CHAT_ID: معرف القناة"
        echo "   - ADMIN_ID: معرف المشرف"
        echo ""
        read -p "هل تريد فتح ملف .env للتعديل؟ (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            nano .env
        fi
    else
        echo "❌ خطأ: .env.example غير موجود"
        exit 1
    fi
fi

# فحص محتوى ملف .env
echo "🔍 فحص إعدادات البوت..."
if grep -q "YOUR_BOT_TOKEN" .env || grep -q "YOUR_CHAT_ID" .env; then
    echo "❌ خطأ: ملف .env يحتوي على قيم افتراضية"
    echo "يرجى تعديل ملف .env أولاً بالبيانات الصحيحة"
    exit 1
fi

echo "✅ ملف .env جاهز"

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات المطلوبة..."
mkdir -p data logs backups
echo "✅ المجلدات جاهزة"

# السؤال عن نوع التشغيل
echo ""
echo "🎯 اختر نوع التشغيل:"
echo "1. تشغيل البوت فقط (الافتراضي)"
echo "2. تشغيل البوت مع Redis"
echo "3. تشغيل البوت مع Redis والمراقبة"
echo "4. تشغيل البوت مع جميع الخدمات (Redis + مراقبة + نسخ احتياطي)"
echo ""
read -p "اختر الرقم (1-4) [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo "🚀 تشغيل البوت فقط..."
        docker-compose up -d ansarollah-bot
        ;;
    2)
        echo "🚀 تشغيل البوت مع Redis..."
        docker-compose up -d ansarollah-bot redis
        ;;
    3)
        echo "🚀 تشغيل البوت مع Redis والمراقبة..."
        docker-compose --profile monitoring up -d ansarollah-bot redis watchtower
        ;;
    4)
        echo "🚀 تشغيل البوت مع جميع الخدمات..."
        docker-compose --profile monitoring --profile backup up -d
        ;;
    *)
        echo "❌ خطأ: خيار غير صحيح"
        exit 1
        ;;
esac

echo ""
echo "⏱️  انتظار بدء التشغيل..."
sleep 10

# فحص حالة الخدمات
echo "📊 فحص حالة الخدمات..."
docker-compose ps

# فحص السجلات
echo ""
echo "📋 آخر سجلات البوت:"
docker-compose logs --tail=10 ansarollah-bot

# معلومات مفيدة
echo ""
echo "🎉 تم تشغيل البوت بنجاح!"
echo "================================================="
echo "أوامر مفيدة:"
echo ""
echo "📋 مراقبة السجلات:"
echo "   docker-compose logs -f ansarollah-bot"
echo ""
echo "📊 فحص الحالة:"
echo "   docker-compose ps"
echo ""
echo "🔄 إعادة تشغيل البوت:"
echo "   docker-compose restart ansarollah-bot"
echo ""
echo "⏹️  إيقاف البوت:"
echo "   docker-compose down"
echo ""
echo "📖 للمزيد من المعلومات:"
echo "   cat دليل_Docker_للأنصار_الله.md"
echo ""
echo "🤖 اختبار البوت:"
echo "   أرسل /start للبوت في Telegram"
echo ""
echo "✅ البوت جاهز للعمل!"