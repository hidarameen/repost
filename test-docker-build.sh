#!/bin/bash
# اختبار سريع لبناء Docker لبوت الأنصار الله

echo "🔨 اختبار بناء Docker لبوت الأنصار الله"
echo "============================================"

# فحص وجود Docker
if ! command -v docker &> /dev/null; then
    echo "❌ خطأ: Docker غير مثبت"
    exit 1
fi

echo "✅ Docker متوفر: $(docker --version)"

# فحص وجود الملفات المطلوبة
echo "📋 فحص الملفات المطلوبة..."
required_files=("Dockerfile" "requirements.txt" "docker-entrypoint.sh" "main.py")

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ خطأ: الملف $file غير موجود"
        exit 1
    fi
done

echo "✅ جميع الملفات موجودة"

# إنشاء ملف .env مؤقت للاختبار
if [ ! -f .env ]; then
    echo "📋 إنشاء ملف .env مؤقت للاختبار..."
    cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
BOT_TOKEN=test_token_for_build
CHAT_ID=test_chat_id
ADMIN_ID=test_admin_id
WEBSITE_URL=https://www.ansarollah.com.ye
MONITORING_INTERVAL=120
AUTO_PUBLISH=true
EOF
fi

# بدء اختبار البناء
echo "🚀 بدء اختبار بناء الصورة..."
echo "⏱️  هذا قد يستغرق بضع دقائق..."

# بناء الصورة
if docker build -t ansarollah-bot-test . --no-cache; then
    echo "✅ نجح بناء الصورة!"
    
    # اختبار تشغيل الحاوية
    echo "🧪 اختبار تشغيل الحاوية..."
    
    # إنشاء حاوية مؤقتة للاختبار
    if docker run --rm -d --name ansarollah-test ansarollah-bot-test sleep 30; then
        echo "✅ نجح تشغيل الحاوية!"
        
        # اختبار تشغيل Python
        echo "🐍 اختبار Python داخل الحاوية..."
        if docker exec ansarollah-test python3 --version; then
            echo "✅ Python يعمل بشكل صحيح"
        else
            echo "❌ مشكلة في Python"
        fi
        
        # اختبار استيراد المكتبات
        echo "📚 اختبار استيراد المكتبات المطلوبة..."
        if docker exec ansarollah-test python3 -c "
import telegram
import requests
import sqlite3
import aiohttp
import newspaper
import telegraph
print('✅ جميع المكتبات متوفرة')
"; then
            echo "✅ جميع المكتبات تعمل بشكل صحيح"
        else
            echo "❌ مشكلة في المكتبات"
        fi
        
        # اختبار وجود الملفات
        echo "📂 اختبار وجود الملفات داخل الحاوية..."
        if docker exec ansarollah-test ls -la /app/main.py; then
            echo "✅ الملفات موجودة في الحاوية"
        else
            echo "❌ مشكلة في نسخ الملفات"
        fi
        
        # إيقاف الحاوية
        docker stop ansarollah-test >/dev/null 2>&1
        
    else
        echo "❌ فشل في تشغيل الحاوية"
    fi
    
    # تنظيف الصورة المؤقتة
    echo "🧹 تنظيف الصورة المؤقتة..."
    docker rmi ansarollah-bot-test >/dev/null 2>&1
    
    echo ""
    echo "🎉 اختبار البناء مكتمل!"
    echo "✅ يمكنك الآن استخدام Docker لتشغيل البوت"
    echo ""
    echo "للتشغيل الفعلي:"
    echo "  ./docker-run.sh"
    echo "أو:"
    echo "  docker-compose up -d"
    
else
    echo "❌ فشل في بناء الصورة"
    echo ""
    echo "الأخطاء الشائعة وحلولها:"
    echo "1. تحقق من وجود جميع الملفات المطلوبة"
    echo "2. تأكد من صحة ملف requirements.txt"
    echo "3. تحقق من الاتصال بالإنترنت"
    echo "4. جرب تشغيل: docker system prune -a"
    exit 1
fi