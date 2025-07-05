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

echo "✅ Docker متوفر: $(docker --version)"
echo "✅ Docker Compose متوفر: $(docker-compose --version)"

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
            nano .env 2>/dev/null || vi .env 2>/dev/null || echo "يرجى تعديل ملف .env يدوياً"
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
    echo ""
    echo "المتغيرات المطلوبة:"
    echo "  BOT_TOKEN=your_bot_token_here"
    echo "  CHAT_ID=your_chat_id_here"
    echo "  ADMIN_ID=your_admin_id_here"
    exit 1
fi

echo "✅ ملف .env جاهز"

# إنشاء المجلدات المطلوبة
echo "📁 إنشاء المجلدات المطلوبة..."
mkdir -p data logs backups
echo "✅ المجلدات جاهزة"

# فحص وجود الملفات المطلوبة
echo "📋 فحص الملفات المطلوبة..."
required_files=("main.py" "config.py" "database.py" "website_monitor.py" "telegram_publisher.py" "docker-compose.yml" "Dockerfile")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ خطأ: الملف $file غير موجود"
        exit 1
    fi
done

echo "✅ جميع الملفات المطلوبة موجودة"

# إيقاف الحاويات القديمة إذا كانت تعمل
echo "🛑 إيقاف الحاويات القديمة..."
docker-compose down 2>/dev/null || true

# السؤال عن نوع التشغيل
echo ""
echo "🎯 اختر نوع التشغيل:"
echo "1. تشغيل البوت فقط (الافتراضي)"
echo "2. تشغيل البوت مع Redis"
echo "3. تشغيل البوت مع Redis والمراقبة"
echo "4. تشغيل البوت مع جميع الخدمات (Redis + مراقبة + نسخ احتياطي)"
echo "5. إعادة بناء الصورة وتشغيل البوت"
echo ""
read -p "اختر الرقم (1-5) [1]: " choice
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
    5)
        echo "🔨 إعادة بناء الصورة..."
        docker-compose build --no-cache ansarollah-bot
        echo "🚀 تشغيل البوت مع الصورة الجديدة..."
        docker-compose up -d ansarollah-bot
        ;;
    *)
        echo "❌ خطأ: خيار غير صحيح"
        exit 1
        ;;
esac

echo ""
echo "⏱️  انتظار بدء التشغيل..."
sleep 15

# فحص حالة الخدمات
echo "📊 فحص حالة الخدمات..."
docker-compose ps

# فحص السجلات
echo ""
echo "📋 آخر سجلات البوت:"
echo "----------------------------------------"
docker-compose logs --tail=15 ansarollah-bot

# فحص صحة الحاوية
echo ""
echo "🔍 فحص صحة البوت..."
if docker-compose exec -T ansarollah-bot python3 -c "print('✅ البوت يعمل بشكل صحيح')" 2>/dev/null; then
    echo "✅ البوت يستجيب بشكل صحيح"
else
    echo "⚠️  البوت قد يحتاج وقت إضافي للبدء"
fi

# معلومات مفيدة
echo ""
echo "🎉 تم تشغيل البوت بنجاح!"
echo "================================================="
echo "📋 أوامر مفيدة:"
echo ""
echo "� مراقبة السجلات المباشرة:"
echo "   docker-compose logs -f ansarollah-bot"
echo ""
echo "� فحص الحالة:"
echo "   docker-compose ps"
echo ""
echo "🔄 إعادة تشغيل البوت:"
echo "   docker-compose restart ansarollah-bot"
echo ""
echo "⏹️  إيقاف البوت:"
echo "   docker-compose down"
echo ""
echo "🧹 تنظيف النظام:"
echo "   docker system prune -a"
echo ""
echo "📖 للمزيد من المعلومات:"
echo "   cat دليل_Docker_للأنصار_الله.md"
echo ""
echo "🤖 اختبار البوت:"
echo "   أرسل /start للبوت في Telegram"
echo ""
echo "🌐 روابط مفيدة:"
echo "   - موقع الأنصار الله: https://www.ansarollah.com.ye"
echo "   - Telegram API: https://api.telegram.org"
echo ""
echo "✅ البوت جاهز للعمل!"
echo "📱 تحقق من قناة التلقرام للتأكد من وصول الرسائل"